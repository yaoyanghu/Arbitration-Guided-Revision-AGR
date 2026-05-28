# Next Step Decision

1. Route B 现在是否已经足够进入 main experiment 设计

不够。

原因不是 graph 没有效果，而是当前净增益仍然主要集中在 `mixed` hard cases，说明 Route B 还没证明自己在更广的 case family 上产生独立方法价值。

2. 如果还不够，最大硬伤是什么

最大硬伤是：

- 虽然 relation pattern 已从 `1` 种增到 `3` 种，但这种异质性目前仍然主要按 case type 分块
- 净增益仍然是 `mixed = 6`，`clear = 0`，`reliability = 0`
- 这说明 graph 已经不再是单一模板，但还没有证明它对非 mixed cases 也有独立收益

3. Route B 应继续扩成 prototype++，还是降级为 analysis module

当前最合理的选择是：`继续扩成 prototype++`

理由：

- graph 不是空壳
- relation structure 已经比 v1 更异质
- A + graph 相比 A only 仍有净增益
- 但还不够支撑 main experiment 设计

所以现在应继续做更强的 prototype++ hardening，而不是直接升格，也不是现在就降级成纯 analysis module。
