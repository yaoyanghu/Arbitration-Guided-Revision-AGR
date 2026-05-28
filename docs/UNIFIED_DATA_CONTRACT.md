# Unified Data Contract

## Purpose

The upgraded `New_ChronoRAG` mainline needs one common schema across:

- the future main public answer-level dataset
- FEVER official retrieval
- legacy Route A temporal-conflict diagnostic slices

## Query Record

Each processed query record should support:

```json
{
  "id": "string",
  "query": "string",
  "answers": ["string"],
  "query_time": "optional int or string",
  "metadata": {
    "dataset": "string",
    "split": "string",
    "query_type": "optional string"
  },
  "gold_evidence_titles": ["optional string"],
  "gold_evidence_texts": ["optional string"]
}
```

## Corpus Record

Each corpus record should support:

```json
{
  "doc_id": "string",
  "title": "string",
  "text": "string",
  "source": "optional string",
  "source_type": "optional string",
  "timestamp": "optional string",
  "url": "optional string",
  "metadata": {}
}
```

## Method-Visible Fields

Allowed as direct method inputs:

- `query`
- `answers` only for evaluation, not generation-time scoring
- `query_time` when naturally present in the query or dataset metadata
- `title`
- `text`
- `source`
- `source_type` if naturally available
- `timestamp`
- `url`

## Evaluation-Only Fields

These may exist in legacy or diagnostic datasets but must not become default mainline inputs:

- `preferred_doc_id`
- `stale_doc_ids`
- `temporal_status`
- `preferred_title`
- `case_type`
- other construction-side labels injected for controlled stress testing

## Compatibility Mapping

### FEVER official retrieval

- `claim` maps to `query`
- label and evidence fields stay evaluation-side

### Route A temporal slices

- `query` stays `query`
- `query_time` may remain available
- `preferred_doc_id`, `stale_doc_ids`, `case_type`, `temporal_status` stay evaluation-side only

### Future main public dataset

- should map directly into this contract without task-specific leakage labels

## Output Contract

The upgraded answer-level pipeline should output:

```json
{
  "query_id": "string",
  "query": "string",
  "predicted_answer": "string",
  "selected_evidence": [
    {
      "doc_id": "string",
      "title": "string",
      "text": "string",
      "score": 0.0,
      "citation_id": "[1]"
    }
  ],
  "arbitration_trace": {
    "temporal": {},
    "conflict": {},
    "reliability": {}
  }
}
```

## Rule

The new mainline is allowed to reuse legacy datasets, but it is not allowed to treat synthetic control labels as first-class model inputs.
