from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.fixed_pool_baselines.common_io import read_jsonl, write_csv, write_json
from scripts.fixed_pool_baselines.fixed_pool_schema import (
    gold_answers,
    predicted_answer,
    prediction_validation,
    query_id,
)
from scripts.fixed_pool_baselines.metrics import bootstrap_rows, mean, metric_payload, recorded_token_counts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate fixed-pool predictions without inference or retrieval.")
    parser.add_argument("--gold", required=True, type=Path)
    parser.add_argument("--predictions", required=True, type=Path)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--output-json", required=True, type=Path)
    parser.add_argument("--output-csv", required=True, type=Path)
    parser.add_argument("--bootstrap-csv", type=Path)
    parser.add_argument("--bootstrap-resamples", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--label", default="method")
    parser.add_argument("--overwrite", action="store_true", help="Only for a new/timestamped output directory.")
    return parser.parse_args()


def unique_map(rows: list[dict[str, Any]], name: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        value = query_id(row)
        if not value:
            continue
        if value in result:
            raise ValueError(f"duplicate query_id {value!r} in {name}")
        result[value] = row
    return result


def evaluate(args: argparse.Namespace) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    gold_rows = read_jsonl(args.gold)
    prediction_rows = read_jsonl(args.predictions)
    gold_map = unique_map(gold_rows, str(args.gold))
    prediction_map = unique_map(prediction_rows, str(args.predictions))
    baseline_rows = read_jsonl(args.baseline) if args.baseline else []
    baseline_map = unique_map(baseline_rows, str(args.baseline)) if args.baseline else {}

    validation = prediction_validation(prediction_rows, set(gold_map))
    baseline_validation = prediction_validation(baseline_rows, set(gold_map)) if args.baseline else None
    common_ids = sorted(set(gold_map) & set(prediction_map) & (set(baseline_map) if args.baseline else set(gold_map)))

    per_query: list[dict[str, Any]] = []
    input_tokens: list[int] = []
    output_tokens: list[int] = []
    latencies: list[float] = []
    for value in common_ids:
        answers = gold_answers(gold_map[value])
        prediction = predicted_answer(prediction_map[value])
        metrics = metric_payload(prediction, answers)
        row: dict[str, Any] = {"query_id": value, **metrics}
        if args.baseline:
            baseline_answer = predicted_answer(baseline_map[value])
            baseline_metrics = metric_payload(baseline_answer, answers)
            for metric in ("EM", "F1", "Precision", "Recall"):
                row[f"baseline_{metric}"] = baseline_metrics[metric]
                row[f"delta_{metric}"] = metrics[metric] - baseline_metrics[metric]
            row["repair"] = int(baseline_metrics["EM"] == 0.0 and metrics["EM"] == 1.0)
            row["harm"] = int(baseline_metrics["EM"] == 1.0 and metrics["EM"] == 0.0)
            row["answer_changed"] = int(prediction.strip() != baseline_answer.strip())
        tokens_in, tokens_out = recorded_token_counts(prediction_map[value])
        if tokens_in is not None:
            input_tokens.append(tokens_in)
        if tokens_out is not None:
            output_tokens.append(tokens_out)
        if prediction_map[value].get("latency_sec") not in (None, "", "NA"):
            latencies.append(float(prediction_map[value]["latency_sec"]))
        per_query.append(row)

    summary: dict[str, Any] = {
        "label": args.label,
        "gold_file": str(args.gold.resolve()),
        "prediction_file": str(args.predictions.resolve()),
        "baseline_file": str(args.baseline.resolve()) if args.baseline else None,
        "n_evaluated": len(per_query),
        "EM": mean([row["EM"] for row in per_query]),
        "F1": mean([row["F1"] for row in per_query]),
        "Precision": mean([row["Precision"] for row in per_query]),
        "Recall": mean([row["Recall"] for row in per_query]),
        "validation": validation,
        "baseline_validation": baseline_validation,
        "avg_input_tokens": mean(input_tokens) if input_tokens else None,
        "avg_output_tokens": mean(output_tokens) if output_tokens else None,
        "avg_latency_sec": mean(latencies) if latencies else None,
    }
    if args.baseline:
        repairs = sum(row["repair"] for row in per_query)
        harms = sum(row["harm"] for row in per_query)
        changed = sum(row["answer_changed"] for row in per_query)
        revision_count = sum(bool(prediction_map[value].get("revision_applied", False)) for value in common_ids)
        has_revision_field = any("revision_applied" in prediction_map[value] for value in common_ids)
        summary.update({
            "repair": repairs,
            "harm": harms,
            "net_repair": repairs - harms,
            "revision_rate": revision_count / len(per_query) if has_revision_field and per_query else None,
            "answer_change_rate": changed / len(per_query) if per_query else 0.0,
        })

    ci_rows = bootstrap_rows(per_query, bool(args.baseline), args.bootstrap_resamples, args.seed)
    summary["bootstrap_ci"] = ci_rows
    return summary, ci_rows


def main() -> None:
    args = parse_args()
    summary, ci_rows = evaluate(args)
    write_json(args.output_json, summary, overwrite=args.overwrite)
    flat = {key: value for key, value in summary.items() if not isinstance(value, (dict, list))}
    write_csv(args.output_csv, [flat], overwrite=args.overwrite)
    if args.bootstrap_csv:
        write_csv(args.bootstrap_csv, ci_rows, overwrite=args.overwrite)
    print(json.dumps(flat, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
