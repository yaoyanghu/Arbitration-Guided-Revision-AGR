# Route A Task Contract v1

## Scope

This contract defines the first real evaluable task for ChronoRAG Route A.

It is separate from the FEVER short paper line.

It does not cover:

- Route B
- Route C
- generation
- sentence-level attribution
- dense retrieval

Grounding sources checked:

- [README.md](D:/HUYAOYANG/Work/ChronoRAG/README.md)
- [README.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v1/README.md)
- [label_relation.py](D:/HUYAOYANG/Work/ChronoRAG/src/temporal/label_relation.py)
- [source_score.py](D:/HUYAOYANG/Work/ChronoRAG/src/reliability/source_score.py)
- [eval_main.py](D:/HUYAOYANG/Work/ChronoRAG/src/eval/eval_main.py)
- [subset_design.md](D:/HUYAOYANG/Work/ChronoRAG/runs/fever_hetero_subset_route_a/subset_design.md)
- local project book copy at `reports/route_a_temporal_v1/_tmp_project_book_copy.docx`

## 1. Task Definition

Route A V1 task:

- given a claim-like query and a small candidate set containing temporally conflicting or differently updated evidence candidates,
- rank candidates so that more current and more reliable evidence is preferred over stale or weaker evidence,
- while keeping the pipeline fully inspectable at the per-query level.

This is not a generic FEVER retrieval task.

This is a `temporal-conflict retrieval-and-reranking` task.

## 2. Dataset Candidate

### Primary choice

- a curated `temporal-conflict subset` built from current repository assets plus a small amount of structured augmentation

Why this is the right first choice:

- current FEVER subsets in this repo are real, but they do not create enough true updated-vs-stale tension
- current Route A runs show zero measurable temporal gain because the subset does not force the temporal module to decide anything meaningful
- the Route A README explicitly allows a `small but real temporal-conflict benchmark or curated subset`

### What counts as acceptable for V1

- the query must be real or grounded in real entities
- at least two candidate evidence items must be in meaningful preference tension
- one candidate must be markable as `updated-preferred` over another `stale` or `less-current` candidate

## 3. Query Schema

Each query record should contain at least:

- `id`
- `query`
- `query_type`
- `entity`
- `focus_attribute`
- `claim_time` or `query_time`
- `gold_preferred_doc_id`
- `gold_preferred_title`
- `comparison_group_id`

Recommended optional fields:

- `claim`
- `gold_preference_reason`
- `source_dataset`
- `notes`

## 4. Evidence Schema

Each candidate evidence item should contain at least:

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
- `is_gold_preferred`

Recommended optional fields:

- `page_id`
- `section`
- `url`
- `version_note`
- `conflict_relation`

## 5. Temporal Label Definition

For V1 the temporal label set should stay minimal and task-facing:

- `updated`
  - this candidate better reflects the query target time or the latest valid state
- `stale`
  - this candidate reflects an older state that should lose to the updated candidate
- `conflicting`
  - this candidate asserts a competing state that is not merely older but directionally inconsistent
- `unknown_time`
  - insufficient time information for confident temporal judgment
- `non_temporal`
  - candidate is relevant but does not express useful update status

Important constraint:

- V1 does not need a full support/contradict/update taxonomy at the sentence level
- V1 only needs enough temporal labeling to judge `updated-preferred vs stale`

## 6. Stale vs Updated Success Criterion

The primary Route A success criterion is:

- when a query has both a stale candidate and an updated-preferred candidate in the retrieved set, the updated-preferred candidate should rank above the stale candidate

This should be measured at least at:

- top1 preference success
- pairwise win rate
- mean preferred rank

Recommended derived labels:

- `preference_success`
  - updated-preferred candidate ranks above all stale competitors
- `partial_success`
  - updated-preferred candidate moves up, but not to the desired rank
- `failure_stale_wins`
  - stale candidate still outranks updated-preferred evidence

## 7. Reliability Label / Prior Definition

Route A V1 reliability should remain lightweight and explicit.

Recommended source prior buckets:

- `official_record`
- `encyclopedic_current`
- `news_report`
- `archival_or_old_news`
- `structured_kb`
- `unknown`

For the first prototype, the reliability label can be assigned either:

- directly in the curated subset, or
- through a simple mapping from `source` / `source_type`

The key principle is:

- reliability is only a prior, not a learned truth estimator

## 8. Evaluation Metrics

### Primary metrics

- updated-over-stale pairwise win rate
- updated candidate top1 rate
- preferred evidence mean rank
- preferred evidence MRR

### Secondary metrics

- temporal signal changed ranking count
- reliability changed ranking count
- final rerank improvement over retrieval-only baseline
- per-query artifact coverage

### Diagnostic metrics

- stale-wins failure count
- temporal false-positive reorder count
- reliability-overrides-temporal count

## 9. Minimum Success Standard

The Route A README lists 5 acceptance criteria. The contract translates them into concrete checks:

### Acceptance 1

- pipeline runs end-to-end on a small but real temporal-conflict subset

Concrete check:

- one command produces retrieval, temporal-scored, reliability-scored, reranked, and evaluated outputs on a non-demo subset

### Acceptance 2

- temporal signal changes ranking behavior in a measurable way

Concrete check:

- temporal scoring changes at least some top-k or pairwise orderings, and these changes are recorded in per-query artifacts

### Acceptance 3

- updated evidence beats retrieval-only baseline often enough

Concrete check:

- final or temporal-only ranking improves updated-over-stale preference relative to retrieval-only baseline on the curated subset

### Acceptance 4

- source reliability helps at least some conflict cases

Concrete check:

- reliability changes the outcome in at least a small number of conflict cases in an inspectably sensible direction

### Acceptance 5

- outputs are inspectable

Concrete check:

- every query has readable artifacts showing raw score, temporal score, reliability score, final score, and ranking movement

## 10. Why Existing Route A Subsets Are Not Enough

Current repository evidence shows that:

- [analysis_summary.md](D:/HUYAOYANG/Work/ChronoRAG/runs/fever_hetero_subset_route_a/analysis_summary.md)
- [analysis_summary.md](D:/HUYAOYANG/Work/ChronoRAG/runs/fever_real_subset_route_a/analysis_summary.md)

both produce:

- no temporal improvements
- no reliability improvements

So Route A V1 should not be judged against those old subsets alone.

The contract therefore requires a new curated subset whose structure actually exposes temporal-conflict decisions.
