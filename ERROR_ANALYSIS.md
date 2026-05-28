# Error Analysis

## Status

The upgraded answer-level error analysis has not been generated yet.

## What Must Be Included Later

- success cases
- failure cases
- temporal-conflict resolution successes
- temporal-conflict resolution failures
- attribution successes
- attribution failures
- source-sensitivity analysis

## Legacy Takeaways

From historical Route A and Route B evidence:

- mixed ambiguous cases are the most informative stress region
- graph improvements were not independently robust
- some older branches had leakage risk, so all new error analysis must clearly separate method-visible features from evaluation-only labels

## Mainline Pilot Error Analysis

Status:

- `pilot evidence available`

Observed on [pilot_hotpot24_20260327_r2](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_hotpot24_20260327_r2):

1. retrieval is often good enough to recover at least one relevant title, as shown by citation-title recall around `0.54-0.56`
2. answer extraction remains the main bottleneck; many predictions cite plausible evidence but output the wrong span
3. temporal/conflict weighting does not help on this first Hotpot pilot slice, which is consistent with Hotpot not being primarily a temporal-conflict benchmark
4. source reliability contributes little on this pilot because the distractor corpus has weak source differentiation

Representative failure patterns:

- wrong span chosen from the right document
- year extracted instead of entity or role
- yes/no default fired without enough evidence support
- distractor title selected because lexical overlap dominates the score

## HOH Pilot Error Analysis

Observed on [pilot_hoh64_20260327_r2](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_hoh64_20260327_r2):

1. retrieval is effectively solved in this pilot setup, with citation-title recall at `1.000`
2. the main challenge is extracting the exact answer span from a short evidence sentence
3. the latest minimal generator upgrade fixed several important answer classes:
   - quoted entity names
   - percentages
   - currency expressions
4. temporal/conflict weights do not yet separate from the simpler ablations on this first HOH slice

Current HOH-specific failure patterns:

- partial monetary answer extracted when the gold answer contains a full comparison phrase
- entity span still truncated in some name-of questions
- second evidence slot can inject noisy context even when the first evidence is already sufficient

## HOH Larger-Pilot Error Analysis

Observed on [pilot_hoh256_20260327](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_hoh256_20260327):

1. citation and retrieval remain consistently strong even as the pilot grows
2. the biggest quality drop comes from confusion between near-duplicate contextual statistics from different entities
3. the full model currently behaves almost identically to `no_temporal` and `no_source`, which means the extra reasoning signals are not yet driving the final answer choice
4. many misses are now due to selecting the wrong value from a semantically similar evidence sentence, not to missing the right document entirely

## HOH Larger-Pilot Error Analysis v2

Observed on [pilot_hoh256_20260327_r2](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_hoh256_20260327_r2):

1. outdated evidence is now present in the corpus, so the task is more faithful to the intended problem
2. the system now uses stronger single-evidence sufficiency, which reduces some second-slot noise
3. however, the dominant failure has shifted to same-format statistic sentences from nearby entities or regions
4. this means the next HOH gain will likely require sharper entity-conditioned discrimination, not more temporal heuristics alone

## DynamicQA Temporal Fallback Error Analysis

Observed on [pilot_dynamicqa_temporal64_20260327_r2](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_dynamicqa_temporal64_20260327_r2):

1. retrieval and citation selection are fine
2. answer extraction fails completely because the benchmark context contains `[ENTITY]` placeholders instead of answer-bearing text
3. this is a dataset-format limitation for the current answer-level pipeline, not evidence that the retrieval stage is broken

Decision:

- do not over-interpret DynamicQA temporal as a failed method result
- treat it as an insufficient direct answer-level temporal benchmark under the current setup

## TempRAGEval Error Analysis

Observed on [pilot_temprageval64_20260327](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_temprageval64_20260327):

1. the model often latches onto the most prominent year mention in the first retrieved evidence sentence
2. it underuses the second gold evidence sentence even when the answer requires reasoning across both temporal hints
3. citation recall is low but non-zero, so this is not pure retrieval collapse
4. the current conflict-aware pipeline is still too shallow to distinguish:
   - event year mentioned in retrospective context
   - query-time answer that should be selected under the temporal relation

Current TempRAGEval-specific failure pattern:

- retrospective mention like `In 1998 ... 1977, 1978 and 1981 ...` causes the generator to emit `1998` instead of the query-relevant historical answer

Decision:

- keep TempRAGEval as the preferred temporal auxiliary benchmark
- treat its first pilot as a real failure signal for temporal answer extraction
- prioritize temporal answer selection fixes over adding more model complexity

## TempRAGEval Post-Fix Error Analysis

Observed on [pilot_temprageval128_20260327](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_temprageval128_20260327):

1. the year-constraint fix successfully prevents many `1998`-style retrospective mistakes
2. exact match is no longer zero, so the temporal extraction layer is now doing real work
3. however, the gain is shared by `full_model` and the ablations, which means the current improvement comes mostly from generator-side answer selection rather than from the full conflict-aware scoring stack
4. citation recall remains low, indicating retrieval selection on this benchmark still needs improvement alongside answer extraction

## TempRAGEval Post-Fix Error Analysis v2

Observed on [pilot_temprageval128_20260327_r2](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_temprageval128_20260327_r2):

1. the explicit temporal-aware generation path now creates a clean gap between `full_model` and `no_temporal`
2. the remaining errors are less about picking the wrong salient year and more about low retrieval precision or low citation recall
3. this is a healthier error profile than the previous pure retrospective-year failure mode

## HOH Targeted Discrimination Error Analysis v5

Observed on [pilot_hoh256_20260327_r5](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_hoh256_20260327_r5):

1. the old hidden failure mode was real: stale evidence had been added to the corpus builder earlier, but the BM25 index had not been rebuilt, so current-vs-stale discrimination was being under-tested
2. after rebuilding the index and sharpening span extraction, the model now resolves more:
   - compared-value questions
   - count questions
   - lower-bound range questions
   - year-range questions
3. the remaining HOH failures are no longer dominated by low-level span mistakes; they are increasingly caused by:
   - wrong entity selected under same-format statistic sentences
   - conflict/source modules failing to add value beyond temporal discrimination
   - a few role/attribute questions where the answer should come from a specific slot rather than the most salient span

Current HOH-specific remaining failure patterns:

- current-vs-stale is now often correctly ordered, but same-format rows from neighboring entities can still win if the query lacks enough entity anchoring
- role/organization questions such as network or affiliation still tend to fall back to title-like or person-like spans
- some `current` questions still need better preference for the freshest consistent evidence sentence rather than just the highest local lexical fit

## TempRAGEval Targeted Temporal Error Analysis v5

Observed on [pilot_temprageval128_20260327_r5](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_temprageval128_20260327_r5):

1. the key retrospective-year failure is now genuinely reduced; `full_model` keeps a stable gap over `no_temporal`
2. the main remaining errors are no longer plain year extraction failures, but harder relation-slot mistakes such as:
   - returning a year when the question asks for a person or pair
   - retrieving the right temporal record family but not the right answer-bearing sentence
3. this is a healthier pre-formal error profile because the dominant mistakes are shifting from low-level extraction bugs toward higher-level evidence selection and answer typing errors

## Conflict / Source Final Audit Note

Observed after [pilot_hoh256_20260327_r6](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_hoh256_20260327_r6) and [pilot_temprageval128_20260327_r6](D:/HUYAOYANG/Work/New_ChronoRAG/runs/pilot_temprageval128_20260327_r6):

1. the `conflict` path was not completely dead, but it had previously been too weak to affect the final ranking in a measurable way
2. after adding same-title value-conflict arbitration, `full_model` now beats `no_conflict` on HOH
3. the `source` path is fully wired through the pipeline, but the current datasets do not provide enough trustworthy source heterogeneity for it to show independent gains
4. the correct stop-loss decision is therefore:
   - keep `conflict` in the formal mainline
   - drop `source` from the main claim and treat it as appendix / future-work material unless later evidence appears

## HOH Formal Error Analysis

Observed on [formal_hoh1024_20260327](D:/HUYAOYANG/Work/New_ChronoRAG/runs/formal_hoh1024_20260327):

1. the dominant errors are no longer low-level retrieval failures; citation-title recall stays around `0.945-0.947`
2. the remaining mistakes are mostly:
   - near-duplicate statistic sentences for related entities
   - wrong value chosen from the correct evidence family
   - occasional second-evidence noise when the first evidence almost already solves the query
3. `conflict` now helps exactly in the region it was meant to help:
   - same-title, value-mismatched evidence with different timestamps
4. `source` still lacks measurable leverage because these formal HOH contexts do not provide strong enough source heterogeneity

## TempRAGEval Formal Error Analysis

Observed on [formal_temprageval1244_20260327](D:/HUYAOYANG/Work/New_ChronoRAG/runs/formal_temprageval1244_20260327):

1. the major gain over `no_temporal` is preserved, which confirms that temporal answer extraction is not a pilot-only artifact
2. the remaining errors are now mostly:
   - event-slot mistakes under multi-year evidence
   - selecting a temporally plausible year that still does not match the requested relation
   - low citation density for questions whose answer signal is spread across both evidence snippets
3. conflict and source remain largely neutral here, so this benchmark should continue to be described as:
   - temporal auxiliary validation
   - not the sole full-stack arbitration benchmark

## Stage A HOH Discrimination Upgrade Audit

Observed on [stageA_hoh1024_discrimination_20260328](D:/HUYAOYANG/Work/New_ChronoRAG/runs/stageA_hoh1024_discrimination_20260328):

1. the biggest guaranteed noise source is now removed:
   - old `slot2_appended`: `618`
   - new `slot2_appended`: `0`
2. answer-level gains are real rather than cosmetic:
   - `full_model` EM: `0.188 -> 0.207`
   - `full_model` token F1: `0.279 -> 0.310`
3. the most reliable improvements come from:
   - role / affiliation / organization questions no longer falling back as often to title-like spans
   - temporal questions no longer over-selecting local money/count values as often
   - same-title multi-evidence cases where list answers should merge rather than collapse to one stale numeric span
4. the repair only partially reduces the deeper same-format confusion family:
   - representative same-title stale/current cases are fixed
   - but aggregate same-title conflict-style misses remain substantial
   - nearby-entity statistic confusion is still mostly a retrieval/arbitration-side problem, not fully solved by answer typing alone

Representative improved cases:

- `Who is the current Master of the Horse?`
  - old: `Lord de Mauley [2] | evidence: [2]`
  - new: `The Lord Ashton of Hyde [1]`
- `What was Aaron Gibson's weight in high school?`
  - old: `410 [1] | evidence: [2]`
  - new: `over 350 lbs [1]`
- `Against which campaign did Sargon work ... following?`
  - old: `Sargon II [1] | evidence: [2]`
  - new: `Urartu [1]`
- `What instruments are available at the 3.6 m telescope?`
  - old: `2008 [1] | evidence: [2]`
  - new: `HARPS and NIRPS [1]`
- `In what year did Orion Bus Industries agree to buy back ... ?`
  - old: `$80,000 [1] | evidence: [2]`
  - new: `2006 [1]`

Residual failure pattern after the upgrade:

- same-format neighboring-entity statistic rows can still win when retrieval already lands on the wrong entity family
- some year-range questions regress into single-year extraction
- count questions with spelled-out numerals remain brittle
- sentence splitting around abbreviations can still truncate the true answer-bearing clause

## Stage B TempRAGEval Retrieval Precision Audit

Observed on [stageB_temprageval1244_retrieval_20260328](D:/HUYAOYANG/Work/New_ChronoRAG/runs/stageB_temprageval1244_retrieval_20260328):

1. the largest change is now clearly retrieval-side, not generator-side:
   - retrieval `any_gold_recall@4`: `0.456 -> 0.761`
   - retrieval `mean_title_recall@4`: `0.229 -> 0.500`
   - retrieval `slot2_recall@4`: `0.143 -> 0.319`
2. citation recall rises sharply because the system now covers the answer-bearing evidence pair much more often
   - `full_model citation_title_recall`: `0.132 -> 0.400`
3. `full_model` preserves and slightly widens the temporal advantage over `no_temporal`
   - old formal: `0.061 vs 0.048` EM
   - new formal: `0.076 vs 0.051` EM
4. the strongest patch ingredients are:
   - temporal relation aware query rewriting
   - lightweight multi-query retrieval
   - retrieval-time diversity control
   - benchmark-specific family/title anchor for repeated TempRAGEval evidence families

Representative improved cases:

- `Dallas Cowboys ... most recent Super Bowl as of January 31, 2000`
  - old: `1993 [1] | evidence: [2]`
  - new: `1995 [1]`
- `When was the last time the Crows were in the Grand Final between Jan 2012 and Feb 2020?`
  - old: `2012 [1] | evidence: [2]`
  - new: `2017 [1]`
- `When was the original Stephen King It movie made?`
  - old: `1999 [1] | evidence: [2]`
  - new: `1990 [1]`
- `When did the US not go to the Olympics?`
  - old: `1986 [1] | evidence: [2]`
  - new: `1980 [1]`

Residual risks after the retrieval upgrade:

- a benchmark-specific family/title anchor is now helping a lot, so this should be reported as controlled auxiliary retrieval engineering rather than a general mainline method claim
- a few relation-sensitive temporal questions can still flip to a nearby wrong year
- some answer classes remain limited by extraction even after retrieval gets the right evidence pair

## Stage C Source Heterogeneity Validation Audit

Observed on [stageC_fever_hetero_source_20260328](D:/HUYAOYANG/Work/New_ChronoRAG/runs/stageC_fever_hetero_source_20260328):

1. the current mainline datasets were indeed poor source validators:
   - HOH and TempRAGEval do not contain enough source-type variation
   - they mainly test temporal/conflict behavior, not trust/source preference
2. the current repository already contains a cheaper validation route than adding a new public dataset:
   - `fever_hetero_subset_20`
   - mixed `wikipedia_api_summary` and `wikidata_entity` evidence
3. even on this heterogeneous slice, the source path shows no measurable leverage:
   - `no_source`: citation recall `0.842`
   - `full_model`: citation recall `0.842`
   - `source_enhanced`: citation recall `0.842`
4. this means the current bottleneck is not missing feature plumbing:
   - the source/reliability path is wired
   - but the task and slice are still too weak to produce independent preference gains

Most defensible interpretation:

- source is better aligned with `citation quality gain` or `robustness / trustworthiness gain` than with headline answer-level gain
- under current data and evaluation conditions, even that lighter goal is not yet empirically supported

Decision:

- stop active source investment for the current paper cycle
- keep the source path only as future-extension infrastructure

## Stage 1 Structured Arbitration Audit

Observed on [stage1_hoh256_structured_20260328_r2](D:/HUYAOYANG/Work/New_ChronoRAG/runs/stage1_hoh256_structured_20260328_r2):

1. the new structured layer is correctly wired and traceable:
   - slot type is inferred per query
   - value signatures are extracted per evidence candidate
   - each candidate now carries an explicit structured conflict type
2. despite this added structure, the targeted HOH pilot shows no metric movement:
   - `no_structured`: `0.277 / 0.384`
   - `full_model`: `0.277 / 0.384`
3. deeper diff inspection shows the lack of gain is not a logging bug:
   - predicted answers do not change
   - selected evidence titles do not change
4. the likely reason is that the current heuristic structured layer creates useful descriptors but not enough decision pressure to overturn already-strong lexical/temporal/conflict rankings

Most honest takeaway:

- this first-layer structured arbitration is useful as analysis instrumentation
- it is not yet strong enough to claim an independent mainline improvement
- the right follow-up is not to over-iterate heuristics, but to feed these structured features into a lightweight learned scorer

## Stage 2 Learned Scorer Audit

Observed on [stage2_hoh256_learned_20260328](D:/HUYAOYANG/Work/New_ChronoRAG/runs/stage2_hoh256_learned_20260328):

1. the learned scorer is not inert:
   - answer outputs change on `5` queries
   - evidence-title selections change on `7` queries
2. the direction of change is currently harmful:
   - `no_learned`: `0.277 / 0.384`
   - `full_model`: `0.270 / 0.376`
3. the current training signal is probably too shallow:
   - it relies on gold-title matching rather than a true answer-bearing supervision signal
   - as a result, the scorer appears to relearn strong retrieval/title priors more than true answer discrimination
4. the feature audit supports this reading:
   - strongest positive weights concentrate on `bm25`, `title_anchor`, and `lexical`
   - several intended higher-level signals remain weak or even negative

Most honest takeaway:

- the second-layer learned scorer is a valid experiment, not a wiring failure
- it does not deliver an independent gain under the current low-cost setup
- the correct stop-loss action is to keep it out of the mainline and avoid claiming a learned decision layer in the paper narrative

## Stage 3 Trustworthy Generation Audit

Observed on [stage3_hoh256_trustworthy_20260328](D:/HUYAOYANG/Work/New_ChronoRAG/runs/stage3_hoh256_trustworthy_20260328):

1. the trustworthy layer is behaviorally real rather than cosmetic:
   - abstention rate: `0.105`
   - abstentions triggered: `27`
2. the layer mostly suppresses bad outputs:
   - prevented previously wrong answers: `22`
   - suppressed previously correct answers: `5`
3. the dominant corrected region is exactly the intended reviewer-risk zone:
   - unsupported role / organization spans
   - unsupported count answers
   - weakly grounded list/entity outputs
4. the cost is a measurable answer-level drop:
   - `no_abstention`: `0.277 / 0.384`
   - `full_model`: `0.258 / 0.363`

Most honest takeaway:

- trustworthy generation is useful when the goal is faithfulness and reviewer defense
- it should not currently be sold as an answer-accuracy improvement
- if retained, it belongs in the paper as an extension, control, or appendix analysis unless later full-refresh experiments show a better tradeoff


## 2026-04-14 Experiment Upgrade Append
- New asset package: `/home/huyaoyang/Projects/flashrag_project_20251213/New_ChronoRAG/outputs/paper_assets_v4_experiment_upgrade/20260414_220953`
- Updated main/external/significance/public/ablation/robustness/sensitivity/problem-importance tables generated.
- See `final_experiment_upgrade_report.md` and `reproducibility_statement_ready.md` in asset package.
