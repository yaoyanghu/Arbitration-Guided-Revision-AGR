# Route B Entry Gate v1

## Purpose

This document defines the exact gate that must be satisfied before any Route B prototype run is allowed.

It does not authorize a Route B main experiment.

## 1. Route A v2 Preconditions

Route B prototype run is allowed only if Route A v2 satisfies all of the following:

1. Route A pipeline runs end to end on the hardened subset
2. query count is at least `30`
3. retrieval-only, temporal-only, and temporal-plus-reliability show ordered behavior:
   - `retrieval-only < temporal-only <= temporal-plus-reliability`
4. temporal changed ranking count is not `0`
5. reliability helped count is not `0`
6. final pairwise preference success beats retrieval-only baseline
7. per-query inspectable artifacts exist and remain readable
8. v2 is interpreted as a harder checkpoint, not as a collapsed rerun of v1

## 2. Current Gate Status

Based on [ACCEPTANCE_CHECK.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v2/ACCEPTANCE_CHECK.md) and [V1_VS_V2_DIFF.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v2/V1_VS_V2_DIFF.md), the current Route A v2 checkpoint satisfies the prototype-entry gate.

That means:

- Route B schema work is justified
- Route B prototype planning is justified

It does not mean:

- Route B main experiment is justified
- Route B has already been validated

## 3. If Route A v2 Is Not Stable

If Route A v2 is later found unstable, Route B should pause at schema level only.

Correct response:

- pause Route B run work
- keep Route B docs only
- return to Route A debugging and subset repair

## 4. If Graph Adds No Net Gain

If a later Route B prototype run shows no net gain over Route A final reranking, Route B should be downgraded from a candidate retrieval module to an analysis module.

That means it may still be useful for:

- interpreting conflict structure
- exposing support or contradiction relations
- producing case studies

But it should not be promoted as a retrieval improvement module without measurable benefit.

## 5. Hard Boundary

Even when the gate is satisfied, the next allowed step is only:

- Route B minimal prototype run

The following remain disallowed:

- Route B main experiment
- Route C
- generation
- full graph
- graph propagation research
- large sweep
