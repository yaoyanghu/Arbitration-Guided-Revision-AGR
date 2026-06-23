from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path("/home/huyaoyang/Projects/flashrag_project_20251213/New_ChronoRAG")
OUT = ROOT / "outputs/published_baseline_adaptations_20260621"


def main() -> None:
    manifest = json.loads((OUT / "manifest/fixed_pool_manifest.json").read_text(encoding="utf-8"))
    reproduction = list(csv.DictReader((OUT / "validation/metric_reproduction.csv").open(encoding="utf-8")))
    validation_files = sorted((OUT / "validation").glob("agr_vs_tp_*.json")) + sorted((OUT / "validation").glob("tp_fp_*.json"))
    validations = [json.loads(path.read_text(encoding="utf-8")) for path in validation_files]
    retrieval_entries = [entry for entry in manifest["entries"] if entry["kind"] == "retrieval"]
    prediction_entries = [entry for entry in manifest["entries"] if entry["kind"] == "existing_prediction"]
    mismatches = [row for row in reproduction if row["status"] != "MATCH"]
    parse_failures = sum(item["validation"]["parse_failure_count"] for item in validations)
    incomplete = [item["label"] for item in validations if not item["validation"]["complete"]]

    lines = [
        "# Phase 1 Foundation Summary",
        "",
        "## Outcome",
        "",
        f"- Manifest: {'PASS' if manifest['all_required_readable'] else 'FAIL'}; {manifest['entry_count']} entries, all exist={manifest['all_required_exist']}, all readable={manifest['all_required_readable']}.",
        f"- Frozen prediction files inventoried: {len(prediction_entries)}.",
        f"- Offline evaluator comparisons: {len(reproduction)}; exact/near-exact matches={len(reproduction)-len(mismatches)}; mismatches={len(mismatches)}.",
        f"- Prediction ID completeness failures: {', '.join(incomplete) if incomplete else 'none'}.",
        f"- Recorded parse-failure rows across the eight validation inputs: {parse_failures} (reported, not silently corrected).",
        "- LLM inference, new retrieval, and index rebuild: none.",
        "",
        "## Retrieval Pool Checks",
        "",
        "| Relative path | Rows | Query IDs | Rows/query distribution |",
        "|---|---:|---:|---|",
    ]
    for entry in retrieval_entries:
        distribution = json.dumps(entry["retrieval_rows_per_query_distribution"], sort_keys=True)
        lines.append(f"| `{entry['relative_path']}` | {entry['row_count']} | {entry['query_id_count']} | `{distribution}` |")
    lines.extend([
        "",
        "## Metric Reproduction",
        "",
        "| Dataset | Method | n | EM difference | F1 difference | Status |",
        "|---|---|---:|---:|---:|---|",
    ])
    lines.extend(
        f"| {row['dataset']} | {row['method']} | {row['n']} | {float(row['EM_difference']):.3g} | {float(row['F1_difference']):.3g} | {row['status']} |"
        for row in reproduction
    )
    lines.extend([
        "",
        "## Infrastructure Added",
        "",
        "- `scripts/fixed_pool_baselines/`: shared I/O, schema adapters, canonical metrics, evidence formatting, runtime logging, manifest inspection, evaluator, and smoke/summary utilities.",
        "- `configs/fixed_pool/published_baseline_adaptations.yaml`: frozen path/protocol/config draft.",
        "- `manifest/fixed_pool_manifest.json`: content hashes, schemas, counts, and retrieval distributions.",
        "- `validation/`: per-method JSON/CSV, paired bootstrap CI, run log, and legacy reproduction report.",
        "- `reports/baseline_fidelity_audit.md`: preliminary naming and mechanism boundary audit.",
        "",
        "## Risks Before Inference",
        "",
        "1. Archive official paper/code versions and commits before using published-method names.",
        "2. Keep the frozen manifest hash and refuse inputs whose hashes drift.",
        "3. Add timestamped run directories and prompt hashes before any dry run.",
        "4. Keep gold answers out of prompts and AGR-only candidate/family/margin/update signals out of published baselines.",
        "5. Match LLM-call and token budgets when interpreting baseline comparisons.",
        "",
        "## Recommended Next Baseline",
        "",
        "Implement `Self-Refine-FP adaptation` first as an explicit feedback/critique stage followed by one refinement stage. Do not rename the existing generic FP-SR artifact. Start with a five-row HOH dry run only after prompt/version and resume safeguards are implemented.",
    ])
    (OUT / "reports/phase1_foundation_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"summary={OUT / 'reports/phase1_foundation_summary.md'} mismatches={len(mismatches)}")


if __name__ == "__main__":
    main()
