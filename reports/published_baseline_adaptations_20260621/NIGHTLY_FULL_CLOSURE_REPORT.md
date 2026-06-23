# Nightly Full Closure Report

## Status

- Manifest: 29 entries; all exist = True; all hashes match = True.
- Prediction grid: 27/27 method-dataset files complete; schema/hash audit written.
- Main results: 27 rows recomputed offline.
- Paired bootstrap: 108 rows, 10,000 resamples, seed 42, paired by query ID.
- Prompt leakage audit passed: True.
- New adaptation/control `no_extra_retrieval=true` for every sample: True.
- Legacy evidence remains inside the frozen per-query pool: True; AGR may reorder/select within that pool.
- Figures: PNG, PDF, source CSV, and signature audit generated.
- Qualitative shortlist: two main-text cases plus appendix diagnostics generated.

## Final Statistical Conclusion

AGR: **34.88% mean EM / 47.25% mean F1**.  
Strongest non-AGR: **TP-FP RAG, 28.88% EM / 37.27% F1**.  
AGR advantage: **+6.00 EM / +9.99 F1 points**.  
AGR repair-harm: HOH 127/48 (+79), TempRAGEval 123/15 (+108), TimeQA 27/19 (+8).

## Main Text

- TP-FP RAG, AGR, FP-CSR, FP-TSR, FP-EASR, Self-Refine-FP adaptation, RARR-FP adaptation.
- Main performance table, AGR repair-harm figure, stale-repair case, relation-mismatch case.

## Appendix

- FaithfulRAG-inspired FP control and CRAG-inspired FP evaluator control.
- Runtime, feature exposure, full bootstrap CI, diagnostic cases, partial existing-artifact ArchivalQA table.

## Skipped Conservatively

- ArchivalQA new adaptation runs: skipped because they require new LLM inference and would create an asymmetric optional grid; only existing TP-FP/AGR/FP-CSR artifacts were evaluated offline.
- Self-RAG main experiment: prohibited and method/model mismatch risk.
- Dense/hybrid retrieval and index rebuild: prohibited because they change evidence state.
- LLaMA3 full grid: prohibited and high cost.
- Self-Refine/RARR/FaithfulRAG/CRAG reruns: skipped because predictions are complete and hashes/schema/query IDs validate; rerunning would add cost without closure value.

## Remaining Human Work

Only manuscript integration and manual case wording verification remain. No required experiment is blocked.
