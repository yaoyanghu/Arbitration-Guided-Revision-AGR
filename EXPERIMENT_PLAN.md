# Experiment Plan

## Goal

Build a fair answer-level evaluation package for the upgraded mainline while keeping older assets as auxiliary or diagnostic experiments.

## Experiment Layers

### Main experiments

- answer-level evaluation on the chosen main dataset
- evidence attribution quality
- fair baseline comparison

### Auxiliary experiments

- FEVER official retrieval benchmark
- controlled retrieval and evidence-selection comparison

### Diagnostic experiments

- Route A temporal-conflict slices
- temporal/conflict arbitration case studies

## Required Baselines

At minimum the mainline should compare:

1. parametric-only or no-retrieval baseline if task-compatible
2. vanilla RAG
3. stronger retrieval baseline
4. no temporal module
5. no conflict arbitration module
6. no source/reliability prior
7. full proposed system

## Required Ablations

- remove temporal module
- remove conflict arbitration
- remove source/reliability prior
- remove routing if routing is introduced
- vary top-k or context budget

## Formal Result Groups

Each formal run should record:

- dataset
- split
- retriever
- generator
- top-k
- context budget
- seed
- timestamp
- config path

## Reporting Outputs

Each formal experiment family must produce:

- `RESULTS_SUMMARY.md`
- `ABLATION_SUMMARY.md`
- `ERROR_ANALYSIS.md`
- paper-facing tables

## Non-Goals

- no Route C
- no Route B main-method comeback
- no giant sweep
- no unfair weak baselines
