Title: Prove the Y-cancellation arrival floor for P104 native words: owned-only X routing and parity-complementary covers (no κ)

No κ claim. This adds `research/p104-native-y-cancellation-floor/`, a registered research package for the card `p104-side-correction`.

**Result.** For the 104 ports of P104 (every port has odd weight, so q_p is not in H_p = q_p^perp):

1. X content reaches Y_p's final value only through owned descents, for every legal native word.
2. Assume (H3) that the public final x-support S_p of Y_p spans H_p. Then the cancellation needs at least one non-Y public arrival at H_p per port, and at least two when Y_p has no interior stop below H_p. Two arriving frames suffice exactly when they lie in a parity-complementary pair of hyperplanes {a, a+1}. There are 127 such pairs per port, and no single hyperplane works.
3. H3 is not forced by legality: S_p empty is attainable with one extra owned rank-1 term per port per call. This is a remark and is not priced.

**Proof sketch.** Public x-support stays inside the ports of the current frame; an owned arrival resets the public part. Frames inside H_p contain no port q_p, which gives (1). Y_p's final public part is carried by Y_p's own arrival and by the other arrivals at H_p; each lies in a proper subspace of H_p, hence in a hyperplane, and one hyperplane cannot hold a spanning set, which gives the floor in (2). Because every port is odd, v.a and v.(a+1) differ, so {a, a+1} covers; the exhaustive count shows these are the only covering pairs.

**Checks.** `check.py` (standard library, under a second) recomputes from the port list: odd weights, |Orth(p)| = 48 with GF(2) rank 8 for all 104 ports, the 127 covering hyperplane pairs per port (all parity-complementary), and the absence of a single covering hyperplane.

**Scope.** The arrival floor is conditional on H3. No word is constructed and nothing is priced; open questions are in the package.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
