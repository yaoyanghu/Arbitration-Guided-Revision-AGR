# HOH Larger Pilot Summary v5

## Run Group

- [pilot_hoh256_20260327_r5](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_hoh256_20260327_r5)

## Real Findings

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| vanilla_rag_extractive | 0.000 | 0.209 | 0.965 |
| stronger_retrieval_template | 0.219 | 0.304 | 0.965 |
| no_temporal | 0.219 | 0.301 | 0.965 |
| no_conflict | 0.234 | 0.328 | 0.965 |
| no_source | 0.234 | 0.328 | 0.965 |
| full_model | 0.234 | 0.328 | 0.965 |

## Gate Readout

- HOH now passes the temporal-ablation criterion
- `full_model` now beats `no_temporal`
- conflict/source contributions still do not separate from the reduced variants
