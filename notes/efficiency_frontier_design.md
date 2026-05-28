# Efficiency Frontier Design

## Scope

This note explains how to add an efficiency-oriented framing to the current FEVER short paper without changing the main task, candidate pool, or model class.

Evidence checked:

- `notes/current_claim_freeze.md`
- `notes/paper_closeout_plan.md`
- `notes/results_error_validity_draft.md`
- `runs/fever_official_route_a_disjoint_1000/official_strict_eval_results.json`
- `runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/nearest_title_baseline_results.json`
- `src/analysis/official_strict_revalidation.py`
- `src/analysis/nearest_title_baseline_eval.py`

## 1. Why the Current Results Fit Efficiency Framing

The current evidence is unusually well suited for an efficiency story because the improvement already has the right shape:

- the candidate pool is fixed
- Recall@10 does not improve
- early-rank strict access improves
- the rerankers are training-free and rule-based

That means the gain is not:

- more retrieval depth
- more index coverage
- more expensive inference
- a larger end-to-end system

Instead, the gain is:

- lower access depth to the correct evidence page within the same top-k budget

This supports a reviewer-safe efficiency framing:

- `budget-preserving evidence access`
- `better early-rank evidence access under fixed retrieval budget`

## 2. Recommended Efficiency Metrics

### A. MRR

Definition:

- mean reciprocal rank of the first strict or relaxed hit per query

Why it fits:

- directly captures how early the first usable evidence page appears
- more sensitive than Recall@k when the main effect is reordering inside a fixed candidate set

Data needed:

- per-query first hit rank already available from current strict and relaxed evaluation logic

### B. nDCG@5 and nDCG@10

Definition:

- discount-aware ranking quality using binary relevance under current strict or relaxed matching

Why it fits:

- rewards moving a relevant evidence page upward even when coverage is unchanged
- cleaner than only reporting Recall@5 when the method mostly improves top ranks

Data needed:

- ranked candidate lists
- strict or relaxed hit function
- binary relevance per candidate

Recommended scope:

- report both `strict nDCG@5/@10` and `relaxed nDCG@5/@10`

### C. First-hit rank summary

Definition:

- mean, median, and selected percentiles of the first strict or relaxed hit rank

Why it fits:

- directly operationalizes how many pages a user or downstream component must inspect before reaching gold evidence
- easy to explain in a short paper

Recommended summary:

- mean first-hit rank on successful queries
- median first-hit rank on successful queries
- proportion of queries with no hit in top-10

### D. Fixed page-budget success

Definition:

- success under tiny inspection budgets such as 1, 3, 5, and 10 pages

Why it fits:

- makes the efficiency story concrete
- can be derived from the same ranked outputs without rerunning retrieval

Recommended view:

- strict success at page budgets 1, 3, 5, 10
- relaxed success at page budgets 1, 3, 5, 10

### E. Gold evidence sentence coverage under fixed page budget

Definition:

- whether at least one gold evidence sentence is accessible once the system exposes the top-B pages

Why it is attractive:

- closer to real downstream verifier cost than page hit alone

Current feasibility:

- not guaranteed from existing run files alone
- may require sentence-level mapping from processed FEVER files to retrieved page texts

Recommendation:

- attempt only as a minimal supplementary analysis if the processed query file already exposes sentence ids cleanly enough
- otherwise keep as a designed follow-up, not a blocker

### F. Runtime / cost note

Definition:

- a lightweight accounting note rather than a full benchmark

Recommended content:

- BM25 retrieval cost is unchanged
- metadata reranking touches only the existing top-k candidates
- each feature is a cheap string-level computation over `query/title/text`

Why this is enough for now:

- the paper only needs to justify `budget-preserving` rather than produce a hardware benchmarking paper

## 3. Script Reuse and Script Additions

### Reusable existing scripts

- `src/analysis/official_strict_revalidation.py`
  - already computes strict and relaxed per-query first hit ranks
- `src/analysis/nearest_title_baseline_eval.py`
  - already builds and compares multiple lightweight title-aware variants

### Recommended new script

- `src/analysis/efficiency_frontier_eval.py`

Planned role:

- read an existing run directory or a new metadata-family run directory
- compute MRR, nDCG@5, nDCG@10, first-hit-rank summaries, and fixed-budget success
- write a compact JSON result and Markdown summary

### Optional supplementary script

- `src/analysis/evidence_sentence_budget_eval.py`

Use only if low-cost implementation is feasible from current processed FEVER fields.

## 4. Which Metrics Can Be Added Without Full Reruns

These can be added from existing ranked outputs only:

- MRR
- nDCG@5
- nDCG@10
- first-hit rank mean and median
- budgeted page success at 1, 3, 5, 10
- runtime / cost note

These do not require:

- new retrieval
- full-dev
- a larger sweep

These may require extra processing or may need deferral:

- gold evidence sentence coverage under fixed page budget

## 5. Recommended Paper Wording

Recommended safe wording:

- The proposed metadata-aware rerankers improve early evidence access under a fixed retrieval budget.
- Because top-10 coverage remains unchanged, the gains come from better rank allocation rather than broader retrieval.
- This places the method on an appealing efficiency frontier: it preserves candidate generation cost while reducing the number of pages that must typically be inspected before reaching gold evidence.

Avoid:

- claiming a full runtime benchmark if none is measured
- claiming lower end-to-end verification cost unless a downstream verifier is actually evaluated

## 6. Minimal Efficiency Package

If time is tight, the minimum useful efficiency package is:

1. strict and relaxed MRR
2. strict and relaxed nDCG@5 / @10
3. first-hit-rank mean and median
4. page-budget success at 1, 3, 5, 10
5. a short runtime/cost note explaining why the rerankers are cheap

That package is enough to support the paper-level phrase:

- `budget-preserving metadata-aware evidence access`
