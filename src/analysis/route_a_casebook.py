from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.common import read_json, read_jsonl


def load_top_cases(artifacts: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    improved = []
    reliability_helped = []
    failures = []
    for item in artifacts:
        raw_rank = item.get("raw_preferred_rank")
        temp_rank = item.get("temporal_preferred_rank")
        final_rank = item.get("final_preferred_rank")
        final_stale = item.get("final_stale_best_rank")
        if raw_rank is not None and final_rank is not None and final_rank < raw_rank:
            improved.append(item)
        if temp_rank is not None and final_rank is not None and final_rank < temp_rank:
            reliability_helped.append(item)
        if final_stale is not None and (final_rank is None or final_stale < final_rank):
            failures.append(item)
    return improved[:5], reliability_helped[:5], failures[:5]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Route A acceptance reports from run artifacts.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--report-dir", required=True)
    parser.add_argument("--min-query-count", type=int, default=1)
    parser.add_argument("--min-temporal-changed", type=int, default=1)
    parser.add_argument("--min-reliability-helped", type=int, default=1)
    parser.add_argument("--min-pairwise-gain", type=float, default=0.0)
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    metrics = read_json(run_dir / "metrics.json")
    artifacts = read_jsonl(run_dir / "per_query_artifacts.jsonl")
    improved, reliability_helped, failures = load_top_cases(artifacts)
    pairwise_gain = (
        metrics["stages"]["temporal_plus_reliability"]["pairwise_preference_success_rate"]
        - metrics["stages"]["retrieval_only"]["pairwise_preference_success_rate"]
    )

    acceptance_lines = [
        "# Acceptance Check",
        "",
        "## README Acceptance Criteria",
        "",
        f"1. End-to-end small real subset run: {'PASS' if metrics['query_count'] >= args.min_query_count else 'FAIL'}",
        f"2. Temporal signal measurably changes ranking: {'PASS' if metrics['acceptance_snapshot']['temporal_changed_ranking_count'] >= args.min_temporal_changed else 'FAIL'}",
        f"3. Updated evidence beats retrieval-only baseline: {'PASS' if pairwise_gain >= args.min_pairwise_gain else 'FAIL'}",
        f"4. Reliability helps some conflict cases: {'PASS' if metrics['acceptance_snapshot']['reliability_helped_count'] >= args.min_reliability_helped else 'FAIL'}",
        f"5. Per-query inspectable artifacts exist: {'PASS' if len(artifacts) == metrics['query_count'] else 'FAIL'}",
        "",
        "## Gate Thresholds",
        "",
        f"- min_query_count: `{args.min_query_count}`",
        f"- min_temporal_changed: `{args.min_temporal_changed}`",
        f"- min_reliability_helped: `{args.min_reliability_helped}`",
        f"- min_pairwise_gain: `{args.min_pairwise_gain:.3f}`",
        "",
        "## Metrics Snapshot",
        "",
        "```json",
        json.dumps(metrics, ensure_ascii=False, indent=2),
        "```",
    ]
    (report_dir / "ACCEPTANCE_CHECK.md").write_text("\n".join(acceptance_lines), encoding="utf-8")

    error_lines = [
        "# Error Taxonomy",
        "",
        f"- stale_still_wins_cases: {metrics['stages']['temporal_plus_reliability']['stale_wins_count']}",
        f"- temporal_changed_ranking_count: {metrics['acceptance_snapshot']['temporal_changed_ranking_count']}",
        f"- reliability_helped_count: {metrics['acceptance_snapshot']['reliability_helped_count']}",
        "",
        "## Main Error Buckets",
        "",
        "- stale candidate still lexically competitive",
        "- temporal signal can help but not always enough to move the preferred candidate to rank 1",
        "- reliability prior is intentionally weak and only breaks some near-ties",
        "- some blog-style conflicting candidates remain sticky because they reuse many query words",
    ]
    (report_dir / "ERROR_TAXONOMY.md").write_text("\n".join(error_lines), encoding="utf-8")

    result_lines = [
        "# Result Summary",
        "",
        "| stage | preferred top1 | pairwise success | mean preferred rank | preferred MRR | stale wins |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for stage_name, stage_metrics in metrics["stages"].items():
        result_lines.append(
            f"| {stage_name} | {stage_metrics['preferred_top1_rate']:.3f} | {stage_metrics['pairwise_preference_success_rate']:.3f} | {stage_metrics['mean_preferred_rank']:.3f} | {stage_metrics['preferred_mrr']:.3f} | {stage_metrics['stale_wins_count']} |"
        )
    result_lines.extend(
        [
            "",
            "## Delta vs Retrieval-Only",
            "",
            f"- temporal-only pairwise delta: `{metrics['stages']['temporal_only']['pairwise_preference_success_rate'] - metrics['stages']['retrieval_only']['pairwise_preference_success_rate']:.3f}`",
            f"- final pairwise delta: `{pairwise_gain:.3f}`",
            f"- temporal changed ranking count: `{metrics['acceptance_snapshot']['temporal_changed_ranking_count']}`",
            f"- reliability helped count: `{metrics['acceptance_snapshot']['reliability_helped_count']}`",
            f"- final better than retrieval count: `{metrics['acceptance_snapshot']['final_better_than_retrieval_count']}`",
        ]
    )
    (report_dir / "RESULT_SUMMARY.md").write_text("\n".join(result_lines), encoding="utf-8")

    case_lines = ["# Casebook", "", "## Improved Cases", ""]
    for item in improved:
        case_lines.append(f"- `{item['query_id']}`: raw preferred rank `{item['raw_preferred_rank']}` -> final `{item['final_preferred_rank']}`")
        case_lines.append(f"  query: {item['query']}")
    case_lines.extend(["", "## Reliability-Helped Cases", ""])
    for item in reliability_helped:
        case_lines.append(f"- `{item['query_id']}`: temporal preferred rank `{item['temporal_preferred_rank']}` -> final `{item['final_preferred_rank']}`")
        case_lines.append(f"  query: {item['query']}")
    case_lines.extend(["", "## Failure Cases", ""])
    for item in failures:
        case_lines.append(f"- `{item['query_id']}`: final preferred rank `{item['final_preferred_rank']}`, final stale best rank `{item['final_stale_best_rank']}`")
        case_lines.append(f"  query: {item['query']}")
    (report_dir / "CASEBOOK.md").write_text("\n".join(case_lines), encoding="utf-8")

    all_pass = (
        metrics["query_count"] >= args.min_query_count
        and metrics["acceptance_snapshot"]["temporal_changed_ranking_count"] >= args.min_temporal_changed
        and pairwise_gain >= args.min_pairwise_gain
        and metrics["acceptance_snapshot"]["reliability_helped_count"] >= args.min_reliability_helped
        and len(artifacts) == metrics["query_count"]
    )
    decision_lines = ["# Next Step Decision", "", f"A. 现在是否允许进入 Route B 主实验: {'允许' if all_pass else '不允许'}"]
    if all_pass:
        decision_lines.extend(
            [
                "",
                "B. Route A hardened gate 已满足。",
                "",
                "C. 如果进入 Route B，最小原型应该只做：",
                "- 对 Route A top-k 结果构建一个轻量局部 evidence graph",
                "- 只验证 graph 是否帮助少数 temporal-conflict hard cases",
                "- 不引入 generation 或大 sweep",
            ]
        )
    else:
        decision_lines.extend(
            [
                "",
                "B. Route A 还差的 1-2 个硬缺口：",
                "- temporal 或 reliability 的增益还不够稳定，未达到 hardened gate",
                "- subset 规模或 case type 覆盖还不够支撑 Route B prototype run",
                "",
                "C. 因此现在不应进入 Route B prototype run。",
            ]
        )
    (report_dir / "NEXT_STEP_DECISION.md").write_text("\n".join(decision_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
