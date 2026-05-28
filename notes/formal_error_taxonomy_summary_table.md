# Formal Error Taxonomy Summary Table

| error type | primary dataset | description | evidence in current formal runs |
| --- | --- | --- | --- |
| Wrong entity or wrong evidence family | HOH | The system retrieves or selects a demographically similar but incorrect entity block. | Example: `Otago` questions answered from `Tikipunga` or another district. |
| Wrong value from correct evidence family | HOH | The title and topic are right, but the extractor picks the wrong number or span from the correct sentence family. | Example: `95` nominated authors instead of `18` winners. |
| Stale evidence copied into final answer | HOH | Conflict ranking is improved, but answer synthesis can still quote the stale second citation. | Example: `Lord de Mauley` instead of `The Lord Ashton of Hyde`. |
| Temporal relation / year selection error | TempRAGEval | The model picks a temporally plausible year that does not satisfy the intended relation. | Example: `1993` selected instead of the most recent valid `1995`. |
| Other answer extraction error | Both | The answer span is malformed, truncated, or mapped to the wrong slot even when evidence is partially relevant. | Example: title-like or subject-like span emitted instead of the requested role/value. |
