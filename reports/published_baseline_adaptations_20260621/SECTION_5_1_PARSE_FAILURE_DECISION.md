# Section 5.1 Parse-Failure Decision

## Decision

- **RARR-FP adaptation:** keep the existing results. Its parse-failure rates are 0.78% (HOH), 3.86% (TempRAGEval), and 1.20% (TimeQA), below the 10-point fairness threshold. Failed RARR rows were not automatically zero-scored: several had non-zero F1 or exact match.
- **FaithfulRAG-inspired FP control:** use the parse-repaired sensitivity results, not the original numbers, if reporting numeric results. The original TimeQA parse-failure rate was 10.40%, and all flagged rows had F1=0 because truncated/wrapped fact JSON was discarded, leaving the answer stage with empty facts.

## Repair Scope

Only the answer stage was rerun for 106 rows whose raw extraction contained recoverable complete fact objects. Five TempRAGEval rows remained conservatively unrecoverable. No retrieval, evidence change, gold prompt input, or AGR signal was used. The other 2,662 FaithfulRAG rows were not rerun.

| Dataset | Old parse rate | New parse rate | Repaired |
|---|---|---|---|
| HOH-1024 | 2.44% | 0.00% | 25 |
| TempRAGEval-1244 | 2.73% | 0.40% | 29 |
| TimeQA-500 | 10.40% | 0.00% | 52 |

FaithfulRAG-inspired mean EM changed from **6.47%** to **6.70%**; mean F1 changed from **11.49%** to **11.96%**. This quantifies the parsing artifact rather than hiding it.

## Paper Use

FaithfulRAG-inspired should still remain in the appendix because the fidelity limitation is independent of parsing: no reusable official implementation was found. RARR-FP may remain in the main comparison with the fixed-pool adaptation footnote. Do not state that evaluator parse failures were mechanically assigned zero; explain that the original fact parser discarded truncated arrays and thereby produced empty fact traces.
