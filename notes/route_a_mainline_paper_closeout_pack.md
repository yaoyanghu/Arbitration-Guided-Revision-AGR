# Route-Axis Paper Closeout Pack

## Problem Statement

Existing retrieval-centric temporal/conflict experiments are too narrow to support a modern RAG paper by themselves. The upgraded New_ChronoRAG mainline instead targets answer-level grounded generation under temporally sensitive and potentially conflicting evidence, while keeping legacy retrieval assets only as controlled auxiliary benchmarks.

## Method Overview

The frozen formal method is a retrieve-then-arbitrate-then-generate system with four validated layers:

1. stronger lexical retrieval
2. temporal-aware answer extraction
3. conflict-aware evidence arbitration
4. citation-aware answer output

The method does not use construction-side labels such as `temporal_status`, `preferred_doc_id`, `stale_doc_ids`, or `reliability_bucket` as direct scoring inputs.

## Dataset Section Draft

- `HOH formal 1024` is the main answer-level result set.
- `TempRAGEval formal 1244` is the temporal auxiliary validation set.
- `FEVER official retrieval` is preserved as a controlled retrieval-only auxiliary benchmark.
- `HotpotQA` remains engineering backbone / pilot only.
- `Route A` remains a diagnostic stress asset.
- `Route B` remains frozen as analysis layer only.

## Experimental Setup Draft

- matched retrieval budget across variants
- fixed top-k retrieval and evidence bundle size
- fixed formal variant set:
  - stronger retrieval baseline
  - no-temporal ablation
  - no-conflict ablation on HOH
  - full model
- answer-level metrics:
  - exact match
  - token F1
  - citation title recall

## Main Results Draft

On `HOH formal 1024`, the frozen full model improves over both `no_temporal` and `no_conflict`, supporting the claim that temporal-aware answer extraction and conflict-aware evidence arbitration both contribute to the answer-level mainline. On `TempRAGEval formal 1244`, the full model continues to outperform `no_temporal`, confirming that temporal extraction remains useful outside the main dataset, although this auxiliary benchmark does not independently validate conflict arbitration.

## Ablation Draft

The cleanest validated contribution is the temporal path. Conflict arbitration shows a smaller but still measurable benefit on HOH. In contrast, source/reliability does not produce independent gains under the current datasets and is therefore excluded from the main claim.

## Case Study Draft

The strongest success cases fall into two families:

- temporal disambiguation under retrospective year mentions
- same-title conflict resolution where fresh and stale evidence disagree on answer-bearing values

Representative failures still come from:

- wrong entity family selected under near-duplicate statistics
- stale secondary evidence leaking into final answer phrasing
- relation-sensitive temporal queries where several years remain admissible but only one is semantically correct

## Limitations Draft

- source/reliability is wired but not empirically validated as a core gain
- TempRAGEval remains an auxiliary validator rather than a full-stack proof set
- some HOH failures now sit at the boundary between evidence discrimination and final answer synthesis
- the system is still heuristic-heavy in answer extraction and conflict handling

## Reproducibility Note

The formal mainline is frozen in:

- [FORMAL_MAINLINE_RUN_PLAN.md](D:/HUYAOYANG/Work/New_ChronoRAG/docs/FORMAL_MAINLINE_RUN_PLAN.md)
- [FORMAL_DATASET_MANIFEST.md](D:/HUYAOYANG/Work/New_ChronoRAG/docs/FORMAL_DATASET_MANIFEST.md)
- [FORMAL_READINESS_CHECK.md](D:/HUYAOYANG/Work/New_ChronoRAG/docs/FORMAL_READINESS_CHECK.md)

Formal runs:

- [formal_hoh1024_20260327](D:/HUYAOYANG/Work/New_ChronoRAG/runs/formal_hoh1024_20260327)
- [formal_temprageval1244_20260327](D:/HUYAOYANG/Work/New_ChronoRAG/runs/formal_temprageval1244_20260327)
