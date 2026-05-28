from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from src.common import ensure_dir, read_jsonl, read_yaml, write_json, write_jsonl
from src.rag.answer_generation import generate_answer
from src.rag.conflict_arbitration import build_scored_candidates, select_evidence_bundle
from src.rag.contracts import QueryRecord, to_query_record
from src.rag.learned_scorer import load_scorer
from src.retrieval.search import run_search


TOKEN_SPLIT = re.compile(r"\W+")
CITATION_PATTERN = re.compile(r"\[\d+\]")


def _lookup_key(data: dict[str, Any], dotted_key: str) -> Any:
    current: Any = data
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            raise KeyError(f"Missing config key: {dotted_key}")
        current = current[part]
    return current


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
        replacement = _lookup_key(context, key) if "." in key else default
        resolved = resolved[:start] + str(replacement) + resolved[end + 1 :]
    return resolved


def _resolve_node(node: Any, context: dict[str, Any]) -> Any:
    if isinstance(node, dict):
        resolved_dict: dict[str, Any] = {}
        for key, value in node.items():
            resolved_dict[key] = _resolve_node(value, {**context, **resolved_dict})
        return resolved_dict
    if isinstance(node, list):
        return [_resolve_node(item, context) for item in node]
    if isinstance(node, str):
        return _resolve_string(node, context)
    return node


def _resolve_config(config_path: str | Path) -> dict[str, Any]:
    raw = read_yaml(config_path)
    return _resolve_node(raw, raw)


def _strip_eval_artifacts(text: str) -> str:
    cleaned = CITATION_PATTERN.sub(" ", text)
    cleaned = cleaned.split("| evidence:")[0]
    return cleaned.strip()


def _normalize_text(text: str) -> str:
    return " ".join(TOKEN_SPLIT.split(_strip_eval_artifacts(text.lower()))).strip()


def exact_match(prediction: str, gold_answers: list[str]) -> float:
    normalized_pred = _normalize_text(prediction)
    if not gold_answers:
        return 0.0
    return 1.0 if any(_normalize_text(answer) == normalized_pred for answer in gold_answers) else 0.0


def token_f1(prediction: str, gold_answers: list[str]) -> float:
    pred_tokens = _normalize_text(prediction).split()
    if not gold_answers:
        return 0.0
    best = 0.0
    for answer in gold_answers:
        gold_tokens = _normalize_text(answer).split()
        if not pred_tokens and not gold_tokens:
            best = max(best, 1.0)
            continue
        common = 0
        gold_counts: dict[str, int] = defaultdict(int)
        for token in gold_tokens:
            gold_counts[token] += 1
        for token in pred_tokens:
            if gold_counts[token] > 0:
                common += 1
                gold_counts[token] -= 1
        if common == 0:
            continue
        precision = common / max(len(pred_tokens), 1)
        recall = common / max(len(gold_tokens), 1)
        best = max(best, 2 * precision * recall / max(precision + recall, 1e-8))
    return best


def citation_title_recall(selected_evidence: list[dict[str, Any]], gold_titles: list[str]) -> float | None:
    if not gold_titles:
        return None
    selected_titles = {str(item.get("title", "")).strip().lower() for item in selected_evidence if str(item.get("title", "")).strip()}
    gold = {title.strip().lower() for title in gold_titles if title.strip()}
    if not gold:
        return None
    return len(selected_titles & gold) / len(gold)


def run_pipeline(config: dict[str, Any], exp_name: str) -> dict[str, Any]:
    mainline = config["mainline"]
    run_stage = str(mainline.get("run_stage", "debug_or_pilot")).strip() or "debug_or_pilot"
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
    learned_model = None
    if str(mainline.get("learned_scorer_path", "")).strip():
        learned_model = load_scorer(str(mainline["learned_scorer_path"]))

    scored = build_scored_candidates(
        query_records=query_records,
        retrieval_records=retrieval_records,
        bm25_weight=float(mainline["bm25_weight"]),
        lexical_weight=float(mainline["lexical_weight"]),
        temporal_weight=float(mainline["temporal_weight"]),
        conflict_weight=float(mainline["conflict_weight"]),
        structured_weight=float(mainline.get("structured_weight", 0.0)),
        reliability_weight=float(mainline["reliability_weight"]),
        learned_weight=float(mainline.get("learned_weight", 0.0)),
        learned_model=learned_model,
        posterior_enabled=bool(mainline.get("posterior_enabled", False)),
        gate_enabled=bool(mainline.get("gate_enabled", False)),
        fixed_gamma=float(mainline.get("fixed_gamma", 0.5)),
        family_conflict_weight=float(mainline.get("family_conflict_weight", 0.7)),
        global_conflict_weight=float(mainline.get("global_conflict_weight", 0.3)),
    )
    bundles = select_evidence_bundle(
        scored,
        evidence_top_k=int(mainline["evidence_top_k"]),
        enable_top_gap_filtering=bool(mainline.get("enable_top_gap_filtering", True)),
        enable_duplicate_suppression=bool(mainline.get("enable_duplicate_suppression", True)),
        top_gap_threshold=float(mainline.get("top_gap_threshold", 0.10)),
    )
    predictions = []
    em_total = 0.0
    f1_total = 0.0
    citation_total = 0.0
    citation_count = 0
    abstention_total = 0

    for query_record in query_records:
        prediction = generate_answer(
            query_record=query_record,
            candidates=bundles.get(query_record.query_id, []),
            generation_mode=str(mainline["generation_mode"]),
        )
        em = exact_match(prediction.predicted_answer, query_record.answers)
        f1 = token_f1(prediction.predicted_answer, query_record.answers)
        citation = citation_title_recall(prediction.selected_evidence, query_record.gold_evidence_titles)
        prediction.metrics = {
            "exact_match": em,
            "token_f1": f1,
            "citation_title_recall": citation,
        }
        predictions.append(
            {
                "query_id": prediction.query_id,
                "query": prediction.query,
                "predicted_answer": prediction.predicted_answer,
                "selected_evidence": prediction.selected_evidence,
                "arbitration_trace": prediction.arbitration_trace,
                "metrics": prediction.metrics,
            }
        )
        em_total += em
        f1_total += f1
        if bool(prediction.arbitration_trace.get("abstained")):
            abstention_total += 1
        if citation is not None:
            citation_total += citation
            citation_count += 1

    run_dir = ensure_dir(Path(config["paths"]["runs_dir"]) / exp_name)
    metrics = {
        "query_count": len(query_records),
        "answer_level": {
            "exact_match": em_total / max(len(query_records), 1),
            "token_f1": f1_total / max(len(query_records), 1),
            "citation_title_recall": citation_total / citation_count if citation_count else None,
            "abstention_rate": abstention_total / max(len(query_records), 1),
        },
        "retrieval_top_k": int(mainline["retrieval_top_k"]),
        "evidence_top_k": int(mainline["evidence_top_k"]),
        "generation_mode": str(mainline["generation_mode"]),
        "retrieval_strategy": str(mainline.get("retrieval_strategy", "standard")),
        "structured_weight": float(mainline.get("structured_weight", 0.0)),
        "learned_weight": float(mainline.get("learned_weight", 0.0)),
        "posterior_enabled": bool(mainline.get("posterior_enabled", False)),
        "gate_enabled": bool(mainline.get("gate_enabled", False)),
        "fixed_gamma": float(mainline.get("fixed_gamma", 0.5)),
        "family_conflict_weight": float(mainline.get("family_conflict_weight", 0.7)),
        "global_conflict_weight": float(mainline.get("global_conflict_weight", 0.3)),
        "enable_top_gap_filtering": bool(mainline.get("enable_top_gap_filtering", True)),
        "enable_duplicate_suppression": bool(mainline.get("enable_duplicate_suppression", True)),
        "top_gap_threshold": float(mainline.get("top_gap_threshold", 0.10)),
        "status": run_stage,
    }
    write_json(run_dir / "metrics.json", metrics)
    write_jsonl(run_dir / "retrieval_results.jsonl", retrieval_records)
    write_jsonl(
        run_dir / "scored_candidates.jsonl",
        [
                {
                    "query_id": item.query_id,
                    "doc_id": item.doc_id,
                    "title": item.title,
                    "source": item.source,
                    "source_type": item.source_type,
                    "timestamp": item.timestamp,
                    "bm25_score": item.bm25_score,
                "lexical_score": item.lexical_score,
                "temporal_score": item.temporal_score,
                "conflict_score": item.conflict_score,
                "structured_score": item.structured_score,
                "learned_score": item.learned_score,
                "reliability_score": item.reliability_score,
                "retrieval_prior": item.retrieval_prior,
                "temporal_expert_score": item.temporal_expert_score,
                "conflict_expert_score": item.conflict_expert_score,
                "evidence_logit": item.evidence_logit,
                "evidence_attention_weight": item.evidence_attention_weight,
                "gate_gamma": item.gate_gamma,
                "arbitration_score": item.arbitration_score,
                "notes": item.notes,
            }
            for item in scored
        ],
    )
    write_jsonl(run_dir / "predictions.jsonl", predictions)
    summary_lines = [
        "# Conflict-Aware Temporal Faithful RAG",
        "",
        f"- Query count: {len(query_records)}",
        f"- Exact Match: {metrics['answer_level']['exact_match']:.3f}",
        f"- Token F1: {metrics['answer_level']['token_f1']:.3f}",
        f"- Citation title recall: {metrics['answer_level']['citation_title_recall']}",
        f"- Generation mode: {metrics['generation_mode']}",
        f"- Run stage: {run_stage}",
    ]
    (run_dir / "summary.md").write_text("\n".join(summary_lines), encoding="utf-8")
    return {"run_dir": str(run_dir), "metrics": metrics}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run answer-level conflict-aware faithful RAG.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--exp-name", required=True)
    args = parser.parse_args()
    result = run_pipeline(_resolve_config(args.config), args.exp_name)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
