# Tables

## Table 1. 500-query weight sweep results

| title_weight | strict Recall@1 | strict top1 delta | strict regressed cases |
| ---: | ---: | ---: | ---: |
| 0.1 | 0.356 | 2 | 0 |
| 0.2 | 0.360 | 4 | 0 |
| 0.3 | 0.366 | 7 | 0 |
| 0.4 | 0.378 | 13 | 0 |
| 0.5 | 0.400 | 24 | 0 |

## Table 2. Old follow-up 1000 vs new disjoint 1000

| split | status | strict baseline R@1 / R@5 / R@10 | strict improved R@1 / R@5 / R@10 | strict delta top1 | improved / regressed |
| --- | --- | --- | --- | ---: | ---: |
| old follow-up 1000 | non-independent follow-up | 0.379 / 0.614 / 0.705 | 0.429 / 0.662 / 0.705 | 50 | 51 / 1 |
| new disjoint 1000 | independent validation | 0.368 / 0.627 / 0.720 | 0.415 / 0.680 / 0.720 | 47 | 49 / 2 |

## Table 3. Disjoint 1000 main results

| setting | strict R@1 / R@5 / R@10 | relaxed R@1 / R@5 / R@10 |
| --- | --- | --- |
| routeA_bm25 | 0.368 / 0.627 / 0.720 | 0.737 / 0.883 / 0.918 |
| routeA_bm25_title_overlap | 0.415 / 0.680 / 0.720 | 0.760 / 0.895 / 0.918 |

## Table 4. Disjoint 1000 improvement statistics

| baseline strict top1 | improved strict top1 | delta | improved cases | regressed cases | relaxed top1 delta |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 368 | 415 | 47 | 49 | 2 | 23 |

## Table 5. Disjoint 1000 label-wise strict results

| label | baseline R@1 / R@5 / R@10 | improved R@1 / R@5 / R@10 | delta@1 | delta@5 |
| --- | --- | --- | ---: | ---: |
| SUPPORTS | 0.411 / 0.696 / 0.770 | 0.466 / 0.732 / 0.770 | 0.054 | 0.036 |
| REFUTES | 0.325 / 0.560 / 0.671 | 0.365 / 0.629 / 0.671 | 0.040 | 0.069 |

## Table 6. Main differences between old and new 1000-query results

| metric | old follow-up 1000 | new disjoint 1000 | change |
| --- | ---: | ---: | ---: |
| strict baseline R@1 | 0.379 | 0.368 | -0.011 |
| strict improved R@1 | 0.429 | 0.415 | -0.014 |
| strict baseline R@5 | 0.614 | 0.627 | +0.013 |
| strict improved R@5 | 0.662 | 0.680 | +0.018 |
| strict baseline R@10 | 0.705 | 0.720 | +0.015 |
| strict improved R@10 | 0.705 | 0.720 | +0.015 |
| strict top1 delta | 50 | 47 | -3 |
| strict regressed cases | 1 | 2 | +1 |
