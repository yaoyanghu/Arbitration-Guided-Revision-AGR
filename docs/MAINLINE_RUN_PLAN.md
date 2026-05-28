# Mainline Run Plan

## Chosen Mainline

The new mainline is:

**Conflict-Aware Temporal Faithful RAG**

This project will no longer treat narrow candidate reranking as the final endpoint. The mainline target is answer generation with evidence selection, citation, and conflict-aware arbitration.

## Run Groups

### Group 1: Data compatibility and smoke checks

Purpose:

- validate new unified data contract
- validate retrieval input and output compatibility
- validate answer-generation artifacts

Planned run type:

- `debug`

### Group 2: Main-dataset pilot runs

Purpose:

- verify the new answer-level pipeline works end to end
- compare no-conflict vs conflict-aware variants

Planned run type:

- `pilot`

### Group 3: Formal mainline baselines

Purpose:

- produce the first formal answer-level main table

Planned comparisons:

- no retrieval or parametric-only if task-compatible
- vanilla RAG
- stronger retrieval baseline
- no temporal module
- no conflict arbitration
- no source prior
- full conflict-aware faithful RAG

Planned run type:

- `formal`

### Group 4: Auxiliary FEVER retrieval evaluation

Purpose:

- preserve the clean benchmark asset
- evaluate retrieval and evidence selection quality under controlled conditions

Planned run type:

- `formal_aux`

### Group 5: Diagnostic Route A stress tests

Purpose:

- evaluate temporal/conflict behavior on curated hard cases
- support case studies and error taxonomy

Planned run type:

- `diagnostic`

## Execution Order

1. freeze legacy assets
2. finalize unified data contract
3. implement answer-level mainline skeleton
4. run debug smoke checks
5. select and wire the main public dataset
6. run pilot baselines
7. run formal mainline comparisons
8. run auxiliary FEVER and diagnostic Route A evaluations
9. export paper-ready tables and notes

## Blocking Rule

No formal run starts until:

- the new answer-level pipeline writes citations
- method-visible inputs exclude obvious leakage labels
- the main dataset contract is fixed
- debug outputs are reproducible
