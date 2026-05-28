# Project Audit

## Scope

This audit covers the copied `New_ChronoRAG` workspace created from the legacy `ChronoRAG` repository. The goal is to decide what should remain as reusable infrastructure, what should be frozen as historical evidence, and what must be replaced to support a modern answer-level RAG system.

## Repository Snapshot

Top-level folders currently present:

- `configs/`
- `data/`
- `docs/`
- `indexes/`
- `logs/`
- `notes/`
- `papers_write/`
- `reports/`
- `runs/`
- `scripts/`
- `src/`
- `tests/`

The repository is not a clean modern RAG codebase yet. It is a layered research workspace containing:

- a reusable BM25-centered retrieval scaffold
- FEVER official retrieval assets
- Route A temporal/reliability slice experiments
- Route B graph experiments and audits
- FEVER short-paper notes and tables
- placeholder generation code

## What The Current Project Actually Does

### Current runnable backbone

The main runnable pipeline is still the old Route A entry in [src/eval/eval_main.py](D:/HUYAOYANG/Work/New_ChronoRAG/src/eval/eval_main.py):

- reads processed query JSONL
- runs BM25 retrieval through [src/retrieval/search.py](D:/HUYAOYANG/Work/New_ChronoRAG/src/retrieval/search.py)
- scores temporal signals with [src/temporal/label_relation.py](D:/HUYAOYANG/Work/New_ChronoRAG/src/temporal/label_relation.py)
- scores reliability with [src/reliability/source_score.py](D:/HUYAOYANG/Work/New_ChronoRAG/src/reliability/source_score.py)
- fuses scores with [src/rerank/rerank.py](D:/HUYAOYANG/Work/New_ChronoRAG/src/rerank/rerank.py)
- writes ranking-style artifacts under `runs/`

### What is missing for a modern RAG system

The current codebase does **not** yet provide a real answer-level RAG mainline:

- [src/generation/generate_answer.py](D:/HUYAOYANG/Work/New_ChronoRAG/src/generation/generate_answer.py) is only a placeholder
- there is no complete retrieve-then-generate pipeline with citations
- there is no answer-level metric package as the main evaluation target
- the strongest existing results are ranking-oriented, not answer-oriented

## Major Historical Lines In The Repo

### 1. FEVER official retrieval line

Status: keep

Why it matters:

- cleanest benchmark-style asset currently in the repo
- best controlled retrieval-only evaluation line
- useful as auxiliary experiment and sanity-check benchmark
- good for retrieval and evidence-selection diagnostics

Limit:

- by itself it is still not a modern answer-level RAG contribution

### 2. Route A temporal/reliability line

Status: keep as diagnostic foundation, but not as final task definition

Strongest package:

- `route_a_temporal_v4`
- fixed `dev/test`
- `120 queries / 40 events`
- balanced case coverage

What it proves:

- temporal evidence preference is real on the curated temporal-conflict setup
- reliability priors can help on part of the task
- the pipeline can support structured case analysis

Why it is still too narrow:

- task objective remains preferred-document ranking, not final answer generation
- data contract still contains construction-side fields such as `preferred_doc_id`, `stale_doc_ids`, `temporal_status`, `reliability_bucket`
- these fields are acceptable for evaluation and auditing, but should not remain primary model inputs in the upgraded mainline

### 3. Route B graph line

Status: freeze and downgrade

Evidence:

- [reports/FINAL_BRANCH_DECISION.md](D:/HUYAOYANG/Work/New_ChronoRAG/reports/FINAL_BRANCH_DECISION.md)
- Route B graph-native tied the matched non-graph baseline
- audits in `reports/AUDIT/` show task mismatch, ceiling effects, and historical leakage risk in older branches

Decision:

- Route B should not be the main method line in `New_ChronoRAG`
- it can survive only as an analysis layer or future appendix branch

### 4. FEVER short-paper assets

Status: preserve but downgrade from mainline

Why:

- useful tables, notes, and retrieval analyses already exist
- they are valid assets for controlled retrieval discussion
- but they are too narrow for the new project goal of modern faithful RAG

## Key Scientific Problems In The Legacy Setup

### 1. The current problem is too narrow

Most current experiments reward:

- ranking a preferred evidence document above stale alternatives

That is useful, but too small to sustain the upgraded paper target. It does not yet establish:

- answer-level correctness
- evidence-grounded generation
- citation fidelity
- conflict-aware answer arbitration

### 2. The current task exposes construction-side fields

The Route A family uses fields like:

- `preferred_doc_id`
- `stale_doc_ids`
- `temporal_status`
- `evidence_time`
- `source_type`
- `reliability_bucket`

These are valuable for diagnosis and evaluation, but cannot remain direct main-method inputs in the upgraded system without leakage concerns or unrealistic assumptions.

### 3. Graph did not earn independent method status

Route B failed its decisive criterion:

- it did not beat a matched non-graph baseline on the held-out graph-native test

This means:

- graph is not the right main contribution for the next paper
- forcing it back in would raise avoidable reviewer risk

### 4. Generation is missing

The repository has no completed answer-generation path. This is the biggest engineering and scientific gap between the current project and a modern RAG system.

## Reusable Assets

These modules are worth reusing into the upgraded repo:

- [src/common.py](D:/HUYAOYANG/Work/New_ChronoRAG/src/common.py)
- [src/data/prepare_fever.py](D:/HUYAOYANG/Work/New_ChronoRAG/src/data/prepare_fever.py)
- [src/retrieval/build_bm25.py](D:/HUYAOYANG/Work/New_ChronoRAG/src/retrieval/build_bm25.py)
- [src/retrieval/search.py](D:/HUYAOYANG/Work/New_ChronoRAG/src/retrieval/search.py)
- [src/rerank/rerank.py](D:/HUYAOYANG/Work/New_ChronoRAG/src/rerank/rerank.py)
- experiment directory conventions under `runs/`, `logs/`, `reports/`
- casebook and audit writing patterns already used in Route A and Route B

These assets are useful mostly as:

- retrieval infrastructure
- score fusion utilities
- data formatting helpers
- report skeletons

## Modules To Freeze

Freeze as historical checkpoints, not active mainline:

- `reports/route_a_temporal_v1/`
- `reports/route_a_temporal_v2/`
- `reports/route_a_temporal_v3/`
- `reports/route_a_temporal_v4/`
- `reports/route_b_graph_v1/`
- `reports/route_b_graph_v2/`
- `reports/route_b_graph_v3_holdout/`
- `reports/route_b_graph_native_v1/`
- `reports/AUDIT/`
- FEVER short-paper notes under `notes/` that are specific to the old retrieval paper framing

## Modules To Downgrade Or Abandon As Mainline

Downgrade:

- Route B graph code and reports: analysis only
- old FEVER short-paper framing: auxiliary controlled retrieval line

Abandon as main-task definition:

- small-slice preferred-doc ranking as the final paper endpoint
- any method path that consumes explicit task-side labels as direct decision signals

## Main Upgrade Decision

The safest and most publishable next mainline is:

**Conflict-Aware Temporal Faithful RAG**

Core idea:

- retrieve evidence from raw text
- identify temporal and conflict signals from evidence text and source metadata, not from task-side labels
- arbitrate across conflicting evidence
- generate answer-level outputs with evidence attribution

## New Mainline Narrative

The upgraded repo should treat existing assets as follows:

- FEVER official retrieval: controlled auxiliary retrieval benchmark
- Route A temporal/reliability slices: diagnostic and stress-test benchmark
- Route B graph: analysis-only historical branch
- new main contribution: answer-level conflict-aware faithful RAG

## Audit Conclusion

`New_ChronoRAG` already contains enough retrieval, logging, and diagnostic infrastructure to bootstrap a new mainline. However, the old repository is still centered on narrow ranking experiments. The biggest necessary shift is:

1. stop treating task-side temporal labels as primary method inputs
2. move from reranking-only outputs to answer-level outputs
3. keep FEVER and Route A as controlled support assets
4. rebuild the main contribution around faithful answer generation with explicit evidence attribution

This is a viable upgrade path and is lower risk than trying to rescue Route B or keep polishing the old slice-ranking story.
