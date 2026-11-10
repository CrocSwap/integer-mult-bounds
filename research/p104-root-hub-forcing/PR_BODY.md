Title: Prove the root hub of P104 chain-nested roots is forced under replay: single-time, piece-adjacent and commuting-split scalings (no κ)

No κ claim. This adds `research/p104-root-hub-forcing/`, a registered research package for the card `p104-side-correction`.

**Result.** Take a saturated word `W(D) = S_N T_N ... S_1 T_1` with `N = n+1` shears `T_j = I - 2 x_j y_j` (`y_j x_j = 0`), characteristic 0, independent scaling parameters `D_m`, scalings `S_e = I + (D_{s(e)} - 1) E_e` with idempotent `E_e`, coordinate target masks `M_m`, and atomic LOCAL pieces (`E x_p = x_p`, `y_p E = y_p`), replaying at `Q = +1` and `Q = -1` with `W(+1) = D^w` and `W(-1) = -D^w`. Then some coordinate lies in every mask, so the hub target `8L+1` (`= 145` on the 9|9 chain-nested root of #6833) cannot be lowered, in each of these cases:

1. every stage is scaled at a single time;
2. one stage is split into two pieces, with no non-local piece between a shear and the LOCAL piece of its own stage;
3. any number of split stages and pieces whose in-window pieces of distinct stages commute.

The package also states Lemma M: the master identity is equivalent to one invertible `M(D)` with `Lam^{-1} T_j Lam = M T_j M^{-1}` for all `j`, confirmed exactly on the 1|1 and 2|2 chains.

**Proof sketch.** The master identity makes every primed Gram entry a signed monomial, and a specialisation to one stage fixes its exponent pattern (including `beta = 0` for the last stage directly from orthogonality of its pieces). The top coefficient of the first-to-last entry is then a sum over one in-window piece per stage of `y_N tau x_1`; under the stated hypotheses every `tau` is supported on the common coordinates of the in-window stages, and that coefficient is nonzero.

**Checks.** `check.py` (standard library, exact rationals, under a second) verifies on chains (1|1) and (2|2): the replay, the monomial Gram with `g_ij g_ji = -1`, the top coefficient and the common carrier, and Lemma M. It also verifies the multilinear top-coefficient formula on random non-commuting pieces, commuting configurations, and one control that violates the commuting hypothesis, where the formula gives a nonzero coefficient with `tau` outside the common coordinates (not a counterexample, since the master identity is not imposed there).

**Scope.** Not covered, and listed as open questions: non-commuting interleaved pieces of distinct stages, the slot between the last shear and its LOCAL piece with a non-commuting first piece, non-atomic LOCAL, unsaturated headers, non-coordinate masks, and `Q`-dependent frame operations. One mid-slot triangle configuration (n = 4) is additionally excluded by an exact reduction, stated as a remark without a checker. No word is constructed and nothing is priced.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
