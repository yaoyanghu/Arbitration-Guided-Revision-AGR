# Title

Route A: Lightweight Temporal-Conflict Evidence Reranking with Source Reliability Priors

# Abstract

This paper studies Route A, a retrieval-only evidence-ranking setting for temporal-conflict queries. The task is to rank updated evidence above stale or conflicting evidence under a fixed BM25 backbone, without changing the model stack or expanding to generation. Route A combines three lightweight components: retrieval-only BM25, a rule-based temporal signal, and a small source-reliability prior. On the 54-query Route A v3 mainline slice, the full pipeline improves preferred top1 from 0.537 to 0.815 and pairwise preference success from 0.667 to 0.833, while preferred MRR rises from 0.762 to 0.907. A separate 18-query held-out slice preserves the same ordering, reaching 0.833 preferred top1 and 0.889 pairwise preference success, which we treat as a robustness confirmation rather than a second main experiment. Stratified analysis shows that clear updated-vs-stale cases are already easy for BM25, while reliability-sensitive and especially mixed ambiguous cases provide the main room for improvement. These results support a narrow but stable claim: lightweight temporal and source-reliability reranking improves preferred-evidence ranking on balanced temporal-conflict slices without changing the underlying retrieval backbone.

# 1 Introduction

Evidence retrieval often becomes harder when a query implicitly asks for the current state of an entity while older descriptions remain lexically competitive. In these temporal-conflict settings, the retrieval problem is not only whether relevant evidence is present, but whether updated evidence is ranked ahead of stale or noisy alternatives. This issue appears in settings where older states remain strongly represented in text and where same-year conflicting reports differ in reliability.

Route A is designed to study this problem in a controlled retrieval-only setting. We deliberately keep the scope narrow. We do not change the retrieval model, introduce a new encoder, or expand the task into generation. Instead, we ask whether lightweight reranking signals can improve evidence ranking under a fixed BM25 backbone. This choice keeps the experimental interpretation simple: any gain should come from temporal-conflict reranking rather than from a new model or larger candidate pool.

The current paper centers entirely on Route A. Route B is not part of the main method and appears only as an analysis layer when needed for inspecting conflict structure around difficult cases. Route C is out of scope. Within this boundary, the main contribution is a frozen Route A v3 mainline package built on a balanced temporal-conflict slice with a matching held-out robustness confirmation.

# 2 Method

Route A studies temporal-conflict evidence ranking. Given a query that refers to an entity at a specific time, the goal is to rank updated evidence above stale or conflicting evidence under a fixed retrieval setting. The backbone is retrieval-only BM25 over a controlled temporal-conflict corpus. We keep the task retrieval-only and reranking-only throughout.

The temporal component is a lightweight rule-based score. It uses query time, evidence time, temporal cues in the evidence text, and explicit temporal-status hints to estimate whether a candidate better matches the current state implied by the query. This component is intended to lift updated evidence when BM25 still gives high lexical weight to older or noisy candidates.

The reliability component is a small source prior applied after temporal reranking. Official records and current encyclopedic sources receive higher scores than archival news or blogs. This prior is intentionally weak. Its role is to break near-ties in conflict-heavy cases rather than dominate the ranking on its own.

The final Route A score is a linear fusion of normalized BM25, temporal score, and reliability score. In the frozen v3 package, the weights are 0.6 for BM25, 0.25 for temporal scoring, and 0.15 for reliability weighting. We evaluate three stages: retrieval-only, temporal-only, and temporal plus reliability.

# 3 Experimental Setup

The main experimental package is Route A v3. It contains 54 queries built from 18 real temporal-conflict events, with balanced coverage across three case types: clear updated-vs-stale, reliability-sensitive conflict, and mixed ambiguous case. The task contract is fixed across all evaluations. Each query has a preferred updated document, one or more stale alternatives, and a small candidate set containing stale, updated, and conflicting evidence.

We report preferred top1, pairwise preference success, mean preferred rank, preferred MRR, and stale-wins count. We also inspect per-query artifacts to verify that temporal and reliability signals measurably change ranking behavior. The acceptance-style checks are not treated as a separate contribution; they serve only to confirm that the frozen Route A package runs end to end and behaves as intended.

To add a minimal robustness check without reopening the main experiment, we evaluate the frozen Route A v3 pipeline on a separate 18-query held-out temporal-conflict slice built under the same contract. This held-out package is not used to redefine the claim. It functions only as a robustness confirmation that the Route A pattern survives on a fresh slice.

# 4 Results

On the 54-query Route A v3 mainline slice, retrieval-only BM25 reaches 0.537 preferred top1 and 0.667 pairwise preference success. Adding the temporal signal raises these numbers to 0.704 and 0.796, and the full Route A pipeline with the source-reliability prior reaches 0.815 preferred top1 and 0.833 pairwise preference success. Preferred MRR rises from 0.762 to 0.846 and then to 0.907. These gains are meaningful because the task contract, retrieval backbone, and scoring family remain fixed.

The held-out robustness confirmation preserves the same ordering. On the 18-query held-out slice, retrieval-only reaches 0.500 preferred top1 and 0.667 pairwise preference success, temporal-only reaches 0.722 and 0.778, and the full Route A pipeline reaches 0.833 and 0.889. We do not treat this as a second main experiment. Instead, it gives a low-risk confirmation that the Route A behavior is not confined to a single frozen slice.

Stratified analysis shows where the gains come from. Clear updated-vs-stale cases are already easy for retrieval-only BM25, which achieves 1.000 preferred top1. The main room for improvement lies in reliability-sensitive and mixed ambiguous cases. In reliability-sensitive cases, the full pipeline improves preferred top1 from 0.611 to 0.944. In mixed cases, retrieval-only fails completely at top1, while the full pipeline recovers to 0.500 preferred top1 and 0.500 pairwise preference success. This makes mixed ambiguous cases the dominant remaining difficulty and the clearest justification for the temporal-conflict formulation.

The main error mode is stale lexical stickiness. Older evidence often remains strongly competitive because it reuses much of the query wording while preserving a previous state. Temporal cues and source priors reduce this problem, but they do not always eliminate it. Reliability priors are most useful in same-year conflict cases where multiple candidates share surface overlap but differ in source trustworthiness.

Route B does not alter these results. If mentioned, it should appear only as an analysis layer for inspecting conflict structure around difficult Route A cases. It is not part of the Route A main method or main results.

# 5 Limitations

The current Route A evidence is built on real temporal-conflict slices rather than a full benchmark-scale evaluation. This is enough to support the Route A claim, but it is not enough to justify a broad external-validity claim over all temporal retrieval settings.

Mixed ambiguous cases remain the dominant source of residual error. These cases preserve strong lexical traces of older states, so stale evidence can remain highly competitive even after temporal and reliability reranking. The reliability prior is intentionally small and rule-based, which keeps the method interpretable and stable but also limits how aggressively it can resolve difficult conflicts.

The held-out slice strengthens confidence in the Route A pattern, but it remains a small robustness confirmation rather than a second main experiment. Finally, Route B should not be treated as a limitation-resolving extension here. Under the current evidence, it remains only an analysis layer.

# 6 Conclusion

Route A is the current mainline experiment package. On a balanced 54-query temporal-conflict slice, lightweight temporal and source-reliability reranking substantially improve preferred-evidence ranking over retrieval-only BM25 while keeping the retrieval backbone fixed. A separate 18-query held-out slice preserves the same ordering and serves as a robustness confirmation. The resulting claim is narrow but stable: Route A shows that lightweight reranking signals can improve evidence ranking in temporal-conflict settings without introducing a new model or reopening the task definition. The main remaining challenge is mixed ambiguous cases, where older evidence still retains strong lexical pull.
