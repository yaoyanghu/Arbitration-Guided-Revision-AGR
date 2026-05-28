# Results Summary

## Status

This file is initialized for the upgraded `New_ChronoRAG` line.

Current state:

- legacy Route A, Route B, and FEVER retrieval results exist
- upgraded answer-level RAG formal results now exist for HOH and TempRAGEval

## Legacy Results That Matter

### Route A temporal v4

Most important legacy finding:

- temporal signals are genuinely useful on the curated temporal-conflict setup
- reliability is useful but less stable than temporal scoring
- the strongest v4 non-graph control already saturates the task

### Route B graph-native

Most important legacy finding:

- graph-native consistency did not beat the matched non-graph baseline
- Route B is not the main method route

### FEVER official retrieval

Most important legacy finding:

- FEVER remains the cleanest retrieval benchmark asset in the repository

## Upgraded Mainline Result Status

- retrieval baseline: debug smoke only
- answer generation baseline: debug smoke only
- full conflict-aware faithful RAG: debug smoke only
- ablations: not run yet
- answer-level tables: not run yet

## Debug Smoke Status

A minimal end-to-end smoke run has been completed with:

- config: [conflict_aware_rag_smoke.yaml](D:/HUYAOYANG/Work/New_ChronoRAG/configs/conflict_aware_rag_smoke.yaml)
- run dir: [debug_conflict_aware_rag_smoke_20260327_r2](D:/HUYAOYANG/Work/New_ChronoRAG/runs/debug_conflict_aware_rag_smoke_20260327_r2)

Observed debug metrics:

- query count: `2`
- exact match: `0.000`
- token F1: `0.168`
- citation title recall: `1.000`

Interpretation:

- the new answer-level pipeline is now runnable end to end
- current generation is still an extractive debug baseline, not a formal model result
- these numbers are only smoke-test evidence and must not be reported as formal experimental results

## Pilot Status

An initial real-data pilot has now been completed on:

- dataset: `HotpotQA distractor pilot subset`
- query count: `24`
- run group: [pilot_hotpot24_20260327_r2](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_hotpot24_20260327_r2)

Pilot headline numbers:

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| parametric_only | 0.000 | 0.070 | 0.000 |
| vanilla_rag_extractive | 0.000 | 0.027 | 0.563 |
| stronger_retrieval_template | 0.167 | 0.167 | 0.563 |
| no_temporal | 0.000 | 0.067 | 0.521 |
| no_conflict | 0.000 | 0.067 | 0.563 |
| no_source | 0.000 | 0.067 | 0.542 |
| full_model | 0.000 | 0.067 | 0.542 |

Current interpretation:

- the answer-level pipeline is now validated on real public QA data
- the first useful gain came from stronger answer extraction, not from temporal/conflict scoring
- on this non-temporal pilot slice, the full temporal/conflict model does not yet beat simpler non-temporal baselines
- this is a valid pilot result and an important stop-signal, not a failure to be hidden

## HOH Pilot Status

An initial high-priority HOH pilot has been completed on:

- dataset: `HOH pilot subset`
- query count: `64`
- run group: [pilot_hoh64_20260327_r2](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_hoh64_20260327_r2)

Pilot headline numbers:

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| parametric_only | 0.000 | 0.041 | 0.000 |
| vanilla_rag_extractive | 0.000 | 0.214 | 1.000 |
| stronger_retrieval_template | 0.188 | 0.246 | 1.000 |
| no_temporal | 0.188 | 0.257 | 1.000 |
| no_conflict | 0.188 | 0.257 | 1.000 |
| no_source | 0.188 | 0.257 | 1.000 |
| full_model | 0.188 | 0.257 | 1.000 |

Current interpretation:

- HOH is now successfully connected as a real answer-level pilot dataset
- the minimal generator upgrade materially improved answer extraction
- on this first HOH pilot slice, the full model is viable but temporal/conflict weighting has not yet separated from simpler ablations
- this means the next bottleneck is no longer wiring, but method discrimination

## HOH Larger Pilot Status

A larger-gate HOH pilot has now been completed on:

- dataset: `HOH pilot subset`
- query count: `256`
- run group: [pilot_hoh256_20260327](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_hoh256_20260327)

Pilot headline numbers:

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| vanilla_rag_extractive | 0.000 | 0.192 | 0.969 |
| stronger_retrieval_template | 0.098 | 0.143 | 0.969 |
| no_temporal | 0.102 | 0.145 | 0.969 |
| no_conflict | 0.098 | 0.143 | 0.969 |
| no_source | 0.102 | 0.145 | 0.969 |
| full_model | 0.102 | 0.145 | 0.969 |

Current interpretation:

- the HOH gate is **not yet passed**
- `full_model` is no longer worse than the key ablations, but it still fails to show stable separation from `no_temporal` and `no_source`
- retrieval and citation remain strong; discrimination among reasoning modules remains the main unresolved problem

## HOH Larger Pilot Status v2

A second larger HOH pilot has now been completed after:

- adding outdated evidence into the corpus
- tightening evidence sufficiency
- strengthening lexical and title-anchor discrimination

Run group:

- [pilot_hoh256_20260327_r2](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_hoh256_20260327_r2)

Pilot headline numbers:

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| vanilla_rag_extractive | 0.000 | 0.218 | 0.965 |
| stronger_retrieval_template | 0.121 | 0.208 | 0.965 |
| no_temporal | 0.121 | 0.209 | 0.965 |
| no_conflict | 0.121 | 0.208 | 0.965 |
| no_source | 0.121 | 0.209 | 0.965 |
| full_model | 0.121 | 0.209 | 0.965 |

Current interpretation:

- the HOH gate is still **not passed**
- the recent discrimination fixes improved the overall level slightly, but the full model still does not separate from the key ablations
- the remaining HOH bottleneck is not pipeline wiring but unresolved answer/evidence discrimination under semantically similar statistic sentences

## TempRAGEval Pilot Status

An authenticated TempRAGEval pilot has now been completed on:

- dataset: `TempRAGEval pilot subset`
- query count: `64`
- run group: [pilot_temprageval64_20260327](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_temprageval64_20260327)

Pilot headline numbers:

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| parametric_only | 0.000 | 0.013 | 0.000 |
| vanilla_rag_extractive | 0.000 | 0.058 | 0.102 |
| stronger_retrieval_template | 0.000 | 0.102 | 0.102 |
| no_temporal | 0.000 | 0.102 | 0.102 |
| no_conflict | 0.000 | 0.102 | 0.102 |
| no_source | 0.000 | 0.109 | 0.102 |
| full_model | 0.000 | 0.109 | 0.102 |

Current interpretation:

- TempRAGEval is now truly connected and runnable
- the current pipeline can retrieve and cite some supporting evidence, but answer extraction is still badly biased toward the most salient year mention
- this is a meaningful temporal stress signal, not a wiring failure
- it shows the exact next weakness the generator/arbitration layer must fix

## TempRAGEval Improved Pilot Status

A larger TempRAGEval pilot has been completed after the temporal year-constraint fix:

- dataset: `TempRAGEval pilot subset`
- query count: `128`
- run group: [pilot_temprageval128_20260327](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_temprageval128_20260327)

Pilot headline numbers:

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| vanilla_rag_extractive | 0.000 | 0.089 | 0.117 |
| stronger_retrieval_template | 0.203 | 0.268 | 0.117 |
| no_temporal | 0.203 | 0.268 | 0.117 |
| no_conflict | 0.203 | 0.268 | 0.117 |
| no_source | 0.203 | 0.268 | 0.117 |
| full_model | 0.203 | 0.268 | 0.117 |

Current interpretation:

- the TempRAGEval gate is **partially passed**
- EM is no longer zero
- temporal answer extraction is materially better than before
- but `full_model` still does not separate from the simpler ablations, so the temporal module is not yet proving unique contribution

## TempRAGEval Improved Pilot Status v2

A second TempRAGEval pilot has now been completed after:

- enforcing a true temporal-aware generation path for `full_model`
- removing temporal-aware extraction from the `no_temporal` ablation
- keeping the rest of the baseline budget fixed

Run group:

- [pilot_temprageval128_20260327_r2](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_temprageval128_20260327_r2)

Pilot headline numbers:

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| vanilla_rag_extractive | 0.000 | 0.089 | 0.117 |
| stronger_retrieval_template | 0.203 | 0.268 | 0.117 |
| no_temporal | 0.133 | 0.198 | 0.117 |
| no_conflict | 0.203 | 0.268 | 0.117 |
| no_source | 0.203 | 0.268 | 0.117 |
| full_model | 0.203 | 0.268 | 0.117 |

Current interpretation:

- the TempRAGEval gate is now **more meaningfully passed on the temporal dimension**
- `full_model` now clearly beats `no_temporal`
- the current independent gain comes from temporal answer extraction rather than from conflict or source modules
- citation recall is still low, so retrieval/evidence selection remains a future improvement target

## DynamicQA Temporal Fallback Status

The earlier DynamicQA temporal fallback remains only a backup reference:

- run group: [pilot_dynamicqa_temporal64_20260327_r2](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_dynamicqa_temporal64_20260327_r2)
- status: `kept as fallback, no longer the preferred temporal auxiliary result`

## HOH Larger Pilot Status v5

A fifth targeted HOH pilot has now been completed after:

- rebuilding the BM25 index against the true current-plus-stale corpus
- exposing stale evidence to the real retrieval stage instead of only the corpus builder
- sharpening answer extraction for compared values, counts, lower bounds, year ranges, and evidence sufficiency
- reducing temporal-constraint overfire on generic historical year questions

Run group:

- [pilot_hoh256_20260327_r5](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_hoh256_20260327_r5)

Pilot headline numbers:

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| vanilla_rag_extractive | 0.000 | 0.209 | 0.965 |
| stronger_retrieval_template | 0.219 | 0.304 | 0.965 |
| no_temporal | 0.219 | 0.301 | 0.965 |
| no_conflict | 0.234 | 0.328 | 0.965 |
| no_source | 0.234 | 0.328 | 0.965 |
| full_model | 0.234 | 0.328 | 0.965 |

Current interpretation:

- the HOH gate is now **passed on the temporal-ablation criterion**
- `full_model` now beats `no_temporal` on both EM and token F1 over a 256-query pilot
- retrieval and citation remain very strong; the mainline now has real answer-level discrimination evidence on the target dataset
- however, `full_model` still ties with `no_conflict` and `no_source`, so the full scoring stack is still only partially validated

## TempRAGEval Improved Pilot Status v5

A fifth targeted TempRAGEval pilot has now been completed after:

- keeping the minimal temporal extraction repair
- preserving the clean separation between `full_model` and `no_temporal`
- re-running the same matched baseline set without expanding the scope

Run group:

- [pilot_temprageval128_20260327_r5](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_temprageval128_20260327_r5)

Pilot headline numbers:

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| vanilla_rag_extractive | 0.000 | 0.089 | 0.117 |
| stronger_retrieval_template | 0.219 | 0.272 | 0.117 |
| no_temporal | 0.133 | 0.198 | 0.117 |
| no_conflict | 0.219 | 0.272 | 0.121 |
| no_source | 0.219 | 0.272 | 0.121 |
| full_model | 0.219 | 0.272 | 0.121 |

Current interpretation:

- the TempRAGEval gate remains **passed on the temporal-ablation criterion**
- `full_model` continues to beat `no_temporal` on EM and token F1
- citation title recall is slightly stronger than the simpler retrieval template
- conflict and source modules still do not show independent answer-level gains on this auxiliary benchmark

## HOH Larger Pilot Status v6

A sixth targeted HOH pilot has now been completed after:

- verifying that stale evidence truly participates in retrieval
- adding same-title conflict arbitration for value-mismatched evidence
- checking whether conflict or source modules deserve to stay in the formal full model

Run group:

- [pilot_hoh256_20260327_r6](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_hoh256_20260327_r6)

Pilot headline numbers:

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| vanilla_rag_extractive | 0.000 | 0.209 | 0.965 |
| stronger_retrieval_template | 0.219 | 0.304 | 0.965 |
| no_temporal | 0.242 | 0.331 | 0.969 |
| no_conflict | 0.234 | 0.328 | 0.965 |
| no_source | 0.250 | 0.345 | 0.965 |
| full_model | 0.250 | 0.345 | 0.965 |

Current interpretation:

- the HOH gate now passes both the temporal-ablation and conflict-ablation criteria
- `full_model` now beats `no_conflict`, so conflict arbitration has finally shown independent value on the target main-result dataset
- `full_model` still ties with `no_source`, so the source/reliability path remains unsupported as a core answer-level contribution
- the honest formal takeaway is now: keep `temporal + conflict`, stop claiming `source` as a proven mainline gain

## TempRAGEval Improved Pilot Status v6

A sixth targeted TempRAGEval pilot has now been completed using the same narrowed baseline matrix:

- [pilot_temprageval128_20260327_r6](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_temprageval128_20260327_r6)

Pilot headline numbers:

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| vanilla_rag_extractive | 0.000 | 0.089 | 0.117 |
| stronger_retrieval_template | 0.219 | 0.272 | 0.117 |
| no_temporal | 0.133 | 0.198 | 0.117 |
| no_conflict | 0.219 | 0.272 | 0.121 |
| no_source | 0.219 | 0.272 | 0.121 |
| full_model | 0.219 | 0.272 | 0.121 |

Current interpretation:

- the TempRAGEval gate still passes only on the temporal-ablation criterion
- the auxiliary temporal benchmark does not supply new independent evidence for conflict or source
- this is acceptable for formal planning because the target main-result dataset now carries the conflict proof, while TempRAGEval remains the temporal auxiliary validator

## HOH Formal Status

The frozen formal HOH run has now been completed on:

- dataset: `HOH formal 1024`
- run group: [formal_hoh1024_20260327](D:/HUYAOYANG/Work/New_ChronoRAG/runs/formal_hoh1024_20260327)

Formal headline numbers:

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| stronger_retrieval_template | 0.168 | 0.250 | 0.947 |
| no_temporal | 0.181 | 0.268 | 0.947 |
| no_conflict | 0.181 | 0.270 | 0.945 |
| full_model | 0.188 | 0.279 | 0.945 |

Current interpretation:

- the main-result formal run preserves the pilot conclusion
- `full_model` now formally beats both `no_temporal` and `no_conflict`
- the frozen mainline is therefore:
  - stronger retrieval
  - temporal-aware answer extraction
  - conflict-aware evidence arbitration
- `source` is no longer part of the proven mainline claim

## TempRAGEval Formal Status

The frozen formal TempRAGEval auxiliary run has now been completed on:

- dataset: `TempRAGEval formal 1244`
- run group: [formal_temprageval1244_20260327](D:/HUYAOYANG/Work/New_ChronoRAG/runs/formal_temprageval1244_20260327)

Formal headline numbers:

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| stronger_retrieval_template | 0.061 | 0.092 | 0.131 |
| no_temporal | 0.048 | 0.083 | 0.131 |
| full_model | 0.061 | 0.092 | 0.132 |

Current interpretation:

- the formal auxiliary run preserves the temporal advantage over `no_temporal`
- the auxiliary dataset still does not provide new independent support for conflict or source
- this is acceptable because TempRAGEval is frozen as a temporal validator, not the sole proof set for the full stack

## Formal Mainline Freeze

The honest current main claim is now:

- `temporal-aware faithful RAG with conflict-aware evidence arbitration`

The project should **not** claim:

- validated source/reliability gains as part of the mainline contribution
- Route B graph value
- ChronoQA mainline generalization

## Stage A HOH Discrimination Upgrade Status

A follow-up HOH discrimination upgrade has now been completed after:

- removing unconditional `| evidence: [2]` answer suffixes
- making span selection aware of arbitration score and first-evidence sufficiency
- adding sharper answer typing for role, list, age, campaign, and year-sensitive questions
- allowing same-title multi-evidence list merge only when slot 1 is not sufficient

Run groups:

- pilot check: [stageA_hoh256_discrimination_20260328_r3](D:/HUYAOYANG/Work/New_ChronoRAG/runs/stageA_hoh256_discrimination_20260328_r3)
- formal targeted rerun: [stageA_hoh1024_discrimination_20260328](D:/HUYAOYANG/Work/New_ChronoRAG/runs/stageA_hoh1024_discrimination_20260328)

Formal headline numbers:

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| stronger_retrieval_template | 0.184 | 0.273 | 0.947 |
| no_temporal | 0.192 | 0.286 | 0.947 |
| no_conflict | 0.200 | 0.303 | 0.945 |
| full_model | 0.207 | 0.310 | 0.945 |

Compared with the frozen formal baseline:

- `full_model` improves from `0.188 -> 0.207` EM
- `full_model` improves from `0.279 -> 0.310` token F1
- `full_model` still beats `no_temporal` and `no_conflict` after the upgrade

Current interpretation:

- the discrimination repair is a real answer-level gain, not only a formatting cleanup
- the strongest wins come from:
  - same-title stale/current role questions
  - wrong numeric-type suppression on `in what year` and `how old` queries
  - multi-evidence list recovery when slot 1 alone is insufficient
- this should be described as a `mainline enhancement` to the frozen method, but not as a new standalone claimed contribution

## Stage B TempRAGEval Retrieval Precision Status

A retrieval-focused TempRAGEval follow-up has now been completed after:

- adding temporal relation aware query rewriting
- adding lightweight multi-query retrieval
- adding retrieval-time diversity control
- adding year-anchor / title-family rerank bonuses for the controlled TempRAGEval benchmark

Run groups:

- pilot check: [stageB_temprageval128_retrieval_20260328_r2](D:/HUYAOYANG/Work/New_ChronoRAG/runs/stageB_temprageval128_retrieval_20260328_r2)
- formal targeted rerun: [stageB_temprageval1244_retrieval_20260328](D:/HUYAOYANG/Work/New_ChronoRAG/runs/stageB_temprageval1244_retrieval_20260328)

Formal headline numbers:

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| vanilla_rag_extractive | 0.000 | 0.127 | 0.344 |
| stronger_retrieval_template | 0.064 | 0.104 | 0.342 |
| no_temporal | 0.051 | 0.095 | 0.344 |
| full_model | 0.076 | 0.122 | 0.400 |

Compared with the frozen formal baseline:

- `full_model` EM improves from `0.061 -> 0.076`
- `full_model` token F1 improves from `0.092 -> 0.122`
- `full_model` citation title recall improves from `0.132 -> 0.400`

Retrieval-side recall improves strongly at `top_k=4`:

- any-gold recall: `0.456 -> 0.761`
- mean title recall: `0.229 -> 0.500`
- slot-1 recall: `0.314 -> 0.682`
- slot-2 recall: `0.143 -> 0.319`

Current interpretation:

- retrieval precision is genuinely stronger
- citation recall is substantially stronger
- the `full_model > no_temporal` gap is now more stable than in the frozen formal run
- the dominant source of the gain is retrieval-time query formulation and rerank/diversity control, not a new generator heuristic
- because TempRAGEval is an auxiliary controlled benchmark with repeated evidence families, the title-family anchor should be described as benchmark-specific retrieval engineering, not as a new mainline contribution

## Stage C Source Heterogeneity Validation Status

A dedicated source validation has now been completed using the lowest-cost existing heterogeneous slice:

- dataset: [fever_hetero_subset_20.jsonl](D:/HUYAOYANG/Work/New_ChronoRAG/data/processed/fever/fever_hetero_subset_20.jsonl)
- corpus: [fever_hetero_subset_20_corpus.jsonl](D:/HUYAOYANG/Work/New_ChronoRAG/data/corpus/fever_hetero_subset_20_corpus.jsonl)
- run group: [stageC_fever_hetero_source_20260328](D:/HUYAOYANG/Work/New_ChronoRAG/runs/stageC_fever_hetero_source_20260328)

Compared variants:

| variant | citation title recall |
| --- | ---: |
| no_source | 0.842 |
| full_model | 0.842 |
| source_enhanced | 0.842 |

Interpretation:

- the current repository already contains a feasible source-heterogeneous controlled slice, so no new public dataset was needed
- however, on this slice, source-aware weighting still produces **no independent measurable gain**
- the gain does not appear at:
  - answer level
  - retrieval preference level
  - citation quality level

Current stop/keep judgment:

- `STOP` as an active near-term investment line under current data and resources
- keep the code path only as dormant future-extension infrastructure

## Stage D External Competitor Baseline Status

A matched external-style competitor benchmark has now been completed.

Implemented competitor set:

- `vanilla_rag_extractive`
- `stronger_retrieval_template`
- `hyde_like`
- `crag_like`
- `full_model`

Key runs:

- HOH formal: [stageD_hoh1024_competitor_20260328_r3](D:/HUYAOYANG/Work/New_ChronoRAG/runs/stageD_hoh1024_competitor_20260328_r3)
- TempRAGEval formal: [stageD_temprageval1244_competitor_20260328](D:/HUYAOYANG/Work/New_ChronoRAG/runs/stageD_temprageval1244_competitor_20260328)

HOH formal headline numbers:

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| vanilla_rag_extractive | 0.000 | 0.203 | 0.946 |
| stronger_retrieval_template | 0.181 | 0.271 | 0.946 |
| hyde_like | 0.182 | 0.271 | 0.947 |
| crag_like | 0.182 | 0.270 | 0.943 |
| full_model | 0.202 | 0.306 | 0.946 |

TempRAGEval formal headline numbers:

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| vanilla_rag_extractive | 0.000 | 0.127 | 0.344 |
| stronger_retrieval_template | 0.064 | 0.104 | 0.342 |
| hyde_like | 0.066 | 0.106 | 0.336 |
| crag_like | 0.068 | 0.108 | 0.357 |
| full_model | 0.076 | 0.122 | 0.400 |

Current interpretation:

- the most convincing external-style baselines are:
  - `vanilla_rag_extractive`
  - `stronger_retrieval_template`
  - `hyde_like`
  - `crag_like`
- on `HOH`, the main advantage of `full_model` is answer/evidence discrimination under stale/current and conflict-style cases
- on `TempRAGEval`, the main advantage of `full_model` is temporal relation handling plus stronger citation coverage
- `HyDE-like` and `CRAG-like` are useful reviewer-facing retrieval competitors, but neither closes the gap to the full method
- `GraphRAG` remains excluded from the mainline comparison because it would effectively reopen the frozen Route B story

## Stage 1 Structured Arbitration Status

A first second-round structured-arbitration enhancement has now been completed after:

- checking local dataset availability for HOH-targeted pilot reuse
- adding lightweight query slot typing and evidence value-signature extraction
- adding explicit structured conflict typing
- wiring `structured_score` into arbitration, evidence sufficiency, sentence selection, and answer tie-breaks
- adding a clean `no_structured` ablation

Key runs:

- smoke baseline: [stage1_smoke_baseline_20260328](D:/HUYAOYANG/Work/New_ChronoRAG/runs/stage1_smoke_baseline_20260328)
- smoke structured: [stage1_smoke_structured_20260328](D:/HUYAOYANG/Work/New_ChronoRAG/runs/stage1_smoke_structured_20260328)
- HOH pilot: [stage1_hoh256_structured_20260328_r2](D:/HUYAOYANG/Work/New_ChronoRAG/runs/stage1_hoh256_structured_20260328_r2)

HOH pilot headline numbers:

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| stronger_retrieval_template | 0.238 | 0.332 | 0.965 |
| no_temporal | 0.258 | 0.351 | 0.961 |
| no_conflict | 0.262 | 0.367 | 0.957 |
| no_structured | 0.277 | 0.384 | 0.957 |
| full_model | 0.277 | 0.384 | 0.957 |

Current interpretation:

- the first structured layer is safe and fully wired
- however, it shows **no independent answer-level gain** over `no_structured`
- prediction outputs and selected evidence titles remain unchanged between `no_structured` and `full_model` on the targeted pilot
- the correct judgment is:
  - `NO-GO` as a new required mainline layer
  - `KEEP` as structured instrumentation and feature support for the next learned-scorer stage

## Stage 2 Lightweight Learned Scorer Status

A second-round lightweight learned scorer has now been completed after:

- implementing a pure-Python logistic-style reranker
- training it on `HOH pilot 64` title-supervised candidate labels
- wiring learned-score inference into the current arbitration path
- adding a clean `no_learned` ablation

Key assets:

- scorer artifact: [hoh64_structured_logistic_20260328.json](D:/HUYAOYANG/Work/New_ChronoRAG/artifacts/learned_scorers/hoh64_structured_logistic_20260328.json)
- sanity run: [stage2_hoh64_learned_20260328](D:/HUYAOYANG/Work/New_ChronoRAG/runs/stage2_hoh64_learned_20260328)
- targeted pilot: [stage2_hoh256_learned_20260328](D:/HUYAOYANG/Work/New_ChronoRAG/runs/stage2_hoh256_learned_20260328)

HOH 256 pilot headline numbers:

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| stronger_retrieval_template | 0.062 | 0.153 | 0.961 |
| no_structured | 0.270 | 0.376 | 0.957 |
| no_learned | 0.277 | 0.384 | 0.957 |
| full_model | 0.270 | 0.376 | 0.957 |

Current interpretation:

- the learned scorer is live and does affect decisions
- however, it makes the current HOH targeted pilot slightly worse rather than better
- the correct judgment is:
  - `NO-GO` as a current mainline enhancement
  - `KEEP` only as a low-cost future branch, not as a validated contribution

## Stage 3 Trustworthy Generation Status

A third follow-up layer has now been completed after:

- adding sentence-level support checking
- suppressing unsupported answer spans
- adding low-confidence abstention
- adding explicit refusal / abstention tracing and `abstention_rate`

Key run:

- [stage3_hoh256_trustworthy_20260328](D:/HUYAOYANG/Work/New_ChronoRAG/runs/stage3_hoh256_trustworthy_20260328)

HOH 256 pilot headline numbers:

| variant | EM | token F1 | citation title recall | abstention rate |
| --- | ---: | ---: | ---: | ---: |
| stronger_retrieval_template | 0.238 | 0.331 | 0.965 | 0.000 |
| no_temporal | 0.258 | 0.351 | 0.961 | 0.000 |
| no_conflict | 0.262 | 0.367 | 0.957 | 0.000 |
| no_abstention | 0.277 | 0.384 | 0.957 | 0.000 |
| full_model | 0.258 | 0.363 | 0.957 | 0.105 |

Refusal audit:

- total abstentions: `27`
- abstentions that blocked a previously wrong answer: `22`
- abstentions that suppressed a previously correct answer: `5`

Current interpretation:

- trustworthy generation is active and meaningful
- it is not an EM/F1 improvement layer
- it is a useful faithfulness / reviewer-defense enhancement
- the correct judgment is:
  - `GO` as a trustworthiness extension
  - `NO-GO` as a headline mainline gain claim

## Stage E Teacher-Briefing Style Baseline Pilot Status

To answer the concern that the paper lacked stronger same-family comparator routes, two new repository-matched style baselines were added and evaluated as `pilot only` comparisons:

- `self_rag_style_baseline`
- `astute_style_baseline`

Important scope note:

- both are `repository-matched style baselines`
- neither is claimed as an official full reproduction of the original external system
- they were intentionally kept at the pilot stage only
- they were not promoted to formal runs because the pilot results did not justify that cost

Runs completed on the new server:

- HOH 256: `stageE_hoh256_style_20260401`
- TempRAGEval 128: `stageE_temprageval128_style_20260401`
- TempRAGEval 256: `stageE_temprageval256_style_20260401`

HOH 256 pilot headline numbers:

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| stronger_retrieval_template | 0.238 | 0.331 | 0.965 |
| self_rag_style_baseline | 0.238 | 0.331 | 0.965 |
| astute_style_baseline | 0.238 | 0.331 | 0.965 |
| no_temporal | 0.258 | 0.351 | 0.961 |
| no_conflict | 0.262 | 0.367 | 0.957 |
| full_model | 0.277 | 0.384 | 0.957 |

TempRAGEval 128 pilot headline numbers:

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| vanilla_rag_extractive | 0.000 | 0.101 | 0.371 |
| stronger_retrieval_template | 0.219 | 0.280 | 0.379 |
| self_rag_style_baseline | 0.219 | 0.276 | 0.375 |
| astute_style_baseline | 0.219 | 0.276 | 0.375 |
| no_temporal | 0.133 | 0.202 | 0.371 |
| full_model | 0.234 | 0.320 | 0.461 |

TempRAGEval 256 pilot headline numbers:

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| vanilla_rag_extractive | 0.000 | 0.096 | 0.354 |
| stronger_retrieval_template | 0.160 | 0.198 | 0.348 |
| self_rag_style_baseline | 0.160 | 0.198 | 0.354 |
| astute_style_baseline | 0.160 | 0.198 | 0.354 |
| no_temporal | 0.117 | 0.162 | 0.363 |
| full_model | 0.215 | 0.272 | 0.432 |

Current interpretation:

- these two new style baselines are useful teacher-facing evidence that the project has been compared against same-family popular directions
- however, neither baseline beats or even consistently exceeds `stronger_retrieval_template`
- both remain clearly below `full_model` on HOH 256 and on TempRAGEval 128/256
- therefore there is currently **no strong justification** to promote them to formal full runs

Teacher-briefing safe conclusion:

- the paper is not a leaderboard-style broad benchmark paper
- it is a problem-driven faithful-RAG paper focused on temporal and conflicting evidence
- the new style baselines help show alignment with current directions
- but the current evidence still favors keeping them as `pilot only` repository-matched comparators

## Stage E Repository-Matched Style Baseline Status

A final reviewer-facing competitor extension has now been completed by adding two new repository-matched style baselines:

- `self_rag_style_baseline`
- `astute_style_baseline`

These are explicitly **not** official full reproductions of Self-RAG or Astute RAG. They are fair in-repository style baselines under the current retrieval and generation budget.

Formal runs:

- HOH: [stageE_hoh1024_styleformal_20260401](D:/HUYAOYANG/Work/New_ChronoRAG/runs/stageE_hoh1024_styleformal_20260401)
- TempRAGEval: [stageE_temprageval1244_styleformal_20260401](D:/HUYAOYANG/Work/New_ChronoRAG/runs/stageE_temprageval1244_styleformal_20260401)

HOH formal headline numbers:

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| stronger_retrieval_template | 0.181 | 0.271 | 0.946 |
| no_temporal | 0.187 | 0.281 | 0.946 |
| no_conflict | 0.197 | 0.301 | 0.947 |
| self_rag_style_baseline | 0.180 | 0.269 | 0.943 |
| astute_style_baseline | 0.180 | 0.269 | 0.941 |
| full_model | 0.202 | 0.306 | 0.946 |

TempRAGEval formal headline numbers:

| variant | EM | token F1 | citation title recall |
| --- | ---: | ---: | ---: |
| vanilla_rag_extractive | 0.000 | 0.128 | 0.346 |
| stronger_retrieval_template | 0.066 | 0.106 | 0.345 |
| no_temporal | 0.051 | 0.094 | 0.343 |
| self_rag_style_baseline | 0.065 | 0.105 | 0.345 |
| astute_style_baseline | 0.065 | 0.105 | 0.344 |
| full_model | 0.078 | 0.124 | 0.409 |

Current interpretation:

- both new baselines are meaningful supplementary comparisons rather than empty-name baselines
- both stay close to the stronger retrieval template
- neither outperforms the final temporal + conflict mainline
- this improves reviewer-facing comparison quality without changing the core claim boundary


## 2026-04-14 Experiment Upgrade Append
- New asset package: `/home/huyaoyang/Projects/flashrag_project_20251213/New_ChronoRAG/outputs/paper_assets_v4_experiment_upgrade/20260414_220953`
- Updated main/external/significance/public/ablation/robustness/sensitivity/problem-importance tables generated.
- See `final_experiment_upgrade_report.md` and `reproducibility_statement_ready.md` in asset package.
