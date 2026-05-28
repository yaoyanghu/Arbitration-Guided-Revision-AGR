# Nearest Title-Aware Baseline Table

| setting | strict R@1 | strict R@5 | strict R@10 | relaxed R@1 | relaxed R@5 | relaxed R@10 | strict top1 delta vs BM25 | strict improved | strict regressed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| routeA_bm25 | 0.368 | 0.627 | 0.720 | 0.737 | 0.883 | 0.918 | 0 | 0 | 0 |
| routeA_bm25_exact_title_boost | 0.544 | 0.708 | 0.720 | 0.801 | 0.904 | 0.918 | 176 | 192 | 16 |
| routeA_bm25_title_overlap | 0.415 | 0.680 | 0.720 | 0.760 | 0.895 | 0.918 | 47 | 49 | 2 |

Caption:
On the disjoint official FEVER 1000 validation split, the nearest simpler title-aware lexical baseline, `BM25 + exact title boost`, is stronger than `BM25 + token-level title overlap` under both strict and relaxed evaluation. The exact-title variant gives the largest absolute gain, while title overlap remains a more conservative alternative with fewer regressions.
