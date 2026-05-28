# Route A Hardening Plan v1

## Purpose

This plan defines how Route A should move from the accepted 12-query curated subset to a stronger pre-Route-B checkpoint.

Grounding sources checked:

- [route_a_task_contract_v1.md](D:/HUYAOYANG/Work/ChronoRAG/docs/route_a_task_contract_v1.md)
- [route_a_subset_build_plan_v1.md](D:/HUYAOYANG/Work/ChronoRAG/docs/route_a_subset_build_plan_v1.md)
- [ACCEPTANCE_CHECK.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v1/ACCEPTANCE_CHECK.md)
- [CASEBOOK.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v1/CASEBOOK.md)
- [ERROR_TAXONOMY.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v1/ERROR_TAXONOMY.md)
- [NEXT_STEP_DECISION.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v1/NEXT_STEP_DECISION.md)
- [README.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v1/README.md)
- [capability_boundary.md](D:/HUYAOYANG/Work/ChronoRAG/docs/capability_boundary.md)

## 1. Why the 12-query subset is enough for acceptance but not enough for Route B main experiment

The 12-query `route_a_temporal_v1` subset did its job:

- it proved the Route A pipeline can run end to end
- it proved the task contract is executable
- it produced measurable temporal and reliability effects
- it generated readable per-query artifacts

But it is still not a strong enough foundation for a Route B main experiment because:

- the sample is too small to support stable graph-related conclusions
- the subset is still tightly curated and diagnosis-oriented
- capability boundary documents explicitly say current gains are pipeline diagnostics, not realistic benchmark claims
- the current Route A effect is real but narrow: only `12` queries, `2` temporal ranking changes, and `1` reliability-helped case

So the correct next step is not Route B main experiment.

The correct next step is:

- freeze v1 as the accepted checkpoint
- build a hardened `30-60` query subset
- verify that the Route A effects survive on that larger subset

## 2. How to expand to a 30-60 query real temporal-conflict subset

Recommended v2 design:

- keep the same task definition and fields
- increase to `30` queries as the first hardened milestone
- use real entities and realistic update scenarios
- keep each query attached to a small conflict set with:
  - one preferred updated candidate
  - one stale candidate
  - one conflicting or weaker-source candidate

Recommended construction pattern:

- `10` real entities
- `3` query styles per entity
- total `30` queries

This creates enough variety while still keeping the subset fully auditable.

## 3. Case Types That Must Be Covered

### A. Clear updated-vs-stale pairs

These are the minimum Route A backbone.

Needed behavior:

- stale candidate can be lexically competitive
- temporal signal should usually move the updated candidate upward

### B. Reliability-sensitive conflicts

These are the cases that justify the reliability module.

Needed behavior:

- conflicting candidate is same-year and lexically strong
- temporal signal alone is not always enough
- reliability prior should rescue at least some cases

### C. Mixed / ambiguous cases

These stop the subset from becoming too toy-like.

Needed behavior:

- not every case is cleanly solved
- some cases should remain partially ambiguous or only weakly improved
- per-query artifacts should reveal why

## 4. What Stays Fixed After Expansion

The hardened subset should keep these stable:

- query schema
- evidence schema
- updated/stale/conflicting task contract
- retrieval backbone
- temporal scoring interface
- reliability scoring interface
- reranking formula
- task-specific evaluation metrics
- per-query artifact format

That stability matters because Route A hardening should test robustness, not silently change the problem definition.

## 5. New Acceptance Gate for Hardened Route A

The hardened subset should use a stronger gate than v1.

Recommended v2 gate:

1. query count must be at least `30`
2. temporal signal must change ranking behavior on at least `5` queries
3. final pairwise preference success must beat retrieval-only baseline by at least `0.05`
4. reliability must help at least `3` queries
5. per-query artifacts must still exist for all queries

If these are not met, Route B prototype run should still wait.

## 6. Rollback and Checkpoint Policy

Route A v1 must be preserved unchanged as the rollback target:

- [route_a_temporal_v1](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v1)
- [route_a_temporal_v1](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v1)

The hardened run must use separate directories:

- `data/processed/route_a_temporal_v2_subset.jsonl`
- `data/corpus/route_a_temporal_v2_corpus.jsonl`
- `runs/route_a_temporal_v2/`
- `logs/route_a_temporal_v2/`
- `reports/route_a_temporal_v2/`

## 7. Stop Condition Before Route B

If Route A v2 shows obvious regression, work must stop in Route A and should not proceed to any Route B run.

Examples of obvious regression:

- retrieval-only, temporal-only, and final reranking collapse into nearly the same behavior
- temporal changed ranking count falls to `0`
- reliability helped count falls to `0` without a convincing subset explanation
- final pairwise preference success does not beat retrieval-only baseline
- per-query artifacts are missing or no longer readable

In that failure mode, the correct action is:

- debug the hardened subset
- debug temporal and reliability scoring behavior
- rerun Route A only

Do not enter Route B until Route A v2 is stable.

## 8. Route B Consequence

Only after the hardened Route A gate passes should Route B move from planning to a minimal prototype run.

Even then:

- only a minimal local graph over Route A top-k results should be attempted
- no Route B main experiment should start immediately
