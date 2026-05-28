# Final Upgrade Experiment Plan

## 1. New High-Level Paper Positioning

Recommended paper positioning:

- a retrieval-only FEVER paper about `metadata-aware grounded retrieval`
- the central problem is how to improve strict evidence-page access inside a fixed BM25 candidate pool
- the paper should combine three ingredients:
  - metadata-aware family comparison
  - efficiency frontier analysis
  - diagnosis of when lightweight metadata cues help or mislead

This is a better fit for the current repository than a narrower `title overlap` story and much safer than any complete ChronoRAG system framing.

## 2. Main Experiment A: Metadata-Aware Family Effectiveness

### Goal

Turn the current title-only story into a genuine family study over lightweight metadata-aware lexical rerankers.

### Variants

- `routeA_bm25`
- `routeA_bm25_title_overlap`
- `routeA_bm25_exact_title_boost`
- `routeA_bm25_alias_redirect_match`
- `routeA_bm25_disambiguation_title_match`

Optional later:

- `routeA_bm25_page_type_prior`
- `routeA_bm25_first_sentence_entity_anchor`

### Core metrics

- strict Recall@1 / @5 / @10
- relaxed Recall@1 / @5 / @10
- improved case count
- regressed case count
- label-wise strict breakdown

### Minimum acceptance standard

- at least one new metadata-aware variant beyond current title overlap and exact title boost is runnable on the disjoint 1000 split
- the family table clearly shows the strength-vs-conservativeness tradeoff
- all results are written to an independent run directory and summarized in Markdown

## 3. Main Experiment B: Efficiency Frontier

### Goal

Show that the improvement is useful because it improves early evidence access without increasing retrieval depth or introducing heavy models.

### Metrics

- strict MRR
- relaxed MRR
- strict nDCG@5 / @10
- relaxed nDCG@5 / @10
- strict and relaxed first-hit-rank summaries
- success under page budgets 1, 3, 5, 10
- short runtime/cost note

Optional:

- fixed page budget sentence coverage if lightweight implementation is feasible

### Minimum acceptance standard

- efficiency metrics are computed for at least BM25, title overlap, exact title boost, and new P0 variants
- the results support a paper-safe wording around `budget-preserving evidence access`
- the analysis is derived from existing disjoint run outputs rather than a new large run

## 4. Main Experiment C: Diagnosis / Claim-Type Analysis

### Goal

Move beyond aggregate gain and explain which FEVER claim patterns benefit from metadata-aware reranking.

### Recommended diagnosis axes

- explicit title mention vs alias-like mention
- disambiguation-sensitive claims
- claims with type words such as `film`, `series`, `band`, `album`, `actor`, `city`
- SUPPORTS vs REFUTES
- conservative vs aggressive reranker behavior

### Output form

- compact case taxonomy
- a small claim-type table
- a short error analysis section focused on misdirection risks

### Minimum acceptance standard

- a paper-facing summary identifies at least two recurrent gain modes and one regression mode
- diagnosis remains grounded in real error cases from the disjoint split

## 5. Explicit Exclusions

The following are not part of the current main line:

- claim-adaptive router
- generation
- GraphRAG
- Route B
- Route C
- dense retrieval
- cross-encoder reranking
- full verifier-generator pipeline claims

## 6. Recommended Execution Order

1. Freeze design and implementation boundaries
- write `metadata_family_design.md`
- write `efficiency_frontier_design.md`
- write `implementation_plan_metadata_family.md`

2. Implement P0 family only
- keep code changes local to analysis scripts
- do not touch Route B or Route C

3. Run low-risk disjoint-1000 family evaluation
- no full-dev
- no large sweep

4. Compute efficiency metrics from the same outputs

5. Write result summary and update paper-facing assets

## 7. Why This Plan Is the Best Fit

This plan is the best fit for the repository because it:

- reuses the strongest existing anchor, `disjoint 1000`
- directly addresses the reviewer challenge already documented in the repo
- upgrades the story from a single heuristic to a design-principle paper
- adds a non-inflated efficiency framing without forcing new large infrastructure
- preserves the FEVER-only retrieval scope
