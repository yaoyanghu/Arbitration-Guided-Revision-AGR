# Method Overview Draft

The formal mainline consists of four layers:

1. stronger lexical retrieval to gather a small evidence candidate pool
2. temporal-aware answer extraction that uses query-time and relation-aware constraints to avoid obvious retrospective year mistakes
3. conflict-aware evidence arbitration that compares same-title, value-mismatched evidence and prefers fresher consistent candidates
4. citation-aware answer output that returns a final answer together with selected evidence and citations

The method intentionally avoids direct use of construction-side labels such as `temporal_status`, `preferred_doc_id`, or `stale_doc_ids`. These fields remain evaluation-only. The source/reliability path remains implemented but is not claimed as a validated core contribution because it did not show independent gains in the final gating and formal runs.
