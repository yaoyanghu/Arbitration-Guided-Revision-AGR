# Route A Temporal v4 Manifest

## Split Summary

| split | event_count | query_count | clear | reliability-sensitive | mixed |
| --- | ---: | ---: | ---: | ---: | ---: |
| dev | 20 | 60 | 20 | 20 | 20 |
| test | 20 | 60 | 20 | 20 | 20 |
| total | 40 | 120 | 40 | 40 | 40 |

## Source / Reliability Marking

- `official_record` and `encyclopedic_current` are the two positive updated-source buckets
- `archival_news` marks older stale evidence
- `blog` marks noisy same-year conflict evidence
- reliability is encoded through `source_type` and `reliability_bucket`

## Stale / Updated Marking

Each event contains three evidence roles:

- `updated`
- `stale`
- `conflicting`

These are encoded through:

- `temporal_status`
- `evidence_time`
- query-side `preferred_doc_id`
- query-side `stale_doc_ids`

## Contract Stability

Route A v4 keeps the same task contract as v3:

- same three case types
- same preferred-vs-stale objective
- same lightweight temporal scoring family
- same lightweight reliability prior family
- same retrieval-only BM25 backbone

## Independence Note

The v4 split is independent of the frozen v3 hold-out slice and is stored in new v4 files only:

- [route_a_temporal_v4_dev.jsonl](D:/HUYAOYANG/Work/ChronoRAG/data/processed/route_a_temporal_v4_dev.jsonl)
- [route_a_temporal_v4_test.jsonl](D:/HUYAOYANG/Work/ChronoRAG/data/processed/route_a_temporal_v4_test.jsonl)
