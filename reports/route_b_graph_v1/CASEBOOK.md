# Route B Graph v1 Casebook

## Improved Cases

- `v2_001_mixed`: Route A final `2` -> graph `1`
  query: Before the update was fully settled, joe biden was a former vice president and presidential candidate, not yet serving as president By 2021, what was the current status of Joe Biden in the official current record?
  edge counts: {'support': 3, 'corroborate': 6, 'update': 1, 'contradict': 2}
- `v2_002_mixed`: Route A final `2` -> graph `1`
  query: Before the update was fully settled, lionel messi played for paris saint-germain before the inter miami move By 2023, what was the current status of Lionel Messi in the official current record?
  edge counts: {'support': 3, 'corroborate': 6, 'update': 1, 'contradict': 2}
- `v2_004_mixed`: Route A final `2` -> graph `1`
  query: Before the update was fully settled, charles was the prince of wales before becoming king By 2022, what was the current status of Charles III in the official current record?
  edge counts: {'support': 3, 'corroborate': 6, 'update': 1, 'contradict': 2}
- `v2_005_mixed`: Route A final `2` -> graph `1`
  query: Before the update was fully settled, before 2022, midnights was only discussed as an upcoming taylor swift project By 2022, what was the current status of Midnights in the official current record?
  edge counts: {'support': 3, 'corroborate': 6, 'update': 1, 'contradict': 2}
- `v2_008_mixed`: Route A final `2` -> graph `1`
  query: Before the update was fully settled, in 2022 novak djokovic spent part of the season outside the number one ranking By 2023, what was the current status of Novak Djokovic in the official current record?
  edge counts: {'support': 3, 'corroborate': 6, 'update': 1, 'contradict': 2}

## Regressed Cases


## Relation Structure Examples

- `v2_001_clear`: edge count `12`, edge counts `{'support': 3, 'corroborate': 6, 'update': 1, 'contradict': 2}`
  query: As of 2021, Joe Biden is the president of the United States.
- `v2_001_reliability`: edge count `12`, edge counts `{'support': 3, 'corroborate': 6, 'update': 1, 'contradict': 2}`
  query: In 2021, some reports said joe biden is the president of the united states but treated it as uncertain and still unconfirmed. What did the official current record say?
- `v2_001_mixed`: edge count `12`, edge counts `{'support': 3, 'corroborate': 6, 'update': 1, 'contradict': 2}`
  query: Before the update was fully settled, joe biden was a former vice president and presidential candidate, not yet serving as president By 2021, what was the current status of Joe Biden in the official current record?
- `v2_002_clear`: edge count `12`, edge counts `{'support': 3, 'corroborate': 6, 'update': 1, 'contradict': 2}`
  query: As of 2023, Lionel Messi plays for Inter Miami.
- `v2_002_reliability`: edge count `12`, edge counts `{'support': 3, 'corroborate': 6, 'update': 1, 'contradict': 2}`
  query: In 2023, some reports said lionel messi plays for inter miami but treated it as uncertain and still unconfirmed. What did the official current record say?