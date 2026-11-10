# Consolidated root theorem: the chain-nested root minimises D_root (no kappa)

**No new kappa.** This package consolidates what is proved and checked about the root of the P104 caller: under a stated model and an explicit hypothesis ledger, the chain-nested root `chain(9|9)` (#6833) minimises the root cost `D_root` among all shortest roots, and no root made of several shortest roots, and no root with one extra unit under the stated conditions, can pay. Nothing is built or priced beyond the root formula. The base statement and the staircase proof are #6868; this package adds the pieces below and a ledger of every hypothesis. Full statements and proofs are in `THEOREM.md`.

## Results

1. **Dieudonne bound and rigidity.** A root of rank-one units `I - 2xy^T` with product `-I` has `N >= n+1` (three-line proof: for `N = n` one would get `K = YX` with `diag K = 1`, `diag YX = 0`); `n` is even. For `N = n+1` the unit data are unique up to gauge and equal the sign Gram `y_i x_j = sgn(i-j)`, with `G_ij G_ji = -1` (a direct proof through the rank-one matrix `Z = I + Lo - Up`; no Katz theorem and no characteristic assumption beyond char != 2, which is automatic over `Z[1/2][i]`). Exact over Q: the sign-Gram root multiplies to `-I` for every even `n = 2..20`, and the tangent space of the solution variety equals the gauge-orbit tangent for `n = 2, 4, 6`.
2. **Star optimality.** Among pair-covering topologies the single all-field is optimal: every other field has price per covered pair above `f(8N+1)/(N(N-1))` for all `N = 2..1199` (50-digit arithmetic).
3. **Chain optimality** (#6868, with `f = x ln x`): `D_root >= f(8L+1) + 2 sum_{m=1..g}[f(8m+1) - f(8m-8)]`, `L = 2g`, equality only for `chain(g|g)` and its twin; `1418.8458829` per port at `L = 18`.
4. **Block roots never pay.** Each unit beyond `n+1` lowers the surplus `S = 760` by 104. For all 384 partitions of 18 into at least two blocks the true gain is negative; the best is `-4.8%` at (9,9).
5. **The cost formula is derived.** `D_root = f(8L+1) + sum over non-A fields [f(8|M|+1) - sum of f(8r) over idle runs]` is the root part of the #6833 invoice term for term: the published invoice minus the native part equals the root events of the literal caller word, and `D_root/104 = 1418.8458829299` to 1e-40. Using the exact kernel `(x - x^{1-kappa})/kappa` in place of `x ln x` rescales `D_root` by `-0.78%` and does not change the optimiser (exhaustive for `L = 4..12`). Support outside a mask would need an extra paid job and gives `S < 0`.
6. **Dense x and dense y.** With `y` dense and `x` free on arbitrary masks, the chain is optimal for `L = 4, 6, 8` by exact enumeration (5,407,049,079 families at `L = 8`; 60 pass the sign prefilter, 58 below the chain are all unrealizable by Groebner basis over Q) and for **all L** when every non-A field has a single host (Theorem A). The only realizable families below the chain are uncovered-pivot families (saving 3.43957 at `L = 4`, 0.43858 at `L = 4, 6`); none exist at `L = 8`, and the natural pivot family is a loss from `L = 8` on.
7. **Roots with one extra unit.** Normal form `rank Z = 2`; under R1-R4 the `k`-th smallest mask is at least `ceil(k/5)`, so `D_root >= 1276.03` at `L = 18`, above the break-even `1120.2` (79.0% of the chain). Break-evens for `e = 2, 3`: 821.6, 523.0.
8. **D-free bases.** The verifier takes ADD/SCALE coefficients as literals and `D_s` only as monomial row shifts, so legal words have D-free bases. This is a convention, not a consequence of the symbolic identity (an exact `L = 2` D-dependent gauge preserves `M(D)`). A D-valued coefficient is priced as an uncredited job of rank `8|J|` (`f(8) = 16.64` per port) that lowers `S` by at least 832 per incidence; at `L = 2` no word with one such job is diagonal (0 of 4536 tested).

## Scope and open items (stated honestly)

* **Hypotheses assumed:** rank-one units, each `D_k` once and affine, `[P_k, U_k] = 0` and `x_k, y_k` inside `M_k` in the site frame, liveness (R4), the verifier's convention of D-free bases, the whole-job/compiler contract behind the cost formula, quoted constants (`S = 760`, native total).
* **Twisted site-frame masks.** Whole-job credit forces only `P_k = U_k E_k U_k^{-1}`, not `P_k = E_k`; an exact twisted witness over Q exists at `n = 4` and lies outside the regime of the proofs. **Closed at `L = 2`**: a pricer that reproduces `chain(1|1) = 87.7147`, `chain(2|2) = 217.9930`, `chain(9|9) = 1418.8458829` gives every twisted root at least 90.854 against 87.7147, and twisted sites with `|S| = 2` do not exist (Groebner basis `{1}` over Q). **Open for `L >= 4`.**
* **Shared-host fields and pivot rows at `L >= 10`:** proved only for single-host fields (all `L`) and by exact decision up to `L = 8`.
* **Roots with `e >= 2` extra units**, and `e = 1` with R2/R3 dropped; the `e = 1` floor holds under R1-R4 only.
* **J-staircase lemma:** constant bases plus uncredited D-jobs are priced (no gain) but not proved never to beat the chain.
* Escapes outside the model: non-coordinate masks, rank-2 units, non-gadget implementations, border and scratch-clearing escapes (conserved only within the named classes).

## Exact checks

`python3.12 -I -B check.py` (about 25 s; `--quick` shortens the exhaustive parts; `--twisted` adds the two twisted-site Groebner decisions, about 90 s; needs Singular). Standard library only. It runs the base checker (`base_check.py`) and the core checker (`root_check.py`: product formula, sign-Gram roots `n = 2..20`, transport identity and frame-gap witness, star dual `N = 2..1199`, staircase and exhaustive sign model `L = 4..18`, the S identity, 384 partitions, break-evens), then items 1, 5, 6, 7, 8 above as exact computations; item 6 uses the decision logs in `supp/` (cost and prefilter recomputed for every stored family, `L = 4, 6` enumerations redone in Python) and re-runs all 104 decisions when Singular is installed. The `L = 8` enumeration (`supp/enum_dense.c`, about 8 minutes) and the Groebner decisions are otherwise stored logs. It ends with `PASS_P104_CONSOLIDATED_ROOT_THEOREM`.

## Open next questions

1. Do twisted site-frame masks lower `D_root` for `L >= 4`? (Closed at `L = 2`; needs an exclusion of `|S| = 2` twisted sites at `n = 6` and a pricer that reproduces `chain(2|2)` with the relaxation.)
2. Can Theorem A be extended to fields shared by several hosts and to pivot rows at `L >= 10`?
3. Is there a J-staircase lemma for constant bases plus uncredited D-jobs?
4. Do roots with `e >= 2` extra units, or `e = 1` without R2/R3, stay above the break-evens 821.6 / 1120.2?

The structured form with first steps and blockers is in `TASK.json`.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
