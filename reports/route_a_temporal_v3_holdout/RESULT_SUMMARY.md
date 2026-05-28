# Route A v3 Holdout Result Summary

## Scope

- held-out slice size: `18` queries
- case types: balanced `clear / reliability-sensitive / mixed`
- this slice was not used to define the Route A v3 mainline checkpoint

## Metrics

| stage | preferred top1 | pairwise success | mean preferred rank | preferred MRR | stale wins |
| --- | ---: | ---: | ---: | ---: | ---: |
| retrieval_only | 0.500 | 0.667 | 1.500 | 0.750 | 6 |
| temporal_only | 0.722 | 0.778 | 1.278 | 0.861 | 4 |
| temporal_plus_reliability | 0.833 | 0.889 | 1.167 | 0.917 | 2 |

## Readout

- Route A still satisfies `retrieval_only < temporal_only <= temporal_plus_reliability`
- temporal signal still changes ranking behavior
- reliability prior still provides additional help on a small held-out slice
- the held-out numbers are slightly stronger than the mainline package, which is consistent with this slice being smaller and cleaner
