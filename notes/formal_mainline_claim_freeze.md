# Formal Mainline Claim Freeze

## Frozen Main Claim

The upgraded New_ChronoRAG mainline should now be described as:

- `Conflict-Aware Temporal Faithful RAG`
- realized in practice as:
  - stronger retrieval
  - temporal-aware answer extraction
  - conflict-aware evidence arbitration
  - citation-aware answer output

## What Is Supported

- HOH formal shows that the full model beats `no_temporal`
- HOH formal shows that the full model beats `no_conflict`
- TempRAGEval formal confirms that temporal-aware extraction is not a pilot-only artifact

## What Is Not Supported

- source/reliability as an independently validated main contribution
- Route B as a main method contribution
- ChronoQA as current mainline evidence

## Safe Paper Wording

- temporal-aware faithful RAG with conflict-aware arbitration
- answer-level grounded generation with evidence citations
- temporal auxiliary validation on TempRAGEval
- controlled retrieval auxiliary evaluation on FEVER
