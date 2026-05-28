# Reviewer Gap Audit

## Scope and Evidence Base

This audit is written from the perspective of a strict NLP / IR reviewer and is grounded in the current ChronoRAG repository state, not in hypothetical future work.

Reviewed assets:
- `notes/ChronoRAG_操作说明书.md`
- `notes/results_error_validity_draft.md`
- `notes/tables_markdown.md`
- `notes/case_analysis.md`
- `notes/case_table.md`
- `notes/overlap_check_report.md`
- `runs/fever_official_route_a/`
- `runs/fever_official_route_a_1000/`
- `runs/fever_official_route_a_disjoint_1000/`

Unavailable asset:
- `ChronoRAG_实验二进度总表.md` was requested but is not present in the current repository, so it is not part of the evidence chain for this audit.

Important framing note:
- The only result that currently supports an independence claim is `runs/fever_official_route_a_disjoint_1000/`.
- The older `runs/fever_official_route_a_1000/` result overlaps with the 500-query tuning split and should not be presented as the main validation result.

## 1. Experimental Dimensions Already Covered

The current repository already contains more structure than a toy prototype. The strongest existing dimensions are:

1. Official FEVER evidence retrieval setup rather than live Wikipedia summaries.
- The project has moved onto the official FEVER claims and FEVER wiki-pages corpus.
- The main claim is now scoped to evidence retrieval on official FEVER, which is much more defensible than the earlier demo-style setup.

2. Clear separation between relaxed and strict evaluation.
- The repository now distinguishes relaxed matching from strict gold-page matching.
- This is a major strength because the paper can explicitly argue that the useful result is not an artifact of substring matching.
- In the disjoint 1000 validation, strict Recall@1 improves from `0.368` to `0.415`, while strict Recall@10 stays at `0.720`.

3. Parameter tuning on a dedicated 500-query split.
- The 500-query run includes a title-weight sweep from `0.1` to `0.5`.
- The best setting selected from that sweep is `bm25_weight=0.5`, `title_weight=0.5`.
- The tuning trace is documented in `runs/fever_official_route_a/official_weight_sweep_results.json`.

4. A repaired independent validation split.
- The repository explicitly documents that the original 1000-query follow-up split overlapped with the 500-query tuning set.
- This problem was identified, documented, and repaired through a disjoint 1000-query validation split.
- That repair is a real strength because it shows awareness of data leakage rather than hiding it.

5. Label-wise reporting.
- The disjoint 1000 run reports SUPPORTS and REFUTES separately.
- Under strict evaluation, both labels improve:
  - SUPPORTS: `0.411 -> 0.466` at Recall@1
  - REFUTES: `0.325 -> 0.365` at Recall@1
- This is useful because it shows the effect is not isolated to only one label type.

6. Case analysis and regression analysis.
- There is already a meaningful case analysis over improved and regressed examples.
- The current notes correctly emphasize that the gain comes from reranking within a fixed candidate pool, not from expanded coverage.
- The documented regressions are interpretable title-driven failures rather than unexplained noise.

7. Failure analysis of the official BM25 baseline.
- The project already examined baseline failures such as lexical gap, title mismatch, and gold-page-not-recalled cases.
- This is valuable because it motivates why a title-based reranker could plausibly help.

## 2. Key Experimental Dimensions Still Missing

From a reviewer perspective, the missing pieces are now less about basic plumbing and more about scientific sufficiency.

### A. Missing robustness validation beyond one repaired split

The main independent result currently rests on one disjoint 1000-query validation split.

Why this matters:
- A reviewer can reasonably say the method works on one repaired sample, but the stability of the effect is still underdetermined.
- The title-weight sweep was done on a single 500-query sample and then validated on one disjoint 1000-query sample. That is much better than the earlier overlapping setup, but still weak for stronger claims about robustness.

What is currently missing:
- full `shared_task_dev` fixed-weight validation
- repeated disjoint validation across multiple random seeds or multiple disjoint splits
- any confidence interval or statistical significance test for the strict top1 improvement

### B. Missing nearest-neighbor baseline comparisons

The current comparison is effectively:
- BM25
- BM25 + token-level title overlap reranking

That is not enough for a strong IR-style paper because the most natural reviewer question is: why this exact title-overlap heuristic instead of a simpler, equally lightweight title-aware heuristic?

What is currently missing:
- page title exact-match boost baseline
- binary title-hit feature vs token-overlap feature comparison
- alias/title normalization baseline as a retrieval-time heuristic

This is important because the current method is very close to standard lexical heuristics. Without a nearby baseline family, the reviewer may conclude that the reported gain is not specific to the proposed design.

### C. Missing statistical testing

The current tables report deltas, but not uncertainty.

Why this matters:
- The main strict improvement on disjoint 1000 is meaningful in absolute terms (`+47` strict top1 hits), but the paper still needs some notion of reliability.
- Because the method only changes ranking inside a fixed candidate set and does not move Recall@10, the main effect is concentrated at the top ranks. Reviewers will often ask for paired significance on those rank changes.

What is currently missing:
- paired significance test between baseline and reranked top1 correctness
- confidence intervals or bootstrap intervals for Recall@1 / Recall@5 deltas

### D. Missing full-dev confirmation

Even for a workshop paper, a reviewer may ask why the fixed best weight was not run on the full official dev verifiable pool once tuning was complete.

Why this matters:
- A full-dev fixed-weight run is not a new method, just a stronger confirmation of the same method.
- Because the current method is cheap and training-free, the absence of a full-dev run can look like avoidable incompleteness.

### E. Missing efficiency / practicality reporting

The method is positioned as lightweight and appealing partly because it is simple.

What is currently missing:
- reranking cost relative to BM25 retrieval
- whether the title-overlap score requires any expensive extra I/O or preprocessing
- how much extra latency or memory the reranker adds

This omission is especially noticeable because lightweight heuristics are often justified on efficiency grounds.

### F. Missing paper-level scoping discipline inside the repo

The repository still contains Route A temporal / reliability artifacts and older overlapping results side-by-side with the title-overlap line.

Why this matters:
- A reviewer will not see the repo, but a paper drafted from these assets can easily become scope-confused.
- The current strongest line is narrow: official FEVER evidence retrieval plus title-overlap reranking.
- Anything that mixes in temporal or reliability modules without gains will weaken the story.

## 3. Questions a Strict Reviewer Will Strongly Challenge

These are the points most likely to trigger serious scrutiny.

### 3.1 Is the validation truly independent?

This was already a real issue once, and the repo documents it.

Why it will be challenged:
- The older `fever_official_route_a_1000` run was not independent.
- Even though the disjoint 1000 repair exists, a reviewer will be sensitive to whether the paper still cites the older run in a way that looks like confirmation.

What must be true in the paper:
- The disjoint 1000 run must be the main validation result.
- The older overlapping 1000 run, if mentioned at all, should be explicitly labeled as a non-independent follow-up or moved to an appendix / ablation note.

### 3.2 Is the gain specific to title-overlap, or would any title-aware lexical heuristic do the same?

This is probably the single biggest scientific challenge after split independence.

Why it will be challenged:
- Title-overlap is simple and plausible, but also very close to common lexical IR heuristics.
- Without comparison to a nearby baseline such as exact title match boost, the reviewer can argue the paper is under-ablated.

### 3.3 Is this an evidence retrieval result or a FEVER verification result?

Why it will be challenged:
- FEVER papers often report end-to-end verification or at least evidence retrieval tied to verification labels.
- The current experiments are retrieval-only.

What must be stated clearly:
- This is a page-level evidence retrieval reranking result, not a full claim-verification system result.
- The unchanged Recall@10 shows that the method improves ordering, not candidate coverage.

### 3.4 Is the gain stable, or is it a one-split artifact?

Why it will be challenged:
- Only one repaired disjoint 1000 split has been used as the main independent validation.
- No multi-seed or repeated-split evidence is currently available.

### 3.5 Is the method novel enough for the target venue?

Why it will be challenged:
- The method is a simple weighted fusion of BM25 and title-overlap score.
- For a formal conference-style submission, that novelty bar may be too low unless the paper is framed as a careful empirical note or short paper.

What this means in practice:
- The framing must emphasize a small, robust, reproducible reranking improvement, not a broad algorithmic advance.

## 4. Must-Fix vs Optional Enhancements

## Must-Fix for a Workshop-Ready Version

1. Use only the disjoint 1000 split as the main validation result.
- The old overlapping 1000 result cannot serve as independent confirmation.
- This is already repairable using current assets and mostly a presentation issue now.

2. Make the paper scope retrieval-only and title-overlap-only.
- Do not let temporal / reliability / Route B / Route C appear as if they support this paper's main claim.
- The clean paper story is much narrower than the broader ChronoRAG repo.

3. Add one nearest-neighbor title baseline.
- The most important missing comparison is a simpler title-aware lexical heuristic.
- A page-title exact-match boost baseline is the cleanest candidate.
- Without this, the title-overlap contribution is under-justified.

4. Add a significance or uncertainty analysis.
- Even a paired bootstrap or approximate randomization test on strict top1 correctness would materially strengthen the result.
- This is analysis-only and does not require method redesign.

5. Clean up the narrative around tuning and validation.
- The paper should explicitly state: 500 for tuning, disjoint 1000 for validation, fixed weight `0.5/0.5` carried forward unchanged.

## Must-Fix for a More Formal Submission

1. Run the fixed best method on full official dev verifiable.
- This is the most obvious missing robustness result.
- A formal reviewer will likely expect it.

2. Add repeated validation or multiple disjoint splits.
- One repaired split is helpful but still limited.
- Repeating the fixed method on additional disjoint samples or multiple seeds would materially strengthen generality claims.

3. Include at least one stronger ablation family around title signals.
- Example: exact title match boost vs token overlap vs normalized title overlap.
- Not many variants are needed, but one nearest baseline is probably insufficient for a more formal venue.

4. Report computational overhead.
- Even a small table with reranking cost and storage implications would help justify the "lightweight" claim.

## Optional Enhancements

1. Expand the qualitative analysis with 1-2 more failure archetypes.
- Useful, but not essential if the current case analysis is already clear.

2. Add claim-type analysis beyond label-wise splits.
- For example, entity-heavy vs relational claims, ambiguous titles vs exact-title claims.
- Interesting, but secondary.

3. Add an appendix comparing strict and relaxed improved cases in more detail.
- Helpful for completeness, not essential for the core claim.

## 5. Minimal But Sufficient Supplementary Experiment List

This section is the practical answer to "what is the smallest additional package that would make this look like a real paper rather than only a promising experiment log?"

### Priority 1. Nearest-baseline comparison

Add exactly one title-aware baseline:
- `BM25 + exact page-title match boost`

Why this is first:
- It directly answers the most obvious reviewer objection.
- It is method-adjacent, cheap, and easy to interpret.
- If title-overlap still wins, the current method becomes much more convincing.

Expected paper value:
- establishes that the gain is not simply due to any generic title bonus

### Priority 2. Significance / uncertainty analysis on disjoint 1000

Add a paired significance analysis for strict top1 correctness and ideally strict Recall@5.

Why this is second:
- The main result already exists; this makes it statistically defensible.
- It is analysis-only and does not require rerunning the system if per-query outputs already exist.

Expected paper value:
- upgrades the result from "promising delta" to "quantified improvement"

### Priority 3. Full-dev fixed-weight confirmation

Run only the frozen best method on the full official dev verifiable split:
- baseline BM25
- BM25 + title-overlap with `0.5/0.5`
- strict and relaxed evaluation only

Why this is third:
- It is the cleanest robustness check without changing the method.
- It avoids reopening tuning and does not require new features.

Expected paper value:
- turns the paper from a strong workshop note into something closer to a fully validated short paper

### Priority 4. Lightweight efficiency table

Report:
- candidate count reranked per query
- extra reranking time per query or per 1000 queries
- any additional index or metadata requirement

Why this is fourth:
- The method is being sold as lightweight; the paper should prove that claim.

### Priority 5. Optional second disjoint split or second seed

If time permits, repeat the disjoint validation once more with the same frozen `0.5/0.5` weights.

Why this is last:
- Valuable, but less urgent than nearest-baseline and full-dev confirmation.
- It is the next best defense against the "one lucky split" critique.

## Workshop vs More Formal Submission

## Suitable for a Workshop-Style Paper After Minimal Fixes

A workshop paper is plausible if the scope is kept narrow:
- official FEVER evidence retrieval
- BM25 baseline
- title-overlap reranking as a lightweight top-rank improver
- strict gold-page evaluation as the primary metric

For that version, the paper can likely survive with:
- disjoint 1000 as the main result
- one nearby title-based baseline
- significance analysis
- a clear retrieval-only framing

## Still Weak for a More Formal Submission Without More Work

For a more formal venue, the current package is still thin because:
- the method is very simple
- robustness is shown on only one repaired validation split
- there is no full-dev result yet
- nearby baseline coverage is too limited
- there is no variance or significance reporting yet

In short:
- workshop version: realistic with targeted repairs
- more formal submission: not ready yet without at least one stronger robustness extension and one better ablation comparison

## Bottom-Line Judgment

Current status:
- The project has crossed the line from engineering prototype to defensible small-scale retrieval study.
- It has not yet crossed the line to a fully reviewer-hardened paper package.

Most important next step:
- add one nearest-baseline title heuristic and a significance test on the disjoint 1000 split

If only a minimal supplement package is feasible, the most cost-effective set is:
1. keep disjoint 1000 as the sole main validation result
2. add `BM25 + exact title match boost` as a comparator
3. add paired significance on strict top1
4. if possible, add one full-dev fixed-weight run

That combination would make the current paper materially harder to dismiss.
