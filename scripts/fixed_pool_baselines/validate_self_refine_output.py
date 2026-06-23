from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from scripts.fixed_pool_baselines.common_io import read_jsonl, write_json
from scripts.fixed_pool_baselines.fixed_pool_schema import query_id


REQUIRED = {
    "query_id", "dataset", "question", "gold", "evidence_ids", "initial_answer", "feedback_text", "final_answer",
    "answer_changed", "llm_calls", "input_tokens_feedback", "output_tokens_feedback", "input_tokens_refinement",
    "output_tokens_refinement", "total_input_tokens", "total_output_tokens", "latency_feedback_sec",
    "latency_refinement_sec", "total_latency_sec", "parse_status", "model_path", "prompt_version",
    "no_extra_retrieval",
}
FORBIDDEN = {
    "candidate_list", "candidate_scores", "candidate_family", "arbitration_trace", "arbitration_margin",
    "arbitration_score", "update_policy", "trigger_reason",
}


def write_jsonl_new(path: Path, rows: list[dict[str, Any]]) -> None:
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        import json
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--expected-count", type=int, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--gold-subset", type=Path)
    parser.add_argument("--baseline-subset", type=Path)
    args = parser.parse_args()

    predictions = read_jsonl(args.predictions)
    ids = [query_id(row) for row in predictions]
    problems: list[str] = []
    if len(predictions) != args.expected_count:
        problems.append(f"row_count={len(predictions)} expected={args.expected_count}")
    if len(set(ids)) != len(ids):
        problems.append("duplicate query_id")
    for index, row in enumerate(predictions):
        missing = sorted(REQUIRED - set(row))
        forbidden = sorted(FORBIDDEN & set(row))
        if missing:
            problems.append(f"row {index} missing={missing}")
        if forbidden:
            problems.append(f"row {index} forbidden={forbidden}")
        if row.get("llm_calls") != 2:
            problems.append(f"row {index} llm_calls={row.get('llm_calls')}")
        if row.get("no_extra_retrieval") is not True:
            problems.append(f"row {index} no_extra_retrieval is not true")
        if not str(row.get("feedback_text", "")).strip() or not str(row.get("final_answer", "")).strip():
            problems.append(f"row {index} empty feedback/final answer")
        if len(row.get("evidence_ids", [])) > 2:
            problems.append(f"row {index} evidence count exceeds 2")

    wanted = set(ids)
    gold_subset = [row for row in read_jsonl(args.gold) if query_id(row) in wanted]
    baseline_subset = [row for row in read_jsonl(args.baseline) if query_id(row) in wanted]
    if len(gold_subset) != len(wanted) or len(baseline_subset) != len(wanted):
        problems.append("gold/baseline subset coverage mismatch")
    if args.gold_subset:
        write_jsonl_new(args.gold_subset, gold_subset)
    if args.baseline_subset:
        write_jsonl_new(args.baseline_subset, baseline_subset)
    report = {
        "prediction_file": str(args.predictions.resolve()),
        "row_count": len(predictions),
        "unique_query_ids": len(set(ids)),
        "parse_status_distribution": {
            value: sum(1 for row in predictions if str(row.get("parse_status")) == value)
            for value in sorted({str(row.get("parse_status")) for row in predictions})
        },
        "answer_changed_count": sum(bool(row.get("answer_changed")) for row in predictions),
        "problems": problems,
        "status": "PASS" if not problems else "FAIL",
    }
    write_json(args.report, report)
    print(f"dryrun schema validation: {report['status']} problems={len(problems)}")
    if problems:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
