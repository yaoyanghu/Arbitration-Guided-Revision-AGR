# New_ChronoRAG 实验审计报告

## 1. 审计范围

- 项目路径：`/home/huyaoyang/Projects/flashrag_project_20251213/New_ChronoRAG/`
- 审计时间：2026-05-23，远程服务器 `huyaoyang@n1`。
- 检查文件类型：`*.json`, `*.jsonl`, `*.csv`, `*.tsv`, `*.txt`, `*.log`, `*.out`, `*.err`, `*.md`, `*.yaml`, `*.yml`, `*.sh`, `*.py`, `*.ipynb`, `*.tex`。
- 执行过的命令类型：`find`, `grep`, `sed`, `python3` 轻量解析脚本，用于目录扫描、CSV/JSON/JSONL 读取、样本数统计、日志关键词搜索、trace 字段检查。
- 未执行的操作：未修改源码，未删除文件，未启动训练，未重跑大规模评测。只新增本审计报告文件。
- 备注：服务器未安装 `rg`，关键词搜索改用 `grep -RIn`。

## 2. 项目结构概览

顶层目录中与实验审计直接相关的路径如下：

| 类别 | 路径 | 审计观察 |
|---|---|---|
| 配置 | `configs/`, `configs/ablations_full/` | 有 HOH-1024、TempRAGEval-1244、HotpotQA、2Wiki、pilot 与 full ablation 配置。|
| 数据 | `data/processed/`, `data/corpus/` | 有 `hoh_formal_1024.jsonl`、`temprageval_formal_1244.jsonl` 及对应 corpus。|
| 索引 | `indexes/` | 有 `hoh_formal_1024_bm25`、`temprageval_formal_1244_bm25`、Hotpot/2Wiki/pilot/noise 索引。|
| 运行产物 | `runs/` | 发现 formal main、strong formal、full ablation、HotpotQA、2Wiki、pilot、Route B/C 等大量 run。|
| 日志 | `logs/` | 有 formal 与 route 日志，但若干早期 casebook/log 为空，formal stageG run 本身主要靠 run 目录内 artifacts。|
| 输出表格 | `outputs/jiis_final_evidence_package/`, `outputs/jiis_full_ablation/`, `outputs/paper_assets_v4_experiment_upgrade/20260414_220953/`, `outputs/Online_outputs/data/` | 有论文表格、bootstrap CI、ablation、public boundary、efficiency、targeted metrics 等整合结果。|
| 文档 | `docs/`, `notes/`, `reports/`, root `*.md` | 有 run plan、readiness、claim-to-evidence、table pack、reviewer audit 等说明。|
| 入口脚本 | `src/eval/run_mainline_baselines.py`, `src/eval/eval_conflict_aware_rag.py`, `outputs/Online_outputs/data/generate_all_artifacts.py`, `outputs/paper_assets_v4_experiment_upgrade/generate_assets.py` | 主实验与表格生成逻辑主要集中在这些脚本。|

项目内相关文件规模：共扫描到约 2997 个相关后缀文件，其中 `.jsonl` 1347 个、`.md` 746 个、`.json` 536 个、`.yaml` 152 个、`.py` 84 个、`.csv` 60 个、`.log` 44 个。

## 3. 已发现实验总览

| 编号 | 数据集 | 方法/实验 | 脚本/配置 | 结果文件 | 日志/说明 | 样本数 | 指标 | 状态 |
|---|---|---|---|---|---|---:|---|---|
| E1 | HOH-1024 | vanilla, fixed-pool baseline, no_temporal, no_conflict, full_model | `configs/conflict_aware_rag_hoh_formal_1024_linux.yaml`; `src/eval/run_mainline_baselines.py` | `runs/stageG_main_formal_hoh1024_20260414__*/metrics.json`; `outputs/jiis_final_evidence_package/main_table_v2.csv` | `runs/stageG_main_formal_hoh1024_20260414/summary.json` | 1024 | EM, Token F1, CTR, TFA/CFA in derived table | 完整，适合主表，但需保守表述 |
| E2 | TempRAGEval-1244 | vanilla, fixed-pool baseline, no_temporal, no_conflict, full_model | `configs/conflict_aware_rag_temprageval_formal_1244_linux.yaml`; `src/eval/run_mainline_baselines.py` | `runs/stageG_main_formal_temprageval1244_20260414__*/metrics.json`; `outputs/jiis_final_evidence_package/main_table_v2.csv` | `runs/stageG_main_formal_temprageval1244_20260414/summary.json` | 1244 | EM, Token F1, CTR, TFA/CFA in derived table | 完整，适合主表，但提升幅度较小 |
| E3 | HOH-1024 | strong fixed-pool comparators: latest_timestamp_wins, temporal_only_rerank, judge_verify_pipeline | `configs/conflict_aware_rag_hoh_formal_1024_linux.yaml` | `runs/stageG_strong_formal_hoh1024_20260414__*/metrics.json`; `outputs/jiis_final_evidence_package/external_baseline_table.csv` | `outputs/paper_assets_v4_experiment_upgrade/20260414_220953/STRONG_BASELINE_RESULTS.md` | 1024 | EM, F1, CTR | 完整，但 judge 在 HOH 略高于 Full Model，不能声称全胜 |
| E4 | TempRAGEval-1244 | strong fixed-pool comparators: latest_timestamp_wins, temporal_only_rerank, judge_verify_pipeline | `configs/conflict_aware_rag_temprageval_formal_1244_linux.yaml` | `runs/stageG_strong_formal_temprageval1244_20260414__*/metrics.json`; `external_baseline_table.csv` | `STRONG_BASELINE_RESULTS.md` | 1244 | EM, F1, CTR | 完整，但 judge EM/F1 高于 Full Model，不能声称全胜 |
| E5 | HOH-1024 | full-dataset ablation x7 | `configs/ablations_full/hoh1024__*.yaml` | `runs/stageG_full_ablation_hoh1024_20260508__*/metrics.json`; `full_dataset_ablation_results.csv` | `outputs/jiis_full_ablation/FULL_ABLATION_FORENSIC_VERIFICATION_REPORT.md` | 1024 | EM, F1, CTR; TFA/CFA NA for ablation rows | 完整，但部分组件零影响 |
| E6 | TempRAGEval-1244 | full-dataset ablation x7 | `configs/ablations_full/temprageval1244__*.yaml` | `runs/stageG_full_ablation_temprageval1244_20260508__*/metrics.json`; `full_dataset_ablation_results.csv` | `FULL_ABLATION_FINAL_EVIDENCE_STATUS.md` | 1244 | EM, F1, CTR; TFA/CFA NA for ablation rows | 完整，但 no_candidate F1 反向更高 |
| E7 | HOH/TempRAGEval | paired bootstrap significance | `outputs/Online_outputs/data/generate_all_artifacts.py`; `outputs/paper_assets_v4_experiment_upgrade/generate_assets.py` | `outputs/jiis_final_evidence_package/significance_table.csv`; `ablation_bootstrap_ci.csv` | `commands_to_reproduce.md`; `HYPERPARAMETER_INVENTORY_REPORT.md` | 1024/1244 paired | 95% CI, seed=42, 10000 resamples | 大体可用；有 p_value=2.0 格式/计算异常需修正 |
| E8 | HotpotQA | public/boundary | `configs/conflict_aware_rag_hotpotqa_dev_distractor*.yaml` | `runs/hotpotqa_batch_20260404__*/metrics.json`; `outputs/paper_assets_v4_experiment_upgrade/20260414_220953/public_dataset_results.csv` | `PUBLIC_DATASET_SUPPLEMENTARY_RESULTS.md` | 7405 in full run; 500 in supplementary table | EM, F1, CTR | 有结果，但 7405 与 500 表格来源需解释，适合 appendix/boundary |
| E9 | 2WikiMultiHopQA-500 | public/boundary | `configs/conflict_aware_rag_2wikimultihopqa_dev_500_linux.yaml` | `runs/stageG_public_2wiki500_20260414__*/metrics.json`; `public_dataset_results.csv` | `PUBLIC_DATASET_SUPPLEMENTARY_RESULTS.md` | 500 | EM, F1, CTR | 完整 appendix 级别 |
| E10 | Arbitration-mismatch/targeted | subset metrics | paper assets scripts | `targeted_metrics.csv`; `PROBLEM_IMPORTANCE_STATS.md`; `selective_conflict_results.csv` | `TARGETED_METRICS_RESULTS.md` | HOH temporal 158/conflict 549; Temp temporal 777/conflict 1239 | TFA, CFA, gain cases | 部分完成；可解释但还不是充分 case-level causal analysis |
| E11 | Decision trace | per-example trace | `eval_conflict_aware_rag.py`; run artifacts | `predictions.jsonl`, `scored_candidates.jsonl`, `retrieval_results.jsonl` | `PER_EXAMPLE_ARTIFACT_AVAILABILITY_REPORT.md` | 与各 run 一致 | trace fields, scores | 部分可审计；缺 rejection reason/hard mismatch reason 等字段 |
| E12 | Efficiency/latency | overhead grid | generated assets | `outputs/paper_assets_v4_experiment_upgrade/20260414_220953/overhead_latency.csv` | `OVERHEAD_LATENCY_SUMMARY.md` | pilot 100 grid, 23 ok records | ms/query, elapsed_sec, pairwise count | 有轻量 pilot；不足以作为正式 Table 7 主结论 |

## 4. 主实验审计

主实验已发现并可核验。核心文件为：

- `outputs/jiis_final_evidence_package/main_table_v2.csv`
- `runs/stageG_main_formal_hoh1024_20260414__full_model/metrics.json`
- `runs/stageG_main_formal_temprageval1244_20260414__full_model/metrics.json`
- `runs/stageG_main_formal_hoh1024_20260414__stronger_retrieval_template/metrics.json`
- `runs/stageG_main_formal_temprageval1244_20260414__stronger_retrieval_template/metrics.json`

主表数字：

| 数据集 | 方法 | EM | Token F1 | CTR | TFA | CFA |
|---|---|---:|---:|---:|---:|---:|
| HOH | vanilla_rag_extractive | 0.0000 | 0.2025 | 0.9463 | 0.0000 | 空 |
| HOH | stronger_retrieval_template / fixed-pool baseline | 0.1807 | 0.2706 | 0.9463 | 0.3734 | 空 |
| HOH | no_temporal | 0.1865 | 0.2811 | 0.9463 | 0.3671 | 空 |
| HOH | no_conflict | 0.1973 | 0.3005 | 0.9473 | 0.4304 | 空 |
| HOH | full_model | 0.2021 | 0.3056 | 0.9463 | 0.4304 | 空 |
| TempRAGEval | vanilla_rag_extractive | 0.0000 | 0.1278 | 0.3465 | 0.0000 | 空 |
| TempRAGEval | stronger_retrieval_template / fixed-pool baseline | 0.0659 | 0.1059 | 0.3453 | 0.0940 | 空 |
| TempRAGEval | no_temporal | 0.0506 | 0.0942 | 0.3432 | 0.0734 | 空 |
| TempRAGEval | no_conflict | 0.0780 | 0.1248 | 0.4100 | 0.1094 | 空 |
| TempRAGEval | full_model | 0.0780 | 0.1244 | 0.4092 | 0.1094 | 空 |

审计判断：

- 可以支撑论文中“在固定证据池、固定 evidence budget 下，Full Model 相比 strict fixed-pool baseline 有稳定提升”的主张。
- 不能支撑“Full Model 全面超过所有 comparator”。HOH 中 `judge_verify_pipeline` EM=0.2031、F1=0.3085，略高于 Full Model 的 EM=0.2021、F1=0.3056；TempRAGEval 中 `judge_verify_pipeline` EM=0.0812、F1=0.1290，也高于 Full Model 的 EM=0.0780、F1=0.1244。
- Vanilla Extractive RAG 的 EM=0 很危险，若作为主要 baseline 容易被认为 strawman；但作为“extractive/free-span mode 的失败案例”可以保留，主比较应使用 stronger_retrieval_template 和 judge_verify_pipeline。
- `metrics.json` 原始文件不含 TFA/CFA；TFA/CFA 来自派生表 `targeted_metrics.csv` / `main_table_v2.csv`，论文中应说明这些是目标子集指标，不是原始 aggregate metrics 字段。

## 5. 统计显著性与置信区间审计

已发现 paired bootstrap 结果：

- `outputs/jiis_final_evidence_package/significance_table.csv`
- `outputs/jiis_final_evidence_package/ablation_bootstrap_ci.csv`
- `outputs/Online_outputs/data/generate_all_artifacts.py` 中 `paired_bootstrap_ci(...)`，默认 `n_resamples=10000`, `seed=42`。
- `outputs/paper_assets_v4_experiment_upgrade/generate_assets.py` 中 `align(...)` 按 `query_id` 交集排序后 bootstrap。

主实验显著性：

| 比较 | 指标 | Δ | 95% CI | n | 显著 |
|---|---|---:|---|---:|---|
| HOH Full vs Fixed-Pool | EM | +0.0215 | [0.0127, 0.0303] | 1024 | yes |
| HOH Full vs Fixed-Pool | F1 | +0.0350 | [0.0252, 0.0458] | 1024 | yes |
| HOH Full vs No Temporal | EM | +0.0156 | [0.0059, 0.0254] | 1024 | yes |
| HOH Full vs No Conflict | EM | +0.0049 | [0.0010, 0.0098] | 1024 | yes, but small |
| TempRAGEval Full vs Fixed-Pool | EM | +0.0121 | [0.0064, 0.0185] | 1244 | yes |
| TempRAGEval Full vs Fixed-Pool | F1 | +0.0185 | [0.0123, 0.0256] | 1244 | yes |
| TempRAGEval Full vs No Temporal | EM | +0.0273 | [0.0185, 0.0370] | 1244 | yes |

风险：

- `ablation_bootstrap_ci.csv` 中若干零差异行的 `bootstrap_p_value` 为 `2.0`，这是非法 p-value。证据：`full_model vs no_top_gap_filtering`、`full_model vs no_duplicate_suppression` 等零差异行。应在论文前修正为 `1.0` 或 `NA`，否则审稿人会质疑统计实现。
- `outputs/Online_outputs/data/generate_all_artifacts.py` 的一版实现按 `vals[:n]` 配对，虽标注 `paired_by=query_id`，但没有显式 assert qid 对齐。`generate_assets.py` 的 `align(...)` 更可信，因为按 qid 交集排序。论文应引用最终 `jiis_final_evidence_package`，并保留实现说明。

最小补充方案：修正 bootstrap p-value 输出边界；在方法/附录写明 resamples=10000、seed=42、paired by query_id、percentile CI；保留一个脚本或伪代码片段说明 qid 对齐。

## 6. 消融实验审计

已完成 full-dataset ablation，不再只是 256-slice。证据：

- `outputs/jiis_final_evidence_package/full_dataset_ablation_results.csv`
- `runs/stageG_full_ablation_hoh1024_20260508__*/predictions.jsonl` 每个 1024 行。
- `runs/stageG_full_ablation_temprageval1244_20260508__*/predictions.jsonl` 每个 1244 行。
- `outputs/jiis_full_ablation/FULL_ABLATION_FORENSIC_VERIFICATION_REPORT.md` 声明 dataset size、fixed-pool consistency、variant semantics、metric sanity 均 PASS。

主要 ablation：

| 数据集 | Variant | EM | F1 | CTR | 相对 full 解释 |
|---|---|---:|---:|---:|---|
| HOH | full_model | 0.2021 | 0.3056 | 0.9463 | 基准 |
| HOH | no_candidate_extraction | 0.0000 | 0.2052 | 0.9463 | EM 崩溃，支持候选抽取必要性 |
| HOH | family_only | 0.1426 | 0.2093 | 0.7236 | 大幅下降，支持 family/arbitration 机制 |
| HOH | no_family_construction | 0.1924 | 0.2917 | 0.9473 | 小幅下降 |
| HOH | no_hard_temporal_rules | 0.1982 | 0.3005 | 0.9463 | 小幅且 CI 跨零 |
| HOH | no_top_gap_filtering | 0.2021 | 0.3054 | 0.9463 | 基本无影响 |
| HOH | no_duplicate_suppression | 0.2021 | 0.3056 | 0.9463 | 无影响 |
| HOH | temporal_only | 0.1992 | 0.3036 | 0.9434 | 与 full 差异不显著 |
| TempRAGEval | full_model | 0.0780 | 0.1244 | 0.4092 | 基准 |
| TempRAGEval | no_candidate_extraction | 0.0000 | 0.1539 | 0.4092 | EM 崩溃但 F1 反向更高，不能简单说全面变差 |
| TempRAGEval | family_only | 0.0482 | 0.0724 | 0.2548 | 明显下降 |
| TempRAGEval | no_family_construction | 0.0691 | 0.1121 | 0.3714 | 小幅下降 |
| TempRAGEval | no_hard_temporal_rules | 0.0587 | 0.1115 | 0.4092 | EM/F1 下降 |
| TempRAGEval | no_top_gap_filtering | 0.0780 | 0.1244 | 0.4092 | 无影响 |
| TempRAGEval | no_duplicate_suppression | 0.0780 | 0.1244 | 0.4092 | 无影响 |
| TempRAGEval | temporal_only | 0.0523 | 0.1029 | 0.4956 | EM/F1 降，CTR 反而升 |

审计判断：

- “Full Model 与各组件移除版本的 ablation”已做完，且是 full dataset。
- “No relation constraint”没有作为明确同名 ablation 发现；可能被包含在 `no_hard_temporal_rules` 或 `no_family_construction` 中，但不能按该名字写成独立实验。
- “No temporal admissibility”没有完全同名，最接近 `no_hard_temporal_rules` / `no_temporal` / `temporal_only`。论文中应使用实际 variant 名称。
- 不能声称“所有组件都必要”，因为 top-gap filtering 与 duplicate suppression 近似零影响。
- 不存在 cherry-pick 风险用于 full ablation；但强基线扩展和 Route B/C 仍多为 pilot，应分开。

## 7. 强基线审计

已发现的强/较强 baseline：

- `judge_verify_pipeline`：formal HOH/TempRAGEval 均运行。证据：`runs/stageG_strong_formal_*__judge_verify_pipeline/metrics.json`。
- `latest_timestamp_wins`、`temporal_only_rerank`：formal 均运行。证据：`external_baseline_table.csv`。
- `hyde_like`, `crag_like`, `self_rag_style_baseline`, `astute_style_baseline`：只作为 pilot256 或 inspired controls。证据：`external_baseline_table.csv` 与 `STRONG_BASELINE_RESULTS.md`。
- `learned_scorer.py` 与 `train_learned_scorer.py` 存在，但未发现 formal learned reader / DeBERTa / RoBERTa QA reader / pairwise answer reranker 的完整结果表。

风险判断：

- 当前 baseline 比最初 Vanilla Extractive RAG 强很多，已有 judge-verify 和 fixed-pool comparators，可以避免“只打弱 baseline”的主要质疑。
- 但没有真正 learned reader、DeBERTa/RoBERTa QA reader、pairwise neural reranker 的 formal full-dataset 结果；如果论文声称“against strong learned readers”则不成立。
- Judge-Verify 在 HOH 和 TempRAGEval 上局部高于 Full Model，因此不能写“Full Model universally outperforms all comparators”。

## 8. Boundary experiments 审计

已发现 boundary/public 结果：

- HotpotQA full dev-like run：`runs/hotpotqa_batch_20260404/summary.json`，query_count=7405。
- HotpotQA-500 supplementary table：`outputs/paper_assets_v4_experiment_upgrade/20260414_220953/public_dataset_results.csv`。
- 2WikiMultiHopQA-500：`runs/stageG_public_2wiki500_20260414__*/metrics.json` 与 `public_dataset_results.csv`。

Supplementary 500 表：

| 数据集 | 方法 | EM | F1 | CTR |
|---|---|---:|---:|---:|
| HotpotQA-500 | stronger_retrieval_template | 0.048 | 0.0726 | 0.360 |
| HotpotQA-500 | no_conflict | 0.050 | 0.0770 | 0.351 |
| HotpotQA-500 | judge_verify_pipeline | 0.046 | 0.0717 | 0.349 |
| HotpotQA-500 | full_model | 0.050 | 0.0753 | 0.349 |
| 2WikiMultiHopQA-500 | stronger_retrieval_template | 0.264 | 0.3169 | 0.4785 |
| 2WikiMultiHopQA-500 | judge_verify_pipeline | 0.274 | 0.3250 | 0.4800 |
| 2WikiMultiHopQA-500 | full_model | 0.266 | 0.3189 | 0.4800 |

审计判断：

- 有正式数字，不只是口头描述。
- 可以支撑“方法边界：ChronoRAG 更适合 fixed-pool temporal arbitration，而不是一般 multi-hop QA 的通用增强器”。
- HotpotQA 存在 7405 full run 与 500 supplementary table 两套结果，应在论文中只选择一套讲清楚，避免表格口径冲突。
- 未发现 TimeQuestions-style subset 的正式结果。

## 9. Arbitration-mismatch 子集分析审计

已发现目标子集分析证据：

- `outputs/paper_assets_v4_experiment_upgrade/20260414_220953/targeted_metrics.csv`
- `outputs/paper_assets_v4_experiment_upgrade/20260414_220953/PROBLEM_IMPORTANCE_STATS.md`
- `outputs/paper_assets_v4_experiment_upgrade/20260414_220953/selective_conflict_results.csv`
- `outputs/paper_assets_v4_experiment_upgrade/20260414_220953/temprageval_citation_analysis.csv/json/md`

关键数字：

- HOH：gold evidence in pool 987/1024=0.9639；stale-current conflict coexistence 549/1024=0.5361；baseline error arbitration mismatch 18/839=0.0215；Full gain cases 22/1024=0.0215。
- TempRAGEval：gold evidence in pool 978/1244=0.7862；stale-current conflict coexistence 1239/1244=0.9960；baseline error arbitration mismatch 173/1162=0.1489；Full gain cases 15/1244=0.0121。
- targeted metrics：HOH temporal subset 158、conflict subset 549；TempRAGEval temporal subset 777、conflict subset 1239。

审计判断：

- 能解释“整体提升小”的原因：实际 full_model gain cases 占比只有 HOH 2.15%、TempRAGEval 1.21%，而且大量样本是 tie。
- 能部分支持“在真正需要仲裁的样本上收益更明显”，但当前证据更多是 ratio 与 subset metrics，不是系统性的 case-level causal proof。
- 若论文重点强调 arbitration-mismatch，建议补一个小表：mismatch subset 上的 Full vs baseline EM/F1/TFA/CFA，并列出样本数、选择规则、qid 对齐方式。

## 10. Decision trace 与可审计性审计

逐样本产物存在：

- `runs/stageG_main_formal_hoh1024_20260414__full_model/predictions.jsonl`：1024 行。
- `runs/stageG_main_formal_temprageval1244_20260414__full_model/predictions.jsonl`：1244 行。
- `scored_candidates.jsonl` 与 `retrieval_results.jsonl` 对应存在。
- `outputs/jiis_final_evidence_package/PER_EXAMPLE_ARTIFACT_AVAILABILITY_REPORT.md` 也确认 predictions、scored candidates、retrieval results 存在。

抽样检查 trace 字段：

- `predictions.jsonl` 顶层字段：`query_id`, `query`, `predicted_answer`, `selected_evidence`, `arbitration_trace`, `metrics`。
- `arbitration_trace` 包含：`answer_mode`, `focus_first_evidence`, `generator_mode`, `posterior_arbitration`, `selected_sentences`。
- `posterior_arbitration` 包含：`retrieval_prior`, `temporal_expert_score`, `conflict_expert_score`, `evidence_attention_weights`, `gate_gamma`。
- `selected_evidence` 包含：`doc_id`, `title`, `timestamp`, `text`, `score`, `temporal_expert_score`, `conflict_expert_score`, `evidence_attention_weight`, `retrieval_prior`。
- `scored_candidates.jsonl` 包含更细的 `notes.structured`, `notes.temporal`, `notes.posterior`, `conflict_score`, `arbitration_score` 等。

缺口：

- 未发现明确字段：`candidate_answers`、`rejection_reason`、`hard_mismatch_reason`、`temporal_admissibility_score`（有 temporal_expert_score，但名称和语义不同）、显式 `evidence_family`。
- 因此可以写“decision trace records selected evidence, candidate scores, temporal/conflict expert scores, posterior weights”，但不宜写“完整记录 rejection reason / hard mismatch reason”。
- “auditable arbitration layer”可以保留，但要定义为可追溯的 scoring/selection trace，而不是完整法律式审计日志。

## 11. 运行成本与效率实验审计

已发现效率相关文件：

- `outputs/paper_assets_v4_experiment_upgrade/20260414_220953/overhead_latency.csv`
- `outputs/paper_assets_v4_experiment_upgrade/20260414_220953/OVERHEAD_LATENCY_SUMMARY.md`
- `runs/stageI_routeB_*__/metrics.json` 中有 `arbitration_latency_ms_per_query`。

审计判断：

- `overhead_latency.csv` 记录 23 个 ok records，字段包括 `elapsed_sec`, `ms_per_query`, `retrieval_top_k`, `evidence_top_k`, `avg_candidates_per_query`, `pairwise_arbitration_count`。
- 主要是 pilot 100 grid，不是 HOH-1024/TempRAGEval-1244 的 formal runtime table。
- 部分结果中 Full Model 与 simpler baseline 的耗时差异很小，甚至可能更快；可能原因是 pipeline 为 deterministic heuristic/CPU lightweight，且不同 variant 的 generation/retrieval path 不完全等价，缓存/候选数不同。不能把它写成“Full Model intrinsically faster”。
- 若论文有 Table 7，建议降为 appendix overhead sanity table，并明确 pilot setting；若要正式成本结论，需要 full formal runtime、token/API/GPU/CPU time 统一记录。

## 12. 当前论文结论能否被实验支撑

### 可以放心写的结论

- Full Model improves over a strict fixed-pool baseline on HOH-1024 and TempRAGEval-1244 under controlled evidence budgets.
- Improvements over fixed-pool baseline have paired bootstrap 95% CI support, with 10000 resamples and seed 42.
- Full-dataset ablations show candidate extraction and family/arbitration mechanisms are important.
- Boundary results on HotpotQA/2Wiki suggest the method is not a universal multi-hop QA enhancer and is better framed as fixed-pool temporal answer-value arbitration.
- Per-example artifacts exist and allow tracing selected evidence plus temporal/conflict scores.

### 需要降调写的结论

- “Full Model beats strong baselines”应改为“competitive with judge-verify and improves over fixed-pool baseline; judge-verify is a close comparator and sometimes higher.”
- “All components are essential”应改为“candidate extraction and family/arbitration are important; top-gap filtering and duplicate suppression had negligible effect in current runs.”
- “Decision trace is fully auditable”应改为“records selected evidence and scoring trace; rejection/hard-mismatch reasons are not fully materialized as explicit fields.”
- “Efficiency advantage”应改为“lightweight overhead pilot suggests low arbitration overhead; formal runtime costs remain limited.”

### 暂时不能写的结论

- Full Model universally outperforms all comparators.
- State-of-the-art on general multi-hop QA.
- Strong learned reader / DeBERTa / RoBERTa / neural reranker baselines have been beaten.
- All ablation components are necessary.
- Decision trace contains explicit rejection reasons and hard mismatch reasons for every candidate.
- Full Model is faster than simple baselines as a general property.

## 13. 缺失实验与补做优先级

| 优先级 | 缺什么 | 为什么重要 | 可能涉及脚本/文件 | 预计输出 | 进入论文位置 |
|---|---|---|---|---|---|
| P0 | 修正 `ablation_bootstrap_ci.csv` 中 `bootstrap_p_value=2.0` 的非法值 | p-value > 1 会直接暴露统计实现问题 | `outputs/Online_outputs/data/generate_all_artifacts.py`; `outputs/jiis_final_evidence_package/ablation_bootstrap_ci.csv` | 修正后的 CSV/TEX；说明 zero-diff p=1 或 NA | Table 5/Appendix CI |
| P0 | 论文表述降调：不要写 universal outperformance / all components essential / complete rejection trace | 当前结果不支持，容易被审稿人抓住 | 论文正文和 tables notes | 修改后的 claim wording | 全文 |
| P1 | mismatch subset 专门表 | 证明收益集中于 arbitration-needed cases | 可基于现有 `predictions.jsonl`, `targeted_metrics.csv`, `PROBLEM_IMPORTANCE_STATS.md` 轻量统计 | `arbitration_mismatch_subset_results.csv` | Table 4 或分析小节 |
| P1 | formal efficiency table | 当前只有 pilot overhead，Table 7 主张不足 | 可在不重跑模型的前提下解析 existing timestamps/metrics；若缺则需轻量 rerun timing | `formal_runtime_costs.csv` | Table 7/Appendix |
| P1 | 强 baseline 描述补强 | 避免 Vanilla EM=0 strawman | 已有 `judge_verify_pipeline`; 如时间允许补 learned reader/reranker | `strong_baseline_formal_results.csv` | Table 3 |
| P1 | 决策 trace 字段补充或论文降调 | 目前无 rejection/hard mismatch explicit field | 若不改代码，则做 trace field inventory；若改代码另开任务 | `decision_trace_field_inventory.md` | Case study/Method |
| P2 | TimeQuestions-style subset | 边界实验更完整 | 新数据准备/评测脚本 | formal subset results | Appendix |
| P2 | 3 seed 重采样 | 当前 deterministic + bootstrap 已可用，多 seed 可增强 | run configs with seeds | seed variance table | Appendix |

## 14. 推荐论文表格映射

| 论文位置 | 建议使用文件 | 当前可写性 |
|---|---|---|
| Table 2 主结果 | `outputs/jiis_final_evidence_package/main_table_v2.csv`; 原始 `runs/stageG_main_formal_*__/metrics.json` | 可以写；标注 fixed-pool、n=1024/1244、不要把 Vanilla 作为唯一 baseline |
| Table 3 强基线/Comparator | `outputs/jiis_final_evidence_package/external_baseline_table.csv`; `runs/stageG_strong_formal_*__/metrics.json`; `STRONG_BASELINE_RESULTS.md` | 可以写；必须说明 judge_verify close/occasionally higher，HyDE/CRAG/Self-RAG/Astute 是 inspired/pilot |
| Table 4 Boundary / target subset | `public_dataset_results.csv`; `targeted_metrics.csv`; `PROBLEM_IMPORTANCE_STATS.md` | 部分可写；建议拆成 Appendix boundary 与 mismatch subset，不要混成主胜率表 |
| Table 5 Ablation | `outputs/jiis_final_evidence_package/full_dataset_ablation_results.csv`; `ablation_bootstrap_ci.csv` | 可以写；先修正 p-value=2.0；主文放 candidate/family，appendix 放零影响项 |
| Figure / Case study | `predictions.jsonl`, `scored_candidates.jsonl`, `temprageval_citation_analysis.csv/json` | 可以做 case study；不要声称含 rejection_reason/hard_mismatch_reason |
| Table 7 Efficiency | `overhead_latency.csv`, `OVERHEAD_LATENCY_SUMMARY.md`, `stageI_routeB_*__/metrics.json` | 不建议作为强主表；可 appendix sanity |
| 目前不能写的表 | learned reader / DeBERTa / RoBERTa / pairwise neural reranker formal comparison | 未发现完整结果 |

## 15. 逐项 checklist

| 实验需求 | 是否已完成 | 证据文件路径 | 关键指标 | 是否足以写进论文 | 风险 | 需要补做什么 |
|---|---|---|---|---|---|---|
| HOH-1024 / TempRAGEval-1244 主实验 | 已完成 | `outputs/jiis_final_evidence_package/main_table_v2.csv`; `runs/stageG_main_formal_*` | EM, F1, CTR, TFA | 是 | P1 | 降调 universal claims |
| Fixed-Pool Baseline / No Conflict / Temporal-only / Judge-Verify / Vanilla | 部分完成 | `main_table_v2.csv`; `external_baseline_table.csv` | EM, F1, CTR | 是，但 judge/vanilla 要谨慎 | P1 | 明确 baseline tier |
| TFA/CFA 指标 | 部分完成 | `targeted_metrics.csv`; `main_table_v2.csv` | TFA/CFA subset | 可以作为 target metrics | P1 | 说明不是 raw metrics.json 字段 |
| Paired bootstrap + 95% CI | 已完成但需修正 | `significance_table.csv`; `ablation_bootstrap_ci.csv`; scripts | CI, p, n=10000, seed=42 | 主实验可写 | P0 | 修 p-value=2.0，写明 qid pairing |
| Full-dataset ablation | 已完成 | `full_dataset_ablation_results.csv`; full ablation run dirs | EM/F1/CTR | 是 | P1 | 不要说所有组件必要 |
| subset-only ablation 风险 | 已解决主消融；强基线仍部分 pilot | `stageG_full_ablation_*`; `external_baseline_table.csv` | n=1024/1244 vs pilot256 | 主消融可写 | P1 | inspired controls 留 appendix |
| 强 learned baselines | 未发现 | 仅有 `train_learned_scorer.py` 等代码 | 无 formal results | 不能写 | P1 | 如需要，补 learned reader/reranker |
| Boundary experiments | 部分完成 | `public_dataset_results.csv`; Hotpot/2Wiki runs | EM/F1/CTR | appendix 可写 | P1 | 解释 Hotpot 7405 vs 500；TimeQuestions 未发现 |
| Arbitration-mismatch subset | 部分完成 | `PROBLEM_IMPORTANCE_STATS.md`; `targeted_metrics.csv` | mismatch/gain ratios, TFA/CFA | 可解释但不够强 | P1 | 生成 mismatch subset comparison table |
| Decision trace | 部分完成 | `predictions.jsonl`; `scored_candidates.jsonl` | selected evidence, scores | 可写“traceable scoring” | P1 | 降调或补 rejection/hard mismatch fields |
| Runtime/efficiency | 部分完成 | `overhead_latency.csv`; `stageI_routeB_*` | ms/query, elapsed | appendix 可写 | P1 | formal runtime/API/token/GPU/CPU table |

## 16. 最终判断

1. 上面论文优化建议中的实验是否基本做完？
   - 对“fixed-pool 主实验 + full-dataset ablation + bootstrap CI”而言，基本做完。
   - 对“强 learned baseline + 完整 trace 审计 + formal efficiency + mismatch subset 强证明”而言，未完全做完。

2. 哪些已经做完？
   - HOH-1024 与 TempRAGEval-1244 主实验。
   - Fixed-pool baseline、No Temporal、No Conflict、Vanilla、Judge-Verify、latest_timestamp、temporal-only rerank。
   - 7 个 full-dataset ablation x 2 datasets。
   - paired bootstrap CI，大体完成。
   - HotpotQA/2Wiki boundary 有正式数字。

3. 哪些只是部分完成？
   - 强基线：有 judge-verify 和 inspired controls，但无 learned reader/DeBERTa/RoBERTa formal。
   - Decision trace：有 scoring/selection trace，但缺 rejection reason/hard mismatch reason。
   - Arbitration-mismatch subset：有统计与 targeted metrics，但缺独立完整 comparison table。
   - Efficiency：有 pilot overhead，不足以支撑强 Table 7。

4. 哪些完全没发现？
   - TimeQuestions-style formal subset。
   - DeBERTa/RoBERTa QA reader formal run。
   - Pairwise answer reranker formal run。
   - 每候选 explicit rejection_reason / hard_mismatch_reason。
   - 明确名为 `No relation constraint` 的 formal ablation。

5. 当前是否适合马上改论文？
   - 适合马上改论文，但应按本报告降调：主张 fixed-pool arbitration 的可靠小幅提升，而不是通用 SOTA 或全面胜出。

6. 当前是否适合马上投稿 JIIS？
   - 不建议“原样马上投稿”。至少先做 P0：修正 bootstrap p-value 异常、调整强基线/trace/efficiency 相关表述。P1 中 mismatch subset 表和 formal efficiency 表强烈建议补。

7. 最合理的下一步是什么？
   - 第一步：修统计输出中非法 p-value，并冻结 `jiis_final_evidence_package` 的最终版本。
   - 第二步：按 Table 2/3/5 更新论文，同时删除或降调 unsupported claims。
   - 第三步：用已有 predictions 轻量生成 arbitration-mismatch subset comparison table；不需要重跑大实验。
   - 第四步：把 decision trace case study 改成“score/selection trace”示例，避免声称 rejection/hard mismatch 字段。
