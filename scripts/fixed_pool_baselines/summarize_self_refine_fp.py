from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

from scripts.fixed_pool_baselines.common_io import read_jsonl, write_csv


ROOT = Path("/home/huyaoyang/Projects/flashrag_project_20251213/New_ChronoRAG")
OUT = ROOT / "outputs/published_baseline_adaptations_20260621"
LEGACY = ROOT / "outputs/aei_submission_closure_v1/metrics/strong_baseline_metrics.csv"
DATASETS = {
    "hoh": "HOH-1024",
    "temprageval": "TempRAGEval-1244",
    "timeqa": "TimeQA-500",
}


def mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def main() -> None:
    legacy_rows = list(csv.DictReader(LEGACY.open(encoding="utf-8")))
    legacy = {(row["dataset"], row["method"]): row for row in legacy_rows}
    metrics_rows: list[dict[str, Any]] = []
    ci_rows: list[dict[str, Any]] = []
    diagnostics: dict[str, Any] = {}

    for key, label in DATASETS.items():
        evaluation_path = OUT / f"metrics/self_refine_fp_{key}_evaluation.json"
        evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
        predictions = read_jsonl(OUT / f"predictions/self_refine_fp/self_refine_fp_{key}.jsonl")
        input_tokens = [float(row["total_input_tokens"]) for row in predictions]
        output_tokens = [float(row["total_output_tokens"]) for row in predictions]
        latencies = [float(row["total_latency_sec"]) for row in predictions]
        llm_calls = [float(row["llm_calls"]) for row in predictions]
        parse_failures = sum(str(row.get("parse_status")) != "ok" for row in predictions)
        status_counts = Counter(str(row.get("feedback_status")) for row in predictions)
        metrics_rows.append({
            "dataset": label,
            "model": "Qwen2.5-7B-Instruct",
            "method": "Self-Refine-FP adaptation",
            "n": evaluation["n_evaluated"],
            "EM": evaluation["EM"],
            "F1": evaluation["F1"],
            "Precision": evaluation["Precision"],
            "Recall": evaluation["Recall"],
            "repair": evaluation["repair"],
            "harm": evaluation["harm"],
            "net_repair": evaluation["net_repair"],
            "revision_rate": evaluation["revision_rate"],
            "answer_change_rate": evaluation["answer_change_rate"],
            "avg_input_tokens": mean(input_tokens),
            "avg_output_tokens": mean(output_tokens),
            "avg_latency_sec": mean(latencies),
            "llm_calls_per_query": mean(llm_calls),
            "parse_failure_count": parse_failures,
            "no_extra_retrieval": True,
        })
        diagnostics[key] = {
            "feedback_status_distribution": dict(sorted(status_counts.items())),
            "parse_failure_count": parse_failures,
        }
        for row in list(csv.DictReader((OUT / f"ci/self_refine_fp_{key}_bootstrap.csv").open(encoding="utf-8"))):
            ci_rows.append({"dataset": label, "method": "Self-Refine-FP adaptation", "comparison": "Self-Refine-FP - TP-FP", **row})

    metrics_path = OUT / "metrics/self_refine_fp_metrics.csv"
    ci_path = OUT / "ci/self_refine_fp_bootstrap_ci.csv"
    write_csv(metrics_path, metrics_rows)
    write_csv(ci_path, ci_rows)

    lines = [
        "# Self-Refine-FP Experiment Report",
        "",
        "## Completion",
        "",
        "Self-Refine-FP completed for HOH-1024, TempRAGEval-1244, and TimeQA-500. ArchivalQA-derived-500 was not run in this phase. All runs used the frozen manifest inputs, top-2 evidence from the materialized pools, and the existing TP-FP answer.",
        "",
        "## Results",
        "",
        "| Dataset | n | EM | F1 | Repair | Harm | Net | Revision rate | Avg latency (s) | Avg input tok | Avg output tok |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in metrics_rows:
        lines.append(
            f"| {row['dataset']} | {row['n']} | {row['EM']:.4f} | {row['F1']:.4f} | {row['repair']} | {row['harm']} | "
            f"{row['net_repair']} | {row['revision_rate']:.4f} | {row['avg_latency_sec']:.4f} | "
            f"{row['avg_input_tokens']:.1f} | {row['avg_output_tokens']:.1f} |"
        )
    lines.extend([
        "",
        "## Fidelity Statement",
        "",
        "- Preserved core mechanism: an explicit model-generated feedback/critique stage followed by a separate refinement stage.",
        "- Fixed-pool adaptation: no research, external search, new retrieval, or index rebuild is allowed; both stages see only the same top-2 materialized evidence records.",
        "- Initial answer: existing TP-FP RAG prediction. Gold answers are stored only for offline evaluation and never interpolated into either prompt.",
        "- AGR separation: prompts and output traces do not expose AGR candidate scores, candidate families, arbitration margins, trigger reasons, or update policy.",
        "- Difference from existing FP-SR: FP-SR is a generic one-pass reconsideration prompt. This implementation materializes an independently auditable critique/status, then supplies that self-feedback to a second model call for refinement.",
        "- Recommended paper name: `Self-Refine-FP adaptation`. Do not claim an official reproduction until the exact public prompt/version and iteration policy are mapped and cited.",
        "",
        "## Runtime and Validation",
        "",
        "- LLM calls/query: 2 for every completed row.",
        "- Decoding: temperature=0.1, top_p=1.0, max_new_tokens=256; Qwen2.5-7B-Instruct local checkpoint.",
        "- Bootstrap: paired by query_id, 10,000 resamples, seed=42; consolidated in `ci/self_refine_fp_bootstrap_ci.csv`.",
        f"- Parse diagnostics: `{json.dumps(diagnostics, ensure_ascii=False, sort_keys=True)}`",
        "- Resume behavior: completed query IDs are skipped; prediction rows are appended batch by batch.",
        "",
        "## Comparison Context",
        "",
    ])
    for row in metrics_rows:
        dataset = row["dataset"]
        fp_sr = legacy.get((dataset, "FP-SR"))
        agr = legacy.get((dataset, "AGR"))
        if fp_sr and agr:
            lines.append(
                f"- {dataset}: Self-Refine-FP F1={row['F1']:.4f}; old FP-SR F1={float(fp_sr['F1']):.4f}; AGR F1={float(agr['F1']):.4f}."
            )
    lines.extend([
        "",
        "These comparisons reuse frozen historical rows and the shared evaluator. They do not alter the legacy result package.",
    ])
    report_path = OUT / "reports/self_refine_fp_report.md"
    if report_path.exists():
        raise FileExistsError(report_path)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"metrics={metrics_path} ci={ci_path} report={report_path}")


if __name__ == "__main__":
    main()
