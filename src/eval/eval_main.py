from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.common import ensure_dir, read_jsonl, read_yaml, write_json, write_jsonl
from src.reliability.source_score import score_reliability_records
from src.rerank.rerank import score_and_rank_records
from src.retrieval.search import run_search
from src.temporal.label_relation import score_temporal_records


def _resolve_string(value: str, context: dict[str, Any]) -> str:
    resolved = value
    while "${" in resolved:
        start = resolved.index("${")
        end = resolved.index("}", start)
        token = resolved[start + 2 : end]
        if ":" in token:
            key, default = token.split(":", 1)
        else:
            key, default = token, ""
        replacement = _lookup_key(context, key) if "." in key else os.environ.get(key, default)
        if replacement in (None, "") and "." not in key:
            replacement = default
        if replacement is None:
            raise KeyError(f"Unable to resolve placeholder: {token}")
        resolved = resolved[:start] + str(replacement) + resolved[end + 1 :]
    return resolved


def _lookup_key(data: dict[str, Any], dotted_key: str) -> Any:
    current: Any = data
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            raise KeyError(f"Missing config key: {dotted_key}")
        current = current[part]
    return current


def _resolve_config(node: Any, context: dict[str, Any]) -> Any:
    if isinstance(node, dict):
        resolved_dict: dict[str, Any] = {}
        for key, value in node.items():
            resolved_dict[key] = _resolve_config(value, {**context, **resolved_dict})
        return resolved_dict
    if isinstance(node, list):
        return [_resolve_config(item, context) for item in node]
    if isinstance(node, str):
        return _resolve_string(node, context)
    return node


def load_config(config_path: str | Path) -> dict[str, Any]:
    raw_config = read_yaml(config_path)
    config = _resolve_config(raw_config, raw_config)
    paths = config["paths"]
    route_a = config["route_a"]
    for key in ("data_dir", "raw_data_dir", "processed_data_dir", "corpus_dir", "index_dir", "runs_dir", "log_dir"):
        paths[key] = str(Path(paths[key]))
    route_a["processed_queries"] = str(Path(route_a["processed_queries"]))
    route_a["corpus_path"] = str(Path(route_a["corpus_path"]))
    route_a["bm25_index_dir"] = str(Path(route_a["bm25_index_dir"]))
    config["project"]["root_dir"] = str(Path(config["project"]["root_dir"]))
    return config


def _has_evidence_hit(gold_evidence: list[str], record: dict[str, Any]) -> bool:
    if not gold_evidence:
        return False
    candidate_text = str(record.get("text", "")).lower()
    candidate_title = str(record.get("title", "")).lower()
    for gold in gold_evidence:
        gold_lower = gold.lower()
        if gold_lower and (gold_lower in candidate_text or gold_lower in candidate_title):
            return True
    return False


def _group_sorted(records: list[dict[str, Any]], rank_field: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[str(record["query_id"])].append(record)
    for query_id, items in grouped.items():
        grouped[query_id] = sorted(items, key=lambda item: int(item.get(rank_field, 10**9)))
    return dict(grouped)


def _gold_rank(records: list[dict[str, Any]], gold_evidence: list[str]) -> int | None:
    for index, record in enumerate(records, start=1):
        if _has_evidence_hit(gold_evidence, record):
            return index
    return None


def _recall_at(grouped_records: dict[str, list[dict[str, Any]]], queries: list[dict[str, Any]], k: int) -> float:
    hits = 0
    for query in queries:
        gold_evidence = [str(item).strip() for item in query.get("evidence", []) if str(item).strip()]
        ranked = grouped_records.get(str(query["id"]), [])
        if any(_has_evidence_hit(gold_evidence, record) for record in ranked[:k]):
            hits += 1
    return hits / max(len(queries), 1)


def _label_hit_rates(
    grouped_records: dict[str, list[dict[str, Any]]],
    queries: list[dict[str, Any]],
    k: int,
) -> dict[str, dict[str, Any]]:
    grouped_labels: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for query in queries:
        grouped_labels[str(query.get("label", "UNKNOWN"))].append(query)
    label_metrics: dict[str, dict[str, Any]] = {}
    for label, items in grouped_labels.items():
        hits = 0
        for query in items:
            gold_evidence = [str(item).strip() for item in query.get("evidence", []) if str(item).strip()]
            ranked = grouped_records.get(str(query["id"]), [])
            if any(_has_evidence_hit(gold_evidence, record) for record in ranked[:k]):
                hits += 1
        label_metrics[label] = {
            "count": len(items),
            f"hit_rate_at_{k}": hits / max(len(items), 1),
        }
    return label_metrics


def _stage_metrics(
    stage_name: str,
    grouped_records: dict[str, list[dict[str, Any]]],
    queries: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "stage": stage_name,
        "recall_at_1": _recall_at(grouped_records, queries, 1),
        "recall_at_5": _recall_at(grouped_records, queries, 5),
        "recall_at_10": _recall_at(grouped_records, queries, 10),
        "label_group_hit_rate_at_1": _label_hit_rates(grouped_records, queries, 1),
        "label_group_hit_rate_at_5": _label_hit_rates(grouped_records, queries, 5),
        "label_group_hit_rate_at_10": _label_hit_rates(grouped_records, queries, 10),
    }


def _classify_error(
    raw_rank: int | None,
    final_rank: int | None,
    raw_top1_hit: bool,
    final_top1_hit: bool,
    raw_top1: dict[str, Any] | None,
    final_top1: dict[str, Any] | None,
) -> str | None:
    if raw_rank is None:
        return "retrieval_miss"
    if raw_top1_hit and not final_top1_hit:
        return "rerank_degradation"
    if raw_rank is not None and final_rank is not None and final_rank > raw_rank:
        return "rerank_degradation"
    if raw_top1 and final_top1 and raw_top1.get("doc_id") != final_top1.get("doc_id"):
        raw_aux = float(raw_top1.get("temporal_score", 0.0)) + float(raw_top1.get("reliability_score", 0.0))
        final_aux = float(final_top1.get("temporal_score", 0.0)) + float(final_top1.get("reliability_score", 0.0))
        if final_aux > raw_aux and not final_top1_hit:
            return "score_conflict"
    return None


def compute_metrics(
    queries: list[dict[str, Any]],
    retrieval_records: list[dict[str, Any]],
    temporal_records: list[dict[str, Any]],
    reliability_records: list[dict[str, Any]],
    temporal_reranked_records: list[dict[str, Any]],
    reranked_records: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], str]:
    raw_grouped = _group_sorted(retrieval_records, "rank")
    temporal_grouped = _group_sorted(temporal_reranked_records, "final_rank")
    final_grouped = _group_sorted(reranked_records, "final_rank")

    per_query_analysis: list[dict[str, Any]] = []
    error_cases: list[dict[str, Any]] = []
    raw_top1_hits = 0
    final_top1_hits = 0
    temporal_top1_hits = 0

    improved_by_temporal: list[str] = []
    improved_by_reliability: list[str] = []
    degraded_by_final: list[str] = []

    for query in queries:
        query_id = str(query["id"])
        gold_evidence = [str(item).strip() for item in query.get("evidence", []) if str(item).strip()]
        raw_query_records = raw_grouped.get(query_id, [])
        temporal_query_records = temporal_grouped.get(query_id, [])
        final_query_records = final_grouped.get(query_id, [])
        raw_top1 = raw_query_records[0] if raw_query_records else None
        temporal_top1 = temporal_query_records[0] if temporal_query_records else None
        final_top1 = final_query_records[0] if final_query_records else None

        raw_rank = _gold_rank(raw_query_records, gold_evidence)
        temporal_rank = _gold_rank(temporal_query_records, gold_evidence)
        final_rank = _gold_rank(final_query_records, gold_evidence)

        raw_top1_hit = raw_rank == 1
        temporal_top1_hit = temporal_rank == 1
        final_top1_hit = final_rank == 1
        raw_top1_hits += int(raw_top1_hit)
        temporal_top1_hits += int(temporal_top1_hit)
        final_top1_hits += int(final_top1_hit)

        if temporal_rank is not None and (raw_rank is None or temporal_rank < raw_rank):
            improved_by_temporal.append(query_id)
        if final_rank is not None and (temporal_rank is None or final_rank < temporal_rank):
            improved_by_reliability.append(query_id)
        if raw_rank is not None and final_rank is not None and final_rank > raw_rank:
            degraded_by_final.append(query_id)

        analysis_row = {
            "id": query_id,
            "claim": query.get("claim"),
            "gold_label": query.get("label"),
            "gold_evidence": gold_evidence,
            "bm25_top1_doc_id": raw_top1.get("doc_id") if raw_top1 else None,
            "bm25_temporal_top1_doc_id": temporal_top1.get("doc_id") if temporal_top1 else None,
            "bm25_temporal_reliability_top1_doc_id": final_top1.get("doc_id") if final_top1 else None,
            "bm25_topk_hit": raw_rank is not None,
            "temporal_topk_hit": temporal_rank is not None,
            "final_topk_hit": final_rank is not None,
            "bm25_rank": raw_rank,
            "temporal_rank": temporal_rank,
            "final_rank": final_rank,
            "bm25_top1_hit": raw_top1_hit,
            "temporal_top1_hit": temporal_top1_hit,
            "final_top1_hit": final_top1_hit,
            "temporal_changed_top1": raw_top1.get("doc_id") != temporal_top1.get("doc_id") if raw_top1 and temporal_top1 else False,
            "reliability_changed_top1": temporal_top1.get("doc_id") != final_top1.get("doc_id") if temporal_top1 and final_top1 else False,
            "final_top1_title": final_top1.get("title") if final_top1 else None,
        }
        per_query_analysis.append(analysis_row)

        error_type = _classify_error(raw_rank, final_rank, raw_top1_hit, final_top1_hit, raw_top1, final_top1)
        if error_type:
            error_cases.append(
                {
                    "id": query_id,
                    "claim": query.get("claim"),
                    "gold_label": query.get("label"),
                    "gold_evidence": gold_evidence,
                    "error_type": error_type,
                    "bm25_rank": raw_rank,
                    "temporal_rank": temporal_rank,
                    "final_rank": final_rank,
                    "bm25_top1_doc_id": raw_top1.get("doc_id") if raw_top1 else None,
                    "final_top1_doc_id": final_top1.get("doc_id") if final_top1 else None,
                }
            )

    total = max(len(queries), 1)
    metrics = {
        "query_count": len(queries),
        "stages": {
            "bm25": _stage_metrics("bm25", raw_grouped, queries),
            "bm25_temporal": _stage_metrics("bm25_temporal", temporal_grouped, queries),
            "bm25_temporal_reliability": _stage_metrics("bm25_temporal_reliability", final_grouped, queries),
        },
        "rerank": {
            "raw_top1_hits": raw_top1_hits,
            "temporal_top1_hits": temporal_top1_hits,
            "final_top1_hits": final_top1_hits,
            "top1_improvement_count": final_top1_hits - raw_top1_hits,
            "top1_improvement_rate": (final_top1_hits - raw_top1_hits) / total,
        },
        "error_summary": dict(Counter(item["error_type"] for item in error_cases)),
    }

    temporal_distribution = dict(Counter(str(record.get("temporal_score")) for record in temporal_records))
    reliability_distribution = dict(Counter(str(record.get("reliability_score")) for record in reliability_records))
    analysis = {
        "temporal_score_distribution": temporal_distribution,
        "reliability_score_distribution": reliability_distribution,
        "ranking_change_summary": {
            "improved_by_temporal": improved_by_temporal,
            "improved_by_reliability": improved_by_reliability,
            "degraded_by_final": degraded_by_final,
        },
        "ranking_change_counts": {
            "improved_by_temporal_count": len(improved_by_temporal),
            "improved_by_reliability_count": len(improved_by_reliability),
            "degraded_by_final_count": len(degraded_by_final),
        },
    }
    summary = "\n".join(
        [
            "# Route A Analysis",
            "",
            f"- Query count: {len(queries)}",
            f"- Temporal score distribution: {temporal_distribution}",
            f"- Reliability score distribution: {reliability_distribution}",
            f"- Queries improved by temporal: {len(improved_by_temporal)}",
            f"- Queries improved by reliability: {len(improved_by_reliability)}",
            f"- Queries degraded by final scoring: {len(degraded_by_final)}",
        ]
    )
    return metrics, per_query_analysis, error_cases, analysis, summary


def save_results(
    run_dir: str | Path,
    metrics: dict[str, Any],
    retrieval_records: list[dict[str, Any]],
    temporal_records: list[dict[str, Any]],
    temporal_reranked_records: list[dict[str, Any]],
    reliability_records: list[dict[str, Any]],
    reranked_records: list[dict[str, Any]],
    predictions: list[dict[str, Any]],
    error_cases: list[dict[str, Any]],
    analysis: dict[str, Any],
    analysis_summary: str,
) -> None:
    run_path = ensure_dir(run_dir)
    write_json(run_path / "metrics.json", metrics)
    write_jsonl(run_path / "retrieval_results.jsonl", retrieval_records)
    write_jsonl(run_path / "temporal_results.jsonl", temporal_records)
    write_jsonl(run_path / "temporal_reranked_results.jsonl", temporal_reranked_records)
    write_jsonl(run_path / "reliability_results.jsonl", reliability_records)
    write_jsonl(run_path / "reranked_results.jsonl", reranked_records)
    write_jsonl(run_path / "predictions.jsonl", predictions)
    write_jsonl(run_path / "error_cases.jsonl", error_cases)
    write_json(run_path / "analysis.json", analysis)
    (run_path / "analysis_summary.md").write_text(analysis_summary, encoding="utf-8")


def run_route_a(
    config: dict[str, Any],
    exp_name: str,
    queries_path: str | None = None,
    corpus_path: str | None = None,
    index_dir: str | None = None,
    top_k: int | None = None,
) -> dict[str, Any]:
    route_a = config["route_a"]
    paths = config["paths"]
    run_dir = ensure_dir(Path(paths["runs_dir"]) / exp_name)
    query_path = Path(queries_path or route_a["processed_queries"])
    corpus_file = Path(corpus_path or route_a["corpus_path"])
    index_root = Path(index_dir or route_a["bm25_index_dir"])
    retrieval_top_k = int(top_k or route_a["retrieval_top_k"])
    if not query_path.exists():
        raise FileNotFoundError(f"Processed FEVER file not found: {query_path}")
    if not corpus_file.exists():
        raise FileNotFoundError(f"Corpus file not found: {corpus_file}")

    queries = read_jsonl(query_path)
    retrieval_records = run_search(
        corpus_path=corpus_file,
        index_dir=index_root,
        queries=queries,
        top_k=retrieval_top_k,
    )
    temporal_records = score_temporal_records(retrieval_records)
    temporal_reranked_records = score_and_rank_records(
        temporal_records,
        bm25_weight=float(route_a["bm25_weight"]),
        temporal_weight=float(route_a["temporal_weight"]),
        reliability_weight=0.0,
    )
    reliability_records = score_reliability_records(temporal_records)
    reranked_records = score_and_rank_records(
        reliability_records,
        bm25_weight=float(route_a["bm25_weight"]),
        temporal_weight=float(route_a["temporal_weight"]),
        reliability_weight=float(route_a["reliability_weight"]),
    )
    metrics, per_query_analysis, error_cases, analysis, analysis_summary = compute_metrics(
        queries=queries,
        retrieval_records=retrieval_records,
        temporal_records=temporal_records,
        reliability_records=reliability_records,
        temporal_reranked_records=temporal_reranked_records,
        reranked_records=reranked_records,
    )
    save_results(
        run_dir,
        metrics,
        retrieval_records,
        temporal_records,
        temporal_reranked_records,
        reliability_records,
        reranked_records,
        per_query_analysis,
        error_cases,
        analysis,
        analysis_summary,
    )
    return {
        "run_dir": str(run_dir),
        "metrics": metrics,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ChronoRAG main evaluation entry.")
    parser.add_argument("--route", required=True, choices=["routeA", "routeB", "routeC"])
    parser.add_argument("--config", required=True)
    parser.add_argument("--exp-name", required=True)
    parser.add_argument("--queries-path", default=None)
    parser.add_argument("--corpus-path", default=None)
    parser.add_argument("--index-dir", default=None)
    parser.add_argument("--top-k", type=int, default=None)
    args = parser.parse_args()
    config = load_config(args.config)
    if args.route != "routeA":
        raise NotImplementedError("Only routeA is implemented in the current minimal runnable version.")
    result = run_route_a(
        config=config,
        exp_name=args.exp_name,
        queries_path=args.queries_path,
        corpus_path=args.corpus_path,
        index_dir=args.index_dir,
        top_k=args.top_k,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
