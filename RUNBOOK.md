# Runbook

## Purpose

This runbook defines how the upgraded `New_ChronoRAG` project should be executed reproducibly across local and server environments.

## Environment

Primary local path:

- `D:/HUYAOYANG/Work/New_ChronoRAG`

Primary server path:

- `/home/huyaoyang/Projects/flashrag_project_20251213/New_ChronoRAG`

## Reproducibility Rules

- never overwrite a finished formal run
- distinguish `debug`, `pilot`, and `formal`
- store logs separately from outputs
- save exact config used for each run

## Recommended Run Flow

1. sanity-check data loading
2. sanity-check retrieval
3. sanity-check generation
4. pilot answer-level run
5. formal baseline runs
6. formal ablations
7. structured case analysis export
8. paper-closeout packaging

## Run Naming

Use:

- `run_group`
- `dataset`
- `model`
- `setting`
- `seed`
- `timestamp`

Example:

- `formal_main_hotpotqwen_bm25_temporalconflict_seed42_20260327`

## Output Structure

- `runs/<run_name>/`
- `logs/<run_name>/`
- `reports/<report_group>/`

## Current Status

- legacy retrieval and diagnostic runs already exist
- formal answer-level mainline runs now exist:
  - [formal_hoh1024_20260327](D:/HUYAOYANG/Work/New_ChronoRAG/runs/formal_hoh1024_20260327)
  - [formal_temprageval1244_20260327](D:/HUYAOYANG/Work/New_ChronoRAG/runs/formal_temprageval1244_20260327)
- the current phase is paper closeout, not exploratory pilot work
