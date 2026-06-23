# AGR 论文表格、图与附录安排优化版

> 版本：按最新 parse repair 结果与表格美化要求重新整理。  
> 使用结果包：`outputs/published_baseline_adaptations_20260621/nightly_closure_20260621_224528/fairness_repair/`  
> 核心原则：主文表格要干净，方法命名要简洁，表注解释 adaptation 和 inspired control，正文说明数据集角色，附录放完整细节。  
> 写作规则：正文和表格中尽量避免使用斜杠符号。文件路径除外。

---

# 一、先回答你的 8 个修改判断

## 1. Table 1 的 Decision unit 不应使用斜杠

应该改成更自然的并列表述：

| 原写法 | 建议写法 |
|---|---|
| Query / passage | Query and passage |
| Passage / context | Passage and context |
| Claim / answer | Claim and answer |
| Fact / statement | Fact and statement |

不建议写成 `Query 、passage`，因为英文表格里中英文标点混用不自然。最稳的是 `Query and passage`。

---

## 2. Table 2 不压缩也可以

可以不压缩。原论文 Table 2 是符号表，属于 Method 阅读辅助，不是结果表。只要表格不超过半页，保留完整符号表没有问题。

建议：

- 如果 Table 2 现在排版正常，就保留原表；
- 只删除明显重复或正文没有再用到的符号；
- 不要为了“简洁”删掉关键符号，否则 Method 会更难读。

结论：**Table 2 可以保留完整版本，不强制压缩。**

---

## 3. Table 3 的 Note 列可以删除

Note 列不是必要的。数据集角色可以放到正文里解释，不必放进表格。这样表更干净。

建议 Table 3 保留：

- Dataset
- n
- k_r
- k_e
- Ans@4
- Stale rate
- Conflict rate

然后正文用一段话解释：HOH 和 TempRAGEval 是主实验，TimeQA 是边界设置，ArchivalQA 只放附录。

---

## 4. Table 4 方法名和列名需要美化

主表中不要写太长的方法名：

| 原写法 | 建议写法 |
|---|---|
| Self-Refine-FP adaptation | Self-Refine* |
| RARR-FP adaptation† | RARR† |
| FP-CSR / strongest diagnostic control | FP-CSR |

表注解释：

- `*` 表示 fixed-pool adaptation；
- `†` 表示 RARR 的 external retrieval 被禁用，只保留 agreement checking and editing。

列名可以保留 `HOH EM`、`HOH F1` 这种短格式。如果用 LaTeX，建议把数据集作为一级表头，EM/F1 作为二级表头，会更美观。

---

## 5. Table 5 数据集名不要带样本数

主文表里写：

- HOH
- TempRAGEval
- TimeQA

不要写：

- HOH-1024
- TempRAGEval-1244
- TimeQA-500

样本数已经在 Dataset 表里交代，结果表不需要重复。

---

## 6. Table 6 不需要 Main or Appendix 列

`Main / Appendix` 这一列不适合放在学术论文正式表格里。它是写作规划信息，不是实验变量。

应删除这一列。

`Support/conflict facts` 改成：

> Support and conflict facts

---

## 7. Table 7 不要 Notes 列

Notes 列显得像工作备忘，不像论文表格。删除。

baseline 的解释放到正文里一句话说明，不要放进表格。

表名也不要写 `Runtime / overhead`，改成：

> Runtime and protocol overhead diagnostics

---

## 8. 本文档已按上述要求重排

下面给出最终建议表格、图和附录安排。

---

# 二、主文表格安排

## Table 1：方法定位表

### 表名

**Table 1. Conceptual positioning of AGR under the fixed-pool protocol**

### 最终表格建议

| Method class | Evidence state | Decision unit | Competing values | Output | Role in this paper |
|---|---|---|---|---|---|
| Adaptive retrieval | Updated | Query and passage | Implicit | New evidence | Related work |
| Context construction | Reorganized | Passage and context | Implicit | New context | Related work |
| Response revision | Fixed or updated | Full response | Implicit | Revised answer | Self-Refine* |
| RARR-style revision | Updated in original, fixed here | Claim and answer | Evidence agreement | Edited answer | RARR† |
| Fact-faithfulness control | Fixed here | Fact and statement | Support and conflict | Grounded answer | Appendix diagnostic |
| CRAG-style evaluator | Updated in original, fixed here | Retrieval quality | Implicit | Correction decision | Appendix diagnostic |
| Hard selection | Fixed candidates | Candidate value | Explicit but forced | Forced answer | Diagnostic control |
| AGR | Fixed pool | Candidate family | Explicit and local | Soft revision signal | Proposed method |

### 表注

`*` denotes a fixed-pool adaptation.  
`†` denotes a fixed-pool adaptation in which external retrieval is disabled.

### 作用

说明 AGR 的位置：它不是检索增强、不是普通修订、不是硬选择，而是在 fixed-pool 下进行 candidate-family evidence arbitration。

---

## Table 2：符号表

### 表名

**Table 2. Core notation used in AGR**

### 处理建议

保留原论文完整 Table 2。不要强行压缩。

### 作用

帮助读者理解 Method 中的公式和算法。

### 修改要求

只检查两点：

1. 正文没有再用到的符号可以删；
2. 符号解释不要太长，一行能解释清楚就不要写成段落。

---

## Table 3：数据集与 fixed-pool 设置表

### 表名

**Table 3. Fixed-pool datasets and operating conditions**

### 最终表格建议

| Dataset | n | k_r | k_e | Ans@4 | Stale rate | Conflict rate |
|---|---:|---:|---:|---:|---:|---:|
| HOH | 1024 | 4 | 2 | 0.847 | 0.992 | 0.992 |
| TempRAGEval | 1244 | 4 | 2 | 0.378 | 0.360 | 0.071 |
| TimeQA | 500 | 4 | 2 | 0.950 | 0.976 | 0.782 |
| ArchivalQA-derived | 500 | 4 | 2 | 0.990 | 0.480 | 0.264 |

### 正文解释

表后加一小段即可：

> HOH and TempRAGEval are the primary fixed-pool evidence-competition settings. TimeQA is used as a boundary setting because temporal constraints are often less explicit. ArchivalQA-derived is retained only as an appendix-level offline check.

### 作用

说明实验数据的 fixed-pool 条件和每个数据集的角色。

---

## Table 4：主结果表

### 表名

**Table 4. Main fixed-pool answer-selection results after parse repair**

### 数据来源

```text
fairness_repair/tables/Table4_parse_repaired.md
fairness_repair/metrics/main_results_parse_repaired.csv
```

### Markdown 展示版

| Method | HOH EM | HOH F1 | Temp EM | Temp F1 | TimeQA EM | TimeQA F1 | Macro EM | Macro F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| TP-FP RAG | 43.46 | 53.82 | 15.19 | 23.46 | 28.00 | 34.53 | 28.88 | 37.27 |
| Self-Refine* | 35.74 | 47.03 | 13.67 | 20.89 | 22.60 | 27.43 | 24.00 | 31.78 |
| RARR† | 13.38 | 32.53 | 7.15 | 18.07 | 12.40 | 23.84 | 10.98 | 24.81 |
| FP-CSR | 30.08 | 42.10 | 15.35 | 23.64 | 24.60 | 30.35 | 23.34 | 31.99 |
| AGR | 51.17 | 68.16 | 23.87 | 36.51 | 29.60 | 37.10 | **34.88** | **47.25** |

### LaTeX 美化建议

LaTeX 里不要重复写 `HOH EM`、`HOH F1`，建议用分组表头：

```latex
\begin{tabular}{lcccccccc}
\toprule
\multirow{2}{*}{Method} & \multicolumn{2}{c}{HOH} & \multicolumn{2}{c}{TempRAGEval} & \multicolumn{2}{c}{TimeQA} & \multicolumn{2}{c}{Macro} \\
\cmidrule(lr){2-3} \cmidrule(lr){4-5} \cmidrule(lr){6-7} \cmidrule(lr){8-9}
& EM & F1 & EM & F1 & EM & F1 & EM & F1 \\
\midrule
...
\bottomrule
\end{tabular}
```

### 表注

`*` denotes a fixed-pool adaptation of Self-Refine.  
`†` denotes a fixed-pool adaptation of RARR that disables external retrieval.

### 作用

这是主文最重要的结果表，用来证明 AGR 超过 strongest non-AGR baseline TP-FP RAG。

### 注意

FaithfulRAG-inspired 和 CRAG-inspired 不放主文 Table 4，放附录完整结果表。

---

## Table 5：AGR 相对 TP-FP 的提升与 repair-harm 表

### 表名

**Table 5. Dataset-wise improvement and repair-harm diagnostics of AGR over TP-FP RAG**

### 最终表格建议

| Dataset | TP-FP EM | AGR EM | EM gain | TP-FP F1 | AGR F1 | F1 gain | Repair | Harm | Net repair |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| HOH | 43.46 | 51.17 | +7.71 | 53.82 | 68.16 | +14.34 | 127 | 48 | +79 |
| TempRAGEval | 15.19 | 23.87 | +8.68 | 23.46 | 36.51 | +13.05 | 123 | 15 | +108 |
| TimeQA | 28.00 | 29.60 | +1.60 | 34.53 | 37.10 | +2.57 | 27 | 19 | +8 |

### 作用

说明 AGR 的提升不是平均数幻觉，而是 repair 多于 harm。

### 注意

数据集名不带样本数。样本数已经在 Table 3 中说明。

---

## Table 6：Prompt-visible feature exposure 表

### 表名

**Table 6. Prompt-visible features exposed to fixed-pool methods**

### 最终表格建议

| Method | Temporal instruction | Self feedback | Agreement check | Support and conflict facts | Candidate family | AGR score | Extra retrieval |
|---|---|---|---|---|---|---|---|
| TP-FP RAG | Yes | No | No | No | No | No | No |
| Self-Refine* | No | Yes | No | No | No | No | No |
| RARR† | No | Yes | Yes | No | No | No | No |
| FP-CSR | No | Yes | No | No | No | No | No |
| FP-TSR | Yes | Yes | No | No | No | No | No |
| FP-EASR | No | Yes | No | Yes | No | No | No |
| FaithfulRAG-inspired | No | Yes | No | Yes | No | No | No |
| CRAG-inspired | No | Yes | No | No | No | No | No |
| AGR | Yes | Yes | Yes | Yes | Yes | Yes | No |

### 作用

证明 baseline 没有看到 AGR-only signal，保证比较公平。

### 放置建议

如果主文篇幅紧张，这张表放 Appendix A。Section 4.2 用一句话引用即可。

---

## Table 7：Runtime and protocol overhead diagnostics

### 表名

**Table 7. Runtime and protocol overhead diagnostics**

### 最终表格建议

| Method | Extra retrieval | LLM calls per query | Answer-change rate | Mean input tokens | Mean latency |
|---|---:|---:|---:|---:|---:|
| TP-FP RAG | 0 | 1.00 (protocol count) | N/A | UNKNOWN | 0.1023 s |
| Self-Refine* | 0 | 2.00 | 13.66% | 867.20 | 0.4471 s |
| RARR† | 0 | 2.00 | 69.29% | 1012.15 | 1.3002 s |
| AGR | 0 | 1 + trigger (protocol count) | 32.95% | UNKNOWN | 0.1027 s |

### 作用

说明各方法在 fixed-pool protocol 下的开销结构。

### 正文说明

表后用一句话说明：

> Because 15 legacy runtime rows lack complete input-token or LLM-call records, this table is used as a protocol-overhead diagnostic rather than an exact deployment-latency benchmark.

The answer-change rate, mean input tokens, and mean latency are sample-weighted over all 2,768 queries in HOH, TempRAGEval, and TimeQA. `UNKNOWN` means that the legacy prediction artifacts did not record the field. TP-FP RAG and AGR call counts describe the protocol rather than a measured `llm_calls` log field.

### 注意

不要加 Notes 列。不要在表名或列名中使用斜杠。

---

# 三、主文图安排

## Figure 1：问题示意图

### 图名

**Figure 1. Post-retrieval evidence-value competition in a fixed evidence pool**

### 作用

解释问题本身：fixed pool 中 current、stale、relation-mismatched evidence 共存。

### 是否与表重复

不重复。它不是结果图。

---

## Figure 2：AGR 方法图

### 图名

**Figure 2. AGR workflow under a frozen evidence state**

### 作用

解释 AGR 的流程：fixed pool、candidate family、arbitration、soft revision signal、provenance。

### 是否与表重复

不重复。Table 1 是方法定位，Figure 2 是方法流程。

---

## Figure 3：F1 主结果图

### 图名

**Figure 3. Dataset-wise F1 comparison under the fixed-pool protocol**

### 数据来源

```text
fairness_repair/figures/Figure3_parse_repaired.pdf
fairness_repair/figures/Figure3_parse_repaired.png
```

### 应该呈现什么

只画核心方法：

- TP-FP RAG
- Self-Refine*
- RARR†
- AGR

三个数据集：

- HOH
- TempRAGEval
- TimeQA

### 作用

直观展示 AGR 在 HOH 和 TempRAGEval 上优势明显，TimeQA 上提升较小。

### 是否与 Table 4 重复

轻微重复，但可以保留。

区别：

- Table 4 给精确 EM/F1；
- Figure 3 只给 F1 趋势。

---

## Figure 4：net repair 图

### 图名

**Figure 4. Net repair of AGR over TP-FP RAG**

### 应该呈现什么

| Dataset | Net repair |
|---|---:|
| HOH | +79 |
| TempRAGEval | +108 |
| TimeQA | +8 |

### 作用

突出 AGR 是正净修复，而不是简单改变答案。

### 是否与 Table 5 重复

轻微重复，但可以保留。

区别：

- Table 5 给完整 repair、harm、net repair；
- Figure 4 只展示 net repair 趋势。

---

## 不建议新增的图

| 图 | 不建议原因 |
|---|---|
| Full baseline ranking figure | 会突出 appendix-only controls，看起来像 strawman |
| Runtime figure | runtime 记录不完整，容易被误读为精确部署效率 |
| Parse-failure figure | 附录表足够，不需要主文图 |

---

# 四、附录安排

## Appendix A：Baseline feature exposure and naming boundary

### 内容

- 完整 Table 6；
- Self-Refine* 和 RARR† 的表注；
- FaithfulRAG-inspired 和 CRAG-inspired 为什么只放附录；
- 所有 baseline 未看到 AGR-only signal 的说明。

### 作用

防止审稿人质疑 baseline 不公平或命名过度。

---

## Appendix B：Full parse-repaired results

### 数据来源

```text
fairness_repair/metrics/main_results_parse_repaired.csv
```

### 内容

完整 27 行结果表。

### 必须包含

FaithfulRAG-inspired 修复后的结果：

| Dataset | EM | F1 |
|---|---:|---:|
| HOH | 9.96 | 17.25 |
| TempRAGEval | 3.14 | 7.91 |
| TimeQA | 7.00 | 10.73 |
| Macro | 6.70 | 11.96 |

### 作用

让主文干净，同时保留完整结果。

---

## Appendix C：Paired bootstrap confidence intervals

### 数据来源

```text
fairness_repair/ci/paired_bootstrap_all_parse_repaired.csv
```

### 内容

108 行 paired bootstrap CI。

### 作用

支撑统计可靠性。

---

## Appendix D：Parse-failure and fairness repair audit

### 内容

#### RARR parse failure

| Dataset | Parse failure rate | Decision |
|---|---:|---|
| HOH | 0.78% | No rerun |
| TempRAGEval | 3.86% | No rerun |
| TimeQA | 1.20% | No rerun |

#### FaithfulRAG-inspired parse repair

| Dataset | Raw failure rate | Repaired failure rate | Decision |
|---|---:|---:|---|
| HOH | 2.44% | 0% | Repaired |
| TempRAGEval | 2.73% | 0.40% | Repaired |
| TimeQA | 10.40% | 0% | Repaired |

### 作用

说明 FaithfulRAG-inspired 的低性能不是 parse failure 造成的主要假象。

---

## Appendix E：Runtime diagnostics

### 内容

完整 runtime 表。

### 必须说明

15 行旧 runtime 记录缺少 input-token 或 LLM-call 字段。

### 作用

支撑 protocol overhead 讨论，但不支撑精确部署效率结论。

---

## Appendix F：Qualitative cases

### 内容

主文 2 个案例，附录 5 个案例。

附录案例建议：

1. AGR harm case；
2. candidate extraction failure；
3. signal override；
4. Self-Refine 或 RARR over-revision；
5. TimeQA boundary case。

### 作用

解释方法为什么有效，也解释边界在哪里。

---

## Appendix G：Deterministic heuristics and diagnostic controls

### 内容

- BM25-top cue；
- Majority family；
- Latest timestamp；
- Temporal-only；
- HCR；
- FaithfulRAG-inspired；
- CRAG-inspired。

### 作用

证明 AGR 不等于简单时间戳规则、hard selection 或普通 evidence-aware revision。

---

## Appendix H：ArchivalQA-derived offline check

### 内容

只放现有离线结果：

- TP-FP RAG；
- AGR；
- FP-CSR。

### 作用

辅助说明 archival fixed-pool condition，不作为主结论。

---

# 五、最终推荐总安排

| 类型 | 编号 | 名称 | 放置位置 | 核心作用 |
|---|---|---|---|---|
| 表 | Table 1 | Method positioning | 主文 | 方法定位 |
| 表 | Table 2 | Notation | 主文 | 符号说明 |
| 表 | Table 3 | Dataset setting | 主文 | 数据条件 |
| 表 | Table 4 | Main results | 主文 | 核心结果 |
| 表 | Table 5 | Improvement and repair-harm | 主文 | 解释修复收益 |
| 表 | Table 6 | Feature exposure | 主文或附录 | 公平性说明 |
| 表 | Table 7 | Runtime diagnostics | 主文或附录 | 开销诊断 |
| 图 | Figure 1 | Failure mode | 主文 | 问题说明 |
| 图 | Figure 2 | AGR workflow | 主文 | 方法说明 |
| 图 | Figure 3 | F1 comparison | 主文 | 性能趋势 |
| 图 | Figure 4 | Net repair | 主文 | 修复趋势 |
| 附录 | Appendix A | Feature exposure and naming | 附录 | baseline 公平性 |
| 附录 | Appendix B | Full results | 附录 | 完整 27 行结果 |
| 附录 | Appendix C | Bootstrap CI | 附录 | 统计可靠性 |
| 附录 | Appendix D | Parse repair audit | 附录 | 公平性修复 |
| 附录 | Appendix E | Runtime diagnostics | 附录 | 开销细节 |
| 附录 | Appendix F | Cases | 附录 | 案例证据 |
| 附录 | Appendix G | Diagnostic controls | 附录 | 启发式与控制实验 |
| 附录 | Appendix H | ArchivalQA check | 附录 | 补充验证 |

---

# 六、最简定稿原则

1. 主文表格不要超过 7 张。  
2. 主文图不要超过 4 张。  
3. Table 4 使用 parse-repaired 版本。  
4. Figure 3 使用 parse-repaired 版本。  
5. FaithfulRAG-inspired 和 CRAG-inspired 不进主文主结果表。  
6. Table 3 删除 Note 列，数据集角色放正文解释。  
7. Table 6 删除 Main or Appendix 列。  
8. Table 7 删除 Notes 列。  
9. 全文慎用斜杠，能用 and 的地方用 and。  
10. 不再新增实验图，防止论文显得散。
