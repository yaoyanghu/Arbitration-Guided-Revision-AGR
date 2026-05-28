from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from src.analysis.official_strict_revalidation import (
    build_title_overlap_rerank,
    compute_metrics,
    group_by_query,
    strict_hit,
)
from src.common import read_jsonl, write_json


def label_subset_metrics(
    grouped_records: dict[str, list[dict[str, object]]],
    queries: list[dict[str, object]],
    label: str,
    rank_field: str,
) -> dict[str, float | int]:
    subset = [query for query in queries if str(query.get("label")) == label]
    metrics = compute_metrics(grouped_records, subset, strict_hit, rank_field)
    return {
        "count": len(subset),
        "strict_recall_at_1": metrics["recall_at_1"],
        "strict_recall_at_5": metrics["recall_at_5"],
        "strict_recall_at_10": metrics["recall_at_10"],
        "strict_top1_hits": metrics["top1_hits"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute label-wise strict metrics for official title-overlap baseline.")
    parser.add_argument("--queries-path", required=True, help="Processed official FEVER queries jsonl.")
    parser.add_argument("--run-dir", required=True, help="Run directory with retrieval results.")
    parser.add_argument("--bm25-weight", type=float, default=0.5)
    parser.add_argument("--title-weight", type=float, default=0.5)
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

    result = {
        "weights": {
            "bm25_weight": args.bm25_weight,
            "title_weight": args.title_weight,
        },
        "baseline": {
            "SUPPORTS": label_subset_metrics(baseline_grouped, queries, "SUPPORTS", "rank"),
            "REFUTES": label_subset_metrics(baseline_grouped, queries, "REFUTES", "rank"),
        },
        "title_overlap": {
            "SUPPORTS": label_subset_metrics(improved_grouped, queries, "SUPPORTS", "improved_rank"),
            "REFUTES": label_subset_metrics(improved_grouped, queries, "REFUTES", "improved_rank"),
        },
    }
    write_json(run_dir / "official_labelwise_results.json", result)
    summary_lines = [
        "# Official Labelwise Strict Summary",
        "",
        f"- Weights: bm25={args.bm25_weight:.1f}, title_overlap={args.title_weight:.1f}",
        "",
        "## Baseline BM25",
        "",
        f"- SUPPORTS strict Recall@1 / @5 / @10: {result['baseline']['SUPPORTS']['strict_recall_at_1']:.4f} / {result['baseline']['SUPPORTS']['strict_recall_at_5']:.4f} / {result['baseline']['SUPPORTS']['strict_recall_at_10']:.4f}",
        f"- REFUTES strict Recall@1 / @5 / @10: {result['baseline']['REFUTES']['strict_recall_at_1']:.4f} / {result['baseline']['REFUTES']['strict_recall_at_5']:.4f} / {result['baseline']['REFUTES']['strict_recall_at_10']:.4f}",
        "",
        "## BM25 + Title Overlap",
        "",
        f"- SUPPORTS strict Recall@1 / @5 / @10: {result['title_overlap']['SUPPORTS']['strict_recall_at_1']:.4f} / {result['title_overlap']['SUPPORTS']['strict_recall_at_5']:.4f} / {result['title_overlap']['SUPPORTS']['strict_recall_at_10']:.4f}",
        f"- REFUTES strict Recall@1 / @5 / @10: {result['title_overlap']['REFUTES']['strict_recall_at_1']:.4f} / {result['title_overlap']['REFUTES']['strict_recall_at_5']:.4f} / {result['title_overlap']['REFUTES']['strict_recall_at_10']:.4f}",
    ]
    (run_dir / "official_labelwise_summary.md").write_text("\n".join(summary_lines), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
