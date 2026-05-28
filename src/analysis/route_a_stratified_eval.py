from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from statistics import mean

from src.common import read_json, read_jsonl


def summarize_case_type(items: list[dict]) -> dict[str, float | int]:
    total = len(items)
    top1 = sum(1 for item in items if item["preferred_rank"] == 1) / total
    pairwise = sum(1 for item in items if item["preferred_beats_stale"]) / total
    mean_rank = mean(item["preferred_rank"] for item in items)
    mrr = sum(1.0 / item["preferred_rank"] for item in items) / total
    improved = sum(1 for item in items if item["improved"])
    regressed = sum(1 for item in items if item["regressed"])
    return {
        "preferred_top1_rate": top1,
        "pairwise_preference_success_rate": pairwise,
        "mean_preferred_rank": mean_rank,
        "preferred_mrr": mrr,
        "improved_count": improved,
        "regressed_count": regressed,
    }


def build_stage_rows(queries: list[dict], artifacts: list[dict], stage_key: str) -> dict[str, list[dict]]:
    case_type_map = {str(query["id"]): str(query["case_type"]) for query in queries}
    rows: dict[str, list[dict]] = defaultdict(list)
    for item in artifacts:
        query_id = str(item["query_id"])
        preferred_rank = item.get(f"{stage_key}_preferred_rank")
        stale_rank = item.get(f"{stage_key}_stale_best_rank")
        if preferred_rank is None:
            continue
        rows[case_type_map[query_id]].append(
            {
                "preferred_rank": int(preferred_rank),
                "preferred_beats_stale": stale_rank is None or int(preferred_rank) < int(stale_rank),
                "improved": item.get("raw_preferred_rank") is not None and int(preferred_rank) < int(item["raw_preferred_rank"]),
                "regressed": item.get("raw_preferred_rank") is not None and int(preferred_rank) > int(item["raw_preferred_rank"]),
            }
        )
    return rows


def render_markdown(metrics: dict, queries: list[dict], artifacts: list[dict]) -> str:
    lines = [
        "# Stratified Eval",
        "",
        "| stage | case_type | preferred top1 | pairwise success | mean preferred rank | preferred MRR | improved | regressed |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for stage_name, stage_key in (
        ("retrieval_only", "raw"),
        ("temporal_only", "temporal"),
        ("temporal_plus_reliability", "final"),
    ):
        grouped = build_stage_rows(queries, artifacts, stage_key)
        for case_type in ("clear_updated_vs_stale", "reliability_sensitive_conflict", "mixed_ambiguous_case"):
            summary = summarize_case_type(grouped[case_type])
            lines.append(
                f"| {stage_name} | {case_type} | {summary['preferred_top1_rate']:.3f} | {summary['pairwise_preference_success_rate']:.3f} | {summary['mean_preferred_rank']:.3f} | {summary['preferred_mrr']:.3f} | {summary['improved_count']} | {summary['regressed_count']} |"
            )
    lines.extend(
        [
            "",
            "## Readout",
            "",
            f"- query_count: `{metrics['query_count']}`",
            f"- temporal changed ranking count: `{metrics['acceptance_snapshot']['temporal_changed_ranking_count']}`",
            f"- reliability helped count: `{metrics['acceptance_snapshot']['reliability_helped_count']}`",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create Route A stratified evaluation report.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    metrics = read_json(run_dir / "metrics.json")
    queries = read_jsonl(run_dir / "queries.jsonl")
    artifacts = read_jsonl(run_dir / "per_query_artifacts.jsonl")
    Path(args.output).write_text(render_markdown(metrics, queries, artifacts), encoding="utf-8")


if __name__ == "__main__":
    main()
