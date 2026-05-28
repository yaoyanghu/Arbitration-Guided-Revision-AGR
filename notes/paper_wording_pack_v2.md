# Paper Wording Pack v2

## 1. Recommended Titles

1. Metadata-Aware Grounded Retrieval for Official FEVER Evidence Access
2. Budget-Preserving Metadata-Aware Reranking for Official FEVER Evidence Retrieval
3. Diagnosing Metadata Cues for Grounded Evidence Retrieval on Official FEVER
4. Lightweight Metadata-Aware Lexical Reranking for Grounded FEVER Evidence Access
5. Improving Early Evidence Access on Official FEVER with Metadata-Aware Grounded Retrieval

## 2. Recommended Abstract Opening

This paper studies metadata-aware grounded retrieval for official FEVER evidence access. Starting from a fixed BM25 candidate retriever, we examine whether lightweight metadata-aware lexical cues can improve early strict gold-page access without expanding candidate coverage. On a disjoint 1000-query validation split, metadata-aware reranking improves early evidence access under a fixed retrieval budget, indicating that the gain comes from better rank allocation rather than broader retrieval.

## 3. Recommended Contributions

1. We recast the FEVER retrieval problem as metadata-aware grounded evidence access inside a fixed BM25 candidate pool.
2. We compare a family of lightweight metadata-aware lexical rerankers rather than centering the paper on a single title-overlap heuristic.
3. We show that exact title boost is the strongest aggressive family member, title overlap is the most conservative useful family member, and disambiguation-aware matching gives additional diagnosis-oriented support.
4. We add an efficiency-oriented evaluation package based on MRR, nDCG, and first-hit-rank summaries, showing that the gains are budget-preserving.
5. We provide diagnosis-oriented analysis showing which metadata cues help and which ones remain unreliable, including a negative result for a naive alias-based heuristic.

## 4. Recommended Method Naming

- family: `metadata-aware lexical reranking`
- task framing: `metadata-aware grounded retrieval`
- baseline: `routeA_bm25`
- conservative variant: `routeA_bm25_title_overlap`
- aggressive variant: `routeA_bm25_exact_title_boost`
- diagnosis variant: `routeA_bm25_disambiguation_title_match`
- negative control: `routeA_bm25_alias_redirect_match`

Avoid:

- naming the entire method family after `title overlap`
- implying that `alias_redirect_match` uses a true redirect table

## 5. Recommended Results Opening

We first evaluate a family of lightweight metadata-aware rerankers over a fixed BM25 candidate pool on the disjoint 1000 official FEVER validation split. The main pattern is consistent: the best variants improve early strict evidence access without changing strict Recall@10, indicating that the benefit comes from reranking already retrieved candidates rather than expanding coverage. Among the tested family members, exact title boost is the strongest aggressive variant, while title overlap remains the most conservative useful variant.

## 6. Recommended Limitations

1. The paper remains retrieval-only and does not validate a full verifier-generator pipeline.
2. The current alias-based heuristic is intentionally lightweight and does not rely on a clean redirect table, so its negative result should not be over-generalized.
3. The current efficiency framing is based on fixed-budget ranking metrics rather than a full end-to-end runtime benchmark.
4. The study is centered on official FEVER and should not be oversold as a universal claim about all grounded retrieval tasks.

## 7. Reviewer-Facing Defense

### Why is a single-task FEVER paper still defensible?

- Because the paper is tightly scoped to a concrete grounded evidence-access problem on an established benchmark.
- The contribution is not a giant system but a careful retrieval-stage study with a repaired disjoint split, nearby baselines, and diagnosis.

### Why is this not just another lexical tweak paper?

- Because the paper now studies a family of metadata-aware grounded cues, not only a single overlap heuristic.
- It also diagnoses which cues help, which ones are conservative, which ones are aggressive, and which ones are unreliable.

### Why does the efficiency claim remain safe?

- Because the candidate pool is fixed and top-10 coverage is unchanged.
- The gains are explicitly about earlier access to correct evidence within the same retrieval budget.

### What should we proactively concede?

- Exact title boost is the strongest tested family member.
- Title overlap is no longer the sole headline method.
- Alias-aware heuristics need stronger metadata resources before they can be claimed as robust.
