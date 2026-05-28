# Route A Results Draft v1

## Main Results

Route A v3 is the main experimental package. On the 54-query balanced temporal-conflict slice, retrieval-only BM25 reaches 0.537 preferred top1 and 0.667 pairwise preference success. Adding the temporal signal raises these numbers to 0.704 and 0.796, and the full Route A pipeline with a small source-reliability prior reaches 0.815 preferred top1 and 0.833 pairwise preference success. Preferred MRR follows the same pattern, rising from 0.762 to 0.846 and then to 0.907.

These gains are meaningful because the task contract, retrieval backbone, and scoring family remain fixed. The improvement therefore comes from lightweight temporal-conflict reranking rather than a model change or candidate-pool expansion.

## Held-out Robustness Confirmation

We also run the frozen Route A v3 pipeline on a separate 18-query held-out temporal-conflict slice built under the same contract. The same ordering remains intact: retrieval-only BM25 reaches 0.500 preferred top1 and 0.667 pairwise preference success, temporal-only reaches 0.722 and 0.778, and the full Route A pipeline reaches 0.833 and 0.889. We treat this held-out package as a robustness confirmation rather than a second main experiment.

## Stratified Analysis

The stratified results show that clear updated-vs-stale cases are already near-solved by retrieval-only BM25. The main room for improvement lies in reliability-sensitive and mixed ambiguous cases. In reliability-sensitive cases, the final Route A pipeline improves preferred top1 from 0.611 to 0.944. In mixed cases, retrieval-only fails completely at top1, while the full Route A pipeline recovers to 0.500 preferred top1 and 0.500 pairwise preference success. This makes mixed cases the most important remaining difficulty and also the clearest justification for the temporal-conflict formulation.

## Error Taxonomy

The dominant error mode is stale lexical stickiness in mixed ambiguous cases. Older evidence often remains strongly rank-competitive because it reuses much of the query wording while preserving a previous state. Temporal cues and source priors reduce this problem, but they do not always eliminate it. Reliability priors help most in same-year conflict cases where multiple candidates share surface overlap but differ in source trustworthiness.

## Route B Positioning

Route B is not part of the main Route A results. If mentioned, it should appear only as an analysis layer for inspecting conflict structure around difficult Route A cases. It should not appear in the main results section as a co-equal method line.
