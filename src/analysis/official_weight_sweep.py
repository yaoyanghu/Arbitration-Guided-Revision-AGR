from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.analysis.official_strict_revalidation import (
    build_title_overlap_rerank,
    compute_metrics,
    group_by_query,
    relaxed_hit,
    strict_hit,
)
from src.common import read_jsonl, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Sweep title-overlap weights under official strict/relaxed evaluation.")
    parser.add_argument("--queries-path", required=True, help="Processed official FEVER queries jsonl.")
    parser.add_argument("--run-dir", required=True, help="Run directory with baseline retrieval results.")
    args = parser.parse_args()

    queries = read_jsonl(args.queries_path)
    run_dir = Path(args.run_dir)
    retrieval_records = read_jsonl(run_dir / "retrieval_results.jsonl")
    baseline_grouped = group_by_query(retrieval_records, "rank")

    sweep_rows: list[dict[str, object]] = []
    best_strict = None
    for title_weight in [0.1, 0.2, 0.3, 0.4, 0.5]:
        bm25_weight = round(1.0 - title_weight, 1)
        improved_records = build_title_overlap_rerank(
            retrieval_records=retrieval_records,
            bm25_weight=bm25_weight,
            title_weight=title_weight,
        )
        improved_grouped = group_by_query(improved_records, "improved_rank")

        strict_baseline = compute_metrics(baseline_grouped, queries, strict_hit, "rank")
        strict_improved = compute_metrics(improved_grouped, queries, strict_hit, "improved_rank")
        relaxed_baseline = compute_metrics(baseline_grouped, queries, relaxed_hit, "rank")
        relaxed_improved = compute_metrics(improved_grouped, queries, relaxed_hit, "improved_rank")

        strict_improved_cases = 0
        strict_regressed_cases = 0
        for query in queries:
            query_id = str(query["id"])
            baseline_rank = strict_baseline["per_query_ranks"][query_id]
            improved_rank = strict_improved["per_query_ranks"][query_id]
            if baseline_rank != 1 and improved_rank == 1:
                strict_improved_cases += 1
            if baseline_rank == 1 and improved_rank != 1:
                strict_regressed_cases += 1

        row = {
            "variant_name": f"routeA_bm25_title_overlap_w{title_weight:.1f}",
            "bm25_weight": bm25_weight,
            "title_weight": title_weight,
            "strict_recall_at_1": strict_improved["recall_at_1"],
            "strict_recall_at_5": strict_improved["recall_at_5"],
            "strict_recall_at_10": strict_improved["recall_at_10"],
            "relaxed_recall_at_1": relaxed_improved["recall_at_1"],
            "relaxed_recall_at_5": relaxed_improved["recall_at_5"],
            "relaxed_recall_at_10": relaxed_improved["recall_at_10"],
            "strict_top1_hits": strict_improved["top1_hits"],
            "relaxed_top1_hits": relaxed_improved["top1_hits"],
            "strict_top1_delta": strict_improved["top1_hits"] - strict_baseline["top1_hits"],
            "relaxed_top1_delta": relaxed_improved["top1_hits"] - relaxed_baseline["top1_hits"],
            "strict_improved_case_count": strict_improved_cases,
            "strict_regressed_case_count": strict_regressed_cases,
        }
        sweep_rows.append(row)
        if best_strict is None or (
            row["strict_top1_hits"],
            -row["strict_regressed_case_count"],
            row["relaxed_top1_hits"],
        ) > (
            best_strict["strict_top1_hits"],
            -best_strict["strict_regressed_case_count"],
            best_strict["relaxed_top1_hits"],
        ):
            best_strict = row

    payload = {
        "baseline_name": "routeA_bm25",
        "improved_family_name": "routeA_bm25_title_overlap",
        "sweep_results": sweep_rows,
        "best_by_strict_top1": best_strict,
    }
    write_json(run_dir / "official_weight_sweep_results.json", payload)

    lines = [
        "# Official Weight Sweep Summary",
        "",
        "- Baseline: `routeA_bm25`",
        "- Improved family: `routeA_bm25_title_overlap`",
        "",
        "## Sweep",
        "",
    ]
    for row in sweep_rows:
        lines.append(
            f"- title_weight={row['title_weight']:.1f}, bm25_weight={row['bm25_weight']:.1f}: "
            f"strict R@1/R@5/R@10 = {row['strict_recall_at_1']:.4f}/{row['strict_recall_at_5']:.4f}/{row['strict_recall_at_10']:.4f}, "
            f"strict delta = {row['strict_top1_delta']}, strict improved/regressed = "
            f"{row['strict_improved_case_count']}/{row['strict_regressed_case_count']}"
        )
    lines.extend(
        [
            "",
            "## Best Weight",
            "",
            f"- Best by strict top1: title_weight={best_strict['title_weight']:.1f}, bm25_weight={best_strict['bm25_weight']:.1f}",
            f"- Strict top1 hits: {best_strict['strict_top1_hits']} (delta {best_strict['strict_top1_delta']})",
            f"- Relaxed top1 hits: {best_strict['relaxed_top1_hits']} (delta {best_strict['relaxed_top1_delta']})",
        ]
    )
    (run_dir / "official_weight_sweep_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
