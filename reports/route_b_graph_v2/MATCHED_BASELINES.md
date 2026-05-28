# Matched Baselines

| setting | preferred top1 | pairwise success | mean preferred rank | preferred MRR | improved | regressed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| a_only | 0.800 | 0.800 | 1.200 | 0.900 | 0 | 0 |
| update_only | 1.000 | 1.000 | 1.000 | 1.000 | 6 | 0 |
| case_aware_non_graph | 1.000 | 1.000 | 1.000 | 1.000 | 6 | 0 |
| full_graph | 1.000 | 1.000 | 1.000 | 1.000 | 6 | 0 |

## Readout

- graph 是否优于同信息量 non-graph 聚合器: 否
- graph 是否优于 update_only: 否
- 如果 graph 不优于 matched baselines，则当前 gain 更像 conflict-aware rule aggregation 而不是独立 graph method。