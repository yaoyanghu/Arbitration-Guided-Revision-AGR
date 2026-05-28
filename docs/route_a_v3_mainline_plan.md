# Route A v3 Mainline Plan

## 1. Route A v2 当前最硬结果

Route A v2 is the strongest completed checkpoint before v3 because it already showed all three required properties on a hardened real subset:

- retrieval-only < temporal-only <= temporal + reliability
- measurable ranking change from the temporal signal
- non-zero help from the reliability prior

The core v2 result package is:

- [metrics.json](D:/HUYAOYANG/Work/ChronoRAG/runs/route_a_temporal_v2/metrics.json)
- [RESULT_SUMMARY.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v2/RESULT_SUMMARY.md)
- [ACCEPTANCE_CHECK.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v2/ACCEPTANCE_CHECK.md)
- [CASEBOOK.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v2/CASEBOOK.md)
- [V1_VS_V2_DIFF.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v2/V1_VS_V2_DIFF.md)

## 2. Route A 为什么现在才是主线

Route A is now the mainline because it has the strongest independent method signal left in the project:

- Route B did not prove independent graph value over a matched non-graph baseline.
- Route C is frozen out of scope.
- FEVER short paper is not the current priority.

That leaves Route A as the only route that currently combines:

- a stable task contract
- real temporal-conflict cases
- measurable gains from lightweight temporal and reliability signals
- reusable per-query artifacts

## 3. Route A v3 要解决的 3 个核心缺口

### A. 更大的 real temporal-conflict slice

Move beyond the 30-query hardened subset into a larger slice that is still built from the same controlled contract.

### B. 更稳的 case-type coverage

Keep `clear_updated_vs_stale`, `reliability_sensitive_conflict`, and `mixed_ambiguous_case` all present in balanced form so Route A is not validated by only one easy case family.

### C. 更强的 reusable checkpoint bundle

Package the subset, metrics, acceptance check, casebook, and stratified readout into one reusable Route A checkpoint so later work does not depend on Route B for explanation.

## 4. Route A v3 的最小成功标准

- query_count >= 54
- all three case types covered in balanced form
- retrieval-only < temporal-only <= temporal + reliability on preferred top1
- final pairwise preference success >= 0.80
- temporal changed ranking count >= 8
- reliability helped count >= 6
- per-query inspectable artifacts exist for every query

## 5. Route A v3 不做什么

- no new model
- no new large benchmark
- no Route B or Route C expansion
- no large sweep
- no change to the Route A task definition
