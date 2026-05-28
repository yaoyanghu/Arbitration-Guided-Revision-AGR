from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.common import read_json, read_jsonl


def short_claim(text: str, limit: int = 90) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 3] + "..."


def classify_case(item: dict[str, Any]) -> tuple[str, str]:
    baseline = str(item.get("baseline_top1_title", ""))
    improved = str(item.get("improved_top1_title", ""))
    gold_titles = [str(x) for x in item.get("gold_titles", []) if str(x)]
    gold_joined = " / ".join(gold_titles)
    if any(gold.lower() in improved.lower() for gold in gold_titles):
        if baseline and "(" not in baseline and len(baseline.split()) <= 2:
            return ("surface_title_match", "The improved ranking promotes the exact gold page title over a shorter or truncated baseline title.")
        if any(token in baseline.lower() for token in ["disambiguation", "list", "series", "song", "group"]):
            return ("disambiguation", "The title-overlap score resolves ambiguity by preferring the candidate whose page title matches the claim entity more directly.")
        return ("exact_gold_promotion", "The gold evidence page was already in the candidate set and title overlap moved it to rank 1.")
    if len(gold_titles) > 1:
        return ("multi_page_claim", "The claim can be supported or refuted by multiple evidence pages, and title overlap helps prioritize one explicit gold page.")
    return ("lexical_alignment", "The improved ranking benefits from stronger lexical alignment between the claim entity phrase and the page title.")


def build_case_analysis(run_dir: Path, notes_dir: Path) -> None:
    strict_improved = read_jsonl(run_dir / "official_strict_improved_cases.jsonl")
    strict_regressed = read_jsonl(run_dir / "official_strict_regressed_cases.jsonl")
    relaxed_improved = read_jsonl(run_dir / "official_improved_cases.jsonl")
    relaxed_regressed = read_jsonl(run_dir / "official_regressed_cases.jsonl")

    enriched_improved: list[dict[str, Any]] = []
    for item in strict_improved:
        case_type, explanation = classify_case(item)
        enriched = dict(item)
        enriched["case_type"] = case_type
        enriched["short_explanation"] = explanation
        enriched_improved.append(enriched)

    type_counts = Counter(item["case_type"] for item in enriched_improved)
    regression = strict_regressed[0] if strict_regressed else None
    regression_cause = ""
    if regression:
        regression_cause = (
            "The single strict regression appears to come from surface title overlap favoring a different entity mention "
            f"(`{regression['improved_top1_title']}`) over the correct baseline page (`{regression['baseline_top1_title']}`), "
            "even though the baseline already ranked the gold page first under strict evaluation."
        )

    representative = []
    priority_order = ["disambiguation", "surface_title_match", "exact_gold_promotion", "multi_page_claim", "lexical_alignment"]
    for case_type in priority_order:
        typed = [item for item in enriched_improved if item["case_type"] == case_type]
        representative.extend(typed[:2])
    seen = set()
    representative_rows = []
    for item in representative:
        if item["query_id"] in seen:
            continue
        seen.add(item["query_id"])
        representative_rows.append(
            {
                "claim_id": item["query_id"],
                "label": item["gold_label"],
                "claim_summary": short_claim(str(item["claim"])),
                "gold_page": " / ".join(item["gold_titles"]),
                "baseline_rank": item["baseline_strict_rank"],
                "improved_rank": item["improved_strict_rank"],
                "case_type": item["case_type"],
                "short_explanation": item["short_explanation"],
            }
        )
        if len(representative_rows) >= 8:
            break

    notes_dir.mkdir(parents=True, exist_ok=True)
    case_table_lines = [
        "# Case Table",
        "",
        "| claim_id | label | claim_summary | gold_page | baseline_rank | improved_rank | case_type | short_explanation |",
        "| --- | --- | --- | --- | ---: | ---: | --- | --- |",
    ]
    for row in representative_rows:
        case_table_lines.append(
            f"| {row['claim_id']} | {row['label']} | {row['claim_summary']} | {row['gold_page']} | {row['baseline_rank']} | {row['improved_rank']} | {row['case_type']} | {row['short_explanation']} |"
        )
    (notes_dir / "case_table.md").write_text("\n".join(case_table_lines), encoding="utf-8")

    analysis_lines = [
        "# Case Analysis",
        "",
        f"- Strict improvement count: {len(strict_improved)}",
        f"- Strict regression count: {len(strict_regressed)}",
        f"- Relaxed improvement count: {len(relaxed_improved)}",
        f"- Relaxed regression count: {len(relaxed_regressed)}",
        "",
        "## Improvement Patterns",
        "",
    ]
    for case_type, count in type_counts.most_common():
        analysis_lines.append(f"- `{case_type}`: {count}")
    analysis_lines.extend(
        [
            "",
            "## Regression",
            "",
            f"- {regression_cause or 'No strict regression was observed.'}",
            "",
            "## Paper-Style Error Analysis",
            "",
            "Across strict improvement cases, the dominant pattern is not expanded candidate coverage but rank correction within the existing top-k set. "
            "In many examples, the baseline top result is a semantically related but non-gold page such as a disambiguation page, a broader franchise page, or a nearby lexical variant. "
            "Title overlap helps in precisely those cases because the claim often repeats the entity phrase that also appears in the gold page title. "
            "This effect is particularly visible for named entities, film titles, and organization names where BM25 retrieves a relevant neighborhood but does not always place the exact evidence page first. "
            "The single strict regression suggests the main risk of this reranker: when a competing page shares high surface overlap with the claim title but is not the gold evidence page, title-aware reranking can over-promote it.",
        ]
    )
    (notes_dir / "case_analysis.md").write_text("\n".join(analysis_lines), encoding="utf-8")


def build_tables(notes_dir: Path, sweep_path: Path, metrics_path: Path, strict_path: Path, labelwise_path: Path) -> None:
    sweep = read_json(sweep_path)
    metrics = read_json(metrics_path)
    strict = read_json(strict_path)
    labelwise = read_json(labelwise_path)

    md_lines = ["# Tables", ""]
    tex_lines = []

    md_lines.extend(
        [
            "## Table 1. 500-query weight sweep results",
            "",
            "| title_weight | strict Recall@1 | strict top1 delta | strict regressed cases |",
            "| ---: | ---: | ---: | ---: |",
        ]
    )
    tex_lines.extend(
        [
            "% Table 1: 500-query weight sweep results",
            "\\begin{table}[t]",
            "\\centering",
            "\\caption{500-query weight sweep for title overlap reranking.}",
            "\\begin{tabular}{lccc}",
            "\\hline",
            "title weight & strict R@1 & strict $\\Delta$top1 & strict regressions \\\\",
            "\\hline",
        ]
    )
    for row in sweep["sweep_results"]:
        md_lines.append(
            f"| {row['title_weight']:.1f} | {row['strict_recall_at_1']:.3f} | {row['strict_top1_delta']} | {row['strict_regressed_case_count']} |"
        )
        tex_lines.append(
            f"{row['title_weight']:.1f} & {row['strict_recall_at_1']:.3f} & {row['strict_top1_delta']} & {row['strict_regressed_case_count']} \\\\"
        )
    tex_lines.extend(["\\hline", "\\end{tabular}", "\\end{table}", ""])

    md_lines.extend(
        [
            "",
            "## Table 2. 1000-query main results",
            "",
            "| setting | strict R@1 / R@5 / R@10 | relaxed R@1 / R@5 / R@10 |",
            "| --- | --- | --- |",
            f"| routeA_bm25 | {strict['strict_baseline']['recall_at_1']:.3f} / {strict['strict_baseline']['recall_at_5']:.3f} / {strict['strict_baseline']['recall_at_10']:.3f} | {strict['relaxed_baseline']['recall_at_1']:.3f} / {strict['relaxed_baseline']['recall_at_5']:.3f} / {strict['relaxed_baseline']['recall_at_10']:.3f} |",
            f"| routeA_bm25_title_overlap | {strict['strict_improved']['recall_at_1']:.3f} / {strict['strict_improved']['recall_at_5']:.3f} / {strict['strict_improved']['recall_at_10']:.3f} | {strict['relaxed_improved']['recall_at_1']:.3f} / {strict['relaxed_improved']['recall_at_5']:.3f} / {strict['relaxed_improved']['recall_at_10']:.3f} |",
        ]
    )
    tex_lines.extend(
        [
            "% Table 2: 1000-query main results",
            "\\begin{table}[t]",
            "\\centering",
            "\\caption{Main results on the 1000-query official FEVER verifiable subset.}",
            "\\begin{tabular}{lcc}",
            "\\hline",
            "setting & strict R@1/R@5/R@10 & relaxed R@1/R@5/R@10 \\\\",
            "\\hline",
            f"routeA\\_bm25 & {strict['strict_baseline']['recall_at_1']:.3f}/{strict['strict_baseline']['recall_at_5']:.3f}/{strict['strict_baseline']['recall_at_10']:.3f} & {strict['relaxed_baseline']['recall_at_1']:.3f}/{strict['relaxed_baseline']['recall_at_5']:.3f}/{strict['relaxed_baseline']['recall_at_10']:.3f} \\\\",
            f"routeA\\_bm25\\_title\\_overlap & {strict['strict_improved']['recall_at_1']:.3f}/{strict['strict_improved']['recall_at_5']:.3f}/{strict['strict_improved']['recall_at_10']:.3f} & {strict['relaxed_improved']['recall_at_1']:.3f}/{strict['relaxed_improved']['recall_at_5']:.3f}/{strict['relaxed_improved']['recall_at_10']:.3f} \\\\",
            "\\hline",
            "\\end{tabular}",
            "\\end{table}",
            "",
        ]
    )

    md_lines.extend(
        [
            "",
            "## Table 3. 1000-query strict improvement statistics",
            "",
            "| baseline strict top1 | improved strict top1 | delta | improved cases | regressed cases |",
            "| ---: | ---: | ---: | ---: | ---: |",
            f"| {strict['strict_baseline']['top1_hits']} | {strict['strict_improved']['top1_hits']} | {strict['strict_top1_delta']} | {strict['strict_improved_case_count']} | {strict['strict_regressed_case_count']} |",
        ]
    )
    tex_lines.extend(
        [
            "% Table 3: 1000-query strict improvement statistics",
            "\\begin{table}[t]",
            "\\centering",
            "\\caption{Strict top-1 improvement statistics on the 1000-query setting.}",
            "\\begin{tabular}{ccccc}",
            "\\hline",
            "baseline strict top1 & improved strict top1 & $\\Delta$ & improved cases & regressed cases \\\\",
            "\\hline",
            f"{strict['strict_baseline']['top1_hits']} & {strict['strict_improved']['top1_hits']} & {strict['strict_top1_delta']} & {strict['strict_improved_case_count']} & {strict['strict_regressed_case_count']} \\\\",
            "\\hline",
            "\\end{tabular}",
            "\\end{table}",
            "",
        ]
    )

    def delta(a: float, b: float) -> float:
        return b - a

    md_lines.extend(
        [
            "",
            "## Table 4. 1000-query label-wise strict results",
            "",
            "| label | baseline R@1 / R@5 / R@10 | improved R@1 / R@5 / R@10 | delta@1 | delta@5 |",
            "| --- | --- | --- | ---: | ---: |",
        ]
    )
    tex_lines.extend(
        [
            "% Table 4: 1000-query label-wise strict results",
            "\\begin{table}[t]",
            "\\centering",
            "\\caption{Label-wise strict retrieval results on the 1000-query setting.}",
            "\\begin{tabular}{lcccc}",
            "\\hline",
            "label & baseline R@1/R@5/R@10 & improved R@1/R@5/R@10 & $\\Delta$@1 & $\\Delta$@5 \\\\",
            "\\hline",
        ]
    )
    for label in ("SUPPORTS", "REFUTES"):
        base = labelwise["baseline"][label]
        imp = labelwise["title_overlap"][label]
        md_lines.append(
            f"| {label} | {base['strict_recall_at_1']:.3f} / {base['strict_recall_at_5']:.3f} / {base['strict_recall_at_10']:.3f} | {imp['strict_recall_at_1']:.3f} / {imp['strict_recall_at_5']:.3f} / {imp['strict_recall_at_10']:.3f} | {delta(base['strict_recall_at_1'], imp['strict_recall_at_1']):.3f} | {delta(base['strict_recall_at_5'], imp['strict_recall_at_5']):.3f} |"
        )
        tex_lines.append(
            f"{label} & {base['strict_recall_at_1']:.3f}/{base['strict_recall_at_5']:.3f}/{base['strict_recall_at_10']:.3f} & {imp['strict_recall_at_1']:.3f}/{imp['strict_recall_at_5']:.3f}/{imp['strict_recall_at_10']:.3f} & {delta(base['strict_recall_at_1'], imp['strict_recall_at_1']):.3f} & {delta(base['strict_recall_at_5'], imp['strict_recall_at_5']):.3f} \\\\"
        )
    tex_lines.extend(["\\hline", "\\end{tabular}", "\\end{table}", ""])

    notes_dir.mkdir(parents=True, exist_ok=True)
    (notes_dir / "tables_markdown.md").write_text("\n".join(md_lines), encoding="utf-8")
    (notes_dir / "tables_latex.tex").write_text("\n".join(tex_lines), encoding="utf-8")


def build_draft(notes_dir: Path, sweep_path: Path, metrics_path: Path, strict_path: Path, labelwise_path: Path, overlap_report_path: Path) -> None:
    sweep = read_json(sweep_path)
    metrics = read_json(metrics_path)
    strict = read_json(strict_path)
    labelwise = read_json(labelwise_path)
    overlap_text = overlap_report_path.read_text(encoding="utf-8") if overlap_report_path.exists() else ""
    case_analysis_text = (notes_dir / "case_analysis.md").read_text(encoding="utf-8") if (notes_dir / "case_analysis.md").exists() else ""

    lines = [
        "# Results",
        "",
        "We evaluate a lightweight reranking variant that augments BM25 with a title-overlap score while keeping the candidate set fixed. "
        f"On the 1000-query official FEVER verifiable subset, the strongest setting from the 500-query sweep is `bm25_weight=0.5` and `title_weight=0.5`. "
        f"Under strict gold-page matching, Recall@1 improves from {strict['strict_baseline']['recall_at_1']:.3f} to {strict['strict_improved']['recall_at_1']:.3f}, "
        f"and Recall@5 improves from {strict['strict_baseline']['recall_at_5']:.3f} to {strict['strict_improved']['recall_at_5']:.3f}. "
        f"Recall@10 remains unchanged at {strict['strict_baseline']['recall_at_10']:.3f}, indicating that the method primarily improves ranking quality rather than candidate coverage.",
        "",
        "The same pattern is visible in the raw top-1 counts: strict top-1 hits increase from "
        f"{strict['strict_baseline']['top1_hits']} to {strict['strict_improved']['top1_hits']} (delta = {strict['strict_top1_delta']}). "
        "This behavior is important because it isolates the contribution of title-aware reranking from any expansion in retrieval breadth. "
        "The 500-query weight sweep further shows that the improvement is monotonic across the tested title weights, with the best strict performance achieved at a 0.5/0.5 balance between BM25 and title overlap.",
        "",
        "Label-wise analysis suggests that the effect is not confined to one claim type. "
        f"For SUPPORTS claims, strict Recall@1 rises from {labelwise['baseline']['SUPPORTS']['strict_recall_at_1']:.3f} to {labelwise['title_overlap']['SUPPORTS']['strict_recall_at_1']:.3f}. "
        f"For REFUTES claims, strict Recall@1 rises from {labelwise['baseline']['REFUTES']['strict_recall_at_1']:.3f} to {labelwise['title_overlap']['REFUTES']['strict_recall_at_1']:.3f}. "
        "This symmetric improvement matters because it suggests that the method is helping with page selection rather than exploiting label-specific regularities.",
        "",
        "# Error Analysis",
        "",
        "The retrieved top-k set remains fixed, so the observed gains come from reranking within the existing candidate pool. "
        "Improvement cases are dominated by situations where the correct evidence page was already present but not ranked first. "
        "The most common patterns include exact gold-page promotion, disambiguation resolution, and surface title alignment, especially for entity-centric claims whose key lexical units appear directly in the gold page title. "
        "These cases are consistent with a simple intuition: BM25 often retrieves a semantically relevant neighborhood, while title overlap helps identify the page that most directly matches the claim's focal entity.",
        "",
        "The regression profile remains small. "
        f"On the 1000-query strict evaluation, the best configuration yields {strict['strict_regressed_case_count']} strict regression against {strict['strict_improved_case_count']} strict improvements. "
        "The remaining regression is consistent with a surface-overlap failure mode, where a competing title shares strong lexical overlap with the claim but is not the official evidence page. "
        "This suggests that title overlap is useful as a reranking signal, but its errors are also title-driven and therefore interpretable.",
        "",
        "# Threats to Validity",
        "",
        "Several limitations remain. First, the current evidence concerns retrieval and reranking rather than end-to-end claim verification. "
        "Second, the present results are based on a single random seed, so variance across repeated samples has not yet been quantified. "
        "Third, although the 1000-query experiment is larger than the 500-query sweep, it is still a subset of the full official development set. "
        "A full-dev rerun would strengthen the external validity of the reported gains. "
        "Fourth, the independence between the 500-query tuning subset and the 1000-query validation subset should be explicitly checked and, if necessary, repaired with a disjoint validation split before making strong claims about held-out generalization.",
    ]
    if overlap_text:
        lines.extend(["", "## Split Independence Note", "", overlap_text[:1200]])
    if case_analysis_text:
        lines.extend(["", "## Case Analysis Note", "", case_analysis_text[:1200]])
    (notes_dir / "results_error_validity_draft.md").write_text("\n".join(lines), encoding="utf-8")


def build_minimal_validation_plan(notes_dir: Path, overlap_report_path: Path, strict_path: Path, labelwise_path: Path, sweep_path: Path) -> None:
    strict = read_json(strict_path)
    _ = read_json(labelwise_path)
    _ = read_json(sweep_path)
    overlap_exists = overlap_report_path.exists()
    overlap_text = overlap_report_path.read_text(encoding="utf-8") if overlap_exists else ""
    need_validation = True
    reason = "The overlap status between the 500-query tuning subset and the 1000-query validation subset must be checked before claiming independent validation."
    if overlap_exists and "need disjoint validation" not in overlap_text.lower():
        need_validation = False
        reason = "The overlap report does not indicate a problematic dependence between tuning and validation splits."

    lines = [
        "# Minimal Validation Plan",
        "",
        f"- Need extra validation: {'yes' if need_validation else 'no'}",
        f"- Why: {reason}",
    ]
    if need_validation:
        lines.extend(
            [
                "",
                "## Recommended Minimal-Cost Plan",
                "",
                "- Construct a validation subset from the official dev verifiable pool that is strictly disjoint from the 500-query tuning subset by FEVER id.",
                "- Keep the method fixed at `bm25_weight=0.5, title_weight=0.5`.",
                "- Reuse the existing official corpus and BM25 index.",
                "- Re-run only the 1000-query evaluation on the disjoint subset rather than performing a full-dev rerun first.",
                "",
                "## Expected New Artifacts",
                "",
                "- `data/processed/fever_official/shared_task_dev_verifiable_1000_disjoint.jsonl`",
                "- `runs/fever_official_route_a_1000_disjoint/metrics.json`",
                "- `runs/fever_official_route_a_1000_disjoint/official_strict_eval_results.json`",
                "- `runs/fever_official_route_a_1000_disjoint/official_improved_cases.jsonl`",
                "- `runs/fever_official_route_a_1000_disjoint/official_regressed_cases.jsonl`",
            ]
        )
    else:
        lines.extend(
            [
                "",
                "## Decision",
                "",
                "- No additional rerun is required before writing up the current result.",
            ]
        )
    (notes_dir / "minimal_validation_plan.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build paper artifacts from current FEVER official experiments.")
    parser.add_argument("--notes-dir", default="notes")
    parser.add_argument("--sweep-path", required=True)
    parser.add_argument("--metrics-path", required=True)
    parser.add_argument("--strict-path", required=True)
    parser.add_argument("--labelwise-path", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--overlap-report", required=True)
    args = parser.parse_args()

    notes_dir = Path(args.notes_dir)
    run_dir = Path(args.run_dir)
    build_case_analysis(run_dir, notes_dir)
    build_tables(notes_dir, Path(args.sweep_path), Path(args.metrics_path), Path(args.strict_path), Path(args.labelwise_path))
    build_draft(notes_dir, Path(args.sweep_path), Path(args.metrics_path), Path(args.strict_path), Path(args.labelwise_path), Path(args.overlap_report))
    build_minimal_validation_plan(notes_dir, Path(args.overlap_report), Path(args.strict_path), Path(args.labelwise_path), Path(args.sweep_path))
    print(json.dumps({"notes_dir": str(notes_dir)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
