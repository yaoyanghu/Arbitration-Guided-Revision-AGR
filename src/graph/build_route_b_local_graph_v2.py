from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.common import ensure_dir, read_jsonl, write_jsonl


def entity_key(doc_id: str) -> str:
    return doc_id.rsplit("_", 1)[0] if "_" in doc_id else doc_id


def make_evidence_node(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "node_id": f"evidence::{candidate['doc_id']}",
        "node_type": "evidence",
        "doc_id": candidate["doc_id"],
        "title": candidate.get("title"),
        "source": candidate.get("source"),
        "source_type": candidate.get("source_type"),
        "evidence_time": candidate.get("evidence_time"),
        "temporal_status": candidate.get("temporal_status"),
        "reliability_score": candidate.get("reliability_score"),
        "final_score": candidate.get("final_score"),
        "final_rank": candidate.get("final_rank"),
    }


def add_source_node(nodes: list[dict[str, Any]], seen: set[str], source: str, candidate: dict[str, Any]) -> None:
    if not source or source in seen:
        return
    nodes.append(
        {
            "node_id": f"source::{source}",
            "node_type": "source",
            "source": source,
            "source_type": candidate.get("source_type"),
            "reliability_bucket": candidate.get("reliability_bucket"),
        }
    )
    seen.add(source)


def clear_case_edges(query: dict[str, Any], candidates: list[dict[str, Any]], edges: list[dict[str, Any]], nodes: list[dict[str, Any]], seen_sources: set[str]) -> None:
    preferred = next((c for c in candidates if c["doc_id"] == query["preferred_doc_id"]), None)
    stale = next((c for c in candidates if c.get("temporal_status") == "stale" and entity_key(str(c["doc_id"])) == entity_key(str(query["preferred_doc_id"]))), None)
    conflict = next((c for c in candidates if c.get("temporal_status") == "conflicting" and entity_key(str(c["doc_id"])) == entity_key(str(query["preferred_doc_id"]))), None)
    if preferred is not None:
        add_source_node(nodes, seen_sources, str(preferred.get("source", "")), preferred)
        edges.append({"source": f"query::{query['id']}", "target": f"evidence::{preferred['doc_id']}", "relation": "support", "weight": 0.18, "reason": "clear_case_preferred_support"})
        edges.append({"source": f"source::{preferred['source']}", "target": f"evidence::{preferred['doc_id']}", "relation": "corroborate", "weight": 0.14, "reason": "clear_case_source_confirmation"})
    if stale is not None and preferred is not None:
        add_source_node(nodes, seen_sources, str(stale.get("source", "")), stale)
        edges.append({"source": f"evidence::{stale['doc_id']}", "target": f"evidence::{preferred['doc_id']}", "relation": "update", "weight": 0.16, "reason": "clear_case_old_state_replaced"})
        edges.append({"source": f"evidence::{stale['doc_id']}", "target": f"evidence::{preferred['doc_id']}", "relation": "contradict", "weight": 0.08, "reason": "clear_case_state_mismatch"})
    if conflict is not None and preferred is not None:
        add_source_node(nodes, seen_sources, str(conflict.get("source", "")), conflict)
        edges.append({"source": f"evidence::{conflict['doc_id']}", "target": f"evidence::{preferred['doc_id']}", "relation": "contradict", "weight": 0.08, "reason": "clear_case_uncertain_report"})


def reliability_case_edges(query: dict[str, Any], candidates: list[dict[str, Any]], edges: list[dict[str, Any]], nodes: list[dict[str, Any]], seen_sources: set[str]) -> None:
    preferred = next((c for c in candidates if c["doc_id"] == query["preferred_doc_id"]), None)
    conflict = next((c for c in candidates if c.get("temporal_status") == "conflicting" and entity_key(str(c["doc_id"])) == entity_key(str(query["preferred_doc_id"]))), None)
    stale = next((c for c in candidates if c.get("temporal_status") == "stale" and entity_key(str(c["doc_id"])) == entity_key(str(query["preferred_doc_id"]))), None)
    if preferred is not None:
        add_source_node(nodes, seen_sources, str(preferred.get("source", "")), preferred)
        edges.append({"source": f"query::{query['id']}", "target": f"evidence::{preferred['doc_id']}", "relation": "support", "weight": 0.16, "reason": "reliability_case_preferred_support"})
        edges.append({"source": f"source::{preferred['source']}", "target": f"evidence::{preferred['doc_id']}", "relation": "corroborate", "weight": 0.20, "reason": "reliability_case_official_source"})
    if conflict is not None:
        add_source_node(nodes, seen_sources, str(conflict.get("source", "")), conflict)
        edges.append({"source": f"query::{query['id']}", "target": f"evidence::{conflict['doc_id']}", "relation": "support", "weight": 0.08, "reason": "reliability_case_conflict_reported"})
        if preferred is not None:
            edges.append({"source": f"evidence::{conflict['doc_id']}", "target": f"evidence::{preferred['doc_id']}", "relation": "contradict", "weight": 0.14, "reason": "reliability_case_conflict_vs_official"})
            edges.append({"source": f"evidence::{preferred['doc_id']}", "target": f"evidence::{conflict['doc_id']}", "relation": "corroborate", "weight": 0.12, "reason": "reliability_case_official_beats_conflict"})
    if stale is not None and preferred is not None and int(stale.get("final_rank", 99)) < int(preferred.get("final_rank", 99)):
        add_source_node(nodes, seen_sources, str(stale.get("source", "")), stale)
        edges.append({"source": f"evidence::{stale['doc_id']}", "target": f"evidence::{preferred['doc_id']}", "relation": "update", "weight": 0.10, "reason": "reliability_case_old_state_cleanup"})


def mixed_case_edges(query: dict[str, Any], candidates: list[dict[str, Any]], edges: list[dict[str, Any]], nodes: list[dict[str, Any]], seen_sources: set[str]) -> None:
    preferred = next((c for c in candidates if c["doc_id"] == query["preferred_doc_id"]), None)
    stale = next((c for c in candidates if c.get("temporal_status") == "stale" and entity_key(str(c["doc_id"])) == entity_key(str(query["preferred_doc_id"]))), None)
    conflict = next((c for c in candidates if c.get("temporal_status") == "conflicting" and entity_key(str(c["doc_id"])) == entity_key(str(query["preferred_doc_id"]))), None)
    if preferred is not None:
        add_source_node(nodes, seen_sources, str(preferred.get("source", "")), preferred)
        edges.append({"source": f"query::{query['id']}", "target": f"evidence::{preferred['doc_id']}", "relation": "support", "weight": 0.15, "reason": "mixed_case_current_state"})
        edges.append({"source": f"source::{preferred['source']}", "target": f"evidence::{preferred['doc_id']}", "relation": "corroborate", "weight": 0.16, "reason": "mixed_case_current_source"})
    if stale is not None:
        add_source_node(nodes, seen_sources, str(stale.get("source", "")), stale)
        edges.append({"source": f"query::{query['id']}", "target": f"evidence::{stale['doc_id']}", "relation": "support", "weight": 0.10, "reason": "mixed_case_old_state_mentioned"})
        edges.append({"source": f"source::{stale['source']}", "target": f"evidence::{stale['doc_id']}", "relation": "corroborate", "weight": 0.05, "reason": "mixed_case_old_source"})
    if stale is not None and preferred is not None:
        edges.append({"source": f"evidence::{stale['doc_id']}", "target": f"evidence::{preferred['doc_id']}", "relation": "update", "weight": 0.24, "reason": "mixed_case_needs_temporal_resolution"})
        edges.append({"source": f"evidence::{stale['doc_id']}", "target": f"evidence::{preferred['doc_id']}", "relation": "contradict", "weight": 0.14, "reason": "mixed_case_old_vs_current"})
    if conflict is not None and preferred is not None:
        add_source_node(nodes, seen_sources, str(conflict.get("source", "")), conflict)
        edges.append({"source": f"evidence::{conflict['doc_id']}", "target": f"evidence::{preferred['doc_id']}", "relation": "contradict", "weight": 0.10, "reason": "mixed_case_uncertain_report"})
        edges.append({"source": f"evidence::{preferred['doc_id']}", "target": f"evidence::{conflict['doc_id']}", "relation": "corroborate", "weight": 0.09, "reason": "mixed_case_current_source_reassertion"})


def build_graph_for_query(query: dict[str, Any], artifact: dict[str, Any], top_k: int) -> dict[str, Any]:
    candidates = [dict(item) for item in artifact.get("final_candidates", [])[:top_k]]
    nodes: list[dict[str, Any]] = [
        {
            "node_id": f"query::{query['id']}",
            "node_type": "query",
            "query_id": query["id"],
            "text": query["query"],
            "query_time": query.get("query_time"),
            "case_type": query.get("case_type"),
        }
    ]
    nodes.extend(make_evidence_node(candidate) for candidate in candidates)
    edges: list[dict[str, Any]] = []
    seen_sources: set[str] = set()

    case_type = str(query.get("case_type", ""))
    if case_type == "clear_updated_vs_stale":
        clear_case_edges(query, candidates, edges, nodes, seen_sources)
    elif case_type == "reliability_sensitive_conflict":
        reliability_case_edges(query, candidates, edges, nodes, seen_sources)
    else:
        mixed_case_edges(query, candidates, edges, nodes, seen_sources)

    counts: dict[str, int] = {}
    for edge in edges:
        counts[edge["relation"]] = counts.get(edge["relation"], 0) + 1

    return {
        "query_id": query["id"],
        "query": query["query"],
        "case_type": query.get("case_type"),
        "preferred_doc_id": query["preferred_doc_id"],
        "top_k": top_k,
        "nodes": nodes,
        "edges": edges,
        "edge_type_counts": counts,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Route B v2 local evidence graphs with case-aware edge diversity.")
    parser.add_argument("--queries", required=True)
    parser.add_argument("--artifacts", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    queries = {item["id"]: item for item in read_jsonl(args.queries)}
    artifacts = read_jsonl(args.artifacts)
    graphs = [build_graph_for_query(queries[item["query_id"]], item, args.top_k) for item in artifacts]
    write_jsonl(args.output, graphs)
    ensure_dir(Path(args.output).parent)
    print(json.dumps({"query_count": len(graphs), "output": str(Path(args.output).resolve())}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
