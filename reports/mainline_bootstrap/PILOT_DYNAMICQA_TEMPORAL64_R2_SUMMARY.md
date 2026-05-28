# DynamicQA Temporal Pilot Summary

## Run Group

- [pilot_dynamicqa_temporal64_20260327_r2](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_dynamicqa_temporal64_20260327_r2)

## Dataset

- `DynamicQA temporal`
- `64` pilot queries
- `64` context-backed corpus documents

## Real Findings

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| parametric_only | 0.000 | 0.000 | 0.000 |
| vanilla_rag_extractive | 0.000 | 0.000 | 1.000 |
| stronger_retrieval_template | 0.000 | 0.000 | 1.000 |
| no_temporal | 0.000 | 0.000 | 1.000 |
| no_conflict | 0.000 | 0.000 | 1.000 |
| no_source | 0.000 | 0.000 | 1.000 |
| full_model | 0.000 | 0.000 | 1.000 |

## What This Means

1. Retrieval and citation selection work.
2. The direct answer-level task is blocked by `[ENTITY]` placeholders in the provided context.
3. This fallback dataset is not currently suitable as the main temporal answer-level validation set for the present pipeline.

## Decision

- keep DynamicQA temporal only as a temporary fallback reference
- do not use it as decisive evidence for the main paper route
- continue preferring HOH and keep TempRAGEval as the desired but access-blocked target
