# HOH Larger Pilot Summary v6

## Run Group

- [pilot_hoh256_20260327_r6](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_hoh256_20260327_r6)

## Real Findings

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| vanilla_rag_extractive | 0.000 | 0.209 | 0.965 |
| stronger_retrieval_template | 0.219 | 0.304 | 0.965 |
| no_temporal | 0.242 | 0.331 | 0.969 |
| no_conflict | 0.234 | 0.328 | 0.965 |
| no_source | 0.250 | 0.345 | 0.965 |
| full_model | 0.250 | 0.345 | 0.965 |

## Gate Readout

- HOH now passes both the temporal-ablation and conflict-ablation criteria
- `full_model` beats `no_conflict`
- `source` remains unsupported as an independent gain
