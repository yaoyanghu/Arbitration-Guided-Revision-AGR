from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.common import ensure_dir, read_json, read_jsonl, write_json, write_jsonl


def incoming_edge_totals(graph: dict[str, Any]) -> dict[str, Counter[str]]:
    totals: dict[str, Counter[str]] = defaultdict(Counter)
    for edge in graph.get("edges", []):
        relation = str(edge["relation"])
        target = str(edge["target"])
        totals[target][relation] += float(edge.get("weight", 0.0))
    return totals


def outgoing_edge_totals(graph: dict[str, Any]) -> dict[str, Counter[str]]:
    totals: dict[str, Counter[str]] = defaultdict(Counter)
    for edge in graph.get("edges", []):
        relation = str(edge["relation"])
        source = str(edge["source"])
        totals[source][relation] += float(edge.get("weight", 0.0))
    return totals


def score_candidate(candidate: dict[str, Any], incoming: Counter[str], outgoing: Counter[str]) -> tuple[float, dict[str, float]]:
    base = float(candidate.get("final_score", 0.0))
    boost = 0.0
    boost += incoming.get("support", 0.0) * 0.30
    boost += incoming.get("update", 0.0) * 0.45
    boost += incoming.get("corroborate", 0.0) * 0.40
    penalty = 0.0
    penalty += outgoing.get("update", 0.0) * 0.35
    penalty += outgoing.get("contradict", 0.0) * 0.25
    if str(candidate.get("temporal_status")) == "conflicting":
        penalty += 0.04
    graph_score = base + boost - penalty
    return graph_score, {"base": base, "boost": round(boost, 4), "penalty": round(penalty, 4)}


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


def stage_summary(artifacts: list[dict[str, Any]], key: str) -> dict[str, Any]:
    top1 = 0
    pairwise = 0
    preferred_ranks: list[int] = []
    stale_wins = 0
    for artifact in artifacts:
        records = artifact[key]
        p_rank = preferred_rank(records, str(artifact["preferred_doc_id"]))
        s_rank = stale_best_rank(records, [str(x) for x in artifact.get("stale_doc_ids", [])])
        if records and str(records[0]["doc_id"]) == str(artifact["preferred_doc_id"]):
            top1 += 1
        if p_rank is not None:
            preferred_ranks.append(p_rank)
        if p_rank is not None and (s_rank is None or p_rank < s_rank):
            pairwise += 1
        if s_rank is not None and (p_rank is None or s_rank < p_rank):
            stale_wins += 1
    total = max(len(artifacts), 1)
    return {
        "query_count": len(artifacts),
        "preferred_top1_rate": top1 / total,
        "pairwise_preference_success_rate": pairwise / total,
        "mean_preferred_rank": sum(preferred_ranks) / max(len(preferred_ranks), 1),
        "preferred_mrr": sum(1.0 / rank for rank in preferred_ranks) / total,
        "stale_wins_count": stale_wins,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Route B minimal graph reranking over Route A v2 artifacts.")
    parser.add_argument("--route-a-run-dir", required=True)
    parser.add_argument("--graph-input", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()

    route_a_run_dir = Path(args.route_a_run_dir)
    run_dir = ensure_dir(args.run_dir)
    route_a_artifacts = {item["query_id"]: item for item in read_jsonl(route_a_run_dir / "per_query_artifacts.jsonl")}
    graphs = read_jsonl(args.graph_input)

    graph_outputs: list[dict[str, Any]] = []
    graph_reranked_records: list[dict[str, Any]] = []
    relation_counts = Counter()
    queries_with_nonempty_graph = 0
    improved = 0
    regressed = 0

    for graph in graphs:
        query_id = str(graph["query_id"])
        artifact = route_a_artifacts[query_id]
        incoming = incoming_edge_totals(graph)
        outgoing = outgoing_edge_totals(graph)
        candidates = [dict(item) for item in artifact.get("final_candidates", [])[: int(graph.get("top_k", 5))]]
        reranked: list[dict[str, Any]] = []
        if graph.get("edges"):
            queries_with_nonempty_graph += 1
        relation_counts.update(graph.get("edge_type_counts", {}))
        for candidate in candidates:
            node_id = f"evidence::{candidate['doc_id']}"
            graph_score, components = score_candidate(candidate, incoming.get(node_id, Counter()), outgoing.get(node_id, Counter()))
            enriched = dict(candidate)
            enriched["graph_score"] = graph_score
            enriched["graph_components"] = components
            reranked.append(enriched)
        reranked = sorted(reranked, key=lambda item: float(item["graph_score"]), reverse=True)
        for rank, candidate in enumerate(reranked, start=1):
            candidate["graph_rank"] = rank
            graph_reranked_records.append(candidate)
        route_a_final_rank = artifact.get("final_preferred_rank")
        graph_preferred_rank = preferred_rank(reranked, str(artifact["preferred_doc_id"]))
        if route_a_final_rank is not None and graph_preferred_rank is not None:
            if graph_preferred_rank < route_a_final_rank:
                improved += 1
            elif graph_preferred_rank > route_a_final_rank:
                regressed += 1
        graph_outputs.append(
            {
                "query_id": query_id,
                "query": artifact["query"],
                "preferred_doc_id": artifact["preferred_doc_id"],
                "stale_doc_ids": artifact.get("stale_doc_ids", []),
                "route_a_final_rank": route_a_final_rank,
                "graph_preferred_rank": graph_preferred_rank,
                "route_a_final_candidates": artifact.get("final_candidates", [])[:5],
                "graph_candidates": reranked[:5],
                "edge_type_counts": graph.get("edge_type_counts", {}),
                "edge_count": len(graph.get("edges", [])),
            }
        )

    metrics = {
        "route_a_final": stage_summary(graph_outputs, "route_a_final_candidates"),
        "route_b_graph": stage_summary(graph_outputs, "graph_candidates"),
        "graph_snapshot": {
            "query_count": len(graph_outputs),
            "queries_with_nonempty_graph": queries_with_nonempty_graph,
            "relation_type_counts": dict(relation_counts),
            "improved_count": improved,
            "regressed_count": regressed,
            "no_change_count": len(graph_outputs) - improved - regressed,
        },
    }

    write_jsonl(run_dir / "per_query_graph_artifacts.jsonl", graph_outputs)
    write_jsonl(run_dir / "graph_reranked_results.jsonl", graph_reranked_records)
    write_json(run_dir / "metrics.json", metrics)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
