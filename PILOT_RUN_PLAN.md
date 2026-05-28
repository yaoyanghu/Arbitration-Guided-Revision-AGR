# Pilot Run Plan

## Status

`pilot phase completed; frozen formal runs launched`

## Objective

Use `HotpotQA` as the engineering pilot dataset to validate the end-to-end answer-level pipeline.

## Pilot Dataset

- source: `HotpotQA distractor`
- role: pilot only
- reason: easier to stream and normalize than a full corpus download, while still supporting answer-level QA and multi-evidence selection

## Pilot Run Groups

### debug

- minimal smoke query set
- verify output contract

### pilot_hotpot_small

- `24` streamed validation queries
- corpus built from the distractor contexts attached to those queries
- baseline matrix executed under matched settings

### completed run groups

- `pilot_hotpot24_20260327`
- `pilot_hotpot24_20260327_r2`

## Required Outputs

- per-variant run directories under `runs/`
- summary under `runs/<run_group>/summary.md`
- update to `RESULTS_SUMMARY.md`
- first error-analysis notes under `ERROR_ANALYSIS.md`

## Current Readout

- first end-to-end pilot completed successfully
- answer-level pipeline is runnable
- citation recall is non-trivial
- answer extraction remains the dominant bottleneck
- current temporal/conflict weighting does not yet help on non-temporal Hotpot pilot data

## Current Gating Focus

- `HOH 256` is now the main pilot gate for the primary dataset
- `TempRAGEval 128` is now the main pilot gate for temporal answer extraction
- the project should continue targeted pilot work until `full_model` separates from at least one key ablation on HOH and demonstrates non-trivial temporal utility on TempRAGEval

## Latest Gate Readout

- `HOH 256 r6`: `full_model` now beats both `no_temporal` and `no_conflict`
- `TempRAGEval 128 r6`: `full_model` still beats `no_temporal`
- `no_source` still ties with `full_model`
- overall status: `pre-formal gating completed for temporal + conflict; source stopped as a mainline contribution`

## Non-Goals

- not formal paper evidence
- not the final HOH result
- not a replacement for FEVER auxiliary runs

## Pilot Closeout

- exploratory pilot work is now closed
- pilot numbers remain valid only for gate-setting and engineering diagnosis
- formal reporting must now use:
  - [formal_hoh1024_20260327](D:/HUYAOYANG/Work/New_ChronoRAG/runs/formal_hoh1024_20260327)
  - [formal_temprageval1244_20260327](D:/HUYAOYANG/Work/New_ChronoRAG/runs/formal_temprageval1244_20260327)

## Immediate Next Focus

- do **not** expand the baseline matrix
- do **not** introduce Route B or ChronoQA into the mainline
- shift from pilot interpretation to formal-result summarization and paper table assembly
