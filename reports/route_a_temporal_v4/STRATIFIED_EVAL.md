# Route A v4 Stratified Eval

| setting | case_type | preferred top1 | pairwise success | mean preferred rank | preferred MRR | improved | regressed |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| retrieval_only | clear_updated_vs_stale | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 0 |
| retrieval_only | reliability_sensitive_conflict | 0.750 | 1.000 | 1.250 | 0.875 | 0 | 0 |
| retrieval_only | mixed_ambiguous_case | 0.000 | 0.000 | 2.150 | 0.475 | 0 | 0 |
| recency_only | clear_updated_vs_stale | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 0 |
| recency_only | reliability_sensitive_conflict | 0.750 | 1.000 | 1.250 | 0.875 | 0 | 0 |
| recency_only | mixed_ambiguous_case | 0.300 | 0.300 | 1.850 | 0.625 | 6 | 0 |
| reliability_only | clear_updated_vs_stale | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 0 |
| reliability_only | reliability_sensitive_conflict | 1.000 | 1.000 | 1.000 | 1.000 | 5 | 0 |
| reliability_only | mixed_ambiguous_case | 0.050 | 0.050 | 1.950 | 0.525 | 4 | 0 |
| temporal_only | clear_updated_vs_stale | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 0 |
| temporal_only | reliability_sensitive_conflict | 0.900 | 1.000 | 1.100 | 0.950 | 3 | 0 |
| temporal_only | mixed_ambiguous_case | 0.800 | 0.800 | 1.200 | 0.900 | 17 | 0 |
| temporal_plus_reliability | clear_updated_vs_stale | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 0 |
| temporal_plus_reliability | reliability_sensitive_conflict | 0.950 | 1.000 | 1.050 | 0.975 | 4 | 0 |
| temporal_plus_reliability | mixed_ambiguous_case | 0.500 | 0.500 | 1.500 | 0.750 | 12 | 0 |
| case_aware_non_graph_rerank | clear_updated_vs_stale | 1.000 | 1.000 | 1.000 | 1.000 | 0 | 0 |
| case_aware_non_graph_rerank | reliability_sensitive_conflict | 1.000 | 1.000 | 1.000 | 1.000 | 5 | 0 |
| case_aware_non_graph_rerank | mixed_ambiguous_case | 1.000 | 1.000 | 1.000 | 1.000 | 20 | 0 |