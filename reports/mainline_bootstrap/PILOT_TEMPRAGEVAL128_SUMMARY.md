# TempRAGEval Larger Pilot Summary

## Run Group

- [pilot_temprageval128_20260327](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_temprageval128_20260327)

## Dataset

- `TempRAGEval`
- `128` pilot queries
- `204` evidence documents

## Real Findings

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| vanilla_rag_extractive | 0.000 | 0.089 | 0.117 |
| stronger_retrieval_template | 0.203 | 0.268 | 0.117 |
| no_temporal | 0.203 | 0.268 | 0.117 |
| no_conflict | 0.203 | 0.268 | 0.117 |
| no_source | 0.203 | 0.268 | 0.117 |
| full_model | 0.203 | 0.268 | 0.117 |

## Gate Readout

- EM is no longer zero
- the temporal year-constraint fix is working
- but the gain is shared by the ablations, so the full model still lacks unique separation

## Decision

- keep TempRAGEval as the temporal failure probe
- continue targeted temporal extraction and evidence discrimination fixes before formal
