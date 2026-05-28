from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.common import read_jsonl, write_json, write_jsonl

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "was",
    "were",
    "with",
}

TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+")
PAREN_PATTERN = re.compile(r"\s*\([^)]*\)")


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def content_tokens(text: str) -> set[str]:
    return {token for token in tokenize(text) if token not in STOPWORDS}


def base_title(title: str) -> str:
    return PAREN_PATTERN.sub("", title).strip()


def title_overlap_score(query: str, title: str) -> float:
    query_tokens = content_tokens(query)
    if not query_tokens:
        return 0.0
    title_tokens = content_tokens(title) | content_tokens(base_title(title))
    if not title_tokens:
        return 0.0
    return len(query_tokens & title_tokens) / len(query_tokens)


def normalize_bm25(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record["query_id"])].append(dict(record))

    normalized: list[dict[str, Any]] = []
    for query_id, items in grouped.items():
        scores = [float(item.get("bm25_score", 0.0)) for item in items]
        min_score = min(scores)
        max_score = max(scores)
        for item in items:
            raw_score = float(item.get("bm25_score", 0.0))
            if max_score == min_score:
                item["bm25_score_norm"] = 1.0 if raw_score > 0 else 0.0
            else:
                item["bm25_score_norm"] = (raw_score - min_score) / (max_score - min_score)
            normalized.append(item)
    return normalized


def group_by_query(records: list[dict[str, Any]], rank_field: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record["query_id"])].append(record)
    for query_id, items in grouped.items():
        grouped[query_id] = sorted(items, key=lambda item: int(item[rank_field]))
    return dict(grouped)


def gold_hit(record: dict[str, Any], gold_titles: list[str]) -> bool:
    title = str(record.get("title", "")).lower()
    text = str(record.get("text", "")).lower()
    for gold in gold_titles:
        gold_lower = str(gold).lower()
        if gold_lower and (gold_lower in title or gold_lower in text):
            return True
    return False


def gold_rank(records: list[dict[str, Any]], gold_titles: list[str], rank_field: str) -> int | None:
    for record in sorted(records, key=lambda item: int(item[rank_field])):
        if gold_hit(record, gold_titles):
            return int(record[rank_field])
    return None


def stage_metrics(grouped_records: dict[str, list[dict[str, Any]]], predictions: list[dict[str, Any]]) -> dict[str, Any]:
    hits = {1: 0, 5: 0, 10: 0}
    total = len(predictions)
    for prediction in predictions:
        query_id = str(prediction["id"])
        gold_titles = [str(item) for item in prediction.get("gold_evidence", []) if str(item)]
        ranked = grouped_records.get(query_id, [])
        for k in hits:
            if any(gold_hit(record, gold_titles) for record in ranked[:k]):
                hits[k] += 1
    return {
        "query_count": total,
        "recall_at_1": hits[1] / max(total, 1),
        "recall_at_5": hits[5] / max(total, 1),
        "recall_at_10": hits[10] / max(total, 1),
        "top1_hits": hits[1],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply a lightweight BM25 + title-overlap improvement.")
    parser.add_argument("--run-dir", required=True, help="Run directory with baseline retrieval outputs.")
    parser.add_argument("--bm25-weight", type=float, default=0.7)
    parser.add_argument("--title-weight", type=float, default=0.3)
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    retrieval_records = read_jsonl(run_dir / "retrieval_results.jsonl")
    predictions = read_jsonl(run_dir / "predictions.jsonl")

    enriched_records = normalize_bm25(retrieval_records)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in enriched_records:
        overlap = title_overlap_score(str(record.get("query", "")), str(record.get("title", "")))
        improved = dict(record)
        improved["title_overlap_score"] = overlap
        improved["improved_score"] = args.bm25_weight * float(record["bm25_score_norm"]) + args.title_weight * overlap
        grouped[str(record["query_id"])].append(improved)

    improved_records: list[dict[str, Any]] = []
    for query_id, items in grouped.items():
        reranked = sorted(items, key=lambda item: float(item["improved_score"]), reverse=True)
        for rank, item in enumerate(reranked, start=1):
            item["improved_rank"] = rank
            improved_records.append(item)

    baseline_grouped = group_by_query(retrieval_records, "rank")
    improved_grouped = group_by_query(improved_records, "improved_rank")
    baseline_metrics = stage_metrics(baseline_grouped, predictions)
    improved_metrics = stage_metrics(improved_grouped, predictions)

    improved_cases: list[dict[str, Any]] = []
    regressed_cases: list[dict[str, Any]] = []
    changed_cases = 0
    for prediction in predictions:
        query_id = str(prediction["id"])
        gold_titles = [str(item) for item in prediction.get("gold_evidence", []) if str(item)]
        baseline_rank = gold_rank(baseline_grouped.get(query_id, []), gold_titles, "rank")
        improved_rank = gold_rank(improved_grouped.get(query_id, []), gold_titles, "improved_rank")
        baseline_top1_hit = baseline_rank == 1
        improved_top1_hit = improved_rank == 1
        baseline_top1 = baseline_grouped.get(query_id, [{}])[0]
        improved_top1 = improved_grouped.get(query_id, [{}])[0]
        if str(baseline_top1.get("doc_id")) != str(improved_top1.get("doc_id")):
            changed_cases += 1
        if (not baseline_top1_hit) and improved_top1_hit:
            improved_cases.append(
                {
                    "query_id": query_id,
                    "claim": prediction.get("claim"),
                    "gold_label": prediction.get("gold_label"),
                    "gold_titles": gold_titles,
                    "baseline_rank": baseline_rank,
                    "improved_rank": improved_rank,
                    "baseline_top1_title": baseline_top1.get("title"),
                    "improved_top1_title": improved_top1.get("title"),
                }
            )
        if baseline_top1_hit and (not improved_top1_hit):
            regressed_cases.append(
                {
                    "query_id": query_id,
                    "claim": prediction.get("claim"),
                    "gold_label": prediction.get("gold_label"),
                    "gold_titles": gold_titles,
                    "baseline_rank": baseline_rank,
                    "improved_rank": improved_rank,
                    "baseline_top1_title": baseline_top1.get("title"),
                    "improved_top1_title": improved_top1.get("title"),
                }
            )

    result = {
        "selected_improvement": "bm25_score_plus_title_overlap_score",
        "weights": {
            "bm25_weight": args.bm25_weight,
            "title_weight": args.title_weight,
        },
        "baseline": baseline_metrics,
        "improved": improved_metrics,
        "top1_delta": improved_metrics["top1_hits"] - baseline_metrics["top1_hits"],
        "changed_top1_doc_count": changed_cases,
        "improved_case_count": len(improved_cases),
        "regressed_case_count": len(regressed_cases),
    }

    write_jsonl(run_dir / "official_improved_cases.jsonl", improved_cases)
    write_jsonl(run_dir / "official_regressed_cases.jsonl", regressed_cases)
    write_json(run_dir / "official_improvement_results.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
