from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import mean, median
from typing import Any

from src.analysis.official_strict_revalidation import (
    compute_metrics,
    group_by_query,
    relaxed_hit,
    strict_hit,
)
from src.common import read_json, read_jsonl, write_json


def as_queries(predictions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in predictions:
        rows.append(
            {
                "id": str(item["id"]),
                "claim": item.get("claim", ""),
                "label": item.get("gold_label", ""),
                "evidence_titles": [str(x) for x in item.get("gold_evidence", []) if str(x)],
            }
        )
    return rows


def reciprocal_rank(first_hit_rank: int | None) -> float:
    if first_hit_rank is None or first_hit_rank <= 0:
        return 0.0
    return 1.0 / first_hit_rank


def dcg_at_k(relevance: list[int], k: int) -> float:
    total = 0.0
    for idx, rel in enumerate(relevance[:k], start=1):
        if rel:
            total += 1.0 / math.log2(idx + 1)
    return total


def idcg_at_k(total_relevant: int, k: int) -> float:
    return dcg_at_k([1] * min(total_relevant, k), k)


def relevance_vector(records: list[dict[str, Any]], gold_titles: list[str], hit_fn) -> list[int]:
    return [1 if hit_fn(record, gold_titles) else 0 for record in records]


def average_ndcg(grouped_records: dict[str, list[dict[str, Any]]], queries: list[dict[str, Any]], hit_fn, rank_field: str, k: int) -> float:
    scores: list[float] = []
    for query in queries:
        query_id = str(query["id"])
        gold_titles = [str(x) for x in query.get("evidence_titles", []) if str(x)]
        records = sorted(grouped_records.get(query_id, []), key=lambda item: int(item[rank_field]))
        rels = relevance_vector(records, gold_titles, hit_fn)
        total_relevant = sum(rels)
        if total_relevant == 0:
            scores.append(0.0)
            continue
        dcg = dcg_at_k(rels, k)
        idcg = idcg_at_k(total_relevant, k)
        scores.append(dcg / idcg if idcg > 0 else 0.0)
    return mean(scores) if scores else 0.0


def first_hit_summary(per_query_ranks: dict[str, int | None]) -> dict[str, Any]:
    observed = [rank for rank in per_query_ranks.values() if rank is not None]
    return {
        "success_count": len(observed),
        "miss_count": sum(1 for rank in per_query_ranks.values() if rank is None),
        "mean_first_hit_rank": mean(observed) if observed else None,
        "median_first_hit_rank": median(observed) if observed else None,
    }


def budget_success(per_query_ranks: dict[str, int | None], budgets: list[int]) -> dict[str, float]:
    total = max(len(per_query_ranks), 1)
    return {
        f"success_at_{budget}": sum(1 for rank in per_query_ranks.values() if rank is not None and rank <= budget) / total
        for budget in budgets
    }


def evaluate_stage(grouped_records: dict[str, list[dict[str, Any]]], queries: list[dict[str, Any]], rank_field: str) -> dict[str, Any]:
    strict_metrics = compute_metrics(grouped_records, queries, strict_hit, rank_field)
    relaxed_metrics = compute_metrics(grouped_records, queries, relaxed_hit, rank_field)
    return {
        "strict": {
            "mrr": mean(reciprocal_rank(rank) for rank in strict_metrics["per_query_ranks"].values()),
            "ndcg_at_5": average_ndcg(grouped_records, queries, strict_hit, rank_field, 5),
            "ndcg_at_10": average_ndcg(grouped_records, queries, strict_hit, rank_field, 10),
            "first_hit_summary": first_hit_summary(strict_metrics["per_query_ranks"]),
            "budget_success": budget_success(strict_metrics["per_query_ranks"], [1, 3, 5, 10]),
        },
        "relaxed": {
            "mrr": mean(reciprocal_rank(rank) for rank in relaxed_metrics["per_query_ranks"].values()),
            "ndcg_at_5": average_ndcg(grouped_records, queries, relaxed_hit, rank_field, 5),
            "ndcg_at_10": average_ndcg(grouped_records, queries, relaxed_hit, rank_field, 10),
            "first_hit_summary": first_hit_summary(relaxed_metrics["per_query_ranks"]),
            "budget_success": budget_success(relaxed_metrics["per_query_ranks"], [1, 3, 5, 10]),
        },
    }


def markdown_summary(results: dict[str, Any]) -> str:
    lines = [
        "# Efficiency Frontier Summary",
        "",
        "## Main Table",
        "",
        "| stage | strict MRR | strict nDCG@5 | strict nDCG@10 | strict mean first-hit rank |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for stage, payload in results["stages"].items():
        first_hit = payload["strict"]["first_hit_summary"]["mean_first_hit_rank"]
        first_hit_text = "NA" if first_hit is None else f"{first_hit:.3f}"
        lines.append(
            f"| {stage} | {payload['strict']['mrr']:.3f} | {payload['strict']['ndcg_at_5']:.3f} | {payload['strict']['ndcg_at_10']:.3f} | {first_hit_text} |"
        )
    lines.extend(
        [
            "",
            "## Runtime / Cost Note",
            "",
            "- All stages reuse the same BM25 candidate pool.",
            "- No dense retriever, cross-encoder, or generation model is introduced.",
            "- Added cost is limited to lightweight string-level metadata scoring over the already retrieved top-k candidates.",
            "",
            "## Sentence Coverage",
            "",
            "- Gold evidence sentence coverage is left as a TODO in this local workspace because the processed disjoint FEVER file is not currently available here.",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute lightweight efficiency metrics for FEVER metadata-aware rerankers.")
    parser.add_argument("--source-run-dir", required=True)
    parser.add_argument("--family-run-dir", required=True)
    args = parser.parse_args()

    source_run_dir = Path(args.source_run_dir)
    family_run_dir = Path(args.family_run_dir)
    predictions = read_jsonl(source_run_dir / "predictions.jsonl")
    queries = as_queries(predictions)

    stages: dict[str, tuple[dict[str, list[dict[str, Any]]], str]] = {
        "routeA_bm25": (group_by_query(read_jsonl(source_run_dir / "retrieval_results.jsonl"), "rank"), "rank"),
    }
    for reranked_file in sorted(family_run_dir.glob("*_reranked_results.jsonl")):
        variant_name = reranked_file.stem.replace("_reranked_results", "")
        rank_field = f"{variant_name}_rank"
        stages[variant_name] = (group_by_query(read_jsonl(reranked_file), rank_field), rank_field)

    results = {
        "source_run_dir": str(source_run_dir),
        "family_run_dir": str(family_run_dir),
        "stages": {},
    }
    for stage_name, (grouped_records, rank_field) in stages.items():
        results["stages"][stage_name] = evaluate_stage(grouped_records, queries, rank_field)

    write_json(family_run_dir / "efficiency_results.json", results)
    (family_run_dir / "efficiency_summary.md").write_text(markdown_summary(results), encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
