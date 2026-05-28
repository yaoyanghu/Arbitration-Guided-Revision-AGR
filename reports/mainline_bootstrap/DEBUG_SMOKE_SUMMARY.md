# Debug Smoke Summary

## Run

- config: [conflict_aware_rag_smoke.yaml](D:/HUYAOYANG/Work/New_ChronoRAG/configs/conflict_aware_rag_smoke.yaml)
- run dir: [debug_conflict_aware_rag_smoke_20260327_r2](D:/HUYAOYANG/Work/New_ChronoRAG/runs/debug_conflict_aware_rag_smoke_20260327_r2)

## Purpose

This run exists only to verify that the new answer-level mainline can:

- load the unified query contract
- retrieve evidence
- score temporal/conflict/reliability signals from raw evidence fields
- select evidence bundles
- generate an answer artifact with citations
- write answer-level outputs and debug metrics

## Outcome

- status: `passed`
- query count: `2`
- exact match: `0.000`
- token F1: `0.168`
- citation title recall: `1.000`

## Interpretation

- the pipeline wiring works
- citation-bearing outputs are produced
- current generation remains a lightweight extractive baseline
- this run is debug-only and not formal evidence for the paper
