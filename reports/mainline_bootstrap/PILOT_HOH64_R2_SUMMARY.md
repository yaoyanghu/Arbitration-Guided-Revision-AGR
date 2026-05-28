# HOH Pilot Round 1 Summary

## Run Group

- [pilot_hoh64_20260327_r2](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_hoh64_20260327_r2)

## Dataset

- `HOH`
- `64` pilot queries
- `64` context-backed corpus documents

## Real Findings

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| parametric_only | 0.000 | 0.041 | 0.000 |
| vanilla_rag_extractive | 0.000 | 0.214 | 1.000 |
| stronger_retrieval_template | 0.188 | 0.246 | 1.000 |
| no_temporal | 0.188 | 0.257 | 1.000 |
| no_conflict | 0.188 | 0.257 | 1.000 |
| no_source | 0.188 | 0.257 | 1.000 |
| full_model | 0.188 | 0.257 | 1.000 |

## What This Means

1. HOH is now connected as a real answer-level pilot benchmark.
2. The minimal answer extraction upgrade materially improved answer-level metrics.
3. Temporal/conflict weighting is not yet the discriminative win on this first HOH pilot slice.
4. The pipeline has moved from wiring risk to method-quality risk.

## Decision

- keep HOH as the highest-priority main-result dataset
- continue improving the minimal generator and arbitration quality
- do not overclaim temporal/conflict gains until they clearly separate from the ablations
