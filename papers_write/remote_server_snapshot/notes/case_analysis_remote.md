# Case Analysis

- Split used for this section: `disjoint 1000 validation`
- Strict improvement count: `49`
- Strict regression count: `2`
- Relaxed top1 delta: `+23`
- Strict top1 delta: `+47`

## Improvement Patterns

- `surface_title_match`: `29`
- `exact_gold_promotion`: `14`
- `disambiguation`: `6`

## Representative Interpretation

Across the disjoint validation set, the dominant pattern remains rank correction inside an already retrieved candidate set rather than broader candidate coverage. The improved cases still cluster around three interpretable behaviors:

- `surface_title_match`: the baseline top result is a nearby entity, person, or franchise page, while title overlap promotes the exact gold page title
- `exact_gold_promotion`: the gold page is already in top-k and title overlap moves it from rank 2 or 3 to rank 1
- `disambiguation`: the baseline lands on a related but ambiguous page, and title overlap resolves the target entity more directly

This is consistent with the intended contribution of the method: a lightweight reranking gain for evidence retrieval, not a change in candidate-set coverage and not a full end-to-end system improvement.

## Regression

Two strict regressions were observed in the disjoint validation set:

- `Hourglass was released 6 years after New Moon Shine.`  
  The baseline top result is the correct page `Hourglass (James Taylor album)`, while title overlap promotes `New Moon Shine`, which shares strong lexical relevance with the comparison statement.
- `There is a video game called Team Fortress 2.`  
  The baseline top result is already a valid strict hit through the multi-page evidence set, while title overlap promotes `Fortress 2 (video game)`, which is lexically close but not one of the official evidence pages used for strict matching.

These regressions are still title-driven and interpretable. They do not contradict the main gain pattern, but they show that surface lexical overlap can occasionally over-promote a non-gold page when multiple nearby entities or evidence pages exist.

## Comparison With Old Follow-up 1000

Relative to the older non-independent follow-up 1000 run:

- strict improvement count decreases from `51` to `49`
- strict regression count increases from `1` to `2`
- strict top1 delta decreases from `+50` to `+47`

The effect therefore becomes slightly more conservative under the disjoint validation split, but the qualitative conclusion is unchanged: title overlap still improves strict rank-1 evidence retrieval in a stable and interpretable way.
