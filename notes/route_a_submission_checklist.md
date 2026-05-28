# Route A Submission Checklist

## 1. Numbers That Still Need Manual Verification

- Confirm all numbers in the final mainline table against [metrics.json](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v3/metrics.json).
- Confirm all hold-out numbers against [metrics.json](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v3_holdout/metrics.json).
- Confirm the stratified case-type table against [STRATIFIED_EVAL.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v3/STRATIFIED_EVAL.md).
- Manually check that all rounded values are consistent between markdown tables and LaTeX tables.

## 2. Phrasing That Still Needs Manual Confirmation

- Confirm the final paper title and whether it should explicitly mention temporal conflict or source reliability.
- Confirm the exact wording of the main claim so it matches [MAINLINE_CLAIM_FREEZE.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v3/MAINLINE_CLAIM_FREEZE.md).
- Confirm that Route B is only described as an analysis layer and never as a co-equal method line.
- Confirm that the hold-out package is described as robustness confirmation rather than a second main experiment.

## 3. Files That Must Enter Final Archive

- [CHECKPOINT_MANIFEST.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v3/CHECKPOINT_MANIFEST.md)
- [REPRO_RUNBOOK.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v3/REPRO_RUNBOOK.md)
- [MAINLINE_CLAIM_FREEZE.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v3/MAINLINE_CLAIM_FREEZE.md)
- [RESULT_SUMMARY.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v3/RESULT_SUMMARY.md)
- [ACCEPTANCE_CHECK.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v3/ACCEPTANCE_CHECK.md)
- [CASEBOOK.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v3/CASEBOOK.md)
- [STRATIFIED_EVAL.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v3/STRATIFIED_EVAL.md)
- [RESULT_SUMMARY.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v3_holdout/RESULT_SUMMARY.md)
- [ACCEPTANCE_CHECK.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v3_holdout/ACCEPTANCE_CHECK.md)
- [NEXT_STEP_DECISION.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v3_holdout/NEXT_STEP_DECISION.md)
- [route_a_final_main_tables.md](D:/HUYAOYANG/Work/ChronoRAG/notes/route_a_final_main_tables.md)
- [route_a_final_tables.tex](D:/HUYAOYANG/Work/ChronoRAG/notes/route_a_final_tables.tex)
- [route_a_results_draft_v1.md](D:/HUYAOYANG/Work/ChronoRAG/notes/route_a_results_draft_v1.md)
- [route_a_method_draft_v1.md](D:/HUYAOYANG/Work/ChronoRAG/notes/route_a_method_draft_v1.md)
- [route_a_limitations_draft_v1.md](D:/HUYAOYANG/Work/ChronoRAG/notes/route_a_limitations_draft_v1.md)

## 4. What Must Not Be Changed Now

- Do not change the Route A task contract.
- Do not change the frozen Route A v3 weights without explicitly reopening experiments.
- Do not add Route B to the main result tables.
- Do not mention Route C.
- Do not relabel the held-out slice as a new benchmark or a second mainline experiment.
