# Relation to the changed construction

[PR #4700](https://github.com/CrocSwap/integer-mult-bounds/pull/4700), at
commit `34434d4ea5d9edf58529eaf79b543cd6c58f3e41`, has a
[proof for the PR #4610 scalar word](https://github.com/CrocSwap/integer-mult-bounds/blob/34434d4ea5d9edf58529eaf79b543cd6c58f3e41/research/center-chart-bound/PROOF.md).
It proves a total centre-rank floor of 64 under its stated global monotone
binary-chart model. It keeps the actual warp maps, scalar graph, main and
adapter boundaries, and centre protocol. Its helper boundaries may vary.

That work uses a different scalar word and a different allowed class.
The present package uses the historical gauge44 word and exact right-gauge
relations at paired endpoints. It proves whole-graph rank and concave-cost
limits for the specified translation-line families, and a separate local
common-product rank-six bound. Neither theorem is used as a premise for
the other in this package.

This is a bounded scope comparison, not an exhaustive novelty claim.
The current publication refresh supplied the PR head and source proof.
No checker or certificate from PR #4700 is consumed here.
