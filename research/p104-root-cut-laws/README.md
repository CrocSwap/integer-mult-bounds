# Root cut laws for two-chain words: hub, rectangle and cut bounds (no new kappa)

**No new kappa.** No word is built and nothing is priced. `THEOREM.md` states and proves, with hypotheses, a rectangle law and the residual-rank floor 144 for two-chain roots (Theorem S), Theorem H for pivot masks and its exact form H', an exact two-chain counterexample to the stronger statement, the closed form of the root cut for all-pivot words, and the crossing bounds of Theorem C for flat words.

Tags: **[P]** hand proof, **[C]** exact computation reproduced by `check.py`, **[Q]** quoted.

## Results

1. **Rectangle law and Theorem S [P+C].** For 2 x 2 gains and an odd sign quadruple the four residual ranks sum to at least 2; 72 odd rectangles pack the 18 x 18 cell grid with no shared cell, so for any hub pair the residual rank over all stage pairs is at least 144. Tight on the two root instances (at one hub pair each); all 703 and 780 hub pairs checked.
2. **Theorem H and H' [P+C].** At least rho coordinates lie in every pivot mask between two pivots. For any label j in the hull, at least rank Z_UU(j) of them lie in M_j. The stronger statement (every mask of the hull) is false: on the t = 0 direct-sum root with two rank-1 labels, hub 20 is in every pivot mask and absent from the interior mask (J = 4 and 7). The counterexample lives on a reducible root; nothing is claimed for connected roots and no kappa consequence.
3. **Root cut [P arithmetic, C].** Cut per chain = 8[f(18) + 2 f(9)] + 87.353 = 819.967 with f(x) = x ln x, for all-pivot words; the words with a t = -1 label have lower incidence and are outside it. The cost expression is a convention fixed in the note.
4. **Theorem C [P+C].** For flat words and any frame set: rank T[D+E, A+D] <= n_down and rank T^-1[A+D, D+E] <= n_up - |C| + |D|; for T invertible and T = I_D + T'', a cut demand (f, r) costs at least f + r crossings with owned registers and at least 2 max(f, r) without. A non-flat toy shows the flat bound fails (n_down alone); n_down + a_down is proved.

## Not claimed

No bound on kappa. The hub rank law (R) and the cost expression of the root cut are quoted, not re-derived. Theorems S and H' are new and read by one model session beyond the author; no human has reviewed the proofs. Credit: the roots, the hub rank law and the cost model come from the same author's PRs #6881, #6889, #6902 and #6833; the nullity theorem is classical (Gustafson 1984; Fiedler and Markham 1986) and is reproved.

## Exact checks

`python3.12 -I -B research/p104-root-cut-laws/check.py` (a few seconds), or `verify.sh`. Standard library only; it ends with `PASS_P104_ROOT_CUT_LAWS`, prints one PASS line per claim and fails on a missing marker, a wrong count or a failing control (planted bounds, contract-breaking mutations, an even sign quadruple, characteristic 2).

## Open next questions

1. Does any connected root have an interior t = -1 stage at which a hub skips the mask?
2. Does Theorem S extend to stages of more than two units and to rho > 2?
3. Can Theorem C be stated for non-flat words without counting non-flat ADDs separately?

The structured form is in `TASK.json`.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
