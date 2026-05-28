# Formal Mainline Table Pack

## Table 1. HOH Main Result

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| stronger_retrieval_template | 0.168 | 0.250 | 0.947 |
| no_temporal | 0.181 | 0.268 | 0.947 |
| no_conflict | 0.181 | 0.270 | 0.945 |
| full_model | 0.188 | 0.279 | 0.945 |

Caption draft:

- Main answer-level result on HOH. The frozen full model combines stronger retrieval, temporal-aware answer extraction, and conflict-aware evidence arbitration. Source/reliability is excluded from the formal main claim because it did not show independent gains in targeted pilots.

## Table 2. TempRAGEval Auxiliary Result

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| stronger_retrieval_template | 0.061 | 0.092 | 0.131 |
| no_temporal | 0.048 | 0.083 | 0.131 |
| full_model | 0.061 | 0.092 | 0.132 |

Caption draft:

- Temporal auxiliary validation on TempRAGEval. The full model preserves a temporal advantage over the no-temporal ablation, while conflict and source are not claimed as independently validated on this dataset.

## Table 3. FEVER Controlled Auxiliary Retrieval

| setting | strict @1 | strict @5 | strict @10 | relaxed @1 | relaxed @5 | relaxed @10 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline BM25 | 0.368 | 0.627 | 0.720 | 0.737 | 0.883 | 0.918 |
| BM25 + title overlap rerank | 0.415 | 0.680 | 0.720 | 0.760 | 0.895 | 0.918 |

Caption draft:

- Controlled auxiliary retrieval benchmark preserved from the legacy FEVER line. This table supports retrieval benchmarking continuity and is not mixed into the answer-level mainline claim.
