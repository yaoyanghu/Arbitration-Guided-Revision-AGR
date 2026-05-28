# HOH Larger Pilot Summary

## Run Group

- [pilot_hoh256_20260327](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_hoh256_20260327)

## Dataset

- `HOH`
- `256` pilot queries
- `256` context-backed corpus documents

## Real Findings

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| vanilla_rag_extractive | 0.000 | 0.192 | 0.969 |
| stronger_retrieval_template | 0.098 | 0.143 | 0.969 |
| no_temporal | 0.102 | 0.145 | 0.969 |
| no_conflict | 0.098 | 0.143 | 0.969 |
| no_source | 0.102 | 0.145 | 0.969 |
| full_model | 0.102 | 0.145 | 0.969 |

## Gate Readout

- `full_model` is not worse than the key ablations
- but it also does not clearly beat `no_temporal` or `no_source`
- therefore the HOH formal gate is not yet passed

## Decision

- stay in pilot mode
- prioritize better answer discrimination over larger-scale formal runs
