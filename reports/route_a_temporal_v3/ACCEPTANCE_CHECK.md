# Acceptance Check

## README Acceptance Criteria

1. End-to-end small real subset run: PASS
2. Temporal signal measurably changes ranking: PASS
3. Updated evidence beats retrieval-only baseline: PASS
4. Reliability helps some conflict cases: PASS
5. Per-query inspectable artifacts exist: PASS

## Gate Thresholds

- min_query_count: `54`
- min_temporal_changed: `8`
- min_reliability_helped: `6`
- min_pairwise_gain: `0.100`

## Metrics Snapshot

```json
{
  "query_count": 54,
  "weights": {
    "bm25_weight": 0.6,
    "temporal_weight": 0.25,
    "reliability_weight": 0.15
  },
  "stages": {
    "retrieval_only": {
      "query_count": 54,
      "preferred_top1_rate": 0.5370370370370371,
      "pairwise_preference_success_rate": 0.6666666666666666,
      "mean_preferred_rank": 1.5,
      "preferred_mrr": 0.7623456790123457,
      "stale_wins_count": 18
    },
    "temporal_only": {
      "query_count": 54,
      "preferred_top1_rate": 0.7037037037037037,
      "pairwise_preference_success_rate": 0.7962962962962963,
      "mean_preferred_rank": 1.3333333333333333,
      "preferred_mrr": 0.8456790123456791,
      "stale_wins_count": 11
    },
    "temporal_plus_reliability": {
      "query_count": 54,
      "preferred_top1_rate": 0.8148148148148148,
      "pairwise_preference_success_rate": 0.8333333333333334,
      "mean_preferred_rank": 1.1851851851851851,
      "preferred_mrr": 0.9074074074074074,
      "stale_wins_count": 9
    }
  },
  "acceptance_snapshot": {
    "temporal_changed_ranking_count": 9,
    "reliability_helped_count": 8,
    "final_better_than_retrieval_count": 17
  }
}
```