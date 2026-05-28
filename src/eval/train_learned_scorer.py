from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.common import ensure_dir, read_jsonl, read_yaml, write_json
from src.eval.eval_conflict_aware_rag import _resolve_config
from src.rag.conflict_arbitration import build_scored_candidates
from src.rag.contracts import to_query_record
from src.rag.learned_scorer import feature_vector, save_scorer, scorer_summary, train_logistic_scorer
from src.retrieval.search import run_search


def _label_candidate(candidate: dict[str, Any], gold_titles: list[str]) -> int:
    title = str(candidate.get("title", "")).strip().lower()
    gold = {item.strip().lower() for item in gold_titles if item.strip()}
    return 1 if title and title in gold else 0


def train_from_config(config: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    mainline = config["mainline"]
    query_records = [to_query_record(item) for item in read_jsonl(mainline["queries_path"])]
    retrieval_records = run_search(
        corpus_path=mainline["corpus_path"],
        index_dir=mainline["bm25_index_dir"],
        queries=[
            {
                "id": item.query_id,
                "query": item.query,
                "query_time": item.query_time,
                "metadata": item.metadata,
            }
            for item in query_records
        ],
        top_k=int(mainline["retrieval_top_k"]),
        strategy=str(mainline.get("retrieval_strategy", "standard")),
    )
    candidates = build_scored_candidates(
        query_records=query_records,
        retrieval_records=retrieval_records,
        bm25_weight=float(mainline["bm25_weight"]),
        lexical_weight=float(mainline["lexical_weight"]),
        temporal_weight=float(mainline["temporal_weight"]),
        conflict_weight=float(mainline["conflict_weight"]),
        structured_weight=float(mainline.get("structured_weight", 0.0)),
        reliability_weight=float(mainline["reliability_weight"]),
        learned_weight=0.0,
        learned_model=None,
    )
    gold_lookup = {record.query_id: record.gold_evidence_titles for record in query_records}
    rows = []
    for candidate in candidates:
        rows.append(
            {
                "query_id": candidate.query_id,
                "doc_id": candidate.doc_id,
                "label": _label_candidate(candidate.__dict__, gold_lookup.get(candidate.query_id, [])),
                "features": feature_vector(candidate),
            }
        )
    model = train_logistic_scorer(rows)
    model["summary"] = scorer_summary(model)
    save_scorer(model, output_path)
    return {
        "output_path": str(output_path),
        "train_rows": model["train_rows"],
        "positive_rows": model["positive_rows"],
        "summary": model["summary"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a lightweight learned scorer for New_ChronoRAG.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    config = _resolve_config(args.config)
    result = train_from_config(config, args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
