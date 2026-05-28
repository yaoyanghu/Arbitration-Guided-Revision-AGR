from __future__ import annotations

import json
import re
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from src.common import ensure_dir, read_jsonl, write_json, write_jsonl
from src.eval.eval_conflict_aware_rag import exact_match, token_f1, citation_title_recall
from src.eval.run_mainline_baselines import load_config
from src.rag.answer_generation import generate_answer
from src.rag.conflict_arbitration import build_scored_candidates, select_evidence_bundle
from src.rag.contracts import QueryRecord, to_query_record
from src.retrieval.search import run_search

YEAR_RE = re.compile(r"\b(?:18|19|20|21)\d{2}\b")
NUM_RE = re.compile(r"\$[\d,]+(?:\.\d+)?|\d+(?:\.\d+)?%|\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b|\b\d+\b")
STALE_CUES = ("former", "previous", "until", "before", "earlier", "used to", "historical")
CURRENT_CUES = ("current", "latest", "most recent", "now", "as of", "updated")
TEMPORAL_INTENT_CUES = ("as of", "latest", "most recent", "before", "after")


@dataclass
class MethodResult:
    dataset: str
    method: str
    threshold: float
    exact_match: float
    token_f1: float
    citation_title_recall: float | None
    tfa: float | None
    cfa: float | None
    gate_activation_ratio: float
    judge_activation_ratio: float
    arbitration_latency_ms_per_query: float
    query_count: int
    run_dir: str


def _parse_year(value: Any) -> int | None:
    if value is None:
        return None
    m = YEAR_RE.search(str(value))
    return int(m.group(0)) if m else None


def _temporal_intent(query: str) -> bool:
    q = query.lower()
    return any(c in q for c in TEMPORAL_INTENT_CUES)


def _title_norm(title: str) -> str:
    return " ".join(str(title).strip().lower().split())


def _family_key(title: str) -> str:
    t = _title_norm(title)
    m = re.search(r"\b(e\d+|t\d+|s\d+)\b", t)
    if m:
        return m.group(1)
    tokens = t.split()
    return " ".join(tokens[:2]) if tokens else t


def _jaccard_tokens(a: str, b: str) -> float:
    ta = set(re.findall(r"[A-Za-z0-9]+", a.lower()))
    tb = set(re.findall(r"[A-Za-z0-9]+", b.lower()))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(len(ta | tb), 1)


def _value_signature(candidate: Any) -> str:
    text = f"{getattr(candidate, 'text', '')} {getattr(candidate, 'timestamp', '')}"
    m = YEAR_RE.search(text)
    if m:
        return f"year:{m.group(0)}"
    m = NUM_RE.search(text)
    if m:
        return f"num:{m.group(0)}"
    title = str(getattr(candidate, "title", "")).strip().lower()
    return f"title:{title}" if title else ""


def _has_stale_current_opposition(c1: Any, c2: Any) -> bool:
    t1 = f"{getattr(c1, 'text', '')} {getattr(c1, 'title', '')}".lower()
    t2 = f"{getattr(c2, 'text', '')} {getattr(c2, 'title', '')}".lower()
    s1 = any(k in t1 for k in STALE_CUES)
    s2 = any(k in t2 for k in STALE_CUES)
    c1f = any(k in t1 for k in CURRENT_CUES)
    c2f = any(k in t2 for k in CURRENT_CUES)
    return (s1 and c2f) or (s2 and c1f)


def _same_or_competing_family(c1: Any, c2: Any) -> bool:
    f1 = _family_key(getattr(c1, "title", ""))
    f2 = _family_key(getattr(c2, "title", ""))
    if f1 and f2 and f1 == f2:
        return True
    jac = _jaccard_tokens(str(getattr(c1, "title", "")), str(getattr(c2, "title", "")))
    return jac >= 0.5


def _gate_decision(cands: list[Any], threshold: float) -> tuple[bool, dict[str, Any]]:
    if len(cands) < 2:
        return False, {"reason": "lt2", "cond_d_count": 0}
    c1, c2 = cands[0], cands[1]
    s1 = _value_signature(c1)
    s2 = _value_signature(c2)
    cond_a = bool(s1 and s2)
    cond_b = _same_or_competing_family(c1, c2)
    cond_c = s1 != s2
    margin = float(c1.arbitration_score) - float(c2.arbitration_score)
    y1 = _parse_year(getattr(c1, "timestamp", None))
    y2 = _parse_year(getattr(c2, "timestamp", None))
    year_disp = abs(y1 - y2) if (y1 is not None and y2 is not None) else 0
    cond_d1 = margin < threshold
    cond_d2 = year_disp >= 2
    cond_d3 = max(float(getattr(c1, "conflict_score", 0.0)), float(getattr(c2, "conflict_score", 0.0))) >= 0.7
    cond_d4 = _has_stale_current_opposition(c1, c2)
    cond_d_count = sum([cond_d1, cond_d2, cond_d3, cond_d4])
    fire = cond_a and cond_b and cond_c and (cond_d_count >= 2)
    return fire, {
        "cond_a": cond_a,
        "cond_b": cond_b,
        "cond_c": cond_c,
        "cond_d_count": cond_d_count,
        "margin": margin,
        "year_dispersion": year_disp,
        "max_conflict_score": max(float(getattr(c1, "conflict_score", 0.0)), float(getattr(c2, "conflict_score", 0.0))),
        "stale_current_opposition": cond_d4,
    }


def _judge_fire(query: str, gate_on: bool, cands: list[Any], gate_meta: dict[str, Any]) -> bool:
    if not gate_on or len(cands) < 2:
        return False
    c1, c2 = cands[0], cands[1]
    if gate_meta.get("margin", 1.0) >= 0.03:
        return False
    if not _same_or_competing_family(c1, c2):
        return False
    sig_diff = _value_signature(c1) != _value_signature(c2)
    y1 = _parse_year(getattr(c1, "timestamp", None))
    y2 = _parse_year(getattr(c2, "timestamp", None))
    year_diff = (y1 is not None and y2 is not None and y1 != y2)
    if not (sig_diff or year_diff):
        return False
    return _temporal_intent(query)


def _judge_pick(query_record: QueryRecord, c1: Any, c2: Any) -> str:
    q = query_record.query.lower()
    qyear = _parse_year(query_record.query_time)
    y1 = _parse_year(getattr(c1, "timestamp", None))
    y2 = _parse_year(getattr(c2, "timestamp", None))

    if qyear is not None and (y1 is not None or y2 is not None):
        if "before" in q:
            score1 = -abs((y1 if y1 is not None else 9999) - qyear) + (0.5 if y1 is not None and y1 <= qyear else -0.5)
            score2 = -abs((y2 if y2 is not None else 9999) - qyear) + (0.5 if y2 is not None and y2 <= qyear else -0.5)
        elif "after" in q:
            score1 = -abs((y1 if y1 is not None else -9999) - qyear) + (0.5 if y1 is not None and y1 >= qyear else -0.5)
            score2 = -abs((y2 if y2 is not None else -9999) - qyear) + (0.5 if y2 is not None and y2 >= qyear else -0.5)
        elif any(k in q for k in ("as of", "latest", "most recent", "current")):
            score1 = (y1 if y1 is not None and y1 <= qyear else -10**6)
            score2 = (y2 if y2 is not None and y2 <= qyear else -10**6)
        else:
            score1 = y1 if y1 is not None else -10**6
            score2 = y2 if y2 is not None else -10**6
        return "A" if score1 >= score2 else "B"

    return "A" if float(c1.arbitration_score) >= float(c2.arbitration_score) else "B"


def _conflict_subset(scored_rows: list[dict[str, Any]], query_time: Any) -> tuple[bool, dict[str, Any]]:
    if len(scored_rows) < 2:
        return False, {"year_dispersion": 0, "max_conflict": 0.0}
    years = [_parse_year(r.get("timestamp")) for r in scored_rows]
    years = [y for y in years if y is not None]
    year_disp = (max(years) - min(years)) if len(years) >= 2 else 0
    max_conf = max(float(r.get("conflict_score", 0.0)) for r in scored_rows)
    return (year_disp >= 1) or (max_conf >= 0.6), {"year_dispersion": year_disp, "max_conflict": max_conf}


def _preferred_year(scored_rows: list[dict[str, Any]], query_time: Any) -> int | None:
    qy = _parse_year(query_time)
    years = [_parse_year(r.get("timestamp")) for r in scored_rows]
    years = [y for y in years if y is not None]
    if not years:
        return None
    if qy is not None:
        past = [y for y in years if y <= qy]
        if past:
            return max(past)
    return max(years)


def _compute_tfa_cfa(query_records: list[QueryRecord], predictions: list[dict[str, Any]], scored_rows: list[dict[str, Any]]) -> tuple[float | None, float | None]:
    pred_map = {str(p["query_id"]): p for p in predictions}
    sbq: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in scored_rows:
        sbq[str(r["query_id"])].append(r)
    t_total = t_hit = 0
    c_total = c_hit = 0
    for q in query_records:
        qid = str(q.query_id)
        p = pred_map.get(qid)
        if p is None:
            continue
        em = float(p["metrics"].get("exact_match", 0.0))
        gold_titles = {_title_norm(t) for t in q.gold_evidence_titles if str(t).strip()}
        sel = p.get("selected_evidence", [])
        sel_titles = {_title_norm(x.get("title", "")) for x in sel if str(x.get("title", "")).strip()}
        title_hit = bool(gold_titles & sel_titles)
        if _temporal_intent(q.query):
            t_total += 1
            temp_ok = False
            if sel:
                sy = _parse_year(sel[0].get("timestamp")) or _parse_year(sel[0].get("text"))
                qy = _parse_year(q.query_time)
                ql = q.query.lower()
                if qy is None:
                    temp_ok = sy is not None
                elif "before" in ql:
                    temp_ok = sy is not None and sy <= qy
                elif "after" in ql:
                    temp_ok = sy is not None and sy >= qy
                elif any(k in ql for k in ("as of", "latest", "most recent", "current")):
                    temp_ok = sy is not None and sy <= qy
                else:
                    temp_ok = sy is not None
            if em == 1.0 and title_hit and temp_ok:
                t_hit += 1
        is_conf, _ = _conflict_subset(sbq.get(qid, []), q.query_time)
        if is_conf:
            c_total += 1
            conf_ok = False
            if sel:
                sy = _parse_year(sel[0].get("timestamp"))
                py = _preferred_year(sbq.get(qid, []), q.query_time)
                if py is None:
                    conf_ok = True
                elif sy is not None:
                    conf_ok = sy == py
            if em == 1.0 and title_hit and conf_ok:
                c_hit += 1
    return (t_hit / t_total) if t_total else None, (c_hit / c_total) if c_total else None


def _resolve_rows(query_records: list[QueryRecord], retrieval_records: list[dict[str, Any]], mainline: dict[str, Any], method: str, threshold: float, base_run_group: str) -> MethodResult:
    qcount = len(query_records)
    t0 = time.perf_counter()
    scored_full = build_scored_candidates(
        query_records=query_records,
        retrieval_records=retrieval_records,
        bm25_weight=float(mainline["bm25_weight"]),
        lexical_weight=float(mainline["lexical_weight"]),
        temporal_weight=float(mainline["temporal_weight"]),
        conflict_weight=float(mainline["conflict_weight"]),
        structured_weight=float(mainline.get("structured_weight", 0.0)),
        reliability_weight=float(mainline.get("reliability_weight", 0.0)),
        learned_weight=float(mainline.get("learned_weight", 0.0)),
        learned_model=None,
        posterior_enabled=bool(mainline.get("posterior_enabled", False)),
        gate_enabled=bool(mainline.get("gate_enabled", False)),
        fixed_gamma=float(mainline.get("fixed_gamma", 0.5)),
        family_conflict_weight=float(mainline.get("family_conflict_weight", 0.7)),
        global_conflict_weight=float(mainline.get("global_conflict_weight", 0.3)),
    )
    scored_no = build_scored_candidates(
        query_records=query_records,
        retrieval_records=retrieval_records,
        bm25_weight=float(mainline["bm25_weight"]),
        lexical_weight=float(mainline["lexical_weight"]),
        temporal_weight=float(mainline["temporal_weight"]),
        conflict_weight=0.0,
        structured_weight=0.0,
        reliability_weight=0.0,
        learned_weight=0.0,
        learned_model=None,
        posterior_enabled=False,
        gate_enabled=False,
        fixed_gamma=float(mainline.get("fixed_gamma", 0.5)),
        family_conflict_weight=float(mainline.get("family_conflict_weight", 0.7)),
        global_conflict_weight=float(mainline.get("global_conflict_weight", 0.3)),
    )
    bundles_full = select_evidence_bundle(
        scored_full,
        evidence_top_k=int(mainline["evidence_top_k"]),
        enable_top_gap_filtering=bool(mainline.get("enable_top_gap_filtering", True)),
        enable_duplicate_suppression=bool(mainline.get("enable_duplicate_suppression", True)),
        top_gap_threshold=float(mainline.get("top_gap_threshold", 0.10)),
    )
    bundles_no = select_evidence_bundle(
        scored_no,
        evidence_top_k=int(mainline["evidence_top_k"]),
        enable_top_gap_filtering=bool(mainline.get("enable_top_gap_filtering", True)),
        enable_duplicate_suppression=bool(mainline.get("enable_duplicate_suppression", True)),
        top_gap_threshold=float(mainline.get("top_gap_threshold", 0.10)),
    )
    t1 = time.perf_counter()
    arb_latency_ms = (t1 - t0) * 1000.0 / max(qcount, 1)

    byq_full: dict[str, list[Any]] = defaultdict(list)
    byq_no: dict[str, list[Any]] = defaultdict(list)
    for c in scored_full:
        byq_full[str(c.query_id)].append(c)
    for c in scored_no:
        byq_no[str(c.query_id)].append(c)
    for arr in byq_full.values():
        arr.sort(key=lambda x: x.arbitration_score, reverse=True)
    for arr in byq_no.values():
        arr.sort(key=lambda x: x.arbitration_score, reverse=True)

    predictions: list[dict[str, Any]] = []
    gate_cnt = 0
    judge_cnt = 0
    run_name = f"{base_run_group}__{method}__th{threshold:.2f}".replace(".", "p")
    run_dir = ensure_dir(Path(mainline["runs_dir"]) / run_name)

    for q in query_records:
        qid = str(q.query_id)
        gate_on = False
        gate_meta: dict[str, Any] = {}
        if method in ("full_model_selective_conflict", "full_model_selective_conflict_judge"):
            gate_on, gate_meta = _gate_decision(byq_full.get(qid, []), threshold)
            if gate_on:
                gate_cnt += 1

        if method == "no_conflict":
            cands = bundles_no.get(qid, [])
            pred = generate_answer(q, cands, generation_mode="citation_aware")
        elif method == "full_model":
            cands = bundles_full.get(qid, [])
            pred = generate_answer(q, cands, generation_mode="citation_aware")
        elif method == "judge_verify_pipeline":
            cands = bundles_full.get(qid, [])
            pred = generate_answer(q, cands, generation_mode="faithfulrag_style")
        elif method == "full_model_selective_conflict":
            cands = bundles_full.get(qid, []) if gate_on else bundles_no.get(qid, [])
            pred = generate_answer(q, cands, generation_mode="citation_aware")
            pred.arbitration_trace["route_b_gate"] = {"activated": gate_on, **gate_meta}
        elif method == "full_model_selective_conflict_judge":
            cands = bundles_full.get(qid, []) if gate_on else bundles_no.get(qid, [])
            pred = generate_answer(q, cands, generation_mode="citation_aware")
            judge_on = _judge_fire(q.query, gate_on, byq_full.get(qid, []), gate_meta)
            if judge_on:
                judge_cnt += 1
                top = byq_full.get(qid, [])[:2]
                if len(top) == 2:
                    pa = generate_answer(q, [top[0]], generation_mode="citation_aware")
                    pb = generate_answer(q, [top[1]], generation_mode="citation_aware")
                    pick = _judge_pick(q, top[0], top[1])
                    chosen = pa if pick == "A" else pb
                    pred.predicted_answer = chosen.predicted_answer
                    pred.selected_evidence = chosen.selected_evidence
                    pred.arbitration_trace["route_b_judge"] = {"activated": True, "choice": pick}
            pred.arbitration_trace["route_b_gate"] = {"activated": gate_on, **gate_meta}
        else:
            raise ValueError(method)

        em = exact_match(pred.predicted_answer, q.answers)
        f1 = token_f1(pred.predicted_answer, q.answers)
        ctr = citation_title_recall(pred.selected_evidence, q.gold_evidence_titles)
        pred.metrics = {"exact_match": em, "token_f1": f1, "citation_title_recall": ctr}
        predictions.append(
            {
                "query_id": pred.query_id,
                "query": pred.query,
                "predicted_answer": pred.predicted_answer,
                "selected_evidence": pred.selected_evidence,
                "arbitration_trace": pred.arbitration_trace,
                "metrics": pred.metrics,
            }
        )

    em_avg = sum(float(p["metrics"]["exact_match"]) for p in predictions) / max(len(predictions), 1)
    f1_avg = sum(float(p["metrics"]["token_f1"]) for p in predictions) / max(len(predictions), 1)
    ctr_vals = [p["metrics"]["citation_title_recall"] for p in predictions if p["metrics"]["citation_title_recall"] is not None]
    ctr_avg = (sum(float(x) for x in ctr_vals) / len(ctr_vals)) if ctr_vals else None
    scored_used = scored_full if method != "no_conflict" else scored_no
    tfa, cfa = _compute_tfa_cfa(
        query_records,
        predictions,
        [{"query_id": c.query_id, "title": c.title, "text": c.text, "timestamp": c.timestamp, "conflict_score": c.conflict_score} for c in scored_used],
    )
    write_jsonl(run_dir / "predictions.jsonl", predictions)
    write_json(
        run_dir / "metrics.json",
        {
            "dataset": mainline["dataset_name"],
            "method": method,
            "threshold": threshold,
            "exact_match": em_avg,
            "token_f1": f1_avg,
            "citation_title_recall": ctr_avg,
            "tfa": tfa,
            "cfa": cfa,
            "gate_activation_ratio": gate_cnt / max(qcount, 1),
            "judge_activation_ratio": judge_cnt / max(qcount, 1),
            "arbitration_latency_ms_per_query": arb_latency_ms,
            "query_count": qcount,
        },
    )
    return MethodResult(
        dataset=str(mainline["dataset_name"]),
        method=method,
        threshold=threshold,
        exact_match=em_avg,
        token_f1=f1_avg,
        citation_title_recall=ctr_avg,
        tfa=tfa,
        cfa=cfa,
        gate_activation_ratio=gate_cnt / max(qcount, 1),
        judge_activation_ratio=judge_cnt / max(qcount, 1),
        arbitration_latency_ms_per_query=arb_latency_ms,
        query_count=qcount,
        run_dir=str(run_dir),
    )


def _rows_to_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    import csv
    fields = ["dataset", "method", "threshold", "exact_match", "token_f1", "citation_title_recall", "tfa", "cfa", "gate_activation_ratio", "judge_activation_ratio", "arbitration_latency_ms_per_query", "query_count", "run_dir"]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    project_root = Path("/home/huyaoyang/Projects/flashrag_project_20251213/New_ChronoRAG")
    asset_dir = project_root / "outputs/paper_assets_v4_experiment_upgrade/20260414_220953"
    ensure_dir(asset_dir)
    configs = {
        "hoh": load_config(project_root / "configs/conflict_aware_rag_hoh_pilot_256_linux.yaml"),
        "temprageval": load_config(project_root / "configs/conflict_aware_rag_temprageval_pilot_256_linux.yaml"),
    }
    thresholds = [0.03, 0.05, 0.07]
    methods_baseline = ["no_conflict", "full_model", "judge_verify_pipeline"]
    method_selective = "full_model_selective_conflict"
    method_selective_judge = "full_model_selective_conflict_judge"

    pilot_rows: list[dict[str, Any]] = []
    for dkey, cfg in configs.items():
        mainline = cfg["mainline"]
        mainline["runs_dir"] = str(project_root / "runs")
        query_records = [to_query_record(item) for item in read_jsonl(mainline["queries_path"])]
        retrieval_records = run_search(
            corpus_path=mainline["corpus_path"],
            index_dir=mainline["bm25_index_dir"],
            queries=[{"id": q.query_id, "query": q.query, "query_time": q.query_time, "metadata": q.metadata} for q in query_records],
            top_k=int(mainline["retrieval_top_k"]),
            strategy=str(mainline.get("retrieval_strategy", "standard")),
        )
        baseline_cache: dict[str, MethodResult] = {}
        for method in methods_baseline:
            baseline_cache[method] = _resolve_rows(query_records, retrieval_records, mainline, method, 0.05, f"stageI_routeB_{dkey}")
        for th in thresholds:
            for method in methods_baseline:
                r = baseline_cache[method]
                pilot_rows.append({"dataset": r.dataset, "method": method, "threshold": th, "exact_match": r.exact_match, "token_f1": r.token_f1, "citation_title_recall": r.citation_title_recall, "tfa": r.tfa, "cfa": r.cfa, "gate_activation_ratio": 0.0, "judge_activation_ratio": 0.0, "arbitration_latency_ms_per_query": r.arbitration_latency_ms_per_query, "query_count": r.query_count, "run_dir": r.run_dir})
            rs = _resolve_rows(query_records, retrieval_records, mainline, method_selective, th, f"stageI_routeB_{dkey}")
            pilot_rows.append({"dataset": rs.dataset, "method": method_selective, "threshold": th, "exact_match": rs.exact_match, "token_f1": rs.token_f1, "citation_title_recall": rs.citation_title_recall, "tfa": rs.tfa, "cfa": rs.cfa, "gate_activation_ratio": rs.gate_activation_ratio, "judge_activation_ratio": rs.judge_activation_ratio, "arbitration_latency_ms_per_query": rs.arbitration_latency_ms_per_query, "query_count": rs.query_count, "run_dir": rs.run_dir})

    _rows_to_csv(asset_dir / "selective_conflict_results.csv", pilot_rows)
    by_ds_th: dict[tuple[str, float], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in pilot_rows:
        by_ds_th[(row["dataset"], float(row["threshold"]))][row["method"]] = row

    scored_thresholds = []
    for th in thresholds:
        hoh = by_ds_th.get(("hoh_pilot_256", th), {})
        tem = by_ds_th.get(("temprageval_pilot_256", th), {})
        if not hoh or not tem:
            continue
        cond_a = float(tem[method_selective]["token_f1"]) >= float(tem["no_conflict"]["token_f1"])
        cond_b = (hoh[method_selective]["cfa"] is not None and hoh["full_model"]["cfa"] is not None and float(hoh[method_selective]["cfa"]) > float(hoh["full_model"]["cfa"]))
        cond_c = float(hoh[method_selective]["gate_activation_ratio"]) < 1.0 and float(tem[method_selective]["gate_activation_ratio"]) < 1.0
        lat_delta_hoh = (float(hoh[method_selective]["arbitration_latency_ms_per_query"]) / max(float(hoh["full_model"]["arbitration_latency_ms_per_query"]), 1e-6)) - 1.0
        lat_delta_tem = (float(tem[method_selective]["arbitration_latency_ms_per_query"]) / max(float(tem["full_model"]["arbitration_latency_ms_per_query"]), 1e-6)) - 1.0
        cond_d = max(lat_delta_hoh, lat_delta_tem) <= 0.25
        score_tuple = (1 if cond_a else 0, 1 if cond_b else 0, 1 if cond_c else 0, 1 if cond_d else 0, float(tem[method_selective]["token_f1"]) - float(tem["no_conflict"]["token_f1"]), float(hoh[method_selective]["cfa"] or 0.0) - float(hoh["full_model"]["cfa"] or 0.0), -float(hoh[method_selective]["gate_activation_ratio"]) - float(tem[method_selective]["gate_activation_ratio"]))
        scored_thresholds.append((th, score_tuple, {"cond_a": cond_a, "cond_b": cond_b, "cond_c": cond_c, "cond_d": cond_d, "lat_delta_hoh": lat_delta_hoh, "lat_delta_tem": lat_delta_tem}))

    scored_thresholds.sort(key=lambda x: x[1], reverse=True)
    best_threshold = scored_thresholds[0][0] if scored_thresholds else 0.05

    judge_rows: list[dict[str, Any]] = []
    for dkey, cfg in configs.items():
        mainline = cfg["mainline"]
        mainline["runs_dir"] = str(project_root / "runs")
        query_records = [to_query_record(item) for item in read_jsonl(mainline["queries_path"])]
        retrieval_records = run_search(
            corpus_path=mainline["corpus_path"],
            index_dir=mainline["bm25_index_dir"],
            queries=[{"id": q.query_id, "query": q.query, "query_time": q.query_time, "metadata": q.metadata} for q in query_records],
            top_k=int(mainline["retrieval_top_k"]),
            strategy=str(mainline.get("retrieval_strategy", "standard")),
        )
        for method in [method_selective, method_selective_judge]:
            r = _resolve_rows(query_records, retrieval_records, mainline, method, best_threshold, f"stageI_routeB_judge_{dkey}")
            judge_rows.append({"dataset": r.dataset, "method": method, "threshold": best_threshold, "exact_match": r.exact_match, "token_f1": r.token_f1, "citation_title_recall": r.citation_title_recall, "tfa": r.tfa, "cfa": r.cfa, "gate_activation_ratio": r.gate_activation_ratio, "judge_activation_ratio": r.judge_activation_ratio, "arbitration_latency_ms_per_query": r.arbitration_latency_ms_per_query, "query_count": r.query_count, "run_dir": r.run_dir})

    _rows_to_csv(asset_dir / "selective_conflict_judge_results.csv", judge_rows)
    best_rows = [r for r in pilot_rows if float(r["threshold"]) == float(best_threshold)]
    best_map = {(r["dataset"], r["method"]): r for r in best_rows}
    judge_map = {(r["dataset"], r["method"]): r for r in judge_rows}

    promoted_method = None
    promote_reason = []
    for cand in [method_selective, method_selective_judge]:
        hoh = judge_map.get(("hoh_pilot_256", cand)) if cand == method_selective_judge else best_map.get(("hoh_pilot_256", cand))
        tem = judge_map.get(("temprageval_pilot_256", cand)) if cand == method_selective_judge else best_map.get(("temprageval_pilot_256", cand))
        hoh_full = best_map.get(("hoh_pilot_256", "full_model"))
        tem_nc = best_map.get(("temprageval_pilot_256", "no_conflict"))
        tem_jv = best_map.get(("temprageval_pilot_256", "judge_verify_pipeline"))
        if not all([hoh, tem, hoh_full, tem_nc, tem_jv]):
            continue
        cond_hoh_f1 = float(hoh["token_f1"]) >= (float(hoh_full["token_f1"]) - 0.001)
        cond_hoh_cfa = (hoh["cfa"] is not None and hoh_full["cfa"] is not None and float(hoh["cfa"]) > float(hoh_full["cfa"]))
        cond_temp = (float(tem["token_f1"]) >= float(tem_nc["token_f1"]) + 0.002) or (float(tem["token_f1"]) >= float(tem_jv["token_f1"]) - 0.002)
        cond_judge_ratio = float(tem.get("judge_activation_ratio", 0.0)) <= 0.15 and float(hoh.get("judge_activation_ratio", 0.0)) <= 0.15
        cond_latency = (float(hoh["arbitration_latency_ms_per_query"]) / max(float(hoh_full["arbitration_latency_ms_per_query"]), 1e-6) - 1.0) <= 0.25 and (float(tem["arbitration_latency_ms_per_query"]) / max(float(best_map[("temprageval_pilot_256", "full_model")]["arbitration_latency_ms_per_query"]), 1e-6) - 1.0) <= 0.25
        if cond_hoh_f1 and cond_hoh_cfa and cond_temp and cond_judge_ratio and cond_latency:
            promoted_method = cand
            promote_reason = [f"HOH constraints satisfied for {cand}", "TempRAGEval F1 constraint satisfied", "Judge ratio and latency constraints satisfied"]
            break

    lines = ["# SELECTIVE_CONFLICT_PILOT_RESULTS", "", f"- timestamp: {datetime.now().isoformat()}", f"- thresholds tested: {thresholds}", f"- best_threshold_by_priority: {best_threshold}", "", "## Pilot Metrics"]
    for r in pilot_rows:
        lines.append(f"- {r['dataset']} | {r['method']} | th={r['threshold']:.2f} | EM={r['exact_match']:.4f} | F1={r['token_f1']:.4f} | CTR={r['citation_title_recall']} | TFA={r['tfa']} | CFA={r['cfa']} | gate={r['gate_activation_ratio']:.4f} | judge={r['judge_activation_ratio']:.4f} | arb_ms={r['arbitration_latency_ms_per_query']:.4f}")
    (asset_dir / "SELECTIVE_CONFLICT_PILOT_RESULTS.md").write_text("\\n".join(lines), encoding="utf-8")

    lines2 = ["# SELECTIVE_CONFLICT_JUDGE_RESULTS", "", f"- timestamp: {datetime.now().isoformat()}", f"- selected_threshold: {best_threshold}", ""]
    for r in judge_rows:
        lines2.append(f"- {r['dataset']} | {r['method']} | th={r['threshold']:.2f} | EM={r['exact_match']:.4f} | F1={r['token_f1']:.4f} | CTR={r['citation_title_recall']} | TFA={r['tfa']} | CFA={r['cfa']} | gate={r['gate_activation_ratio']:.4f} | judge={r['judge_activation_ratio']:.4f} | arb_ms={r['arbitration_latency_ms_per_query']:.4f}")
    (asset_dir / "SELECTIVE_CONFLICT_JUDGE_RESULTS.md").write_text("\\n".join(lines2), encoding="utf-8")

    decision = ["# SELECTIVE_CONFLICT_DECISION", "", f"- best_gate_threshold: {best_threshold}", f"- promote_to_formal: {'YES' if promoted_method else 'NO'}", f"- promoted_method: {promoted_method or 'none'}", "", "## Why"]
    if promoted_method:
        decision.extend([f"- {x}" for x in promote_reason])
    else:
        decision.extend(["- At least one formal-promotion constraint not satisfied on pilot.", "- Keep Route B at pilot to avoid unnecessary formal compute."])
    decision.extend(["", "## Impact on Main Narrative", "- If not promoted: Route B serves as targeted selective-control evidence; mainline remains unchanged.", "- If promoted: Route B can be added as selective arbitration refinement under fixed-pool setting."])
    (asset_dir / "SELECTIVE_CONFLICT_DECISION.md").write_text("\\n".join(decision), encoding="utf-8")

    write_json(asset_dir / "route_b_run_manifest.json", {"thresholds": thresholds, "best_threshold": best_threshold, "promoted_method": promoted_method, "pilot_rows": len(pilot_rows), "judge_rows": len(judge_rows)})
    print(json.dumps({"asset_dir": str(asset_dir), "best_threshold": best_threshold, "promoted_method": promoted_method, "pilot_rows": len(pilot_rows), "judge_rows": len(judge_rows)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
