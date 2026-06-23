# Paper-Ready Result Summary

AGR is the best method on the unweighted three-dataset mean: **34.88% EM / 47.25% F1**. The strongest non-AGR baseline is **TP-FP RAG** at **28.88% EM / 37.27% F1**.

| Dataset | TP-FP RAG EM | AGR EM | Gain | Repair | Harm | Net |
|---|---|---|---|---|---|---|
| HOH-1024 | 43.46 | 51.17 | +7.71 | 127 | 48 | 79 |
| TempRAGEval-1244 | 15.19 | 23.87 | +8.68 | 123 | 15 | 108 |
| TimeQA-500 | 28.00 | 29.60 | +1.60 | 27 | 19 | 8 |

Self-Refine-FP is the strongest new published-method adaptation/control (24.00% mean EM), but remains below TP-FP RAG and AGR. FaithfulRAG-inspired and CRAG-inspired should remain appendix diagnostics because method fidelity is incomplete and their repair-harm balance is negative. RARR-FP may enter the main comparison only with a fixed-pool adaptation footnote.
