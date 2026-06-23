from __future__ import annotations

import csv
import json
from pathlib import Path

from scripts.fixed_pool_baselines.common_io import write_csv, write_json


ROOT = Path("/home/huyaoyang/Projects/flashrag_project_20251213/New_ChronoRAG")
VALIDATION = ROOT / "outputs/published_baseline_adaptations_20260621/validation"
LEGACY = ROOT / "outputs/aei_submission_closure_v1/metrics/strong_baseline_metrics.csv"

CASES = {
    "tp_fp_hoh": ("HOH-1024", "TP-FP RAG"),
    "agr_vs_tp_hoh": ("HOH-1024", "AGR"),
    "tp_fp_temprageval": ("TempRAGEval-1244", "TP-FP RAG"),
    "agr_vs_tp_temprageval": ("TempRAGEval-1244", "AGR"),
    "tp_fp_timeqa": ("TimeQA-500", "TP-FP RAG"),
    "agr_vs_tp_timeqa": ("TimeQA-500", "AGR"),
    "tp_fp_archivalqa": ("ArchivalQA-derived-500", "TP-FP RAG"),
    "agr_vs_tp_archivalqa": ("ArchivalQA-derived-500", "AGR"),
}


def main() -> None:
    legacy_rows = list(csv.DictReader(LEGACY.open(encoding="utf-8")))
    lookup = {(row["dataset"], row["method"]): row for row in legacy_rows}
    rows = []
    for stem, key in CASES.items():
        current = json.loads((VALIDATION / f"{stem}.json").read_text(encoding="utf-8"))
        legacy = lookup[key]
        em_diff = float(current["EM"]) - float(legacy["EM"])
        f1_diff = float(current["F1"]) - float(legacy["F1"])
        rows.append({
            "dataset": key[0],
            "method": key[1],
            "n": current["n_evaluated"],
            "recomputed_EM": current["EM"],
            "legacy_EM": legacy["EM"],
            "EM_difference": em_diff,
            "recomputed_F1": current["F1"],
            "legacy_F1": legacy["F1"],
            "F1_difference": f1_diff,
            "prediction_complete": current["validation"]["complete"],
            "parse_failure_count": current["validation"]["parse_failure_count"],
            "status": "MATCH" if abs(em_diff) <= 1e-12 and abs(f1_diff) <= 1e-12 else "MISMATCH",
        })
    write_csv(VALIDATION / "metric_reproduction.csv", rows)
    write_json(VALIDATION / "metric_reproduction.json", rows)
    mismatches = [row for row in rows if row["status"] != "MATCH"]
    lines = [
        "# Legacy Metric Reproduction Report",
        "",
        f"- Compared rows: {len(rows)}",
        f"- Exact matches (tolerance 1e-12): {len(rows) - len(mismatches)}",
        f"- Mismatches: {len(mismatches)}",
        "- Canonical metric source: `src/eval/eval_conflict_aware_rag.py`",
        "",
        "| Dataset | Method | n | EM diff | F1 diff | Status |",
        "|---|---|---:|---:|---:|---|",
    ]
    lines.extend(
        f"| {row['dataset']} | {row['method']} | {row['n']} | {row['EM_difference']:.3g} | {row['F1_difference']:.3g} | {row['status']} |"
        for row in rows
    )
    if mismatches:
        lines.extend(["", "## Mismatch Warning", "", "Differences were reported as observed; no legacy result was modified."])
    (VALIDATION / "metric_reproduction_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"compared={len(rows)} matches={len(rows)-len(mismatches)} mismatches={len(mismatches)}")


if __name__ == "__main__":
    main()
