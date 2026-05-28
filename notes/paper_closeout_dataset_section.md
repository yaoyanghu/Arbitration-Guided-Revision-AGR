# Dataset Section Draft

The paper uses a tiered dataset design.

- `HOH formal 1024` is the primary answer-level result set.
- `TempRAGEval formal 1244` is the temporal auxiliary validation set.
- `FEVER official retrieval` is retained as a controlled auxiliary retrieval benchmark.
- `HotpotQA` is kept as engineering backbone and pilot-only evidence.
- `Route A` is retained as a diagnostic temporal-conflict stress set.
- `Route B` is frozen as analysis layer only and is not part of the main method claim.

This structure reflects a deliberate separation of roles: HOH carries the main answer-level comparison, TempRAGEval validates temporal behavior on an external temporal benchmark, and FEVER preserves continuity with the repository's strongest controlled retrieval asset.
