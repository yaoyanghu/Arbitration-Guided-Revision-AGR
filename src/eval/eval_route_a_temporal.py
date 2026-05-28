from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from src.common import ensure_dir, read_jsonl, write_json, write_jsonl
from src.reliability.score_route_a_reliability import score_reliability_records
from src.rerank.rerank import score_and_rank_records
from src.retrieval.build_bm25 import build_and_save_index, load_corpus
from src.retrieval.search import run_search
from src.temporal.score_temporal_conflict import score_temporal_records


def enrich_with_query_and_corpus(retrieval_records: list[dict[str, Any]], queries: list[dict[str, Any]], corpus_path: str | Path) -> list[dict[str, Any]]:
    query_map = {str(query["id"]): query for query in queries}
    corpus_map = {str(row["doc_id"]): row for row in load_corpus(corpus_path)}
    enriched: list[dict[str, Any]] = []
    for record in retrieval_records:
        query = query_map[str(record["query_id"])]
        corpus_row = corpus_map.get(str(record["doc_id"]), {})
        merged = dict(record)
        merged["query_time"] = query.get("query_time")
        merged["entity"] = query.get("entity")
        merged["focus_attribute"] = query.get("focus_attribute")
        merged["preferred_doc_id"] = query.get("preferred_doc_id")
        merged["stale_doc_ids"] = query.get("stale_doc_ids", [])
        for key in ("source_type", "evidence_time", "temporal_status", "pair_role", "reliability_bucket"):
            if key in corpus_row:
                merged[key] = corpus_row[key]
        enriched.append(merged)
    return enriched


def rank_records(records: list[dict[str, Any]], rank_field: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record["query_id"])].append(record)
    for query_id in list(grouped.keys()):
        grouped[query_id] = sorted(grouped[query_id], key=lambda item: int(item[rank_field]))
    return dict(grouped)


def add_temporal_ranks(records: list[dict[str, Any]], bm25_weight: float, temporal_weight: float) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in records:
        grouped[str(item["query_id"])].append(dict(item))
    output: list[dict[str, Any]] = []
    for _, items in grouped.items():
        min_b = min(float(it["bm25_score"]) for it in items)
        max_b = max(float(it["bm25_score"]) for it in items)
        scored_items = []
        for item in items:
            bm25_norm = 1.0 if max_b == min_b else (float(item["bm25_score"]) - min_b) / (max_b - min_b)
            item["bm25_score_norm"] = bm25_norm
            item["temporal_rerank_score"] = bm25_weight * bm25_norm + temporal_weight * float(item["temporal_score"])
            scored_items.append(item)
        reranked = sorted(scored_items, key=lambda x: float(x["temporal_rerank_score"]), reverse=True)
        for rank, item in enumerate(reranked, start=1):
            item["temporal_rank"] = rank
            output.append(item)
    return output


def preferred_rank(records: list[dict[str, Any]], preferred_doc_id: str) -> int | None:
    for idx, record in enumerate(records, start=1):
        if str(record.get("doc_id")) == preferred_doc_id:
            return idx
    return None


def stale_best_rank(records: list[dict[str, Any]], stale_doc_ids: list[str]) -> int | None:
    stale_set = {str(x) for x in stale_doc_ids}
    best = None
    for idx, record in enumerate(records, start=1):
        if str(record.get("doc_id")) in stale_set:
            best = idx if best is None else min(best, idx)
    return best


def stage_summary(queries: list[dict[str, Any]], grouped_records: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    pairwise_success = 0
    top1_preferred = 0
    preferred_ranks: list[int] = []
    stale_wins = 0
    for query in queries:
        records = grouped_records.get(str(query["id"]), [])
        p_rank = preferred_rank(records, str(query["preferred_doc_id"]))
        s_rank = stale_best_rank(records, [str(x) for x in query.get("stale_doc_ids", [])])
        if p_rank is not None:
            preferred_ranks.append(p_rank)
        if records and str(records[0].get("doc_id")) == str(query["preferred_doc_id"]):
            top1_preferred += 1
        if p_rank is not None and (s_rank is None or p_rank < s_rank):
            pairwise_success += 1
        if s_rank is not None and (p_rank is None or s_rank < p_rank):
            stale_wins += 1
    total = max(len(queries), 1)
    return {
        "query_count": len(queries),
        "preferred_top1_rate": top1_preferred / total,
        "pairwise_preference_success_rate": pairwise_success / total,
        "mean_preferred_rank": sum(preferred_ranks) / max(len(preferred_ranks), 1),
        "preferred_mrr": sum(1.0 / rank for rank in preferred_ranks) / total,
        "stale_wins_count": stale_wins,
    }


def build_per_query_artifacts(
    queries: list[dict[str, Any]],
    raw_grouped: dict[str, list[dict[str, Any]]],
    temporal_grouped: dict[str, list[dict[str, Any]]],
    final_grouped: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    for query in queries:
        query_id = str(query["id"])
        raw_records = raw_grouped.get(query_id, [])
        temporal_records = temporal_grouped.get(query_id, [])
        final_records = final_grouped.get(query_id, [])
        artifacts.append(
            {
                "query_id": query_id,
                "query": query["query"],
                "query_time": query.get("query_time"),
                "preferred_doc_id": query.get("preferred_doc_id"),
                "stale_doc_ids": query.get("stale_doc_ids", []),
                "raw_preferred_rank": preferred_rank(raw_records, str(query["preferred_doc_id"])),
                "temporal_preferred_rank": preferred_rank(temporal_records, str(query["preferred_doc_id"])),
                "final_preferred_rank": preferred_rank(final_records, str(query["preferred_doc_id"])),
                "raw_stale_best_rank": stale_best_rank(raw_records, [str(x) for x in query.get("stale_doc_ids", [])]),
                "temporal_stale_best_rank": stale_best_rank(temporal_records, [str(x) for x in query.get("stale_doc_ids", [])]),
                "final_stale_best_rank": stale_best_rank(final_records, [str(x) for x in query.get("stale_doc_ids", [])]),
                "raw_candidates": raw_records[:5],
                "temporal_candidates": temporal_records[:5],
                "final_candidates": final_records[:5],
            }
        )
    return artifacts


def acceptance_snapshot(queries: list[dict[str, Any]], raw_grouped: dict[str, list[dict[str, Any]]], temporal_grouped: dict[str, list[dict[str, Any]]], final_grouped: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    temporal_changed = 0
    reliability_helped = 0
    final_better = 0
    for query in queries:
        qid = str(query["id"])
        raw_pref = preferred_rank(raw_grouped.get(qid, []), str(query["preferred_doc_id"]))
        temp_pref = preferred_rank(temporal_grouped.get(qid, []), str(query["preferred_doc_id"]))
        final_pref = preferred_rank(final_grouped.get(qid, []), str(query["preferred_doc_id"]))
        if raw_pref != temp_pref:
            temporal_changed += 1
        if temp_pref is not None and final_pref is not None and final_pref < temp_pref:
            reliability_helped += 1
        if raw_pref is not None and final_pref is not None and final_pref < raw_pref:
            final_better += 1
    return {
        "temporal_changed_ranking_count": temporal_changed,
        "reliability_helped_count": reliability_helped,
        "final_better_than_retrieval_count": final_better,
    }


def markdown_report(metrics: dict[str, Any]) -> str:
    lines = [
        "# Route A Temporal V1 Summary",
        "",
        "| stage | preferred top1 | pairwise success | mean preferred rank | preferred MRR | stale wins |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for stage_name, stage_metrics in metrics["stages"].items():
        lines.append(
            f"| {stage_name} | {stage_metrics['preferred_top1_rate']:.3f} | {stage_metrics['pairwise_preference_success_rate']:.3f} | {stage_metrics['mean_preferred_rank']:.3f} | {stage_metrics['preferred_mrr']:.3f} | {stage_metrics['stale_wins_count']} |"
        )
    lines.extend(
        [
            "",
            "## Acceptance Snapshot",
            "",
            f"- temporal changed ranking count: `{metrics['acceptance_snapshot']['temporal_changed_ranking_count']}`",
            f"- reliability helped count: `{metrics['acceptance_snapshot']['reliability_helped_count']}`",
            f"- final better than retrieval count: `{metrics['acceptance_snapshot']['final_better_than_retrieval_count']}`",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Route A temporal-conflict retrieval and reranking evaluation.")
    parser.add_argument("--queries", required=True)
    parser.add_argument("--corpus", required=True)
    parser.add_argument("--index-dir", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--bm25-weight", type=float, default=0.6)
    parser.add_argument("--temporal-weight", type=float, default=0.25)
    parser.add_argument("--reliability-weight", type=float, default=0.15)
    args = parser.parse_args()

    run_dir = ensure_dir(args.run_dir)
    queries = read_jsonl(args.queries)
    build_and_save_index(args.corpus, args.index_dir, backend="json")

    retrieval_records = run_search(
        corpus_path=args.corpus,
        index_dir=args.index_dir,
        queries=[{"id": q["id"], "query": q["query"]} for q in queries],
        top_k=args.top_k,
    )
    retrieval_records = enrich_with_query_and_corpus(retrieval_records, queries, args.corpus)
    write_jsonl(run_dir / "retrieval_results.jsonl", retrieval_records)

    temporal_scored = score_temporal_records(retrieval_records)
    write_jsonl(run_dir / "temporal_results.jsonl", temporal_scored)

    temporal_reranked = add_temporal_ranks(temporal_scored, args.bm25_weight, args.temporal_weight)
    write_jsonl(run_dir / "temporal_reranked_results.jsonl", temporal_reranked)

    reliability_scored = score_reliability_records(temporal_reranked)
    write_jsonl(run_dir / "reliability_results.jsonl", reliability_scored)

    final_reranked = score_and_rank_records(
        reliability_scored,
        bm25_weight=args.bm25_weight,
        temporal_weight=args.temporal_weight,
        reliability_weight=args.reliability_weight,
    )
    write_jsonl(run_dir / "reranked_results.jsonl", final_reranked)

    raw_grouped = rank_records(retrieval_records, "rank")
    temporal_grouped = rank_records(temporal_reranked, "temporal_rank")
    final_grouped = rank_records(final_reranked, "final_rank")

    metrics = {
        "query_count": len(queries),
        "weights": {
            "bm25_weight": args.bm25_weight,
            "temporal_weight": args.temporal_weight,
            "reliability_weight": args.reliability_weight,
        },
        "stages": {
            "retrieval_only": stage_summary(queries, raw_grouped),
            "temporal_only": stage_summary(queries, temporal_grouped),
            "temporal_plus_reliability": stage_summary(queries, final_grouped),
        },
    }
    metrics["acceptance_snapshot"] = acceptance_snapshot(queries, raw_grouped, temporal_grouped, final_grouped)

    artifacts = build_per_query_artifacts(queries, raw_grouped, temporal_grouped, final_grouped)
    write_jsonl(run_dir / "queries.jsonl", queries)
    write_jsonl(run_dir / "per_query_artifacts.jsonl", artifacts)
    write_json(run_dir / "metrics.json", metrics)
    (run_dir / "summary.md").write_text(markdown_report(metrics), encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
