# Route B v1 Ablation Summary

| setting | preferred top1 | pairwise success | mean preferred rank | preferred MRR | stale wins |
| --- | ---: | ---: | ---: | ---: | ---: |
| a_only | 0.800 | 0.800 | 1.200 | 0.900 | 6 |
| update_only | 1.000 | 1.000 | 1.000 | 1.000 | 0 |
| contradict_only | 0.867 | 0.867 | 1.133 | 0.933 | 4 |
| support_corroborate_only | 0.867 | 0.867 | 1.133 | 0.933 | 4 |
| full_graph | 1.000 | 1.000 | 1.000 | 1.000 | 0 |

## Readout

- If `update_only` is close to `full_graph`, most gain comes from update edges.
- If `support_corroborate_only` is near `a_only`, these edges mainly reweight existing preferences.
- If `contradict_only` barely moves results, contradiction is diagnostic but not the main driver.