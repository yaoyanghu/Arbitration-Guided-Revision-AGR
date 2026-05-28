# Route A v1 vs v2 Diff

## Scope Difference

Route A v1:

- `12` query curated acceptance subset
- primarily for pipeline wiring, contract validation, and controlled diagnosis

Route A v2:

- `30` query hardened temporal-conflict subset
- designed to stress retrieval, temporal reranking, and reliability weighting on a more realistic conflict pattern

## Dataset Difference

### v1

- narrower curated slice
- less explicit balancing across case families
- smaller number of reliability-sensitive and mixed hard cases

### v2

- `10` clear updated-vs-stale cases
- `10` reliability-sensitive conflict cases
- `10` mixed ambiguous cases

## Metrics Difference

| stage | v1 preferred top1 | v2 preferred top1 | v1 pairwise | v2 pairwise |
| --- | ---: | ---: | ---: | ---: |
| retrieval_only | 0.750 | 0.500 | 0.833 | 0.667 |
| temporal_only | 0.917 | 0.667 | 1.000 | 0.800 |
| temporal_plus_reliability | 1.000 | 0.800 | 1.000 | 0.800 |

## Acceptance Snapshot Difference

- temporal changed ranking count: `2 -> 5`
- reliability helped count: `1 -> 5`
- final better than retrieval count: `3 -> 10`

## Interpretation

v2 is more realistic and more demanding than v1.

The lower absolute rates in v2 do not indicate collapse.

They indicate that:

- retrieval-only is no longer over-favored by subset wording
- temporal reranking produces a measurable lift on a harder slice
- reliability now matters on more than a single case

## Explicit Answer: Is v2 actually more stable?

Yes, v2 is more stable in the sense needed for pre-Route-B decision making.

Reasons:

- it uses more queries
- it introduces balanced case families
- it preserves the same task contract and evaluation interface
- it still shows ordered behavior: `retrieval-only < temporal-only <= temporal+reliability`
- temporal and reliability effects are both measurable rather than accidental

So v2 is not just “v1 with more samples.”

It is a stronger checkpoint for deciding whether a later Route B prototype is worth attempting.
