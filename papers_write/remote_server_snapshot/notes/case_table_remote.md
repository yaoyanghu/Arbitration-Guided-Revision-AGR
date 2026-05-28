# Case Table

| claim_id | label | claim_summary | gold_page | baseline_rank | improved_rank | case_type | short_explanation |
| --- | --- | --- | --- | ---: | ---: | --- | --- |
| 1544 | SUPPORTS | Cheese in the Trap (TV series) is a television series. | Cheese in the Trap (TV series) | 3 | 1 | disambiguation | The title-overlap score resolves ambiguity by preferring the candidate whose page title matches the claim entity more directly. |
| 88473 | SUPPORTS | Edward G. Robinson is a star in The Cincinnati Kid. | The Cincinnati Kid | 2 | 1 | disambiguation | The title-overlap score resolves ambiguity by preferring the candidate whose page title matches the claim entity more directly. |
| 117305 | SUPPORTS | Awkward Black Girl is a series on the Internet. | Awkward Black Girl | 2 | 1 | surface_title_match | The improved ranking promotes the exact gold page title over a shorter or truncated baseline title. |
| 50923 | SUPPORTS | Andrew Kevin Walker is American. | Andrew Kevin Walker | 2 | 1 | surface_title_match | The improved ranking promotes the exact gold page title over a shorter or truncated baseline title. |
| 164411 | REFUTES | Carey Hayes died in April of 1961. | Carey Hayes | 2 | 1 | exact_gold_promotion | The gold evidence page was already in the candidate set and title overlap moved it to rank 1. |
| 183629 | SUPPORTS | Finding Dory was written. | Finding Dory | 2 | 1 | exact_gold_promotion | The gold evidence page was already in the candidate set and title overlap moved it to rank 1. |
| 84409 | SUPPORTS | Hourglass was released 6 years after New Moon Shine. | Hourglass (James Taylor album) | 1 | 2 | strict_regression | Title overlap over-promotes a nearby comparison page with strong lexical overlap. |
| 87942 | SUPPORTS | There is a video game called Team Fortress 2. | Team Fortress 2 / Multiplayer video game / Source (game engine) / Robin Walker (game designer) / Electronic Arts / The Orange Box / Team Fortress Classic | 1 | 2 | strict_regression | Title overlap promotes a lexically similar but non-gold page under strict evaluation. |
