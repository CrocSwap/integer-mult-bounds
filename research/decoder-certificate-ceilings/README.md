# Ceilings for linear rank-counting certificates on the E8 decoder cost, and a one-sided lift bound (no kappa claim)

> **Scope, stated first.** Pure finite combinatorics on the E8 root lines and the units P112, E7, E6. **No kappa claim**, no window, no supplier. Two results: **Theorem C**, a ceiling on a named family of linear rank-counting (orthogonal-set / Hall-charging) lower-bound certificates for the decoder cost, with an explicit fractional "fake decoder" witness; and **Lemma S**, a lower bound `cost_w(S) >= 72` for large lifts of the E8 span. Neither proves or disproves the decoder floor 72 for the E8 unit (P120); Theorem C says that one natural proof shape cannot reach it.
> Labels: **PROVEN** (argument below), **CHECKED** (recomputed by `verify.sh`, exact arithmetic unless marked), **MILP-COMPUTED** (floating-point HiGHS, integral optima rounded), **OPEN**.
> **Credit.** The charging / orthogonal-set certificate shape (`rank N0[C,C'] <= #terms meeting (C,C')`, cliques `C = C'`) is that of #1977 (Lemma 2) and #798; #968 supplies the P104 pair setting that is not computed here. The cost model (terms `p_k q_k^T`, `rho(R,A) = rank_F2 Bd[R,A]`) is the repository's. The definitions of the families below are our formalisation of that shape and may differ in detail from the authors' statements (see 1.3).

## 1. Setting

`L` = the 120 root lines of E8, `G` their Gram matrix (roots of norm 2), `Bd[t,s] = 1` iff `t = s` or `t` is orthogonal to `s`, `N0 = G/2`. The decoder cost of a factorisation `sum_k p_k q_k^T = N0` over a field of characteristic 0 (any number of terms) is `sum_k rho(R_k, A_k)`, `rho(R,A) = rank_F2 Bd[R,A]`, `R_k = supp p_k`, `A_k = supp q_k`. A term with a single entry `(t,s)`, `t` and `s` not orthogonal, has `rho = 0` ("cost-0 term"). A *frame* is a maximal set of pairwise orthogonal lines (8 lines in E8; 2025 of them). Units: P120 = E8 (120 lines), P112 = E8 minus one frame (112 lines), E7 (the 63 lines orthogonal to a line), E6 (the 36 lines orthogonal to an A2); for a unit `T = rank_Q N0` (8, 8, 7, 6).

## 2. Theorem C (ceiling of the family F)

**Family F.** Weights `lambda_{C,C'} >= 0` on rectangles of lines, dual-feasible: for every support pair `(R,A)`, `sum over (C,C') with R∩C ≠ ∅ and A∩C' ≠ ∅ of lambda_{C,C'} <= rho(R,A)`. Since `N0[C,C'] = sum_k p_k[C] q_k[C']^T`, `rank N0[C,C'] <= #{k : term k meets (C,C')}`, so every factorisation has cost `>= sum lambda_{C,C'} rank N0[C,C']`. (Averaging over the automorphism group keeps feasibility, so F contains every orbit-type LP.) The value of F is the maximum of that sum.

**Theorem C.** Every certificate in F on the stated unit gives at most

| unit | ceiling | true floor targeted | binding set |
|---|---|---|---|
| P120 (E8) | **360/17 = 21.18** | 72 | full frame, 765 frames meet it |
| P112 | **15968/757 = 21.09** | 64 | orthogonal 8-set, 757 |
| E7 | **945/71 = 13.31** | 49 | 7-frame, 71 |
| E6 | **12** | 36 | 4-frame, 45 |

*Proof (PROVEN + CHECKED).* Fake decoder `y`: weight `y_u` on each frame (resp. maximal orthogonal set) `F` of the unit, with `R = A = F`, `Bd[F,F]` all ones, `rho = 1`; and weight `T` on every cost-0 single-entry term, `rho = 0`. Here `y_u = max_D |D| / meet(D)` over all orthogonal sets `D`, where `meet(D)` is the number of frames meeting `D`; this is `8/765` for P120. Feasibility of every rectangle `(C,C')`: if `C x C'` contains a non-orthogonal pair `(t,s)`, `t ≠ s`, the cost-0 term `(t,s)` alone has weight `T >= rank N0[C,C']`. Otherwise all off-diagonal pairs of `C x C'` are orthogonal, `N0[C,C']` is a partial identity on `D = C∩C'` (an orthogonal set), of rank `|D|`, and every frame meeting `D` meets `(C,C')`, so `y_u meet(D) >= |D|`. Weak duality: `sum lambda rank N0[C,C'] <= sum_rect lambda sum_{terms meeting} y = sum_terms y sum_{rects met} lambda <= sum y rho`, and the right side is `#frames * y_u` (the cost-0 terms contribute 0). `verify.sh` enumerates all 352,875 orthogonal sets of E8 (262,928 for P112, 13,743 for E7, 981 for E6) and recomputes every `meet(D)` and the ceilings as exact fractions (`checks/thmC.py`; E8 meets `135, 255, 363, 459/461, 549, 629, 701, 765` for `|D| = 1..8`). The ceilings for P112, E7, E6 use the maximal orthogonal sets of the unit (1996, 135, 135 of them) in place of the 2025 frames. ∎

**Why this is not a decoder.** The witness is fractional and sees only orthogonal-or-diagonal entries (frame terms) and non-orthogonal entries (cost-0 terms): exactness over Q of the orthogonal-pattern part forces rank 120, i.e. at least 120 frame terms, so the witness is not a factorisation. Counting arguments see `rank N0[C,C'] <= 8` but not that the orthogonal-pattern part has Q-rank 120 while the charge is an F2-rank.

### 2.1 Correction: F does not cover #1977 Lemma 2 / #798 as stated; the larger family F'

An independent audit established that F, as defined above, forces `lambda = 0` on every rectangle that contains a non-orthogonal pair, hence it is orthogonal-set counting only; it therefore **does not contain** the clique certificates of #1977 Lemma 2 / #798 as originally stated. Those drop the zero-cost terms and credit a set `D` with `m(D) <= min(T, |D|)`. The corresponding larger family **F'** (cost-0 terms dropped, value of a set `D` bounded by `min(T, |D|)`) needs, for a uniform fake decoder with weight `y` on the maximal orthogonal sets, `y * meet(D) >= min(|D|, T)` for **every** set `D` of lines, not only orthogonal ones. Ceilings for F':

| unit | ceiling for F' | status |
|---|---|---|
| P120 | **<= 24** (`y = 8/675`, 2025 frames) | PROVEN by a Bonferroni bound on `meet(D)` (`meet(D) >= a1*k - a2*(#orthogonal pairs of D)`, where `a1` = least number of maximal orthogonal sets through a line (135; 134 for P112), `a2` = most through an orthogonal pair (15), and no maximal orthogonal set contains a non-orthogonal pair; combined with the exact minima of `meet` over orthogonal `k`-sets and `y = 8/(a1*8 - a2*27)`) and CHECKED (`checks/fprime_bonferroni.py`) |
| P112 | **<= 15968/667 = 23.94** | same |
| E7 | **<= 945/68 = 13.90** | **MILP-COMPUTED** (HiGHS; minimum of `meet(D)` over all `k`-sets, `k <= 7`: 15, 27, 37, 45, 55, 62, 68; `checks/fprime_milp.py`) |
| E6 | **<= 405/31 = 13.06** | **MILP-COMPUTED** (minima 15, 27, 37, 45, 55, 62) |

All are far below the targets 72 / 64 / 49 / 36. **OPEN:** whether the sharper value 360/17 (resp. 15968/757, ...) also bounds F'. The conclusion "linear counting certificates of this shape cannot prove the floors" is supported by the table, but the exact optimum of F' is not claimed. Certificates of other kinds (mixed char-0 / F2 objects, nonlinear or integer counting) are not covered.

## 3. Lemma S (one-sided lifts)

Notation. `u_t in F2^9` is the label of line `t` (coordinates of the root in a simple-root basis reduced mod 2, with a constant coordinate), so that `Bd[t,s] = Omega(u_t,u_s)` for the F2 form `Omega`. `C(E8)` is the 8-dimensional span of the root-coordinate rows in `K^120`. For a subspace `S` of `K^120` and a basis `{v_k}`, `w_k = dim span{u_t : t in supp v_k}` and `cost_w(S)` is the minimum of `sum_k w_k` over bases.

**Lemma S.** For every subspace `S ⊇ C(E8)` with `dim S >= 23` (put `e = dim S - 8 >= 15`): `cost_w(S) >= 72`. The bound is tight in the following sense: the counting relaxation below attains equality at `e = 15` (`sum d = 135 = 9e`) and fails for `e <= 14`.

*Proof (PROVEN, with CHECKED finite inputs).* Take a basis of `S` (`8+e` vectors), `d_k = 9 - w_k`, call `k` low if `d_k >= 1`; `cost = 9(8+e) - sum d_k >= 72` iff `sum d_k <= 9e`. Let `F_k = {t : u_t in U_k}` be the flat of the span `U_k` of the labels in `supp v_k`; `supp v_k ⊆ F_k`.
1. (Rado) For a set `J` of low vectors with `H = ∪_J F_k`, the `v_k` (`k in J`) are independent in `S ∩ K^H`, and `dim(S ∩ K^H) = dim S - dim pi_{L∖H}(S) <= 8 + e - rk(L∖H)`, because `pi_{L∖H}S ⊇ pi_{L∖H}C(E8)`, of dimension the root rank of `L∖H`. So `rk(L∖H) <= 8 + e - |J|`.
2. A subspace of dimension `8-i` contains at most `63, 36, 20, 12, 6, 3, 1, 0` lines (`i = 1..8`): lines in a subspace form a root system of rank at most `8-i` (E7, E6, D5, D4, A3, A2, A1; classification of root subsystems). Hence if `|J| = e+i` then `|H| >= g(i) = 57, 84, 100, 108, 114, 117, 119, 120`.
3. `|F_k| <= f(d_k)` with `f = 64, 36, 20, 12, 8, 4, 2, 1` for `d = 1..8`: the maximum number of labels in an affine subspace of codimension `d` of `F2^8`. CHECKED over all 417,199 subspaces (`checks/lemmaS_flats.py`).
4. `|∪_J F_k| <=` sum of sizes, so the `e+i` smallest flats satisfy `sum f(d) >= g(i)`. The maximum of `sum d_k` under these constraints with at most `8+e` low vectors is `<= 9e` for every `e in [15,112]` (CHECKED, exact dynamic programme `checks/lemmaS_dp.py`; for `e >= 64` it is trivial since `sum d <= 8(8+e)`). ∎

*Limits.* For `e <= 14` the size relaxation allows `sum d > 9e` (e.g. 18 vs 9 at `e = 1`; 127 vs 126 at `e = 14`), so a set-level (not size-only) Rado argument would be required there. Lemma S is one-sided: it says nothing about two-sided decoders, where cost-0 terms make the other factor arbitrary.

## 4. What is not claimed

* Nothing about the true E8 floor beyond the one-sided Lemma S; no kappa.
* The value of F' on P120, P112 beyond the proven ceilings 24 and 23.94; the E7/E6 values for F' are solver-computed.
* Orbit-LP completeness for F: the ceilings are upper bounds from an explicit feasible witness, not optima of F.
* P104 and the Eisenstein unit are not treated.

## 5. Reproduce

`bash verify.sh` (about 9 minutes; `PYTHON=` points at an interpreter with numpy and scipy). Step 0 checks `MANIFEST.sha256`. Scripts in `checks/`: `geom.py` (E8 lines, orthogonal sets, F2 rank), `units.py` (the four units), `thmC.py`, `fprime_bonferroni.py`, `fprime_milp.py` + `fprime_wrap.py`, `lemmaS_flats.py`, `lemmaS_dp.py`. The scripts are an independent re-implementation of the original computations.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0.
