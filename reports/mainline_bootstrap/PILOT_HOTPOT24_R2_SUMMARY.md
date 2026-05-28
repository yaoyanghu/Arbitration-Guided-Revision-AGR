# HotpotQA Pilot Round 1 Summary

## Run Group

- [pilot_hotpot24_20260327_r2](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_hotpot24_20260327_r2)

## Dataset

- `HotpotQA distractor`
- `24` streamed validation queries
- `240` corpus documents built from distractor contexts

## Real Findings

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| parametric_only | 0.000 | 0.070 | 0.000 |
| vanilla_rag_extractive | 0.000 | 0.027 | 0.563 |
| stronger_retrieval_template | 0.167 | 0.167 | 0.563 |
| no_temporal | 0.000 | 0.067 | 0.521 |
| no_conflict | 0.000 | 0.067 | 0.563 |
| no_source | 0.000 | 0.067 | 0.542 |
| full_model | 0.000 | 0.067 | 0.542 |

## What This Means

1. The new answer-level pipeline is genuinely running on real public QA data.
2. The main engineering gap is still answer generation and span extraction.
3. Temporal and conflict scoring are not helping on this first Hotpot slice, which is acceptable because this dataset is being used as a pilot/backbone set rather than as the final temporal benchmark.
4. The current strongest pilot variant is a stronger non-temporal retrieval-plus-template baseline, not the full conflict-aware model.

## Decision

- keep HotpotQA as the pilot backbone
- do not overclaim temporal/conflict gains from this pilot
- continue toward HOH and a temporal-sensitive auxiliary validation set
