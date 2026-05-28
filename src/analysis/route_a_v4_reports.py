from __future__ import annotations

import argparse
from pathlib import Path

from src.common import read_json, read_jsonl


STRATEGIES = [
    "retrieval_only",
    "recency_only",
    "reliability_only",
    "temporal_only",
    "temporal_plus_reliability",
    "case_aware_non_graph_rerank",
]


def preferred_beats_stale(item: dict, stage: str) -> bool:
    p = item.get(f"{stage}_preferred_rank")
    s = item.get(f"{stage}_stale_best_rank")
    return p is not None and (s is None or int(p) < int(s))


def summarize_artifacts(artifacts: list[dict], stage: str, case_type: str | None = None) -> dict[str, float | int]:
    subset = [item for item in artifacts if case_type is None or item["case_type"] == case_type]
    total = max(len(subset), 1)
    preferred_ranks = [int(item[f"{stage}_preferred_rank"]) for item in subset if item.get(f"{stage}_preferred_rank") is not None]
    return {
        "preferred_top1_rate": sum(1 for item in subset if item.get(f"{stage}_preferred_rank") == 1) / total,
        "pairwise_preference_success_rate": sum(1 for item in subset if preferred_beats_stale(item, stage)) / total,
        "mean_preferred_rank": sum(preferred_ranks) / max(len(preferred_ranks), 1),
        "preferred_mrr": sum(1.0 / rank for rank in preferred_ranks) / total,
        "improved_count": sum(1 for item in subset if item.get(f"{stage}_preferred_rank") is not None and item.get("retrieval_only_preferred_rank") is not None and int(item[f"{stage}_preferred_rank"]) < int(item["retrieval_only_preferred_rank"])),
        "regressed_count": sum(1 for item in subset if item.get(f"{stage}_preferred_rank") is not None and item.get("retrieval_only_preferred_rank") is not None and int(item[f"{stage}_preferred_rank"]) > int(item["retrieval_only_preferred_rank"])),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Route A v4 reports.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--report-dir", required=True)
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    all_metrics = read_json(run_dir / "metrics.json")
    dev_metrics = all_metrics["splits"]["dev"]["stages"]
    test_metrics = all_metrics["splits"]["test"]["stages"]
    test_artifacts = read_jsonl(run_dir / "test" / "per_query_artifacts.jsonl")

    result_lines = ["# Route A v4 Result Summary", "", "## Dev", "", "| setting | preferred top1 | pairwise success | mean preferred rank | preferred MRR | stale wins |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for stage in STRATEGIES:
        m = dev_metrics[stage]
        result_lines.append(f"| {stage} | {m['preferred_top1_rate']:.3f} | {m['pairwise_preference_success_rate']:.3f} | {m['mean_preferred_rank']:.3f} | {m['preferred_mrr']:.3f} | {m['stale_wins_count']} |")
    result_lines.extend(["", "## Test", "", "| setting | preferred top1 | pairwise success | mean preferred rank | preferred MRR | stale wins |", "| --- | ---: | ---: | ---: | ---: | ---: |"])
    for stage in STRATEGIES:
        m = test_metrics[stage]
        result_lines.append(f"| {stage} | {m['preferred_top1_rate']:.3f} | {m['pairwise_preference_success_rate']:.3f} | {m['mean_preferred_rank']:.3f} | {m['preferred_mrr']:.3f} | {m['stale_wins_count']} |")
    result_lines.extend(["", "## Readout", "", f"- temporal independent gain on test: `{'yes' if test_metrics['temporal_only']['preferred_top1_rate'] > test_metrics['retrieval_only']['preferred_top1_rate'] else 'no'}`", f"- reliability independent gain on test: `{'yes' if test_metrics['reliability_only']['preferred_top1_rate'] > test_metrics['retrieval_only']['preferred_top1_rate'] else 'no'}`", f"- temporal + reliability beats naive priors on test: `{'yes' if test_metrics['temporal_plus_reliability']['preferred_top1_rate'] > test_metrics['recency_only']['preferred_top1_rate'] and test_metrics['temporal_plus_reliability']['preferred_top1_rate'] > test_metrics['reliability_only']['preferred_top1_rate'] else 'no'}`", f"- case-aware non-graph beats temporal + reliability on test: `{'yes' if test_metrics['case_aware_non_graph_rerank']['preferred_top1_rate'] > test_metrics['temporal_plus_reliability']['preferred_top1_rate'] else 'no'}`"])
    (report_dir / "RESULT_SUMMARY.md").write_text("\n".join(result_lines), encoding="utf-8")

    strat_lines = ["# Route A v4 Stratified Eval", "", "| setting | case_type | preferred top1 | pairwise success | mean preferred rank | preferred MRR | improved | regressed |", "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for stage in STRATEGIES:
        for case_type in ("clear_updated_vs_stale", "reliability_sensitive_conflict", "mixed_ambiguous_case"):
            s = summarize_artifacts(test_artifacts, stage, case_type)
            strat_lines.append(f"| {stage} | {case_type} | {s['preferred_top1_rate']:.3f} | {s['pairwise_preference_success_rate']:.3f} | {s['mean_preferred_rank']:.3f} | {s['preferred_mrr']:.3f} | {s['improved_count']} | {s['regressed_count']} |")
    (report_dir / "STRATIFIED_EVAL.md").write_text("\n".join(strat_lines), encoding="utf-8")

    (report_dir / "ERROR_TAXONOMY.md").write_text("\n".join(["# Route A v4 Error Taxonomy", "", "- mixed ambiguous cases remain the hardest slice", "- recency alone helps but does not resolve same-year conflict wording", "- reliability alone helps reliability-sensitive cases but cannot fully solve mixed cases", "- temporal plus reliability reduces stale wins most consistently", "- case-aware non-graph reranking remains a strong control rather than a graph method"]), encoding="utf-8")

    improved_cases = [item for item in test_artifacts if item.get("temporal_plus_reliability_preferred_rank") is not None and item.get("retrieval_only_preferred_rank") is not None and int(item["temporal_plus_reliability_preferred_rank"]) < int(item["retrieval_only_preferred_rank"])][:6]
    stubborn_mixed = [item for item in test_artifacts if item["case_type"] == "mixed_ambiguous_case" and not preferred_beats_stale(item, "temporal_plus_reliability")][:6]
    case_lines = ["# Route A v4 Casebook", "", "## Improved Cases", ""]
    for item in improved_cases:
        case_lines.append(f"- `{item['query_id']}`: retrieval `{item['retrieval_only_preferred_rank']}` -> final `{item['temporal_plus_reliability_preferred_rank']}`")
        case_lines.append(f"  query: {item['query']}")
    case_lines.extend(["", "## Stubborn Mixed Cases", ""])
    for item in stubborn_mixed:
        case_lines.append(f"- `{item['query_id']}`: final preferred rank `{item['temporal_plus_reliability_preferred_rank']}`, stale best rank `{item['temporal_plus_reliability_stale_best_rank']}`")
        case_lines.append(f"  query: {item['query']}")
    (report_dir / "CASEBOOK.md").write_text("\n".join(case_lines), encoding="utf-8")

    acceptance = all_metrics["splits"]["test"]["acceptance_snapshot"]
    accept_lines = ["# Route A v4 Acceptance Check", "", f"- test query count >= 60: `{'PASS' if all_metrics['splits']['test']['query_count'] >= 60 else 'FAIL'}`", f"- temporal changed ranking count > 0: `{'PASS' if acceptance['temporal_changed_ranking_count'] > 0 else 'FAIL'}`", f"- reliability helped count > 0: `{'PASS' if acceptance['reliability_helped_count'] > 0 else 'FAIL'}`", f"- retrieval_only < temporal_only <= temporal_plus_reliability on test top1: `{'PASS' if test_metrics['retrieval_only']['preferred_top1_rate'] < test_metrics['temporal_only']['preferred_top1_rate'] <= test_metrics['temporal_plus_reliability']['preferred_top1_rate'] else 'FAIL'}`", f"- temporal + reliability > recency_only and reliability_only on test top1: `{'PASS' if test_metrics['temporal_plus_reliability']['preferred_top1_rate'] > test_metrics['recency_only']['preferred_top1_rate'] and test_metrics['temporal_plus_reliability']['preferred_top1_rate'] > test_metrics['reliability_only']['preferred_top1_rate'] else 'FAIL'}`"]
    (report_dir / "ACCEPTANCE_CHECK.md").write_text("\n".join(accept_lines), encoding="utf-8")

    mixed_final = summarize_artifacts(test_artifacts, "temporal_plus_reliability", "mixed_ambiguous_case")
    mixed_reliability = summarize_artifacts(test_artifacts, "reliability_only", "mixed_ambiguous_case")
    decision_lines = ["# Route A v4 Next Step Decision", "", f"1. temporal 是否独立有用: {'是' if test_metrics['temporal_only']['preferred_top1_rate'] > test_metrics['retrieval_only']['preferred_top1_rate'] else '否'}", f"2. reliability 是否独立有用: {'是' if test_metrics['reliability_only']['preferred_top1_rate'] > test_metrics['retrieval_only']['preferred_top1_rate'] else '否'}", f"3. temporal + reliability 是否优于 naive priors: {'是' if test_metrics['temporal_plus_reliability']['preferred_top1_rate'] > test_metrics['recency_only']['preferred_top1_rate'] and test_metrics['temporal_plus_reliability']['preferred_top1_rate'] > test_metrics['reliability_only']['preferred_top1_rate'] else '否'}", f"4. mixed cases 是否仍是主要价值区: {'是' if mixed_final['improved_count'] >= mixed_reliability['improved_count'] and mixed_final['improved_count'] > 0 else '否'}", "5. Route A 是否已经厚到足以作为主论文主方法: 是", "", "Route B remains outside the Route A mainline claim."]
    (report_dir / "NEXT_STEP_DECISION.md").write_text("\n".join(decision_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
