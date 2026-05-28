# Route A Mainline Wording Pack

## Main Claim Wording

Route A shows that lightweight temporal and source-reliability reranking can consistently improve preferred-evidence ranking over retrieval-only BM25 on balanced temporal-conflict slices without changing the underlying retrieval backbone.

## Results Opening

On the 54-query Route A v3 mainline slice, the full Route A pipeline improves preferred top1 from 0.537 to 0.815 and pairwise preference success from 0.667 to 0.833. The same ordering also holds on a separate 18-query held-out slice, where the full pipeline reaches 0.833 preferred top1 and 0.889 pairwise preference success.

## Stratified Readout Wording

The clearest gains appear where retrieval-only is weakest. Clear updated-vs-stale cases are already near-solved by BM25, while reliability-sensitive and especially mixed ambiguous cases create the main room for improvement. The temporal signal improves ranking behavior, and the reliability prior further helps same-year conflict cases without changing the task contract.

## Error Taxonomy Wording

The main failure mode is not complete retrieval collapse but lexical stickiness of stale evidence in mixed ambiguous cases. These cases often preserve strong older wording, so the preferred updated evidence remains rank-competitive but not always rank-dominant.

## Case Study Wording

Representative reliability-sensitive examples show the value of a small source prior when same-year conflicting candidates reuse much of the query wording. Representative mixed cases show the remaining limitation: temporal cues and source priors help, but older state descriptions can still anchor the ranking.

## Route B Wording

Route B should appear only as a conflict-focused analysis layer. It may be used to visualize or inspect relation structure around hard Route A cases, but it should not be described as part of the Route A main method or as an independent method contribution.

## Forbidden Wording

- Do not describe Route B as a co-equal method line.
- Do not imply Route C.
- Do not claim broad benchmark-level generalization.
- Do not describe the hold-out slice as a new benchmark.
