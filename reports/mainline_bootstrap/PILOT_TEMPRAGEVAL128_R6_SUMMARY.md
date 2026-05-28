# TempRAGEval Larger Pilot Summary v6

## Run Group

- [pilot_temprageval128_20260327_r6](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_temprageval128_20260327_r6)

## Real Findings

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| vanilla_rag_extractive | 0.000 | 0.089 | 0.117 |
| stronger_retrieval_template | 0.219 | 0.272 | 0.117 |
| no_temporal | 0.133 | 0.198 | 0.117 |
| no_conflict | 0.219 | 0.272 | 0.121 |
| no_source | 0.219 | 0.272 | 0.121 |
| full_model | 0.219 | 0.272 | 0.121 |

## Gate Readout

- TempRAGEval still validates the temporal path
- conflict and source remain neutral on this auxiliary benchmark
- the auxiliary role stays temporal, not full-stack proof
