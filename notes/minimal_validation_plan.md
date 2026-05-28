# Validation Status

## Status

- The old overlap problem has been repaired.
- The `disjoint 1000 validation` run has been completed.
- The main validation result should now use `fever_official_route_a_disjoint_1000`, not the older overlapping `fever_official_route_a_1000`.

## Completed Artifacts

- `data/processed/fever_official/shared_task_dev_disjoint_1000.jsonl`
- `runs/fever_official_route_a_disjoint_1000/metrics.json`
- `runs/fever_official_route_a_disjoint_1000/official_strict_eval_results.json`
- `runs/fever_official_route_a_disjoint_1000/official_labelwise_results.json`
- `runs/fever_official_route_a_disjoint_1000/official_strict_improved_cases.jsonl`
- `runs/fever_official_route_a_disjoint_1000/official_strict_regressed_cases.jsonl`

## Decision

- Keep the old follow-up 1000 result as auxiliary context only.
- Use the new disjoint 1000 result as the main validation evidence in the paper.
- No new weight sweep is needed before drafting.

## Remaining Optional Work

- full-dev rerun for stronger external validity
- repeated random seeds for variance reporting
- cleaner paper-ready automation for table regeneration

These are useful extensions, but they are not required before starting the first draft of a focused small paper on lightweight reranking for evidence retrieval.
