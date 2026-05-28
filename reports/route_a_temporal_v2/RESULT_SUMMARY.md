# Result Summary

| stage | preferred top1 | pairwise success | mean preferred rank | preferred MRR | stale wins |
| --- | ---: | ---: | ---: | ---: | ---: |
| retrieval_only | 0.500 | 0.667 | 1.533 | 0.744 | 10 |
| temporal_only | 0.667 | 0.800 | 1.367 | 0.828 | 6 |
| temporal_plus_reliability | 0.800 | 0.800 | 1.200 | 0.900 | 6 |

## Delta vs Retrieval-Only

- temporal-only pairwise delta: `0.133`
- final pairwise delta: `0.133`
- temporal changed ranking count: `5`
- reliability helped count: `5`
- final better than retrieval count: `10`