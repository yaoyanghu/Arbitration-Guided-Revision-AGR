# TempRAGEval Pilot Summary

## Run Group

- [pilot_temprageval64_20260327](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_temprageval64_20260327)

## Dataset

- `TempRAGEval`
- `64` pilot queries
- `90` evidence documents

## Real Findings

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| parametric_only | 0.000 | 0.013 | 0.000 |
| vanilla_rag_extractive | 0.000 | 0.058 | 0.102 |
| stronger_retrieval_template | 0.000 | 0.102 | 0.102 |
| no_temporal | 0.000 | 0.102 | 0.102 |
| no_conflict | 0.000 | 0.102 | 0.102 |
| no_source | 0.000 | 0.109 | 0.102 |
| full_model | 0.000 | 0.109 | 0.102 |

## What This Means

1. TempRAGEval is now successfully connected as the preferred temporal auxiliary benchmark.
2. The current temporal answer extraction is still weak.
3. The main failure mode is retrospective temporal mention confusion, not total retrieval collapse.
4. This benchmark is now giving a useful and concrete debugging signal for the next generator/arbitration upgrade.

## Decision

- keep TempRAGEval as the preferred temporal auxiliary dataset
- prioritize temporal answer extraction fixes
- do not claim temporal gains until the pilot clearly improves over the current baseline
