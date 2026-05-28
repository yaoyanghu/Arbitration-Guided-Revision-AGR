# Dataset Compatibility Audit

## Decision

The upgraded project will use:

- main: `HotpotQA (fullwiki)`
- auxiliary: `FEVER official retrieval`
- diagnostic: `Route A temporal-conflict slices`

## Why This Stack Is Internally Consistent

### HotpotQA as main

What it gives:

- answer-level supervision
- multi-evidence supervision
- supporting titles that can anchor citation evaluation
- a standard benchmark name that reviewers understand

What it does not give by itself:

- rich temporal-conflict supervision

Why that is still acceptable:

- the mainline can still be designed to detect and arbitrate conflicts
- Route A remains the dedicated temporal/conflict stress layer

### FEVER as auxiliary

What it gives:

- controlled retrieval benchmark
- strong legacy asset reuse
- benchmark-like evidence retrieval measurement

Why it should not carry the whole upgraded paper:

- it is too retrieval-centric to stand alone as the new answer-level mainline

### Route A as diagnostic

What it gives:

- targeted temporal-conflict stress conditions
- controlled arbitration examples
- reusable error analysis material

Why it should not be the only benchmark:

- too curated
- too narrow
- too dependent on synthetic construction-side fields for evaluation

## Why Not Use Route A As Main

- not broad enough
- not benchmark-like enough
- too easy for reviewers to dismiss as a special-case slice study

## Why Not Use FEVER As Main

- cleaner retrieval than answer-generation story
- weaker fit for modern answer-level faithful RAG as the sole benchmark

## Why Not Revive Route B

- graph line failed to prove independent value against matched non-graph baselines

## Engineering Compatibility

This stack is practical because:

- BM25 infrastructure already exists
- FEVER preprocessing already exists
- Route A diagnostics already exist
- HotpotQA can be normalized into the same query schema with modest engineering effort

## Next Engineering Requirement

The repo now needs:

- a HotpotQA preparation script into the unified contract
- an answer-level evaluation entry
- a citation-aware output format
