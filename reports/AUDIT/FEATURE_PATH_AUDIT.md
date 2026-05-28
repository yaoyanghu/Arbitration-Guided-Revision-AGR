# Feature Path Audit

## Audit Principle

本审计区分两类字段：

- `评测字段`：只用于计算 gold-aware 指标、生成 casebook、统计 improved/regressed
- `方法可见字段`：方法在打分、重排、建图时可以直接或间接读取的字段

如果某字段在方法打分阶段可见，而且该字段本身携带 gold 目标信息，就存在标签泄漏风险。

## Field-by-Field Audit

### 1. `preferred_doc_id`

角色：
- 评测字段，在 Route A / Route B 多个 eval 和 report 脚本中用于算 preferred rank

正常用途：
- [eval_route_a_temporal.py](D:/HUYAOYANG/Work/ChronoRAG/src/eval/eval_route_a_temporal.py):67
- [eval_route_a_temporal_v4.py](D:/HUYAOYANG/Work/ChronoRAG/src/eval/eval_route_a_temporal_v4.py):128
- [eval_route_b_graph_native.py](D:/HUYAOYANG/Work/ChronoRAG/src/eval/eval_route_b_graph_native.py):13

标签泄漏风险：
- **高风险，且旧 Route B 确实存在**

具体路径：
- [route_b_matched_baselines.py](D:/HUYAOYANG/Work/ChronoRAG/src/analysis/route_b_matched_baselines.py):65  
  `non_graph_case_aware_score(candidate, case_type, preferred_doc_id)` 直接把 `preferred_doc_id` 传进打分函数
- [route_b_matched_baselines.py](D:/HUYAOYANG/Work/ChronoRAG/src/analysis/route_b_matched_baselines.py):69  
  `same_entity = entity_key(candidate.doc_id) == entity_key(preferred_doc_id)`  
  这是直接用 gold 目标实体做方法分数判断
- [build_route_b_local_graph.py](D:/HUYAOYANG/Work/ChronoRAG/src/graph/build_route_b_local_graph.py):22
- [build_route_b_local_graph_v2.py](D:/HUYAOYANG/Work/ChronoRAG/src/graph/build_route_b_local_graph_v2.py):47-49, 64-66, 83-85  
  旧 Route B 图构造会围绕 `preferred_doc_id` 选 preferred/stale/conflict 节点

当前 B-native 是否仍有这类泄漏：
- 当前 [build_route_b_graph_native.py](D:/HUYAOYANG/Work/ChronoRAG/src/graph/build_route_b_graph_native.py) 只把 `preferred_doc_id` 作为 graph metadata 写出，没有在 edge 构造或 score 里直接读取
- 当前 [eval_route_b_graph_native.py](D:/HUYAOYANG/Work/ChronoRAG/src/eval/eval_route_b_graph_native.py) 只把它用于评测和 improved/regressed 统计

结论：
- 旧 Route B 路线有真实标签泄漏风险
- 当前 B-native 评分路径里没有发现 `preferred_doc_id` 直接参与打分

### 2. `stale_doc_ids`

角色：
- 主要是评测字段，用于 pairwise success 和 stale-best-rank

正常用途：
- [eval_route_a_temporal_v4.py](D:/HUYAOYANG/Work/ChronoRAG/src/eval/eval_route_a_temporal_v4.py):135
- [eval_route_b_graph_native.py](D:/HUYAOYANG/Work/ChronoRAG/src/eval/eval_route_b_graph_native.py):20
- [route_b_graph_native_casebook.py](D:/HUYAOYANG/Work/ChronoRAG/src/analysis/route_b_graph_native_casebook.py):9

标签泄漏风险：
- 当前主路径里**低风险**
- 没发现它在当前 Route A v4 或 B-native 打分逻辑里直接参与 score

### 3. `temporal_status`

角色：
- 方法可见字段

直接使用路径：
- [score_temporal_conflict.py](D:/HUYAOYANG/Work/ChronoRAG/src/temporal/score_temporal_conflict.py):63-70
- [eval_route_a_temporal_v4.py](D:/HUYAOYANG/Work/ChronoRAG/src/eval/eval_route_a_temporal_v4.py):58-81
- [build_route_b_graph_native.py](D:/HUYAOYANG/Work/ChronoRAG/src/graph/build_route_b_graph_native.py):20, 28-33
- [eval_route_b_graph_native.py](D:/HUYAOYANG/Work/ChronoRAG/src/eval/eval_route_b_graph_native.py) 间接通过 graph edges 使用

标签泄漏风险：
- **中风险，不是 gold 泄漏，但属于强任务侧标签**

原因：
- 它不是 `preferred_doc_id` 这种 gold target
- 但它是我们数据构造时显式赋给 candidate 的结构标签：`updated / stale / conflicting`
- 这意味着方法不是从原始文本自行发现 temporal role，而是在利用任务构造提供的显式角色标签

结论：
- 不属于 gold 泄漏
- 但属于强方法先验，必须在论文或报告里说清楚

### 4. `evidence_time`

角色：
- 方法可见字段

直接使用路径：
- [score_temporal_conflict.py](D:/HUYAOYANG/Work/ChronoRAG/src/temporal/score_temporal_conflict.py):26-28
- [eval_route_a_temporal_v4.py](D:/HUYAOYANG/Work/ChronoRAG/src/eval/eval_route_a_temporal_v4.py):53
- 旧 graph builder 也使用：
  [build_route_b_local_graph.py](D:/HUYAOYANG/Work/ChronoRAG/src/graph/build_route_b_local_graph.py):93

标签泄漏风险：
- 低风险

原因：
- 这是任务定义允许的方法输入
- 它是时间元数据，不是 gold target

### 5. `source_type`

角色：
- 方法可见字段

直接使用路径：
- [score_route_a_reliability.py](D:/HUYAOYANG/Work/ChronoRAG/src/reliability/score_route_a_reliability.py):21-28
- [eval_route_a_temporal_v4.py](D:/HUYAOYANG/Work/ChronoRAG/src/eval/eval_route_a_temporal_v4.py):30
- 旧 graph builder 会把它带进节点：
  [build_route_b_local_graph.py](D:/HUYAOYANG/Work/ChronoRAG/src/graph/build_route_b_local_graph.py):45,70

标签泄漏风险：
- 低风险

原因：
- 它只是来源类别，如 `official_record / blog / archival_news`
- 它是任务允许的 metadata，不是 gold answer

### 6. `reliability_bucket`

角色：
- mostly metadata carrier

直接使用路径：
- 当前主线中，它主要被写入和传递，但**没有在 Route A v4 主打分中直接参与 score**
- [eval_route_a_temporal_v4.py](D:/HUYAOYANG/Work/ChronoRAG/src/eval/eval_route_a_temporal_v4.py):30 只是搬运
- [score_route_a_reliability.py](D:/HUYAOYANG/Work/ChronoRAG/src/reliability/score_route_a_reliability.py) 实际打分依赖的是 `source_type`，不是 `reliability_bucket`

标签泄漏风险：
- 当前主线中低风险

补充：
- 旧 graph builder 会把它挂到 source node 上：
  [build_route_b_local_graph.py](D:/HUYAOYANG/Work/ChronoRAG/src/graph/build_route_b_local_graph.py):71

## Audit Conclusion

### 当前主线 Route A v4

- 没发现 `preferred_doc_id` / `stale_doc_ids` 直接进入主打分逻辑
- 主打分真正依赖的是：
  - `bm25_score_norm`
  - `evidence_time`
  - `temporal_status`
  - `source_type`
  - `reliability_score`

### 当前 B-native

- 没发现 `preferred_doc_id` 直接进入 graph-native score 或 matched non-graph score
- 但 graph-native 仍 heavily depends on `temporal_status` and `reliability_score`, which are strong task-visible features

### 旧 Route B 线

- 存在真实的 label leakage risk
- 主要问题路径就是：
  - [route_b_matched_baselines.py](D:/HUYAOYANG/Work/ChronoRAG/src/analysis/route_b_matched_baselines.py):65-69
  - [build_route_b_local_graph.py](D:/HUYAOYANG/Work/ChronoRAG/src/graph/build_route_b_local_graph.py):22
  - [build_route_b_local_graph_v2.py](D:/HUYAOYANG/Work/ChronoRAG/src/graph/build_route_b_local_graph_v2.py):47-49, 64-66, 83-85

所以：

- 当前 B-native 打平，不是由明显 gold leakage 直接造成
- 但旧 Route B 历史结果确实不能被无保留地当作干净证据使用
