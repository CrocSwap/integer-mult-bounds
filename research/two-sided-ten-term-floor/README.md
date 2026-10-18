# Decoder floors: the smallest two-sided case (m = 10, one outside direction per side) costs ≥ 64 on P112 — conjecture K3 of #2832 (no κ claim)

**Status: research note. No κ claim, no supplier word, no new floor beyond the single class below.** Every claim is a written proof in this file plus exact finite computations that `verify.sh` re-runs
(about 12 minutes wall unloaded (696 s measured; about 22 minutes under heavy load), at most 4 parallel processes (`JOBS=2` runs two at a time), each under `timeout 1200`, no SAT solver). Only `research/two-sided-ten-term-floor/` is added; nothing existing is changed.

Labels: **PROVEN** (written proof here; finite inputs listed), **CHECKED** (exact script in `checks/`, re-run by `verify.sh`, asserted in `checks/check_logs.py`),
**FROM #n** (a statement of another PR, cited, not re-derived), **CONDITIONAL on #n** (depends on a PR that is not merged), **RECORDED** (not re-run).

## 0. Result

**Theorem K3.** Let `(P, Q)` be a decoder of `N₀ = G/2` on P112 (dense h = 9 table) with `m = 10` terms, two-sided with `(s, t) = (1, 1)` (§1), and *normalised*: every `p_k, q_k ≠ 0` and no two `p`'s and no two `q`'s are proportional (Lemma D of #2338).
Then `cost(P, Q) ≥ 64`. No assumption on `J_P ∩ J_Q` (disjoint or not) is made.

**Dependencies.** CONDITIONAL on the open PR **#2816** only, entering through #2832: Lemma 3.1 of #2816, the cover facts (C1), (C3) and `g(5) = 12` of #2816 and the completeness of its 1200-direction list (these underlie #2832 Lemmas 3.8–3.9, Theorem 3.5, Corollary 3.6 and the twelve-overlap check of §3.6).
**Not used:** #1212, #2724 (so none of #2832 Corollary 3.4), #2826, any disjointness hypothesis, and the disjoint closure #2832 Theorem 3.13 (it is covered again here; it may be cited as an independent proof of that sub-case).
**Tight:** two exact cost-64 decoders in the class, one with `J_P ∩ J_Q = ∅` and one with `|J_P ∩ J_Q| = 2` (§7).

**Consequence for the map of #2832 (§5 there).** K3 is now a theorem (conditional as stated). With #2832, the P112 master `C(P112) ≥ 64` reduces to **K1** (every two-sided decoder of `N₀(P112)`, general `m, s, t`) and **K2** (excess pays for corrections, one-sided) only. Nothing is claimed about K1, K2 or P120.

## 1. Setting, imports, notation

**Setting (#2832 §1–§2).** Lines `t ∈ L` (112 lines of P112); `C ∈ ℚ^{L×8}` with `N₀ = CCᵀ`, row `t` of `C` equal to `c_t/2`, where `c_t ∈ {0, ±1}⁸` has four non-zero entries (frame coordinates of the root, supports are the 14 blocks of the Steiner system S(3,4,8), CHECKED `caseb4.py`) and `⟨c_t, c_s⟩ = 2⟨r_t, r_s⟩ ∈ {0, ±2, ±4}`; `Off(y) = supp(Cy)`.
Labels `u_t ∈ F₂⁹` with the nondegenerate symmetric form `Ω`, `Bd[t,s] = Ω(u_t, u_s)`, `Bd[t,s] = 1` iff `t = s` or `t ⊥ s`. The eight frame roots `f_1..f_8` (the lines of E8 outside P112) have labels `z_i`; since `Bd` is the table of all of E8, **`Ω(z_i, z_j) = 1` for all `i, j`** and `Ω(z_i, u_t) = 1` iff `t ⊥ f_i` iff `c_t[i] = 0`. Put `W_i := z_i^⊥` (a hyperplane), so `z_j ∉ W_i` for all `i, j`, and labels of distinct E8 lines are distinct.
For a set `S` of lines: `U_S = span u(S)`, `w(S) = dim U_S`, `Z_S = U_S^⊥`; `O_z := {t : Ω(u_t, z) = 1}`; `g(w)` = largest number of lines whose labels lie in a `w`-flat.
`ρ(R, A) := rank_{F₂} Bd[R, A] = w(R) − dim(U_R ∩ Z_A) = w(A) − dim(U_A ∩ Z_R)` (symmetric, `Bd` is symmetric).

**Decoders (#2832 §2.2).** `p_k = C x_k + x2_k E`, `q_k = C y_k + y2_k F` (`k = 1..10`; `E, F ∉ col C`), with `X̂Ŷᵀ = diag(I₈, 0)`, i.e.
`Σ_k x_k y_kᵀ = I₈`, `Σ_k y2_k x_k = 0`, `Σ_k x2_k y_k = 0`, `Σ_k x2_k y2_k = 0`. `J_P = {k : x2_k ≠ 0}`, `J_Q = {k : y2_k ≠ 0}`. `R_k = supp p_k`, `A_k = supp q_k`, `cost_k = ρ(R_k, A_k)`. A term outside `J_P` has *inside row*, outside `J_Q` *inside column*.
The transpose `(Q, P)` is again a normalised (1,1), `m = 10` decoder of the symmetric `N₀`; every statement about columns below holds for rows, and conversely ("by transposition").

**Imports (all FROM #2832, which cites #2816 and #2338; statements only).**
* **(F1)** (#2816 Lemma 3.1) For `y ∈ ℚ⁸∖0`, `U_{Off(y)} = F₂⁹` unless `y ∝ e_i`, and then `U_{Off(y)} = W_i`. So an inside row/column has weight 9, or weight 8 with `U = W_i`.
* **(F2)** (#2832 Lemma 2.3) In a normalised decoder `|J_P|, |J_Q| ≥ 3`. (Each row restriction `p(t)|_{J_Q}` lies in the kernel of `Y₂[:,J_Q]`; if `|J_Q| ≤ 2`, all `p_k`, `k ∈ J_Q`, are proportional.)
* **(F3)** (#2832 Theorem 3.5 and the twelve-overlap check of §3.6, `d4.py`) *Catalogue.* Let `λ` be an outside vector of the coset with `w(supp λ) ≤ 5` (so `|supp λ| ≤ g(5) = 12`), and `p_k = x2_k(λ + Cη_k)` another outside row, `η_k ≠ 0`. If `w(R_k) = 8`, i.e. `p_k` vanishes on `O_z` for a class `z` with `U_{R_k} = z^⊥`, then `|Off(η_k) ∩ O_z| ≤ |supp λ ∩ O_z| ≤ 12`, and: either **frame type** (`η_k ∝ e_i`, `z = z_i`) or **root swap** (`η_k ∝ c_v`, `z = u_v`, `v ∈ supp λ`, `supp λ ∩ O_{u_v} = {v}`). The twelve-overlap sets have label span of dimension 7 and do not fit in `supp λ`.
* **(F3′)** (#2832 Corollary 3.6, stated there from F1 alone, without the weight hypothesis of F3) For outside columns (rows, by transposition) of the coset with distinct `η`, a non-frame class `z` lies in `Z_{A_k}` for at most one `k`.
* **(F4)** (#2832 Lemmas 3.7–3.9) Among outside columns there is at most one of weight ≤ 6, and then no other column of weight ≤ 7; otherwise at most two columns have weight ≤ 7 and both have weight 7.

Fact used with its proof in §3 (Lemma S): a root swap row is `p_k = x2_k(λ + α C c_v)`, where `(C c_v)(t) = G_{tv} = ⟨r_t, r_v⟩` is non-zero exactly at `v` (value 2) and at the lines non-orthogonal to `v`; it vanishes on `O_{u_v} = {v} ∪ v^⊥` iff `α = −λ(v)/2` and `supp λ ∩ O_{u_v} = {v}`.

## 2. Normal form (PROVEN)

**Lemma N.** Let `a ∈ J_Q`, `a′ ∈ J_P`, `a ≠ a′` (possible by F2). After rescaling terms (`(p_k, q_k) ↦ (c p_k, c⁻¹ q_k)`) and moving the outside directions, `y2_a = x2_{a′} = 1` and
`p_k = C x_k + x2_k λ`, `q_k = C y_k + y2_k μ` for all `k`, with `λ := p_{a′}`, `μ := q_a` (outside vectors), `x_{a′} = 0`, `y_a = 0`. The eight **dual terms** `l ∉ {a, a′}` satisfy `⟨x_l, y_{l′}⟩ = δ_{ll′}` (`(x_l)` a basis of ℚ⁸, `(y_l)` its dual basis), and
`x_a = −Σ_l y2_l x_l`, `y_{a′} = −Σ_l x2_l y_l`, hence `⟨x_a, y_l⟩ = −y2_l`, `⟨x_l, y_{a′}⟩ = −x2_l`.
*Proof.* Put `Ŷ′ = SŶ`, `S = [[I₈, −y_a/y2_a],[0, 1]]`, and `F′ = F + C y_a/y2_a = q_a/y2_a`. Then `X̂ Ŷ′ᵀ = diag(I₈,0)·Sᵀ = diag(I₈,0)` and `[C F′]Ŷ′ = [C F]Ŷ` (since `[C F′]S = [C F]`): the same matrix `Q`, written with `y_a = 0` and outside direction `μ := F′`. Likewise on the `P` side with `x_{a′}` and `λ`. Terms `a, a′` then contribute `0` to `Σ x_k y_kᵀ = I₈`, so the other eight form a dual-basis pair; the circuits `Σ y2_k x_k = 0`, `Σ x2_k y_k = 0` give the formulas for `x_a`, `y_{a′}` (`x_{a′} = 0 = y_a`). All `p_k, q_k` are non-zero: `C x_l ≠ 0`, `λ ∉ col C`, and `x_a ≠ 0` because some dual `l ∈ J_Q∖{a′}` exists (`|J_Q| ≥ 3`), so `x_a = −Σ y2_l x_l ≠ 0` (the `x_l` are independent). ∎
Consequence: `y2_l ≠ 0` for a dual column that is outside, and outside rows/columns lie in the cosets `λ + 𝒞`, `μ + 𝒞` (`𝒞 = col C`) with `η_k = x_k/x2_k`, `η_k = y_k/y2_k`; normalised ⇒ the `η` of different outside rows (columns) are distinct.

## 3. Accounting (PROVEN)

**Savings.** `d^R_k := 9 − w(R_k)`, `d^A_k := 9 − w(A_k)`, `c_k := dim(U_{R_k} ∩ Z_{A_k}) ≤ d^A_k`, `c′_k := dim(U_{A_k} ∩ Z_{R_k}) ≤ d^R_k`, `s_k := 9 − cost_k = d^R_k + c_k = d^A_k + c′_k ≤ d^R_k + d^A_k`.
`cost = 90 − Σ_k s_k`, so **cost ≤ 63 ⇔ Σ s_k ≥ 27** (E1).

**Row profiles and D̂ (L1).** By F1 inside rows have `d^R ≤ 1`. Call an outside row *low* if its weight is ≤ 7. By F4 (rows, by transposition) exactly one of four profiles occurs:
| profile of low rows | `D̂_P` | `Σ_k d^R_k` |
|---|---|---|
| one low row of weight `9 − D ≤ 6` (`D ≥ 3`), no other low | `D` | `D + (9 − ζ_P)` |
| two low rows, both weight 7 | 3 | `2 + 2 + (8 − ζ_P)` |
| one low row, weight 7 | 2 | `2 + (9 − ζ_P)` |
| no low row | 1 | `10 − ζ_P` |

where `ζ_P` = number of non-low terms with `d^R = 0` (non-low terms have `d^R ≤ 1`). So `Σ d^R = D̂_P + 9 − ζ_P` in every profile; `D̂ = D` for `D ≥ 3`, `D̂ ∈ {2,3}` for `D = 2`, `D̂ = 1` for `D ≤ 1`. Same for columns (`D̂_Q`, `ζ_Q`). With `Λ := Σ_k (d^A_k − c_k) ≥ 0`:
**cost = 72 − D̂_P − D̂_Q + ζ_P + ζ_Q + Λ** (E2), so with `σ := D̂_P + D̂_Q − 9`:
**cost ≤ 63 ⇒ σ ≥ 0 and ζ_P + ζ_Q + Λ ≤ σ** (E3). In particular **(L1) cost ≤ 63 needs D̂_P + D̂_Q ≥ 9**; (4,4) and everything smaller is closed here.

**Lemma S (swap slots).** Let `λ` be the low outside row vector with `w_P := w(supp λ) ≤ 5`. Root-swap rows (type of F3) of different terms have pairwise distinct lines, pairwise non-orthogonal, and their labels are `Ω`-orthonormal in `U_{supp λ}`; hence at most `w_P` terms have a root-swap row (the term carrying `λ` itself does not count). Same for columns with `μ`, `w_Q`.
*Proof.* Two swap rows at the same line `v` both lie in `span(λ, Cc_v)` and vanish at `v`, so they are proportional (excluded). Every swap line `v` has `supp λ ∩ O_{u_v} = {v}` (F3), so for swap lines `v ≠ v′` we get `v′ ∈ supp λ∖{v}`, hence `Bd[v, v′] = 0`: `Ω(u_v, u_{v′}) = 0`, `Ω(u_v, u_v) = 1`. An orthonormal family is independent, and lies in `U_{supp λ}`. ∎

**Lemma F (frame/frame).** If a term has `d^R = d^A = 1` and both its row and column are of frame type (`U_R = W_i`, `Z_A = ⟨z_{i′}⟩`) then `s = 1`, because `z_{i′} ∉ W_i`. Hence, when F3 applies on both sides, **`s_k = 2` forces a root swap on at least one side of term `k`**.

## 4. Cells with a low side, `min D̂ ≤ 3` (PROVEN; finite part CHECKED)

**Theorem LOWD.** A normalised (1,1), `m = 10` decoder in which some side has `D̂ ≤ 3` (a unique low of weight 6, one or two lows of weight 7, or no low) costs ≥ 64, for every `K = J_P ∩ J_Q`.

*Proof.* Suppose cost ≤ 63. By (L1) the other side has `D̂ ≥ 6`; by transposition it is `P`: a unique low row `a′` with `D_P ≥ 6`, `w_P = 9 − D_P ≤ 3`; and `D̂_Q ≤ 3`. Then `σ = D_P + D̂_Q − 9 ≥ 0` and `w_P + σ = D̂_Q`.
Fix `a ∈ J_Q∖{a′}` and the normal form of Lemma N at `(a, a′)`; `λ = p_{a′}`.

*Step 1 (dual rows).* A dual row has `d^R ∈ {0, 1}`; if `d^R = 1`, by F1 (inside) or F3 (outside) it is a **frame row** (`x_l ∝ e_i`; normalise `x_l = e_{i_l}`) or a **root swap**. Let `F` be the set of dual terms with frame rows; the `i_l` are distinct (the `x_l` are independent); `I := {i_l}`, `I^c := [8]∖I`. Then `|I^c|` = #(swap rows) + #(rows with `d^R = 0`) ≤ `w_P` + ζ_P (Lemma S).
Call `l ∈ F` **lossless** if `d^A_l ≥ 1` and `c_l = d^A_l` (i.e. `Z_{A_l} ⊆ U_{R_l} = W_{i_l}`; here `U_{R_l} = W_{i_l}` by F1, or by F3 for an outside frame-type row). A term of `F` that is not lossless contributes ≥ 1 to `ζ_Q + Λ` (either `d^A_l = 0`, a non-low column, or `d^A_l − c_l ≥ 1`); terms of `F` have `d^R = 1`, so they are not counted in `ζ_P`. By (E3),
(#rows with `d^R = 0`) + (|F| − #lossless) ≤ ζ_P + ζ_Q + Λ ≤ σ, whence
**#lossless ≥ 8 − w_P − σ = 8 − D̂_Q ≥ 5** and **|I^c| ≤ w_P + σ = D̂_Q ≤ 3**.

*Step 2 (a lossless column is outside, in a non-frame class).* Let `l` be lossless, so `Z_{A_l} ≠ 0` and `Z_{A_l} ⊆ W_{i_l}`. If the column were inside, F1 gives `y_l ∝ e_{i′}`, `⟨x_l, y_l⟩ ≠ 0` forces `i′ = i_l` and `Z_{A_l} = ⟨z_{i_l}⟩ ⊄ W_{i_l}`: contradiction. So `y2_l ≠ 0`, `q_l = y2_l(μ + Cη_l)`. Pick `z_l ∈ Z_{A_l}∖0`; `z_l ∈ W_{i_l}`, so it is **not a frame class**, and `q_l` vanishes on `O_{z_l}`. For `l ≠ l′` lossless, `z_l ≠ z_{l′}` (F3′; `η_l ≠ η_{l′}` since `y_l, y_{l′}` are independent).

*Step 3 (linear constraints).* Duality `⟨e_{i_{l′}}, y_l⟩ = δ_{ll′}` for `l′ ∈ F` gives **`η_l ∈ span(e_{i_l}, e_{I^c})` and `η_l[i_l] ≠ 0`**. For `l ≠ l′` lossless both columns vanish on `Θ := O_{z_l} ∩ O_{z_{l′}}`, so `μ = −Cη_l = −Cη_{l′}` there:
**`⟨c_t, η_l − η_{l′}⟩ = 0` for `t ∈ Θ`**, with `η_l − η_{l′} ∈ span(e_{i_l}, e_{i_{l′}}, e_{I^c})` having non-zero `i_l` and `i_{l′}` coordinates.

*Step 4 (finite test, CHECKED).* For `I^c` with `|I^c| ≤ 3` let `V = {(i, z) : i ∈ I, z ∈ W_i∖0}` (255 classes per `i`; no frame class lies in `W_i`), with an edge `(i,z) ~ (i′,z′)` iff `i ≠ i′`, `z ≠ z′` and some `h ∈ span(e_i, e_{i′}, e_{I^c})` has `⟨c_t, h⟩ = 0` on `O_z ∩ O_{z′}` and `h_i ≠ 0 ≠ h_{i′}`. Step 3 turns the lossless terms into a clique with distinct `i`, which also passes the **joint test** (one exact solution of all pair systems with every `η_l[i_l] ≠ 0`; solvable iff every coordinate functional is non-zero on the kernel, exact rational arithmetic). Steps 1–3 give such a clique of size ≥ 5.
`clique2.py 5` (exact, sympy): on **every** `I^c` with `|I^c| ≤ 3` (1 + 8 + 28 + 56 = 93 sets; no symmetry used) there is **no 5-clique passing the joint test**. The independent re-implementation `verify_cl.py` (compatibility from exact `Bd`-ranks, edges by the row-space criterion, networkx maximal cliques) agrees on the four orbit representatives:

| `I^c` | vertices | edges | largest clique |
|---|---|---|---|
| `∅` | 2040 | 3584 | 2 |
| `{0}` | 1785 | 2856 | 2 |
| `{0,1}` | 1530 | 9648 | 2 |
| `{0,1,2}` | 1275 | 16496 | 4 (7936 maximal 4-cliques) |

(`stab.py`, `sym.py`: the frame stabiliser acts on the 8 coordinates as AGL(3,2), order 1344, 3-transitive, one orbit per size ≤ 3, and preserves the family `{O_z}` and the compatible classes; this only explains why the four representatives are typical, the 93 direct runs do not use it.)
A clique of size ≥ 5 does not exist: contradiction. ∎
The margin is structural: the largest clique is 4 < 5.

## 5. Cells with both sides high, `min D̂ ≥ 4` (PROVEN)

Here both sides have a unique low of weight ≤ 5: `a′` the low row (`D_P ≥ 4`, `λ = p_{a′}`, `w_P = 9 − D_P ≤ 5`), `a` the low column (`D_Q ≥ 4`, `μ = q_a`). F3 applies on both sides, so Lemmas S and F hold. Every other term has non-low row and column, `d^R, d^A ≤ 1`, `s ≤ 2`.

**Theorem H.** (ii) If `a ≠ a′`: `Σ s ≤ 26`, so `cost ≥ 64`. (i) If `a = a′ =: b` and `D_P + D_Q ≥ 9` (the cell `(4,4)` is closed by (L1)): `Σ s ≤ 36 − cost_b − (D_P + D_Q)`; so `cost ≥ 64` unless `cost_b = 0` and `D_P + D_Q = 9`, i.e. `(D_P, D_Q) ∈ {(4,5), (5,4)}`, which Proposition B closes.

### 5.1 `a ≠ a′` (Theorem H(ii))
Take the normal form at `(a, a′)`. `Σ s = s_a + s_{a′} + Σ_{dual} s_l`. By F1/F3 a term has `d^R = 1` only with a frame or root-swap row (same for columns); `s_a = D_Q + c_a`, `c_a := dim(U_{A_a} ∩ Z_{R_a}) ≤ d^R_a ≤ 1`; `s_{a′} = D_P + c_{a′}`, `c_{a′} := dim(U_{R_{a′}} ∩ Z_{A_{a′}}) ≤ 1`. A dual term has `s ≤ 2`, and `s = 2` needs a swap on one side (Lemma F). Let `N₂` be the number of dual terms with `s = 2`: `Σ s ≤ D_Q + c_a + D_P + c_{a′} + 8 + N₂`, and `N₂ ≤ (#dual row swaps) + (#dual column swaps) ≤ w_P + w_Q` (Lemma S), `D_P + w_P = D_Q + w_Q = 9`. **It remains to pay for `c_a` and `c_{a′}`:** `N₂ ≤ w_P + w_Q − c_a − c_{a′}`.
* `c_a = 1`, row of `a` of frame type `x_a ∝ e_j` (`Z_{R_a} = ⟨z_j⟩ ⊆ U_μ`). For a dual column swap `l` (`y_l ∝ c_v`, `v ∈ supp μ`, `y2_l ≠ 0`): `0 ≠ −y2_l = ⟨x_a, y_l⟩` gives `c_v[j] ≠ 0`, i.e. `u_v ∈ W_j`. Since `Ω(z_j, z_j) = 1`, `z_j ∈ U_μ∖W_j`, so `dim(U_μ ∩ W_j) = w_Q − 1` and **dual column swaps ≤ w_Q − 1** (α).
* `c_a = 1`, row of `a` a root swap at `v₀`: it occupies one of the `w_P` row slots: **dual row swaps ≤ w_P − 1** (β).
* `c_{a′} = 1` is symmetric: column of `a′` of frame type `f_i` (`z_i ∈ U_λ`): dual row swaps lie in `W_i ∩ U_λ`, **≤ w_P − 1** (α′); or a column swap: **dual column swaps ≤ w_Q − 1** (β′).
* If both are 1 and the losses fall on different sides, `N₂ ≤ w_P + w_Q − 2`. They fall on the same side in the pairs (α, β′) and (β, α′). In (α, β′): the dual column swaps and `u_{v₀}` (`a′`'s own swap line) are `Ω`-orthonormal in `U_μ`; if there were `w_Q − 1` dual swaps, together with `u_{v₀}` they would be an orthonormal basis of `U_μ`, the dual ones lie in `W_j`, so `z_j ∈ U_μ` would equal `Ω(z_j, u_{v₀}) u_{v₀} = u_{v₀}`: a frame label equal to a line label, impossible. So dual column swaps ≤ `w_Q − 2`. (β, α′) is the transpose.
Hence `Σ s ≤ D_P + D_Q + w_P + w_Q + 8 = 26`. ∎

### 5.2 `a = a′ = b` (Theorem H(i)), `D_P + D_Q ≥ 9`
`Σ s = s_b + Σ_{9 others} s_k ≤ (9 − cost_b) + 9 + N₂`, where `N₂` (# others with `s = 2`, each with a swap, Lemma F) `≤ w_P + w_Q = 18 − D_P − D_Q`. This gives the bound of H(i): `≤ 26 − cost_b` if `D_P + D_Q ≥ 10`, and `≤ 27 − cost_b` if `D_P + D_Q = 9`. So `Σ s ≥ 27` forces `D_P + D_Q = 9` (with both `≥ 4`: `(4,5)` or `(5,4)`), `cost_b = 0`, `N₂ = 9`. ∎

### 5.3 Proposition B: `a = a′ = b`, `cost_b = 0`, `D_P + D_Q = 9` is impossible (PROVEN; CHECKED corroboration)
**Setup.** Shear both sides at `b` (it lies in `J_P ∩ J_Q`; Lemma N's shear on each side): `x_b = y_b = 0`, `p_b = λ`, `q_b = μ`, and the nine other terms satisfy `Σ_{k≠b} x_k y_kᵀ = I₈`. `cost_b = ρ(supp λ, supp μ) = 0` means `Bd[supp λ, supp μ] = 0`: every line of `supp λ` is non-orthogonal to every line of `supp μ`, hence `⟨c_u, c_v⟩ = ±2 ≠ 0` for such pairs, and `U_λ ⊥ U_μ`. Here `(w_P, w_Q) ∈ {(5,4), (4,5)}`.
By the equality case of Theorem H(i): all nine other terms have `s = 2`, each has a swap, and `#row-swap terms + #column-swap terms ≤ w_P + w_Q = 9` (Lemma S) with at least one swap per term forces: **no term has two swaps, exactly `r := w_P` terms are *R-terms* (root-swap row) and `c := w_Q` are *C-terms* (root-swap column)**, `r + c = 9`. A term with `d^A = 1` that is not a swap has a frame column (pure outside is proportional to `q_b`, excluded):
* R-term `k`: `x_k = a_k c_{u_k}`, `y_k = e_{j_k}`, `u_k ∈ supp λ`, `a_k ≠ 0` (swap line, F3).
* C-term `l`: `x_l = e_{i_l}`, `y_l = b_l c_{v_l}`, `v_l ∈ supp μ`, `b_l ≠ 0`.
Identity (★): **`I₈ = A + B`**, `A := Σ_R a_k c_{u_k} e_{j_k}ᵀ`, `B := Σ_C b_l e_{i_l} c_{v_l}ᵀ`. Let `J = {j_k}`, `I = {i_l}` (as sets; indices may repeat).

**Case 1: some index repeats** (`|J| < r` or `|I| < c`). `A` has non-zero columns only in `J`, `B` non-zero rows only in `I`, so `8 = rank(A + B) ≤ rank A + rank B ≤ |J| + |I| ≤ 8`. Hence equality throughout: exactly one index repeats, exactly twice, and `rank A + rank B = 8`.
*Then `A, B` are complementary idempotents:* `ℚ⁸ = im A + im B` (as `v = Av + Bv`) and the dimensions add up, so the sum is direct. For `y ∈ im A`: `By = y − Ay ∈ im A ∩ im B = 0`. Thus `BA = 0` (and `A² = A`).
Say the repeated index is a `j` (R side; the C side is symmetric). Then `|J| = r − 1 ≥ 3` and `|I| = c`, so there is a column index `j ∈ J` hit by a single R-term `k` and a row index `i` hit by a single C-term `l`. The `(i, j)` entry of `BA = Σ_{l,k} a_k b_l ⟨c_{v_l}, c_{u_k}⟩ e_{i_l} e_{j_k}ᵀ` is the single product `a_k b_l ⟨c_{v_l}, c_{u_k}⟩ ≠ 0`: contradiction with `BA = 0`.

**Case 2: no index repeats** (`|J| = r`, `|I| = c`). By transposing `(★)` (roles `R, J, r ↔ C, I, c`) we may assume `r = 5`, `c = 4`.
* A column `h ∉ J` has `A e_h = 0`, so `e_h = B e_h ∈ span(e_i : i ∈ I)`: `J^c ⊆ I`. As `|J^c| = 3` and `|I| = 4`: `I = J^c ∪ {m}` with a unique `m ∈ J`.
* A row `ρ ∉ I`, i.e. `ρ ∈ J∖{m}`, has `e_ρᵀ = e_ρᵀ A`: for the R-term `k` with `j_k = j`, `a_k c_{u_k}[ρ] = δ_{jρ}`. So `c_{u_k}[ρ] = 0` for `ρ ∈ J∖{m, j_k}`, and `c_{u_k}[j_k] ≠ 0` when `j_k ≠ m`.
* The R-term with `j_k = m` has `supp c_{u_k} ⊆ J^c ∪ {m} =: B₀` (4 points), so `supp c_{u_k} = B₀` is a block. Any other R-term `k` has `supp c_{u_k}` a 4-subset of the 5-set `B₀ ∪ {j_k}` containing `j_k ∉ B₀`, hence containing at least 3 points of `B₀`; three points lie in a unique block (S(3,4,8)), so `supp c_{u_k} = B₀ ∋ j_k`: contradiction.
So Proposition B holds. ∎
**CHECKED corroboration.** `diag9.py`: for each of the 280 pairs `(J, m)` (`|J| = 5`, `m ∈ J`) some column `j ∈ J` has no root with `supp ⊆ J^c ∪ {m, j}` (the finite content of Case 2, 0 candidates for all 280). `caseb4.py` (chunked, 22,020,096 linear-core solutions): the case `r = 5` with one repeated column and `c = 4` distinct rows (singles with `supp ⊆ I ∪ {j}`) has **no** configuration with `s = 2` at both repeated terms (`lin_s2 = 0`) and none with pairwise non-orthogonal lines (`full = 0`); it enumerates one orientation of Case 1, and is not used in the proof.

### 5.4 A second proof for `(4, ≥5)` with distinct lows (Case A; PROVEN, CHECKED `d4A*.py`)
Not needed (Theorem H(ii) already covers it) and kept because its finite check ships. Let `D_Q = 4`, `D_P ≥ 5`, `a ≠ a′`, `σ = D_P − 5`. Run Steps 1–3 of §4 with the roles of `D̂_Q` as 4: `#lossless ≥ 4`, `|I^c| ≤ 4`. The column catalogue (F3 transposed, `μ` with `w = 5`) says a lossless column (non-frame class) is a **column root swap**, `η_l ∝ c_{w_l}`, `w_l ∈ supp μ`; with `η_l ∈ span(e_{i_l}, e_{I^c})` and `η_l[i_l] ≠ 0`, `supp c_{w_l} = {i_l} ∪ T_l`, `T_l` a 3-subset of `I^c`. By S(3,4,8): `|I^c| = 3` gives one block, so `i_l` are equal: ≤ 1 lossless; `|I^c| = 4` a block gives 0; so `I^c` is a **non-block 4-set**, the four 3-subsets give four blocks, `#lossless = |I^c| = 4`, all slack is used (`ζ_P = σ`, no other loss). Then `d^R_a = 1`, and `a`'s row cannot be a swap (`w_P` slots are taken), so `x_a = γ e_m` is a frame vector.
`x_a = −Σ_l y2_l x_l = −Σ_{lossless} y2_l e_{i_l} − w`, `w ∈ W^⊥ := span` of the four non-frame dual rows `= (span c_{w_l})^⊥` (duality, `y_l ∝ c_{w_l}`), and `W^⊥ ∩ span(e_I) = 0` (the `x_l` are a basis); all `y2_l ≠ 0`.
(a) `m ∈ I`: `w ∈ span(e_I) ∩ W^⊥ = 0` so `x_a = −Σ y2_l e_{i_l}` has four non-zero entries: not a frame vector.
(b) `m ∈ I^c`: `γ e_m + Σ y2_l e_{i_l} ∈ W^⊥` is orthogonal to every `c_{w_l}`: `γ c_{w_l}[m] + y2_l c_{w_l}[i_l] = 0`, so `m ∈ supp c_{w_l}` for all four `l`, i.e. `m ∈ ∩ T_l`, but the four 3-subsets of a 4-set have empty intersection.
**CHECKED:** `clique2.py 4` on the non-block set `I^c = {0,1,2,4}` finds 16128 joint-feasible 4-cliques; `d4A.py`: 128 are column-swap configurations passing the non-orthogonality and joint `β` system; `d4A2.py`: `{0,1,2,3}` is a block (so `{0,1,2,4}` is the non-block orbit; `stab.py`: two orbits of 4-sets); `d4A3.py`: **0 of the 128** admit a frame row for term `a`. ∎

## 6. Coverage: every cell of `(D̂_P, D̂_Q)` has a proof

`D̂` as in §3 (`D̂ = D` for `D ≥ 3`; `D̂ ∈ {2, 3}` for `D = 2`: one weight-7 low gives 2, two weight-7 lows give 3; `D̂ = 1` for `D ≤ 1`). By transposition only unordered cells matter.
| cell | proof |
|---|---|
| `D̂_P + D̂_Q ≤ 8` (includes `(4,4)`) | (L1), §3: `cost ≥ 72 − D̂_P − D̂_Q` |
| `min D̂ ≤ 3`, sum ≥ 9 (so `max D̂ ≥ 6`): `(1..3, 6..8)` | Theorem LOWD, §4 (any `K`, `a = a′` or not) |
| both `≥ 4`, lows in different terms (`a ≠ a′`) | Theorem H(ii), §5.1 (for `(4, ≥5)` also §5.4) |
| both `≥ 4`, one term is the low of both sides, `D_P + D_Q ≥ 10`, or `cost_b > 0` | Theorem H(i), §5.2 |
| both `≥ 4`, `a = a′`, `cost_b = 0`, `D_P + D_Q = 9`: `(4,5)`, `(5,4)` | Proposition B, §5.3 |
A cell with `min D̂ ≥ 4` has unique lows (F4) of weight ≤ 5, which is what §5 uses; `D = 3` (a weight-6 low, `|supp| ≤ 20`, F3 not available) is a `D̂ = 3` cell and is covered by §4. The disjoint sub-case also has the independent proof #2832 Theorem 3.13.

## 7. Tightness (CHECKED `witness16.py`)

Starting from the two-sided root-swap family (one row swap and one column swap, each with its own outside direction, cost 64; #2832 §3.7), frame terms are inflated with outside components that cancel at the swap line, and the `δ`-term's inside part is re-solved. Both decoders have `P Qᵀ = N₀` on **all** `112²` entries, `m = 10`, no proportional `p`'s or `q`'s, and cost exactly 64:
* **disjoint:** `|J_P| = |J_Q| = 3`, `J_P ∩ J_Q = ∅`, cost 64, `Σ(s − 1) = 16`.
* **shared:** `|J_P| = 4`, `|J_Q| = 3`, `|J_P ∩ J_Q| = 2`, cost 64.
Both have `Σ s = 26`, equal to the bound of Theorem H(ii) (`c_a = c_{a′} = 0`, `N₂ = w_P + w_Q = 2` with `D_P = D_Q = 8`): the bound 64 is attained inside the class, and the proof is exact there.

## 8. What is and is not claimed
* **Claimed:** Theorem K3 (§0), CONDITIONAL on #2816 as listed; the coverage of §6; tightness at 64.
* **Not claimed:** anything for `m ≥ 11`, `(s, t) ≠ (1, 1)` (K1), the one-sided excess statement (K2), P120, or any κ.
* The proofs of §5 use the catalogue only through F3 on both sides; §4 uses it on one side and F1 on the other. No SAT solver and no random search enters any claim.

## 9. Reproduce

`bash verify.sh [/fresh/output/dir]` (Python ≥ 3.10 with numpy, sympy, networkx: `requirements.txt`; `PYTHON=` to choose; `timeout`/`gtimeout` if present). Phases, each stream a serial list under `timeout 1200` and `nice -n 10`, at most 4 processes: 0 manifest; 1 (`clique.py` → `null.pkl` | three `caseb4.py` chunks, plus the small scripts); 2 (four `clique2.py 5` chunks over the 93 sets `I^c`); 3 (`clique2.py 4`, `d4A.py`, `d4A2.py`, `d4A3.py` | `verify_cl.py` on four representatives, two streams | `sym.py`, `stab.py`); 4 `check_logs.py` asserts every number quoted above as PASS/FAIL.

| Claim | Script |
|---|---|
| compatible classes (255 per `i`), 35400 pairs with deficient `Θ`-rank | `clique.py` |
| no 5-clique on any of the 93 `I^c` (|I^c| ≤ 3) | `clique2.py 5` |
| independent clique table (2, 2, 2, 4) | `verify_cl.py` |
| AGL(3,2) of order 1344 preserves `{O_z}`, compat | `stab.py`, `sym.py` |
| S(3,4,8) supports; `diag9`: 280 pairs, 0 candidates | `caseb4.py`, `diag9.py` (`enum9.py`, `lib2.py`) |
| single repeated column, `r = 5`: 22,020,096 solutions, 0 valid | `caseb4.py` (3 chunks) |
| §5.4 chain: 16128 → 128 → 0 | `clique2.py 4`, `d4A.py`, `d4A2.py`, `d4A3.py` |
| exact cost-64 witnesses | `witness16.py` (`swapfam.py`, `lib.py`) |

Data: `data/data.json` (labels, frame coordinates, E8 roots of P112), identical to the file of #2832.

## Maintainer verification correction

The original `clique.py` pruned full-rank matrices using floating-point SVD,
and `verify_cl.py` used it for row-space decisions. Those decisions now use
integer elimination modulo 65537. The inputs have at most eight columns and
entries in {-1,0,1}; Hadamard bounds every square minor in absolute value by
4096, strictly below this prime. Thus modular and rational ranks agree exactly.
The routine rejects inputs outside this proved domain. This change preserves
the catalogue and the full search scope; it does not assume that a floating
rank classification was correct.

The auxiliary repeated-column computation now clears its Gram denominators and
compares integer numerators, and the diagonal-private-coordinate check tests
that structure directly. These replace numerical tolerances/determinants.
The shell wrapper now propagates a manifest/check-log command failure even when
the failing command did not print a `FAIL` line. Original submitted sources are
retained in the maintainer review archive. Full replay of the corrected package
is required before incorporation; #2816's stated dependencies remain inherited.
