# Overlap Check Report

## Files

- `data/processed/fever_official/shared_task_dev_verifiable_500.jsonl`
- `data/processed/fever_official/shared_task_dev_verifiable_1000.jsonl`

## Comparison Key

- Primary key: `id`
- Secondary sanity keys: `claim` and `claim + label`

## Method

The two subsets were generated from the same source file (`shared_task_dev.jsonl`) with the same preprocessing filter (`--require-evidence`) and the same random seed (`--seed 42`), while only changing `--sample-size` from `500` to `1000`.

Under the current ChronoRAG sampling implementation, both subsets are produced through Python's `random.sample(...)` on the same filtered population order. In Python 3.10, when the same RNG seed is reused on the same population, the `k=500` sample is a prefix-subset of the `k=1000` sample. Therefore the 500-query tuning subset is nested inside the 1000-query validation subset by construction.

## Result

- 500 subset size: `500`
- 1000 subset size: `1000`
- Overlap count by `id`: `500`
- Overlap ratio vs. 500 subset: `1.000`
- Overlap ratio vs. 1000 subset: `0.500`

## Representative Overlap Items

- `95417` | SUPPORTS | `South Island is referred to as the "mainland" by South Island residents.`
- `42213` | SUPPORTS | `John Deighton had no choice but to pursue other lines of work.`
- `223349` | REFUTES | `The principal photography of The Disaster Artist (film) started on the 9th.`
- `135340` | REFUTES | `Moves Like Jagger is on Overexposed.`
- `214262` | SUPPORTS | `DJ Quik is a recording artist.`
- `209872` | REFUTES | `In a Lonely Place is only a book without a script.`
- `155212` | SUPPORTS | `Taran Killam is a person.`
- `5513` | SUPPORTS | `Shadowhunters premiered in 2016.`
- `71072` | SUPPORTS | `Richard Kuklinski has a wife and child.`
- `93621` | REFUTES | `The Armenian Genocide was the Ottoman government's systematic extermination of 1.5 million Jews.`

## Interpretation

This overlap is not acceptable if the 1000-query run is described as an independent validation set. Because the 500-query tuning subset is fully contained in the 1000-query validation subset, the current 1000-query result is better described as a larger follow-up evaluation on a partially reused sample, not a fully disjoint validation.

## Minimal-Cost Repair

The lowest-cost repair is to create a disjoint validation subset from the same official FEVER dev verifiable pool:

1. Keep the 500-query subset as the tuning set.
2. Build a new 1000-query validation subset by excluding all 500 tuning `id`s.
3. Fix the method at the current best setting: `bm25_weight=0.5`, `title_weight=0.5`.
4. Re-run only the 1000-query evaluation on the disjoint subset, reusing the existing official corpus and BM25 index.

This repair is sufficient for a stronger independence claim and is much cheaper than re-running the full development set immediately.

## Conclusion

`need disjoint validation`
