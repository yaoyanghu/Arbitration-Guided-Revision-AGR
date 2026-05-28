# Route B Salvage Or Stop

## Decision

Choose **B**:

Route B 只在重新定义的 `graph-sensitive task` 上保留最后一次机会。

## Why Not A Immediately

这次审计显示，当前 Route B 打平不只是“图方法不行”，而是当前 v4 task 自身并不要求 graph-native superiority。

更具体地说：

- 当前任务的主要奖励是候选级排序做对
- `case_aware_non_graph_rerank` 已经把 test 做到 `1.000 / 1.000`
- 当前 graph-native 进入的是一个没有 headroom、也不天然偏向 graph 的任务

在这种条件下直接宣布“图方法永远不值得继续”，结论会过强。

## Why Current v4 Task Is Not Enough

当前 v4 task 不够 graph-sensitive，原因是：

1. 正确答案大多可以由单候选局部特征决定  
`temporal_status + evidence_time + source_type/reliability + case_type` 已经足够把 preferred doc 排到前面。

2. 图没有独占信息源  
graph edges 本身也是由这些局部特征诱导出来的，所以 matched non-graph 能把相同信息压缩成分数。

3. 当前指标不要求跨节点一致性  
preferred top1 / pairwise success 都是在奖励“把正确候选放前面”，而不是奖励“必须通过多节点一致性才能判断”。

## If Route B Gets One Last Chance, The New Task Must Satisfy

只有当新 task 同时满足下面条件时，Route B 才值得保留最后一次机会：

1. `No single candidate-local score is sufficient`  
单候选的 BM25/temporal/reliability/简单 case-aware rerank 不能把问题做满。

2. `Answer requires multi-node consistency`  
正确判断必须依赖多个 evidence node 之间的联合一致性，而不是一个局部 aggregator 就能复刻。

3. `Matched non-graph baseline remains a strong control`  
必须继续保留同信息量的 non-graph baseline，防止图方法再次靠“换一种表示同样信息”取胜。

4. `Evaluation rewards consistency, not only top1 placement`  
评测要能真正区分“只是候选排前了”与“图结构解决了冲突一致性”。

## Practical Interpretation

在当前 v4 task 上：

- Route B 不应继续扩张
- Route B 不应回到主方法线
- Route B 仍然只能作为 analysis layer 出现

但从审计角度说，Route B 还没有被“普遍性地证死”；它只是被当前 v4 task 证成了“不适合作为这个任务上的主方法”。

## Bottom Line

- 对当前 v4 task：Route B 应停止为主方法
- 对未来是否还有最后一次机会：只有在重新定义的 graph-sensitive task 上才有
- 如果做不到这样的 task 设计，Route B 就应永久固定为 analysis layer
