# Results

This paper should now be framed as a study of **lightweight title-aware lexical reranking** for official FEVER evidence retrieval, rather than as a paper claiming that token-level title overlap is the validated best method.

The main independent validation result remains the disjoint 1000 split:
- [`official_strict_eval_results.json`](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/official_strict_eval_results.json)

On that split, the `routeA_bm25_title_overlap` variant still improves strict gold-page ranking over BM25:
- strict Recall@1: `0.368 -> 0.415`
- strict Recall@5: `0.627 -> 0.680`
- strict Recall@10: `0.720 -> 0.720`

This remains an important result because it shows that a lightweight title-aware lexical signal can improve early-rank evidence retrieval without expanding candidate-set coverage. The unchanged Recall@10 indicates that the gain comes from reranking inside a fixed BM25 candidate pool, not from broader retrieval coverage.

However, the nearest-baseline comparison now changes the correct paper-level interpretation:
- [`nearest_title_baseline_results.json`](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/nearest_title_baseline_results.json)

On the same disjoint 1000 split:
- BM25 + exact title boost strict Recall@1 / @5 / @10: `0.544 / 0.708 / 0.720`
- BM25 + title overlap strict Recall@1 / @5 / @10: `0.415 / 0.680 / 0.720`

So the most defensible current claim is not:
- title overlap is the strongest lightweight reranking method

The correct claim is:
- lightweight title-aware lexical reranking improves official FEVER evidence retrieval
- within the currently tested lightweight title-aware heuristics, exact title boost is stronger than token-level title overlap
- title overlap remains a more conservative alternative with fewer regressions

This interpretation is also consistent with the significance evidence:
- [`significance_analysis.md`](/D:/HUYAOYANG/Work/ChronoRAG/notes/significance_analysis.md)

For the BM25 vs title-overlap comparison on the disjoint 1000 split:
- strict top1 discordant pairs: `49` vs `2`
- paired exact McNemar-style `p = 1.17861e-12`
- strict Recall@1 delta CI: `0.047 [0.034, 0.061]`
- strict Recall@5 delta CI: `0.053 [0.039, 0.068]`

So the repository still supports a statistically defensible BM25 vs title-overlap result. What changed is not whether title overlap works. What changed is the broader method narrative: title overlap should now be presented as one variant inside a larger family of title-aware lexical rerankers, not as the uniquely validated best method.

# Error Analysis

The disjoint validation still supports the same retrieval-stage interpretation:
- the gain appears at the top ranks
- Recall@10 remains unchanged
- the main effect is rank correction inside an already retrieved candidate set

Variant-specific evidence from:
- [`case_analysis.md`](/D:/HUYAOYANG/Work/ChronoRAG/notes/case_analysis.md)

For the `routeA_bm25_title_overlap` variant, the dominant strict improvement patterns remain:
- `surface_title_match`
- `exact_gold_promotion`
- `disambiguation`

This is still useful for the paper, but it should now be written as:
- analysis of the title-overlap variant

not as:
- proof that title overlap is the strongest title-aware lexical design

The new nearest-baseline comparison provides an additional interpretation layer:
- exact title boost wins on many queries where the claim contains the gold page title as a clean contiguous phrase
- title overlap still helps on some parenthetical or non-contiguous surface-form cases

This is supported by:
- [`nearest_title_baseline_results.md`](/D:/HUYAOYANG/Work/ChronoRAG/notes/nearest_title_baseline_results.md)

So the paper's error analysis should distinguish:
- why title-aware lexical reranking helps in general
- why exact title boost is stronger in aggregate
- why title overlap can still be retained as a conservative alternative

# Threats to Validity

The split-independence issue has already been repaired for the main result by moving from the older overlapping 1000 run to the disjoint 1000 run:
- [`overlap_check_report.md`](/D:/HUYAOYANG/Work/ChronoRAG/notes/overlap_check_report.md)

But the following limitations remain and should still be stated clearly:

1. This is a retrieval-stage evidence-ranking paper, not an end-to-end FEVER verification paper.
2. The current most defensible main result is still on a single disjoint 1000 validation split.
3. A full-dev confirmation run has not been completed in a usable form yet.
4. The currently strongest nearby lexical baseline is exact title boost, not title overlap.

The fourth point is now particularly important. Without acknowledging it, the paper risks overstating what the repository actually shows.

# Writing Readiness

The paper is still writable now, but the final story must be narrower and more accurate than before.

Recommended scope:
- official FEVER evidence retrieval
- BM25 baseline retrieval
- lightweight title-aware lexical reranking family
- disjoint 1000 strict gold-page validation
- BM25 vs title-overlap main comparison
- nearest exact-title baseline as a stronger nearby comparator

Not supported as the primary claim:
- title overlap is the best lightweight title-aware method
- a complete ChronoRAG system result
- Route B or Route C conclusions
- generation or graph claims

In short, the most paper-ready interpretation is now:
- title-aware lexical reranking helps strict FEVER evidence-page ranking
- title overlap is one statistically supported variant
- exact title boost is stronger among the tested lightweight title-aware heuristics
