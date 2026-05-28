# Final Table Pack

## 1. Main Table

| setting | strict R@1 / R@5 / R@10 | relaxed R@1 / R@5 / R@10 |
| --- | --- | --- |
| routeA_bm25 | 0.368 / 0.627 / 0.720 | 0.737 / 0.883 / 0.918 |
| routeA_bm25_title_overlap | 0.415 / 0.680 / 0.720 | 0.760 / 0.895 / 0.918 |

Caption-style wording:
On the disjoint 1000 official FEVER validation split, the title-overlap variant improves strict and relaxed early-rank evidence retrieval over BM25, while Recall@10 remains unchanged, indicating reranking gain rather than candidate-set expansion.

## 2. Nearest Baseline Table

| setting | strict R@1 | strict R@5 | strict R@10 | relaxed R@1 | relaxed R@5 | relaxed R@10 | strict top1 delta vs BM25 | strict improved | strict regressed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| routeA_bm25 | 0.368 | 0.627 | 0.720 | 0.737 | 0.883 | 0.918 | 0 | 0 | 0 |
| routeA_bm25_exact_title_boost | 0.544 | 0.708 | 0.720 | 0.801 | 0.904 | 0.918 | 176 | 192 | 16 |
| routeA_bm25_title_overlap | 0.415 | 0.680 | 0.720 | 0.760 | 0.895 | 0.918 | 47 | 49 | 2 |

Caption-style wording:
Among the tested lightweight title-aware lexical rerankers, exact title boost is stronger than title overlap in absolute retrieval gain, while title overlap is more conservative and introduces fewer strict regressions.

## 3. Label-Wise Table

| label | baseline R@1 / R@5 / R@10 | title-overlap R@1 / R@5 / R@10 | delta@1 | delta@5 |
| --- | --- | --- | ---: | ---: |
| SUPPORTS | 0.411 / 0.696 / 0.770 | 0.466 / 0.732 / 0.770 | 0.054 | 0.036 |
| REFUTES | 0.325 / 0.560 / 0.671 | 0.365 / 0.629 / 0.671 | 0.040 | 0.069 |

Caption-style wording:
The title-overlap variant improves strict early-rank retrieval for both SUPPORTS and REFUTES, showing that the effect is not confined to a single label category.

## 4. Significance Table

| metric | baseline | title-overlap | delta | 95% CI for delta |
| --- | ---: | ---: | ---: | --- |
| strict Recall@1 | 0.368 | 0.415 | 0.047 | [0.034, 0.061] |
| strict Recall@5 | 0.627 | 0.680 | 0.053 | [0.039, 0.068] |
| relaxed Recall@1 | 0.737 | 0.760 | 0.023 | [0.012, 0.035] |
| relaxed Recall@5 | 0.883 | 0.895 | 0.012 | [0.004, 0.021] |

Caption-style wording:
For the BM25 vs title-overlap comparison, the strict top1 paired test uses discordant pairs 49 vs 2 with exact McNemar-style p = 1.17861e-12. All Recall@1 and Recall@5 deltas have positive bootstrap confidence intervals, confirming that the title-overlap variant is statistically supported relative to BM25.
