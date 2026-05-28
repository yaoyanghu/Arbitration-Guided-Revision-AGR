# Route B Graph v3 Holdout Result Summary

## Holdout Scope

- Held-out hard subset size: 24 queries
- Case types covered: clear updated-vs-stale, reliability-sensitive conflict, mixed ambiguous case
- No edge-rule tuning was done on this held-out set

## Route A vs Route B

| setting | preferred top1 | pairwise success | mean preferred rank | preferred MRR | stale wins |
| --- | ---: | ---: | ---: | ---: | ---: |
| route_a_final | 0.833 | 0.875 | 1.167 | 0.917 | 3 |
| route_b_graph | 1.000 | 1.000 | 1.000 | 1.000 | 0 |

## Matched Baselines

| setting | preferred top1 | pairwise success | mean preferred rank | preferred MRR | improved | regressed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| a_only | 0.833 | 0.875 | 1.167 | 0.917 | 0 | 0 |
| update_only | 0.958 | 1.000 | 1.042 | 0.979 | 3 | 0 |
| case_aware_non_graph | 1.000 | 1.000 | 1.000 | 1.000 | 4 | 0 |
| full_graph | 1.000 | 1.000 | 1.000 | 1.000 | 4 | 0 |

## Graph Snapshot

- Queries with graphs: 24
- Relation counts: `support=40`, `corroborate=48`, `update=16`, `contradict=40`
- Improved over Route A final: 4
- Regressed: 0
- No-change: 20

## Bottom Line

- The current Route B prototype still has net gain over Route A alone on the held-out hard subset.
- The graph is stronger than `update_only`.
- But the graph does **not** beat the matched `case_aware_non_graph` baseline.
- So this held-out result does **not** yet prove independent graph value; it supports a stronger conflict-aware aggregator, not necessarily a uniquely graph-based method.
