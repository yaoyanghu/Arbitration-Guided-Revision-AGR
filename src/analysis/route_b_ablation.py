from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.common import ensure_dir, read_jsonl


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


def incoming_for_subset(graph: dict[str, Any], allowed: set[str]) -> dict[str, Counter[str]]:
    totals: dict[str, Counter[str]] = defaultdict(Counter)
    for edge in graph.get("edges", []):
        relation = str(edge["relation"])
        if relation not in allowed:
            continue
        totals[str(edge["target"])][relation] += float(edge.get("weight", 0.0))
    return totals


def outgoing_for_subset(graph: dict[str, Any], allowed: set[str]) -> dict[str, Counter[str]]:
    totals: dict[str, Counter[str]] = defaultdict(Counter)
    for edge in graph.get("edges", []):
        relation = str(edge["relation"])
        if relation not in allowed:
            continue
        totals[str(edge["source"])][relation] += float(edge.get("weight", 0.0))
    return totals


def score_candidate(candidate: dict[str, Any], incoming: Counter[str], outgoing: Counter[str]) -> float:
    base = float(candidate.get("final_score", 0.0))
    boost = 0.0
    boost += incoming.get("support", 0.0) * 0.30
    boost += incoming.get("update", 0.0) * 0.45
    boost += incoming.get("corroborate", 0.0) * 0.40
    penalty = 0.0
    penalty += outgoing.get("update", 0.0) * 0.35
    penalty += outgoing.get("contradict", 0.0) * 0.25
    if "contradict" in incoming or "contradict" in outgoing:
        penalty += 0.04 if str(candidate.get("temporal_status")) == "conflicting" else 0.0
    return base + boost - penalty


def stage_summary(per_query: list[dict[str, Any]], key: str) -> dict[str, Any]:
    top1 = 0
    pairwise = 0
    preferred_ranks: list[int] = []
    stale_wins = 0
    for item in per_query:
        records = item[key]
        p_rank = preferred_rank(records, str(item["preferred_doc_id"]))
        s_rank = stale_best_rank(records, [str(x) for x in item.get("stale_doc_ids", [])])
        if records and str(records[0]["doc_id"]) == str(item["preferred_doc_id"]):
            top1 += 1
        if p_rank is not None:
            preferred_ranks.append(p_rank)
        if p_rank is not None and (s_rank is None or p_rank < s_rank):
            pairwise += 1
        if s_rank is not None and (p_rank is None or s_rank < p_rank):
            stale_wins += 1
    total = max(len(per_query), 1)
    return {
        "query_count": len(per_query),
        "preferred_top1_rate": top1 / total,
        "pairwise_preference_success_rate": pairwise / total,
        "mean_preferred_rank": sum(preferred_ranks) / max(len(preferred_ranks), 1),
        "preferred_mrr": sum(1.0 / rank for rank in preferred_ranks) / total,
        "stale_wins_count": stale_wins,
    }


def run_ablation(graphs: list[dict[str, Any]], artifacts: dict[str, dict[str, Any]], allowed: set[str]) -> list[dict[str, Any]]:
    per_query: list[dict[str, Any]] = []
    for graph in graphs:
        artifact = artifacts[str(graph["query_id"])]
        incoming = incoming_for_subset(graph, allowed)
        outgoing = outgoing_for_subset(graph, allowed)
        reranked = []
        for candidate in artifact.get("final_candidates", [])[: int(graph.get("top_k", 5))]:
            scored = dict(candidate)
            node_id = f"evidence::{candidate['doc_id']}"
            scored["ablation_score"] = score_candidate(candidate, incoming.get(node_id, Counter()), outgoing.get(node_id, Counter()))
            reranked.append(scored)
        reranked = sorted(reranked, key=lambda item: float(item["ablation_score"]), reverse=True)
        for rank, item in enumerate(reranked, start=1):
            item["ablation_rank"] = rank
        per_query.append(
            {
                "query_id": artifact["query_id"],
                "preferred_doc_id": artifact["preferred_doc_id"],
                "stale_doc_ids": artifact.get("stale_doc_ids", []),
                "case_type": str(artifact["query_id"]).split("_")[-1],
                "graph_candidates": reranked,
            }
        )
    return per_query


def main() -> None:
    parser = argparse.ArgumentParser(description="Route B v1 ablation and diversity analysis.")
    parser.add_argument("--graph-input", required=True)
    parser.add_argument("--route-a-artifacts", required=True)
    parser.add_argument("--report-dir", required=True)
    args = parser.parse_args()

    graphs = read_jsonl(args.graph_input)
    artifacts = {item["query_id"]: item for item in read_jsonl(args.route_a_artifacts)}
    report_dir = ensure_dir(args.report_dir)

    ablations = {
        "a_only": set(),
        "update_only": {"update"},
        "contradict_only": {"contradict"},
        "support_corroborate_only": {"support", "corroborate"},
        "full_graph": {"support", "corroborate", "update", "contradict"},
    }

    summary_lines = [
        "# Route B v1 Ablation Summary",
        "",
        "| setting | preferred top1 | pairwise success | mean preferred rank | preferred MRR | stale wins |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    full_metrics = None
    for name, allowed in ablations.items():
        per_query = []
        if name == "a_only":
            for artifact in artifacts.values():
                per_query.append(
                    {
                        "query_id": artifact["query_id"],
                        "preferred_doc_id": artifact["preferred_doc_id"],
                        "stale_doc_ids": artifact.get("stale_doc_ids", []),
                        "graph_candidates": artifact.get("final_candidates", [])[:5],
                    }
                )
        else:
            per_query = run_ablation(graphs, artifacts, allowed)
        metrics = stage_summary(per_query, "graph_candidates")
        if name == "full_graph":
            full_metrics = metrics
        summary_lines.append(
            f"| {name} | {metrics['preferred_top1_rate']:.3f} | {metrics['pairwise_preference_success_rate']:.3f} | {metrics['mean_preferred_rank']:.3f} | {metrics['preferred_mrr']:.3f} | {metrics['stale_wins_count']} |"
        )

    summary_lines.extend(
        [
            "",
            "## Readout",
            "",
            "- If `update_only` is close to `full_graph`, most gain comes from update edges.",
            "- If `support_corroborate_only` is near `a_only`, these edges mainly reweight existing preferences.",
            "- If `contradict_only` barely moves results, contradiction is diagnostic but not the main driver.",
        ]
    )
    (Path(report_dir) / "ABLATION_SUMMARY.md").write_text("\n".join(summary_lines), encoding="utf-8")

    pattern_counter = Counter()
    pattern_by_case = defaultdict(Counter)
    edge_counts = []
    for graph in graphs:
        items = tuple(sorted((k, int(v)) for k, v in graph.get("edge_type_counts", {}).items()))
        pattern_counter[items] += 1
        case_type = str(graph["query_id"]).split("_")[-1]
        pattern_by_case[case_type][items] += 1
        edge_counts.append(int(sum(graph.get("edge_type_counts", {}).values())))

    diversity_lines = [
        "# Route B v1 Graph Diversity Report",
        "",
        f"- query count: `{len(graphs)}`",
        f"- min edge count: `{min(edge_counts) if edge_counts else 0}`",
        f"- max edge count: `{max(edge_counts) if edge_counts else 0}`",
        f"- unique relation patterns: `{len(pattern_counter)}`",
        f"- dominant pattern frequency: `{pattern_counter.most_common(1)[0][1] if pattern_counter else 0}`",
        "",
        "## Global Patterns",
        "",
    ]
    for pattern, count in pattern_counter.most_common():
        diversity_lines.append(f"- `{dict(pattern)}` -> `{count}` queries")
    diversity_lines.extend(["", "## Case-Type Patterns", ""])
    for case_type, counter in sorted(pattern_by_case.items()):
        diversity_lines.append(f"- `{case_type}`: { {str(dict(pattern)): count for pattern, count in counter.items()} }")
    (Path(report_dir) / "GRAPH_DIVERSITY_REPORT.md").write_text("\n".join(diversity_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
