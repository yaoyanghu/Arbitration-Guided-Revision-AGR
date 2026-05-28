# Dataset Status

## Active

- `HotpotQA distractor pilot`
  - status: `completed first pilot round`
  - role: answer-level backbone verification

## Formal Active

- `HOH`
  - status: `formal launched and completed`
  - role: target main-result dataset
  - frozen formal slice: `1024 queries`
  - latest readout: `full_model` beats both `no_temporal` and `no_conflict` on the formal run

- `TempRAGEval`
  - status: `formal launched and completed`
  - role: temporal-sensitive auxiliary validation
  - frozen formal slice: `1244 queries`
  - latest readout: `full_model` still beats `no_temporal`, while conflict/source remain neutral

- `DynamicQA temporal`
  - status: `fallback connected; pilot completed`
  - role: temporary public temporal-sensitive fallback
  - caution: raw context contains `[ENTITY]` placeholders, so answer-level validation is limited

- `ChronoQA`
  - status: `raw downloaded`
  - role: future temporal reasoning extension asset
  - caution: nested narrative structure needs dedicated normalization before pilot use

## Preserved Legacy

- `FEVER official retrieval`
  - status: `preserved`
  - role: controlled auxiliary retrieval benchmark

- `Route A`
  - status: `preserved`
  - role: diagnostic temporal-conflict stress set

- `Route B`
  - status: `frozen`
  - role: analysis layer only

## Formal Status

- overall: `formal runs completed; summarization in progress`
- reason:
  - HOH formal preserves the temporal and conflict gains from pilot
  - TempRAGEval formal preserves the temporal gain from pilot
  - source gains remain unproven and are no longer part of the main claim
