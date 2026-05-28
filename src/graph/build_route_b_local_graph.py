from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.common import ensure_dir, read_jsonl, write_jsonl


def entity_key(doc_id: str) -> str:
    return doc_id.rsplit("_", 1)[0] if "_" in doc_id else doc_id


def reliability_weight(candidate: dict[str, Any]) -> float:
    return float(candidate.get("reliability_score", 0.0))


def build_graph_for_query(artifact: dict[str, Any], top_k: int) -> dict[str, Any]:
    candidates = [dict(item) for item in artifact.get("final_candidates", [])[:top_k]]
    preferred_key = entity_key(str(artifact["preferred_doc_id"]))

    nodes: list[dict[str, Any]] = [
        {
            "node_id": f"query::{artifact['query_id']}",
            "node_type": "query",
            "query_id": artifact["query_id"],
            "text": artifact["query"],
            "query_time": artifact.get("query_time"),
        }
    ]
    edges: list[dict[str, Any]] = []
    source_nodes: dict[str, dict[str, Any]] = {}

    for candidate in candidates:
        candidate["entity_key"] = entity_key(str(candidate["doc_id"]))
        nodes.append(
            {
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
        )
        if candidate["entity_key"] == preferred_key:
            edges.append(
                {
                    "source": f"query::{artifact['query_id']}",
                    "target": f"evidence::{candidate['doc_id']}",
                    "relation": "support",
                    "weight": 0.20 if candidate.get("temporal_status") == "updated" else 0.12,
                    "reason": "same_query_entity",
                }
            )

        source = str(candidate.get("source", ""))
        if source and source not in source_nodes:
            source_nodes[source] = {
                "node_id": f"source::{source}",
                "node_type": "source",
                "source": source,
                "source_type": candidate.get("source_type"),
                "reliability_bucket": candidate.get("reliability_bucket"),
            }
        if source:
            edges.append(
                {
                    "source": f"source::{source}",
                    "target": f"evidence::{candidate['doc_id']}",
                    "relation": "corroborate",
                    "weight": round(reliability_weight(candidate) * 0.15, 4),
                    "reason": "source_prior",
                }
            )

    nodes.extend(source_nodes.values())

    preferred_group = [item for item in candidates if item["entity_key"] == preferred_key]
    updated_docs = [item for item in preferred_group if item.get("temporal_status") == "updated"]
    stale_docs = [item for item in preferred_group if item.get("temporal_status") == "stale"]
    conflicting_docs = [item for item in preferred_group if item.get("temporal_status") == "conflicting"]

    for stale in stale_docs:
        for updated in updated_docs:
            if int(stale.get("evidence_time", 0)) < int(updated.get("evidence_time", 0)):
                edges.append(
                    {
                        "source": f"evidence::{stale['doc_id']}",
                        "target": f"evidence::{updated['doc_id']}",
                        "relation": "update",
                        "weight": 0.22,
                        "reason": "older_state_superseded_by_newer_state",
                    }
                )
                edges.append(
                    {
                        "source": f"evidence::{stale['doc_id']}",
                        "target": f"evidence::{updated['doc_id']}",
                        "relation": "contradict",
                        "weight": 0.10,
                        "reason": "stale_vs_updated_conflict",
                    }
                )

    for conflict in conflicting_docs:
        for updated in updated_docs:
            edges.append(
                {
                    "source": f"evidence::{conflict['doc_id']}",
                    "target": f"evidence::{updated['doc_id']}",
                    "relation": "contradict",
                    "weight": 0.12,
                    "reason": "uncertain_report_vs_preferred_update",
                }
            )
            if reliability_weight(updated) > reliability_weight(conflict):
                edges.append(
                    {
                        "source": f"evidence::{updated['doc_id']}",
                        "target": f"evidence::{conflict['doc_id']}",
                        "relation": "corroborate",
                        "weight": 0.08,
                        "reason": "higher_reliability_updated_evidence",
                    }
                )

    return {
        "query_id": artifact["query_id"],
        "query": artifact["query"],
        "preferred_doc_id": artifact["preferred_doc_id"],
        "top_k": top_k,
        "nodes": nodes,
        "edges": edges,
        "edge_type_counts": dict(Counter(edge["relation"] for edge in edges)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Route B local evidence graphs from Route A per-query artifacts.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    artifacts = read_jsonl(args.input)
    graphs = [build_graph_for_query(artifact, args.top_k) for artifact in artifacts]
    write_jsonl(args.output, graphs)
    ensure_dir(Path(args.output).parent)
    print(json.dumps({"query_count": len(graphs), "output": str(Path(args.output).resolve())}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
