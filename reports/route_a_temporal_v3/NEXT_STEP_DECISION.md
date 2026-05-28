# Route A v3 Next Step Decision

## Decision

1. Route A v3 是否已足够作为真正主线实验包  
是，作为当前项目的主线实验包已经足够。

2. Route A 还缺什么才能开始论文化  
还缺两样更硬的东西：

- a larger reusable temporal-conflict slice beyond the current 54-query package
- a cleaner checkpoint bundle that can be reused and cited without relying on Route B context

3. Route B 当前应如何在论文里定位为 analysis layer  
Route B should only be described as an `analysis / conflict-focused module` that helps inspect update, contradiction, and corroboration structure around Route A cases. It should not be presented as the main method line.

## Why v3 Is Mainline-Ready

- The slice is larger and still balanced across all three Route A case types.
- The task contract and evaluation metrics are unchanged from v2.
- The final Route A stage remains clearly better than retrieval-only.
- Temporal and reliability signals both have measurable effects.
- Per-query inspectable artifacts exist for all 54 queries.

## What v3 Still Does Not Mean

- It does not justify Route B as a main experiment.
- It does not say anything about Route C.
- It does not mean the Route A line is already publication-ready without more external-validity support.
