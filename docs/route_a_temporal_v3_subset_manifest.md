# Route A Temporal v3 Subset Manifest

## Scope

- subset name: `route_a_temporal_v3_mainline`
- entity count: `18`
- query count: `54`
- corpus document count: `54`

## Case Type Distribution

- `clear_updated_vs_stale`: `18`
- `reliability_sensitive_conflict`: `18`
- `mixed_ambiguous_case`: `18`

## Source Slice Composition

- inherited from v2 hardened slice: `10` entities
- inherited from held-out hard slice: `8` entities

## Updated Source Type Distribution

- `official_record`: `13`
- `encyclopedic_current`: `5`

## Focus Distribution

- `office`: `5`
- `name`: `4`
- `club`: `2`
- `launch_status`: `2`
- `ranking`: `2`
- `release`: `2`
- `milestone`: `1`

## Contract Stability

The v3 subset keeps the same Route A contract as v2:

- same query schema
- same evidence fields
- same preferred-vs-stale evaluation target
- same temporal and reliability scoring logic
- same three-stage evaluation:
  - retrieval-only
  - temporal-only
  - temporal + reliability

## Why This v3 Slice Is Stronger Than v2

- larger than the v2 hardened slice
- still balanced across the three case types
- built from two already-real Route A slices instead of introducing a new problem definition
- suitable as a reusable mainline Route A checkpoint
