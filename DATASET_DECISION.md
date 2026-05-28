# Dataset Decision

## Decision Summary

The upgraded project will use the following dataset hierarchy:

1. **Target main-result dataset**: `HOH`
2. **Engineering pilot / backbone dataset**: `HotpotQA`
3. **Temporal-sensitive auxiliary validation**: `TempRAGEval` preferred, `DynaQuest` as fallback
4. **Controlled auxiliary benchmark**: `FEVER official retrieval`
5. **Diagnostic stress dataset**: legacy `Route A temporal-conflict slices`
6. **Historical analysis layer**: `Route B`
7. **Additional public temporal QA asset**: `ChronoQA`

## Why A New Main Dataset Is Needed

Current Route A and FEVER assets are useful, but neither is enough by itself:

- Route A is too curated and narrow
- FEVER official retrieval is strong as retrieval supervision, but not sufficient as the sole answer-level RAG story

The mainline needs:

- answer-level outputs
- raw evidence grounding
- multi-evidence support
- potential temporal or conflicting evidence behavior

## Main Dataset Criteria

The chosen main dataset must be:

- public and reproducible
- answer-level
- evidence-oriented
- runnable on a single A100 40G
- compatible with citation-style outputs
- not dependent on hidden proprietary infrastructure

## Current Mainline Dataset Decision

The project now separates:

- **paper target dataset**: `HOH`
- **active engineering pilot dataset**: `HotpotQA distractor/fullwiki family`

## Why HOH Is The Target Main Dataset

HOH best matches the upgraded paper ambition because it is closer to a real answer-level, evidence-grounded RAG setting than the older rerank-style legacy assets.

## Why HotpotQA Is Still Active Right Now

HotpotQA is currently the safest way to keep engineering moving because it gives the new project:

- answer-level QA targets
- explicit supporting titles
- multi-evidence reasoning
- a standard and recognizable RAG benchmark story
- compatibility with retrieval, evidence selection, and citation-style reporting
- realistic but still manageable engineering scope on a single A100 40G

Current status:

- `HotpotQA` is **active** for pilot and backbone verification
- `HOH` is **still required** before the project can claim a full main-result paper package

## Why HotpotQA Is Better Than Reusing Route A As Mainline

Route A remains valuable, but it is still:

- curated
- narrow
- diagnostic by design
- exposed to construction-side fields that should not become main-method inputs

HotpotQA gives the upgraded project a proper answer-level main benchmark, while Route A can continue to serve as the temporal/conflict stress set.

## Why FEVER Stays Auxiliary Instead Of Main

FEVER is still the cleanest retrieval benchmark asset in the repository, but:

- it is better suited to controlled retrieval and evidence selection analysis
- it is not the strongest sole answer-generation benchmark for the new upgraded narrative

## Why Route A Stays Diagnostic

Route A is now best positioned as:

- temporal/conflict stress test
- arbitration casebook source
- diagnostic slice for methods that claim to handle stale, updated, or conflicting evidence

## Temporal Auxiliary Validation Decision

Preferred next auxiliary temporal validation dataset:

- `TempRAGEval`

Current temporal auxiliary status:

- `TempRAGEval` is now connected and runnable
- `DynamicQA temporal` remains a public fallback only
- `ChronoQA` has been downloaded as an additional future temporal reasoning asset

Reason:

- this layer is meant to validate temporal sensitivity under a more answer-level framing than legacy Route A
- `TempRAGEval` is now available through authenticated download and should be preferred
- `DynamicQA temporal` stays as fallback and reference
- `ChronoQA` is downloaded, but its nested narrative format makes it a secondary integration target rather than the immediate next benchmark

## Deferred Dataset Lines

The repository already contains placeholder scripts for datasets such as `RAGTruth` and `HoH`, but they are not yet mature enough to serve as the immediate mainline benchmark. They can be revisited later as:

- attribution robustness checks
- hallucination-oriented auxiliary analysis
- post-mainline generalization experiments

## Auxiliary Dataset: FEVER Official Retrieval

Role:

- controlled retrieval benchmark
- reusable legacy asset
- sanity-check benchmark for retrieval and evidence selection

Use in the upgraded project:

- retrieval-only benchmark
- auxiliary analysis of evidence selection quality
- controlled experiment for comparing retrieval modules

## Diagnostic Dataset: Route A Temporal-Conflict Slices

Role:

- stress-test temporal/conflict reasoning
- diagnostic casebook source
- controlled slice for arbitration behavior

Use in the upgraded project:

- not the sole headline benchmark
- used for targeted diagnosis, ablations, and case studies

## Dataset Rules For The New Mainline

The upgraded mainline must avoid:

- explicit task-side labels as direct model inputs
- benchmark designs that reward only tiny-candidate reranking
- incomparable data budgets across baselines

## Immediate Dataset Action

The immediate implementation path is now:

1. keep `HotpotQA` as the active pilot backbone
2. continue wiring `HOH` as the target main-result dataset and active high-priority pilot
3. keep `FEVER` as the auxiliary retrieval benchmark
4. keep `Route A` as the diagnostic temporal-conflict benchmark
5. use `TempRAGEval` as the current temporal auxiliary validation set
6. keep `DynamicQA temporal` as fallback and `ChronoQA` as future extension asset
6. keep `ChronoQA` available as an additional public temporal QA asset for future auxiliary validation or long-context stress testing

## Latest Dataset Readout

After the newest targeted pilots:

- `HOH` remains the correct main-result dataset choice
  - reason: it now shows real answer-level separation between `full_model` and `no_temporal` on a 256-query pilot
  - caution: conflict/source contributions are still not independently validated
- `TempRAGEval` remains the correct temporal auxiliary dataset
  - reason: it continues to expose whether temporal extraction truly helps
  - current state: the temporal path is validated against `no_temporal`, but not yet against all other ablations
- `source` should not be a headline dataset-dependent claim
  - reason: neither `HOH` nor `TempRAGEval` currently offers enough source heterogeneity to prove an independent source/reliability contribution
- frozen formal datasets:
  - `HOH formal 1024`
  - `TempRAGEval formal 1244`
- `HotpotQA` stays frozen as engineering backbone / pilot only
- `Route B` remains frozen as analysis layer and does not re-enter the mainline

## Source Validation Route Decision

For dedicated source heterogeneity validation, the lowest-cost credible route is now:

- use the existing `fever_hetero_subset_20`

Reason:

- it already contains mixed source types
  - `wikipedia_api_summary`
  - `wikidata_entity`
- it is cheaper and more reproducible than adding another public dataset during paper closeout

Outcome of the validation:

- source-aware weighting still showed no independent measurable gain on this controlled heterogeneous slice

Implication:

- do not reopen `source` as a mainline paper claim
- treat source as dormant future-extension infrastructure unless a stronger heterogeneous benchmark becomes available later
