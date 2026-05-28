from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.common import read_jsonl, write_jsonl


def build_graph(artifact: dict) -> dict:
    candidates = [dict(item) for item in artifact.get("case_aware_non_graph_rerank_candidates", [])[:5]]
    nodes = [{"id": f"query::{artifact['query_id']}", "type": "query", "score": 1.0}]
    edges = []
    for candidate in candidates:
        doc_id = str(candidate["doc_id"])
        evidence_id = f"evidence::{doc_id}"
        source_id = f"source::{doc_id}"
        base_score = float(candidate.get("case_aware_non_graph_score", 0.0))
        reliability = float(candidate.get("reliability_score", 0.0))
        nodes.append({"id": evidence_id, "type": "evidence", "doc_id": doc_id, "temporal_status": candidate.get("temporal_status"), "base_score": base_score})
        nodes.append({"id": source_id, "type": "source", "doc_id": doc_id, "reliability_score": reliability})
        edges.append({"source": f"query::{artifact['query_id']}", "target": evidence_id, "relation": "support", "weight": max(0.05, min(1.0, base_score))})
        edges.append({"source": source_id, "target": evidence_id, "relation": "corroborate", "weight": reliability})
    for source in candidates:
        for target in candidates:
            if source["doc_id"] == target["doc_id"]:
                continue
            source_status = str(source.get("temporal_status"))
            target_status = str(target.get("temporal_status"))
            s_id = f"evidence::{source['doc_id']}"
            t_id = f"evidence::{target['doc_id']}"
            if source_status == "updated" and target_status == "stale":
                edges.append({"source": s_id, "target": t_id, "relation": "update", "weight": 1.0})
            if source_status == "conflicting" and target_status in {"updated", "stale"}:
                edges.append({"source": s_id, "target": t_id, "relation": "contradict", "weight": 0.7})
    return {"query_id": artifact["query_id"], "query": artifact["query"], "case_type": artifact["case_type"], "preferred_doc_id": artifact["preferred_doc_id"], "stale_doc_ids": artifact.get("stale_doc_ids", []), "top_k": len(candidates), "nodes": nodes, "edges": edges}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Route B graph-native local graphs from Route A++ artifacts.")
    parser.add_argument("--artifacts", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    artifacts = read_jsonl(args.artifacts)
    graphs = [build_graph(item) for item in artifacts]
    write_jsonl(args.output, graphs)
    print(json.dumps({"graph_count": len(graphs), "output": str(Path(args.output).resolve())}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
