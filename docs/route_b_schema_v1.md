# Route B Schema v1

## Purpose

This document defines the minimal input and output contract for Route B after Route A hardening.

Route B is not a full graph research track in this version.

This version only prepares a minimal prototype that operates on Route A hardened subset artifacts.

## Scope Boundary

Included:

- local graph construction over Route A hardened subset top-k candidates
- rule-based edge creation
- query-level graph inspection
- small-scale reranking support analysis

Explicitly excluded:

- full graph construction over a large corpus
- graph propagation research
- Route C
- generation
- sentence-level attribution
- dense retrieval
- large sweep or full-dev run

## Input Contract

Route B v1 should consume the hardened Route A outputs from:

- [route_a_temporal_v2_subset.jsonl](D:/HUYAOYANG/Work/ChronoRAG/data/processed/route_a_temporal_v2_subset.jsonl)
- [route_a_temporal_v2_corpus.jsonl](D:/HUYAOYANG/Work/ChronoRAG/data/corpus/route_a_temporal_v2_corpus.jsonl)
- [retrieval_results.jsonl](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v2/retrieval_results.jsonl)
- [temporal_reranked_results.jsonl](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v2/temporal_reranked_results.jsonl)
- [reranked_results.jsonl](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v2/reranked_results.jsonl)
- [per_query_artifacts.jsonl](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v2/per_query_artifacts.jsonl)

### Query Node

Each query node should contain at least:

- `query_id`
- `query`
- `query_time`
- `entity`
- `focus_attribute`
- `preferred_doc_id`
- `case_type`

### Evidence Node

Each evidence node should contain at least:

- `doc_id`
- `title`
- `text`
- `source`
- `source_type`
- `timestamp`
- `evidence_time`
- `temporal_status`
- `reliability_bucket`
- retrieval and reranking scores already produced by Route A

### Optional Source Node

If Route B v1 includes a source node, it should be lightweight and only store:

- `source`
- `source_type`
- `reliability_bucket`

No richer source graph is needed in v1.

## Edge Contract

Allowed edge types in Route B v1:

- `support`
- `contradict`
- `update`
- `corroborate`

### Rule-Based Edge Definitions

`support`

- connect evidence nodes whose text expresses compatible claims about the same entity and attribute

`contradict`

- connect evidence nodes that express incompatible states for the same entity and attribute

`update`

- connect an older stale candidate to a newer updated candidate when the query time and evidence time imply replacement

`corroborate`

- connect a candidate to another candidate or source node when they share the same updated state with stronger reliability

All edges in v1 must be rule-based and auditable from the artifact text.

## Output Contract

Route B v1 should eventually write to a dedicated directory such as:

- `runs/route_b_minimal_v1/`
- `logs/route_b_minimal_v1/`
- `reports/route_b_minimal_v1/`

Expected output artifacts:

- per-query graph json
- per-query edge list
- graph-aware reranked candidate list
- casebook-style markdown summary
- small metrics json comparing Route A final vs Route B prototype

## Minimal Evaluation Targets

Route B v1 should only answer these questions:

1. can a local graph be built from Route A hardened top-k candidates
2. do rule-based edges expose temporal conflict structure clearly
3. does graph-aware reranking help at least some hard cases left unresolved by Route A final reranking
4. are the outputs still query-level inspectable

## Reused Route A Artifacts

Route B v1 should explicitly reuse:

- Route A hardened subset contract
- Route A retrieval backbone
- Route A temporal score
- Route A reliability score
- Route A per-query artifacts

This keeps Route B grounded in the already accepted Route A checkpoint rather than starting a separate pipeline.
