# Route B Graph v2 Result Summary

| stage | preferred top1 | pairwise success | mean preferred rank | preferred MRR | stale wins |
| --- | ---: | ---: | ---: | ---: | ---: |
| route_a_final | 0.800 | 0.800 | 1.200 | 0.900 | 6 |
| route_b_graph | 1.000 | 1.000 | 1.000 | 1.000 | 0 |

## Graph Snapshot

- queries with nonempty graph: `30`
- relation type counts: `{'support': 50, 'corroborate': 60, 'update': 20, 'contradict': 50}`
- improved count: `6`
- regressed count: `0`
- no-change count: `24`

## Diversity Readout

- clear-case dominant pattern: `{'support': 1, 'corroborate': 1, 'update': 1, 'contradict': 2}`
- reliability-case dominant pattern: `{'support': 2, 'corroborate': 2, 'contradict': 1}`
- mixed-case dominant pattern: `{'support': 2, 'corroborate': 3, 'update': 1, 'contradict': 2}`
- unique pattern count: `3`
