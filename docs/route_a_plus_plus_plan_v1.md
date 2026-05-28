# Route A++ Plan v1

## Goal

Route A++ does not change the model stack. Its purpose is to make the Route A problem thicker and more benchmark-like while keeping the same task definition.

## Target Scale

- target query scale: `120-180`
- target event scale: `40-60`
- fixed split design:
  - `dev`
  - `test`

## Required Case Coverage

All three case types must remain balanced:

- `clear_updated_vs_stale`
- `reliability_sensitive_conflict`
- `mixed_ambiguous_case`

## Fixed Split Policy

Route A++ must freeze a `dev / test` split now and not change it later. The split is for stable reporting and future reproducibility, not for broad hyperparameter search.

## Required Main Comparisons

The Route A++ main experiment must include:

- `retrieval_only`
- `recency_only`
- `reliability_only`
- `temporal_only`
- `temporal_plus_reliability`
- `case_aware_non_graph_rerank`

## Minimum Success Standard

- total query count within `120-180`
- both `dev` and `test` cover all three case types
- `temporal` shows independent gain over `retrieval_only`
- `reliability` shows independent gain over `retrieval_only`
- `temporal_plus_reliability` outperforms naive priors
- `mixed` remains the main value region rather than disappearing from the task
- the resulting package is thick enough to stand as the main Route A paper method

## Route A++ Does Not Do

- no new model
- no Route B or Route C expansion
- no generation
- no large benchmark migration
- no large sweep
