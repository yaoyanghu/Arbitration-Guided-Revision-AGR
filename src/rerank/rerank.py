from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from src.common import read_jsonl, write_jsonl


def _normalize_bm25(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        grouped.setdefault(str(record["query_id"]), []).append(dict(record))

    normalized_records: list[dict[str, Any]] = []
    for query_id, items in grouped.items():
        scores = [float(item.get("bm25_score", 0.0)) for item in items]
        min_score = min(scores)
        max_score = max(scores)
        for item in items:
            raw_score = float(item.get("bm25_score", 0.0))
            if max_score == min_score:
                normalized = 1.0 if raw_score > 0 else 0.0
            else:
                normalized = (raw_score - min_score) / (max_score - min_score)
            item["bm25_score_norm"] = normalized
            normalized_records.append(item)
    return normalized_records


def rerank_records(
    records: list[dict[str, Any]],
    bm25_weight: float,
    temporal_weight: float,
    reliability_weight: float,
) -> list[dict[str, Any]]:
    return score_and_rank_records(records, bm25_weight, temporal_weight, reliability_weight)


def score_and_rank_records(
    records: list[dict[str, Any]],
    bm25_weight: float,
    temporal_weight: float,
    reliability_weight: float,
) -> list[dict[str, Any]]:
    normalized_records = _normalize_bm25(records)
    reranked: list[dict[str, Any]] = []
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in normalized_records:
        final_score = (
            bm25_weight * float(record.get("bm25_score_norm", 0.0))
            + temporal_weight * float(record.get("temporal_score", 0.0))
            + reliability_weight * float(record.get("reliability_score", 0.0))
        )
        enriched = dict(record)
        enriched["final_score"] = final_score
        grouped.setdefault(str(record["query_id"]), []).append(enriched)
    for query_id, items in grouped.items():
        sorted_items = sorted(items, key=lambda item: float(item["final_score"]), reverse=True)
        for rank, item in enumerate(sorted_items, start=1):
            item["final_rank"] = rank
            reranked.append(item)
    return reranked


def main() -> None:
    parser = argparse.ArgumentParser(description="Fuse BM25, temporal, and reliability scores.")
    parser.add_argument("--input", required=True, help="Input jsonl.")
    parser.add_argument("--output", required=True, help="Output reranked jsonl.")
    parser.add_argument("--bm25-weight", type=float, default=0.6)
    parser.add_argument("--temporal-weight", type=float, default=0.2)
    parser.add_argument("--reliability-weight", type=float, default=0.2)
    args = parser.parse_args()
    records = read_jsonl(args.input)
    reranked = rerank_records(
        records,
        bm25_weight=args.bm25_weight,
        temporal_weight=args.temporal_weight,
        reliability_weight=args.reliability_weight,
    )
    write_jsonl(args.output, reranked)
    print(f"Wrote {len(reranked)} reranked records to {Path(args.output).resolve()}")


if __name__ == "__main__":
    main()
