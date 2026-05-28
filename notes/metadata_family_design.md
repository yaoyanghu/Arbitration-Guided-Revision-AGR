# Metadata-Aware Family Design

## Scope

This design upgrades the current FEVER short paper line from a single `title-aware lexical reranking` story to a broader `metadata-aware grounded retrieval` family study.

Grounding evidence checked before writing this plan:

- `notes/current_claim_freeze.md`
- `notes/paper_closeout_plan.md`
- `notes/paper_wording_pack.md`
- `notes/final_table_pack.md`
- `notes/results_error_validity_draft.md`
- `runs/fever_official_route_a_disjoint_1000/official_strict_eval_results.json`
- `runs/fever_official_route_a_disjoint_1000/official_labelwise_results.json`
- `runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/nearest_title_baseline_results.json`
- `src/analysis/official_title_overlap_improvement.py`
- `src/analysis/official_strict_revalidation.py`
- `src/analysis/nearest_title_baseline_eval.py`
- `src/retrieval/search.py`

Important boundary:

- This family is for FEVER retrieval only.
- It does not include Route B or Route C.
- It does not include generation, GraphRAG, dense retrieval, or learned rerankers.

## 1. Family Definition

Recommended family definition:

- `metadata-aware lexical reranking` means lightweight reranking over a fixed BM25 candidate pool using interpretable page metadata already exposed by current retrieval outputs, mainly `title`, `doc_id`, and lead-text-derived cues from `text`.

Recommended paper-safe framing:

- The study asks which cheap metadata cues help move the correct evidence page earlier in rank without expanding the candidate set.
- The family is grounded because the target remains strict FEVER evidence-page access, not open-ended semantic relevance.

Core shared structure:

- retrieve with BM25 once
- normalize BM25 scores per query
- compute one lightweight metadata feature per candidate
- linearly fuse `normalized_bm25 + metadata_feature`
- evaluate under the current strict and relaxed FEVER definitions

## 2. Candidate Variants

### P0 variants

#### A. `title_overlap`

Current status:

- Already implemented in `src/analysis/official_title_overlap_improvement.py`
- Already validated on disjoint 1000

Intuition:

- If the claim repeats salient content tokens from the page title, that page should move upward among already retrieved lexical neighbors.

Required input fields:

- `query`
- `title`
- optionally de-parenthesized base title
- normalized BM25 score

Potential risk:

- can overvalue surface token overlap without resolving entity identity
- can still be misled by wrong but lexically similar pages

Role in family:

- conservative lexical metadata baseline

#### B. `exact_title_boost`

Current status:

- Already implemented in `src/analysis/nearest_title_baseline_eval.py`

Intuition:

- If the page title, or its de-parenthesized base title, appears as a contiguous phrase in the claim, that is a strong grounded hint for the correct page.

Required input fields:

- `query`
- `title`
- de-parenthesized base title
- normalized BM25 score

Potential risk:

- brittle to paraphrase and alias use
- can aggressively over-promote exact phrase matches that are still not the gold FEVER page
- current evidence shows it is stronger but also less conservative than title overlap

Role in family:

- strongest current P0 anchor
- should likely be positioned as the aggressive variant

#### C. `alias_redirect_match`

Recommended implementation scope:

- heuristic alias-style surface matching derived only from current retrieval outputs
- do not assume a true Wikipedia redirect table, because current FEVER corpus packaging does not expose one

Intuition:

- some FEVER misses come from title normalization or alias mismatch rather than pure retrieval failure
- a candidate should receive a boost if its lead text exposes a likely alias that appears in the claim

Required input fields:

- `query`
- `title`
- `doc_id`
- `text`
- normalized BM25 score

Practical feature sources available in the current repo:

- base title from `title`
- normalized title from `doc_id`
- alias-like strings in lead text such as `also known as`, `known as`, `alias`, quoted alternate forms, or appositional short forms

Potential risk:

- FEVER official pages do not expose a clean alias table
- heuristic alias extraction from lead text may be noisy
- this should be named `alias_redirect_match` only if the paper clearly states that the redirect part is heuristic rather than table-backed

Role in family:

- P0 if implemented as a lightweight heuristic baseline
- scientifically useful because it directly addresses a reviewer-style `alias/title normalization` question already noted in the repo

#### D. `disambiguation_title_match`

Intuition:

- many FEVER ranking errors involve disambiguation-sensitive pages such as `(film)`, `(TV series)`, `(album)`, `(actor)`, or explicit disambiguation pages
- a candidate should be rewarded when its parenthetical qualifier matches evidence-bearing type words in the claim

Required input fields:

- `query`
- `title`
- `doc_id`
- `text`
- normalized BM25 score

Potential risk:

- type words like `film`, `series`, `band`, `album`, `city`, `actor` can be absent from the claim even when the qualified page is correct
- over-penalizing generic base-title pages could create regressions

Role in family:

- P0 because the current notes already show disambiguation-heavy failure patterns

### P1 variants

#### E. `page_type_prior`

Intuition:

- some page forms are systematically better evidence pages than others, while explicit disambiguation pages or list-like pages are often weaker top-1 choices

Required input fields:

- `title`
- `text`
- maybe `doc_id`
- normalized BM25 score

Practical current approximation:

- infer weak page type from title and lead text only
- examples: disambiguation page, list page, season page, surname page, franchise page

Potential risk:

- very heuristic
- FEVER gold pages can still legitimately be list-like or broad pages
- can silently encode dataset-specific bias if made too strong

Role in family:

- P1 optional
- good for diagnosis, but not required for the first paper-ready family table

#### F. `first_sentence_entity_anchor`

Intuition:

- if the opening sentence directly anchors the same entity phrase or alias that appears in the claim, that can be a grounded cue stronger than raw title tokens alone

Required input fields:

- `query`
- `title`
- `text`
- normalized BM25 score

Potential risk:

- lead-text parsing is noisier than title-based features
- can collapse into a fuzzy semantic heuristic if not kept simple

Role in family:

- P1 optional
- useful only if implemented with a very lightweight and interpretable rule set

## 3. Required Inputs by Variant

| variant | query | title | doc_id | text | normalized BM25 |
| --- | --- | --- | --- | --- | --- |
| title_overlap | yes | yes | no | no | yes |
| exact_title_boost | yes | yes | optional | no | yes |
| alias_redirect_match | yes | yes | yes | yes | yes |
| disambiguation_title_match | yes | yes | yes | optional | yes |
| page_type_prior | no | yes | optional | yes | yes |
| first_sentence_entity_anchor | yes | yes | no | yes | yes |

## 4. Misleading-Risk Summary

| variant | main risk |
| --- | --- |
| title_overlap | over-promotes lexical neighbors with shared title tokens |
| exact_title_boost | brittle but aggressive; may over-promote exact matches that are not the FEVER gold page |
| alias_redirect_match | alias extraction may be noisy because no true redirect table is currently exposed |
| disambiguation_title_match | type-word matching may be too narrow and miss valid pages without explicit type mention |
| page_type_prior | may hard-code dataset bias against broad or list-like pages |
| first_sentence_entity_anchor | lead-text pattern rules may become fuzzy and less interpretable |

## 5. P0 vs P1

### P0 must-do

- `title_overlap`
- `exact_title_boost`
- `alias_redirect_match`
- `disambiguation_title_match`

Reason:

- These four variants can all be built from fields already present in the current disjoint run outputs.
- They directly answer the strongest reviewer-facing question: which lightweight metadata cue family actually helps, and what is the aggressive-vs-conservative tradeoff?

### P1 optional

- `page_type_prior`
- `first_sentence_entity_anchor`
- any simple combined variant after single-feature baselines are stable

Reason:

- They are diagnosis-friendly but less necessary for the first paper-safe family comparison.

## 6. Recommended Paper Positioning

The paper should not present the family as a search for one final magic heuristic.

The safer framing is:

- BM25 already often retrieves the right evidence page somewhere in top-k
- metadata-aware lexical cues help re-order that fixed candidate set
- different metadata cues occupy different points on a strength-vs-conservativeness frontier

On the current repository evidence:

- `exact_title_boost` is the strongest known aggressive variant
- `title_overlap` is a weaker but more conservative variant
- `alias_redirect_match` and `disambiguation_title_match` are the two most justified next P0 additions for turning the story into a real metadata-aware family paper
