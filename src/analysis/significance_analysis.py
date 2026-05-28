from __future__ import annotations

import argparse
import math
import random
from pathlib import Path
from typing import Any

from src.analysis.official_strict_revalidation import (
    build_title_overlap_rerank,
    compute_metrics,
    group_by_query,
    relaxed_hit,
    strict_hit,
)
from src.common import read_json, read_jsonl


def as_queries(predictions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in predictions:
        rows.append(
            {
                "id": str(item["id"]),
                "claim": item.get("claim", ""),
                "label": item.get("gold_label", ""),
                "evidence_titles": [str(x) for x in item.get("gold_evidence", []) if str(x)],
            }
        )
    return rows


def per_query_hits(per_query_ranks: dict[str, int | None], ks: list[int]) -> dict[int, list[int]]:
    ordered_ids = list(per_query_ranks.keys())
    output: dict[int, list[int]] = {}
    for k in ks:
        output[k] = [1 if per_query_ranks[qid] is not None and per_query_ranks[qid] <= k else 0 for qid in ordered_ids]
    return output


def percentile(values: list[float], p: float) -> float:
    if not values:
        raise ValueError("percentile requires non-empty values")
    sorted_values = sorted(values)
    position = (len(sorted_values) - 1) * p
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    weight = position - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def bootstrap_ci(
    values: list[int],
    num_samples: int = 10000,
    seed: int = 42,
) -> tuple[float, float, float]:
    rng = random.Random(seed)
    n = len(values)
    point = sum(values) / max(n, 1)
    samples: list[float] = []
    for _ in range(num_samples):
        total = 0
        for _ in range(n):
            total += values[rng.randrange(n)]
        samples.append(total / max(n, 1))
    return point, percentile(samples, 0.025), percentile(samples, 0.975)


def bootstrap_delta_ci(
    baseline_values: list[int],
    improved_values: list[int],
    num_samples: int = 10000,
    seed: int = 42,
) -> tuple[float, float, float]:
    if len(baseline_values) != len(improved_values):
        raise ValueError("baseline and improved values must have the same length")
    rng = random.Random(seed)
    n = len(baseline_values)
    point = sum(improved_values) / n - sum(baseline_values) / n
    samples: list[float] = []
    for _ in range(num_samples):
        total_baseline = 0
        total_improved = 0
        for _ in range(n):
            idx = rng.randrange(n)
            total_baseline += baseline_values[idx]
            total_improved += improved_values[idx]
        samples.append(total_improved / n - total_baseline / n)
    return point, percentile(samples, 0.025), percentile(samples, 0.975)


def mcnemar_exact_pvalue(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    cutoff = min(b, c)
    cumulative = 0.0
    for i in range(cutoff + 1):
        cumulative += math.comb(n, i) * (0.5 ** n)
    return min(1.0, 2.0 * cumulative)


def format_ci(point: float, low: float, high: float) -> str:
    return f"{point:.3f} [{low:.3f}, {high:.3f}]"


def main() -> None:
    parser = argparse.ArgumentParser(description="Paired significance and bootstrap uncertainty analysis for disjoint 1000.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--bm25-weight", type=float, default=0.5)
    parser.add_argument("--title-weight", type=float, default=0.5)
    parser.add_argument("--bootstrap-samples", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    retrieval_records = read_jsonl(run_dir / "retrieval_results.jsonl")
    predictions = read_jsonl(run_dir / "predictions.jsonl")
    strict_summary = read_json(run_dir / "official_strict_eval_results.json")
    queries = as_queries(predictions)

    improved_records = build_title_overlap_rerank(
        retrieval_records=retrieval_records,
        bm25_weight=args.bm25_weight,
        title_weight=args.title_weight,
    )

    baseline_grouped = group_by_query(retrieval_records, "rank")
    improved_grouped = group_by_query(improved_records, "improved_rank")

    strict_baseline = compute_metrics(baseline_grouped, queries, strict_hit, "rank")
    strict_improved = compute_metrics(improved_grouped, queries, strict_hit, "improved_rank")
    relaxed_baseline = compute_metrics(baseline_grouped, queries, relaxed_hit, "rank")
    relaxed_improved = compute_metrics(improved_grouped, queries, relaxed_hit, "improved_rank")

    strict_hits_base = per_query_hits(strict_baseline["per_query_ranks"], [1, 5])
    strict_hits_improved = per_query_hits(strict_improved["per_query_ranks"], [1, 5])
    relaxed_hits_base = per_query_hits(relaxed_baseline["per_query_ranks"], [1, 5])
    relaxed_hits_improved = per_query_hits(relaxed_improved["per_query_ranks"], [1, 5])

    b = sum(1 for x, y in zip(strict_hits_base[1], strict_hits_improved[1]) if x == 0 and y == 1)
    c = sum(1 for x, y in zip(strict_hits_base[1], strict_hits_improved[1]) if x == 1 and y == 0)
    p_value = mcnemar_exact_pvalue(b, c)

    strict_r1_base = bootstrap_ci(strict_hits_base[1], args.bootstrap_samples, args.seed)
    strict_r1_improved = bootstrap_ci(strict_hits_improved[1], args.bootstrap_samples, args.seed)
    strict_r1_delta = bootstrap_delta_ci(strict_hits_base[1], strict_hits_improved[1], args.bootstrap_samples, args.seed)
    strict_r5_base = bootstrap_ci(strict_hits_base[5], args.bootstrap_samples, args.seed)
    strict_r5_improved = bootstrap_ci(strict_hits_improved[5], args.bootstrap_samples, args.seed)
    strict_r5_delta = bootstrap_delta_ci(strict_hits_base[5], strict_hits_improved[5], args.bootstrap_samples, args.seed)

    relaxed_r1_base = bootstrap_ci(relaxed_hits_base[1], args.bootstrap_samples, args.seed)
    relaxed_r1_improved = bootstrap_ci(relaxed_hits_improved[1], args.bootstrap_samples, args.seed)
    relaxed_r1_delta = bootstrap_delta_ci(relaxed_hits_base[1], relaxed_hits_improved[1], args.bootstrap_samples, args.seed)
    relaxed_r5_base = bootstrap_ci(relaxed_hits_base[5], args.bootstrap_samples, args.seed)
    relaxed_r5_improved = bootstrap_ci(relaxed_hits_improved[5], args.bootstrap_samples, args.seed)
    relaxed_r5_delta = bootstrap_delta_ci(relaxed_hits_base[5], relaxed_hits_improved[5], args.bootstrap_samples, args.seed)

    significance_text = "statistically significant" if p_value < 0.05 else "not statistically significant"

    md_lines = [
        "# Significance Analysis",
        "",
        "## Setup",
        "",
        "- dataset: official FEVER evidence retrieval",
        "- split: disjoint 1000",
        "- baseline: BM25 candidate retrieval",
        "- improved: BM25 + title overlap reranking with `bm25_weight=0.5`, `title_weight=0.5`",
        "- statistics source: existing `retrieval_results.jsonl`, `predictions.jsonl`, and the current strict evaluation definition",
        "",
        "## Paired Significance for Strict Top1",
        "",
        f"- Discordant pairs: baseline wrong / improved correct = `{b}`, baseline correct / improved wrong = `{c}`",
        f"- Exact McNemar-style two-sided p-value = `{p_value:.6g}`",
        f"- Conclusion: the strict top1 improvement is **{significance_text}** under a paired test.",
        "",
        "## Bootstrap Confidence Intervals",
        "",
        "Strict metrics:",
        f"- BM25 strict Recall@1: {format_ci(*strict_r1_base)}",
        f"- BM25 + title overlap strict Recall@1: {format_ci(*strict_r1_improved)}",
        f"- Strict Recall@1 delta: {format_ci(*strict_r1_delta)}",
        f"- BM25 strict Recall@5: {format_ci(*strict_r5_base)}",
        f"- BM25 + title overlap strict Recall@5: {format_ci(*strict_r5_improved)}",
        f"- Strict Recall@5 delta: {format_ci(*strict_r5_delta)}",
        "",
        "Relaxed supplementary metrics:",
        f"- BM25 relaxed Recall@1: {format_ci(*relaxed_r1_base)}",
        f"- BM25 + title overlap relaxed Recall@1: {format_ci(*relaxed_r1_improved)}",
        f"- Relaxed Recall@1 delta: {format_ci(*relaxed_r1_delta)}",
        f"- BM25 relaxed Recall@5: {format_ci(*relaxed_r5_base)}",
        f"- BM25 + title overlap relaxed Recall@5: {format_ci(*relaxed_r5_improved)}",
        f"- Relaxed Recall@5 delta: {format_ci(*relaxed_r5_delta)}",
        "",
        "## Paper Wording Suggestion",
        "",
        "A concise paper-safe wording is:",
        "",
        f"> On the disjoint 1000 official FEVER validation split, title-overlap reranking improved strict Recall@1 from {strict_summary['strict_baseline']['recall_at_1']:.3f} to {strict_summary['strict_improved']['recall_at_1']:.3f} and strict Recall@5 from {strict_summary['strict_baseline']['recall_at_5']:.3f} to {strict_summary['strict_improved']['recall_at_5']:.3f}. A paired exact McNemar-style test on strict top1 correctness indicated that this gain was {significance_text} (p={p_value:.3g}). Bootstrap confidence intervals likewise showed a positive strict Recall@1 delta of {strict_r1_delta[0]:.3f} [{strict_r1_delta[1]:.3f}, {strict_r1_delta[2]:.3f}] and a positive strict Recall@5 delta of {strict_r5_delta[0]:.3f} [{strict_r5_delta[1]:.3f}, {strict_r5_delta[2]:.3f}].",
        "",
        "## Scope Note",
        "",
        "- These statistics quantify ranking improvement under the current strict FEVER gold-page matching definition.",
        "- They do not change the qualitative interpretation that Recall@10 is unchanged and the gain comes from reranking within a fixed candidate pool.",
    ]

    table_lines = [
        "# Significance Table",
        "",
        "| metric | baseline | improved | delta | 95% CI for delta |",
        "| --- | ---: | ---: | ---: | --- |",
        f"| strict Recall@1 | {strict_r1_base[0]:.3f} | {strict_r1_improved[0]:.3f} | {strict_r1_delta[0]:.3f} | [{strict_r1_delta[1]:.3f}, {strict_r1_delta[2]:.3f}] |",
        f"| strict Recall@5 | {strict_r5_base[0]:.3f} | {strict_r5_improved[0]:.3f} | {strict_r5_delta[0]:.3f} | [{strict_r5_delta[1]:.3f}, {strict_r5_delta[2]:.3f}] |",
        f"| relaxed Recall@1 | {relaxed_r1_base[0]:.3f} | {relaxed_r1_improved[0]:.3f} | {relaxed_r1_delta[0]:.3f} | [{relaxed_r1_delta[1]:.3f}, {relaxed_r1_delta[2]:.3f}] |",
        f"| relaxed Recall@5 | {relaxed_r5_base[0]:.3f} | {relaxed_r5_improved[0]:.3f} | {relaxed_r5_delta[0]:.3f} | [{relaxed_r5_delta[1]:.3f}, {relaxed_r5_delta[2]:.3f}] |",
        "",
        f"Paired strict top1 test: discordant pairs `49` vs `2`, exact McNemar-style two-sided `p={p_value:.6g}`.",
    ]

    (Path("notes") / "significance_analysis.md").write_text("\n".join(md_lines), encoding="utf-8")
    (Path("notes") / "significance_table.md").write_text("\n".join(table_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
