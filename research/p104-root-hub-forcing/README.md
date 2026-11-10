# Root hub forcing: some coordinate lies in every mask (no κ)

**No new κ.** This package proves that, for the saturated replayed words that realise the chain-nested roots of P104 (the 9|9 root of #6833 and its smaller members),
splitting a stage's scaling over several times cannot remove a coordinate from any mask in three families: single-time scaling, one split stage with piece adjacency,
and any splits whose in-window pieces of distinct stages commute. Nothing is priced and no word is constructed.

## Setting

* Characteristic 0. `D_1, ..., D_L` are independent indeterminates, one per stage. The word is `W(D) = S_N T_N ... S_1 T_1` (later events on the left),
  with `N = n+1` shears `T_j = I - 2 x_j y_j`, `y_j x_j = 0` (saturated header). Gap `g` (0 <= g <= N) lies between `T_g` and `T_{g+1}`.
* Scalings are `S_e = I + (D_{s(e)} - 1) E_e` with `E_e` an idempotent, `s(e)` the stage of the event; the pieces of a stage are its events.
  Scalings do not depend on `Q`.
* Replay: at `Q = +1` the shears vanish, `W(+1) = D^w`; at `Q = -1`, `W(-1) = -D^w`, where `D^w = diag(prod over stages m with f in M_m of D_m)`.
  Coordinate masks `M_m` (coordinate projectors). The other frame operations are `Q`-independent at `Q = ±1` and are absorbed into the shears and idempotents.
* **Atomic LOCAL.** Every thick stage `m` has exactly one shear `T_{p_m}` and a LOCAL piece `E_m^loc` at the same instant with `E x_{p_m} = x_{p_m}` and `y_{p_m} E = y_{p_m}`.
  Thin shears carry no scaling. `m(N)` is the stage of the last shear, `S_in` the stages with `1 <= p_m <= N-1`.
* The `L` stages and the masks give the coordinate degrees `d_f = #{m : f in M_m}`. A coordinate lying in every mask has degree `L`, hence the hub target `8L+1`
  (`= 145` for `L = 18`, the 9|9 chain-nested root of #6833).

Hypotheses, as used:

* **H0** replay at `Q = ±1` as above, `Q`-independent frame operations. **H1** characteristic 0, saturation `N = n+1`, independent `D_m`.
  **H2** coordinate target masks. **H3** atomic LOCAL simultaneous with its shear. **H5** the pieces of a stage carry the same `D`.
* **H6a (window commutation).** Any two pieces of distinct stages of `S_in` that lie in gaps `1..N-1` commute.
* **H7 (piece adjacency).** No non-local piece of any stage lies strictly between a shear `T_j` and the LOCAL piece of its own stage
  (in particular, none in the slot between `T_N` and the LOCAL piece of `m(N)`, and none at gap `j` before the LOCAL piece).

## Statement

**Theorem (root hub forcing).** Assume H0-H3 and H5, and one of

* **(a)** every stage is scaled at a single time (one piece per stage);
* **(b)** exactly one stage `P` has two pieces `E_1` (its LOCAL piece) and `E_2` (at any gap, before or after the window), every other stage has one piece, and H7 holds;
* **(c)** any number of stages with any number of pieces at any gaps (order inside a gap arbitrary), and H6a holds.

Then some coordinate lies in every mask `M_m`. In particular the hub target `8L+1 (= 145)` of the chain-nested root cannot be lowered by any of these scalings,
and no coordinate can be dropped from any mask, including the first and last sites.
Case (a) is the special case of (c) in which every piece is a coordinate projector, and it is also the content of the unsplit hub argument (Lemma 6 below).

**Lemma M (master identity as a conjugation).** Put `Lam_{<j}` for the ordered product of the scalings before `T_j` and `T'_j = Lam_{<j}^{-1} T_j Lam_{<j}`.
The master identity `prod_j T'_j = -I` (for all `D`) holds if and only if there is one invertible Laurent matrix `M(D)`, `M(1) = I`,
with `T'_j = M T_j M^{-1}` for all `j`; equivalently `B_j = Lam_{<j} M` commutes with `T_j`. On the chains (1|1) and (2|2) the solution space of `T'_j M = M T_j` is one-dimensional
and `det M` is a monomial unit. Lemma M restates the whole `Q = -1` content; it is not used in the proof of the theorem.

**Not covered** (open questions below): non-commuting interleaved pieces of distinct in-window stages (H6a fails); the mid slot with a non-commuting `E_1` (H7 fails);
non-atomic LOCAL; unsaturated headers; non-coordinate masks; `Q`-dependent frame operations.

## Proof

**Lemma 1 (pieces).** For a stage `m` specialise `D_{m'} = 1` for `m' != m` and put `a = D_m - 1`. The ordered product of the pieces of `m` is `I + a sum E_e` and must equal `I + a M_m`.
So `sum E_e = M_m`. Idempotents with `sum E_e = M_m` have `tr M_m = sum rank E_e` and `range M_m = sum range E_e`, so the ranges are independent and the pieces are
pairwise orthogonal with `M_m E_e = E_e M_m = E_e`. A single-piece stage has `E = M_m`, a coordinate projector. The same holds for the pieces conjugated by the `T`-prefix at `Q = -1`.

**Lemma 2 (commutation).** If a single-piece stage with event `M` lies in time strictly between two pieces `E_1` (earlier) and `E_2` of another stage `P`,
the coefficient of `a_P a_m` in the replay at `Q = +1` is `E_2 M + M E_1` (later on the left) and must equal `M_P M`. With `M_P = E_1 + E_2` commuting with `M` this gives `M E_1 = E_1 M`, hence `M E_2 = E_2 M`.
If `M` is before both or after both pieces nothing follows. (`check.py` verifies the coefficient identity.)

**Lemma 3 (primed Gram).** With `x'_j = Lam_{<j}^{-1} x_j`, `y'_j = y_j Lam_{<j}`, `g_ij = y'_i x'_j`, `K = I + 2L` (`L` the strictly lower part of `G`), the master identity gives `X K^{-1} Y = I_n`.
Hence `G K^{-1}` is an idempotent of rank `n`, and `Z = K - G` has rank one with unit diagonal (here `N = n+1` is used). So `Z_il = Z_ij Z_jl` and `g_ij g_ji = -1`.
For `i > j`, `g_ij = y_i Lam_{(j,i)} x_j` is a polynomial in `D` and `g_ji = y_j Lam_{(j,i)}^{-1} x_i` is a Laurent polynomial, so every `g_ij` is a signed monomial `c_ij D^{alpha_ij}` with `alpha_ij = sum_{k=j}^{i-1} alpha_{k+1,k}`.
No commutation of `Lam` with anything is used.

**Lemma 4 (exponent pattern).** Specialise `D_{m'} = 1` for `m' != m`. Then `g_ij = y_i x_j + a y_i F x_j`, with `F` the sum of the pieces of `m` in gaps `j..i-1`, an idempotent by Lemma 1, so the exponent `beta^m_ij` of `D_m` in `g_ij` is 0 or 1.
For the pair `(p_m, p_m+1)` atomicity gives `y_{p+1} F x_p = y_{p+1} x_p != 0` (other pieces satisfy `E_2 x_p = E_2 E_1 x_p = 0`), so `beta = 1` there.
Additivity (Lemma 3) with `beta <= 1` for every window forces `beta^m_ij = [j <= p_m < i]`. Consequently
`g_{N1} = c prod_{m in S_in} D_m`.
*The unstated step for the last stage.* For `m = m(N)` and the pair `(N, 1)`, the LOCAL piece of `m(N)` is at gap `N`, after `T_N`, outside gaps `1..N-1`; the pieces of `m(N)` that lie inside are non-local ones. Since `y_N = y_N E^loc` and the pieces of a stage are orthogonal,
`y_N F = y_N E^loc F = 0` directly, so `beta^{m(N)}_{N1} = 0` without the pair-additivity argument. (Verified by `check.py`: `y_N (I + a F) = y_N` exactly.) This is where the placement of `E_2` between `T_N` and the LOCAL piece of `m(N)` matters, and it is why H7 appears in (b).

**Lemma 5 (support).** `x_p, y_p` lie in range/co-range of `E^loc`, and `E^loc = M E^loc M` (Lemma 1), so `supp x_p`, `supp y_p`, and every nonzero entry of `E^loc x`, `y E^loc` lie in the coordinates of `M_{m(p)}`.

**Multilinear top coefficient.** Take the window `(1, N)` (the scalings in gaps `1..N-1`). Only `m(N)` has `p = N`; set `a_m = 0` for stages outside `S_in`.
Then `g_{N1} = c prod_{S_in}(1 + a_m)` and
`c = sum over choices of one in-window piece e_m for each m in S_in of y_N tau(e) x_1`, with `tau(e)` the time-ordered product of the chosen pieces.
Pieces outside gaps `1..N-1`, including the slot between `T_N` and the LOCAL piece of `m(N)`, do not enter. (Verified on random non-commuting pieces.)

**Proof of (c).** If `S_in` is empty at most one thick stage exists and its mask is a common coordinate set. Otherwise under H6a every `tau(e)` is a product of pairwise commuting idempotents, each `E_e = M_m E_e M_m`,
so `tau = M_m tau = tau M_m` for every `m in S_in` (move the factor of `m` to the left or the right), hence `tau = M^cap tau M^cap` with `M^cap = prod_{S_in} M_m` a coordinate projector.
`c != 0` because `g_{N1}` is a nonzero monomial (Lemma 3, `g_{N1} g_{1N} = -1`); this gives a coordinate `f in M^cap` with `y_N(f) != 0`. By Lemma 5, `supp y_N` lies in `M_{m(N)}`, so `f` lies in every mask. (If `T_N` is thin all thick stages are in `S_in`.) ∎

**Proof of (a).** Special case of (c): single-piece stages have `E = M_m`, which commute. ∎ (Equivalently, the unsplit argument below.)

**Lemma 6 (unsplit hub).** With every stage scaled once, `Lam_win = prod_{S_in}(I + a_m M_m)` is diagonal, `g_{N1}` has top coefficient `sum_{f in ∩_{S_in} M_m} y_N(f) x_1(f) = c != 0`, so some `f` lies in all masks of `S_in` with `y_N(f) != 0`, and Lemma 5 puts `f` in `M_{m(N)}`.

**Proof of (b).** `Lam_win` has at most one non-diagonal factor. Write `Delta = prod_{S_in, single}(I + a_m M_m)` (commuting coordinate factors).
* *X, both pieces of `P` inside the window.* By Lemma 2 the stages strictly between them commute with both; the pieces merge, `Lam_win = Delta (I + a M_P)`, diagonal, and the argument of Lemma 6 applies with `M_P` added to `S_in`.
* *Y1, `E_1` inside, `E_2` outside.* If `E_2` is at gap 0, the stages between `E_2` and `E_1` commute with `E_1` (Lemma 2) so `Lam_win = Delta (I + a E_1)`. If `E_2` is at gap `N` (H7: not between `T_N` and the LOCAL piece of `m(N)`), the stages between `E_1` and `E_2`, including `m(N)`, commute with `E_1`, so `Lam_win = (I + a E_1) Delta`. The top coefficient is `sum y_N(f) (E_1 x_1)(f)` or `sum (y_N E_1)(f) x_1(f)` over `f` in all `M_m`, `m in S_in`; every nonzero term has `f in M_P` (as `E_1 = M_P E_1 M_P`) and `f in M_{m(N)}` (from `y_N(f) != 0`, or from `y_N E_1 = y_N E_1 M_{m(N)}` by Lemma 2).
* *Y2, `P = m(N)`, `E_1` at gap `N`, `E_2` inside.* The stages after `E_2` in the window commute with `E_2`, so `g_{N1} = y_N (I + a E_2) Delta x_1` and `y_N E_2 = y_N E_1 E_2 = 0`; the top coefficient is `sum y_N(f) x_1(f)` over the common coordinates of `S_in`, and `supp y_N` lies in `M_P`.
* *Z, both outside (`P = m(N)`).* `Lam_win = Delta`; same.

In every case the common coordinate lies in every mask, including `M_P`. ∎

**The triangle does not help.** The one place a split could help is a stage `P` whose non-coordinate piece `E_1` sits between the shears of `Q` and `R` whose masks share a coordinate `c` outside `M_P`
(`M_Q = {b,c}`, `M_R = {a,c}`, `M_P = {a,b,d}`). Then `g_{RQ} = D_Q [y_R x_Q + a_P y_R E_1 x_Q]` would have to be `c' D_Q D_P`, forcing `y_R E_1 x_Q != 0`; but Lemma 2 makes `E_1` block-diagonal on `{a} + {b,d}` and `y_R E_1 x_Q = 0` identically. Contradiction (checked).

**Proof of Lemma M.** (⇐) If `T'_j = M T_j M^{-1}` then `prod T'_j = M (prod T_j) M^{-1} = -I`, because `prod T_j = -I` (it is the `Q = -1` replay at `D = 1`) is independent of `D`.
(⇒) `Z` has rank one (Lemma 3), so the factorisations `X K^{-1} Y = I_n`, `X' K'^{-1} Y' = I_n` of the same rank-`n` matrix `J` are unique up to `GL_n`; the diagonal `Delta` with `G' = Delta G Delta^{-1}` is read off the first column of `Z`, and `M` is the `GL_n` element carrying `X` to `X' Delta`. `check.py` builds `M` this way on the chains and checks `T'_j M = M T_j`. ∎

## Exact checks (`check.py`, `verify.sh`, about one second)

Everything is recomputed in exact rational arithmetic (own Laurent polynomial class, standard library only) from the shear vectors of the 1|1 and 2|2 chains embedded in `check.py`.

* Chains (1|1) (`n=4`, `N=5`) and (2|2) (`n=6`, `N=7`): replay `W(+1) = D^w`, `W(-1) = -D^w`; all `N(N-1)/2` Gram entries `g_ij` are single monomials with `g_ij g_ji = -1`, additive exponents, and exponent pattern `[j <= p_m < i]`;
  `g_{N1} = prod D_m` over the thick stages before the last shear, the top coefficient equals `sum y_N(f) x_1(f)` over the common coordinates of those stages, and the common carrier is coordinate 0 (the hub) in every mask.
* Lemma M on both chains: `Z` rank one, `G' = Delta G Delta^{-1}`, an invertible `M(D)` with `M(1) = I` and `T'_j = M T_j M^{-1}` for all `j`, `det M` a monomial (`D_0^2` and `D_0^4 D_1^3`), solution space one-dimensional (at a random rational point, which bounds the generic dimension).
* Multilinear formula: on 6 random non-commuting piece configurations (`n = 4, 5`, stages with 2, 2, 3 pieces) the top coefficient equals the sum over one-piece-per-stage choices of `y tau x`.
* H6a configurations (pieces commuting by construction, including three split stages): `tau = M^cap tau M^cap` for every choice; hub-free masks give `c = 0`; with a hub `c != 0` is seen.
* H6a-violating control: `n = 4`, hub-free masks `{0,1,2}, {1,2,3}, {0,3}`, non-commuting cross-stage pieces; the formula gives `c != 0` and `tau != M^cap tau M^cap`. This is not a counterexample to the theorem (the master identity is not imposed); it shows H6a is what makes the formula force a hub.
* The commutation identity of Lemma 2, the triangle contradiction, and `y_N (I + a F) = y_N`.

Marker: `PASS_P104_ROOT_HUB_FORCING`.

## Remark (one mid-slot configuration; not part of the theorem, no checker here)

For `n = 4`, `N = 5`, the triangle masks `M_Q = {b,c}`, `M_R = {a,c}`, `M_P = {a,b,d}`, shears in the order `(Q, R, P) = (2, 5, 3)`, and `E_2` in the mid slot at gap 5 (after `T_5`, before the LOCAL piece of `R`),
an exact reduction shows that no hub-free word exists. The LOCAL piece of `R` and `E_2` drop out of the replay, and `W = -D^w` is equivalent to three conditions:
`T_5 T_4 T_3 T_2 T_1 = -I`, `[M_Q, T_2 T_1] = 0`, `[E_1, T_3 T_2 T_1] = 0`.
The second makes `T_1` block diagonal, with `T_1` on `{b,c}` (Case I) or on `{a,d}` (Case II). Case II is excluded by a rank argument (`T_5 T_4 T_3 = -C^{-1}` with `C` unipotent, so `I - T_5 T_4 T_3` is invertible of rank at most 3). In Case I, a Groebner basis computation (random gauge, rank-one atomic `E_2`) returns `{1}` over `Q` and modulo 32003.
Caveats: this covers that single configuration only; Case II is a hand argument; the Groebner step had no positive control (the feasible-control runs did not finish). The `E_2` placed after the LOCAL piece adds `[E_1, M_R] = 0` to the system, so it is infeasible a fortiori.
The general mid slot with a non-commuting `E_1` stays open (question 2). `check.py` does not cover this remark, since the elimination needs a computer algebra system outside the allowed tools.

## Open next questions

1. Interleaved, non-commuting in-window pieces of two or more split stages (H6a fails). Smallest hub-free candidate: `n = 4`, `N = 5`, masks `{0,1,2}`, `{1,2,3}`, `{0,3}`. The `Q = +1` replay does not force commutation.
2. The mid slot (second piece between `T_N` and the LOCAL piece of `m(N)`) with a first piece that does not commute with a coordinate stage before it, beyond the single n = 4 triangle configuration of the remark.
3. Non-atomic LOCAL (`x_p` or `y_p` leaving the mask).
4. Unsaturated header (`N = n+2`), where `Z` has rank two.
5. Non-coordinate masks and `Q`-dependent frame operations.

The structured form with first steps and blockers is in `TASK.json`.
