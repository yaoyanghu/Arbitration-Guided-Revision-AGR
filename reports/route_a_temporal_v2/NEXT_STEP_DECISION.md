# Next Step Decision

A. 现在是否允许进入 Route B 主实验: 允许

B. Route A hardened gate 已满足。

C. 如果进入 Route B，最小原型应该只做：
- 对 Route A top-k 结果构建一个轻量局部 evidence graph
- 只验证 graph 是否帮助少数 temporal-conflict hard cases
- 不引入 generation 或大 sweep