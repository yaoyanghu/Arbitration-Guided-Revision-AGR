from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from src.common import ensure_dir, read_jsonl, write_json, write_jsonl
from src.reliability.score_route_a_reliability import score_reliability_records
from src.retrieval.build_bm25 import build_and_save_index, load_corpus
from src.retrieval.search import run_search
from src.temporal.score_temporal_conflict import score_temporal_records


def enrich_records(retrieval_records: list[dict[str, Any]], queries: list[dict[str, Any]], corpus_path: str | Path) -> list[dict[str, Any]]:
    query_map = {str(query["id"]): query for query in queries}
    corpus_map = {str(row["doc_id"]): row for row in load_corpus(corpus_path)}
    output: list[dict[str, Any]] = []
    for record in retrieval_records:
        query = query_map[str(record["query_id"])]
        corpus_row = corpus_map[str(record["doc_id"])]
        merged = dict(record)
        merged["query_time"] = query["query_time"]
        merged["entity"] = query["entity"]
        merged["focus_attribute"] = query["focus_attribute"]
        merged["case_type"] = query["case_type"]
        merged["preferred_doc_id"] = query["preferred_doc_id"]
        merged["stale_doc_ids"] = query.get("stale_doc_ids", [])
        for key in ("source_type", "evidence_time", "temporal_status", "reliability_bucket"):
            merged[key] = corpus_row.get(key)
        output.append(merged)
    return output


def normalize_bm25(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in records:
        grouped[str(item["query_id"])].append(dict(item))
    output: list[dict[str, Any]] = []
    for items in grouped.values():
        min_score = min(float(it["bm25_score"]) for it in items)
        max_score = max(float(it["bm25_score"]) for it in items)
        for item in items:
            score = float(item["bm25_score"])
            item["bm25_score_norm"] = 1.0 if max_score == min_score else (score - min_score) / (max_score - min_score)
            output.append(item)
    return output


def naive_recency_score(record: dict[str, Any]) -> float:
    query_year = int(record.get("query_time", 0))
    doc_year = int(record.get("evidence_time", 0))
    if doc_year == query_year:
        return 1.0
    if doc_year > query_year:
        return 0.85
    return max(0.0, 0.65 - 0.18 * (query_year - doc_year))


def case_aware_non_graph_score(record: dict[str, Any]) -> float:
    score = float(record.get("bm25_score_norm", 0.0)) * 0.55
    score += float(record.get("temporal_score", 0.0)) * 0.25
    score += float(record.get("reliability_score", 0.0)) * 0.20
    case_type = str(record.get("case_type", ""))
    status = str(record.get("temporal_status", ""))
    reliability = float(record.get("reliability_score", 0.0))
    if case_type == "clear_updated_vs_stale":
        if status == "updated":
            score += 0.10 + 0.04 * reliability
        elif status == "stale":
            score -= 0.08
        elif status == "conflicting":
            score -= 0.06
    elif case_type == "reliability_sensitive_conflict":
        if status == "updated":
            score += 0.08 + 0.08 * reliability
        elif status == "conflicting":
            score -= 0.10
        elif status == "stale":
            score -= 0.02
    else:
        if status == "updated":
            score += 0.12 + 0.06 * reliability
        elif status == "stale":
            score -= 0.07
        elif status == "conflicting":
            score -= 0.05
    return score


def add_strategy_scores(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scored = []
    for record in normalize_bm25(records):
        item = dict(record)
        item["recency_score"] = naive_recency_score(item)
        item["recency_only_score"] = 0.6 * float(item["bm25_score_norm"]) + 0.4 * float(item["recency_score"])
        item["reliability_only_score"] = 0.6 * float(item["bm25_score_norm"]) + 0.4 * float(item["reliability_score"])
        item["temporal_only_score"] = 0.6 * float(item["bm25_score_norm"]) + 0.4 * float(item["temporal_score"])
        item["temporal_plus_reliability_score"] = 0.6 * float(item["bm25_score_norm"]) + 0.25 * float(item["temporal_score"]) + 0.15 * float(item["reliability_score"])
        item["case_aware_non_graph_score"] = case_aware_non_graph_score(item)
        scored.append(item)
    return scored


def rerank(records: list[dict[str, Any]], score_field: str, rank_field: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in records:
        grouped[str(item["query_id"])].append(dict(item))
    output: list[dict[str, Any]] = []
    for items in grouped.values():
        ranked = sorted(items, key=lambda x: float(x.get(score_field, 0.0)), reverse=True)
        for rank, item in enumerate(ranked, start=1):
            item[rank_field] = rank
            output.append(item)
    return output


def group_by_query(records: list[dict[str, Any]], rank_field: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in records:
        grouped[str(item["query_id"])].append(item)
    for key in grouped:
        grouped[key] = sorted(grouped[key], key=lambda x: int(x[rank_field]))
    return dict(grouped)


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


def summarize_stage(queries: list[dict[str, Any]], grouped_records: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    top1 = 0
    pairwise = 0
    stale_wins = 0
    ranks: list[int] = []
    for query in queries:
        records = grouped_records[str(query["id"])]
        p_rank = preferred_rank(records, str(query["preferred_doc_id"]))
        s_rank = stale_best_rank(records, [str(x) for x in query.get("stale_doc_ids", [])])
        if records and str(records[0].get("doc_id")) == str(query["preferred_doc_id"]):
            top1 += 1
        if p_rank is not None:
            ranks.append(p_rank)
        if p_rank is not None and (s_rank is None or p_rank < s_rank):
            pairwise += 1
        if s_rank is not None and (p_rank is None or s_rank < p_rank):
            stale_wins += 1
    total = max(len(queries), 1)
    return {
        "query_count": len(queries),
        "preferred_top1_rate": top1 / total,
        "pairwise_preference_success_rate": pairwise / total,
        "mean_preferred_rank": sum(ranks) / max(len(ranks), 1),
        "preferred_mrr": sum(1.0 / rank for rank in ranks) / total,
        "stale_wins_count": stale_wins,
    }


def build_artifacts(queries: list[dict[str, Any]], grouped_by_stage: dict[str, dict[str, list[dict[str, Any]]]]) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    for query in queries:
        qid = str(query["id"])
        payload = {"query_id": qid, "query": query["query"], "case_type": query["case_type"], "preferred_doc_id": query["preferred_doc_id"], "stale_doc_ids": query.get("stale_doc_ids", [])}
        for stage_name, grouped in grouped_by_stage.items():
            records = grouped[qid]
            payload[f"{stage_name}_preferred_rank"] = preferred_rank(records, str(query["preferred_doc_id"]))
            payload[f"{stage_name}_stale_best_rank"] = stale_best_rank(records, [str(x) for x in query.get("stale_doc_ids", [])])
            payload[f"{stage_name}_candidates"] = records[:5]
        artifacts.append(payload)
    return artifacts


def split_metrics(queries: list[dict[str, Any]], records: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    retrieval_grouped = group_by_query(records, "rank")
    scored = add_strategy_scores(score_reliability_records(score_temporal_records(records)))
    stages = {
        "retrieval_only": retrieval_grouped,
        "recency_only": group_by_query(rerank(scored, "recency_only_score", "recency_only_rank"), "recency_only_rank"),
        "reliability_only": group_by_query(rerank(scored, "reliability_only_score", "reliability_only_rank"), "reliability_only_rank"),
        "temporal_only": group_by_query(rerank(scored, "temporal_only_score", "temporal_only_rank"), "temporal_only_rank"),
        "temporal_plus_reliability": group_by_query(rerank(scored, "temporal_plus_reliability_score", "temporal_plus_reliability_rank"), "temporal_plus_reliability_rank"),
        "case_aware_non_graph_rerank": group_by_query(rerank(scored, "case_aware_non_graph_score", "case_aware_non_graph_rank"), "case_aware_non_graph_rank"),
    }
    metrics = {stage: summarize_stage(queries, grouped) for stage, grouped in stages.items()}
    artifacts = build_artifacts(queries, stages)
    acceptance_snapshot = {
        "temporal_changed_ranking_count": sum(1 for item in artifacts if item["retrieval_only_preferred_rank"] != item["temporal_only_preferred_rank"]),
        "reliability_helped_count": sum(1 for item in artifacts if item["temporal_only_preferred_rank"] is not None and item["temporal_plus_reliability_preferred_rank"] is not None and int(item["temporal_plus_reliability_preferred_rank"]) < int(item["temporal_only_preferred_rank"])),
        "case_aware_helped_count": sum(1 for item in artifacts if item["temporal_plus_reliability_preferred_rank"] is not None and item["case_aware_non_graph_rerank_preferred_rank"] is not None and int(item["case_aware_non_graph_rerank_preferred_rank"]) < int(item["temporal_plus_reliability_preferred_rank"])),
    }
    return {"stages": metrics, "acceptance_snapshot": acceptance_snapshot}, artifacts


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Route A v4 evaluation with fixed dev/test splits.")
    parser.add_argument("--dev-queries", required=True)
    parser.add_argument("--test-queries", required=True)
    parser.add_argument("--corpus", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    run_dir = ensure_dir(args.run_dir)
    index_dir = ensure_dir(Path(run_dir) / "index")
    build_and_save_index(args.corpus, index_dir, backend="json")
    all_metrics: dict[str, Any] = {"top_k": args.top_k, "splits": {}}
    for split, query_path in (("dev", args.dev_queries), ("test", args.test_queries)):
        queries = read_jsonl(query_path)
        split_dir = ensure_dir(Path(run_dir) / split)
        retrieval_records = run_search(args.corpus, index_dir, [{"id": q["id"], "query": q["query"]} for q in queries], args.top_k)
        retrieval_records = enrich_records(retrieval_records, queries, args.corpus)
        write_jsonl(split_dir / "retrieval_results.jsonl", retrieval_records)
        metrics, artifacts = split_metrics(queries, retrieval_records)
        metrics["query_count"] = len(queries)
        write_json(split_dir / "metrics.json", metrics)
        write_jsonl(split_dir / "queries.jsonl", queries)
        write_jsonl(split_dir / "per_query_artifacts.jsonl", artifacts)
        all_metrics["splits"][split] = metrics
    write_json(Path(run_dir) / "metrics.json", all_metrics)
    print(json.dumps(all_metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
