# Route A Mainline Paper Outline

## 1. Problem Setup

- Define the Route A task as temporal-conflict evidence ranking.
- Keep the scope retrieval-only and reranking-only.
- Explain why stale vs updated evidence and source conflict matter.

## 2. Method

- Retrieval-only BM25 backbone
- Temporal signal
- Source reliability prior
- Final linear reranking layer

## 3. Main Experimental Package

- Present the Route A v3 mainline slice
- State that it contains 54 queries with balanced clear / reliability-sensitive / mixed coverage
- Use the main result table as the centerpiece

## 4. Stratified Analysis

- Show the case-type table
- Emphasize that mixed cases remain hardest
- Show that reliability-sensitive cases benefit strongly from the reliability prior

## 5. Error Taxonomy

- stale lexical stickiness in mixed cases
- partial rather than full correction on noisy conflict wording
- limited effect of reliability priors outside near-tie same-year conflicts

## 6. Representative Case Studies

- one reliability-helped example
- one mixed improved example
- one mixed still-failing example

## 7. Minimal Robustness Check

- Report the separate 18-query held-out slice
- Use it only as a robustness confirmation
- Do not upgrade it into a second mainline experiment

## 8. Route B Positioning

- Mention Route B only as an analysis / conflict-focused layer
- Explicitly state that it is not part of the Route A main result package

## 9. Limitations

- current slices are still curated temporal-conflict subsets
- external validity remains narrower than a full benchmark claim
- mixed ambiguous cases remain the main unresolved difficulty
