# Route A Next Stage Plan v1

## 1. Route A Current Strongest Result Package

The current strongest Route A package is the hardened v2 checkpoint:

- [route_a_hardening_plan_v1.md](D:/HUYAOYANG/Work/ChronoRAG/docs/route_a_hardening_plan_v1.md)
- [route_a_temporal_v2_subset_manifest.md](D:/HUYAOYANG/Work/ChronoRAG/docs/route_a_temporal_v2_subset_manifest.md)
- [metrics.json](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v2/metrics.json)
- [RESULT_SUMMARY.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v2/RESULT_SUMMARY.md)
- [ACCEPTANCE_CHECK.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v2/ACCEPTANCE_CHECK.md)
- [CASEBOOK.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v2/CASEBOOK.md)
- [NEXT_STEP_DECISION.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v2/NEXT_STEP_DECISION.md)
- [V1_VS_V2_DIFF.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v2/V1_VS_V2_DIFF.md)

This is the most defensible Route A result line because it is stronger than the 12-query acceptance-only v1, keeps the same task contract, and shows measurable gains from temporal and reliability signals on a harder subset.

## 2. What Route A Still Lacks To Become The True Mainline Experiment

1. A larger and more realistic temporal-conflict subset.
The current hardened subset is strong enough for prototype validation, but still too small to stand in for a main experimental line.

2. More stable coverage across case types.
Route A now handles clear, reliability-sensitive, and mixed cases, but the balance and scale are still limited.

3. A stronger external-validity story.
Right now the strongest evidence is still “controlled but real subset” rather than “realistic, stable, reusable benchmark slice.”

## 3. Top 3 Priority Next Steps

1. Expand Route A from the current hardened subset into a larger real temporal-conflict slice while keeping the same contract and metrics.

2. Stress-test Route A across more reliability-sensitive and ambiguous conflict cases so that the temporal and reliability signals are not supported by only a narrow slice of examples.

3. Harden the per-query artifact and evaluation package into a reusable checkpoint bundle so Route A can stand on its own without borrowing credibility from Route B.

## 4. Which Route B Assets Can Be Reused As Analysis Layer

The following Route B assets remain useful, but only as analysis support:

- [CASEBOOK.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_b_graph_v3_holdout/CASEBOOK.md)
- [WHAT_ROUTE_B_CAN_AND_CANNOT_CLAIM.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_b_graph_v3_holdout/WHAT_ROUTE_B_CAN_AND_CANNOT_CLAIM.md)
- [MATCHED_BASELINES.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_b_graph_v2/MATCHED_BASELINES.md)
- [STRATIFIED_EVAL.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_b_graph_v2/STRATIFIED_EVAL.md)

They can help diagnose where Route A struggles and which conflict patterns are hardest, but they should not define the Route A mainline claim.
