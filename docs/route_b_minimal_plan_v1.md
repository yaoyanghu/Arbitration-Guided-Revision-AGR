# Route B Minimal Plan v1

## High-Level Goal

Build a minimal Route B prototype on top of the hardened Route A subset, without turning it into a full graph experiment.

The purpose is to test whether a small local evidence graph can help a few remaining temporal-conflict cases after Route A reranking.

## Preconditions

Route B should only start from the hardened Route A checkpoint:

- [route_a_hardening_plan_v1.md](D:/HUYAOYANG/Work/ChronoRAG/docs/route_a_hardening_plan_v1.md)
- [RESULT_SUMMARY.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v2/RESULT_SUMMARY.md)
- [ACCEPTANCE_CHECK.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v2/ACCEPTANCE_CHECK.md)
- [CASEBOOK.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v2/CASEBOOK.md)
- [NEXT_STEP_DECISION.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v2/NEXT_STEP_DECISION.md)

Route A hardened gate is now satisfied, but that only authorizes a Route B prototype.

It does not authorize a Route B main experiment.

## Minimal Prototype Design

### 1. Candidate Window

Use only Route A hardened subset top-k candidates per query.

Recommended v1 setting:

- top-k from Route A final artifacts
- no corpus-wide graph expansion
- no neighbor crawling outside current query candidates

### 2. Nodes

Minimal node inventory:

- one query node
- k evidence nodes
- optional source nodes if source-aware edges are easier to explain

### 3. Edges

Only use rule-based edges:

- `support`
- `contradict`
- `update`
- `corroborate`

No learned edge classifier.

No multi-hop propagation research in v1.

### 4. Graph-Aware Reranking Goal

The prototype should try to improve only the remaining hard cases where Route A final reranking is still not clearly optimal.

Success should be defined conservatively:

- a few cases improved is enough
- zero large-scale claim should be made
- casebook evidence matters more than aggregate numbers at this stage

## Minimal Evaluation Metrics

Route B prototype should report only:

- preferred top1 rate
- pairwise preference success rate
- count of cases improved over Route A final reranking
- count of cases regressed vs Route A final reranking
- number of queries with readable graph artifacts

Case-oriented outputs should remain primary.

## Recommended Execution Order

1. freeze Route A hardened checkpoint
2. build graph input formatter from Route A per-query artifacts
3. implement rule-based edge builder
4. generate per-query graph artifacts for a tiny pilot slice first
5. run minimal Route B prototype on the hardened subset
6. write casebook and acceptance note

## Files Likely Needed Later

These are planning targets only for the next round:

- `src/graph/build_route_b_local_graph.py`
- `src/graph/score_route_b_edges.py`
- `src/eval/eval_route_b_minimal.py`
- `src/analysis/route_b_casebook.py`

No code is added in this document.

## Hard Exclusions

Do not do any of the following in Route B v1:

- full graph over the full corpus
- graph propagation research as a main claim
- Route C
- generation
- large sweep
- dense retrieval
- sentence-level attribution

## Route B Readiness Decision

If Route B prototype is started in the next round, it should be judged only on whether the local graph adds interpretable value on top of Route A hardened artifacts.

If it does not, Route B should be narrowed further instead of expanded.
