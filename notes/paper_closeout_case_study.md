# Case Study Draft

The strongest temporal cases show that the system can ignore salient retrospective mentions and return the year that is actually licensed by the query relation, such as `as of`, `before`, or “last time”. These cases support the argument that temporal-aware answer extraction is doing more than generic lexical span selection.

The strongest conflict cases occur when current and stale same-title evidence disagree on the answer-bearing value. In these cases, conflict-aware arbitration helps the model prefer the fresher and more specific evidence. The most representative remaining failures occur when several evidence snippets share nearly identical surface structure, causing the system either to pick the wrong entity family or to copy the wrong answer-bearing value from an otherwise relevant passage.
