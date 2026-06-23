from __future__ import annotations

import csv
import json
from argparse import Namespace
from pathlib import Path

import matplotlib.pyplot as plt

from scripts.fixed_pool_baselines.common_io import read_jsonl, write_csv, write_json
from scripts.fixed_pool_baselines.evaluate_fixed_pool_predictions import evaluate
from scripts.fixed_pool_baselines.fixed_pool_schema import query_id


ROOT = Path("/home/huyaoyang/Projects/flashrag_project_20251213/New_ChronoRAG")
NIGHTLY = ROOT / "outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528"
REPAIR = NIGHTLY / "fairness_repair"
SOURCE = ROOT / "outputs/published_baseline_adaptations_20260621/predictions/faithfulrag_fp"
BASELINE = ROOT / "outputs/aei_submission_closure_v1/predictions/strong_baselines"

DATASETS = {
    "hoh": ("HOH-1024", "hoh1024", ROOT / "data/processed/hoh_formal_1024.jsonl"),
    "temprageval": ("TempRAGEval-1244", "temprageval1244", ROOT / "data/processed/temprageval_formal_1244.jsonl"),
    "timeqa": ("TimeQA-500", "timeqa500", ROOT / "outputs/paper_assets_final/timeqa500_formal/timeqa500_examples.jsonl"),
}


def is_parse_failure(row: dict) -> bool:
    return bool(row.get("parsing_failure", False)) or str(row.get("parse_status", "")).lower() not in ("", "ok", "success")


def md_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines.extend("| " + " | ".join(str(value) for value in row) + " |" for row in rows)
    return "\n".join(lines) + "\n"


def main() -> None:
    repaired = {str(row["repair_key"]): row for row in read_jsonl(REPAIR / "repaired_rows.jsonl")}
    main_rows = list(csv.DictReader((NIGHTLY / "metrics/main_results.csv").open()))
    old_ci = list(csv.DictReader((NIGHTLY / "ci/paired_bootstrap_all.csv").open()))
    new_ci = [row for row in old_ci if row["method"] != "FaithfulRAG-inspired FP control"]
    audit_rows = []
    summaries = {}
    prediction_dir = REPAIR / "predictions/faithfulrag_fp"
    prediction_dir.mkdir(parents=True, exist_ok=True)
    for dataset, (dataset_label, suffix, gold) in DATASETS.items():
        source_rows = read_jsonl(SOURCE / f"faithfulrag_fp_{dataset}.jsonl")
        merged = [repaired.get(f"{dataset}::{row['query_id']}", row) for row in source_rows]
        output = prediction_dir / f"faithfulrag_fp_{dataset}_parse_repaired.jsonl"
        with output.open("w", encoding="utf-8") as handle:
            for row in merged:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        old_fail = sum(is_parse_failure(row) for row in source_rows)
        new_fail = sum(is_parse_failure(row) for row in merged)
        audit_rows.append({
            "method": "FaithfulRAG-inspired FP control", "dataset": dataset_label,
            "n": len(merged), "old_parse_failures": old_fail, "old_parse_fail_rate": old_fail / len(merged),
            "new_parse_failures": new_fail, "new_parse_fail_rate": new_fail / len(merged),
            "repaired_rows": sum(f"{dataset}::{row['query_id']}" in repaired for row in source_rows),
            "all_query_ids_preserved": [query_id(row) for row in source_rows] == [query_id(row) for row in merged],
            "all_no_extra_retrieval": all(row.get("no_extra_retrieval") is True for row in merged),
            "empty_final_answers": sum(not str(row.get("final_answer", "")).strip() for row in merged),
        })
        args = Namespace(
            gold=gold, predictions=output, baseline=BASELINE / f"tp_fp_rag_{suffix}.jsonl",
            output_json=Path("unused"), output_csv=Path("unused"), bootstrap_csv=None,
            bootstrap_resamples=10000, seed=42, label=f"FaithfulRAG-inspired FP control parse-repaired - {dataset_label}", overwrite=True,
        )
        summary, ci = evaluate(args)
        summary["method"] = "FaithfulRAG-inspired FP control"
        summary["dataset"] = dataset_label
        summary["parse_failure_count"] = new_fail
        summary["llm_calls_per_query"] = 2.0
        summaries[dataset_label] = summary
        write_json(REPAIR / f"metrics/faithfulrag_fp_{dataset}_evaluation.json", summary, overwrite=True)
        write_csv(REPAIR / f"ci/faithfulrag_fp_{dataset}_bootstrap.csv", [{"method": summary["method"], "dataset": dataset_label, **row} for row in ci], overwrite=True)
        new_ci.extend({"method": summary["method"], "dataset": dataset_label, **row} for row in ci)

    write_csv(REPAIR / "validation/parse_failure_before_after.csv", audit_rows, overwrite=True)
    fields = list(main_rows[0])
    updated_main = []
    for row in main_rows:
        if row["method"] != "FaithfulRAG-inspired FP control":
            updated_main.append(row)
            continue
        summary = summaries[row["dataset"]]
        replacement = dict(row)
        for key in ("n_evaluated", "EM", "F1", "Precision", "Recall", "repair", "harm", "net_repair", "revision_rate", "answer_change_rate", "avg_input_tokens", "avg_output_tokens", "avg_latency_sec", "parse_failure_count", "llm_calls_per_query"):
            replacement[key] = summary.get(key, replacement.get(key, "UNKNOWN"))
        updated_main.append(replacement)
    write_csv(REPAIR / "metrics/main_results_parse_repaired.csv", updated_main, overwrite=True)
    write_csv(REPAIR / "ci/paired_bootstrap_all_parse_repaired.csv", new_ci, overwrite=True)

    placement = {"FaithfulRAG-inspired FP control": "Appendix (fidelity)", "CRAG-inspired FP evaluator control": "Appendix (fidelity)"}
    table_rows = [[row["method"], row["dataset"], f"{100*float(row['EM']):.2f}", f"{100*float(row['F1']):.2f}", row["net_repair"], row["parse_failure_count"], placement.get(row["method"], "Main")] for row in updated_main]
    (REPAIR / "tables/Table4_parse_repaired.md").parent.mkdir(parents=True, exist_ok=True)
    (REPAIR / "tables/Table4_parse_repaired.md").write_text(md_table(["Method", "Dataset", "EM (%)", "F1 (%)", "Net repair", "Parse failures", "Placement"], table_rows), encoding="utf-8")
    write_csv(REPAIR / "tables/Table4_parse_repaired.csv", updated_main, overwrite=True)

    datasets = [value[0] for value in DATASETS.values()]
    methods = list(dict.fromkeys(row["method"] for row in updated_main))
    lookup = {(row["method"], row["dataset"]): row for row in updated_main}
    figure_rows = [{"method": method, "mean_EM": sum(float(lookup[(method, dataset)]["EM"]) for dataset in datasets) / 3, "mean_F1": sum(float(lookup[(method, dataset)]["F1"]) for dataset in datasets) / 3} for method in methods]
    write_csv(REPAIR / "figures/Figure3_parse_repaired_source.csv", figure_rows, overwrite=True)
    fig, ax = plt.subplots(figsize=(11, 5.5))
    colors = ["#b2182b" if row["method"] == "AGR" else "#2166ac" if row["method"] == "TP-FP RAG" else "#777777" for row in figure_rows]
    ax.bar(range(len(figure_rows)), [100 * row["mean_EM"] for row in figure_rows], color=colors)
    ax.set_ylabel("Mean EM (%)"); ax.set_xticks(range(len(figure_rows))); ax.set_xticklabels([row["method"] for row in figure_rows], rotation=35, ha="right")
    ax.set_title("Fixed-pool performance after parse-fairness repair"); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(REPAIR / "figures/Figure3_parse_repaired.png", dpi=220); fig.savefig(REPAIR / "figures/Figure3_parse_repaired.pdf"); plt.close(fig)

    old_lookup = {(row["method"], row["dataset"]): row for row in main_rows}
    faith_old_em = sum(float(old_lookup[("FaithfulRAG-inspired FP control", dataset)]["EM"]) for dataset in datasets) / 3
    faith_new_em = sum(float(lookup[("FaithfulRAG-inspired FP control", dataset)]["EM"]) for dataset in datasets) / 3
    faith_old_f1 = sum(float(old_lookup[("FaithfulRAG-inspired FP control", dataset)]["F1"]) for dataset in datasets) / 3
    faith_new_f1 = sum(float(lookup[("FaithfulRAG-inspired FP control", dataset)]["F1"]) for dataset in datasets) / 3
    report = f"""# Section 5.1 Parse-Failure Decision

## Decision

- **RARR-FP adaptation:** keep the existing results. Its parse-failure rates are 0.78% (HOH), 3.86% (TempRAGEval), and 1.20% (TimeQA), below the 10-point fairness threshold. Failed RARR rows were not automatically zero-scored: several had non-zero F1 or exact match.
- **FaithfulRAG-inspired FP control:** use the parse-repaired sensitivity results, not the original numbers, if reporting numeric results. The original TimeQA parse-failure rate was 10.40%, and all flagged rows had F1=0 because truncated/wrapped fact JSON was discarded, leaving the answer stage with empty facts.

## Repair Scope

Only the answer stage was rerun for 106 rows whose raw extraction contained recoverable complete fact objects. Five TempRAGEval rows remained conservatively unrecoverable. No retrieval, evidence change, gold prompt input, or AGR signal was used. The other 2,662 FaithfulRAG rows were not rerun.

{md_table(['Dataset', 'Old parse rate', 'New parse rate', 'Repaired'], [[row['dataset'], f"{100*row['old_parse_fail_rate']:.2f}%", f"{100*row['new_parse_fail_rate']:.2f}%", row['repaired_rows']] for row in audit_rows])}
FaithfulRAG-inspired mean EM changed from **{100*faith_old_em:.2f}%** to **{100*faith_new_em:.2f}%**; mean F1 changed from **{100*faith_old_f1:.2f}%** to **{100*faith_new_f1:.2f}%**. This quantifies the parsing artifact rather than hiding it.

## Paper Use

FaithfulRAG-inspired should still remain in the appendix because the fidelity limitation is independent of parsing: no reusable official implementation was found. RARR-FP may remain in the main comparison with the fixed-pool adaptation footnote. Do not state that evaluator parse failures were mechanically assigned zero; explain that the original fact parser discarded truncated arrays and thereby produced empty fact traces.
"""
    (REPAIR / "reports/SECTION_5_1_PARSE_FAILURE_DECISION.md").parent.mkdir(parents=True, exist_ok=True)
    (REPAIR / "reports/SECTION_5_1_PARSE_FAILURE_DECISION.md").write_text(report, encoding="utf-8")
    print(json.dumps({"repaired_rows": len(repaired), "audit": audit_rows, "faith_old_em": faith_old_em, "faith_new_em": faith_new_em, "faith_old_f1": faith_old_f1, "faith_new_f1": faith_new_f1}, indent=2))


if __name__ == "__main__":
    main()
