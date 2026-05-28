# Full Paper Draft v2

## Title

Metadata-Aware Grounded Retrieval for Official FEVER Evidence Access

## Abstract

This paper studies metadata-aware grounded retrieval for official FEVER evidence access. Starting from a fixed BM25 candidate retriever, we ask whether lightweight metadata-aware lexical cues can improve strict gold-page access without changing candidate coverage. We evaluate a family of rerankers on a disjoint 1000-query official FEVER validation split, including title overlap, exact title boost, alias-style matching, and disambiguation-aware title matching. The results show that metadata-aware reranking improves early evidence access under a fixed retrieval budget. Exact title boost is the strongest aggressive variant, title overlap is a more conservative variant with fewer regressions, and disambiguation-aware matching gives additional support for a type-sensitive diagnosis of ranking failures. Efficiency-oriented metrics such as MRR, nDCG, and first-hit-rank summaries further show that the gain comes from better early evidence access rather than broader retrieval coverage. The paper is deliberately retrieval-only and does not claim a complete ChronoRAG system.

## 1. Introduction

Evidence access remains a core bottleneck in grounded claim verification. In FEVER-style settings, a lexical retriever such as BM25 often retrieves a neighborhood of relevant pages, but it does not always place the gold evidence page at the earliest rank. This suggests a narrower and more tractable problem than full end-to-end verification: can we improve grounded evidence access inside an already retrieved candidate set?

This paper focuses on that retrieval-stage question for official FEVER. The goal is not to validate a complete ChronoRAG pipeline, nor to introduce generation, GraphRAG, or a large learned reranker. Instead, we study whether lightweight metadata-aware lexical cues can improve early access to the correct evidence page under a fixed retrieval budget.

Earlier versions of this work emphasized token-level title overlap. However, the current repository evidence supports a broader and more accurate story. On the repaired disjoint 1000 validation split, title overlap is effective relative to BM25, but an exact-title-style boost is stronger, while a disambiguation-sensitive cue provides additional diagnosis-oriented support. This means the right contribution is not a single-heuristic paper about title overlap, but a family study of metadata-aware grounded retrieval.

## 2. Problem Framing

We define metadata-aware grounded retrieval as lightweight reranking over a fixed BM25 candidate pool using cheap metadata signals already present in the retrieved page representation, such as page title, document identifier normalization, and lead-text-derived cues. The setting is grounded because success is measured by access to the FEVER gold evidence page under strict and relaxed matching definitions.

This framing is intentionally narrow. We do not change the retriever, do not enlarge the candidate set, and do not introduce dense models or trained cross-encoders. The question is instead whether a small amount of grounded page metadata can correct early-rank mistakes that pure lexical retrieval leaves unresolved.

## 3. Metadata-Aware Family

We evaluate a family of lightweight rerankers over the same BM25 candidate lists.

The first family member is title overlap, which boosts candidates whose title shares content-bearing tokens with the claim. This is the most conservative useful variant in the current study.

The second family member is exact title boost, which fires when the page title or its de-parenthesized base title appears as a contiguous phrase in the claim. This is the strongest aggressive variant in the current results.

The third family member is alias-style matching, implemented here as a lightweight heuristic over title normalization and lead-text alias-like surfaces. In the current study this variant does not help, and is better interpreted as a negative control showing that alias-aware signals are not robust without a clean metadata source such as an explicit redirect or alias table.

The fourth family member is disambiguation-aware title matching, which rewards candidates whose parenthetical qualifier aligns with type-bearing words in the claim. This variant is not the strongest overall, but it provides useful evidence that disambiguation-sensitive metadata cues target a real sub-problem in FEVER evidence retrieval.

## 4. Experimental Setup

All experiments use official FEVER evidence retrieval with BM25 candidate retrieval as the baseline. The main evaluation anchor is the repaired disjoint 1000 validation split. This choice is important because an older 1000-query follow-up split overlapped with the tuning split and therefore should not be treated as the main independent validation result.

We report strict and relaxed retrieval metrics. Strict evaluation requires matching the correct gold evidence page, while relaxed evaluation allows looser evidence-page matches under the current repository definition. This distinction matters because the paper is specifically about grounded page access rather than only loose lexical relevance.

## 5. Main Results

The main pattern is that metadata-aware reranking improves early evidence access without changing top-10 strict coverage. BM25 reaches strict Recall@1 of 0.368 on the disjoint 1000 split. Title overlap raises this to 0.415 with only two strict regressions, making it a useful conservative variant. Exact title boost raises strict Recall@1 further to 0.544, but with more regressions, showing a stronger but less conservative behavior. Disambiguation-aware matching gives a smaller positive gain to 0.378 and is especially tied to type-bearing or parenthetical claim surfaces. The current alias-style heuristic reduces performance, indicating that not all metadata cues are equally reliable.

These results support a family-level interpretation. Metadata-aware lexical cues do help grounded FEVER retrieval, but they occupy different points on a strength-versus-conservativeness frontier. The paper should therefore emphasize the family comparison rather than presenting title overlap as the sole validated method.

## 6. Efficiency Frontier

The current results are well suited to an efficiency-oriented interpretation because candidate generation is unchanged. Strict Recall@10 remains fixed at 0.720 across BM25, title overlap, exact title boost, and the other tested rerankers. The gain therefore comes from reordering already retrieved candidates.

Efficiency metrics reinforce this point. Under strict evaluation, BM25 has MRR 0.478 and mean first-hit rank 2.575. Title overlap improves these to 0.520 and 2.078. Exact title boost improves them further to 0.617 and 1.451. Similar trends appear in nDCG@5 and nDCG@10. These results support the claim that metadata-aware reranking improves early evidence access under a fixed retrieval budget.

The efficiency claim should still be kept narrow. We do not present a full hardware benchmark or an end-to-end verifier cost study. The supported claim is budget-preserving early evidence access, not universal runtime superiority.

## 7. Diagnosis and Error Analysis

The family comparison also clarifies why different variants behave differently. Exact title boost is strongest on claims that explicitly contain the gold page title as a clean surface form. Title overlap helps more conservatively on claims whose entity surface is partially shared with the correct page title. Disambiguation-aware matching especially helps claims containing type-bearing words such as film, series, album, or actor, which often correspond to parenthetical page qualifiers in FEVER.

The negative alias result is also informative. A naive alias-style heuristic over lead text and title normalization is too noisy in the current setup, likely because the FEVER corpus packaging used here does not expose a clean redirect or alias table. This is useful paper evidence because it shows that metadata-aware grounded retrieval is not simply “any extra metadata helps.” Instead, the metadata source and matching rule matter.

## 8. Scope and Defensibility

This is intentionally a retrieval-only FEVER paper. It is not a full ChronoRAG paper, and it does not claim that Route B, Route C, generation, or GraphRAG has been validated. That narrower scope is not a weakness if described honestly. The paper studies a concrete grounded retrieval problem on an established benchmark, uses an independent repaired split, compares nearby lightweight baselines, and provides diagnosis-oriented analysis. That is a defensible short-paper contribution.

## 9. Limitations

The study remains limited to official FEVER retrieval and lightweight lexical metadata cues. The alias-aware variant is only a heuristic because no clean redirect table is used in the current setup. The efficiency framing is based on ranking metrics and fixed-budget access rather than full runtime benchmarking. Finally, the paper does not validate a full verifier-generator pipeline, so its claims should remain tightly scoped to retrieval-stage evidence access.

## 10. Conclusion

The strongest version of the current paper is a metadata-aware grounded retrieval study for official FEVER. The evidence no longer supports a title-overlap-only story. Instead, it supports a clearer family-level conclusion: lightweight metadata-aware lexical reranking can improve early gold-page access under a fixed BM25 budget, exact title boost is the strongest aggressive variant, title overlap is the most conservative useful variant, and disambiguation-aware cues provide additional diagnosis-oriented support. That is a cleaner, more defensible, and more paper-ready contribution than the earlier single-heuristic framing.
