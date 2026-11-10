# Surplus bound, hub rank law and form-capacity lemma for the P104 word (no kappa)

**No new kappa.** No word is built and nothing is priced beyond stated arithmetic. This package states, with an explicit hypothesis ledger, three conditional structural results about the P104 caller and the checks that back them. Statements and proofs are in `THEOREM.md`.

Tag discipline (as in `THEOREM.md`): **[C]** exact computation reproduced by `check.py` (one PASS line per claim); **[P]** hand proof; **[P+C]** both; **CONDITIONAL** stated but not proved, or not checkable here. A verifier or package restriction is never called a law: the labels are SPEC (outer framework or paper), package convention, verifier behaviour, derived, family assumption.

## Results

1. **Surplus identity [C].** At the selected record (13,444 productive fields, 66,834 paid calls) the rank-mass surplus is `S = 760 = v(L-1) - Lc = 104*17 - 18*56`, recomputed from the stored profile. The pricer's own assertion at `research/p104-helper470-twin-rung-removal/pricing.py:75` is quoted and its line is checked.
2. **Ratio lemma [P+C].** For any word made of invertible Q-independent maps and `N` isotropic rank-one units, `N >= 1 + dim ker(R+I)` with `R = P(-1)P(1)^-1`. The identities in the proof hold exactly over Q on random isotropic instances; the chain roots attain the bound. CONDITIONAL on exactness at `Q = +-1`, isotropic rank-one units, and credited fields equal to `ker(R+I)`.
3. **Surplus bound, Theorem 2 [P, sweeps C], CONDITIONAL on H1-H6.** `S <= sum_p (L_p - 1) - sum_j c_j`, which is `v(L-1) - Lc` for uniform ports; the target size cancels. H1 and H4 are hand arguments (H4's "mains pay exactly the stage rank" step is not re-audited), H5 (one hosted Q-odd unit per LOCAL) is a family assumption, and with two the same arithmetic would allow 2632. The bound concerns the numerator only.
4. **Typed query, Proposition 3 [C, P], scoped.** A rank-one Q-odd unit realised by a Clifford operator has Bruhat rank one and lies in a single `F H F` cell; the plane kernel `K_P` is a rank-two job in the cell of `C (x) C`. The cost-model reading (a thin query costs one rank-one paid call per port) is CONDITIONAL; the non-unitary shear factorisation lies outside the lemma and whether a shear-typed supplier can be priced below a leaf is open. The check runs in exact Gaussian-rational arithmetic with the standard library only.
5. **Hub rank law, Theorem 4 [P+C], CONDITIONAL on the coordinate-mask grammar.** rank `Z(D) = v`, the cocycle relation, divisibility `Z_fl(D) = Z_fl(1) prod D_k^-1`, and at least `v` coordinates in every LOCAL mask, at every nonzero `D`. The checked instances are gauge-equivalent to a direct sum and cannot exhibit a non-gauge coupling; the proof, not the replays, carries the claim.
6. **Form-capacity lemma, Theorem 5 [P, tested by C], scoped.** In the stated one-pass stop family, if `Y' = c x`, `T[Y,K] = 0` and `X', K'` span `(y - a x, k)`, then `ku >= v` for every `kd` and `a`. The numerical cells (v = 3, eight cells; v = 2, four cells) are generic-solution evidence for the invariant, and unsolved cells are not evidence; a control family with down rows landing at a line exceeds the bound, as the scope says.
7. **Label corrections and retained arithmetic [C].** The identical-representative requirement is a package convention, not SPEC; symbolic exactness in `D` and ascend-only public paths are verifier behaviour. For words multi-affine in `D`, vanishing on `{+1,-1}^k` is equivalent to vanishing as a polynomial (evaluation matrix rank `2^k`, `k = 2, 3, 4`). Invoice-total arithmetic uses typed-in constants, not a recomputation from a word; the two partial sums differ by 4 from the quoted total (226,935 versus 226,939) from rounding.

## Scope and what is not claimed

No bound on kappa; no statement about the denominator; nothing about non-diagonal Gram structure; Lemma 1 and Theorem 2 do not cover in-place units, words with leak, or words exact only in a limit; Theorem 4 and Theorem 5 are as scoped above. No word from any pull request is replayed or checked here.

## Exact checks

`python3.12 -I -B research/p104-surplus-hub-form-note/check.py` from the repository root (or `verify.sh` from anywhere). About 20 s. Exact parts use the standard library only (`fractions`). The Theorem 5 numerical cells need numpy, pinned in `VERIFY.json` (`numpy==2.4.2`). The quote checks read six repository files named in `data/quotes.json` (19 lines) and fail if a file is absent or a line changed; the same files are pinned in `SOURCES.json`. The run ends with `PASS_P104_SURPLUS_HUB_FORM_NOTE`.

## Open next questions

1. Can a LOCAL host two Q-odd units per port (H5), and does any word then reach the 2632 value the same arithmetic allows?
2. Can a shear-typed supplier realise the thin queries below one rank-one paid call per port (H6)?
3. Does the hub rank law survive outside coordinate masks with one scalar per LOCAL, and is a half-width hub possible there?
4. Does the form-capacity bound extend to down-row landings at a line after X reached V, and to targets with `T[Y,Y] != 0`?

The structured form with first steps and blockers is in `TASK.json`.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
