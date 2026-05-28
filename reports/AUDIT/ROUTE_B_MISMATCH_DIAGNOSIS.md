# Route B Mismatch Diagnosis

## 1. Route B 想证明的是什么

按照 [route_b_graph_native_v1.md](D:/HUYAOYANG/Work/ChronoRAG/docs/route_b_graph_native_v1.md)，Route B 这次真正想证明的是：

- graph-native consistency / consensus 有独立价值
- 这种价值不能被同信息量的 matched non-graph baseline 等价复刻

也就是说，Route B 不是要证明“图不空”，也不是要证明“图比 Route A alone 好”，而是要证明“图结构本身带来了 matched non-graph 做不到的收益”。

## 2. 当前 A++ 任务真正奖励的是什么

按照 [route_a_plus_plus_plan_v1.md](D:/HUYAOYANG/Work/ChronoRAG/docs/route_a_plus_plus_plan_v1.md)、[route_a_temporal_v4_manifest.md](D:/HUYAOYANG/Work/ChronoRAG/docs/route_a_temporal_v4_manifest.md) 和 [eval_route_a_temporal_v4.py](D:/HUYAOYANG/Work/ChronoRAG/src/eval/eval_route_a_temporal_v4.py)，A++ 任务真正奖励的是：

- 在每个 query 的 top-k 候选里，把 `updated` 排到 `stale / conflicting` 前面
- 主要依赖候选级别的时间信息、来源可靠性信息和 case-type aware 的局部重排

当前主指标是：

- preferred top1
- pairwise preference success
- preferred rank / MRR

这些指标本质上奖励的是“候选级局部排序做对”，不是“多节点关系一致性做对”。

## 3. 为什么这两者没有完全对上

Route B 想验证的是“图结构的独立必要性”，但 A++ 任务主要奖励的是“单候选 updated-vs-stale 排序能力”。这两者没有完全对上的原因有三点：

1. 当前任务的正确答案大多已经可以由候选自身特征决定  
在 [eval_route_a_temporal_v4.py](D:/HUYAOYANG/Work/ChronoRAG/src/eval/eval_route_a_temporal_v4.py) 里，`case_aware_non_graph_score` 直接使用 `bm25_score_norm + temporal_score + reliability_score + case_type`。这已经足够把 test 上的 `case_aware_non_graph_rerank` 推到 `1.000 / 1.000`。

2. 当前图结构主要还是由同一批局部特征诱导出来  
在 [build_route_b_graph_native.py](D:/HUYAOYANG/Work/ChronoRAG/src/graph/build_route_b_graph_native.py) 里，graph 的 `support / corroborate / update / contradict` 边基本都来自：
`case_aware_non_graph_score`、`reliability_score`、`temporal_status`。
这意味着图并没有引入一个新的信息源，而是在重新组织已有局部信号。

3. 当前评测不要求跨节点一致性必须胜出  
在 [eval_route_b_graph_native.py](D:/HUYAOYANG/Work/ChronoRAG/src/eval/eval_route_b_graph_native.py) 里，最终还是看 preferred doc 的排序位置。只要局部特征已经足够把 preferred doc 排第一，graph-native consistency 就没有额外可拿的分数。

## 4. 为什么 graph-native 会和 matched non-graph baseline 打平

打平不是偶然，而是当前设计的直接结果：

1. `A++ best non-graph mainline` 已经到 ceiling  
在 [route_a_temporal_v4/RESULT_SUMMARY.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v4/RESULT_SUMMARY.md) 中，test 上的 `case_aware_non_graph_rerank = 1.000 / 1.000`。  
当 baseline 已经满分时，Route B 不可能再显示“严格超过”。

2. graph-native 的 base 也是从非图最强排序出发  
在 [eval_route_b_graph_native.py](D:/HUYAOYANG/Work/ChronoRAG/src/eval/eval_route_b_graph_native.py) 中：
- `a_plus_best_non_graph` 直接使用 `case_aware_non_graph_rerank_candidates`
- `graph_native_consensus` 也以 `case_aware_non_graph_score` 归一化后的状态作为初始 base  
这让 graph-native 更像“对已经最优的排序再做平滑一致性更新”，而不是在一个有明显剩余错误的空间里夺回增益。

3. matched non-graph conflict aggregator 能复刻同样的信息流  
同一个脚本里的 `matched_non_graph_score(...)` 已经直接读取：
- support
- corroborate
- update
- contradict  
这些正是 graph 里传递的一致性来源。既然 matched non-graph 已能把这些边信号压缩成局部聚合分数，graph-native 就很难再证明“只有图能做到”。

## 5. 这更像 ceiling effect、task mismatch、还是 implementation weakness

最准确的判断是：

- 主要是 `task mismatch`
- 其次是 `ceiling effect`
- `implementation weakness` 是次要但真实存在的因素

### 主因：task mismatch

当前 v4 任务奖励的是“局部候选排序正确”，不是“跨节点一致性必须成立”。所以 graph-native 进入的是一个并不天然偏向 graph 的任务。

### 次因：ceiling effect

一旦 [route_a_temporal_v4/RESULT_SUMMARY.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v4/RESULT_SUMMARY.md) 里的 `case_aware_non_graph_rerank` 在 test 上已经是 `1.000 / 1.000`，Route B 生死实验就失去了可分辨空间。

### 次要但存在：implementation weakness

当前 graph-native 原型仍然 heavily anchored on local scores：
- graph edges mainly come from `temporal_status` and `reliability_score`
- node initialization comes from normalized `case_aware_non_graph_score`

所以这版 graph-native 仍然没有摆脱“局部特征重表达”的影子。

## 审计结论

当前 Route B 打平，不能简单解释成“图方法失败”。更准确地说：

- 当前 A++ task 不足以奖励 graph-native superiority
- 非图基线已经把当前任务几乎做满
- graph-native 原型又没有引入一个 truly indispensable 的结构信号

因此，当前结果最像：

`task mismatch + ceiling effect` 主导，`implementation weakness` 次之。
