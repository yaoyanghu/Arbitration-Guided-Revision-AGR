# Route B Graph v3 Holdout Next Step Decision

## Decision

1. Route B 是否已经证明了 graph 的独立价值  
否。

2. 如果还没有，最大硬伤是什么  
最大的硬伤是：`full_graph` 在 held-out hard subset 上没有优于同信息量的 `case_aware_non_graph` baseline。当前净增益可以被一个不显式建图的 conflict-aware rule aggregator 复现，因此还不能把收益归因为 graph 本身。

3. Route B 应继续扩成 main experiment，还是降级为 analysis / conflict-focused module  
当前更合理的选择是：先降级为 `analysis / conflict-focused module`，不要进入 Route B main experiment。

## Supporting Facts

- `full_graph` > `a_only`
- `full_graph` > `update_only`
- `full_graph` = `case_aware_non_graph`
- clear cases 上 graph 基本中性
- reliability-sensitive 和 mixed cases 上有帮助，但这些帮助没有显示出独立于 matched non-graph aggregation 的额外价值

## Practical Readout

- The prototype is useful for diagnosis and structured conflict handling.
- The current hold-out evidence is not enough to justify a standalone graph-method claim.
- If Route B continues later, the next bar is not "more gain than A only"; it is "gain that survives matched non-graph controls."
