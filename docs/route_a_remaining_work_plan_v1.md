# Route A Remaining Work Plan v1

## Scope

This roadmap covers only Route A until it reaches an acceptance-stage decision point.

Out of scope:

- Route B
- Route C
- generation
- sentence-level attribution
- dense retrieval

## 1. Remaining Work Breakdown

### Step 1. Freeze the task contract

Artifacts:

- [route_a_task_contract_v1.md](D:/HUYAOYANG/Work/ChronoRAG/docs/route_a_task_contract_v1.md)
- [route_a_subset_build_plan_v1.md](D:/HUYAOYANG/Work/ChronoRAG/docs/route_a_subset_build_plan_v1.md)

Goal:

- define what counts as success before touching more code

### Step 2. Build a real temporal-conflict subset

Needed artifact:

- `data/processed/route_a_temporal_v1_subset.jsonl`

Goal:

- create a subset where updated-vs-stale preference is explicit and auditable

### Step 3. Implement Route A V1 minimal scoring

Needed modules:

- temporal scoring specialized for updated-vs-stale preference
- reliability prior specialized for conflict cases
- final reranking over retrieval candidates

### Step 4. Implement Route A task-specific evaluation

Needed outputs:

- retrieval-only baseline
- retrieval + temporal
- retrieval + temporal + reliability

Task-specific checks:

- updated evidence wins over stale more often
- temporal signal produces measurable rank changes
- reliability helps at least some conflict cases

### Step 5. Produce acceptance-stage reports

Needed reports:

- `ACCEPTANCE_CHECK.md`
- `ERROR_TAXONOMY.md`
- `CASEBOOK.md`
- `NEXT_STEP_DECISION.md`

## 2. Existing Scripts That Can Be Reused

### Retrieval backbone

- [search.py](D:/HUYAOYANG/Work/ChronoRAG/src/retrieval/search.py)
- [build_bm25.py](D:/HUYAOYANG/Work/ChronoRAG/src/retrieval/build_bm25.py)

### Score fusion

- [rerank.py](D:/HUYAOYANG/Work/ChronoRAG/src/rerank/rerank.py)

### Current temporal/reliability skeleton

- [label_relation.py](D:/HUYAOYANG/Work/ChronoRAG/src/temporal/label_relation.py)
- [source_score.py](D:/HUYAOYANG/Work/ChronoRAG/src/reliability/source_score.py)

### Orchestration and artifact style

- [eval_main.py](D:/HUYAOYANG/Work/ChronoRAG/src/eval/eval_main.py)
- existing `runs/` artifact layout

## 3. Scripts That Should Be Added

Recommended additions:

- `src/data/build_route_a_temporal_subset.py`
- `src/temporal/score_temporal_conflict.py`
- `src/reliability/score_route_a_reliability.py`
- `src/eval/eval_route_a_temporal.py`
- `src/analysis/route_a_casebook.py`

Optional helper:

- `scripts/run_route_a_temporal_v1.sh`

## 4. Execution Order

Recommended order:

1. finalize the contract and subset plan
2. build the subset
3. wire temporal scoring
4. wire reliability scoring
5. add task-specific evaluation
6. run the small real subset
7. write acceptance reports

This order matters because the current repository already proved that a weakly targeted subset leads to zero measurable temporal gain.

## 5. What Must Be True Before Route B

Only when all 5 acceptance criteria from [README.md](D:/HUYAOYANG/Work/ChronoRAG/reports/route_a_temporal_v1/README.md) are met should Route B be allowed.

Those criteria are:

1. the Route A pipeline runs end-to-end on a small but real temporal-conflict subset
2. the temporal signal measurably changes ranking behavior
3. updated evidence beats the retrieval-only baseline often enough to show real value
4. reliability helps at least some conflict cases in a sensible direction
5. per-query artifacts are inspectable

If any one of these is missing, Route B should not start.

## 6. Why Route B Must Wait

Current repository evidence shows:

- [analysis_summary.md](D:/HUYAOYANG/Work/ChronoRAG/runs/fever_hetero_subset_route_a/analysis_summary.md)
- [analysis_summary.md](D:/HUYAOYANG/Work/ChronoRAG/runs/fever_real_subset_route_a/analysis_summary.md)

both have:

- zero temporal improvements
- zero reliability improvements

That means Route A is not yet in a state where graph augmentation would be interpretable.

So the correct next step is not Route B.

The correct next step is:

- rebuild Route A around a real temporal-conflict subset and acceptance-stage evaluation.
