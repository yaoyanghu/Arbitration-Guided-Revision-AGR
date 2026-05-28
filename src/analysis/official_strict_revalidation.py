from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from src.common import read_jsonl, write_json, write_jsonl
from src.analysis.official_title_overlap_improvement import normalize_bm25, title_overlap_score

TOKEN_FIXES = {
    "-lrb-": "(",
    "-rrb-": ")",
    "-lsb-": "[",
    "-rsb-": "]",
    "-lcb-": "{",
    "-rcb-": "}",
    "_": " ",
}


def canonical_title(text: str) -> str:
    normalized = text.strip().lower()
    for old, new in TOKEN_FIXES.items():
        normalized = normalized.replace(old, new)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def relaxed_hit(record: dict[str, Any], gold_titles: list[str]) -> bool:
    title = str(record.get("title", "")).lower()
    text = str(record.get("text", "")).lower()
    doc_id = canonical_title(str(record.get("doc_id", "")))
    for gold in gold_titles:
        gold_lower = str(gold).lower()
        if gold_lower and (gold_lower in title or gold_lower in text or canonical_title(gold) == doc_id):
            return True
    return False


def strict_hit(record: dict[str, Any], gold_titles: list[str]) -> bool:
    candidate_titles = {
        canonical_title(str(record.get("title", ""))),
        canonical_title(str(record.get("doc_id", ""))),
    }
    gold_set = {canonical_title(title) for title in gold_titles if str(title).strip()}
    return bool(candidate_titles & gold_set)


def group_by_query(records: list[dict[str, Any]], rank_field: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record["query_id"])].append(record)
    for query_id, items in grouped.items():
        grouped[query_id] = sorted(items, key=lambda item: int(item[rank_field]))
    return dict(grouped)


def compute_metrics(
    grouped_records: dict[str, list[dict[str, Any]]],
    queries: list[dict[str, Any]],
    hit_fn,
    rank_field: str,
) -> dict[str, Any]:
    hits = {1: 0, 5: 0, 10: 0}
    total = len(queries)
    per_query_ranks: dict[str, int | None] = {}
    for query in queries:
        query_id = str(query["id"])
        gold_titles = [str(item) for item in query.get("evidence_titles", []) if str(item)]
        ranked = grouped_records.get(query_id, [])
        matched_rank = None
        for record in ranked:
            if hit_fn(record, gold_titles):
                matched_rank = int(record[rank_field])
                break
        per_query_ranks[query_id] = matched_rank
        for k in hits:
            if matched_rank is not None and matched_rank <= k:
                hits[k] += 1
    return {
        "query_count": total,
        "recall_at_1": hits[1] / max(total, 1),
        "recall_at_5": hits[5] / max(total, 1),
        "recall_at_10": hits[10] / max(total, 1),
        "top1_hits": hits[1],
        "per_query_ranks": per_query_ranks,
    }


def build_title_overlap_rerank(
    retrieval_records: list[dict[str, Any]],
    bm25_weight: float,
    title_weight: float,
) -> list[dict[str, Any]]:
    enriched_records = normalize_bm25(retrieval_records)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in enriched_records:
        overlap = title_overlap_score(str(record.get("query", "")), str(record.get("title", "")))
        improved = dict(record)
        improved["title_overlap_score"] = overlap
        improved["improved_score"] = bm25_weight * float(record["bm25_score_norm"]) + title_weight * overlap
        grouped[str(record["query_id"])].append(improved)

    improved_records: list[dict[str, Any]] = []
    for query_id, items in grouped.items():
        reranked = sorted(items, key=lambda item: float(item["improved_score"]), reverse=True)
        for rank, item in enumerate(reranked, start=1):
            item["improved_rank"] = rank
            improved_records.append(item)
    return improved_records


def top1_title(grouped_records: dict[str, list[dict[str, Any]]], query_id: str) -> str | None:
    items = grouped_records.get(query_id, [])
    return str(items[0].get("title")) if items else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Revalidate official FEVER baseline under strict gold-page matching.")
    parser.add_argument("--queries-path", required=True, help="Processed official FEVER queries jsonl.")
    parser.add_argument("--run-dir", required=True, help="Run directory with baseline retrieval results.")
    parser.add_argument("--bm25-weight", type=float, default=0.7)
    parser.add_argument("--title-weight", type=float, default=0.3)
    args = parser.parse_args()

    queries = read_jsonl(args.queries_path)
    run_dir = Path(args.run_dir)
    retrieval_records = read_jsonl(run_dir / "retrieval_results.jsonl")
    improved_records = build_title_overlap_rerank(
        retrieval_records=retrieval_records,
        bm25_weight=args.bm25_weight,
        title_weight=args.title_weight,
    )

    baseline_grouped = group_by_query(retrieval_records, "rank")
    improved_grouped = group_by_query(improved_records, "improved_rank")

    strict_baseline = compute_metrics(baseline_grouped, queries, strict_hit, "rank")
    strict_improved = compute_metrics(improved_grouped, queries, strict_hit, "improved_rank")
    relaxed_baseline = compute_metrics(baseline_grouped, queries, relaxed_hit, "rank")
    relaxed_improved = compute_metrics(improved_grouped, queries, relaxed_hit, "improved_rank")

    strict_improved_cases: list[dict[str, Any]] = []
    strict_regressed_cases: list[dict[str, Any]] = []
    relaxed_only_improvements: list[dict[str, Any]] = []
    still_strict_improvements: list[dict[str, Any]] = []

    for query in queries:
        query_id = str(query["id"])
        gold_titles = [str(item) for item in query.get("evidence_titles", []) if str(item)]
        baseline_strict_rank = strict_baseline["per_query_ranks"][query_id]
        improved_strict_rank = strict_improved["per_query_ranks"][query_id]
        baseline_relaxed_rank = relaxed_baseline["per_query_ranks"][query_id]
        improved_relaxed_rank = relaxed_improved["per_query_ranks"][query_id]
        row = {
            "query_id": query_id,
            "claim": query.get("claim"),
            "gold_label": query.get("label"),
            "gold_titles": gold_titles,
            "baseline_top1_title": top1_title(baseline_grouped, query_id),
            "improved_top1_title": top1_title(improved_grouped, query_id),
            "baseline_strict_rank": baseline_strict_rank,
            "improved_strict_rank": improved_strict_rank,
            "baseline_relaxed_rank": baseline_relaxed_rank,
            "improved_relaxed_rank": improved_relaxed_rank,
        }
        if baseline_strict_rank != 1 and improved_strict_rank == 1:
            strict_improved_cases.append(row)
            still_strict_improvements.append(row)
        if baseline_strict_rank == 1 and improved_strict_rank != 1:
            strict_regressed_cases.append(row)
        if baseline_relaxed_rank != 1 and improved_relaxed_rank == 1 and not (baseline_strict_rank != 1 and improved_strict_rank == 1):
            relaxed_only_improvements.append(row)

    result = {
        "selected_improvement": "bm25_score_plus_title_overlap_score",
        "weights": {
            "bm25_weight": args.bm25_weight,
            "title_weight": args.title_weight,
        },
        "strict_baseline": {
            "recall_at_1": strict_baseline["recall_at_1"],
            "recall_at_5": strict_baseline["recall_at_5"],
            "recall_at_10": strict_baseline["recall_at_10"],
            "top1_hits": strict_baseline["top1_hits"],
        },
        "strict_improved": {
            "recall_at_1": strict_improved["recall_at_1"],
            "recall_at_5": strict_improved["recall_at_5"],
            "recall_at_10": strict_improved["recall_at_10"],
            "top1_hits": strict_improved["top1_hits"],
        },
        "relaxed_baseline": {
            "recall_at_1": relaxed_baseline["recall_at_1"],
            "recall_at_5": relaxed_baseline["recall_at_5"],
            "recall_at_10": relaxed_baseline["recall_at_10"],
            "top1_hits": relaxed_baseline["top1_hits"],
        },
        "relaxed_improved": {
            "recall_at_1": relaxed_improved["recall_at_1"],
            "recall_at_5": relaxed_improved["recall_at_5"],
            "recall_at_10": relaxed_improved["recall_at_10"],
            "top1_hits": relaxed_improved["top1_hits"],
        },
        "strict_improved_case_count": len(strict_improved_cases),
        "strict_regressed_case_count": len(strict_regressed_cases),
        "strict_top1_delta": strict_improved["top1_hits"] - strict_baseline["top1_hits"],
        "relaxed_top1_delta": relaxed_improved["top1_hits"] - relaxed_baseline["top1_hits"],
        "relaxed_only_improved_case_count": len(relaxed_only_improvements),
        "strictly_valid_improved_case_count": len(still_strict_improvements),
    }

    lines = [
        "# Official Strict Evaluation Summary",
        "",
        "## Metric Definitions",
        "",
        "- Strict: a retrieved item counts only when its page title or doc_id exactly canonicalizes to one of the official `evidence_titles`.",
        "- Relaxed: a retrieved item counts when a gold title appears as a substring in title/text, or canonicalizes via doc_id.",
        "",
        "## Results",
        "",
        f"- Strict BM25 Recall@1 / @5 / @10: {strict_baseline['recall_at_1']:.4f} / {strict_baseline['recall_at_5']:.4f} / {strict_baseline['recall_at_10']:.4f}",
        f"- Strict BM25+title-overlap Recall@1 / @5 / @10: {strict_improved['recall_at_1']:.4f} / {strict_improved['recall_at_5']:.4f} / {strict_improved['recall_at_10']:.4f}",
        f"- Relaxed BM25 Recall@1 / @5 / @10: {relaxed_baseline['recall_at_1']:.4f} / {relaxed_baseline['recall_at_5']:.4f} / {relaxed_baseline['recall_at_10']:.4f}",
        f"- Relaxed BM25+title-overlap Recall@1 / @5 / @10: {relaxed_improved['recall_at_1']:.4f} / {relaxed_improved['recall_at_5']:.4f} / {relaxed_improved['recall_at_10']:.4f}",
        "",
        "## Improvement Validity",
        "",
        f"- Relaxed-only improvements that do not survive strict evaluation: {len(relaxed_only_improvements)}",
        f"- Improvements that still hold under strict evaluation: {len(still_strict_improvements)}",
        f"- Stable strict top1 gain: {strict_improved['top1_hits'] - strict_baseline['top1_hits']}",
    ]
    if relaxed_only_improvements:
        lines.extend(["", "## Relaxed-Only Improvements"])
        for item in relaxed_only_improvements:
            lines.append(
                f"- {item['query_id']}: `{item['baseline_top1_title']}` -> `{item['improved_top1_title']}`"
            )
    if still_strict_improvements:
        lines.extend(["", "## Strictly Valid Improvements"])
        for item in still_strict_improvements:
            lines.append(
                f"- {item['query_id']}: `{item['baseline_top1_title']}` -> `{item['improved_top1_title']}`"
            )

    write_json(run_dir / "official_strict_eval_results.json", result)
    write_jsonl(run_dir / "official_strict_improved_cases.jsonl", strict_improved_cases)
    write_jsonl(run_dir / "official_strict_regressed_cases.jsonl", strict_regressed_cases)
    (run_dir / "official_strict_eval_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
