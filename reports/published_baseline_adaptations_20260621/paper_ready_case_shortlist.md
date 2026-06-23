# Paper-Ready Case Shortlist

Automatically screened; verify wording against source evidence before manuscript insertion.

## Main Text

### agr_repairs_stale_answer: HOH-1024 / 1

- Question: What was the median income in Otago compared to the national median income?
- Gold: ['$39,100, compared with $41,500 nationally']
- TP-FP: Insufficient evidence
- AGR: $39,100, compared with $41,500 nationally
- Selection basis: TP incorrect, AGR exact-match correct, stale-tagged evidence present

### agr_avoids_relation_mismatched_distractor: HOH-1024 / 4

- Question: What percentage of people in Otago were born overseas, compared to the national percentage?
- Gold: ['23.8%, compared with 28.8% nationally']
- TP-FP: Insufficient evidence
- AGR: 23.8%, compared with 28.8% nationally
- Selection basis: AGR repair with an off-query candidate in candidate list

## Appendix

### tp_correct_agr_harm: TimeQA-500 / /wiki/Aurelio_Lampredi#P108#2

- Question: What was the name of the employer Aurelio Lampredi work for in late 1940s?
- Gold: ['Ferrari']
- TP-FP: Ferrari
- AGR: Isotta Fraschini
- Selection basis: TP exact-match correct, AGR incorrect

### gold_in_pool_candidate_extraction_failure: TimeQA-500 / /wiki/A._J._Casson#P463#0

- Question: A. J. Casson became a member of what organization or association in 1926?
- Gold: ['Group of Seven']
- TP-FP: Group of Seven
- AGR: Group of Seven
- Selection basis: Gold string in evidence but absent from candidate answers

### correct_arbitration_candidate_signal_override: TimeQA-500 / eval-000883

- Question: Today is Tuesday, January 14, 2020. The pulmonary valve regulates blood flow from what?
- Gold: ['the right ventricle to the lungs', 'right ventricle to the lungs', 'right ventricle to the lungs.']
- TP-FP: right ventricle
- AGR: right ventricle
- Selection basis: Top arbitration candidate exact-match correct but AGR final answer incorrect

### all_published_controls_harm_agr_retains: HOH-1024 / 11

- Question: What television network did Jill Whelan work for as an associate producer when she met her first husband, Brad St. John?
- Gold: ['KCOP-TV']
- TP-FP: KCOP-TV
- AGR: KCOP-TV
- Selection basis: TP-FP and AGR exact-match correct; all four new adaptation/control answers incorrect

### timeqa_boundary_published_repairs_agr_misses: TimeQA-500 / /wiki/Attaphol_Buspakom#P54#3

- Question: Which team did Attaphol Buspakom play for between Mar 1995 and Dec 1995?
- Gold: ['Pahang FA', 'Thailand national football team']
- TP-FP: Insufficient evidence
- AGR: Insufficient evidence
- Selection basis: Published baseline correct, AGR incorrect
