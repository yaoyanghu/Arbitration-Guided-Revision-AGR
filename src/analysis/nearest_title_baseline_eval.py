from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

from src.analysis.official_strict_revalidation import (
    canonical_title,
    compute_metrics,
    group_by_query,
    relaxed_hit,
    strict_hit,
)
from src.analysis.official_title_overlap_improvement import (
    PAREN_PATTERN,
    normalize_bm25,
    title_overlap_score,
)
from src.common import ensure_dir, read_jsonl, write_json, write_jsonl


def base_title(title: str) -> str:
    return PAREN_PATTERN.sub("", title).strip()


def normalize_text(text: str) -> str:
    normalized = canonical_title(text)
    normalized = re.sub(r"[^a-z0-9()\\[\\]{}\\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return f" {normalized} " if normalized else " "


def exact_title_match_score(query: str, title: str) -> float:
    query_text = normalize_text(query)
    candidates = []
    for candidate in (title, base_title(title)):
        candidate_norm = normalize_text(candidate)
        if candidate_norm.strip():
            candidates.append(candidate_norm)
    for candidate in candidates:
        if candidate in query_text:
            return 1.0
    return 0.0


def build_rerank(
    retrieval_records: list[dict[str, Any]],
    bm25_weight: float,
    title_weight: float,
    title_score_fn: Callable[[str, str], float],
    title_score_field: str,
    rerank_score_field: str,
    rank_field: str,
) -> list[dict[str, Any]]:
    enriched_records = normalize_bm25(retrieval_records)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in enriched_records:
        title_score = title_score_fn(str(record.get("query", "")), str(record.get("title", "")))
        updated = dict(record)
        updated[title_score_field] = title_score
        updated[rerank_score_field] = bm25_weight * float(record["bm25_score_norm"]) + title_weight * title_score
        grouped[str(record["query_id"])].append(updated)

    reranked_records: list[dict[str, Any]] = []
    for query_id, items in grouped.items():
        reranked = sorted(
            items,
            key=lambda item: (float(item[rerank_score_field]), float(item.get("bm25_score_norm", 0.0))),
            reverse=True,
        )
        for rank, item in enumerate(reranked, start=1):
            item[rank_field] = rank
            reranked_records.append(item)
    return reranked_records


def top1_title(grouped_records: dict[str, list[dict[str, Any]]], query_id: str) -> str | None:
    items = grouped_records.get(query_id, [])
    return str(items[0].get("title")) if items else None


def compare_cases(
    queries: list[dict[str, Any]],
    baseline_grouped: dict[str, list[dict[str, Any]]],
    candidate_grouped: dict[str, list[dict[str, Any]]],
    baseline_metrics: dict[str, Any],
    candidate_metrics: dict[str, Any],
    candidate_name: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    improved_cases: list[dict[str, Any]] = []
    regressed_cases: list[dict[str, Any]] = []
    for query in queries:
        query_id = str(query["id"])
        gold_titles = [str(item) for item in query.get("evidence_titles", []) if str(item)]
        baseline_rank = baseline_metrics["per_query_ranks"][query_id]
        candidate_rank = candidate_metrics["per_query_ranks"][query_id]
        row = {
            "query_id": query_id,
            "claim": query.get("claim"),
            "gold_label": query.get("label"),
            "gold_titles": gold_titles,
            "baseline_top1_title": top1_title(baseline_grouped, query_id),
            "candidate_top1_title": top1_title(candidate_grouped, query_id),
            "baseline_strict_rank": baseline_rank,
            "candidate_strict_rank": candidate_rank,
            "candidate_name": candidate_name,
        }
        if baseline_rank != 1 and candidate_rank == 1:
            improved_cases.append(row)
        if baseline_rank == 1 and candidate_rank != 1:
            regressed_cases.append(row)
    return improved_cases, regressed_cases


def as_query_rows(predictions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    queries: list[dict[str, Any]] = []
    for item in predictions:
        queries.append(
            {
                "id": str(item["id"]),
                "claim": item.get("claim", ""),
                "label": item.get("gold_label", ""),
                "evidence_titles": [str(x) for x in item.get("gold_evidence", []) if str(x)],
            }
        )
    return queries


def summarize_variant(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "recall_at_1": metrics["recall_at_1"],
        "recall_at_5": metrics["recall_at_5"],
        "recall_at_10": metrics["recall_at_10"],
        "top1_hits": metrics["top1_hits"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare exact-title-match boost against title-overlap reranking.")
    parser.add_argument("--source-run-dir", required=True, help="Existing run directory with retrieval_results.jsonl and predictions.jsonl.")
    parser.add_argument("--output-run-dir", required=True, help="Directory to write nearest-baseline analysis artifacts.")
    parser.add_argument("--bm25-weight", type=float, default=0.5)
    parser.add_argument("--title-weight", type=float, default=0.5)
    args = parser.parse_args()

    source_run_dir = Path(args.source_run_dir)
    output_run_dir = ensure_dir(args.output_run_dir)

    retrieval_records = read_jsonl(source_run_dir / "retrieval_results.jsonl")
    predictions = read_jsonl(source_run_dir / "predictions.jsonl")
    queries = as_query_rows(predictions)

    baseline_grouped = group_by_query(retrieval_records, "rank")
    baseline_strict = compute_metrics(baseline_grouped, queries, strict_hit, "rank")
    baseline_relaxed = compute_metrics(baseline_grouped, queries, relaxed_hit, "rank")

    exact_records = build_rerank(
        retrieval_records=retrieval_records,
        bm25_weight=args.bm25_weight,
        title_weight=args.title_weight,
        title_score_fn=exact_title_match_score,
        title_score_field="exact_title_match_score",
        rerank_score_field="exact_title_boost_score",
        rank_field="exact_title_rank",
    )
    overlap_records = build_rerank(
        retrieval_records=retrieval_records,
        bm25_weight=args.bm25_weight,
        title_weight=args.title_weight,
        title_score_fn=title_overlap_score,
        title_score_field="title_overlap_score",
        rerank_score_field="title_overlap_rerank_score",
        rank_field="title_overlap_rank",
    )

    exact_grouped = group_by_query(exact_records, "exact_title_rank")
    overlap_grouped = group_by_query(overlap_records, "title_overlap_rank")

    exact_strict = compute_metrics(exact_grouped, queries, strict_hit, "exact_title_rank")
    exact_relaxed = compute_metrics(exact_grouped, queries, relaxed_hit, "exact_title_rank")
    overlap_strict = compute_metrics(overlap_grouped, queries, strict_hit, "title_overlap_rank")
    overlap_relaxed = compute_metrics(overlap_grouped, queries, relaxed_hit, "title_overlap_rank")

    exact_improved, exact_regressed = compare_cases(
        queries, baseline_grouped, exact_grouped, baseline_strict, exact_strict, "routeA_bm25_exact_title_boost"
    )
    overlap_improved, overlap_regressed = compare_cases(
        queries, baseline_grouped, overlap_grouped, baseline_strict, overlap_strict, "routeA_bm25_title_overlap"
    )

    overlap_only_wins: list[dict[str, Any]] = []
    exact_only_wins: list[dict[str, Any]] = []
    for query in queries:
        query_id = str(query["id"])
        base_rank = baseline_strict["per_query_ranks"][query_id]
        exact_rank = exact_strict["per_query_ranks"][query_id]
        overlap_rank = overlap_strict["per_query_ranks"][query_id]
        row = {
            "query_id": query_id,
            "claim": query.get("claim"),
            "gold_label": query.get("label"),
            "gold_titles": query.get("evidence_titles", []),
            "baseline_top1_title": top1_title(baseline_grouped, query_id),
            "exact_top1_title": top1_title(exact_grouped, query_id),
            "title_overlap_top1_title": top1_title(overlap_grouped, query_id),
            "baseline_strict_rank": base_rank,
            "exact_strict_rank": exact_rank,
            "title_overlap_strict_rank": overlap_rank,
        }
        if base_rank != 1 and exact_rank != 1 and overlap_rank == 1:
            overlap_only_wins.append(row)
        if base_rank != 1 and exact_rank == 1 and overlap_rank != 1:
            exact_only_wins.append(row)

    result = {
        "dataset": "official_fever_disjoint_1000",
        "weights": {
            "bm25_weight": args.bm25_weight,
            "title_weight": args.title_weight,
        },
        "baseline_name": "routeA_bm25",
        "nearest_title_baseline_name": "routeA_bm25_exact_title_boost",
        "title_overlap_name": "routeA_bm25_title_overlap",
        "strict": {
            "baseline": summarize_variant(baseline_strict),
            "exact_title_boost": summarize_variant(exact_strict),
            "title_overlap": summarize_variant(overlap_strict),
        },
        "relaxed": {
            "baseline": summarize_variant(baseline_relaxed),
            "exact_title_boost": summarize_variant(exact_relaxed),
            "title_overlap": summarize_variant(overlap_relaxed),
        },
        "deltas": {
            "exact_title_boost_vs_bm25_strict_top1_delta": exact_strict["top1_hits"] - baseline_strict["top1_hits"],
            "title_overlap_vs_bm25_strict_top1_delta": overlap_strict["top1_hits"] - baseline_strict["top1_hits"],
            "title_overlap_vs_exact_title_boost_strict_top1_delta": overlap_strict["top1_hits"] - exact_strict["top1_hits"],
            "exact_title_boost_vs_bm25_relaxed_top1_delta": exact_relaxed["top1_hits"] - baseline_relaxed["top1_hits"],
            "title_overlap_vs_bm25_relaxed_top1_delta": overlap_relaxed["top1_hits"] - baseline_relaxed["top1_hits"],
            "title_overlap_vs_exact_title_boost_relaxed_top1_delta": overlap_relaxed["top1_hits"] - exact_relaxed["top1_hits"],
        },
        "case_counts": {
            "exact_title_boost_strict_improved_case_count": len(exact_improved),
            "exact_title_boost_strict_regressed_case_count": len(exact_regressed),
            "title_overlap_strict_improved_case_count": len(overlap_improved),
            "title_overlap_strict_regressed_case_count": len(overlap_regressed),
            "title_overlap_only_wins_over_exact_case_count": len(overlap_only_wins),
            "exact_title_only_wins_over_overlap_case_count": len(exact_only_wins),
        },
    }

    summary_lines = [
        "# Nearest Title Baseline Results",
        "",
        "## Setup",
        "",
        "- Source run: `runs/fever_official_route_a_disjoint_1000/`",
        "- Candidate pool: unchanged BM25 retrieval candidates",
        "- Compared systems:",
        "  - `routeA_bm25`",
        "  - `routeA_bm25_exact_title_boost`",
        "  - `routeA_bm25_title_overlap`",
        f"- Fixed weights for both title-aware methods: `bm25_weight={args.bm25_weight}`, `title_weight={args.title_weight}`",
        "",
        "## Strict Results",
        "",
        f"- BM25 Recall@1 / @5 / @10: {baseline_strict['recall_at_1']:.3f} / {baseline_strict['recall_at_5']:.3f} / {baseline_strict['recall_at_10']:.3f}",
        f"- BM25 + exact title match boost: {exact_strict['recall_at_1']:.3f} / {exact_strict['recall_at_5']:.3f} / {exact_strict['recall_at_10']:.3f}",
        f"- BM25 + title overlap: {overlap_strict['recall_at_1']:.3f} / {overlap_strict['recall_at_5']:.3f} / {overlap_strict['recall_at_10']:.3f}",
        "",
        "## Relaxed Results",
        "",
        f"- BM25 Recall@1 / @5 / @10: {baseline_relaxed['recall_at_1']:.3f} / {baseline_relaxed['recall_at_5']:.3f} / {baseline_relaxed['recall_at_10']:.3f}",
        f"- BM25 + exact title match boost: {exact_relaxed['recall_at_1']:.3f} / {exact_relaxed['recall_at_5']:.3f} / {exact_relaxed['recall_at_10']:.3f}",
        f"- BM25 + title overlap: {overlap_relaxed['recall_at_1']:.3f} / {overlap_relaxed['recall_at_5']:.3f} / {overlap_relaxed['recall_at_10']:.3f}",
        "",
        "## Head-to-Head Answer",
        "",
    ]

    strict_delta = overlap_strict["top1_hits"] - exact_strict["top1_hits"]
    relaxed_delta = overlap_relaxed["top1_hits"] - exact_relaxed["top1_hits"]
    if strict_delta > 0:
        summary_lines.extend(
            [
                f"- Under strict evaluation, title overlap outperforms the simpler exact-title baseline by `+{strict_delta}` top1 hits.",
                f"- Under relaxed evaluation, title overlap outperforms the simpler exact-title baseline by `+{relaxed_delta}` top1 hits.",
                f"- Title overlap wins exclusively on `{len(overlap_only_wins)}` queries, while exact title boost wins exclusively on `{len(exact_only_wins)}` queries.",
                "- Interpretation: token-level overlap helps when the claim mentions most of a page title but not as a contiguous exact phrase, so it rescues cases that a binary exact-title feature misses.",
            ]
        )
    elif strict_delta < 0:
        summary_lines.extend(
            [
                f"- Under strict evaluation, title overlap underperforms exact title boost by `{strict_delta}` top1 hits.",
                f"- Under relaxed evaluation, title overlap differs by `{relaxed_delta}` top1 hits.",
                "- Interpretation: the simpler exact-title heuristic is at least as strong as token-level overlap on this split.",
            ]
        )
    else:
        summary_lines.extend(
            [
                "- Under strict evaluation, title overlap ties the simpler exact-title baseline at top1.",
                f"- Under relaxed evaluation, the difference is `{relaxed_delta}` top1 hits.",
                "- Interpretation: token-level overlap does not provide a clear advantage over the nearest simpler title-aware heuristic on this split.",
            ]
        )

    table_lines = [
        "# Nearest Title Baseline Table",
        "",
        "| setting | strict R@1 | strict R@5 | strict R@10 | relaxed R@1 | relaxed R@5 | relaxed R@10 | strict top1 delta vs BM25 | strict improved | strict regressed |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        f"| routeA_bm25 | {baseline_strict['recall_at_1']:.3f} | {baseline_strict['recall_at_5']:.3f} | {baseline_strict['recall_at_10']:.3f} | {baseline_relaxed['recall_at_1']:.3f} | {baseline_relaxed['recall_at_5']:.3f} | {baseline_relaxed['recall_at_10']:.3f} | 0 | 0 | 0 |",
        f"| routeA_bm25_exact_title_boost | {exact_strict['recall_at_1']:.3f} | {exact_strict['recall_at_5']:.3f} | {exact_strict['recall_at_10']:.3f} | {exact_relaxed['recall_at_1']:.3f} | {exact_relaxed['recall_at_5']:.3f} | {exact_relaxed['recall_at_10']:.3f} | {exact_strict['top1_hits'] - baseline_strict['top1_hits']} | {len(exact_improved)} | {len(exact_regressed)} |",
        f"| routeA_bm25_title_overlap | {overlap_strict['recall_at_1']:.3f} | {overlap_strict['recall_at_5']:.3f} | {overlap_strict['recall_at_10']:.3f} | {overlap_relaxed['recall_at_1']:.3f} | {overlap_relaxed['recall_at_5']:.3f} | {overlap_relaxed['recall_at_10']:.3f} | {overlap_strict['top1_hits'] - baseline_strict['top1_hits']} | {len(overlap_improved)} | {len(overlap_regressed)} |",
    ]

    write_json(output_run_dir / "nearest_title_baseline_results.json", result)
    write_jsonl(output_run_dir / "exact_title_boost_reranked_results.jsonl", exact_records)
    write_jsonl(output_run_dir / "title_overlap_reranked_results.jsonl", overlap_records)
    write_jsonl(output_run_dir / "exact_title_boost_strict_improved_cases.jsonl", exact_improved)
    write_jsonl(output_run_dir / "exact_title_boost_strict_regressed_cases.jsonl", exact_regressed)
    write_jsonl(output_run_dir / "title_overlap_strict_improved_cases.jsonl", overlap_improved)
    write_jsonl(output_run_dir / "title_overlap_strict_regressed_cases.jsonl", overlap_regressed)
    write_jsonl(output_run_dir / "title_overlap_only_wins_over_exact_cases.jsonl", overlap_only_wins)
    write_jsonl(output_run_dir / "exact_title_only_wins_over_overlap_cases.jsonl", exact_only_wins)
    (output_run_dir / "nearest_title_baseline_summary.md").write_text("\n".join(summary_lines), encoding="utf-8")
    (output_run_dir / "nearest_title_baseline_table.md").write_text("\n".join(table_lines), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
