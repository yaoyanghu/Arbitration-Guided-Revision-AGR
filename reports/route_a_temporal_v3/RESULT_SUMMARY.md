# Result Summary

| stage | preferred top1 | pairwise success | mean preferred rank | preferred MRR | stale wins |
| --- | ---: | ---: | ---: | ---: | ---: |
| retrieval_only | 0.537 | 0.667 | 1.500 | 0.762 | 18 |
| temporal_only | 0.704 | 0.796 | 1.333 | 0.846 | 11 |
| temporal_plus_reliability | 0.815 | 0.833 | 1.185 | 0.907 | 9 |

## Delta vs Retrieval-Only

- temporal-only pairwise delta: `0.130`
- final pairwise delta: `0.167`
- temporal changed ranking count: `9`
- reliability helped count: `8`
- final better than retrieval count: `17`