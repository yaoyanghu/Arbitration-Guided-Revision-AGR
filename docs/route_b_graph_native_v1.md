# Route B Graph-Native v1

## Purpose

This experiment is the only allowed Route B survival test. It does not ask whether graph structure can beat Route A alone; it asks whether graph-native consistency or consensus can beat a matched non-graph baseline using the same information.

## How It Differs From Older Route B

Older Route B variants were largely local rule aggregation over edge-like signals. This version explicitly uses a consistency or consensus score over a local evidence graph built from Route A++ top-k artifacts.

## What Counts As Graph-Native Here

The graph-native part is not a single edge bonus. It is the consensus score computed from multi-node interaction:

- query-to-evidence support
- source-to-evidence corroboration
- evidence-to-evidence update and contradiction structure
- iterative or joint consistency over these relations

## Why A Matched Non-Graph Baseline Is Still Required

A matched non-graph baseline with access to the same local information is the only honest control. If the non-graph baseline can reproduce the gain, then the graph is not adding independent value.

## Success Standard

Route B survives only if graph-native consistency or consensus clearly beats the matched non-graph conflict aggregator on the held-out A++ test slice, especially in mixed hard cases.

## Failure Standard

If graph-native consistency ties or loses to the matched non-graph baseline, Route B stops as a main-method line and remains only an analysis layer.
