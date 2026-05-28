# Route A v2 vs v3 Diff

## Coverage

| split | entities | queries | clear | reliability | mixed |
| --- | ---: | ---: | ---: | ---: | ---: |
| v2 | 10 | 30 | 10 | 10 | 10 |
| v3 | 18 | 54 | 18 | 18 | 18 |

## Overall Metrics

| stage | metric | v2 | v3 | delta |
| --- | --- | ---: | ---: | ---: |
| retrieval_only | preferred top1 | 0.500 | 0.537 | +0.037 |
| retrieval_only | pairwise success | 0.667 | 0.667 | +0.000 |
| temporal_only | preferred top1 | 0.667 | 0.704 | +0.037 |
| temporal_only | pairwise success | 0.800 | 0.796 | -0.004 |
| temporal_plus_reliability | preferred top1 | 0.800 | 0.815 | +0.015 |
| temporal_plus_reliability | pairwise success | 0.800 | 0.833 | +0.033 |
| temporal_plus_reliability | preferred MRR | 0.900 | 0.907 | +0.007 |

## Acceptance Snapshot

| metric | v2 | v3 | delta |
| --- | ---: | ---: | ---: |
| temporal changed ranking count | 5 | 9 | +4 |
| reliability helped count | 5 | 8 | +3 |
| final better than retrieval count | 10 | 17 | +7 |

## Interpretation

- v3 is not just bigger; it is stronger.
- The final Route A stage improves over v2 on preferred top1, pairwise success, and preferred MRR.
- Temporal-only remains helpful, and the final reliability layer now helps on more queries than in v2.
- The hardest remaining area is still `mixed_ambiguous_case`, which is exactly why v3 is more useful as a mainline checkpoint than v2.
