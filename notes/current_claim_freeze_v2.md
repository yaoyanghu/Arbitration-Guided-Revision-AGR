# Current Claim Freeze v2

## Purpose

This note freezes the upgraded paper claim after the metadata-family and efficiency analysis in `runs/fever_metadata_family_v1/`.

Primary evidence checked:

- `runs/fever_metadata_family_v1/family_results.json`
- `runs/fever_metadata_family_v1/efficiency_results.json`
- `reports/fever_metadata_family_v1/RESULT_SUMMARY.md`
- `runs/fever_official_route_a_disjoint_1000/official_strict_eval_results.json`
- `runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/nearest_title_baseline_results.json`
- `notes/current_claim_freeze.md`
- `notes/final_upgrade_experiment_plan.md`

## 1. Upgraded Main Claim

The paper should now be framed as:

- **a metadata-aware grounded retrieval paper for official FEVER evidence access**

The safest claim is:

- lightweight metadata-aware lexical reranking improves early gold-page access inside a fixed BM25 candidate pool
- the effect is best understood as a grounded evidence-access improvement, not as broader retrieval coverage
- the main benefit is budget-preserving early-rank correction

This is stronger and safer than:

- `title overlap is the main validated method`

## 2. How `exact_title_boost` Should Be Positioned

`exact_title_boost` is now the strongest tested member of the metadata-aware family.

Its proper positioning is:

- the aggressive metadata-aware lexical variant
- the upper-performing family anchor on the current disjoint 1000 split
- evidence that the broader title/metadata grounding story is real

It should not be positioned as:

- proof that exact surface match is universally optimal beyond this setup

Why:

- it gives the best absolute gains
- but it also causes more regressions than `title_overlap`

So the stable family story is:

- `exact_title_boost` = strongest
- `title_overlap` = most conservative

## 3. Do Alias and Disambiguation Add Real New Support?

### `alias_redirect_match`

Not as a positive contribution in its current form.

Current result:

- strict top1 falls from `368` to `357`
- strict improved / regressed = `1 / 12`

What it does add:

- a useful negative control
- evidence that naive alias heuristics are noisy without a clean redirect or alias table

### `disambiguation_title_match`

Yes, but modestly.

Current result:

- strict top1 rises from `368` to `378`
- strict improved / regressed = `22 / 12`

What it adds:

- direct support for the diagnosis claim that type-sensitive disambiguation is a real source of ranking error
- evidence that metadata signals beyond plain title overlap can help specific FEVER claim types

## 4. Do the Efficiency Metrics Support `budget-preserving`?

Yes, with careful wording.

Supported:

- strict MRR improves from `0.478` to `0.520` for `title_overlap`
- strict MRR improves further to `0.617` for `exact_title_boost`
- strict mean first-hit rank improves from `2.575` to `2.078` for `title_overlap`
- strict mean first-hit rank improves further to `1.451` for `exact_title_boost`
- strict top-10 coverage remains unchanged at `0.720`

Therefore the paper can safely say:

- metadata-aware reranking improves early evidence access under a fixed retrieval budget

But it should not say:

- measured end-to-end runtime is lower
- downstream verification cost is proven lower

because those were not directly benchmarked here.

## 5. What the Paper Still Cannot Say

The paper still should not claim:

- that token-level title overlap is the strongest method
- that the current alias heuristic is a validated positive result
- that the method is redirect-aware in the sense of using a real redirect table
- that the paper validates a complete ChronoRAG system
- that Route B or Route C is part of the evidence chain
- that generation or GraphRAG has been validated
- that the method is generally optimal outside this FEVER retrieval setting

## Final Freeze

Current frozen claim:

- **This paper studies metadata-aware grounded retrieval for official FEVER evidence access. Over a fixed BM25 candidate pool, lightweight metadata-aware lexical rerankers improve early strict gold-page access without changing top-k coverage. Among the tested family members, exact title boost is the strongest aggressive variant, title overlap is the most conservative useful variant, and disambiguation-aware matching provides additional diagnosis-oriented support for type-sensitive ranking errors.**
