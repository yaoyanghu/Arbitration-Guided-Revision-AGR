# TempRAGEval Formal Summary

## Run Group

- [formal_temprageval1244_20260327](D:/HUYAOYANG/Work/New_ChronoRAG/runs/formal_temprageval1244_20260327)

## Auxiliary Table

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| stronger_retrieval_template | 0.061 | 0.092 | 0.131 |
| no_temporal | 0.048 | 0.083 | 0.131 |
| full_model | 0.061 | 0.092 | 0.132 |

## Formal Readout

- `full_model` keeps the temporal gain over `no_temporal`
- the auxiliary temporal benchmark does not add new independent evidence for conflict or source
- this dataset remains a temporal validator, not a full-stack proof set
