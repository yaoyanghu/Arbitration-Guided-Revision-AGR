# Route A Method Draft v1

## Task Scope

Route A studies temporal-conflict evidence ranking. Given a query that refers to an entity at a specific time, the goal is to rank updated evidence above stale or conflicting evidence under a fixed retrieval setting. We keep the task retrieval-only and reranking-only throughout.

## Backbone

The backbone is retrieval-only BM25 over a small controlled temporal-conflict corpus. We do not change the retrieval model, introduce a new encoder, or expand the task into generation.

## Temporal Signal

The temporal component is a lightweight rule-based score. It uses query time, evidence time, temporal cues in the evidence text, and explicit temporal-status hints to estimate whether a candidate better matches the current state implied by the query.

## Reliability Prior

The reliability component is a small source prior applied after temporal reranking. Official records and current encyclopedic sources receive higher scores than archival news or blogs. This prior is intentionally weak: it is designed to break near-ties in conflict-heavy cases rather than dominate the ranking on its own.

## Final Reranking

The final Route A score is a linear fusion of normalized BM25, temporal score, and reliability score. In the frozen v3 package, the weights are 0.6 for BM25, 0.25 for temporal scoring, and 0.15 for reliability weighting.

## Evaluation

We report three stages: retrieval-only, temporal-only, and temporal plus reliability. The main metrics are preferred top1, pairwise preference success, mean preferred rank, preferred MRR, and stale-wins count. We also inspect per-query artifacts to verify that the temporal and reliability signals measurably alter ranking behavior.

## Scope Boundary

This method section is about Route A only. Route B is not part of the Route A method. Route C is out of scope.
