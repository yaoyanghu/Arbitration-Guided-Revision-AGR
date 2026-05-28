# TempRAGEval Larger Pilot Summary v5

## Run Group

- [pilot_temprageval128_20260327_r5](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_temprageval128_20260327_r5)

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

- TempRAGEval still passes the temporal-ablation criterion
- `full_model` continues to beat `no_temporal`
- conflict/source contributions still do not separate from the reduced variants
