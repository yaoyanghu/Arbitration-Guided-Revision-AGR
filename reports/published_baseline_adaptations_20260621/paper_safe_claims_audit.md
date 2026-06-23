# Paper-Safe Claims Audit

## Allowed

- AGR has the highest mean EM (34.88%) and F1 (47.25%) across the three fixed-pool datasets.
- AGR exceeds the strongest non-AGR baseline, TP-FP RAG, by 6.00 EM points and 9.99 F1 points on the unweighted three-dataset mean.
- AGR has positive net repair on HOH (+79), TempRAGEval (+108), and TimeQA (+8).
- All four new adaptation/control prediction sets pass frozen-evidence and no-extra-retrieval verification: True.
- Legacy fixed-pool artifacts contain no evidence outside their frozen per-query pools: True.

## Forbidden or Too Strong

- Do not claim official reproduction of RARR, FaithfulRAG, or CRAG.
- Do not claim CRAG equivalence: corrective retrieval is deliberately absent.
- Do not claim FaithfulRAG method fidelity beyond an inspired fact-support/conflict control.
- Do not claim universal superiority: AGR's TimeQA EM gain is only +1.60 points.
- Do not make precise end-to-end deployment overhead claims from legacy artifacts; 15 method-dataset runtime rows have unlogged input-token or LLM-call fields.
- Do not describe ArchivalQA as a complete baseline grid; only three existing artifacts were evaluated offline.
