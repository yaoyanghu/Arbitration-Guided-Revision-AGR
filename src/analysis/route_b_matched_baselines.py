from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from typing import Any

from src.common import ensure_dir, read_jsonl


def entity_key(doc_id: str) -> str:
    return doc_id.rsplit("_", 1)[0] if "_" in doc_id else doc_id


def preferred_rank(records: list[dict[str, Any]], preferred_doc_id: str) -> int | None:
    for idx, record in enumerate(records, start=1):
        if str(record.get("doc_id")) == preferred_doc_id:
            return idx
    return None


def stale_best_rank(records: list[dict[str, Any]], stale_doc_ids: list[str]) -> int | None:
    stale_set = set(stale_doc_ids)
    best = None
    for idx, record in enumerate(records, start=1):
        if str(record.get("doc_id")) in stale_set:
            best = idx if best is None else min(best, idx)
    return best


def incoming_for_subset(graph: dict[str, Any], allowed: set[str]) -> dict[str, dict[str, float]]:
    totals: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for edge in graph.get("edges", []):
        relation = str(edge["relation"])
        if relation not in allowed:
            continue
        totals[str(edge["target"])][relation] += float(edge.get("weight", 0.0))
    return totals


def outgoing_for_subset(graph: dict[str, Any], allowed: set[str]) -> dict[str, dict[str, float]]:
    totals: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for edge in graph.get("edges", []):
        relation = str(edge["relation"])
        if relation not in allowed:
            continue
        totals[str(edge["source"])][relation] += float(edge.get("weight", 0.0))
    return totals


def graph_score(candidate: dict[str, Any], incoming: dict[str, float], outgoing: dict[str, float]) -> float:
    base = float(candidate.get("final_score", 0.0))
    boost = 0.0
    boost += incoming.get("support", 0.0) * 0.30
    boost += incoming.get("update", 0.0) * 0.45
    boost += incoming.get("corroborate", 0.0) * 0.40
    penalty = 0.0
    penalty += outgoing.get("update", 0.0) * 0.35
    penalty += outgoing.get("contradict", 0.0) * 0.25
    if str(candidate.get("temporal_status")) == "conflicting" and (incoming.get("contradict", 0.0) > 0 or outgoing.get("contradict", 0.0) > 0):
        penalty += 0.04
    return base + boost - penalty


def non_graph_case_aware_score(candidate: dict[str, Any], case_type: str, preferred_doc_id: str) -> float:
    base = float(candidate.get("final_score", 0.0))
    status = str(candidate.get("temporal_status", ""))
    reliability = float(candidate.get("reliability_score", 0.0))
    same_entity = entity_key(str(candidate.get("doc_id"))) == entity_key(str(preferred_doc_id))

    score = base
    if not same_entity:
        return score

    if case_type == "clear_updated_vs_stale":
        if status == "updated":
            score += 0.16 + 0.06 * reliability
        elif status == "stale":
            score -= 0.10
        elif status == "conflicting":
            score -= 0.08
    elif case_type == "reliability_sensitive_conflict":
        if status == "updated":
            score += 0.14 + 0.10 * reliability
        elif status == "conflicting":
            score -= 0.10
        elif status == "stale":
            score -= 0.03
    else:
        if status == "updated":
            score += 0.18 + 0.08 * reliability
        elif status == "stale":
            score -= 0.09
        elif status == "conflicting":
            score -= 0.06
    return score


def rerank_with_strategy(
    graph: dict[str, Any],
    artifact: dict[str, Any],
    strategy: str,
) -> list[dict[str, Any]]:
    candidates = [dict(item) for item in artifact.get("final_candidates", [])[: int(graph.get("top_k", 5))]]
    if strategy == "a_only":
        reranked = candidates
    elif strategy == "case_aware_non_graph":
        reranked = []
        for candidate in candidates:
            enriched = dict(candidate)
            enriched["matched_score"] = non_graph_case_aware_score(candidate, str(graph.get("case_type", "")), str(artifact["preferred_doc_id"]))
            reranked.append(enriched)
        reranked = sorted(reranked, key=lambda item: float(item["matched_score"]), reverse=True)
    else:
        allowed = {
            "update_only": {"update"},
            "full_graph": {"support", "corroborate", "update", "contradict"},
        }[strategy]
        incoming = incoming_for_subset(graph, allowed)
        outgoing = outgoing_for_subset(graph, allowed)
        reranked = []
        for candidate in candidates:
            enriched = dict(candidate)
            node_id = f"evidence::{candidate['doc_id']}"
            enriched["matched_score"] = graph_score(candidate, incoming.get(node_id, {}), outgoing.get(node_id, {}))
            reranked.append(enriched)
        reranked = sorted(reranked, key=lambda item: float(item["matched_score"]), reverse=True)
    for rank, item in enumerate(reranked, start=1):
        item["matched_rank"] = rank
    return reranked


def summarize(items: list[dict[str, Any]], key: str) -> dict[str, Any]:
    top1 = 0
    pairwise = 0
    preferred_ranks: list[int] = []
    stale_wins = 0
    improved = 0
    regressed = 0
    for item in items:
        records = item[key]
        p_rank = preferred_rank(records, str(item["preferred_doc_id"]))
        s_rank = stale_best_rank(records, [str(x) for x in item.get("stale_doc_ids", [])])
        route_a_rank = item.get("route_a_final_rank")
        if records and str(records[0].get("doc_id")) == str(item["preferred_doc_id"]):
            top1 += 1
        if p_rank is not None:
            preferred_ranks.append(p_rank)
        if p_rank is not None and (s_rank is None or p_rank < s_rank):
            pairwise += 1
        if s_rank is not None and (p_rank is None or s_rank < p_rank):
            stale_wins += 1
        if route_a_rank is not None and p_rank is not None:
            if p_rank < route_a_rank:
                improved += 1
            elif p_rank > route_a_rank:
                regressed += 1
    total = max(len(items), 1)
    return {
        "query_count": len(items),
        "preferred_top1_rate": top1 / total,
        "pairwise_preference_success_rate": pairwise / total,
        "mean_preferred_rank": sum(preferred_ranks) / max(len(preferred_ranks), 1),
        "preferred_mrr": sum(1.0 / rank for rank in preferred_ranks) / total,
        "stale_wins_count": stale_wins,
        "improved_count": improved,
        "regressed_count": regressed,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate matched Route B baselines and stratified case-type metrics.")
    parser.add_argument("--graph-input", required=True)
    parser.add_argument("--route-a-artifacts", required=True)
    parser.add_argument("--report-dir", required=True)
    parser.add_argument("--summary-name", default="MATCHED_BASELINES.md")
    parser.add_argument("--stratified-name", default="STRATIFIED_EVAL.md")
    args = parser.parse_args()

    report_dir = ensure_dir(args.report_dir)
    graphs = read_jsonl(args.graph_input)
    artifacts = {item["query_id"]: item for item in read_jsonl(args.route_a_artifacts)}

    strategies = ["a_only", "update_only", "case_aware_non_graph", "full_graph"]
    per_strategy: dict[str, list[dict[str, Any]]] = {}
    for strategy in strategies:
        per_query = []
        for graph in graphs:
            artifact = artifacts[str(graph["query_id"])]
            reranked = rerank_with_strategy(graph, artifact, strategy)
            per_query.append(
                {
                    "query_id": artifact["query_id"],
                    "case_type": str(graph.get("case_type")),
                    "preferred_doc_id": artifact["preferred_doc_id"],
                    "stale_doc_ids": artifact.get("stale_doc_ids", []),
                    "route_a_final_rank": artifact.get("final_preferred_rank"),
                    "candidates": reranked,
                }
            )
        per_strategy[strategy] = per_query

    summary_lines = [
        "# Matched Baselines",
        "",
        "| setting | preferred top1 | pairwise success | mean preferred rank | preferred MRR | improved | regressed |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    results: dict[str, dict[str, Any]] = {}
    for strategy in strategies:
        metrics = summarize(per_strategy[strategy], "candidates")
        results[strategy] = metrics
        summary_lines.append(
            f"| {strategy} | {metrics['preferred_top1_rate']:.3f} | {metrics['pairwise_preference_success_rate']:.3f} | {metrics['mean_preferred_rank']:.3f} | {metrics['preferred_mrr']:.3f} | {metrics['improved_count']} | {metrics['regressed_count']} |"
        )

    summary_lines.extend(
        [
            "",
            "## Readout",
            "",
            f"- graph 是否优于同信息量 non-graph 聚合器: {'是' if results['full_graph']['preferred_top1_rate'] > results['case_aware_non_graph']['preferred_top1_rate'] or results['full_graph']['pairwise_preference_success_rate'] > results['case_aware_non_graph']['pairwise_preference_success_rate'] else '否'}",
            f"- graph 是否优于 update_only: {'是' if results['full_graph']['preferred_top1_rate'] > results['update_only']['preferred_top1_rate'] or results['full_graph']['pairwise_preference_success_rate'] > results['update_only']['pairwise_preference_success_rate'] else '否'}",
            "- 如果 graph 不优于 matched baselines，则当前 gain 更像 conflict-aware rule aggregation 而不是独立 graph method。",
        ]
    )
    (Path(report_dir) / args.summary_name).write_text("\n".join(summary_lines), encoding="utf-8")

    stratified_lines = [
        "# Stratified Eval",
        "",
        "| setting | case_type | preferred top1 | pairwise success | mean preferred rank | preferred MRR | improved | regressed |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for strategy in strategies:
        for case_type in ["clear_updated_vs_stale", "reliability_sensitive_conflict", "mixed_ambiguous_case"]:
            subset = [item for item in per_strategy[strategy] if item["case_type"] == case_type]
            metrics = summarize(subset, "candidates")
            stratified_lines.append(
                f"| {strategy} | {case_type} | {metrics['preferred_top1_rate']:.3f} | {metrics['pairwise_preference_success_rate']:.3f} | {metrics['mean_preferred_rank']:.3f} | {metrics['preferred_mrr']:.3f} | {metrics['improved_count']} | {metrics['regressed_count']} |"
            )

    stratified_lines.extend(
        [
            "",
            "## Readout",
            "",
            "- graph 的收益是不是主要只在 mixed cases: 看 `full_graph` 相对其他 setting 在 `mixed_ambiguous_case` 上的 improved / regressed。",
            "- clear / reliability-sensitive 上 graph 是否只是中性: 看 `clear_updated_vs_stale` 与 `reliability_sensitive_conflict` 的 full_graph 与 matched baselines 差值。",
            "- 如果 graph 只对 mixed cases 有用，它仍可以支持一个 conflict-focused Route B 定位，但不足以支撑更一般化的 graph retrieval claim。",
        ]
    )
    (Path(report_dir) / args.stratified_name).write_text("\n".join(stratified_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
