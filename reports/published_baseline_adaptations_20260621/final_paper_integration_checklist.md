# Final Paper Integration Checklist

- [ ] Methods: define fixed-pool protocol and frozen top-2 evidence once.
- [ ] Methods: use the exact safe display names from `paper_safe_method_naming.md`.
- [ ] Baselines: add the RARR-FP adaptation footnote.
- [ ] Baselines: move FaithfulRAG-inspired and CRAG-inspired controls to the appendix.
- [ ] Results: replace the main table with `tables/paper_ready_main_table.md`.
- [ ] Results: report AGR mean EM/F1 and dataset-specific gains without universal-superiority wording.
- [ ] Analysis: report repair/harm/net repair, emphasizing the smaller TimeQA margin.
- [ ] Runtime: retain `UNKNOWN` for unlogged legacy fields; do not impute values.
- [ ] Qualitative analysis: manually verify the two main-text cases against source evidence.
- [ ] Appendix: include diagnostic, runtime, feature-exposure, bootstrap CI, and partial ArchivalQA tables.
- [ ] Figures: use PNG/PDF files only after checking captions and journal sizing.
- [ ] Reproducibility: cite the nightly manifest and prediction hash audits.
