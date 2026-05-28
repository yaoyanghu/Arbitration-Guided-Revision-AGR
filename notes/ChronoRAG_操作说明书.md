# ChronoRAG 操作说明书

## 1. 文档目的

本说明书用于在云服务器内容丢失后，帮助重新恢复 ChronoRAG 当前实验线。内容覆盖：

- 我已完成的全部关键操作
- 每一步是如何实现的
- 当前代码和数据如何组织
- 需要重新下载的外部数据
- 已经得到的主要实验结果
- 当前结果的风险点与后续最小补救方案

本文档刻意不包含任何密码或敏感连接信息。

## 2. 当前实验目标

当前 ChronoRAG 这条线不是一个大而全的完整系统，而是一个更小、更稳的子问题：

- 基于 official FEVER 数据
- 使用 BM25 做候选检索
- 引入一个轻量 `title overlap` 信号
- 在不改变 top-k coverage 的情况下，改善 strict gold page 排序质量

当前不包含：

- Route B
- Route C
- dense retrieval
- generation
- evidence graph
- 新模型训练

## 3. 项目根目录与主要结构

本地工作目录：

- `D:\HUYAOYANG\Work\ChronoRAG`

远端曾经使用过的标准根目录：

- `/home/huyaoyang/Projects/ChronoRAG`

主要目录说明：

- `configs/`: 基础配置
- `src/`: 数据准备、语料构建、检索、评测、分析脚本
- `data/raw/fever_official/`: official FEVER 原始 claims 与 wiki-pages.zip
- `data/processed/fever_official/`: 处理后的 official FEVER 子集
- `data/corpus/fever_official/`: official Wikipedia pages 规范化后的 shard
- `indexes/bm25_fever_official/`: official FEVER BM25 索引
- `runs/fever_official_route_a/`: 500 条调参与 strict 重验证结果
- `runs/fever_official_route_a_1000/`: 1000 条验证结果
- `notes/`: 论文表格、误差分析、overlap 检查、写作草稿

## 4. 我从头到尾做了哪些操作

### 4.1 初始工程搭建

先搭了一个可迁移的 ChronoRAG 实验骨架，包括：

- `scripts/bootstrap_env.sh`
- `scripts/check_env.sh`
- `scripts/prepare_all.sh`
- `scripts/run_route_a.sh`
- `src/eval/eval_main.py`
- `src/retrieval/build_bm25.py`
- `src/retrieval/search.py`
- `src/temporal/label_relation.py`
- `src/reliability/source_score.py`
- `src/rerank/rerank.py`

目标是先把最小 Route A 做成能端到端落盘结果的闭环。

### 4.2 最小 Route A 闭环

最初先在 demo / 小样本上打通流程：

1. FEVER 输入标准化
2. corpus 接口
3. BM25 建索引
4. BM25 检索
5. temporal score
6. reliability score
7. rerank
8. eval

所有中间结果与最终结果统一落盘到：

- `runs/{exp_name}/`

### 4.3 切换到 official FEVER 数据

之后停止使用 live Wikipedia summary 作为主实验语料，改成 official FEVER 数据线：

下载了 official FEVER claims：

- `train.jsonl`
- `shared_task_dev.jsonl`
- `shared_task_dev_public.jsonl`
- `shared_task_test.jsonl`

下载了 official FEVER 预处理 Wikipedia Pages：

- `wiki-pages.zip`

官方数据下载源使用：

- `https://fever.ai/download/fever/`

旧的 `fever.public` S3 链接在当时环境中返回 403，所以改用 `fever.ai`。

### 4.4 official FEVER 语料规范化

解压 `wiki-pages.zip` 后，原始结构为：

- `wiki-pages/wiki-pages/wiki-001.jsonl ... wiki-221.jsonl`

我把它规范化到：

- `data/corpus/fever_official/`

关键统计：

- 规范化后 shard 数：`109`
- 文档总数：`5,396,106`
- 规范化后语料大小：约 `3.4G`

实现方式：

- 改造了 `src/corpus/build_wiki2018_corpus.py`
- 支持 `--official-wiki-dir`
- 直接读取 official `wiki-*.jsonl`
- 规范化输出字段：
  - `doc_id`
  - `title`
  - `text`
  - `source`
  - `timestamp`

### 4.5 official FEVER claims 处理

我改造了 `src/data/prepare_fever.py`，使其支持 official FEVER 原始 evidence 结构。

重要点：

- 正确解析 nested evidence
- 过滤掉没有 gold evidence page 的 NEI 样本
- 输出标准字段：
  - `id`
  - `claim`
  - `label`
  - `evidence`
  - `source`
  - `verifiable`
  - `evidence_titles`
  - `evidence_sentence_ids`
  - `primary_evidence_title`

## 5. BM25 是如何实现的

### 5.1 早期小样本

早期小样本语料直接使用 json 序列化索引。

### 5.2 official FEVER 全量语料

因为 official FEVER Wikipedia pages 太大，普通内存版 BM25 不适合直接吃 500 多万篇文档，所以我把 `src/retrieval/build_bm25.py` 改成支持 SQLite FTS5 后端。

当前 official 索引位置：

- `indexes/bm25_fever_official/bm25_fts.db`

关键统计：

- 索引大小：约 `5.5G`
- 文档数：`5,396,106`

对应检索脚本：

- `src/retrieval/search.py`

检索仍然保持 BM25 路线，不含 dense retrieval。

## 6. 500 条 official FEVER 调参与 baseline

从 official `shared_task_dev.jsonl` 中抽取了 `500` 条 verifiable 样本作为 title overlap 调参集。

500 条样本统计：

- `SUPPORTS = 230`
- `REFUTES = 270`
- `VERIFIABLE = 500`

baseline 结果目录：

- `runs/fever_official_route_a/`

500 条 baseline 结果：

- BM25 Recall@1 = `0.698`
- BM25 Recall@5 = `0.860`
- BM25 Recall@10 = `0.910`

strict 重评估结果：

- strict BM25 Recall@1 = `0.352`
- strict BM25 Recall@5 = `0.596`
- strict BM25 Recall@10 = `0.692`

### 6.1 title overlap 改进

我没有增加新模型，而是实现了一个非常轻量的 rerank 信号：

- `title_overlap_score`

核心思想：

- 如果 claim 中的核心实体词与页面标题更直接对齐，则给该候选更高分

早期验证权重：

- `bm25_weight = 0.7`
- `title_weight = 0.3`

在 strict 评测下，当时得到：

- strict top1: `176 -> 183`
- strict delta: `+7`

### 6.2 严格评测定义

严格评测文件：

- `runs/fever_official_route_a/official_strict_eval_results.json`
- `runs/fever_official_route_a/official_strict_eval_summary.md`

strict 定义：

- 只有当检索到的 `title` 或 `doc_id` 规范化后，与 official `evidence_titles` 精确对齐时，才算命中

relaxed 定义：

- 允许 gold title 在候选 `title/text` 中做 substring 命中

## 7. 500 条权重扫描

之后仅对 title overlap 一个参数做了小范围扫描：

- `title_weight = 0.1, 0.2, 0.3, 0.4, 0.5`
- `bm25_weight = 1 - title_weight`

结果文件：

- `runs/fever_official_route_a/official_weight_sweep_results.json`
- `runs/fever_official_route_a/official_weight_sweep_summary.md`

真实 strict top1 结果：

- `0.1 -> 178 (+2)`
- `0.2 -> 180 (+4)`
- `0.3 -> 183 (+7)`
- `0.4 -> 189 (+13)`
- `0.5 -> 200 (+24)`

所以当前最优权重不是最初的 `0.7/0.3`，而是：

- `bm25_weight = 0.5`
- `title_weight = 0.5`

## 8. 1000 条验证结果

随后固定最优权重 `0.5 / 0.5`，在 `1000` 条 official dev verifiable 子集上做验证。

结果目录：

- `runs/fever_official_route_a_1000/`

baseline 结果：

- relaxed BM25 Recall@1 = `0.734`
- relaxed BM25 Recall@5 = `0.871`
- relaxed BM25 Recall@10 = `0.913`

strict 结果：

- baseline strict Recall@1 = `0.379`
- baseline strict Recall@5 = `0.614`
- baseline strict Recall@10 = `0.705`
- title-overlap strict Recall@1 = `0.429`
- title-overlap strict Recall@5 = `0.662`
- title-overlap strict Recall@10 = `0.705`

strict top1 变化：

- `379 -> 429`
- `delta = +50`

对应案例统计：

- strict improved case count = `51`
- strict regressed case count = `1`

说明：

- `top10` 不变
- 这说明 title overlap 改善的是 reranking，而不是 candidate coverage

## 9. 分标签结果

对应文件：

- `runs/fever_official_route_a_1000/official_labelwise_results.json`
- `runs/fever_official_route_a_1000/official_labelwise_summary.md`

当前最优权重 `0.5 / 0.5` 下：

baseline BM25：

- SUPPORTS strict Recall@1 / @5 / @10 = `0.4045 / 0.6386 / 0.7351`
- REFUTES strict Recall@1 / @5 / @10 = `0.3548 / 0.5906 / 0.6764`

BM25 + title overlap：

- SUPPORTS strict Recall@1 / @5 / @10 = `0.4517 / 0.6858 / 0.7351`
- REFUTES strict Recall@1 / @5 / @10 = `0.4074 / 0.6394 / 0.6764`

这说明 SUPPORTS 和 REFUTES 都得到了提升。

## 10. 失败分析与案例分析

### 10.1 500 条失败分析

文件：

- `runs/fever_official_route_a/official_failure_analysis.md`
- `runs/fever_official_route_a/official_failure_cases.jsonl`
- `runs/fever_official_route_a/official_label_breakdown.json`

主要结论：

- `retrieval_miss = 45`
- `large_lexical_gap_between_query_and_gold_page = 18`
- `alias_or_title_normalization_mismatch = 17`
- `gold_page_in_corpus_but_not_recalled = 10`

### 10.2 1000 条案例分析

文件：

- `notes/case_analysis.md`
- `notes/case_table.md`

目前归纳出的 improvement 模式：

- `surface_title_match`
- `exact_gold_promotion`
- `disambiguation`

strict regression 只有 `1` 个，说明主要风险是：

- 表层标题词重合误导排序

## 11. 500 调参与 1000 验证之间的重叠问题

文件：

- `notes/overlap_check_report.md`
- `src/analysis/overlap_check.py`

当前结论非常重要：

- 500 集大小：`500`
- 1000 集大小：`1000`
- overlap：`500`
- overlap vs 500：`1.000`
- overlap vs 1000：`0.500`

也就是说：

- 当前 500 调参与 1000 验证不是独立的
- 1000 集包含了全部 500 条调参样本

因此当前 1000 条结果：

- 可以作为“更大规模 follow-up evaluation”
- 但不能严格写成“独立 validation”

## 12. 最小代价补救方案

文件：

- `notes/minimal_validation_plan.md`

推荐补救：

1. 保留现有 500 条作为 tuning set
2. 从 official dev verifiable 池中排除这 500 条
3. 构造一个新的 disjoint 1000 validation 子集
4. 固定当前最优权重 `0.5 / 0.5`
5. 只重跑这个 disjoint validation，不必先做 full dev

这样成本最低，而且最能补齐论文证据链。

## 13. 当前已经生成的论文辅助材料

位于 `notes/`：

- `overlap_check_report.md`
- `case_analysis.md`
- `case_table.md`
- `tables_markdown.md`
- `tables_latex.tex`
- `results_error_validity_draft.md`
- `minimal_validation_plan.md`

这些内容已经可以直接支撑论文中的：

- Results
- Error Analysis
- Threats to Validity
- 结果表格

## 14. 如果云服务器内容丢失，应该重新下载和重建什么

### 14.1 需要重新下载的外部数据

必须重新下载：

- `train.jsonl`
- `shared_task_dev.jsonl`
- `shared_task_dev_public.jsonl`
- `shared_task_test.jsonl`
- `wiki-pages.zip`

推荐下载源：

- `https://fever.ai/download/fever/`

### 14.2 需要重新构建的中间产物

云服务器丢失后，需要重新构建：

- `data/corpus/fever_official/`
- `indexes/bm25_fever_official/bm25_fts.db`
- 各个 `runs/.../` 目录

### 14.3 不需要重新写的内容

本地 ChronoRAG 仓库中已经保留：

- 代码
- 分析脚本
- 论文表格
- 说明文档
- 本地 run 结果副本

## 15. 推荐的重建顺序

如果要在新云服务器上重建，建议按下面顺序做：

1. 建立 ChronoRAG 根目录
2. 安装 Python / conda 环境
3. 安装基础依赖
4. 下载 official FEVER claims
5. 下载并解压 `wiki-pages.zip`
6. 运行 official corpus 规范化
7. 构建 SQLite FTS5 BM25 索引
8. 准备 500 / 1000 或 disjoint validation 子集
9. 跑 BM25 baseline
10. 跑 title overlap rerank
11. 跑 strict / relaxed 重评估
12. 导出 notes 与结果表格

## 16. 当前最重要的结论

当前最稳的实验结论不是“ChronoRAG 完整系统已经完成”，而是：

- 在 official FEVER evidence retrieval 子问题上
- 使用 BM25 候选 + 轻量 title overlap reranking
- 在 strict gold page 指标下可以稳定提升 top1 排名质量

当前最优设置：

- `bm25_weight = 0.5`
- `title_weight = 0.5`

1000 条 follow-up 结果：

- strict top1: `379 -> 429`
- strict delta: `+50`

但必须注意：

- 当前 1000 条并非独立验证
- 若用于论文主结果，强烈建议补一个 disjoint validation

## 17. 本地重要文件清单

实验结果：

- `runs/fever_official_route_a/`
- `runs/fever_official_route_a_1000/`

论文材料：

- `notes/overlap_check_report.md`
- `notes/case_analysis.md`
- `notes/case_table.md`
- `notes/tables_markdown.md`
- `notes/tables_latex.tex`
- `notes/results_error_validity_draft.md`
- `notes/minimal_validation_plan.md`

代码：

- `src/data/prepare_fever.py`
- `src/corpus/build_wiki2018_corpus.py`
- `src/retrieval/build_bm25.py`
- `src/retrieval/search.py`
- `src/analysis/official_strict_revalidation.py`
- `src/analysis/official_weight_sweep.py`
- `src/analysis/official_labelwise_strict_eval.py`
- `src/analysis/overlap_check.py`
- `src/analysis/paper_artifacts.py`

## 18. 一句话建议

如果你现在要恢复实验，最优先做三件事：

1. 重新下载 official FEVER 原始数据
2. 重新构建 official corpus 与 BM25 索引
3. 先补 disjoint validation，再写论文主结果
