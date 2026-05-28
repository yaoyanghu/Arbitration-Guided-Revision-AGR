# Current Claim Freeze

## Purpose

This note freezes the most defensible current paper claim for the official FEVER short paper line, using the real result files in the repository rather than only narrative notes.

Primary evidence checked:
- [official_strict_eval_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/official_strict_eval_results.json)
- [official_labelwise_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/official_labelwise_results.json)
- [nearest_title_baseline_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/nearest_title_baseline_results.json)
- [nearest_title_baseline_results.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/nearest_title_baseline_results.md)
- [nearest_title_baseline_table.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/nearest_title_baseline_table.md)
- [significance_analysis.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/significance_analysis.md)
- [significance_table.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/significance_table.md)
- [tables_markdown.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/tables_markdown.md)
- [results_error_validity_draft.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/results_error_validity_draft.md)

## Freeze Decision

### 1. What is the safest current claim?

Current safest claim:

- **B. More general title-aware lexical reranking is effective**

This is stronger and safer than:

- **A. Title overlap reranking is the main effective method**

### Why?

Evidence from [official_strict_eval_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/official_strict_eval_results.json):
- BM25 strict `R@1 / R@5 / R@10 = 0.368 / 0.627 / 0.720`
- BM25 + title overlap strict `R@1 / R@5 / R@10 = 0.415 / 0.680 / 0.720`
- So title overlap is clearly effective relative to BM25 on the disjoint 1000 main split.

Evidence from [nearest_title_baseline_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/nearest_title_baseline_results.json):
- BM25 + exact title boost strict `R@1 / R@5 / R@10 = 0.544 / 0.708 / 0.720`
- BM25 + title overlap strict `R@1 / R@5 / R@10 = 0.415 / 0.680 / 0.720`
- Exact title boost beats title overlap by `129` strict top1 hits and `41` relaxed top1 hits.

So the repository now supports the following statement:
- title-aware lexical reranking helps evidence ranking

But it no longer safely supports the stronger statement:
- token-level title overlap is the best or necessary title-aware reranker

## 2. Is the nearest title baseline now stronger than the original title-overlap story?

Yes.

This is not just a narrative interpretation in notes. It is directly reflected in [nearest_title_baseline_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/nearest_title_baseline_results.json) and summarized again in [nearest_title_baseline_table.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/nearest_title_baseline_table.md):

- BM25 strict top1 hits: `368`
- exact title boost strict top1 hits: `544`
- title overlap strict top1 hits: `415`

Tradeoff evidence from the same file:
- exact title boost strict improved cases: `192`
- exact title boost strict regressed cases: `16`
- title overlap strict improved cases: `49`
- title overlap strict regressed cases: `2`

This means:
- exact title boost is stronger in absolute retrieval gain
- title overlap is more conservative

The old paper story centered on title overlap as the headline method is therefore no longer the most defensible story.

## 3. What should be rewritten?

### Title direction

Avoid titles that claim or imply that `title overlap` itself is the central validated contribution.

Recommended direction:
- lightweight title-aware lexical reranking for FEVER evidence retrieval
- improving strict gold-page ranking with lightweight title-aware reranking

Avoid:
- titles whose main novelty noun is specifically `title overlap`

### Abstract direction

Recommended abstract framing:
- This paper studies lightweight title-aware lexical reranking for official FEVER evidence retrieval.
- Starting from BM25 candidate retrieval, it evaluates whether a simple title-aware reranker can improve strict gold-page ranking without changing top-k coverage.
- On the disjoint 1000 validation split, title-aware lexical reranking improves early-rank evidence retrieval quality.
- Within the tested heuristics, a nearest simpler exact-title-style boost is stronger than token-level title overlap, while title overlap remains a conservative alternative.

This wording is supported by:
- [official_strict_eval_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/official_strict_eval_results.json)
- [nearest_title_baseline_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/nearest_title_baseline_results.json)
- [significance_analysis.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/significance_analysis.md)

### Method naming

Recommended naming hierarchy:
- task family: `title-aware lexical reranking`
- baseline: `routeA_bm25`
- variant 1: `routeA_bm25_title_overlap`
- variant 2: `routeA_bm25_exact_title_boost`

Avoid naming the whole paper after only `title overlap`, because [nearest_title_baseline_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/nearest_title_baseline_results.json) now shows that title overlap is not the strongest tested lexical title feature.

### Result wording

The stable wording should now be:

- BM25 + title overlap is effective relative to BM25 on the disjoint 1000 split.
- Its strict top1 gain is statistically significant.
- However, among the currently tested lightweight title-aware heuristics, exact title boost is stronger on the same split.

This wording is grounded by:
- effectiveness vs BM25: [official_strict_eval_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/official_strict_eval_results.json)
- statistical support: [significance_analysis.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/significance_analysis.md)
- stronger nearby baseline: [nearest_title_baseline_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/nearest_title_baseline_results.json)

## 4. What should still be cited as the main experimental anchor?

The main validation split remains:
- [official_strict_eval_results.json](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/official_strict_eval_results.json)

The exact values that remain valid and important:
- strict BM25 `0.368 / 0.627 / 0.720`
- strict BM25 + title overlap `0.415 / 0.680 / 0.720`
- strict improved cases `49`
- strict regressed cases `2`

These should remain in the paper because they show that title overlap is real and statistically supported relative to BM25.

But these should no longer be presented as sufficient to claim title overlap is the best lightweight title-aware method, because the nearest-baseline comparison contradicts that stronger interpretation.

## Final Freeze

Current frozen claim:

- **The paper should now be framed as a study of lightweight title-aware lexical reranking for official FEVER evidence retrieval, not as a paper whose central claim is that token-level title overlap is the strongest validated method.**

More specific freeze:

- keep the disjoint 1000 BM25 vs title-overlap result as a valid core result
- keep significance and CI for that result
- but rewrite the paper title, abstract, and method framing so that exact-title-style lexical reranking is acknowledged as the stronger tested nearby baseline
