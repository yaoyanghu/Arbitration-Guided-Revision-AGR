# AGR 缺失数据源文件清单

服务器项目根目录：

`/home/huyaoyang/Projects/flashrag_project_20251213/New_ChronoRAG`

以下路径均相对于该目录。最终性能结果优先使用 `nightly_closure_20260621_224528/fairness_repair`，不要退回未修复的 nightly 主表。

## 1. Table 1：Method positioning

- **缺失类型**：不是数值缺失，而是方法命名、定位和是否可进主文的依据。
- **命名权威源**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/reports/paper_safe_method_naming.md`
- **fidelity 权威源**：`outputs/published_baseline_adaptations_20260621/reports/baseline_fidelity_audit.md`
- **feature boundary 源**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/tables/baseline_feature_exposure_table.md`
- **状态**：可直接用于文字核对，没有待补实验数值。

## 2. Table 2：Core notation

- **缺失项**：计划要求保留“原论文完整 Table 2”，但当前 nightly 包没有原始 notation table。
- **可用方法公式源**：`outputs/paper_assets_final/jiis_major_revision_audit/method_formula_latex.tex`
- **可用算法源**：`outputs/paper_assets_final/jiis_major_revision_audit/algorithm1_latex.tex`
- **方法审计说明**：`outputs/paper_assets_final/jiis_major_revision_audit/method_algorithm_audit.md`
- **原始完整 Table 2 文件**：`UNKNOWN`。需要从当前论文 `.tex/.docx` 正文中提取，不能用上述公式文件冒充完整 notation table。

## 3. Table 3：Dataset and fixed-pool settings

- **全部数值的权威 CSV**：`outputs/paper_assets_final/jiis_major_revision_audit/dataset_fixedpool_statistics.csv`
- **现成 LaTeX**：`outputs/paper_assets_final/jiis_major_revision_audit/dataset_fixedpool_statistics_latex.tex`
- **构建说明**：`outputs/paper_assets_final/jiis_major_revision_audit/dataset_construction_report.md`
- **manifest/hash 复核**：`outputs/published_baseline_adaptations_20260621/manifest/fixed_pool_manifest.json`
- **对应字段**：`sample_count`, `retrieval_top_k`, `evidence_top_k`, `gold_answer_in_top4_rate`, `stale_cue_rate`, `conflict_cue_rate`。
- **状态**：计划中的 n、k_r、k_e、Ans@4、stale rate、conflict rate 均已有源文件，不缺数据。

## 4. Table 4：Main parse-repaired results

- **唯一应使用的主 CSV**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/fairness_repair/metrics/main_results_parse_repaired.csv`
- **长表 Markdown**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/fairness_repair/tables/Table4_parse_repaired.md`
- **长表 CSV 副本**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/fairness_repair/tables/Table4_parse_repaired.csv`

计划中缺失的 RARR 数值：

| Dataset | EM | F1 |
|---|---:|---:|
| HOH | 13.38 | 32.53 |
| TempRAGEval | 7.15 | 18.07 |
| TimeQA | 12.40 | 23.84 |
| Macro | 10.98 | 24.81 |

计划中缺失的 FP-CSR 数值：

| Dataset | EM | F1 |
|---|---:|---:|
| HOH | 30.08 | 42.10 |
| TempRAGEval | 15.35 | 23.64 |
| TimeQA | 24.60 | 30.35 |
| Macro | 23.34 | 31.99 |

- **FaithfulRAG 修复后来源**：同一 CSV；HOH 9.96/17.25，TempRAGEval 3.14/7.91，TimeQA 7.00/10.73。
- **状态**：Table 4 所有结果都有源，不应再使用原 nightly 的未修复 FaithfulRAG 行。

## 5. Table 5：AGR improvement and repair-harm

- **EM/F1/gain 源**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/fairness_repair/metrics/main_results_parse_repaired.csv`
- **repair/harm/net repair 源**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/metrics/repair_harm_all.csv`
- **Figure 4 同源 CSV**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/figures/figure_agr_repair_harm_source.csv`
- **状态**：计划表中的全部数值已有源。

## 6. Table 6：Prompt-visible feature exposure

- **旧 baseline 的最完整 feature 表**：`outputs/aei_submission_closure_v1/latex_tables/table_prompt_feature_comparison.tex`
- **AGR-only feature 边界**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/tables/baseline_feature_exposure_table.md`
- **prompt 泄漏审计**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/validation/prompt_leakage_audit.csv`
- **Self-Refine prompt**：`outputs/published_baseline_adaptations_20260621/prompts/self_refine_fp_v1.md`
- **RARR prompt**：`outputs/published_baseline_adaptations_20260621/prompts/rarr_fp_v1.md`
- **FaithfulRAG prompt**：`outputs/published_baseline_adaptations_20260621/prompts/faithfulrag_fp_v1.md`
- **CRAG prompt**：`outputs/published_baseline_adaptations_20260621/prompts/crag_fp_evaluator_v1.md`
- **状态**：没有一个文件单独包含计划中的全部 7 个 feature 列。必须由旧 feature table 加四份新 prompt 联合生成，不能只引用 nightly 的四列 feature 表。

## 7. Table 7：Runtime and protocol overhead

- **逐数据集 runtime 主源**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/metrics/runtime_overhead_all.csv`
- **answer-change/revision/no-extra-retrieval 源**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/metrics/low_cost_diagnostics_all.csv`
- **parse-repaired FaithfulRAG runtime 源**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/fairness_repair/metrics/main_results_parse_repaired.csv`
- **原始逐样本 runtime 源**：各方法 prediction JSONL，位于 `outputs/aei_submission_closure_v1/predictions/strong_baselines/` 和 `outputs/published_baseline_adaptations_20260621/predictions/`。

逐项判断：

1. **TP-FP answer-change rate**：应写 `N/A` 或 0（它是比较基线本身）；来源为 parse-repaired main CSV。
2. **TP-FP LLM calls/query = 1.00**：协议上可推断，但旧 artifact 没有 `llm_calls` 字段；日志源为 `UNKNOWN`，必须标为 protocol count，而非 measured count。
3. **TP-FP mean input tokens**：`UNKNOWN`，旧预测未记录，不能补数字。
4. **TP-FP mean latency**：有逐数据集值，来源为 runtime CSV；计划中的单行总体均值需要先规定 macro 还是 sample-weighted aggregation。
5. **Self-Refine answer-change/input tokens/latency**：均在 runtime CSV 和 low-cost diagnostics CSV 中完整记录。
6. **RARR answer-change/input tokens/latency**：均在 runtime CSV 和 low-cost diagnostics CSV 中完整记录。
7. **AGR answer-change rate**：在 parse-repaired main CSV 中有相对 TP-FP 的逐数据集值。
8. **AGR LLM calls/query = 1 + trigger**：只能作为协议表达；旧 artifact 没有精确 `llm_calls` 字段。
9. **AGR mean input tokens**：`UNKNOWN`，旧 artifact 未记录。
10. **AGR mean latency**：有逐数据集值；单行总体值需要明确聚合规则。

- **重要**：Table 7 当前设计没有 Dataset 列，却引用逐数据集 runtime。填表前必须决定使用 macro average 还是 sample-weighted average，否则没有唯一数值。

## 8. Figure 1：Failure-mode example

- **推荐真实案例 Markdown**：`outputs/figure1_value_competition_case_for_paper.md`
- **同一案例结构化 JSON**：`outputs/figure1_value_competition_case.json`
- **备选案例**：`outputs/figure1_real_case_for_paper.md` 和 `outputs/figure1_real_case.json`
- **状态**：案例数据已有；最终绘图文件未在 nightly 包中发现，需要据此排版绘制。

## 9. Figure 2：AGR workflow

- **算法流程源**：`outputs/paper_assets_final/jiis_major_revision_audit/algorithm1_latex.tex`
- **公式源**：`outputs/paper_assets_final/jiis_major_revision_audit/method_formula_latex.tex`
- **方法审计**：`outputs/paper_assets_final/jiis_major_revision_audit/method_algorithm_audit.md`
- **最终 Figure 2 图片文件**：`UNKNOWN`。未发现与计划标题完全对应的最终 PDF/PNG/SVG。

## 10. Figure 3：Dataset-wise F1 comparison

- **正确数据源**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/fairness_repair/metrics/main_results_parse_repaired.csv`
- **计划要求筛选的方法**：TP-FP RAG、Self-Refine-FP adaptation、RARR-FP adaptation、AGR。
- **计划要求指标**：三个数据集各自的 F1。
- **现有 Figure3 文件**：`fairness_repair/figures/Figure3_parse_repaired.pdf/.png`
- **关键问题**：现有 Figure3 实际画的是 9 个方法的 macro EM，不是计划要求的 4 个方法 × 3 数据集 F1。因此现有图片不能直接使用；只能从 main-results CSV 重新绘制。
- **现有 Figure3 source CSV**：`fairness_repair/figures/Figure3_parse_repaired_source.csv` 也只有 macro EM/F1，不是 dataset-wise 作图矩阵。

## 11. Figure 4：Net repair

- **直接作图 CSV**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/figures/figure_agr_repair_harm_source.csv`
- **完整 repair-harm 表**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/metrics/repair_harm_all.csv`
- **现有图**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/figures/figure_agr_repair_harm.pdf` 和 `.png`。
- **状态**：数据齐全；若计划只画 net repair，应从 source CSV 的 `net_repair` 列重画，现有图展示的是 repair 与 harm 双柱。

## 12. Appendix A：Feature exposure and naming

- **命名源**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/reports/paper_safe_method_naming.md`
- **claims 边界**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/reports/paper_safe_claims_audit.md`
- **feature 源**：见本清单 Table 6。

## 13. Appendix B：Full parse-repaired results

- **完整 27 行源**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/fairness_repair/metrics/main_results_parse_repaired.csv`
- **现成表**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/fairness_repair/tables/Table4_parse_repaired.md`

## 14. Appendix C：Paired bootstrap CI

- **完整 108 行源**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/fairness_repair/ci/paired_bootstrap_all_parse_repaired.csv`
- **注意**：必须使用带 `_parse_repaired` 的版本，原 nightly CI 含未修复 FaithfulRAG 行。

## 15. Appendix D：Parse-failure audit

- **before/after CSV**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/fairness_repair/validation/parse_failure_before_after.csv`
- **决策报告**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/fairness_repair/reports/SECTION_5_1_PARSE_FAILURE_DECISION.md`
- **dry-run 验证**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/fairness_repair/dryrun_validation.json`
- **无法恢复的 5 条**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/fairness_repair/unrecoverable_rows.json`

## 16. Appendix E：Runtime diagnostics

- **主要源文件**：同 Table 7。
- **缺失事实**：15 个 legacy method-dataset 行缺少 input-token 或 LLM-call 字段。
- **状态**：这些字段没有更底层的已记录数据，必须保持 `UNKNOWN`，不能从输出 token 或 latency 反推。

## 17. Appendix F：Qualitative cases

- **paper-ready Markdown**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/cases/paper_ready_case_shortlist.md`
- **结构化 JSONL**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/cases/paper_ready_case_shortlist.jsonl`
- **内容**：2 个主文候选和 5 个附录候选。

## 18. Appendix G：Deterministic heuristics and diagnostic controls

- **heuristic metrics**：`outputs/aei_submission_closure_v1/metrics/deterministic_heuristic_metrics.csv`
- **heuristic predictions**：`outputs/aei_submission_closure_v1/predictions/strong_baselines/deterministic_heuristic_predictions.jsonl`
- **heuristic bootstrap CI**：`outputs/aei_submission_closure_v1/ci/deterministic_heuristic_bootstrap_ci.csv`
- **现成 LaTeX comparison**：`outputs/aei_submission_closure_v1/latex_tables/table_deterministic_heuristic_comparison.tex`
- **现成 LaTeX CI**：`outputs/aei_submission_closure_v1/latex_tables/table_deterministic_heuristic_ci.tex`
- **已明确包含**：BM25-top Cue、Majority Family、Latest Timestamp、Temporal-Only、Hard Top-Candidate 等。
- **HCR 独立 metrics**：`UNKNOWN`。项目只在 prompt archive 中把 HCR 描述为 hard-candidate replacement；若用 `Hard Top-Candidate` 代表 HCR，必须写明映射依据，不能直接改名。
- **FaithfulRAG/CRAG 数值源**：parse-repaired main CSV（FaithfulRAG）和原 nightly main CSV/parse-repaired main CSV（CRAG 行未变）。

## 19. Appendix H：ArchivalQA offline check

- **汇总 CSV**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/metrics/archivalqa_appendix_existing_only.csv`
- **现成 Markdown**：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/tables/archivalqa_appendix_existing_only.md`
- **底层预测**：
  - `outputs/aei_submission_closure_v1/predictions/strong_baselines/tp_fp_rag_archivalqa500.jsonl`
  - `outputs/aei_submission_closure_v1/predictions/strong_baselines/agr_archivalqa500.jsonl`
  - `outputs/aei_submission_closure_v1/predictions/strong_baselines/fp_csr_archivalqa500.jsonl`
- **状态**：只有这三种方法，不能称为完整 ArchivalQA baseline grid。

## 最需要优先处理的真实缺口

1. **Figure 3 必须重画**：现有图与计划指标不一致。
2. **Table 7 必须先规定聚合方式**：当前源是逐数据集值，计划表却没有 Dataset 列。
3. **TP-FP/AGR input tokens 与 measured LLM calls 不存在**：保持 `UNKNOWN`；1 或 1+trigger 只能标成 protocol count。
4. **Table 2 原始完整 notation table 未定位**：需要从论文正文源文件取出。
5. **Figure 2 最终图片未定位**：只有公式、算法和方法审计材料。
6. **HCR 独立结果未定位**：Hard Top-Candidate 只能作为候选映射，不能静默改名。
