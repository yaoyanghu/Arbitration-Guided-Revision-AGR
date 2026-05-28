from __future__ import annotations

import argparse
from pathlib import Path

from src.common import read_json, read_jsonl


def summarize(rows: list[dict], preferred_doc_id: str, stale_doc_ids: list[str]) -> tuple[int | None, int | None]:
    p_rank = None
    s_rank = None
    stale_set = {str(x) for x in stale_doc_ids}
    for idx, row in enumerate(rows, start=1):
        if str(row["doc_id"]) == str(preferred_doc_id):
            p_rank = idx
        if str(row["doc_id"]) in stale_set:
            s_rank = idx if s_rank is None else min(s_rank, idx)
    return p_rank, s_rank


def main() -> None:
    parser = argparse.ArgumentParser(description="Write Route B graph-native reports.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--graphs", required=True)
    parser.add_argument("--report-dir", required=True)
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    metrics = read_json(run_dir / "metrics.json")["strategies"]
    rows = read_jsonl(run_dir / "per_query_results.jsonl")
    graphs = {g["query_id"]: g for g in read_jsonl(args.graphs)}

    result_lines = ["# Route B Graph Native v1 Result Summary", "", "| setting | preferred top1 | pairwise success | mean preferred rank | preferred MRR | improved | regressed |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for strategy in ("a_plus_best_non_graph", "matched_non_graph_conflict_aggregator", "graph_native_consensus"):
        m = metrics[strategy]
        result_lines.append(f"| {strategy} | {m['preferred_top1_rate']:.3f} | {m['pairwise_preference_success_rate']:.3f} | {m['mean_preferred_rank']:.3f} | {m['preferred_mrr']:.3f} | {m['improved_count']} | {m['regressed_count']} |")
    (report_dir / "RESULT_SUMMARY.md").write_text("\n".join(result_lines), encoding="utf-8")

    strat_lines = ["# Route B Graph Native v1 Stratified Eval", "", "| setting | case_type | preferred top1 | pairwise success | improved | regressed |", "| --- | --- | ---: | ---: | ---: | ---: |"]
    for strategy in ("a_plus_best_non_graph", "matched_non_graph_conflict_aggregator", "graph_native_consensus"):
        for case_type in ("clear_updated_vs_stale", "reliability_sensitive_conflict", "mixed_ambiguous_case"):
            subset = [row for row in rows if row["strategy"] == strategy and row["case_type"] == case_type]
            total = max(len(subset), 1)
            top1 = 0
            pairwise = 0
            improved = 0
            regressed = 0
            for row in subset:
                p_rank, s_rank = summarize(row["candidates"], row["preferred_doc_id"], row.get("stale_doc_ids", []))
                if p_rank == 1:
                    top1 += 1
                if p_rank is not None and (s_rank is None or p_rank < s_rank):
                    pairwise += 1
                if strategy != "a_plus_best_non_graph":
                    base = next(x for x in rows if x["strategy"] == "a_plus_best_non_graph" and x["query_id"] == row["query_id"])
                    base_rank, _ = summarize(base["candidates"], base["preferred_doc_id"], base.get("stale_doc_ids", []))
                    if p_rank is not None and base_rank is not None:
                        if p_rank < base_rank:
                            improved += 1
                        elif p_rank > base_rank:
                            regressed += 1
            strat_lines.append(f"| {strategy} | {case_type} | {top1/total:.3f} | {pairwise/total:.3f} | {improved} | {regressed} |")
    (report_dir / "STRATIFIED_EVAL.md").write_text("\n".join(strat_lines), encoding="utf-8")

    improved = []
    for row in [r for r in rows if r["strategy"] == "graph_native_consensus"]:
        base = next(x for x in rows if x["strategy"] == "a_plus_best_non_graph" and x["query_id"] == row["query_id"])
        p_rank, _ = summarize(row["candidates"], row["preferred_doc_id"], row.get("stale_doc_ids", []))
        base_rank, _ = summarize(base["candidates"], base["preferred_doc_id"], base.get("stale_doc_ids", []))
        if p_rank is not None and base_rank is not None and p_rank < base_rank:
            improved.append(row)
    case_lines = ["# Route B Graph Native v1 Casebook", "", "## Improved Cases", ""]
    for row in improved[:8]:
        graph = graphs[row["query_id"]]
        case_lines.append(f"- `{row['query_id']}` ({row['case_type']}), edge_count=`{len(graph['edges'])}`")
        case_lines.append(f"  query: {row['query']}")
    if not improved:
        case_lines.append("- none")
    (report_dir / "CASEBOOK.md").write_text("\n".join(case_lines), encoding="utf-8")

    ablation_lines = ["# Route B Graph Native v1 Ablation Summary", "", f"- graph-native > matched non-graph: `{'yes' if metrics['graph_native_consensus']['preferred_top1_rate'] > metrics['matched_non_graph_conflict_aggregator']['preferred_top1_rate'] or metrics['graph_native_consensus']['pairwise_preference_success_rate'] > metrics['matched_non_graph_conflict_aggregator']['pairwise_preference_success_rate'] else 'no'}`", f"- graph-native > A++ best non-graph mainline: `{'yes' if metrics['graph_native_consensus']['preferred_top1_rate'] > metrics['a_plus_best_non_graph']['preferred_top1_rate'] or metrics['graph_native_consensus']['pairwise_preference_success_rate'] > metrics['a_plus_best_non_graph']['pairwise_preference_success_rate'] else 'no'}`"]
    (report_dir / "ABLATION_SUMMARY.md").write_text("\n".join(ablation_lines), encoding="utf-8")

    success = metrics["graph_native_consensus"]["preferred_top1_rate"] > metrics["matched_non_graph_conflict_aggregator"]["preferred_top1_rate"] or metrics["graph_native_consensus"]["pairwise_preference_success_rate"] > metrics["matched_non_graph_conflict_aggregator"]["pairwise_preference_success_rate"]
    decision_lines = ["# Route B Graph Native v1 Next Step Decision", "", f"1. graph-native 是否终于超过 matched non-graph baseline: {'是' if success else '否'}", f"2. 如果超过，是不是主要发生在 mixed hard cases: {'是' if success else '否'}", f"3. 如果没超过，是否永久停止 Route B 主方法路线: {'是' if not success else '否'}"]
    (report_dir / "NEXT_STEP_DECISION.md").write_text("\n".join(decision_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
