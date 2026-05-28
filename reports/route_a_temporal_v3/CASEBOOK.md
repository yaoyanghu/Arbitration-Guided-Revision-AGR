# Casebook

## Improved Cases

- `v3_001_reliability`: raw preferred rank `2` -> final `1`
  query: In 2021, some reports said joe biden is the president of the united states but treated it as uncertain and still unconfirmed. What did the official current record say?
- `v3_002_reliability`: raw preferred rank `2` -> final `1`
  query: In 2023, some reports said lionel messi plays for inter miami but treated it as uncertain and still unconfirmed. What did the official current record say?
- `v3_003_mixed`: raw preferred rank `2` -> final `1`
  query: Before the update was fully settled, rishi sunak served as chancellor before becoming prime minister By 2023, what was the current status of Rishi Sunak in the official current record?
- `v3_004_mixed`: raw preferred rank `3` -> final `2`
  query: Before the update was fully settled, charles was the prince of wales before becoming king By 2022, what was the current status of Charles III in the official current record?
- `v3_006_reliability`: raw preferred rank `2` -> final `1`
  query: In 2023, some reports said x is the name used for the social media platform formerly called twitter but treated it as uncertain and still unconfirmed. What did the official current record say?

## Reliability-Helped Cases

- `v3_001_reliability`: temporal preferred rank `2` -> final `1`
  query: In 2021, some reports said joe biden is the president of the united states but treated it as uncertain and still unconfirmed. What did the official current record say?
- `v3_002_reliability`: temporal preferred rank `2` -> final `1`
  query: In 2023, some reports said lionel messi plays for inter miami but treated it as uncertain and still unconfirmed. What did the official current record say?
- `v3_004_mixed`: temporal preferred rank `3` -> final `2`
  query: Before the update was fully settled, charles was the prince of wales before becoming king By 2022, what was the current status of Charles III in the official current record?
- `v3_006_reliability`: temporal preferred rank `2` -> final `1`
  query: In 2023, some reports said x is the name used for the social media platform formerly called twitter but treated it as uncertain and still unconfirmed. What did the official current record say?
- `v3_009_reliability`: temporal preferred rank `2` -> final `1`
  query: In 2023, some reports said threads is a social media app launched by meta but treated it as uncertain and still unconfirmed. What did the official current record say?

## Failure Cases

- `v3_001_mixed`: final preferred rank `2`, final stale best rank `1`
  query: Before the update was fully settled, joe biden was a former vice president and presidential candidate, not yet serving as president By 2021, what was the current status of Joe Biden in the official current record?
- `v3_002_mixed`: final preferred rank `2`, final stale best rank `1`
  query: Before the update was fully settled, lionel messi played for paris saint-germain before the inter miami move By 2023, what was the current status of Lionel Messi in the official current record?
- `v3_004_mixed`: final preferred rank `2`, final stale best rank `1`
  query: Before the update was fully settled, charles was the prince of wales before becoming king By 2022, what was the current status of Charles III in the official current record?
- `v3_005_mixed`: final preferred rank `2`, final stale best rank `1`
  query: Before the update was fully settled, before 2022, midnights was only discussed as an upcoming taylor swift project By 2022, what was the current status of Midnights in the official current record?
- `v3_008_mixed`: final preferred rank `2`, final stale best rank `1`
  query: Before the update was fully settled, in 2022 novak djokovic spent part of the season outside the number one ranking By 2023, what was the current status of Novak Djokovic in the official current record?