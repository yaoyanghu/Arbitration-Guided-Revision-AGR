from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path("/home/huyaoyang/Projects/flashrag_project_20251213/New_ChronoRAG")
ASSET = ROOT / "outputs/paper_assets_v4_experiment_upgrade/20260414_220953"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def run_group(config: str, run_group: str, variants: list[str]) -> None:
    cmd = [
        "python",
        "-u",
        "src/eval/run_mainline_baselines.py",
        "--config",
        config,
        "--run-group",
        run_group,
        "--variants",
        *variants,
    ]
    p = subprocess.run(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stdout)


def compute_tfa_cfa(preds: list[dict[str, Any]]) -> tuple[float | None, float | None]:
    # fallback to existing per-example metrics only; strict TFA/CFA unavailable from this route runner
    # keep N/A as required by user when not reliably computable from this script.
    return None, None


def collect_rows(run_group: str, dataset: str) -> list[dict[str, Any]]:
    rows = []
    for item in read_jsonl(ROOT / "runs" / run_group / "summary.jsonl"):
        run_dir = Path(item["run_dir"])
        m = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
        preds = read_jsonl(run_dir / "predictions.jsonl")
        tfa, cfa = compute_tfa_cfa(preds)
        rows.append(
            {
                "dataset": dataset,
                "method": item["variant"],
                "exact_match": item["exact_match"],
                "token_f1": item["token_f1"],
                "citation_title_recall": item["citation_title_recall"],
                "tfa": tfa,
                "cfa": cfa,
                "arbitration_latency_ms_per_query": "N/A",
                "run_dir": str(run_dir),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "dataset",
        "method",
        "exact_match",
        "token_f1",
        "citation_title_recall",
        "tfa",
        "cfa",
        "arbitration_latency_ms_per_query",
        "run_dir",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def pick(rows: list[dict[str, Any]], dataset: str, method: str, metric: str) -> float:
    for r in rows:
        if r["dataset"] == dataset and r["method"] == method:
            return float(r[metric])
    raise KeyError((dataset, method, metric))


def main() -> None:
    ASSET.mkdir(parents=True, exist_ok=True)
    base_methods = ["no_conflict", "full_model", "no_hard_temporal_rules", "judge_verify_pipeline", "full_model_soft_temporal"]
    run_group("configs/conflict_aware_rag_hoh_pilot_256_linux.yaml", "stageK_routeC_hoh256", base_methods)
    run_group("configs/conflict_aware_rag_temprageval_pilot_256_linux.yaml", "stageK_routeC_temprageval256", base_methods)
    rows = collect_rows("stageK_routeC_hoh256", "hoh_pilot_256") + collect_rows("stageK_routeC_temprageval256", "temprageval_pilot_256")
    write_csv(ASSET / "soft_temporal_results.csv", rows)

    cond_a = pick(rows, "temprageval_pilot_256", "full_model_soft_temporal", "token_f1") > pick(rows, "temprageval_pilot_256", "no_conflict", "token_f1")
    cond_b = pick(rows, "hoh_pilot_256", "full_model_soft_temporal", "token_f1") >= pick(rows, "hoh_pilot_256", "full_model", "token_f1")
    cond_c = False  # TFA unavailable in this minimal runner
    cond_d = True   # latency unavailable in this minimal runner
    continue_judge = cond_a and cond_b and cond_c and cond_d

    judge_rows: list[dict[str, Any]] = []
    if continue_judge:
        run_group("configs/conflict_aware_rag_hoh_pilot_256_linux.yaml", "stageK_routeC_judge_hoh256", ["full_model_soft_temporal", "full_model_soft_temporal_judge"])
        run_group("configs/conflict_aware_rag_temprageval_pilot_256_linux.yaml", "stageK_routeC_judge_temprageval256", ["full_model_soft_temporal", "full_model_soft_temporal_judge"])
        judge_rows = collect_rows("stageK_routeC_judge_hoh256", "hoh_pilot_256") + collect_rows("stageK_routeC_judge_temprageval256", "temprageval_pilot_256")
        write_csv(ASSET / "soft_temporal_judge_results.csv", judge_rows)
        (ASSET / "SOFT_TEMPORAL_JUDGE_RESULTS.md").write_text(
            "# SOFT_TEMPORAL_JUDGE_RESULTS\n\n" + "\n".join([f"- {r['dataset']} | {r['method']} | EM={float(r['exact_match']):.4f} | F1={float(r['token_f1']):.4f}" for r in judge_rows]),
            encoding="utf-8",
        )

    (ASSET / "SOFT_TEMPORAL_PILOT_RESULTS.md").write_text(
        "# SOFT_TEMPORAL_PILOT_RESULTS\n\n"
        + f"- continue_judge: {continue_judge}\n\n"
        + "\n".join([f"- {r['dataset']} | {r['method']} | EM={float(r['exact_match']):.4f} | F1={float(r['token_f1']):.4f} | CTR={r['citation_title_recall']} | TFA={r['tfa']} | CFA={r['cfa']} | arb_latency={r['arbitration_latency_ms_per_query']}" for r in rows]),
        encoding="utf-8",
    )

    # formal criteria with available metrics
    hoh_ok = pick(rows, "hoh_pilot_256", "full_model_soft_temporal", "token_f1") >= pick(rows, "hoh_pilot_256", "full_model", "token_f1") - 0.001
    temp_ok = pick(rows, "temprageval_pilot_256", "full_model_soft_temporal", "token_f1") >= pick(rows, "temprageval_pilot_256", "no_conflict", "token_f1") + 0.003 or pick(rows, "temprageval_pilot_256", "full_model_soft_temporal", "token_f1") >= pick(rows, "temprageval_pilot_256", "judge_verify_pipeline", "token_f1") - 0.002
    promote = hoh_ok and temp_ok
    (ASSET / "SOFT_TEMPORAL_DECISION.md").write_text(
        "# SOFT_TEMPORAL_DECISION\n\n"
        + f"- continue_judge: {continue_judge}\n"
        + f"- promote_to_formal: {promote}\n\n"
        + "## Why\n"
        + f"- TempRAGEval F1 > no_conflict: {cond_a}\n"
        + f"- HOH F1 >= full_model: {cond_b}\n"
        + f"- TFA improve check: {cond_c} (N/A in this run)\n"
        + f"- latency check: {cond_d} (N/A in this run)\n"
        + f"- formal HOH condition: {hoh_ok}\n"
        + f"- formal TempRAGEval condition: {temp_ok}\n\n"
        + "## Impact on Main Narrative\n"
        + ("- If promoted: soft temporal can be considered for formal insertion.\n" if promote else "- Not promoted: Route C remains pilot evidence; mainline unchanged.\n"),
        encoding="utf-8",
    )

    print(json.dumps({"continue_judge": continue_judge, "promote_to_formal": promote, "rows": len(rows), "judge_rows": len(judge_rows)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

