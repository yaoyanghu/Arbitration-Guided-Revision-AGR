# Stratified Eval

| setting | case_type | preferred top1 | pairwise success | mean preferred rank | preferred MRR | improved | regressed |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| a_only | clear_updated_vs_stale | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 0 |
| a_only | reliability_sensitive_conflict | 0.875 | 1.000 | 1.125 | 0.938 | 0 | 0 |
| a_only | mixed_ambiguous_case | 0.625 | 0.625 | 1.375 | 0.812 | 0 | 0 |
| update_only | clear_updated_vs_stale | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 0 |
| update_only | reliability_sensitive_conflict | 0.875 | 1.000 | 1.125 | 0.938 | 0 | 0 |
| update_only | mixed_ambiguous_case | 1.000 | 1.000 | 1.000 | 1.000 | 3 | 0 |
| case_aware_non_graph | clear_updated_vs_stale | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 0 |
| case_aware_non_graph | reliability_sensitive_conflict | 1.000 | 1.000 | 1.000 | 1.000 | 1 | 0 |
| case_aware_non_graph | mixed_ambiguous_case | 1.000 | 1.000 | 1.000 | 1.000 | 3 | 0 |
| full_graph | clear_updated_vs_stale | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 0 |
| full_graph | reliability_sensitive_conflict | 1.000 | 1.000 | 1.000 | 1.000 | 1 | 0 |
| full_graph | mixed_ambiguous_case | 1.000 | 1.000 | 1.000 | 1.000 | 3 | 0 |

## Readout

- graph 的收益是不是主要只在 mixed cases: 看 `full_graph` 相对其他 setting 在 `mixed_ambiguous_case` 上的 improved / regressed。
- clear / reliability-sensitive 上 graph 是否只是中性: 看 `clear_updated_vs_stale` 与 `reliability_sensitive_conflict` 的 full_graph 与 matched baselines 差值。
- 如果 graph 只对 mixed cases 有用，它仍可以支持一个 conflict-focused Route B 定位，但不足以支撑更一般化的 graph retrieval claim。