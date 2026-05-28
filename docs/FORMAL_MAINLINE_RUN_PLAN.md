# Formal Mainline Run Plan

## Status

`completed`

## Frozen Mainline Definition

The formal mainline is now frozen as:

- stronger retrieval backbone
- temporal-aware answer extraction
- conflict-aware evidence arbitration
- citation-aware answer output

The `source` path is **not** part of the frozen core claim because it has not shown independent gains in targeted pilots.

## Formal Run Set

### Main

- `HOH formal main run`
  - dataset size:
    - `1024 queries`
  - variants:
    - `stronger_retrieval_template`
    - `no_temporal`
    - `no_conflict`
    - `full_model`

### Auxiliary

- `TempRAGEval formal auxiliary run`
  - dataset size:
    - `1244 queries`
  - variants:
    - `stronger_retrieval_template`
    - `no_temporal`
    - `full_model`

### Controlled auxiliary line

- `FEVER official retrieval`
  - retrieval-only auxiliary benchmark
  - keep separate from answer-level mainline claims

## Completed Run Groups

- [formal_hoh1024_20260327](D:/HUYAOYANG/Work/New_ChronoRAG/runs/formal_hoh1024_20260327)
- [formal_temprageval1244_20260327](D:/HUYAOYANG/Work/New_ChronoRAG/runs/formal_temprageval1244_20260327)

## Formal Preconditions

- use the same frozen data contracts already validated in pilot
- keep budgets matched across variants
- do not reintroduce Route B
- do not promote `source` as a proven core module
- record every run as formal with frozen config copies

## Formal Claim Scope

The formal paper should now aim to support:

- temporal-aware faithful RAG with conflict-aware arbitration

It should **not** claim:

- validated source/reliability gains
- Route B graph value
- ChronoQA mainline generalization
