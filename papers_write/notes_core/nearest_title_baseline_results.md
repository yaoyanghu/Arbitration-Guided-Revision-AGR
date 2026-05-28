# Nearest Title-Aware Lexical Baseline Results

## Purpose

This analysis answers the reviewer-style question raised in [reviewer_gap_audit.md](/D:/HUYAOYANG/Work/ChronoRAG/notes/reviewer_gap_audit.md): is token-level title overlap actually necessary, or would a simpler title-aware lexical heuristic already recover the same gain?

## Compared Systems

- `routeA_bm25`
- `routeA_bm25_exact_title_boost`
- `routeA_bm25_title_overlap`

Shared setting:
- dataset: official FEVER
- validation split: disjoint 1000
- candidate pool: unchanged BM25 retrieval candidates from [retrieval_results.jsonl](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000/retrieval_results.jsonl)
- weights for both title-aware methods: `bm25_weight=0.5`, `title_weight=0.5`

Comparator definition:
- `exact_title_boost` fires a binary title-aware feature when the page title, or its de-parenthesized base title, appears as an exact contiguous phrase in the claim text.
- This is therefore very close to an `exact page-title match boost`, with a light title normalization backoff for parenthetical titles.

## Main Results

Strict evaluation:
- BM25: `R@1=0.368`, `R@5=0.627`, `R@10=0.720`, `top1=368`
- BM25 + exact title boost: `R@1=0.544`, `R@5=0.708`, `R@10=0.720`, `top1=544`
- BM25 + title overlap: `R@1=0.415`, `R@5=0.680`, `R@10=0.720`, `top1=415`

Relaxed evaluation:
- BM25: `R@1=0.737`, `R@5=0.883`, `R@10=0.918`, `top1=737`
- BM25 + exact title boost: `R@1=0.801`, `R@5=0.904`, `R@10=0.918`, `top1=801`
- BM25 + title overlap: `R@1=0.760`, `R@5=0.895`, `R@10=0.918`, `top1=760`

## Direct Answer

On the current disjoint 1000 validation split, `title overlap` is **not** better than the simpler nearest title-aware lexical baseline.

- Under strict evaluation, exact title boost beats title overlap by `129` top1 hits.
- Under relaxed evaluation, exact title boost beats title overlap by `41` top1 hits.
- Against raw BM25, exact title boost yields `+176` strict top1 hits, while title overlap yields `+47`.

So the current evidence does **not** support the claim that token-level title overlap is necessary as the main method. A stricter and more reviewer-safe interpretation is:

- title-aware lexical reranking clearly helps
- but the simplest exact-title-style heuristic is currently stronger than token-level overlap on this split

## Where Exact Title Boost Wins

Exact title boost is especially strong when:
- the claim explicitly contains the gold page title as a clean contiguous phrase
- BM25 retrieves near neighbors such as list pages, history pages, franchise pages, or related entities ahead of the exact page
- the gold page is already in top-k, and a binary phrase hit is enough to move it to rank 1

Representative examples from [exact_title_only_wins_over_overlap_cases.jsonl](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/exact_title_only_wins_over_overlap_cases.jsonl):
- `Daenerys Targaryen is a character in a George R. R. Martin series.`  
  baseline top1: `Viserys Targaryen`  
  exact title top1: `Daenerys Targaryen`  
  title overlap top1: `Viserys Targaryen`
- `Yandex is a website.`  
  baseline top1: `Yandex.Direct`  
  exact title top1: `Yandex`  
  title overlap top1: `Yandex.Direct`
- `Donald Duck typically wears a cap.`  
  baseline top1: `The Oregon Duck`  
  exact title top1: `Donald Duck`  
  title overlap top1: `The Oregon Duck`

These are strong disambiguation wins that a phrase-level exact title hit captures immediately.

## Where Title Overlap Still Helps

Title overlap still wins on some cases where exact-title boost is too brittle.

It helps when:
- the gold page contains parenthetical disambiguation not copied exactly in the claim
- the claim mentions most of the title tokens but not as an exact contiguous surface form
- the gold page should beat a shorter near-duplicate or base-title page

Representative examples from [title_overlap_only_wins_over_exact_cases.jsonl](/D:/HUYAOYANG/Work/ChronoRAG/runs/fever_official_route_a_disjoint_1000_nearest_title_baseline/title_overlap_only_wins_over_exact_cases.jsonl):
- `Cheese in the Trap (TV series) is a television series.`  
  exact title top1: `Cheese in the Trap`  
  title overlap top1: `Cheese in the Trap (TV series)`
- `Victor Frankenstein is only a romance film.`  
  exact title top1: `Frankenstein (2004 film)`  
  title overlap top1: `Victor Frankenstein (film)`
- `Meteora is an album.`  
  exact title top1: `Meteora (disambiguation)`  
  title overlap top1: `Meteora (album)`

So overlap is not useless. It captures some disambiguation-sensitive cases that binary exact title hits miss.

## Tradeoff

Exact title boost is stronger in aggregate, but it is also less conservative:
- exact title boost: `192` strict improvements, `16` strict regressions
- title overlap: `49` strict improvements, `2` strict regressions

This means:
- if the optimization target is pure strict top1 gain, exact title boost is currently the stronger lexical reranker
- if the optimization target is a smaller and more conservative reranking change, title overlap is safer but weaker

## Paper Implication

For the current paper line, the reviewer challenge is real and now empirically answered:

- `title overlap` should no longer be presented as the strongest lightweight title-aware lexical method
- the stronger claim is that **title-aware lexical reranking** improves FEVER evidence page ranking
- among the currently tested lightweight heuristics, the nearest simpler baseline `exact_title_boost` is actually better than token-level overlap on the disjoint 1000 split

If the paper keeps the title-overlap method as the headline method, it will now be vulnerable to reviewer criticism. The cleaner path is to either:
- shift the main method to the stronger exact-title-style reranker, or
- explicitly reposition title overlap as a more conservative but weaker alternative
