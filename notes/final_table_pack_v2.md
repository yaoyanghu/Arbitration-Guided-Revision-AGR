# Final Table Pack v2

## Table 1. Main metadata-aware family results on disjoint 1000

| variant | strict R@1 / R@5 / R@10 | relaxed R@1 / R@5 / R@10 | strict improved / regressed |
| --- | --- | --- | ---: |
| routeA_bm25 | 0.368 / 0.627 / 0.720 | 0.737 / 0.883 / 0.918 | 0 / 0 |
| routeA_bm25_title_overlap | 0.415 / 0.680 / 0.720 | 0.760 / 0.895 / 0.918 | 49 / 2 |
| routeA_bm25_exact_title_boost | 0.544 / 0.708 / 0.720 | 0.801 / 0.904 / 0.918 | 192 / 16 |
| routeA_bm25_alias_redirect_match | 0.357 / 0.626 / 0.720 | 0.733 / 0.883 / 0.918 | 1 / 12 |
| routeA_bm25_disambiguation_title_match | 0.378 / 0.622 / 0.720 | 0.749 / 0.887 / 0.918 | 22 / 12 |

Caption:
Metadata-aware grounded reranking improves early evidence access within a fixed BM25 candidate pool, but not all metadata cues are equally effective. Exact title boost is the strongest aggressive variant, while title overlap remains the most conservative useful variant.

## Table 2. Efficiency frontier under fixed page budget

| variant | strict MRR | strict nDCG@5 | strict nDCG@10 | strict mean first-hit rank |
| --- | ---: | ---: | ---: | ---: |
| routeA_bm25 | 0.478 | 0.502 | 0.534 | 2.575 |
| routeA_bm25_title_overlap | 0.520 | 0.551 | 0.567 | 2.078 |
| routeA_bm25_exact_title_boost | 0.617 | 0.636 | 0.641 | 1.451 |
| routeA_bm25_alias_redirect_match | 0.472 | 0.497 | 0.530 | 2.594 |
| routeA_bm25_disambiguation_title_match | 0.483 | 0.505 | 0.538 | 2.568 |

Caption:
The main gain of metadata-aware reranking is budget-preserving early evidence access: candidate generation is unchanged, but reciprocal rank and discount-aware ranking quality improve.

## Table 3. Diagnosis-oriented claim-type summary

| variant | dominant improved claim types | dominant regression signal | interpretation |
| --- | --- | --- | --- |
| routeA_bm25_title_overlap | plain entity surface, some type-word claims | rare plain lexical confusions | conservative lexical metadata cue |
| routeA_bm25_exact_title_boost | plain entity surface, some type-word claims | stronger exact-match over-promotion | strongest aggressive cue |
| routeA_bm25_disambiguation_title_match | type-word claims, parenthetical surface cues | type-sensitive overfiring | diagnosis support for disambiguation-sensitive ranking |
| routeA_bm25_alias_redirect_match | negligible | noisy alias-like surface matches | negative control rather than positive contribution |

Caption:
The upgraded paper should emphasize not only aggregate gain but also which claim patterns benefit from different metadata cues.

## Table 4. Title-overlap vs exact-title comparison

| variant | strict top1 hits | strict top1 delta vs BM25 | strict improved / regressed | relaxed top1 hits |
| --- | ---: | ---: | ---: | ---: |
| routeA_bm25 | 368 | 0 | 0 / 0 | 737 |
| routeA_bm25_title_overlap | 415 | 47 | 49 / 2 | 760 |
| routeA_bm25_exact_title_boost | 544 | 176 | 192 / 16 | 801 |

Caption:
The paper should no longer claim that title overlap is the strongest variant. Instead, title overlap should be positioned as the conservative family member, while exact title boost is the strongest tested aggressive variant.
