# HOH Formal Summary

## Run Group

- [formal_hoh1024_20260327](D:/HUYAOYANG/Work/New_ChronoRAG/runs/formal_hoh1024_20260327)

## Main Table

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| stronger_retrieval_template | 0.168 | 0.250 | 0.947 |
| no_temporal | 0.181 | 0.268 | 0.947 |
| no_conflict | 0.181 | 0.270 | 0.945 |
| full_model | 0.188 | 0.279 | 0.945 |

## Formal Readout

- `full_model` beats `no_temporal`
- `full_model` beats `no_conflict`
- `source` is not part of this formal table because it did not pass the pilot gate
- the formal HOH result supports a frozen mainline of:
  - stronger retrieval
  - temporal-aware answer extraction
  - conflict-aware evidence arbitration
