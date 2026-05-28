# Paper Ready Notes

## Current Paper Position

The project is now in **paper closeout mode**.

What exists:

- a frozen answer-level formal mainline
- completed formal runs on:
  - `HOH formal 1024`
  - `TempRAGEval formal 1244`
- preserved FEVER controlled auxiliary retrieval results
- a stable claim freeze that keeps:
  - temporal
  - conflict
  and drops:
  - source from the main contribution

What still needs careful handling:

- paper wording must not overclaim source/reliability
- TempRAGEval must be described as temporal auxiliary validation, not sole full-stack proof
- FEVER must stay retrieval-only auxiliary

## Paper Narrative Direction

The likely paper direction is:

- conflict-aware temporal faithful RAG
- answer-level generation with evidence attribution
- FEVER official retrieval as auxiliary controlled evidence-selection benchmark
- Route A temporal-conflict slices as diagnostic stress tests

## What Should Not Be Revived As The Main Story

- Route B graph as the main contribution
- FEVER short paper as the mainline
- narrow preferred-doc reranking as the final endpoint
- source/reliability as a validated headline contribution
