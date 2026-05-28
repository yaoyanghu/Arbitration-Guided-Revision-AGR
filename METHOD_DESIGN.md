# Method Design

## Main Method

The upgraded system will be a **retrieve-then-arbitrate-then-generate** pipeline for conflict-aware temporal faithful RAG.

## Frozen Formal Mainline

The validated formal mainline is now frozen as:

- stronger retrieval
- temporal-aware answer extraction
- conflict-aware evidence arbitration
- citation-aware answer output

The `source/reliability` path is no longer part of the proven core contribution and should only appear as:

- appendix material
- limitation
- future work

## Input / Output Definition

### Input

- natural-language query
- retrievable evidence corpus
- optional source metadata available at corpus level

### Output

- final answer
- selected supporting evidence set
- citation or attribution mapping from answer to evidence
- optional conflict/arbitration trace for analysis

## Core Modules

### 1. Retrieval

Start with a fair and reproducible retriever stack:

- BM25 baseline
- stronger retrieval baseline if cost permits, under matched budget

### 2. Query Analysis

Lightweight routing or query characterization may be added, but only if it materially improves the answer-level task and stays fair.

### 3. Evidence Scoring

Each retrieved candidate may receive:

- lexical relevance score
- temporal salience score derived from raw text and dates
- conflict signal score derived from cross-evidence disagreement
- optional source prior derived from source metadata

Current formal claim only relies on the first three as validated contributors.

### 4. Conflict Arbitration

This is the real replacement for old Route A heuristics:

- compare competing evidence blocks
- prefer evidence sets that are better aligned with temporal recency and cross-source support
- penalize unsupported or outdated evidence when the text evidence supports that decision

### 5. Answer Generation

Generation will not rely on task-side labels. It will use:

- selected evidence bundle
- answer prompting with citation slots
- controlled context budgeting

### 6. Attribution

The system must export:

- chosen evidence passages
- mapping from answer claims to cited evidence
- artifacts that support case analysis

## Relationship To Legacy Assets

### Reused

- retrieval and indexing infrastructure
- score fusion utilities
- reporting patterns
- FEVER and Route A evaluation helpers where applicable

### Replaced

- direct consumption of `temporal_status`-style labels
- ranking-only endpoint as the main evaluation target
- graph-centric main contribution framing

## Minimal Viable Mainline

The first runnable upgraded system should include:

- BM25 retrieval
- text-derived temporal scoring
- text-derived conflict arbitration
- answer generation with citations
- answer-level evaluation

This is the minimum publishable system path. Anything more complex must be justified by real gains.
