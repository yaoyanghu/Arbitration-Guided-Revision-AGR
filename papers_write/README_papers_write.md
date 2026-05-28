# Papers Write Asset Pack

这个目录是为 FEVER short paper 成稿阶段整理出的“硬结果资料包”。目标是把当前最有效、最能直接写论文、最值得保留的实验结果和文档集中到一个地方，避免你再到仓库各处翻找。

## 1. 目录说明

### `runs/fever_official_route_a_disjoint_1000_main/`

当前最重要的主结果目录。建议把它当作论文主验证锚点。

关键文件：
- `official_strict_eval_results.json`
- `official_labelwise_results.json`
- `official_strict_improved_cases.jsonl`
- `official_strict_regressed_cases.jsonl`
- `retrieval_results.jsonl`
- `reranked_results.jsonl`
- `predictions.jsonl`

这套结果支持的核心结论是：
- BM25 vs title-overlap 的主验证线
- strict / relaxed 区分
- label-wise 分析
- case-level 分析

### `runs/fever_official_route_a_disjoint_1000_nearest_baseline/`

最近邻 title-aware baseline 对比目录。

关键文件：
- `nearest_title_baseline_results.json`
- `nearest_title_baseline_summary.md`
- `exact_title_boost_strict_improved_cases.jsonl`
- `exact_title_boost_strict_regressed_cases.jsonl`
- `title_overlap_strict_improved_cases.jsonl`
- `title_overlap_strict_regressed_cases.jsonl`

这套结果支持的核心结论是：
- `exact_title_boost` 是当前仓库里更强的 tested lightweight title-aware heuristic
- `title_overlap` 仍然是更保守、回退更少的变体

### `runs/fever_official_route_a/`

500 条调参与早期 official baseline 资料。

关键文件：
- `official_weight_sweep_results.json`
- `official_weight_sweep_summary.md`
- `official_failure_analysis.md`
- `official_label_breakdown.json`
- `official_strict_eval_results.json`

这套资料适合用来写：
- weight sweep
- 早期 baseline failure analysis

### `runs/fever_official_route_a_1000_historical/`

这是旧的 1000 条结果，保留为历史记录，不建议作为当前论文主验证结果。

保留原因：
- 方便交叉比对旧叙事
- 方便说明为什么后面改成 disjoint 1000

### `notes_core/`

这里放的是论文收口必需的说明与分析文档。

最推荐优先看的文件：
- `current_claim_freeze.md`
- `paper_asset_inventory.md`
- `paper_closeout_plan.md`
- `paper_wording_pack.md`
- `overlap_check_report.md`
- `case_analysis.md`
- `significance_analysis.md`
- `tables_markdown.md`
- `tables_latex.tex`

### `paper_draft/`

这里放的是已经可以直接拿来扩写正文的草稿。

关键文件：
- `abstract_draft_v1.md`
- `introduction_draft_v1.md`
- `results_draft_v1.md`
- `limitations_draft_v1.md`
- `paper_draft_outline.md`
- `final_tables_for_paper.tex`

### `remote_server_snapshot/`

这里是从学校服务器同步下来的小体量快照，用于保留“服务器上确实存在过这些资料/任务”的证据。

包含：
- `logs/fever_official_route_a_full_dev.*`
- 远端 `runs / notes / logs` 的目录快照
- 若干远端 notes 和结果 json 的备份

注意：
- 这里没有复制大数据、全量语料、5.5G 索引数据库
- 这里也没有把 full-dev 伪装成已完成结果，因为它当前并未产出可用结果

## 2. 当前最硬的论文证据链

如果你现在立刻开始写论文，优先使用下面这条证据链：

1. 主结果
- `runs/fever_official_route_a_disjoint_1000_main/official_strict_eval_results.json`

2. label-wise
- `runs/fever_official_route_a_disjoint_1000_main/official_labelwise_results.json`

3. 最近邻 baseline 对比
- `runs/fever_official_route_a_disjoint_1000_nearest_baseline/nearest_title_baseline_results.json`

4. 显著性与置信区间
- `notes_core/significance_analysis.md`
- `notes_core/significance_table.md`

5. overlap 修补说明
- `notes_core/overlap_check_report.md`

6. case analysis
- `notes_core/case_analysis.md`
- `notes_core/case_table.md`

## 3. 当前最稳的论文叙事

当前建议统一成：

- `lightweight title-aware lexical reranking for official FEVER evidence retrieval`

不要再写成：

- `title overlap is the validated best method`

理由已经冻结在：
- `notes_core/current_claim_freeze.md`

## 4. 远端同步说明

这次已经从学校服务器同步了小体量、与论文写作直接相关的快照文件。

未同步的内容：
- 全量 official 数据
- 全量 Wikipedia 语料
- 大索引数据库

原因：
- 它们体量过大
- 不属于“写论文所需的核心结果资料包”

另外，学校服务器上一份中文文件名的说明书在 Windows 本地落盘时遇到了文件名编码问题，因此这里保留的是本地同名说明书主版本，而不是远端那份重命名副本。

## 5. 现在怎么用

如果你想最快开始写：

1. 先读 `notes_core/current_claim_freeze.md`
2. 再读 `paper_draft/abstract_draft_v1.md`
3. 再读 `paper_draft/introduction_draft_v1.md`
4. 然后配合 `paper_draft/final_tables_for_paper.tex` 和 `notes_core/tables_markdown.md` 写正文

如果你想先看最关键的结果数字：

1. `runs/fever_official_route_a_disjoint_1000_main/official_strict_eval_results.json`
2. `runs/fever_official_route_a_disjoint_1000_main/official_labelwise_results.json`
3. `runs/fever_official_route_a_disjoint_1000_nearest_baseline/nearest_title_baseline_results.json`

## 6. 一句话结论

`papers_write` 现在已经是一份可以直接支撑 FEVER short paper 起草的本地资料包：主结果、baseline 对比、显著性、误差分析、表格和正文草稿都在这里了。
