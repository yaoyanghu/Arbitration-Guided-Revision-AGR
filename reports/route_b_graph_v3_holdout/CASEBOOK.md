# Route B Graph v3 Holdout Casebook

## Improved Cases

- `h3_002_reliability`: Route A final rank `2` -> graph rank `1`
- `h3_002_mixed`: Route A final rank `2` -> graph rank `1`
- `h3_004_mixed`: Route A final rank `2` -> graph rank `1`
- `h3_006_mixed`: Route A final rank `2` -> graph rank `1`

## Regressed Cases

- None

## Pattern Readout

- `clear_updated_vs_stale`: graph behavior is mostly neutral because Route A final is already near-perfect.
- `reliability_sensitive_conflict`: graph helps on one held-out case, but this gain is reproducible by the matched non-graph aggregator.
- `mixed_ambiguous_case`: graph helps most often here, but the same gains are also reproduced by the matched non-graph baseline.

## Interpretation

- The graph is not empty and does create interpretable relation structure on the hold-out split.
- However, the practical gains observed in this split are not uniquely graph-dependent.
- The current evidence supports a conflict-aware structured reranker, but not yet an independent graph-method claim.
