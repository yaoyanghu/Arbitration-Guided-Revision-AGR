# Tables

## Table 1. Main disjoint 1000 results for BM25 vs title-overlap variant

| setting | strict R@1 / R@5 / R@10 | relaxed R@1 / R@5 / R@10 |
| --- | --- | --- |
| routeA_bm25 | 0.368 / 0.627 / 0.720 | 0.737 / 0.883 / 0.918 |
| routeA_bm25_title_overlap | 0.415 / 0.680 / 0.720 | 0.760 / 0.895 / 0.918 |

Caption:
On the disjoint 1000 official FEVER validation split, the title-overlap variant improves early-rank strict and relaxed retrieval quality over BM25, while Recall@10 remains unchanged, indicating reranking rather than candidate-set expansion.

## Table 2. Nearest title-aware lexical baseline comparison

| setting | strict R@1 | strict R@5 | strict R@10 | relaxed R@1 | relaxed R@5 | relaxed R@10 | strict top1 delta vs BM25 | strict improved | strict regressed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| routeA_bm25 | 0.368 | 0.627 | 0.720 | 0.737 | 0.883 | 0.918 | 0 | 0 | 0 |
| routeA_bm25_exact_title_boost | 0.544 | 0.708 | 0.720 | 0.801 | 0.904 | 0.918 | 176 | 192 | 16 |
| routeA_bm25_title_overlap | 0.415 | 0.680 | 0.720 | 0.760 | 0.895 | 0.918 | 47 | 49 | 2 |

Caption:
Among the currently tested lightweight title-aware lexical rerankers, the exact-title-boost variant is stronger than the title-overlap variant in absolute retrieval gain, while title overlap is more conservative and incurs fewer regressions.

## Table 3. Label-wise strict results for BM25 vs title-overlap variant

| label | baseline R@1 / R@5 / R@10 | title-overlap R@1 / R@5 / R@10 | delta@1 | delta@5 |
| --- | --- | --- | ---: | ---: |
| SUPPORTS | 0.411 / 0.696 / 0.770 | 0.466 / 0.732 / 0.770 | 0.054 | 0.036 |
| REFUTES | 0.325 / 0.560 / 0.671 | 0.365 / 0.629 / 0.671 | 0.040 | 0.069 |

Caption:
The title-overlap variant improves strict early-rank retrieval for both SUPPORTS and REFUTES on the disjoint 1000 split, indicating that the effect is not restricted to one label group.

## Table 4. Statistical support for BM25 vs title-overlap

| metric | baseline | title-overlap | delta | 95% CI for delta |
| --- | ---: | ---: | ---: | --- |
| strict Recall@1 | 0.368 | 0.415 | 0.047 | [0.034, 0.061] |
| strict Recall@5 | 0.627 | 0.680 | 0.053 | [0.039, 0.068] |
| relaxed Recall@1 | 0.737 | 0.760 | 0.023 | [0.012, 0.035] |
| relaxed Recall@5 | 0.883 | 0.895 | 0.012 | [0.004, 0.021] |

Caption:
The BM25 vs title-overlap comparison is statistically supported on the disjoint 1000 split: the strict top1 paired test uses discordant pairs `49` vs `2` with exact McNemar-style `p = 1.17861e-12`, and all reported Recall@1 / Recall@5 deltas have positive bootstrap confidence intervals.

## Table 5. Historical note: old overlapping 1000 vs disjoint 1000

| split | status | strict baseline R@1 / R@5 / R@10 | strict title-overlap R@1 / R@5 / R@10 | strict delta top1 | improved / regressed |
| --- | --- | --- | --- | ---: | ---: |
| old follow-up 1000 | non-independent follow-up | 0.379 / 0.614 / 0.705 | 0.429 / 0.662 / 0.705 | 50 | 51 / 1 |
| new disjoint 1000 | independent validation | 0.368 / 0.627 / 0.720 | 0.415 / 0.680 / 0.720 | 47 | 49 / 2 |

Caption:
The disjoint 1000 split should be treated as the only main validation result. The older 1000-query run is retained only as historical context because it overlaps with the tuning set.
