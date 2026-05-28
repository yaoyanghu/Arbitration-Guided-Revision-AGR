# Formal Ablation Table

## HOH Main Ablation

| variant | EM | token F1 | delta vs full (EM) | delta vs full (F1) |
| --- | ---: | ---: | ---: | ---: |
| no_temporal | 0.181 | 0.268 | -0.008 | -0.012 |
| no_conflict | 0.181 | 0.270 | -0.008 | -0.009 |
| full_model | 0.188 | 0.279 | 0.000 | 0.000 |

## TempRAGEval Auxiliary Ablation

| variant | EM | token F1 | delta vs full (EM) | delta vs full (F1) |
| --- | ---: | ---: | ---: | ---: |
| no_temporal | 0.048 | 0.083 | -0.013 | -0.010 |
| full_model | 0.061 | 0.092 | 0.000 | 0.000 |

## Readout

- temporal is the cleanest independently validated component across both datasets
- conflict shows independent value on HOH
- source is intentionally excluded because it did not separate from the frozen full model during pilot gating
