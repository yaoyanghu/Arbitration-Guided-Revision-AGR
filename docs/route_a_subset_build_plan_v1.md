# Route A Subset Build Plan v1

## Goal

Build a small but real `temporal-conflict subset` that gives the Route A temporal and reliability modules something non-trivial to decide.

Grounding sources checked:

- [README.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v1/README.md)
- [subset_design.md](D:/HUYAOYANG/Work/ChronoRAG/runs/fever_hetero_subset_route_a/subset_design.md)
- [analysis_summary.md](D:/HUYAOYANG/Work/ChronoRAG/runs/fever_hetero_subset_route_a/analysis_summary.md)
- [analysis_summary.md](D:/HUYAOYANG/Work/ChronoRAG/runs/fever_real_subset_route_a/analysis_summary.md)
- project book notes about `time_label` and `source_meta`

## 1. Best Initial Data Source

### Recommended source

- start from a curated subset derived from the existing heterogeneous-source Route A idea, but rebuild it around explicit `updated vs stale` preference pairs

Why:

- the heterogeneous-source subset already demonstrated that the repository can hold multiple source types for the same entity
- but it did not create real temporal-conflict pressure
- the next subset should therefore keep the multi-source idea while adding explicit time-preference structure

### Practical V1 construction strategy

Use:

- real FEVER claims or FEVER-like entity-focused claim forms as the query side
- paired evidence candidates that differ in update recency or state validity

Candidate pair patterns:

- older summary vs newer summary
- encyclopedic page snapshot vs structured KB entry with newer value
- stale status statement vs updated status statement
- current page vs disambiguation-like or legacy page whose wording reflects an older state

## 2. Per-Sample Required Fields

Each sample should contain:

- `id`
- `query`
- `entity`
- `focus_attribute`
- `query_time`
- `preferred_doc_id`
- `preferred_title`
- `preferred_reason`
- `stale_doc_ids`
- `candidate_doc_ids`
- `source_dataset`

Each candidate evidence item should contain:

- `query_id`
- `doc_id`
- `title`
- `text`
- `source`
- `source_type`
- `timestamp`
- `evidence_time`
- `temporal_status`
- `reliability_bucket`
- `pair_role`
- `is_gold_preferred`

## 3. How to Label Updated / Stale / Conflicting

### `updated`

Assign when:

- the candidate clearly matches the target time or latest intended state in the query
- or the candidate is the designated preferred record in an update pair

### `stale`

Assign when:

- the candidate refers to an older state of the same entity/attribute
- and the task contract says the newer state should win

### `conflicting`

Assign when:

- the candidate asserts a competing incompatible state rather than merely an older version

### `unknown_time`

Assign when:

- no reliable temporal signal is available, but the candidate remains part of the comparison set

## 4. Minimal Sample Scale

Recommended V1 size:

- `30-60 queries`

Reason:

- large enough to expose repeated behavior patterns
- small enough for manual audit and casebook writing
- appropriate for a first acceptance-stage Route A benchmark

Suggested composition:

- at least `20` clear updated-vs-stale pairs
- at least `10` reliability-sensitive conflicts
- at least `10` mixed or ambiguous cases

## 5. What Can Be Reused Directly

Directly reusable from the current repo:

- BM25 retrieval backbone
- retrieval result schema with `query/title/doc_id/text/source/timestamp/bm25_score`
- temporal score slot
- reliability score slot
- rerank fusion logic
- per-query analysis and artifact conventions

Can also reuse:

- subset naming discipline from `fever_hetero_subset_route_a`
- output structure already used under `runs/`

## 6. What Must Be Added

Must be newly added for this subset:

- explicit `query_time`
- explicit `temporal_status`
- explicit `pair_role`
- explicit `is_gold_preferred`
- explicit stale-vs-updated comparison target

Recommended additions:

- `preferred_reason`
- `source_type`
- `conflict_relation`

## 7. Why This Subset Is Better Than Existing Ones

Existing Route A subsets are not sufficient because:

- BM25 is already correct too often
- many examples have no meaningful temporal tension
- source differences often do not matter under the current page-hit metric

The new subset should therefore be designed so that:

- retrieval alone is not always enough
- temporal cues can change pairwise ordering
- reliability priors can help when multiple candidates remain plausible

## 8. Build Recommendation

For V1, prefer:

- a hand-auditable curated jsonl subset

over:

- a large automatically mined dataset

because the current goal is acceptance-stage proof of Route A usefulness, not benchmark scale.
