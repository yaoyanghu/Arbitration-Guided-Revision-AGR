# FEVER Metadata Family v1 Result Summary

## Scope

This report summarizes the completed low-risk metadata-aware family analysis over the existing disjoint 1000 FEVER run.

Inputs reused:

- `runs/fever_official_route_a_disjoint_1000/retrieval_results.jsonl`
- `runs/fever_official_route_a_disjoint_1000/predictions.jsonl`

No full-dev run, no dense retriever, and no Route B or Route C component was used.

## 1. Core Family Results

| variant | strict R@1 / R@5 / R@10 | relaxed R@1 / R@5 / R@10 | strict improved / regressed |
| --- | --- | --- | ---: |
| routeA_bm25 | 0.368 / 0.627 / 0.720 | 0.737 / 0.883 / 0.918 | 0 / 0 |
| title_overlap | 0.415 / 0.680 / 0.720 | 0.760 / 0.895 / 0.918 | 49 / 2 |
| exact_title_boost | 0.544 / 0.708 / 0.720 | 0.801 / 0.904 / 0.918 | 192 / 16 |
| alias_redirect_match | 0.357 / 0.626 / 0.720 | 0.733 / 0.883 / 0.918 | 1 / 12 |
| disambiguation_title_match | 0.378 / 0.622 / 0.720 | 0.749 / 0.887 / 0.918 | 22 / 12 |

## 2. Efficiency Metrics

### Strict efficiency

| variant | MRR | nDCG@5 | nDCG@10 | mean first-hit rank |
| --- | ---: | ---: | ---: | ---: |
| routeA_bm25 | 0.478 | 0.502 | 0.534 | 2.575 |
| title_overlap | 0.520 | 0.551 | 0.567 | 2.078 |
| exact_title_boost | 0.617 | 0.636 | 0.641 | 1.451 |
| alias_redirect_match | 0.472 | 0.497 | 0.530 | 2.594 |
| disambiguation_title_match | 0.483 | 0.505 | 0.538 | 2.568 |

### Relaxed efficiency

| variant | MRR | nDCG@5 | nDCG@10 | mean first-hit rank |
| --- | ---: | ---: | ---: | ---: |
| routeA_bm25 | 0.799 | 0.748 | 0.809 | 1.563 |
| title_overlap | 0.817 | 0.751 | 0.817 | 1.415 |
| exact_title_boost | 0.846 | 0.787 | 0.839 | 1.282 |
| alias_redirect_match | 0.797 | 0.747 | 0.808 | 1.566 |
| disambiguation_title_match | 0.808 | 0.755 | 0.816 | 1.500 |

## 3. Interpretation

### Which variant is strongest?

- `exact_title_boost` is the strongest tested variant by a large margin.
- It improves strict top1 from `368` to `544`, and also gives the best MRR, nDCG, and mean first-hit rank.

### Which variant is most conservative?

- `title_overlap` remains the most conservative useful variant.
- It improves strict top1 from `368` to `415` with only `2` strict regressions.
- It remains clearly weaker than `exact_title_boost`, but it is much safer.

### Which new variant adds meaningful support?

- `disambiguation_title_match` adds modest positive evidence.
- It improves strict top1 from `368` to `378`, and its improved cases are dominated by `type_word` and `parenthetical_surface` claims.
- This is useful for the new diagnosis framing even though it is not the strongest reranker.

### Which new variant does not currently help?

- `alias_redirect_match` in its current heuristic form does not help.
- It drops strict top1 from `368` to `357` and causes more regressions than improvements.
- So the paper should not claim that alias-aware metadata cues are already solved; instead, this variant is valuable as a negative result showing that naive alias heuristics are noisy without a clean redirect table.

## 4. Initial Claim-Type Diagnosis

### title_overlap

- improved claims are mostly `plain_entity_surface`
- smaller but real gains also appear on `type_word` claims
- regressions are rare and mostly plain lexical confusions

### exact_title_boost

- strongest gains are again concentrated on `plain_entity_surface`
- it also helps many type-word claims
- regressions are still limited, but noticeably higher than title_overlap

### disambiguation_title_match

- improved cases are dominated by `type_word` and `parenthetical_surface`
- this is the clearest evidence that disambiguation-sensitive metadata cues are a real sub-problem in FEVER evidence ranking

### alias_redirect_match

- current improvements are negligible
- current regressions show that weak alias extraction from lead text is too noisy to serve as a paper headline method

## 5. Budget-Preserving Efficiency Claim

The current results support the following claim:

- metadata-aware reranking improves early evidence access under a fixed BM25 retrieval budget

What is supported:

- candidate generation does not change
- top-10 strict coverage remains unchanged
- early-rank access improves
- extra computation is limited to lightweight string-level scoring over already retrieved candidates

What is not yet supported:

- a strong wall-clock runtime benchmark
- evidence sentence coverage under fixed page budget

The sentence-coverage metric remains a TODO because the processed disjoint FEVER file is not present in this local workspace.

## 6. Paper-Facing Bottom Line

The upgraded short-paper story is now:

- not `title overlap is best`
- but `metadata-aware grounded retrieval helps under fixed retrieval budget`

Within that story:

- `exact_title_boost` is the strongest aggressive metadata-aware lexical variant
- `title_overlap` is the best conservative variant
- `disambiguation_title_match` gives diagnosis-oriented support for a type-sensitive metadata story
- `alias_redirect_match` currently works better as a negative control than as a positive contribution
