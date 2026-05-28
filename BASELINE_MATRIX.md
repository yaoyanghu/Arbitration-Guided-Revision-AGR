# Baseline Matrix

## Mainline Baselines

| baseline | status | retrieval | generation | temporal | conflict | source/reliability | role |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `parametric_only` | implemented | none | query-only placeholder | no | no | no | lower-bound sanity baseline |
| `vanilla_rag_extractive` | implemented | BM25 | extractive | no | no | no | vanilla answer-level baseline |
| `stronger_retrieval_template` | implemented | BM25 + stronger lexical weighting | local instruct template | no | no | no | stronger non-temporal baseline |
| `hyde_like` | implemented | BM25 + hypothetical query expansion | local instruct template | no | no | no | lightweight external-style retrieval competitor |
| `crag_like` | implemented | BM25 + confidence-aware corrective retrieval | local instruct template | no | no | no | lightweight external-style corrective-retrieval competitor |
| `self_rag_style_baseline` | implemented | BM25 + self-reflective style query reformulation | local instruct template | no | no | no | repository-matched style baseline, not an official Self-RAG reproduction |
| `astute_style_baseline` | implemented | BM25 + conflict-robust style query reformulation | local instruct template | no | no | no | repository-matched style baseline, not an official Astute RAG reproduction |
| `no_temporal` | implemented | BM25 | citation-aware template | no | yes | yes | ablation |
| `no_conflict` | implemented | BM25 | citation-aware template | yes | no | yes | ablation |
| `no_structured` | implemented | BM25 | citation-aware template | yes | yes | yes | first-layer ablation for structured arbitration |
| `no_learned` | implemented | BM25 | citation-aware template | yes | yes | yes | second-layer ablation for lightweight learned scorer |
| `no_abstention` | implemented | BM25 | citation-aware template | yes | yes | yes | third-layer ablation for trustworthy generation / refusal |
| `no_source` | implemented | BM25 | citation-aware template | yes | yes | no | ablation |
| `full_model` | implemented | BM25 | citation-aware template | yes | yes | yes | current full pilot model |

## Notes

- these are pilot-grade baselines, not yet formal paper settings
- a true stronger retrieval baseline may later upgrade to hybrid retrieval if the environment supports it fairly
- a true local instruct generator may later upgrade from template mode to a local model-backed generator
- `hyde_like` and `crag_like` are intentionally lightweight, fair, same-budget approximations for competitor-style comparison rather than claimed full reproductions of the original external systems
- `self_rag_style_baseline` and `astute_style_baseline` are repository-matched style baselines only; they are not official full reproductions of Self-RAG or Astute RAG
- `no_structured` only disables the new lightweight structured arbitration layer; it does not reopen Route B or add a graph-style method path
- `no_learned` only disables the lightweight reranker layer trained on pilot supervision; it is not part of the frozen formal mainline
- `no_abstention` disables the trustworthy-generation rejection layer and should be treated as a faithfulness-control comparison rather than a new retrieval or reasoning baseline
- none of these pilot baselines are allowed to consume Route A construction labels as direct inputs
