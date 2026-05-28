# New_ChronoRAG Execution Contract

## Reviewer Audit Prompt

Please act as a strict but constructive internal reviewer for the current New_ChronoRAG paper package.

Requirements:
1. Use only real repository files, formal runs, and revised paper-facing notes.
2. Evaluate the paper on:
   - novelty
   - methodological clarity
   - evaluation completeness
   - claim-evidence alignment
   - likely reviewer attacks
   - venue fit
3. Output:
   - the 5 most likely reviewer attacks
   - whether each attack has already been neutralized by experiments or wording
   - which remaining issue is still the most dangerous
   - whether the paper is ready to submit
   - if not, the smallest remaining patch

Output file:
- `reports/formal_mainline/review/final_reviewer_style_audit.md`

Tone:
- no empty praise
- no cosmetic optimism
- write like a real internal reviewer deciding whether submission is justified now

## Current Task Prompt

Continue executing `New_ChronoRAG`, but remain in `paper closeout mode`.

Current ground-truth state:
1. formal mainline is frozen as:
   - retrieval
   - temporal-aware answer extraction
   - conflict-aware evidence arbitration
   - citation-aware answer output
2. `source/reliability` is no longer part of the validated main contribution
3. formal runs are completed:
   - `formal_hoh1024_20260327`
   - `formal_temprageval1244_20260327`
4. `FEVER` remains a controlled auxiliary retrieval benchmark
5. `Route B` remains frozen as analysis layer only
6. `ChronoQA` remains a future asset, not part of the mainline

Execution order:
1. keep the formal claim frozen
2. remove or rewrite any stale wording that still presents `source` as a proven core gain
3. generate paper-ready tables, case studies, error taxonomy, and writing-pack materials
4. generate a reviewer-style internal audit for the current formal package
5. do not reopen exploratory experimentation unless a formal configuration error is discovered

Hard constraints:
- do not reopen pre-formal gating
- do not add new datasets
- do not reintroduce Route B
- do not expand the baseline matrix
- do not claim `source` as validated core contribution
- do not present pilot numbers as formal

## Unattended Mode Prompt

The user may be offline. Keep moving with the most conservative paper-closeout path.

Default permissions:
- small document rewrites
- table-pack generation
- case-study extraction from formal outputs
- error-taxonomy summarization
- reviewer-audit drafting
- wording cleanup for claim consistency
- local sync and result-pack organization

When small issues appear:
1. fix them automatically if possible
2. downgrade to the safer implementation if needed
3. record assumptions in markdown and continue
4. do not stop the pipeline for minor cleanup issues

Only stop and ask if:
1. new credentials or external permissions are required
2. a formal result appears corrupted or self-contradictory
3. a major paper-direction fork appears that cannot be resolved from existing formal evidence

Non-negotiable rules:
- do not call pilot results formal
- do not revive frozen routes to make the story look bigger
- do not overclaim conflict/source evidence
- do not print secrets, passwords, tokens, or server credentials anywhere
- every claimed completion must have files, run outputs, or markdown artifacts as evidence
