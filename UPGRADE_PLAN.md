# Upgrade Plan

## Chosen Mainline

The upgraded project will move from narrow temporal/reliability reranking to:

**Conflict-Aware Temporal Faithful RAG**

This name may change later, but the task definition will not: the mainline must be an answer-level RAG system that handles temporally sensitive or conflicting evidence while producing inspectable evidence attribution.

## Why This Direction

This direction is the best fit under current constraints:

- reuses the repository's strongest assets
- avoids the failed Route B main-method trap
- upgrades the project to a modern RAG problem
- remains feasible on a single A100 40G
- is easier to evaluate fairly than a graph-heavy or fully adaptive mega-system

## What Will Stay

- FEVER official retrieval as a controlled auxiliary retrieval benchmark
- Route A temporal/conflict slices as diagnostic datasets
- BM25 and retrieval infrastructure
- report and experiment organization patterns

## What Will Change

- main task becomes answer-level, not only rerank-level
- temporal/conflict signals must be derived from raw evidence text and source metadata
- the system must produce answer + evidence selection + citations
- evaluation must include answer correctness and attribution quality

## Proposed System Skeleton

1. query analysis / lightweight routing
2. retrieval
3. evidence scoring
4. conflict-aware arbitration
5. answer generation with citations
6. evaluation and error taxonomy

## Why Not Other Options

### Not Route B as main method

Route B failed the decisive criterion of beating a matched non-graph baseline.

### Not generation-only

A pure generator would discard the repository's strongest retrieval assets and weaken evidence-based claims.

### Not dense-heavy redesign

That would increase engineering risk and cost before the answer-level faithful pipeline is even established.

## Upgrade Stages

### Stage 0

Audit and freeze legacy assets.

### Stage 1

Define the new answer-level task, dataset stack, and experiment protocol.

### Stage 2

Implement the minimum runnable faithful RAG pipeline with retrieval, conflict arbitration, generation, and attribution.

### Stage 3

Run pilot experiments and sanity checks.

### Stage 4

Run formal baselines and ablations.

### Stage 5

Generate paper-facing materials.

## Success Condition

The upgrade succeeds only if the repository ends with:

- a stable answer-level pipeline
- fair baselines
- at least one main dataset and one auxiliary dataset
- evidence attribution artifacts
- structured error analysis
- paper-ready results tables and notes
