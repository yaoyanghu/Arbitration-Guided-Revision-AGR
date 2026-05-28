# Route A Temporal v2 Subset Manifest

## Purpose

This manifest records the hardened Route A v2 subset that expands the v1 curated acceptance slice into a larger temporal-conflict evaluation set.

## 1. Sample Count

- total queries: `30`
- total corpus documents: `30`
- construction pattern: `10 entities x 3 query styles`

## 2. Case Type Distribution

- `clear_updated_vs_stale`: `10`
- `reliability_sensitive_conflict`: `10`
- `mixed_ambiguous_case`: `10`

## 3. What Each Case Type Covers

### Clear Updated-vs-Stale

- one updated preferred candidate
- one older stale candidate
- one same-era conflicting candidate

### Reliability-Sensitive Conflict

- same-year conflict is lexically strong
- temporal signal alone may still leave the conflicting candidate competitive
- reliability prior is expected to rescue part of these cases

### Mixed / Ambiguous

- stale wording remains strong in raw retrieval
- updated answer should still be preferred after temporal and reliability reranking when the case is solvable
- some cases may remain hard by design

## 4. Comparison to v1

v1 characteristics:

- `12` queries
- acceptance-oriented
- field-focused query types such as `current_role`, `current_affiliation`, `release_status`, `rename_status`, `current_credit`, `current_status`, `milestone_status`

v2 additions:

- explicit balanced case families instead of only field-style variation
- more same-year conflict cases
- more reliability-sensitive conflicts
- more mixed ambiguous cases that keep raw retrieval competitive

## 5. Stable Fields and Evaluation Contract

The following remain stable from v1 to v2:

- query text field
- query time
- entity
- focus attribute
- preferred doc id
- stale doc ids
- candidate doc ids
- source type
- evidence time
- temporal status
- per-query artifact format
- retrieval-only / temporal-only / temporal-plus-reliability evaluation split

## 6. Why v2 Is a Hardening Step

This subset is not just larger than v1.

It is harder because:

- retrieval-only no longer gets a near-trivial win
- stale and conflicting candidates are deliberately more competitive
- temporal and reliability modules now need to produce measurable ranking changes to pass the gate
