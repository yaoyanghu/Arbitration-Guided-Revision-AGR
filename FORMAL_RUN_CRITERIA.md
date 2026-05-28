# Formal Run Criteria

## Status

`formal runs launched and completed`

## A run can be called formal only if

1. the dataset contract is frozen for that dataset
2. the baseline matrix is fixed
3. debug and pilot runs have passed without format breakage
4. outputs contain:
   - predicted answers
   - selected evidence
   - citations
   - arbitration traces
5. method-visible features have passed leakage audit
6. the config used for the run is stored and reproducible
7. result summaries clearly distinguish formal from debug and pilot

## Current State

- formal FEVER retrieval from the legacy controlled line exists
- formal answer-level RAG runs now exist for:
  - `HOH formal 1024`
  - `TempRAGEval formal 1244`
- current mainline work has moved from pilot into formal result collection

## Current Gate Readout

### HOH gate

- status: `passed on temporal and conflict-ablation criteria`
- evidence:
  - [pilot_hoh256_20260327_r6](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_hoh256_20260327_r6)
  - `full_model` now separates from `no_temporal`
  - `full_model` now separates from `no_conflict`
  - `full_model` still ties with `no_source`

### TempRAGEval gate

- status: `passed on temporal ablation criterion; not yet fully mature`
- evidence:
  - [pilot_temprageval128_20260327_r6](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_temprageval128_20260327_r6)
  - EM is no longer zero
  - `full_model` continues to separate from `no_temporal`
  - but it still does not separate from `no_conflict` or `no_source`

### Generator gate

- status: `partially passed`
- evidence:
  - low-level year extraction failures were reduced on TempRAGEval
  - low-level count / compared-value / range extraction is improved on HOH
  - many remaining errors are now higher-level entity-slot or evidence-selection mistakes
  - conflict discrimination is now visible on HOH
  - source discrimination is still weak

## Conclusion

The project now passes the minimum gate needed to prepare formal runs for a frozen mainline defined as:

- retrieval
- temporal-aware answer extraction
- conflict-aware evidence arbitration

The `source` module does **not** pass the same bar and should not be presented as part of the proven core contribution.

## Formal Run Record

- HOH:
  - [formal_hoh1024_20260327](D:/HUYAOYANG/Work/New_ChronoRAG/runs/formal_hoh1024_20260327)
- TempRAGEval:
  - [formal_temprageval1244_20260327](D:/HUYAOYANG/Work/New_ChronoRAG/runs/formal_temprageval1244_20260327)

Allowed next step:

- analyze formal results and produce paper-ready tables with `temporal + conflict` as the frozen full model

Not allowed:

- presenting any existing pilot number as formal evidence
- keeping `source` in the formal main claim as if it had already been validated
