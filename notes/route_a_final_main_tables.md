# Route A Final Main Tables

## Table 1. Route A v3 Mainline Results

| Stage | Preferred Top1 | Pairwise Success | Mean Preferred Rank | Preferred MRR | Stale Wins |
| --- | ---: | ---: | ---: | ---: | ---: |
| Retrieval-only | 0.537 | 0.667 | 1.500 | 0.762 | 18 |
| Temporal-only | 0.704 | 0.796 | 1.333 | 0.846 | 11 |
| Temporal + Reliability | 0.815 | 0.833 | 1.185 | 0.907 | 9 |

Caption draft:
Route A v3 mainline results on the 54-query balanced temporal-conflict slice. Lightweight temporal reranking improves over retrieval-only BM25, and adding a small source-reliability prior yields a further gain.

## Table 2. Held-out Robustness Confirmation

| Stage | Preferred Top1 | Pairwise Success | Mean Preferred Rank | Preferred MRR | Stale Wins |
| --- | ---: | ---: | ---: | ---: | ---: |
| Retrieval-only | 0.500 | 0.667 | 1.500 | 0.750 | 6 |
| Temporal-only | 0.722 | 0.778 | 1.278 | 0.861 | 4 |
| Temporal + Reliability | 0.833 | 0.889 | 1.167 | 0.917 | 2 |

Caption draft:
Held-out robustness confirmation on an 18-query temporal-conflict slice built under the same Route A contract. This table is not a second mainline experiment; it only confirms that the Route A pattern remains intact on a fresh slice.

## Table 3. Stratified Case-Type Results On Route A v3

| Stage | Case Type | Preferred Top1 | Pairwise Success | Mean Preferred Rank | Preferred MRR | Improved | Regressed |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Retrieval-only | Clear | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 0 |
| Retrieval-only | Reliability-sensitive | 0.611 | 1.000 | 1.389 | 0.806 | 0 | 0 |
| Retrieval-only | Mixed | 0.000 | 0.000 | 2.111 | 0.481 | 0 | 0 |
| Temporal-only | Clear | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 0 |
| Temporal-only | Reliability-sensitive | 0.722 | 1.000 | 1.278 | 0.861 | 2 | 0 |
| Temporal-only | Mixed | 0.389 | 0.389 | 1.722 | 0.676 | 7 | 0 |
| Temporal + Reliability | Clear | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 0 |
| Temporal + Reliability | Reliability-sensitive | 0.944 | 1.000 | 1.056 | 0.972 | 6 | 0 |
| Temporal + Reliability | Mixed | 0.500 | 0.500 | 1.500 | 0.750 | 11 | 0 |

Caption draft:
Case-type stratified results on the Route A v3 mainline slice. Clear updated-vs-stale cases are already easy for BM25, while reliability-sensitive and mixed cases provide the main room for improvement.
