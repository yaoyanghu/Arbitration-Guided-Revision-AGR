# Route A v3 Holdout Next Step Decision

## Decision

1. Does Route A v3 still hold on a new slice?  
Yes.

2. What does this hold-out check add?  
It gives a low-risk external robustness check showing that the same Route A contract and same scoring logic remain effective on a new temporal-conflict slice that was not part of the v3 mainline package.

3. Does this change the Route A mainline claim?  
No. It strengthens confidence in the current claim, but it does not change the claim scope.

## Practical Readout

- Keep Route A v3 as the mainline experiment package.
- Treat this hold-out as a robustness confirmation, not a new mainline.
- Keep Route B only as an analysis layer if it appears in later writing.
