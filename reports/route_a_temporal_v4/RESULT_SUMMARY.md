# Route A v4 Result Summary

## Dev

| setting | preferred top1 | pairwise success | mean preferred rank | preferred MRR | stale wins |
| --- | ---: | ---: | ---: | ---: | ---: |
| retrieval_only | 0.617 | 0.667 | 1.400 | 0.806 | 20 |
| recency_only | 0.783 | 0.833 | 1.233 | 0.889 | 10 |
| reliability_only | 0.733 | 0.733 | 1.267 | 0.867 | 16 |
| temporal_only | 0.950 | 0.967 | 1.050 | 0.975 | 2 |
| temporal_plus_reliability | 0.917 | 0.917 | 1.083 | 0.958 | 5 |
| case_aware_non_graph_rerank | 1.000 | 1.000 | 1.000 | 1.000 | 0 |

## Test

| setting | preferred top1 | pairwise success | mean preferred rank | preferred MRR | stale wins |
| --- | ---: | ---: | ---: | ---: | ---: |
| retrieval_only | 0.583 | 0.667 | 1.467 | 0.783 | 20 |
| recency_only | 0.683 | 0.767 | 1.367 | 0.833 | 14 |
| reliability_only | 0.683 | 0.683 | 1.317 | 0.842 | 19 |
| temporal_only | 0.900 | 0.933 | 1.100 | 0.950 | 4 |
| temporal_plus_reliability | 0.817 | 0.833 | 1.183 | 0.908 | 10 |
| case_aware_non_graph_rerank | 1.000 | 1.000 | 1.000 | 1.000 | 0 |

## Readout

- temporal independent gain on test: `yes`
- reliability independent gain on test: `yes`
- temporal + reliability beats naive priors on test: `yes`
- case-aware non-graph beats temporal + reliability on test: `yes`