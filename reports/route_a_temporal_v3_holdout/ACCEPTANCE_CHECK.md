# Route A v3 Holdout Acceptance Check

## Scope

- held-out slice size: `18` queries
- task contract: unchanged from Route A v3
- scoring logic: unchanged from Route A v3
- stages evaluated:
  - retrieval-only
  - temporal-only
  - temporal + reliability

## Acceptance Readout

1. End-to-end held-out run completed: PASS
2. Temporal signal still measurably changes ranking: PASS
3. Updated evidence still beats retrieval-only baseline: PASS
4. Reliability still helps some conflict cases: PASS
5. Per-query inspectable artifacts exist: PASS

## Metrics Snapshot

| stage | preferred top1 | pairwise success | mean preferred rank | preferred MRR | stale wins |
| --- | ---: | ---: | ---: | ---: | ---: |
| retrieval_only | 0.500 | 0.667 | 1.500 | 0.750 | 6 |
| temporal_only | 0.722 | 0.778 | 1.278 | 0.861 | 4 |
| temporal_plus_reliability | 0.833 | 0.889 | 1.167 | 0.917 | 2 |

## Snapshot Deltas

- temporal changed ranking count: `4`
- reliability helped count: `2`
- final better than retrieval count: `6`

## Decision

The held-out slice supports the current Route A v3 mainline claim. It functions as a low-risk robustness confirmation rather than a new mainline package.
