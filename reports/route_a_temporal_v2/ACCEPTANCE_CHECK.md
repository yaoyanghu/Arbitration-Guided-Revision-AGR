# Acceptance Check

## README Acceptance Criteria

1. End-to-end small real subset run: PASS
2. Temporal signal measurably changes ranking: PASS
3. Updated evidence beats retrieval-only baseline: PASS
4. Reliability helps some conflict cases: PASS
5. Per-query inspectable artifacts exist: PASS

## Gate Thresholds

- min_query_count: `30`
- min_temporal_changed: `5`
- min_reliability_helped: `3`
- min_pairwise_gain: `0.050`

## Metrics Snapshot

```json
{
  "query_count": 30,
  "weights": {
    "bm25_weight": 0.6,
    "temporal_weight": 0.25,
    "reliability_weight": 0.15
  },
  "stages": {
    "retrieval_only": {
      "query_count": 30,
      "preferred_top1_rate": 0.5,
      "pairwise_preference_success_rate": 0.6666666666666666,
      "mean_preferred_rank": 1.5333333333333334,
      "preferred_mrr": 0.7444444444444446,
      "stale_wins_count": 10
    },
    "temporal_only": {
      "query_count": 30,
      "preferred_top1_rate": 0.6666666666666666,
      "pairwise_preference_success_rate": 0.8,
      "mean_preferred_rank": 1.3666666666666667,
      "preferred_mrr": 0.8277777777777778,
      "stale_wins_count": 6
    },
    "temporal_plus_reliability": {
      "query_count": 30,
      "preferred_top1_rate": 0.8,
      "pairwise_preference_success_rate": 0.8,
      "mean_preferred_rank": 1.2,
      "preferred_mrr": 0.9,
      "stale_wins_count": 6
    }
  },
  "acceptance_snapshot": {
    "temporal_changed_ranking_count": 5,
    "reliability_helped_count": 5,
    "final_better_than_retrieval_count": 10
  }
}
```