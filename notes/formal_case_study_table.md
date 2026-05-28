# Formal Case Study Table

## Temporal Success Cases

| case | query | gold answer | predicted answer | selected evidence / citations | why success |
| --- | --- | --- | --- | --- | --- |
| T1 | When was the time the Dodgers played the Yankees in the World Series? | 1981 | 1981 `[1]` | `[1]` cites a retrospective sentence listing `1977, 1978, 1981`; the temporal constraint still selects `1981` rather than the distractor `1998` mention. | The temporal answer selector ignores the salient retrospective year and picks the query-relevant event year. |
| T2 | When was the last time the Dodgers played the Yankees in the World Series as of 1981? | 1981 | 1981 `[1]` | `[1]` and `[2]` both cite evidence mentioning multiple World Series years. | The `as of` constraint preserves the latest valid year not exceeding the query time. |
| T3 | When was the last time the Dodgers played the Yankees in the World Series as of 1991? | 1981 | 1981 `[1]` | Evidence contains multiple years; the answer still resolves to `1981`. | The model now prefers the latest temporally admissible answer rather than the most recent surface year mention. |

## Conflict Success Cases

| case | query | gold answer | predicted answer | selected evidence / citations | why success |
| --- | --- | --- | --- | --- | --- |
| C1 | How many names of Radha are mentioned in the fifth chapter of the Sanskrit scripture "Narada Pancharatra" under the title "Shri Radha Saharsnama Strotam"? | 1008 | 1008 `[1]` | `[1]` gives `1008`; `[2]` is stale and says `more than 1000`. | Conflict arbitration prefers the fresher same-title evidence with a sharper value match. |
| C2 | When did freeze dried candy see a major surge in popularity? | 2020 | 2020 `[1]` | Single current evidence sentence is selected, with stale alternatives suppressed. | Conflict-aware selection keeps the freshest answer-bearing sentence when same-topic evidence competes. |
| C3 | What type of spirit did José Bedia Valdés receive at his initiation into Palo? | mpungu | mpungu `[1]` | `[1]` says `mpungu`; `[2]` stale evidence says `nganga` spirit. | Same-title, value-mismatched evidence is now resolved in favor of the fresher, internally consistent answer. |

## Representative Failure Cases

| case | query | gold answer | predicted answer | selected evidence / citations | why failure |
| --- | --- | --- | --- | --- | --- |
| F1 | What percentage of people at least 15 years old had a bachelor's or higher degree? | 19.9% | 10.0% `[1]` | `[1]` comes from `Tikipunga`, not `Otago`. | The system still sometimes picks the wrong entity/evidence family under near-duplicate demographic sentences. |
| F2 | Who is the current Master of the Horse? | The Lord Ashton of Hyde | Lord de Mauley `[2]` | Both current and stale same-title sentences are selected. | The final answer extractor can still copy the stale second citation even when the correct current sentence is present. |
| F3 | For which NFL season did the Dallas Cowboys win their most recent Super Bowl as of January 31, 2000? | 1995 | 1993 `[1]` | Evidence mentions `1992, 1993, 1995`; the model outputs `1993`. | The temporal selector still fails on some relation-sensitive multi-year cases where “most recent” must be grounded in event semantics, not just local admissibility. |
