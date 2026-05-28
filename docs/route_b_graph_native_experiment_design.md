# Route B Graph-Native Experiment Design

## Goal

Design exactly one experiment that could still justify keeping Route B alive as a method line.

## The Only Acceptable Question

Why can a matched non-graph baseline not implement the same gain?

If this cannot be answered cleanly, Route B should not continue as a main method line.

## Proposed Single Experiment

### Graph-Native Consistency / Consensus Test

Use the existing Route A hardened artifacts and construct cases where the preferred evidence is not recoverable from any single local cue alone, but only from multi-edge consistency across a small local graph.

The graph-native requirement is:

- One evidence node gives an `update` cue
- Another gives a `corroborate` cue
- A third provides a `contradict` relation against the stale alternative
- The preferred outcome should depend on the joint consistency of these relations, not on any one candidate’s local score

## Why This Could Be Graph-Native

A matched non-graph baseline can replicate any decision that reduces to:

- local feature summation
- case-type heuristics
- hand-coded candidate rescoring

So the only remaining chance for Route B is to show that the winning decision depends on relation structure across multiple nodes, where the value comes from coordinated agreement and conflict, not from a single candidate’s aggregated local features.

## Required Control

The control must be a matched non-graph aggregator with access to exactly the same local evidence fields.

If the non-graph control can still reproduce the gain, then Route B is not graph-native in practice.

## Success Criterion

Route B is worth keeping alive only if:

1. `full_graph` beats the matched non-graph control on held-out consistency/conflict cases
2. the gain is attributable to multi-node relation structure rather than hand-coded local rescoring
3. the resulting cases are interpretable enough to show why graph structure matters

## Failure Criterion

If the matched non-graph baseline can still match the gain, then Route B should be permanently downgraded from “method candidate” to “analysis / conflict-focused module.”

## Current Recommendation

At this moment, Route B does not yet justify further method expansion.
This experiment is the only remaining defensible chance for Route B as a main-method candidate.
