# Paper Asset Inventory

## Scope

This inventory covers the current official FEVER short-paper line only. It is based on real files in the repository.

## Main Results

- [official_strict_eval_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/official_strict_eval_results.json)
  Main disjoint 1000 validation result for BM25 vs BM25 + title overlap.
- [official_strict_eval_summary.md](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/official_strict_eval_summary.md)
  Human-readable summary of strict / relaxed definitions and improvement counts.
- [metrics.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/metrics.json)
  Broader Route A stage metrics, including BM25 stage metrics and label-group hit rates.

## Baseline Comparisons

- [nearest_title_baseline_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/nearest_title_baseline_results.json)
  Direct comparison among `routeA_bm25`, `routeA_bm25_exact_title_boost`, and `routeA_bm25_title_overlap`.
- [nearest_title_baseline_summary.md](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/nearest_title_baseline_summary.md)
  Human-readable summary of the nearest title-aware baseline comparison.
- [exact_title_boost_strict_improved_cases.jsonl](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/exact_title_boost_strict_improved_cases.jsonl)
- [exact_title_boost_strict_regressed_cases.jsonl](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/exact_title_boost_strict_regressed_cases.jsonl)
- [title_overlap_strict_improved_cases.jsonl](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/title_overlap_strict_improved_cases.jsonl)
- [title_overlap_strict_regressed_cases.jsonl](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/title_overlap_strict_regressed_cases.jsonl)
- [exact_title_only_wins_over_overlap_cases.jsonl](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/exact_title_only_wins_over_overlap_cases.jsonl)
- [title_overlap_only_wins_over_exact_cases.jsonl](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/title_overlap_only_wins_over_exact_cases.jsonl)

## Strict / Relaxed Assets

- [official_strict_eval_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/official_strict_eval_results.json)
  Primary strict / relaxed result file for BM25 vs title overlap.
- [official_strict_eval_summary.md](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/official_strict_eval_summary.md)
- [nearest_title_baseline_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/nearest_title_baseline_results.json)
  Includes strict and relaxed values for exact-title boost and title overlap.

## Label-Wise Assets

- [official_labelwise_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/official_labelwise_results.json)
  SUPPORTS / REFUTES strict metrics for BM25 vs title overlap.
- [official_labelwise_summary.md](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/official_labelwise_summary.md)

## Case Analysis

- [case_analysis.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/case_analysis.md)
  Pattern-level summary of strict improvements and regressions on disjoint 1000.
- [case_table.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/case_table.md)
  Compact paper-ready case table.
- [official_strict_improved_cases.jsonl](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/official_strict_improved_cases.jsonl)
- [official_strict_regressed_cases.jsonl](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/official_strict_regressed_cases.jsonl)

## Significance / Confidence Intervals

- [significance_analysis.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/significance_analysis.md)
  McNemar-style paired test and bootstrap CIs for the BM25 vs title-overlap comparison.
- [significance_table.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/significance_table.md)

## Tables

- [tables_markdown.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/tables_markdown.md)
  Main markdown tables for the disjoint 1000 title-overlap line.
- [tables_latex.tex](/D:/HUYAOYANG/Work/ChronoRAG/notes/tables_latex.tex)
  LaTeX export of table assets.
- [nearest_title_baseline_table.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/nearest_title_baseline_table.md)
  Separate table for the nearest title-aware baseline comparison.
- [significance_table.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/significance_table.md)
  Separate table for statistical evidence.

## Methods / Scripts

Core evaluation and reranking scripts actually used to produce current assets:

- [official_strict_revalidation.py](/D:/HUYAOYANG/Work/ChronoRAG/src/analysis/official_strict_revalidation.py)
  Rebuilds title-overlap reranking from retrieval results and computes strict / relaxed metrics.
- [nearest_title_baseline_eval.py](/D:/HUYAOYANG/Work/ChronoRAG/src/analysis/nearest_title_baseline_eval.py)
  Computes the nearest baseline comparison against exact-title boost.
- [significance_analysis.py](/D:/HUYAOYANG/Work/ChronoRAG/src/analysis/significance_analysis.py)
  Computes paired significance and bootstrap CIs.
- [official_labelwise_strict_eval.py](/D:/HUYAOYANG/Work/ChronoRAG/src/analysis/official_labelwise_strict_eval.py)
  Produces label-wise strict metrics for the title-overlap line.
- [overlap_check.py](/D:/HUYAOYANG/Work/ChronoRAG/src/analysis/overlap_check.py)
  Supports split overlap checking.

Supporting run inputs:
- [retrieval_results.jsonl](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/retrieval_results.jsonl)
- [predictions.jsonl](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/predictions.jsonl)

## Still Missing

These are still missing if the paper is to be pushed beyond a tight short-paper scope:

- completed full-dev fixed-weight confirmation run
  Evidence: there is no completed `runs/fever_official_route_a_full_dev/` asset set in the local repository.
- cleanly frozen paper wording after the nearest-baseline result
  Evidence: [results_error_validity_draft.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/results_error_validity_draft.md) still centers title overlap as the main method without integrating the stronger exact-title baseline.
- unified main table set that incorporates nearest-baseline comparison and significance into one final paper-facing table package
  Evidence: [tables_markdown.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/tables_markdown.md) currently covers the title-overlap line but not the newer nearest-baseline comparison.
- explicit runtime / efficiency reporting
  Evidence: no runtime summary file is present in `notes/` or the run directories.

## Bottom Line

The short-paper line already has:
- a main disjoint validation result
- strict and relaxed metrics
- label-wise results
- case analysis
- significance / CI
- a nearest title-aware baseline comparison

What is still missing is not core evidence of a retrieval effect. What is missing is:
- final narrative unification
- full-dev robustness confirmation
- paper-facing packaging of the now-updated method story
