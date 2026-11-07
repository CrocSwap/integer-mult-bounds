Title: Prove that P104 has no rank-8 complex realisation over any field: a 14-port Hall obstruction (no κ)

No κ claim. This adds `research/p104-rank8-hall-obstruction/`, a registered research package for the card `p104-side-correction`.

**Result.** Assume the complex label pattern: each of the 104 ports of the #5561 word carries a pair of label matrices of size k × d over a
field, the pairing between ports vanishes exactly on the E8-non-orthogonal pairs (port pairs with zero F2 dot product), and every diagonal
block is invertible. The pairing may be asymmetric. Then no realisation has inner dimension exactly 8k, over any field of any
characteristic. For k = 1 the minimum rank is at least 9.

**Proof sketch.** Eight pairwise forced-zero ports (`62, 63, 69, 74, 81, 86, 91, 99`) fix a gauge. Six further ports
(`57, 67, 68, 95, 100, 101`) are then supported on at most five of those coordinates, any two of them sharing a coordinate are forced zero and
share only that one, so the stacked products at each coordinate are block diagonal and have rank at most k. The six invertible diagonal
blocks need total rank 6k, but only 5k is available: a Hall deficiency.

**Checks.** `check.py` (standard library, under a second) verifies the clique, the coordinate sets, the 11 sharing pairs, the
absence of a system of distinct representatives, an exhaustive F2 and F3 search of the gauge-fixed 14-port system, a satisfiable control, and a
satisfiable dimension-9 realisation. Singular inputs and outputs (rings Z/2, Q, Z/3, Z/5, Z) are retained.

**Scope.** The label pattern is a hypothesis. Ranks strictly between 8k and 9k (k >= 2), other masks and any pricing are not covered; they are
listed as open questions in the package.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
