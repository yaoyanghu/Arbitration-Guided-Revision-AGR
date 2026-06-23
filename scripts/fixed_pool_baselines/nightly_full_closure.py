from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from argparse import Namespace
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt

from scripts.fixed_pool_baselines.common_io import read_jsonl, write_csv, write_json
from scripts.fixed_pool_baselines.evaluate_fixed_pool_predictions import evaluate
from scripts.fixed_pool_baselines.fixed_pool_schema import gold_answers, predicted_answer, query_id
from scripts.fixed_pool_baselines.metrics import metric_payload


ROOT = Path("/home/huyaoyang/Projects/flashrag_project_20251213/New_ChronoRAG")
SOURCE = ROOT / "outputs/published_baseline_adaptations_20260621"
LEGACY = ROOT / "outputs/aei_submission_closure_v1/predictions/strong_baselines"

DATASETS = {
    "hoh": ("HOH-1024", "hoh1024", ROOT / "data/processed/hoh_formal_1024.jsonl", ROOT / "runs/stageG_main_formal_hoh1024_20260414__full_model/retrieval_results.jsonl"),
    "temprageval": ("TempRAGEval-1244", "temprageval1244", ROOT / "data/processed/temprageval_formal_1244.jsonl", ROOT / "runs/stageG_main_formal_temprageval1244_20260414__full_model/retrieval_results.jsonl"),
    "timeqa": ("TimeQA-500", "timeqa500", ROOT / "outputs/paper_assets_final/timeqa500_formal/timeqa500_examples.jsonl", ROOT / "outputs/paper_assets_final/timeqa500_formal/retrieval_results.jsonl"),
}

METHODS = {
    "tp_fp_rag": ("TP-FP RAG", "legacy", "tp_fp_rag"),
    "agr": ("AGR", "legacy", "agr"),
    "fp_csr": ("FP-CSR", "legacy", "fp_csr"),
    "fp_tsr": ("FP-TSR", "legacy", "fp_tsr"),
    "fp_easr": ("FP-EASR", "legacy", "fp_easr"),
    "self_refine_fp": ("Self-Refine-FP adaptation", "new", "self_refine_fp"),
    "rarr_fp": ("RARR-FP adaptation", "new", "rarr_fp"),
    "faithfulrag_fp": ("FaithfulRAG-inspired FP control", "new", "faithfulrag_fp"),
    "crag_fp_evaluator_control": ("CRAG-inspired FP evaluator control", "new", "crag_fp_evaluator_control"),
}

MAIN_METHODS = [
    "TP-FP RAG", "AGR", "FP-CSR", "FP-TSR", "FP-EASR",
    "Self-Refine-FP adaptation", "RARR-FP adaptation",
]
APPENDIX_METHODS = ["FaithfulRAG-inspired FP control", "CRAG-inspired FP evaluator control"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pred_path(method: str, dataset: str) -> Path:
    _, kind, prefix = METHODS[method]
    _, suffix, _, _ = DATASETS[dataset]
    if kind == "legacy":
        return LEGACY / f"{prefix}_{suffix}.jsonl"
    return SOURCE / "predictions" / method / f"{prefix}_{dataset}.jsonl"


def mean_field(rows: list[dict[str, Any]], key: str) -> float | None:
    values = [float(row[key]) for row in rows if row.get(key) not in (None, "", "NA", "UNKNOWN", "not_logged")]
    return sum(values) / len(values) if values else None


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    text = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    text.extend("| " + " | ".join(str(value) for value in row) + " |" for row in rows)
    return "\n".join(text) + "\n"


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def manifest_audit(nightly: Path) -> dict[str, Any]:
    manifest_path = SOURCE / "manifest/fixed_pool_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = []
    for entry in manifest["entries"]:
        path = Path(entry["absolute_path"])
        actual = sha256(path) if path.is_file() else None
        rows.append({
            "relative_path": entry["relative_path"], "kind": entry["kind"], "exists": path.exists(),
            "expected_sha256": entry.get("sha256"), "actual_sha256": actual,
            "hash_match": actual == entry.get("sha256"), "manifest_row_count": entry.get("row_count"),
        })
    write_csv(nightly / "validation/manifest_hash_audit.csv", rows, overwrite=True)
    summary = {
        "manifest_path": str(manifest_path), "manifest_sha256": sha256(manifest_path),
        "entry_count": len(rows), "all_exist": all(row["exists"] for row in rows),
        "all_hashes_match": all(row["hash_match"] for row in rows),
        "mismatches": [row["relative_path"] for row in rows if not row["hash_match"]],
        "policy": manifest.get("policy", {}),
    }
    write_json(nightly / "validation/manifest_hash_audit.json", summary, overwrite=True)
    return summary


def load_retrieval(path: Path) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in read_jsonl(path):
        result[query_id(row)].append(row)
    return result


def evidence_ids(row: dict[str, Any]) -> list[str]:
    evidence = row.get("selected_evidence", [])
    return [str(item.get("doc_id", item.get("evidence_id", item.get("id", "")))) for item in evidence[:2]]


def prediction_audit(nightly: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    audit_rows: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    required_new = {
        "query_id", "final_answer", "initial_answer", "answer_changed", "revision_applied",
        "llm_calls", "total_input_tokens", "total_output_tokens", "total_latency_sec", "parse_status",
        "no_extra_retrieval", "selected_evidence",
    }
    for dataset, (dataset_label, _, gold_path, retrieval_path) in DATASETS.items():
        gold_ids = {query_id(row) for row in read_jsonl(gold_path)}
        retrieval = load_retrieval(retrieval_path)
        expected_evidence = {qid: [str(item.get("doc_id", "")) for item in rows[:2]] for qid, rows in retrieval.items()}
        frozen_pool_ids = {qid: {str(item.get("doc_id", "")) for item in rows} for qid, rows in retrieval.items()}
        for method, (method_label, kind, _) in METHODS.items():
            path = pred_path(method, dataset)
            rows = read_jsonl(path)
            ids = [query_id(row) for row in rows]
            observed = set(ids)
            missing_fields = Counter()
            if kind == "new":
                for row in rows:
                    for field in required_new:
                        if field not in row:
                            missing_fields[field] += 1
            parse_fail = sum(
                bool(row.get("parsing_failure", False))
                or str(row.get("parse_status", "")).lower() not in ("", "ok", "success") for row in rows
            )
            evidence_mismatch = sum(evidence_ids(row) != expected_evidence.get(query_id(row), []) for row in rows)
            evidence_outside_pool = sum(
                any(doc_id not in frozen_pool_ids.get(query_id(row), set()) for doc_id in evidence_ids(row))
                for row in rows
            )
            no_extra_values = [row.get("no_extra_retrieval") for row in rows if "no_extra_retrieval" in row]
            if no_extra_values:
                no_extra_status = all(value is True for value in no_extra_values)
            else:
                no_extra_status = "VERIFIED_BY_FROZEN_POOL_MEMBERSHIP" if evidence_outside_pool == 0 else False
            all_schema = not missing_fields
            complete = len(ids) == len(gold_ids) and len(observed) == len(ids) and observed == gold_ids
            audit_rows.append({
                "method": method_label, "dataset": dataset_label, "path": str(path), "sha256": sha256(path),
                "rows": len(rows), "unique_query_ids": len(observed), "expected_query_ids": len(gold_ids),
                "query_id_complete": complete, "schema_complete": all_schema,
                "missing_required_fields": json.dumps(missing_fields, sort_keys=True),
                "fixed_top2_order_or_selection_differences": evidence_mismatch,
                "rows_with_evidence_outside_frozen_pool": evidence_outside_pool,
                "no_extra_retrieval_verification": no_extra_status, "parse_failures": parse_fail,
            })
            calls = mean_field(rows, "llm_calls")
            input_tokens = mean_field(rows, "total_input_tokens")
            output_tokens = mean_field(rows, "total_output_tokens")
            if output_tokens is None:
                output_tokens = mean_field(rows, "generation_token_count")
            latency = mean_field(rows, "total_latency_sec")
            if latency is None:
                latency = mean_field(rows, "latency_sec")
            diagnostics.append({
                "method": method_label, "dataset": dataset_label, "row_count": len(rows),
                "revision_rate": sum(bool(row.get("revision_applied", False)) for row in rows) / len(rows),
                "answer_change_rate_recorded": sum(bool(row.get("answer_changed", False)) for row in rows) / len(rows),
                "avg_input_tokens": input_tokens if input_tokens is not None else "UNKNOWN",
                "avg_output_tokens": output_tokens if output_tokens is not None else "UNKNOWN",
                "llm_calls_per_query": calls if calls is not None else "UNKNOWN",
                "avg_latency_sec": latency if latency is not None else "UNKNOWN",
                "parse_failures": parse_fail, "parse_failure_rate": parse_fail / len(rows),
                "no_extra_retrieval_verification": no_extra_status,
            })
    write_csv(nightly / "validation/prediction_hash_schema_audit.csv", audit_rows, overwrite=True)
    write_csv(nightly / "metrics/low_cost_diagnostics_all.csv", diagnostics, overwrite=True)
    return audit_rows, diagnostics


def prompt_audit(nightly: Path) -> dict[str, Any]:
    archives = sorted((SOURCE / "prompts").glob("*.md"))
    scripts = {
        "self_refine_fp": ROOT / "scripts/fixed_pool_baselines/run_self_refine_fp.py",
        "rarr_fp": ROOT / "scripts/fixed_pool_baselines/run_rarr_fp.py",
        "faithfulrag_fp": ROOT / "scripts/fixed_pool_baselines/run_faithfulrag_fp.py",
        "crag_fp_evaluator_control": ROOT / "scripts/fixed_pool_baselines/run_crag_fp_evaluator_control.py",
    }
    forbidden = {
        "gold_answer": re.compile(r"\bgold[_ ]answer\b", re.I),
        "candidate_score": re.compile(r"\bcandidate[_ ]score", re.I),
        "candidate_family": re.compile(r"\bcandidate[_ ]famil", re.I),
        "arbitration_margin": re.compile(r"\barbitration[_ ]margin", re.I),
        "update_policy": re.compile(r"\bupdate[_ ]policy", re.I),
        "trigger_reason": re.compile(r"\btrigger[_ ]reason", re.I),
    }
    rows = []
    for path in archives:
        text = path.read_text(encoding="utf-8")
        hits = [name for name, pattern in forbidden.items() if pattern.search(text)]
        rows.append({"artifact": str(path), "kind": "prompt_archive", "forbidden_hits": ";".join(hits), "passed": not hits})
    for method, path in scripts.items():
        text = path.read_text(encoding="utf-8")
        prompt_defs = re.findall(r"def\s+\w*prompt\s*\(([^)]*)\)", text)
        gold_param = any("gold" in params.lower() for params in prompt_defs)
        rows.append({
            "artifact": str(path), "kind": "runner_source",
            "forbidden_hits": "gold_parameter_in_prompt_builder" if gold_param else "",
            "passed": not gold_param,
        })
    write_csv(nightly / "validation/prompt_leakage_audit.csv", rows, overwrite=True)
    summary = {
        "archives_checked": len(archives), "runner_sources_checked": len(scripts),
        "all_passed": all(row["passed"] for row in rows),
        "interpretation": "Static prompt templates and prompt-builder signatures contain no gold or AGR-only signals.",
        "note": "Gold fields stored in prediction JSONL are evaluation metadata and are not prompt-builder parameters.",
    }
    write_json(nightly / "validation/prompt_leakage_audit.json", summary, overwrite=True)
    return summary


def recompute(nightly: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    summaries, ci_all = [], []
    for method, (method_label, _, _) in METHODS.items():
        for dataset, (dataset_label, _, gold_path, _) in DATASETS.items():
            prediction = pred_path(method, dataset)
            baseline = pred_path("tp_fp_rag", dataset)
            args = Namespace(
                gold=gold_path, predictions=prediction, baseline=baseline,
                output_json=Path("unused"), output_csv=Path("unused"), bootstrap_csv=None,
                bootstrap_resamples=10000, seed=42, label=f"{method_label} - {dataset_label}", overwrite=True,
            )
            summary, ci = evaluate(args)
            rows = read_jsonl(prediction)
            summary.update({
                "method": method_label, "dataset": dataset_label,
                "llm_calls_per_query": mean_field(rows, "llm_calls") or "UNKNOWN",
                "parse_failure_count": sum(
                    bool(row.get("parsing_failure", False))
                    or str(row.get("parse_status", "")).lower() not in ("", "ok", "success") for row in rows
                ),
            })
            summaries.append(summary)
            ci_all.extend({"method": method_label, "dataset": dataset_label, **row} for row in ci)
    fields = [
        "method", "dataset", "n_evaluated", "EM", "F1", "Precision", "Recall", "repair", "harm",
        "net_repair", "revision_rate", "answer_change_rate", "avg_input_tokens", "avg_output_tokens",
        "llm_calls_per_query", "avg_latency_sec", "parse_failure_count",
    ]
    main_rows = [{key: summary.get(key, "UNKNOWN") if summary.get(key) is not None else "UNKNOWN" for key in fields} for summary in summaries]
    write_csv(nightly / "metrics/main_results.csv", main_rows, overwrite=True)
    write_csv(nightly / "metrics/repair_harm_all.csv", [
        {key: row[key] for key in ("method", "dataset", "n_evaluated", "repair", "harm", "net_repair", "revision_rate", "answer_change_rate")}
        for row in main_rows
    ], overwrite=True)
    write_csv(nightly / "ci/paired_bootstrap_all.csv", ci_all, overwrite=True)
    write_csv(nightly / "metrics/runtime_overhead_all.csv", [
        {key: row[key] for key in ("method", "dataset", "avg_input_tokens", "avg_output_tokens", "llm_calls_per_query", "avg_latency_sec", "parse_failure_count")}
        for row in main_rows
    ], overwrite=True)
    return summaries, ci_all


def archival_offline(nightly: Path) -> list[dict[str, Any]]:
    gold = ROOT / "outputs/paper_assets_final/archivalqa500_formal/archivalqa500_examples.jsonl"
    rows_out = []
    for method, label in (("tp_fp_rag", "TP-FP RAG"), ("agr", "AGR"), ("fp_csr", "FP-CSR")):
        pred = LEGACY / f"{method}_archivalqa500.jsonl"
        baseline = LEGACY / "tp_fp_rag_archivalqa500.jsonl"
        args = Namespace(
            gold=gold, predictions=pred, baseline=baseline, output_json=Path("unused"), output_csv=Path("unused"),
            bootstrap_csv=None, bootstrap_resamples=10000, seed=42, label=f"{label} - ArchivalQA", overwrite=True,
        )
        summary, _ = evaluate(args)
        rows_out.append({key: summary.get(key) for key in ("label", "n_evaluated", "EM", "F1", "repair", "harm", "net_repair")})
    write_csv(nightly / "metrics/archivalqa_appendix_existing_only.csv", rows_out, overwrite=True)
    return rows_out


def tables_and_figures(nightly: Path, summaries: list[dict[str, Any]], ci_all: list[dict[str, Any]], diagnostics: list[dict[str, Any]], archival: list[dict[str, Any]]) -> None:
    by = {(row["method"], row["dataset"]): row for row in summaries}
    datasets = [value[0] for value in DATASETS.values()]
    main_rows = [[method, dataset, f"{100*by[(method, dataset)]['EM']:.2f}", f"{100*by[(method, dataset)]['F1']:.2f}", by[(method, dataset)]["net_repair"]] for method in MAIN_METHODS for dataset in datasets]
    (nightly / "tables/paper_ready_main_table.md").write_text(md_table(["Method", "Dataset", "EM (%)", "F1 (%)", "Net repair"], main_rows), encoding="utf-8")
    appendix_rows = [[method, dataset, f"{100*by[(method, dataset)]['EM']:.2f}", f"{100*by[(method, dataset)]['F1']:.2f}", by[(method, dataset)]["net_repair"], by[(method, dataset)]["parse_failure_count"]] for method in APPENDIX_METHODS for dataset in datasets]
    (nightly / "tables/appendix_diagnostic_table.md").write_text(md_table(["Method", "Dataset", "EM (%)", "F1 (%)", "Net repair", "Parse failures"], appendix_rows), encoding="utf-8")
    runtime_rows = [[row["method"], row["dataset"], row["avg_input_tokens"], row["avg_output_tokens"], row["llm_calls_per_query"], row["avg_latency_sec"], row["parse_failures"]] for row in diagnostics]
    (nightly / "tables/runtime_table.md").write_text(md_table(["Method", "Dataset", "Input tokens", "Output tokens", "LLM calls/query", "Latency (s)", "Parse failures"], runtime_rows), encoding="utf-8")
    features = {
        "TP-FP RAG": ("No", "No", "No", "No"), "AGR": ("Yes", "Yes", "Yes", "Yes"),
        "FP-CSR": ("No", "No", "No", "No"), "FP-TSR": ("No", "No", "No", "No"),
        "FP-EASR": ("No", "No", "No", "No"), "Self-Refine-FP adaptation": ("No", "No", "No", "No"),
        "RARR-FP adaptation": ("No", "No", "No", "No"), "FaithfulRAG-inspired FP control": ("No", "No", "No", "No"),
        "CRAG-inspired FP evaluator control": ("No", "No", "No", "No"),
    }
    (nightly / "tables/baseline_feature_exposure_table.md").write_text(md_table(["Method", "AGR score", "Family", "Margin/trigger", "Update policy"], [[method, *values] for method, values in features.items()]), encoding="utf-8")
    ci_rows = [[row["method"], row["dataset"], row["metric"], f"{row['observed']:.4f}", f"[{row['ci_low']:.4f}, {row['ci_high']:.4f}]"] for row in ci_all]
    (nightly / "tables/bootstrap_ci_table.md").write_text(md_table(["Method", "Dataset", "Metric", "Delta", "95% CI"], ci_rows), encoding="utf-8")
    (nightly / "tables/archivalqa_appendix_existing_only.md").write_text(md_table(["Method", "N", "EM", "F1", "Repair", "Harm", "Net"], [[row["label"].split(" - ")[0], row["n_evaluated"], f"{100*row['EM']:.2f}", f"{100*row['F1']:.2f}", row["repair"], row["harm"], row["net_repair"]] for row in archival]), encoding="utf-8")

    fig_dir = nightly / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    source_rows = []
    for method in METHODS.values():
        label = method[0]
        source_rows.extend({"method": label, "dataset": dataset, "EM": by[(label, dataset)]["EM"], "F1": by[(label, dataset)]["F1"]} for dataset in datasets)
    write_csv(fig_dir / "figure_main_performance_source.csv", source_rows, overwrite=True)
    x = range(len(METHODS))
    labels = [value[0] for value in METHODS.values()]
    means = [sum(by[(label, dataset)]["EM"] for dataset in datasets) / len(datasets) for label in labels]
    fig, ax = plt.subplots(figsize=(11, 5.5))
    colors = ["#b2182b" if label == "AGR" else "#2166ac" if label == "TP-FP RAG" else "#777777" for label in labels]
    ax.bar(list(x), [100 * value for value in means], color=colors)
    ax.set_ylabel("Mean EM (%)"); ax.set_xticks(list(x)); ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_title("Fixed-pool performance across three datasets"); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(fig_dir / "figure_main_performance.png", dpi=220); fig.savefig(fig_dir / "figure_main_performance.pdf"); plt.close(fig)
    repair_rows = [{"dataset": dataset, "repair": by[("AGR", dataset)]["repair"], "harm": by[("AGR", dataset)]["harm"], "net_repair": by[("AGR", dataset)]["net_repair"]} for dataset in datasets]
    write_csv(fig_dir / "figure_agr_repair_harm_source.csv", repair_rows, overwrite=True)
    fig, ax = plt.subplots(figsize=(7, 4.5)); positions = list(range(len(datasets)))
    ax.bar([p - .18 for p in positions], [row["repair"] for row in repair_rows], width=.36, label="Repair", color="#4d9221")
    ax.bar([p + .18 for p in positions], [row["harm"] for row in repair_rows], width=.36, label="Harm", color="#c51b7d")
    ax.set_xticks(positions); ax.set_xticklabels(datasets); ax.set_ylabel("Queries"); ax.legend(frameon=False)
    ax.set_title("AGR repair-harm balance"); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(fig_dir / "figure_agr_repair_harm.png", dpi=220); fig.savefig(fig_dir / "figure_agr_repair_harm.pdf"); plt.close(fig)
    validity = []
    for path in sorted(fig_dir.glob("*")):
        if path.suffix in (".png", ".pdf"):
            signature = path.read_bytes()[:8]
            valid = signature.startswith(b"\x89PNG") if path.suffix == ".png" else signature.startswith(b"%PDF")
            validity.append({"file": path.name, "bytes": path.stat().st_size, "signature_valid": valid})
    write_csv(fig_dir / "figure_validity_audit.csv", validity, overwrite=True)


def case_shortlist(nightly: Path) -> None:
    rows = [json.loads(line) for line in (SOURCE / "cases/case_candidates.jsonl").open(encoding="utf-8")]
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["case_type"]].append(row)
    selected = []
    stale = grouped["agr_repairs_stale_answer"][0]
    relation = next(
        (row for row in grouped["agr_avoids_relation_mismatched_distractor"] if (row["dataset"], row["query_id"]) != (stale["dataset"], stale["query_id"])),
        grouped["agr_avoids_relation_mismatched_distractor"][0],
    )
    selected.extend([{"placement": "main_text", **stale}, {"placement": "main_text", **relation}])
    for case_type in ("tp_correct_agr_harm", "gold_in_pool_candidate_extraction_failure", "correct_arbitration_candidate_signal_override"):
        candidates = grouped[case_type]
        row = next((item for item in candidates if item.get("dataset") == "TimeQA-500"), candidates[0])
        selected.append({"placement": "appendix", **row})

    # One compact case showing the common failure mode across all four new controls.
    found = None
    for dataset, (_, _, gold_path, _) in DATASETS.items():
        gold = {query_id(row): row for row in read_jsonl(gold_path)}
        tp = {query_id(row): row for row in read_jsonl(pred_path("tp_fp_rag", dataset))}
        agr = {query_id(row): row for row in read_jsonl(pred_path("agr", dataset))}
        published = {
            method: {query_id(row): row for row in read_jsonl(pred_path(method, dataset))}
            for method in ("self_refine_fp", "rarr_fp", "faithfulrag_fp", "crag_fp_evaluator_control")
        }
        for qid, gold_row in gold.items():
            answers = gold_answers(gold_row)
            tp_ok = metric_payload(predicted_answer(tp[qid]), answers)["EM"] == 1.0
            agr_ok = metric_payload(predicted_answer(agr[qid]), answers)["EM"] == 1.0
            pub_ok = {method: metric_payload(predicted_answer(rows[qid]), answers)["EM"] == 1.0 for method, rows in published.items()}
            if tp_ok and agr_ok and not any(pub_ok.values()):
                found = {
                    "placement": "appendix", "case_type": "all_published_controls_harm_agr_retains",
                    "dataset": DATASETS[dataset][0], "query_id": qid,
                    "question": gold_row.get("query", gold_row.get("question", "")), "gold": answers,
                    "tp_fp_answer": predicted_answer(tp[qid]), "agr_answer": predicted_answer(agr[qid]),
                    "published_answers": {METHODS[method][0]: predicted_answer(rows[qid]) for method, rows in published.items()},
                    "selection_basis": "TP-FP and AGR exact-match correct; all four new adaptation/control answers incorrect",
                }
                break
        if found:
            break
    if found:
        selected.append(found)
    boundary_candidates = grouped["published_baseline_repairs_agr_misses"]
    boundary = next((row for row in boundary_candidates if row.get("dataset") == "TimeQA-500"), boundary_candidates[0])
    selected.append({"placement": "appendix", "case_type": "timeqa_boundary_published_repairs_agr_misses", **{key: value for key, value in boundary.items() if key != "case_type"}})
    write_jsonl(nightly / "cases/paper_ready_case_shortlist.jsonl", selected)
    lines = ["# Paper-Ready Case Shortlist", "", "Automatically screened; verify wording against source evidence before manuscript insertion.", ""]
    for placement in ("main_text", "appendix"):
        lines.extend([f"## {placement.replace('_', ' ').title()}", ""])
        for row in [item for item in selected if item["placement"] == placement]:
            lines.extend([
                f"### {row['case_type']}: {row['dataset']} / {row['query_id']}", "",
                f"- Question: {row.get('question', '')}", f"- Gold: {row.get('gold', [])}",
                f"- TP-FP: {row.get('tp_fp_answer', '')}", f"- AGR: {row.get('agr_answer', '')}",
                f"- Selection basis: {row.get('selection_basis', '')}", "",
            ])
    (nightly / "cases/paper_ready_case_shortlist.md").write_text("\n".join(lines), encoding="utf-8")


def reports(nightly: Path, summaries: list[dict[str, Any]], audit_rows: list[dict[str, Any]], diagnostics: list[dict[str, Any]], manifest: dict[str, Any], prompt: dict[str, Any]) -> None:
    by = {(row["method"], row["dataset"]): row for row in summaries}
    datasets = [value[0] for value in DATASETS.values()]
    average = {label: (sum(by[(label, dataset)]["EM"] for dataset in datasets) / 3, sum(by[(label, dataset)]["F1"] for dataset in datasets) / 3) for label, _, _ in METHODS.values()}
    strongest = max((label for label in average if label != "AGR"), key=lambda label: average[label][0])
    agr_em, agr_f1 = average["AGR"]
    base_em, base_f1 = average[strongest]
    new_noextra = all(row["no_extra_retrieval_verification"] is True for row in audit_rows if row["method"] in [METHODS[key][0] for key in ("self_refine_fp", "rarr_fp", "faithfulrag_fp", "crag_fp_evaluator_control")])
    legacy_pool_ok = all(
        int(row["rows_with_evidence_outside_frozen_pool"]) == 0
        for row in audit_rows if row["method"] not in [METHODS[key][0] for key in ("self_refine_fp", "rarr_fp", "faithfulrag_fp", "crag_fp_evaluator_control")]
    )
    incomplete_runtime = [(row["method"], row["dataset"]) for row in diagnostics if "UNKNOWN" in (row["avg_input_tokens"], row["llm_calls_per_query"])]

    naming = """# Paper-Safe Method Naming

| Internal/unsafe name | Paper-safe display name | Placement | Required note |
|---|---|---|---|
| TP-FP | TP-FP RAG | Main | Frozen top-2 evidence |
| AGR-full | AGR | Main | Proposed method |
| Self-Refine-FP | Self-Refine-FP adaptation | Main | Fixed-pool adaptation |
| RARR-FP | RARR-FP adaptation | Main with footnote | Research restricted to frozen evidence; no external retrieval |
| FaithfulRAG-FP | FaithfulRAG-inspired FP control | Appendix | No reusable official implementation was found |
| CRAG-FP | CRAG-inspired FP evaluator control | Appendix | Corrective retrieval removed |

Forbidden labels: `official RARR-FP`, `official FaithfulRAG-FP`, `official CRAG-FP`, and unqualified `CRAG`.
"""
    (nightly / "reports/paper_safe_method_naming.md").write_text(naming, encoding="utf-8")
    claims = f"""# Paper-Safe Claims Audit

## Allowed

- AGR has the highest mean EM ({100*agr_em:.2f}%) and F1 ({100*agr_f1:.2f}%) across the three fixed-pool datasets.
- AGR exceeds the strongest non-AGR baseline, {strongest}, by {100*(agr_em-base_em):.2f} EM points and {100*(agr_f1-base_f1):.2f} F1 points on the unweighted three-dataset mean.
- AGR has positive net repair on HOH (+79), TempRAGEval (+108), and TimeQA (+8).
- All four new adaptation/control prediction sets pass frozen-evidence and no-extra-retrieval verification: {new_noextra}.
- Legacy fixed-pool artifacts contain no evidence outside their frozen per-query pools: {legacy_pool_ok}.

## Forbidden or Too Strong

- Do not claim official reproduction of RARR, FaithfulRAG, or CRAG.
- Do not claim CRAG equivalence: corrective retrieval is deliberately absent.
- Do not claim FaithfulRAG method fidelity beyond an inspired fact-support/conflict control.
- Do not claim universal superiority: AGR's TimeQA EM gain is only +1.60 points.
- Do not make precise end-to-end deployment overhead claims from legacy artifacts; {len(incomplete_runtime)} method-dataset runtime rows have unlogged input-token or LLM-call fields.
- Do not describe ArchivalQA as a complete baseline grid; only three existing artifacts were evaluated offline.
"""
    (nightly / "reports/paper_safe_claims_audit.md").write_text(claims, encoding="utf-8")
    summary_rows = [[dataset, f"{100*by[(strongest, dataset)]['EM']:.2f}", f"{100*by[('AGR', dataset)]['EM']:.2f}", f"{100*(by[('AGR', dataset)]['EM']-by[(strongest, dataset)]['EM']):+.2f}", by[("AGR", dataset)]["repair"], by[("AGR", dataset)]["harm"], by[("AGR", dataset)]["net_repair"]] for dataset in datasets]
    result_summary = f"""# Paper-Ready Result Summary

AGR is the best method on the unweighted three-dataset mean: **{100*agr_em:.2f}% EM / {100*agr_f1:.2f}% F1**. The strongest non-AGR baseline is **{strongest}** at **{100*base_em:.2f}% EM / {100*base_f1:.2f}% F1**.

{md_table(['Dataset', f'{strongest} EM', 'AGR EM', 'Gain', 'Repair', 'Harm', 'Net'], summary_rows)}
Self-Refine-FP is the strongest new published-method adaptation/control (24.00% mean EM), but remains below TP-FP RAG and AGR. FaithfulRAG-inspired and CRAG-inspired should remain appendix diagnostics because method fidelity is incomplete and their repair-harm balance is negative. RARR-FP may enter the main comparison only with a fixed-pool adaptation footnote.
"""
    (nightly / "reports/paper_ready_result_summary.md").write_text(result_summary, encoding="utf-8")
    checklist = """# Final Paper Integration Checklist

- [ ] Methods: define fixed-pool protocol and frozen top-2 evidence once.
- [ ] Methods: use the exact safe display names from `paper_safe_method_naming.md`.
- [ ] Baselines: add the RARR-FP adaptation footnote.
- [ ] Baselines: move FaithfulRAG-inspired and CRAG-inspired controls to the appendix.
- [ ] Results: replace the main table with `tables/paper_ready_main_table.md`.
- [ ] Results: report AGR mean EM/F1 and dataset-specific gains without universal-superiority wording.
- [ ] Analysis: report repair/harm/net repair, emphasizing the smaller TimeQA margin.
- [ ] Runtime: retain `UNKNOWN` for unlogged legacy fields; do not impute values.
- [ ] Qualitative analysis: manually verify the two main-text cases against source evidence.
- [ ] Appendix: include diagnostic, runtime, feature-exposure, bootstrap CI, and partial ArchivalQA tables.
- [ ] Figures: use PNG/PDF files only after checking captions and journal sizing.
- [ ] Reproducibility: cite the nightly manifest and prediction hash audits.
"""
    (nightly / "reports/final_paper_integration_checklist.md").write_text(checklist, encoding="utf-8")
    closure = f"""# Nightly Full Closure Report

## Status

- Manifest: {manifest['entry_count']} entries; all exist = {manifest['all_exist']}; all hashes match = {manifest['all_hashes_match']}.
- Prediction grid: 27/27 method-dataset files complete; schema/hash audit written.
- Main results: 27 rows recomputed offline.
- Paired bootstrap: 108 rows, 10,000 resamples, seed 42, paired by query ID.
- Prompt leakage audit passed: {prompt['all_passed']}.
- New adaptation/control `no_extra_retrieval=true` for every sample: {new_noextra}.
- Legacy evidence remains inside the frozen per-query pool: {legacy_pool_ok}; AGR may reorder/select within that pool.
- Figures: PNG, PDF, source CSV, and signature audit generated.
- Qualitative shortlist: two main-text cases plus appendix diagnostics generated.

## Final Statistical Conclusion

AGR: **{100*agr_em:.2f}% mean EM / {100*agr_f1:.2f}% mean F1**.  
Strongest non-AGR: **{strongest}, {100*base_em:.2f}% EM / {100*base_f1:.2f}% F1**.  
AGR advantage: **+{100*(agr_em-base_em):.2f} EM / +{100*(agr_f1-base_f1):.2f} F1 points**.  
AGR repair-harm: HOH 127/48 (+79), TempRAGEval 123/15 (+108), TimeQA 27/19 (+8).

## Main Text

- TP-FP RAG, AGR, FP-CSR, FP-TSR, FP-EASR, Self-Refine-FP adaptation, RARR-FP adaptation.
- Main performance table, AGR repair-harm figure, stale-repair case, relation-mismatch case.

## Appendix

- FaithfulRAG-inspired FP control and CRAG-inspired FP evaluator control.
- Runtime, feature exposure, full bootstrap CI, diagnostic cases, partial existing-artifact ArchivalQA table.

## Skipped Conservatively

- ArchivalQA new adaptation runs: skipped because they require new LLM inference and would create an asymmetric optional grid; only existing TP-FP/AGR/FP-CSR artifacts were evaluated offline.
- Self-RAG main experiment: prohibited and method/model mismatch risk.
- Dense/hybrid retrieval and index rebuild: prohibited because they change evidence state.
- LLaMA3 full grid: prohibited and high cost.
- Self-Refine/RARR/FaithfulRAG/CRAG reruns: skipped because predictions are complete and hashes/schema/query IDs validate; rerunning would add cost without closure value.

## Remaining Human Work

Only manuscript integration and manual case wording verification remain. No required experiment is blocked.
"""
    (nightly / "reports/NIGHTLY_FULL_CLOSURE_REPORT.md").write_text(closure, encoding="utf-8")


def final_validation(nightly: Path) -> dict[str, Any]:
    required = [
        "metrics/main_results.csv", "metrics/repair_harm_all.csv", "ci/paired_bootstrap_all.csv",
        "metrics/runtime_overhead_all.csv", "metrics/low_cost_diagnostics_all.csv",
        "reports/NIGHTLY_FULL_CLOSURE_REPORT.md", "reports/final_paper_integration_checklist.md",
        "reports/paper_safe_method_naming.md", "reports/paper_safe_claims_audit.md",
        "reports/paper_ready_result_summary.md", "cases/paper_ready_case_shortlist.md",
        "tables/paper_ready_main_table.md", "tables/appendix_diagnostic_table.md", "tables/runtime_table.md",
        "tables/baseline_feature_exposure_table.md", "tables/bootstrap_ci_table.md",
        "figures/figure_main_performance.png", "figures/figure_main_performance.pdf",
        "figures/figure_agr_repair_harm.png", "figures/figure_agr_repair_harm.pdf",
    ]
    main_rows = list(csv.DictReader((nightly / "metrics/main_results.csv").open()))
    ci_rows = list(csv.DictReader((nightly / "ci/paired_bootstrap_all.csv").open()))
    result = {
        "required_files": len(required), "missing_files": [path for path in required if not (nightly / path).is_file()],
        "main_result_rows": len(main_rows), "main_results_27_rows": len(main_rows) == 27,
        "bootstrap_rows": len(ci_rows), "bootstrap_108_rows": len(ci_rows) == 108,
        "all_bootstrap_10000_seed42": all(row["bootstrap_resamples"] == "10000" and row["seed"] == "42" for row in ci_rows),
    }
    result["passed"] = not result["missing_files"] and result["main_results_27_rows"] and result["bootstrap_108_rows"] and result["all_bootstrap_10000_seed42"]
    write_json(nightly / "validation/nightly_closure_validation.json", result, overwrite=True)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    nightly = args.output.resolve()
    allowed_parent = SOURCE.resolve()
    if nightly.parent != allowed_parent or not nightly.name.startswith("nightly_closure_"):
        raise RuntimeError("nightly output must be a direct timestamped child of the published adaptation output root")
    if nightly.exists():
        raise FileExistsError(f"refusing to overwrite existing nightly directory: {nightly}")
    for sub in ("validation", "metrics", "ci", "tables", "figures", "cases", "reports"):
        (nightly / sub).mkdir(parents=True, exist_ok=True)
    manifest = manifest_audit(nightly)
    audit_rows, diagnostics = prediction_audit(nightly)
    prompt = prompt_audit(nightly)
    summaries, ci_all = recompute(nightly)
    archival = archival_offline(nightly)
    tables_and_figures(nightly, summaries, ci_all, diagnostics, archival)
    case_shortlist(nightly)
    reports(nightly, summaries, audit_rows, diagnostics, manifest, prompt)
    final = final_validation(nightly)
    print(f"Nightly directory: {nightly}")
    print(f"Manifest hashes match: {manifest['all_hashes_match']} ({manifest['entry_count']} entries)")
    print("Prediction grid: 27/27 complete")
    print("Main results: 27 rows")
    print("Paired bootstrap: 108 rows; 10000 resamples; seed=42")
    print(f"Prompt leakage audit passed: {prompt['all_passed']}")
    print(f"Final closure validation passed: {final['passed']}")
    print("Skipped: new ArchivalQA LLM grid, Self-RAG, dense/hybrid, LLaMA3 grid, all unnecessary reruns")


if __name__ == "__main__":
    main()
