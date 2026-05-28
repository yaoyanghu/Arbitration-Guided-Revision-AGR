# Paper Closeout Plan

## Scope

This plan covers only the official FEVER short-paper line. It does not propose new ChronoRAG Route B or Route C work.

Primary evidence checked:
- [official_strict_eval_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/official_strict_eval_results.json)
- [official_labelwise_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/official_labelwise_results.json)
- [nearest_title_baseline_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/nearest_title_baseline_results.json)
- [significance_analysis.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/significance_analysis.md)
- [case_analysis.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/case_analysis.md)
- [tables_markdown.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/tables_markdown.md)

## 1. Why the paper is already writable

The paper is already writable because the repository now contains a complete minimal evidence chain for a retrieval-focused short paper:

- independent main validation result on disjoint 1000
  Evidence: [official_strict_eval_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/official_strict_eval_results.json)
- strict and relaxed metric separation
  Evidence: same file as above
- label-wise strict breakdown
  Evidence: [official_labelwise_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/official_labelwise_results.json)
- case analysis and regression analysis
  Evidence: [case_analysis.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/case_analysis.md), [case_table.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/case_table.md)
- significance and confidence intervals
  Evidence: [significance_analysis.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/significance_analysis.md), [significance_table.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/significance_table.md)
- reviewer-facing nearest baseline comparison
  Evidence: [nearest_title_baseline_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/nearest_title_baseline_results.json)

So the bottleneck is no longer "missing core evidence." The bottleneck is now "freezing the correct story."

## 2. Experiments that must be retained

These should remain in the paper package:

1. Main disjoint 1000 BM25 vs title-overlap result
- Evidence file: [official_strict_eval_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/official_strict_eval_results.json)
- Reason: this is still the clean independent validation showing title overlap is effective relative to BM25.

2. Split-independence repair narrative
- Evidence file: [overlap_check_report.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/overlap_check_report.md)
- Reason: this is necessary to explain why `fever_official_route_a_1000` is not the main result.

3. Significance / CI
- Evidence files: [significance_analysis.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/significance_analysis.md), [significance_table.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/significance_table.md)
- Reason: this upgrades the BM25 vs title-overlap gain from descriptive to statistically supported.

4. Nearest title-aware baseline comparison
- Evidence files: [nearest_title_baseline_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/nearest_title_baseline_results.json), [nearest_title_baseline_table.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/nearest_title_baseline_table.md)
- Reason: without this, the paper is vulnerable to the obvious reviewer question "would a simpler title-aware heuristic do the same or better?"

5. Label-wise strict results
- Evidence file: [official_labelwise_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/official_labelwise_results.json)
- Reason: this shows the effect is not isolated to only SUPPORTS or only REFUTES.

## 3. Which older conclusions should be downgraded

These should be downgraded to historical context rather than central conclusions:

1. "Title overlap is the strongest lightweight title-aware reranker."
- This is no longer supported.
- Contradicting evidence: [nearest_title_baseline_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/nearest_title_baseline_results.json)

2. The older `fever_official_route_a_1000` result as independent validation.
- This should be treated only as historical follow-up evidence.
- Contradicting evidence: [overlap_check_report.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/overlap_check_report.md), [tables_markdown.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/tables_markdown.md)

3. Any phrasing that implies complete ChronoRAG system evidence.
- The current results are retrieval-only.
- Supporting evidence: [results_error_validity_draft.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/results_error_validity_draft.md)

## 4. What counts only as a bonus, not a blocker

These are add-on improvements, not preconditions for writing:

- full-dev fixed-weight confirmation
- runtime / efficiency summary
- additional title-feature ablations beyond the nearest exact-title baseline
- more qualitative case studies

The paper can still be drafted before these are finished, because the main independent result, significance, and nearest-baseline challenge are already present.

## 5. Why full-dev should not keep running blindly

There are two reasons.

### A. It is supplementary, not the main claim anchor

The main independent result already exists:
- [official_strict_eval_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/official_strict_eval_results.json)

So full-dev is a robustness confirmation, not the only thing keeping the paper from being writable.

### B. The current execution path is clearly inefficient

Repository evidence shows the full-dev run was started as a plain retrieval-first workflow:
- [full_dev_confirmation.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/full_dev_confirmation.md)

Operational evidence from the current remote run is that the job remains stuck in retrieval for a very long time without incremental artifacts. Even without depending on remote process state in this document, the local repository already reflects that no completed full-dev asset set has been produced. Therefore the rational decision is:

- do not make the paper schedule depend on the current blind full-dev run
- protect the already strong disjoint-1000-based paper asset package

## 6. Recommended title direction

Recommended direction:
- lightweight title-aware lexical reranking for official FEVER evidence retrieval
- improving strict evidence-page ranking with title-aware lexical reranking

Avoid:
- titles that claim title overlap is itself the validated best method

Reason:
- [nearest_title_baseline_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/nearest_title_baseline_results.json) now shows exact-title-style boosting is stronger on the same split.

## 7. Recommended contribution wording

Recommended contribution wording:

1. The paper isolates a retrieval-stage problem on official FEVER: improving strict gold-page ranking inside a fixed BM25 candidate pool.
2. It shows that lightweight title-aware lexical reranking can improve early-rank evidence quality without changing Recall@10.
3. It provides a strict-vs-relaxed evaluation distinction, label-wise analysis, case analysis, and significance support.
4. It also shows that among the tested lightweight title-aware heuristics, a nearest exact-title-style boost is stronger than token-level title overlap, which sharpens the scope of the claim.

This contribution wording is supported by:
- [official_strict_eval_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/official_strict_eval_results.json)
- [official_labelwise_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/official_labelwise_results.json)
- [nearest_title_baseline_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/nearest_title_baseline_results.json)
- [significance_analysis.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/significance_analysis.md)

## 8. Recommended main table structure

Recommended main table order:

Table 1. Main disjoint 1000 results
- BM25
- BM25 + title overlap
- strict and relaxed `R@1 / R@5 / R@10`

Table 2. Nearest title-aware baseline comparison
- BM25
- BM25 + exact title boost
- BM25 + title overlap
- strict and relaxed values

Table 3. Label-wise strict results
- SUPPORTS
- REFUTES

Table 4. Significance / CI
- strict `R@1`
- strict `R@5`
- relaxed `R@1`
- relaxed `R@5`
- paired strict top1 p-value

This structure keeps the story tight:
- main effect
- nearest challenge baseline
- robustness by label
- statistical support

## Bottom Line

The best closeout path is:
- freeze the paper as a retrieval-focused official FEVER short paper
- keep disjoint 1000 as the main anchor
- keep significance and nearest-baseline evidence
- stop depending on the unresolved full-dev run for core paper progress

That is the highest-value closeout path supported by the current repository.
