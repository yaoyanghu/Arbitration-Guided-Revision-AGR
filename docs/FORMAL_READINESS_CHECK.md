# Formal Readiness Check

## Status

`passed`

## Frozen Mainline

- stronger retrieval backbone
- temporal-aware answer extraction
- conflict-aware evidence arbitration
- citation-aware answer output

`source/reliability` is no longer part of the frozen main claim.

## Preconditions

### Dataset contract

- status: `passed`
- evidence:
  - [UNIFIED_DATA_CONTRACT.md](D:/HUYAOYANG/Work/New_ChronoRAG/docs/UNIFIED_DATA_CONTRACT.md)
  - [conflict_aware_rag_hoh_formal_1024.yaml](D:/HUYAOYANG/Work/New_ChronoRAG/configs/conflict_aware_rag_hoh_formal_1024.yaml)
  - [conflict_aware_rag_temprageval_formal_1244.yaml](D:/HUYAOYANG/Work/New_ChronoRAG/configs/conflict_aware_rag_temprageval_formal_1244.yaml)

### Baseline matrix

- status: `passed`
- frozen formal subset:
  - HOH: `stronger_retrieval_template`, `no_temporal`, `no_conflict`, `full_model`
  - TempRAGEval: `stronger_retrieval_template`, `no_temporal`, `full_model`

### Config freeze

- status: `passed`
- note:
  - formal configs now carry `run_stage: formal`
  - `reliability_weight` is frozen to `0.0` in formal configs

### Output contract

- status: `passed`
- note:
  - formal runs will still emit `predicted_answer`, `selected_evidence`, `citations`, and `arbitration_trace`

### Leakage audit

- status: `passed`
- note:
  - the formal mainline does not consume `preferred_doc_id`, `stale_doc_ids`, `temporal_status`, `case_type`, or similar construction-only labels as scoring inputs

### Naming and directory hygiene

- status: `passed`
- note:
  - formal run groups will use `formal_*`
  - pilot and formal outputs remain separated by run-group names and config files

## Conclusion

The project is ready to launch the minimal formal plan without reopening exploratory pilot work.
