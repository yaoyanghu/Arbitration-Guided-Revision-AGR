# Implementation Plan: Metadata Family

## Scope

This plan covers only lightweight FEVER retrieval analysis additions.

Out of scope:

- Route B and Route C
- generation
- GraphRAG
- dense retrieval
- full-dev reruns

## 1. Code That Can Be Reused

### Existing retrieval and ranking base

- `src/retrieval/search.py`
  - confirms the retrieval outputs already expose `query`, `title`, `doc_id`, `text`, `source`, `timestamp`, and `bm25_score`
- `src/analysis/official_title_overlap_improvement.py`
  - already contains `normalize_bm25`, `base_title`, and `title_overlap_score`
- `src/analysis/official_strict_revalidation.py`
  - already contains `strict_hit`, `relaxed_hit`, `group_by_query`, and `compute_metrics`
- `src/analysis/nearest_title_baseline_eval.py`
  - already contains a reusable exact-title-style feature and a multi-variant evaluation pattern

### Existing result anchors

- `runs/fever_official_route_a_disjoint_1000/`
- `runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/`

These existing run directories are sufficient for low-risk family evaluation because they already include:

- `retrieval_results.jsonl`
- `predictions.jsonl`
- strict and relaxed result files

## 2. What Should Be Added

### New analysis script

- `src/analysis/metadata_family_eval.py`

Responsibilities:

- build and compare metadata-aware variants over the existing disjoint 1000 retrieval results
- reuse normalized BM25 and current strict/relaxed evaluation
- write per-variant reranked outputs and summary artifacts into a new run directory

### New efficiency script

- `src/analysis/efficiency_frontier_eval.py`

Responsibilities:

- compute MRR
- compute nDCG@5 and nDCG@10
- compute first-hit-rank summary
- compute fixed page-budget success at 1, 3, 5, 10
- write JSON and Markdown summaries

## 3. Functions That Should Be Added

Inside `metadata_family_eval.py`:

- text normalization helper for phrase-level matching
- alias-like surface extractor from `text`
- `exact_title_boost_score`
- `alias_redirect_match_score`
- `disambiguation_title_match_score`
- generic rerank builder that fuses `bm25_score_norm + metadata_score`
- per-variant case comparison helper
- lightweight claim-type tagging for summary only

Inside `efficiency_frontier_eval.py`:

- binary relevance vector builder for strict and relaxed matching
- reciprocal-rank calculator
- nDCG calculator
- first-hit-rank summary calculator
- fixed-budget success calculator

## 4. What Should Stay Light

- do not modify `src/eval/eval_main.py`
- do not modify `src/retrieval/search.py`
- do not modify Route A/B/C shell scripts
- do not thread new metadata features into the main pipeline yet

Reason:

- the short paper only needs analysis-stage support on top of an existing disjoint run
- keeping changes local to `src/analysis/` minimizes risk

## 5. Naming and Output Paths

### Run directory

- `runs/fever_metadata_family_v1/`

### Log directory

- `logs/fever_metadata_family_v1/`

### Report directory

- `reports/fever_metadata_family_v1/`

### Expected artifacts

- per-variant reranked jsonl files
- `family_results.json`
- `family_summary.md`
- `efficiency_results.json`
- `efficiency_summary.md`
- `RESULT_SUMMARY.md`

## 6. Data-Field Constraints

Current stable fields visible in local run artifacts:

- query side: `query`, `claim`, `gold_label`, `gold_evidence`
- candidate side: `title`, `doc_id`, `text`, `bm25_score`

Important limitation:

- the local workspace does not currently expose the processed disjoint query file needed for an easy sentence-level evidence-coverage calculation
- therefore `gold evidence sentence coverage` should be treated as optional and likely deferred unless a local processed file becomes available

## 7. Minimal Validation Strategy

Allowed:

- run new analysis scripts on the existing disjoint 1000 retrieval outputs
- create new result directories

Not allowed:

- full-dev
- large sweep
- new retrieval over a bigger split

## 8. Practical Goal

The immediate goal is not to refactor the whole repository.

The immediate goal is:

- add a paper-ready metadata family comparison
- add a paper-ready efficiency analysis
- do so with minimal code movement and fully inspectable outputs
