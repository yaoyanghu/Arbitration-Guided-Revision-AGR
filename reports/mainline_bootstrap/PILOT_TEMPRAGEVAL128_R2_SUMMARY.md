# TempRAGEval Larger Pilot Summary v2

## Run Group

- [pilot_temprageval128_20260327_r2](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_temprageval128_20260327_r2)

## Real Findings

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| vanilla_rag_extractive | 0.000 | 0.089 | 0.117 |
| stronger_retrieval_template | 0.203 | 0.268 | 0.117 |
| no_temporal | 0.133 | 0.198 | 0.117 |
| no_conflict | 0.203 | 0.268 | 0.117 |
| no_source | 0.203 | 0.268 | 0.117 |
| full_model | 0.203 | 0.268 | 0.117 |

## Gate Readout

- full_model now clearly beats no_temporal
- temporal extraction fix is validated
- conflict/source modules still do not separate
