from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

from src.common import read_jsonl, write_json, write_jsonl


def preferred_rank(records: list[dict[str, Any]], preferred_doc_id: str) -> int | None:
    for idx, item in enumerate(records, start=1):
        if str(item.get("doc_id")) == preferred_doc_id:
            return idx
    return None


def stale_best_rank(records: list[dict[str, Any]], stale_doc_ids: list[str]) -> int | None:
    stale_set = {str(x) for x in stale_doc_ids}
    best = None
    for idx, item in enumerate(records, start=1):
        if str(item.get("doc_id")) in stale_set:
            best = idx if best is None else min(best, idx)
    return best


def incoming_edges(graph: dict[str, Any], target: str) -> list[dict[str, Any]]:
    return [edge for edge in graph.get("edges", []) if str(edge["target"]) == target]


def outgoing_edges(graph: dict[str, Any], source: str) -> list[dict[str, Any]]:
    return [edge for edge in graph.get("edges", []) if str(edge["source"]) == source]


def normalize_scores(candidates: list[dict[str, Any]], field: str) -> dict[str, float]:
    values = [float(item.get(field, 0.0)) for item in candidates]
    min_v = min(values)
    max_v = max(values)
    out = {}
    for item in candidates:
        value = float(item.get(field, 0.0))
        out[str(item["doc_id"])] = 1.0 if max_v == min_v else (value - min_v) / (max_v - min_v)
    return out


def matched_non_graph_score(graph: dict[str, Any], candidate: dict[str, Any]) -> float:
    evidence_id = f"evidence::{candidate['doc_id']}"
    base = float(candidate.get("case_aware_non_graph_score", 0.0))
    inc = incoming_edges(graph, evidence_id)
    out = outgoing_edges(graph, evidence_id)
    corroborate = sum(float(edge["weight"]) for edge in inc if edge["relation"] == "corroborate")
    support = sum(float(edge["weight"]) for edge in inc if edge["relation"] == "support")
    update_out = sum(float(edge["weight"]) for edge in out if edge["relation"] == "update")
    contradict_in = sum(float(edge["weight"]) for edge in inc if edge["relation"] == "contradict")
    contradict_out = sum(float(edge["weight"]) for edge in out if edge["relation"] == "contradict")
    return base + 0.08 * support + 0.12 * corroborate + 0.12 * update_out - 0.08 * contradict_in - 0.05 * contradict_out


def graph_native_score(graph: dict[str, Any], candidate: dict[str, Any], base_norms: dict[str, float]) -> float:
    evidence_id = f"evidence::{candidate['doc_id']}"
    base_norm = base_norms[str(candidate["doc_id"])]
    node_states: dict[str, float] = {f"query::{graph['query_id']}": 1.0}
    for node in graph["nodes"]:
        if node["type"] == "source":
            node_states[str(node["id"])] = 2 * float(node.get("reliability_score", 0.5)) - 1
        elif node["type"] == "evidence":
            node_states[str(node["id"])] = 2 * base_norms[str(node["doc_id"])] - 1
    for _ in range(3):
        new_states = dict(node_states)
        for node in graph["nodes"]:
            if node["type"] != "evidence":
                continue
            nid = str(node["id"])
            incoming = 0.0
            for edge in incoming_edges(graph, nid):
                src_state = node_states.get(str(edge["source"]), 0.0)
                relation = str(edge["relation"])
                sign = -1.0 if relation == "contradict" else 1.0
                incoming += sign * float(edge["weight"]) * src_state
            update_bonus = 0.0
            for edge in outgoing_edges(graph, nid):
                if str(edge["relation"]) == "update":
                    target_state = node_states.get(str(edge["target"]), 0.0)
                    update_bonus += float(edge["weight"]) * (1.0 - target_state)
            new_states[nid] = math.tanh(0.70 * node_states[nid] + 0.20 * incoming + 0.15 * update_bonus)
        node_states = new_states
    consensus = (node_states[evidence_id] + 1.0) / 2.0
    return 0.70 * base_norm + 0.30 * consensus


def rerank_records(graph: dict[str, Any], artifact: dict[str, Any], strategy: str) -> list[dict[str, Any]]:
    candidates = [dict(item) for item in artifact.get("case_aware_non_graph_rerank_candidates", [])[: int(graph.get("top_k", 5))]]
    if strategy == "a_plus_best_non_graph":
        reranked = candidates
    elif strategy == "matched_non_graph_conflict_aggregator":
        reranked = []
        for candidate in candidates:
            item = dict(candidate)
            item["route_b_score"] = matched_non_graph_score(graph, candidate)
            reranked.append(item)
        reranked = sorted(reranked, key=lambda x: float(x["route_b_score"]), reverse=True)
    else:
        base_norms = normalize_scores(candidates, "case_aware_non_graph_score")
        reranked = []
        for candidate in candidates:
            item = dict(candidate)
            item["route_b_score"] = graph_native_score(graph, candidate, base_norms)
            reranked.append(item)
        reranked = sorted(reranked, key=lambda x: float(x["route_b_score"]), reverse=True)
    for rank, item in enumerate(reranked, start=1):
        item["route_b_rank"] = rank
    return reranked


def summarize(per_query: list[dict[str, Any]], key: str) -> dict[str, Any]:
    top1 = 0
    pairwise = 0
    stale_wins = 0
    ranks: list[int] = []
    improved = 0
    regressed = 0
    for item in per_query:
        records = item[key]
        p_rank = preferred_rank(records, str(item["preferred_doc_id"]))
        s_rank = stale_best_rank(records, [str(x) for x in item.get("stale_doc_ids", [])])
        base_rank = item.get("a_plus_best_non_graph_rank")
        if records and str(records[0].get("doc_id")) == str(item["preferred_doc_id"]):
            top1 += 1
        if p_rank is not None:
            ranks.append(p_rank)
        if p_rank is not None and (s_rank is None or p_rank < s_rank):
            pairwise += 1
        if s_rank is not None and (p_rank is None or s_rank < p_rank):
            stale_wins += 1
        if base_rank is not None and p_rank is not None:
            if p_rank < base_rank:
                improved += 1
            elif p_rank > base_rank:
                regressed += 1
    total = max(len(per_query), 1)
    return {
        "query_count": len(per_query),
        "preferred_top1_rate": top1 / total,
        "pairwise_preference_success_rate": pairwise / total,
        "mean_preferred_rank": sum(ranks) / max(len(ranks), 1),
        "preferred_mrr": sum(1.0 / r for r in ranks) / total,
        "stale_wins_count": stale_wins,
        "improved_count": improved,
        "regressed_count": regressed,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Route B graph-native consistency experiment.")
    parser.add_argument("--graphs", required=True)
    parser.add_argument("--artifacts", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()

    graphs = read_jsonl(args.graphs)
    artifacts = {item["query_id"]: item for item in read_jsonl(args.artifacts)}
    strategies = ["a_plus_best_non_graph", "matched_non_graph_conflict_aggregator", "graph_native_consensus"]
    per_strategy: dict[str, list[dict[str, Any]]] = {}
    combined_rows: list[dict[str, Any]] = []
    for strategy in strategies:
        rows = []
        for graph in graphs:
            artifact = artifacts[str(graph["query_id"])]
            reranked = rerank_records(graph, artifact, strategy)
            row = {"query_id": artifact["query_id"], "query": artifact["query"], "case_type": artifact["case_type"], "preferred_doc_id": artifact["preferred_doc_id"], "stale_doc_ids": artifact.get("stale_doc_ids", []), "candidates": reranked}
            if strategy == "a_plus_best_non_graph":
                row["a_plus_best_non_graph_rank"] = preferred_rank(reranked, str(artifact["preferred_doc_id"]))
            else:
                row["a_plus_best_non_graph_rank"] = preferred_rank(per_strategy["a_plus_best_non_graph"][len(rows)]["candidates"], str(artifact["preferred_doc_id"]))
            rows.append(row)
            combined_rows.append({"strategy": strategy, **row})
        per_strategy[strategy] = rows

    metrics = {strategy: summarize(rows, "candidates") for strategy, rows in per_strategy.items()}
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    write_json(run_dir / "metrics.json", {"strategies": metrics})
    write_jsonl(run_dir / "per_query_results.jsonl", combined_rows)
    print(json.dumps({"strategies": metrics}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
