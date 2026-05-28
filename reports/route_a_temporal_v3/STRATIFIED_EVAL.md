# Stratified Eval

| stage | case_type | preferred top1 | pairwise success | mean preferred rank | preferred MRR | improved | regressed |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| retrieval_only | clear_updated_vs_stale | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 0 |
| retrieval_only | reliability_sensitive_conflict | 0.611 | 1.000 | 1.389 | 0.806 | 0 | 0 |
| retrieval_only | mixed_ambiguous_case | 0.000 | 0.000 | 2.111 | 0.481 | 0 | 0 |
| temporal_only | clear_updated_vs_stale | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 0 |
| temporal_only | reliability_sensitive_conflict | 0.722 | 1.000 | 1.278 | 0.861 | 2 | 0 |
| temporal_only | mixed_ambiguous_case | 0.389 | 0.389 | 1.722 | 0.676 | 7 | 0 |
| temporal_plus_reliability | clear_updated_vs_stale | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 0 |
| temporal_plus_reliability | reliability_sensitive_conflict | 0.944 | 1.000 | 1.056 | 0.972 | 6 | 0 |
| temporal_plus_reliability | mixed_ambiguous_case | 0.500 | 0.500 | 1.500 | 0.750 | 11 | 0 |

## Readout

- query_count: `54`
- temporal changed ranking count: `9`
- reliability helped count: `8`