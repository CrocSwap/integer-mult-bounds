# Decoder floors, case (b) for every number of terms: one-sided P112 decoders cost ≥ 64 without corrections (unique optimum) and with ≤ 2 non-full corrections (no κ claim)

**Status: research note; every claim below is a written proof plus exact finite computations that `verify.sh` re-runs (about 12–15 minutes, two processes, no SAT solver). No κ claim, no supplier word.**
Only `research/one-sided-decoders-all-m/` is added; nothing existing is changed.

Labels: **PROVEN** (written proof in this file, every finite input listed), **CHECKED** (an exact script re-run by `verify.sh`, assertion in `checks/check_logs.py`), **RECORDED** (a log shipped in `evidence/logs`, not re-run),
**IMPORTED** (a merged result of this repository, cited from its statement and not re-derived here), **OPEN**.

## 0. Claims box (scope is part of the claim)

Setting (the model of #2338 / #2277 / #2724 / #1224): the 112 lines of P112 (E8 minus the frame F0), the dense F2-pairing `B` of rank 9, a decoder `N = Σ_{j ≤ m} p_j q_jᵀ` of the **Gram realisation** of the masked pattern,
over a field `K` of **characteristic 0**, cost `Σ_j rank_F2 B[R_j, A_j]`. **Case (b):** the factors `q_j` lie in `col M` (`q_j = C y_j`), the factors `p_j` are arbitrary (one side outside `col M`). **Every `m`.**

| # | Statement (P112, case (b), every `m`) | Status |
|---|---|---|
| R1 | **ε-free** one-sided decoders (no correction subtracted) cost **≥ 64** for every `d = dim(𝒞 ∩ S_{≤7})`, `d = 1..8` | PROVEN from CHECKED (§4); exact integer LP dual certificates for `d = 7, 8` (`lp3.py`), independently re-derived (`symlp.py`) |
| R2 | **Theorem U′.** The cost-64 ε-free decoder is **unique**: the coordinate decoder (8 terms `(e_j, W_j)`). Cost-65 decoders have `n_nf ≤ 1`; the cost-66 case is reduced to six OPEN `d = 8` weight multisets (§5.3) | PROVEN from CHECKED (§5) |
| R3 | **Corrections.** Lemma P: a full corrected term is free (absorbed at no cost). Corrected cost `≥ 64` whenever `n_nf ≤ 2`; in general `≥ 64 − max(0, n_nf − 2) ≥ 58` (`n_nf ≤ 8`). The **root-swap family attains 64 exactly** for `n_nf = 1, 2, 3, 4` (tightness of `Δ ≥ n_nf`) | PROVEN from CHECKED (§6); tight family exact `P·Y = C` (`rootswap.py`) |
| R4 | **Lift level.** Every `S ⊇ 𝒞_{X_I}` has `cost_w(S) ≥ 64 + min(|I|, 2)`; every lift of the E8 root code has `cost_w ≥ 66` | PROVEN from CHECKED (§7); needs char 0 |
| R5 | **Lemma N** (exact, two independent implementations) and the **Pencil Lemma** | CHECKED / PROVEN (§8) |

Here `n_nf` is the number of corrected terms that are not full (`U ≠ F2^9`) **of the normalised decoder**: merge corrected terms with proportional `y` and absorb full corrected terms (Lemma P), repeating until stable (Theorem A); then `n_nf ≤ 8`. Lemma P's projection can create new non-full corrections, so the raw count can rise; the version that holds for raw decoders is the lift-level form R4 (`≥ 64` if `|I| ≤ 2`, `I` = all corrected terms).
The gain-law reading (philippeVV, Discussion #1587 follow-up 6, `gain(L) = |L| − C(L)`): R1 says that in the one-sided class (ε-free) the gain on P112 is at most 48 (`112 − 64`); the kill shot needs `gain ≤ 48` for all line sets, equivalent to `C(P120) ≥ 72`. This note makes no claim beyond the class stated.

**Open residue, stated exactly (not claimed).** `Δ ≥ n_nf` for `n_nf ≥ 3`, i.e. corrected cost `≥ 64` with ≥ 3 non-full corrections. At `n_nf = 3` the only unkilled configurations are **exactly six `d = 8` multisets of the weight-≤7 basis of `T = S_{≤7}`**:
`[7^5,6^5,1]`, `[7^6,6^4]`, `[7^8,5,4,1]`, `[7^8,5,5]`, `[7^8,6,3,1]`, `[7^8,6,4]` (reproduced by `c66.py`, §5.3, §9). Another card of the author (SIX) is working on them; **nothing about them is claimed here.**

**Not covered:** two-sided decoders and case (c) (rank-9 realisations; see #2784 for the A2 family); P104 and other punctured units; `B` of rank ≥ 10; fields of positive characteristic (the char-0 steps are marked).

## 1. Overlap and credit

Scanned: titles of the 1,000 most recent PRs, bodies of the 119 decoder-related ones, and the 100 most recently updated Discussions. No PR or Discussion contains an ε-free one-sided floor for all `m`, LP / charging certificates, uniqueness of the optimal P112 decoder,
the root-swap family, Lemma N or a lift-level statement. Nearest work: **#1224** (joaqcoo; one-sided nine-term decoders are overcomplete representations; the model used here), **#1180** (both factors in the root code), **#1633** (excess-rank budget `s + t ≤ m − 8`),
**#1815 / #1609** (rigidity of one-sided masked fits), **#2338 / #2277 / #2724** (ours: `col M` floors and case (b) at `m = 9`), #2582 / #2659 / #2719 (root-code factors only), the COPY-power PRs (different cost model).
Credit: philippeVV (gain law), #1224, #1633, #1180, #1815, #2338, #2277, #2724. No file is copied from another contributor.

## 2. Imported results and one classical fact

* **C1 (Gram realisation; imported from merged #1212, Theorem 1).** On P112, every realisation `K` of rank ≤ 8 with `K_ii = 4` and zeros on orthogonal pairs equals `D·(2G)·D⁻¹` (`G` the Gram matrix), over any field of characteristic 0; a one-line diagonal normalisation turns any rank-8 realisation of the iff pattern into `D₁·Gram·D₂`. Diagonal scalings do not change supports, hence not cost. The work below is in the Gram realisation `c_t = (⟨r_t, f_i⟩)_i`. (#1815 gives the one-sided fitting corollary; credit there.)
* **C2 (dense pairing; imported from merged #2338, Theorem R).** Every fitting `B` of F2-rank ≤ 9 equals the dense table `B_d[t,s] = Ω(ℓ_t, ℓ_s)` (DRAT-checked in #2338). The shape of `B_d` is recomputed here (`chk1.py`).
* **C3 (flats of the root system; PROVEN).** For a subspace `V ⊆ R⁸`, `Φ ∩ V` (`Φ` = E8) is `W(E8)`-conjugate to a standard parabolic subsystem `Φ_J`. *Proof.* Choose `φ ∈ V^⊥` with `φ(α) ≠ 0` for every root `α ∉ V` (finitely many hyperplanes to avoid). Then `Φ ∩ V = {α : φ(α) = 0}`, the root system of the pointwise stabiliser of `φ` in `W`, which is a parabolic subgroup (Bourbaki, Lie V §3.3: the stabiliser of a point is generated by the reflections it contains and is conjugate to a standard `W_J`; VI §1.7: its root system is the corresponding `Φ_J`). ∎ Used by `flats_classify.py`.
* **C4 (char 0).** Used where "the lines inside a K-subspace of dimension u form a root subsystem of rank ≤ u": the 120 lines are rational vectors, so the rank of a set of lines is the same over `Q` and `K`. This fails in positive characteristic.

Everything else below is proved in this file or computed by `verify.sh`.

## 3. Setting, the (y,U) form and the lift S (PROVEN)

**Lines and labels.** `c_t ∈ Q⁸` (`FC` in the code) is the row of the Gram realisation: `c_t = (⟨r_t, f_i⟩)_{i=1..8}`, entries in `{0, ±1}`, support 4 for every `t` (`chk1.py`). Labels `ℓ_t = (1, r̄_t) ∈ F2 ⊕ E8/2E8 = F2⁹`, form `β((a,x),(b,y)) = ab + ⟨x,y⟩` (mod 2); `B_{ts} = β(ℓ_t, ℓ_s)`; `z_i := (1, f̄_i)`, `W_i := z_i^⊥`.
(`chk1.py`: the 112 labels are distinct and span `F2⁹`; `κ`-formula agrees with the oscommon cost on 300 random term tests.)
The **root code** is `𝒞 = {p_h := (⟨c_t, h⟩)_t : h ∈ K⁸}` (dimension 8), `Off(h) = supp p_h`, `weight(p) := rank_F2 ℓ(supp p)` (≤ 9).

**3.1 Reduction to the (y,U) form.** Case (b): `q_k = C y_k`, so `N = P Yᵀ Cᵀ` and exactness `P Qᵀ = C Cᵀ` is equivalent to `P Yᵀ = C` (`C` has rank 8). Term `k` has `R_k = supp p_k`, `A_k = {s : ⟨c_s,y_k⟩ ≠ 0} = Off(y_k)`, and with dense `B`
`rank B[R_k, A_k] = dim U_k − dim(U_k ∩ ℓ(A_k)^{⊥β})`, `U_k := span ℓ(R_k)`. **Lemma 3.1 (CHECKED, `w8.py`).** The label span of `Off(y)` is `F2⁹` unless `y ∝ f_i`, when it is `W_i`.
*Proof.* If `ℓ(Off(y)) ⊆ H` for a hyperplane `H`, the lines with label outside `H` are all ⊥ `y`, so they have real rank ≤ 7. `w8.py` lists the label hyperplanes whose complement has real rank ≤ 7: exactly the 8 hyperplanes `W_i`, with complement the 56 lines ⊥ `f_i` (rank 7), so `y ∝ f_i`. ∎
Hence **cost `= Σ_k (dim U_k − ε_k)`**, `ε_k = [y_k ∝ f_i and z_i ∈ U_k]` (the *corrections*: for `y_k ∝ f_i` the label span of `A_k` is `W_i = z_i^⊥`, whose `β`-orthogonal is `⟨z_i⟩`; otherwise it is `F2⁹` with orthogonal `0`). Terms with `p_k = 0` or `y_k = 0` cost nothing and are deleted. Corrected terms with `y ∝ f_i` for the same `i` are merged: if both `U` contain `z_i`, `dim(U₁+U₂) − 1 ≤ (d₁−1) + (d₂−1)`, so **at most one corrected term per `i`** (`n_corr ≤ 8`).
The decoder is a pair of matrices with `C = P Yᵀ`; equivalently a set of pairs `(y_k, U_k)` with `c_t ∈ span{y_k : ℓ_t ∈ U_k}` for every line `t` (take `p_k(t) ≠ 0` only if `ℓ_t ∈ U_k`).

**3.2 The lift `S`.** `S := col P ⊇ 𝒞` (as `C = P Yᵀ`). The columns of `P` span `S`, so they contain a basis, and **cost ≥ cost_w(S) := min over bases of S of Σ weight** (ε-free; corrections are handled in §6–7). By the matroid greedy algorithm, `cost_w(S) = Σ_{w=0}^{8} (s − a_w)`, `s = dim S`, `a_w = dim S_{≤w}`, `S_{≤w} = span{p ∈ S : weight ≤ w}`.
**Peeling (PROVEN).** Put `T := S_{≤7}`, `d := dim(𝒞 ∩ T)`, `D := 𝒞 ∩ T`. Since `𝒞 ⊆ S`, `s − a_7 ≥ 8 − dim(𝒞 ∩ T) = 8 − d`; `Σ_{w ≤ 7}(s − a_w) = 8(s − a_7) + cost_w(T)` (all `S_{≤w}` with `w ≤ 7` lie in `T`), and `s − a_8 =: c_8` (the number of weight-9 basis vectors). So
`cost_w(S) = 8(s − a_7) + cost_w(T) + c_8 ≥ 64 − 8d + cost_w(T) + c_8` (★), with `s − a_7 = (8 − d) + x`, `x ≥ 0`. Write `Δ_w := cost_w(S) − 64 = (cost(T) − 8d) + 8x + c_8`, every term ≥ 0 once `cost(T) ≥ 8d` (§4); for a decoder, `Δ := (ε-free decoder cost) − 64 = δ_basis + Δ_w` with `δ_basis := decoder cost − cost_w(S) ≥ 0`.
**Codeword weights (CHECKED, `w8.py`, `gen_targets.py`).** (the directions with `|Off(h)| ≤ 69` have ≥ 43 P112 lines ⊥ `h`, and by `flats_classify.py` + C3 the only flat of rank ≤ 7 with ≥ 43 lines is E7, i.e. `h` is a root or frame direction.) `|Off(h)| ≥ 53` for `h ≠ 0`; `|Off| = 53` for the 112 roots, `56` for the 8 frame directions `f_i`, `≥ 70` otherwise. Every codeword has weight ≥ 8 (`g(7) = 36 < 53`), and weight exactly 8 ⇔ `h ∝ f_i`; the root `p_r` has weight 9.

**3.3 The tables.** `g(w)` := the maximum number of lines whose labels lie in a `w`-dimensional subspace: **`g = (1, 2, 4, 8, 12, 20, 36, 64)` for `w = 1..8`** (CHECKED: `g78.py` for `g(8) = 64`, `g(7) = 36` over all 43,435 seven-dimensional subspaces; `gsmall.py` for `g(6) = 20`, `g(5) = 12`; `g(w) ≤ 2^{w−1}` because all labels lie in the affine hyperplane `a = 1`).
`N_u` := the maximum number of E8 lines in a `u`-dimensional real subspace: **`N = (1, 3, 6, 12, 20, 36, 63)`** for `u = 1..7` (CHECKED by `flats_classify.py` over the standard parabolics, valid by C3; this is an upper bound for P112 too).
In-target capacities (CHECKED, `gT.py`): a label flat of dimension 7 holds at most 32 of the 56 lines of `N(f_i)` and of the 53 lines of `Off(r)`; dimension 6 at most 20.

## 4. R1: the ε-free floor 64 for every d (PROVEN from CHECKED)

**Theorem 1.** For every decoder (every `m`), `cost ≥ cost_w(S) ≥ 64`; and `cost_w(S) = 64` forces `S = 𝒞`.
*Proof.* By (★) it suffices to show **`cost_w(T) ≥ 8d` for every `d`** (then `cost_w(S) ≥ 64 + 8x + c_8 ≥ 64`). Let `q_1..q_a` be a minimum-weight basis of `T` (weights `w_j ≤ 7`), `D = 𝒞 ∩ T`, `λ: T → T/D`. Three necessary conditions on the weight multiset `(w_1..w_a)`, `a = d + e`:

* **(C1) Robust cover.** For `1 ≤ k ≤ d`, delete the `d − k` heaviest pieces; the span of the remaining pieces meets `D` in ≥ `k` dimensions, i.e. contains a `k`-dimensional space `Π` of codewords `p_h`. For `k = 1`: some `Off(h)` is covered by the remaining supports, and `Off(h)` is one of: a frame target `N(f_i)` (56 lines; the cheapest cover is two 7-flats, weight 14), a root target `Off(r)` (53 lines; no pair of flats of dimension ≤ 7 covers it, the cheapest cover has weight 15, and no 3 flats of dimension ≤ 6), or one of the ≥ 70-line targets (`|Off| ≥ 70` by §3.2; needs `Σ g ≥ 70`, weight ≥ 14). These facts are CHECKED: `cover.py` (pair/triple covers: 14 / none / 15), `cover6.py` (no 3-cover of `Off(r)` by flats of dimension ≤ 6), `d7.py` (the 70-line targets are not pair-coverable), capacities `gT.py`; `cover.py`, `cover6.py`, `gT.py` examine one root target `Off(r_0)` and one frame target `N(f_0)`: this suffices because line permutations that are label-linear, preserve inner products and permute the frame targets act transitively on the 112 roots and on the 8 frame targets (`symcheck.py`). The only weight-14 shape with ≥ 3 pieces and `ΣG ≥ 53` for `Off(r)` is `(7,6,1)` (`32+20+1 = 53`; all other weight-14 shapes have `ΣG < 53`); `cover761.py` checks it exactly for **all 112 roots** over all 6- and 7-dimensional label subspaces: at least 9 lines of `Off(r)` stay uncovered, so `W ≥ 15` for ≥ 3 pieces. Capacities: a 7-flat holds at most 32 target lines and a 6-flat at most 20 (`gT.py`; `g(5..7) = 12, 20, 36` are upper bounds for the monotone closure). The DP rule `k1` in `dp3.py` encodes exactly "W ≥ 14 and ΣG ≥ 56, or W ≥ 15 and ΣG ≥ 53 and ≥ 3 pieces and not (3 pieces of weight ≤ 6), or Σg ≥ 70". For `k ≥ 2`: the union of `Off(h)` over a `k`-dimensional `Π` is the set of lines not ⊥ `Π`, which has ≥ `112 − N_{8−k}` lines, so `Σ g(w_j) ≥ 112 − N_{8−k}` over the remaining pieces.
* **(C2) Multiplicity.** Every line is covered by some piece; a line covered by exactly one piece `j` has `c_t ∝ y_j`, and the 112 vectors `c_t` are pairwise non-proportional, so at most one line per piece is covered once: `Σ_j |supp q_j| ≥ 224 − a` for `d = 8`. For `d = 7` (quotient by a normal, at most 3 lines per plane through it, at most one line killed): `≥ 222 − 3a`.
* **(C3) Pair rule.** `a ≥ d + 2` for `d ≥ 2`. If `a = d + 1` (`e = 1`) every pair `(j,l)` gives a codeword `p_{jl} = λ_l q_j − λ_j q_l` covered by two flats of dimension ≤ 7; by `cover.py` / `d7.py` and `|Off| ≥ 73 > 72` the only pair-coverable direction is `f_i` (with weights `(7,7)`); a combination of two different `f`'s has `|Off| ≥ 76`, so all triangles are monochromatic and all `p_{jl}` are proportional to one `p_{f_c}`, yet they span `D` (dimension `d ≥ 2`): contradiction.

`dp3.py P112` enumerates all multisets of weights ≤ 7 and reports the minimum of `cost_w(T)` under (C1)–(C3): **`14, 22, 29, 36, 42, 48, 55, 61` for `d = 1..8`** (CHECKED). This is `≥ 8d` for `d ≤ 6`. `enum.py d 8d` lists every multiset with `cost < 8d` passing the rules (CHECKED, complete recursion): none for `d ≤ 6`, **one for `d = 7`** (`[7,6^8]`, cost 55), **seven for `d = 8`** (`[7,6^9]`, `[7,6^9,1]`, `[7,7,6^8]`, `[7,6^9,1,1]`, `[7,6^9,2]`, `[7,7,6^8,1]`, `[7,7,7,6^7]`; costs 61–63).

* **(LP) These eight are impossible.** Let the pieces be `q_j` with `T`-basis, `C_H := C·(basis of H) = Q M`, where `H ⊆ K⁸` is the `d`-dimensional space with `D = {p_h: h ∈ H}` and `M` is `a × d`. Then `c̄_t := (c_t projected to H) = Σ_j q_j(t) M_j`, so `c̄_t ∈ span{y_j : t ∈ supp q_j}` with `y_j := M_j ∈ K^d`. For each line with `c̄_t ≠ 0` choose a minimal set `M(t)` of pieces with `c̄_t ∈ span(y_{M(t)})`, and let `m_S` be the number of lines with `M(t) = S`. Then:
  (a) `Σ_{S ⊆ U} m_S ≤ N_{|U| + 8 − d}` for every set `U` of pieces (the lines with `M(t) ⊆ U` lie in a K-subspace of dimension `≤ |U| + 8 − d` of `K⁸`; **C4**);
  (b) `Σ_{S ∋ j} m_S ≤ |supp q_j| ≤ g(w_j)`;
  (c) `Σ_S m_S ≥ 112 − N_{8−d}` (lines with `c̄_t = 0` lie in a subspace of dimension `8 − d`): 112 for `d = 8`, 111 for `d = 7`.
  Maximising `Σ m_S` under (a), (b) gives an upper bound; **it is < the need for all eight multisets**: `96.97, 97.97, 97.80, 98.97, 98.97, 98.81, 101.87` (< 112) for `d = 8` and `97.81` (< 111) for `d = 7` (`lp2.py` floats). **Exact certificates:** `lp3.py` builds the LP without symmetrisation and verifies, in exact integer arithmetic, a dual vector `y ≥ 0` with `Aᵀy ≥ 1` (numerators over `10⁴`), whose value `b·y` is the printed bound (`< 112`, `< 111`). **Independent re-derivation:** `symlp.py` is a different formulation (symmetrised over equal-weight pieces, exact by averaging; exact `Fraction` dual repaired against the full-type column) with the same verdicts, and the control `8` pieces of weight 8 gives exactly 112 (so the LP is not vacuous). ∎

So `cost_w(T) ≥ 8d` for all `d`, hence Theorem 1. (E8-restricted variants are not used.)

## 5. R2: uniqueness of the optimum and the cost-65 / 66 classification

**5.1 Theorem U′ (PROVEN from CHECKED).** An ε-free decoder of cost 64 is the coordinate decoder.
*Proof.* Equality in (★) forces `Δ = 0`: `δ_basis = 0` (the columns are a min basis), `x = 0`, `c_8 = 0`, `cost(T) = 8d`. For `d ≤ 5` the DP gives `cost(T) − 8d ≥ 2` (`dp3.py`, `enum.py`: no multiset with cost `8d`, and none with `cost ≤ 8d + 2` for `d ≤ 3`, `land.py`). For `d = 6, 7, 8` the multisets of cost exactly `8d` are listed by `enum.py d 8d+1`; the quotient LP kills `[6^8]` (97.78 < 109), `[7,6^8,1]`, `[7,7,6^7]` and 15 of the 18 multisets at `d = 8` (`eq.py`). The three LP survivors `[7^9,1]`, `[7^8,6,2]`, `[7^8,6,1,1]` (LP value exactly 112) are killed by the **Pencil Lemma** (§8: they have `d = 8 ≥ 3` and `e − 1` anchors on ≤ 4 lines). So `d = 0`: `T = 0`, `s = 8`, `S = 𝒞`, the columns are 8 codewords of weight 8, which are the frame codewords `p_{f_j}` (§3.2) with flat `W_j`. ∎ (CHECKED: `eq.py`, `eq2.py`, `land.py`.)

**5.2 Cost 65 (Theorem Δ1).** `Δ = 1` forces one of: `S = 𝒞` with one weight-9 column (or one surplus unit), `d = 0` with `T = ⟨δ_t⟩` (a unit piece), or an LP/Pencil-killed `d ≥ 1` multiset (`eq2.py`, `land.py`). In the second case the weight-8 columns `p_h + aδ_t` with `a ≠ 0` need `rank ℓ(Off(h) ∖ {t}) ≤ 8`: `h` is a frame direction (flat `W_j` or weight 9) or a root `r_t` with `t` cancelled (`coloop.py`: root targets have exactly one coloop each, and no pair of lines other than the coloop drops the rank to 8; `c65.py`/`coloop2.py`: `N(r)` minus ≤ 3 lines keeps rank 8). So **`n_nf ≤ 1`**: the only possible non-full corrected term is the *root swap* `p_{r_t} − c δ_t` (weight 8, flat `W_t ∋ z_i`).
`c65.py` (cost(T) ≤ 8d + 1, LP): the LP survivors are the `7^k + small` multisets at `d = 7, 8` and `[7^5,6^5]` at `d = 8` (12 in all); the first kind die by the Pencil Lemma, `[7^5,6^5]` by the triple rule below (CHECKED).

**5.3 Cost 66.** `c66.py` (cost(T) ≤ 8d + 2: DP → LP → Pencil → `e = 2` triple rule) leaves **exactly the six `d = 8` multisets** of §0 (CHECKED), and `land.py` independently reproduces the same landscape (survivors only at `d = 8`, slack 2, six of them). *Triple rule (e = 2):* with `e = 2` all `λ_j ∈ K²`, pairs of non-(7,7) pieces are non-parallel (pair rule), so every triple of pieces of weight ≤ 6 is a circuit whose codeword has `Off` inside the union of the three supports: only `N(f_i)` (three 6-flats, `cover6.py`) is possible, at most 8 directions exist and distinct circuits give distinct directions, so ≥ 5 pieces of weight ≤ 6 (10 triples > 8) is impossible (kills `[7^5,6^5]`, and the `d = 6, 7` cases `[7^2,6^6]`, `[7^4,6^5]`).
*Circuit lemma (PROVEN).* A dependency `Σ_J a_j λ_j = 0` is a codeword `p_h ∈ D` supported in `∪_J supp q_j`; minimal supports `J` (circuits) give distinct directions, because the `q_j` are linearly independent.

## 6. R3: corrections

**Lemma P (absorption of a full correction; PROVEN).** Let a decoder in `X_I` form contain the term `(f_i, U)` with `U = F2⁹`, and let `π` be the orthogonal projection killing `f_i`. Then `{(π y_j, U_j) : j ≠ k} ∪ {(f_i, W_i)}` decodes `X_{I∖i}` at the same corrected cost.
*Proof.* Write `c_t = a_t f_i + Σ_{j≠k} p_{tj} y_j` (in frame coordinates, `a_t = c_t[i]`). For `t ⊥ f_i` (this includes the frame lines `f_j`, `j ∈ I∖i`): `c_t = π c_t = Σ p_{tj} π y_j`, with the same label conditions. For `t ∈ N(f_i)`: `c_t = π c_t + (⟨c_t,f_i⟩/2) f_i` and `ℓ_t ∈ W_i`, so the new term `(f_i, W_i)` supplies the `f_i`-component. Terms `(f_j, U_j)`, `j ≠ i`, keep `y = f_j` (`π f_j = f_j`) and their corrections. Cost: the term `(f_i, F2⁹)` cost `9 − 1 = 8` and `(f_i, W_i)` costs `8`; the others do not rise. ∎

**Theorem A (PROVEN).** Corrected cost `≥ 64 − n_nf` for every `m`, with `n_nf` the number of non-full corrected terms of the *normalised* decoder. *Normalisation:* repeat (i) merge corrected terms with proportional `y` (cost never rises, §3.1) and (ii) apply Lemma P to a full corrected term (corrected cost unchanged) until neither applies. It terminates: each step lowers the pair (#terms, #full corrected terms) lexicographically (a merge lowers #terms; Lemma P removes one corrected term and adds none full) and the corrected cost never rises. Lemma P's projection `π y_j` may create new non-full corrected terms (a projected `y` can become proportional to some `f_l`), so `n_nf` is defined after normalisation, not on the raw decoder. *Proof.* On the normalised decoder every corrected term is non-full and keeps `ε = 1`; the ε-free cost is `≥ 64` (Theorem 1), so corrected cost `= ε-free − n_nf ≥ 64 − n_nf`. ∎

**Corollary (main result).** Let `Δ := ε-free cost − 64` after absorption. Then corrected cost `= 64 + Δ − n_nf`, and
* `n_nf ≤ 2` ⇒ **corrected cost ≥ 64** (any number of full corrections): `Δ = 0` forces the coordinate decoder (`n_nf = 0`, Theorem U′), `Δ = 1` forces `n_nf ≤ 1` (§5.2), and `Δ ≥ 2` gives `64 + Δ − n_nf ≥ 64` directly when `n_nf ≤ 2`. In other words `Δ ≥ n_nf` whenever `n_nf ≤ 2`.
* `n_nf ≥ 2` ⇒ `Δ ≥ 2` (since `Δ ≤ 1 ⇒ n_nf ≤ 1`), so **corrected cost `≥ 66 − n_nf = 64 − (n_nf − 2)`**; with `n_nf ≤ 8`, **corrected cost ≥ 58 always**.

**Tightness (CHECKED, `rootswap.py`, exact `P·Y = C` over `Q`).** The **root-swap family**: for `J ⊆ [8]` and roots `r_m` with `supp(c_{r_m}) ∩ J = {j_m}`, take the 8 − |J| frame columns `c^{(j)} (j ∉ J)`, the terms `p_{r_m} − p_{r_m}(r_m) δ_{r_m}` (weight 8, flat `W_{r_m} ∋ z_{j_m}`, `y ∝ e_{j_m}`: a non-full corrected term) and the unit terms `δ_{r_m}`. ε-free cost `64 + k`, `k` corrections, **corrected cost exactly 64**, for `k = 1, 2, 3, 4` (the script finds no admissible `J` with `k = 5`). So `Δ ≥ n_nf` is *tight* at `k ≤ 4` and a proof for `n_nf ≥ 3` must be exact on this family. `rootswap_audit.py` independently scans all weight-≤ 8 carriers of a `z_i` (every `t`, every `|Off| ≤ 65` direction, cancelling or generic shift) and finds exactly the root swaps (0 deviations).

## 7. R4: lift-level form (PROVEN from CHECKED; char 0)

Let `X_I := P112 ∪ {f_i : i ∈ I}` with `ℓ(f_i) = z_i`, `S ⊇ 𝒞_{X_I}`, `B` a min-weight basis of `S`, `ρ` the restriction to P112, `π_F` the projection to the frame coordinates, `drop(b) := w(b) − w(ρb) ≥ 0`, `D := Σ drop`, `Δ := Σ_b w(ρb) − 64`. A corrected P112 decoder with corrected set `I` is an ε-free decoder of `X_I` of cost `+|I|` (put `z_i` into the corrected term: its rank is unchanged and its `−1` disappears), so **corrected cost `= cost(X_I) − |I|`**.
* **Identity** `cost_w(S) = 64 + Δ + D`; **R1** `Δ ≥ 0` (`ρB` spans `ρS ⊇ 𝒞`, Theorem 1).
* **Frame rank.** `π_F(S) ⊇ π_F(𝒞_{X_I}) = K^I` (as `π_F p_h = (⟨f_i,h⟩)_i`), so `|I| ≤ ρ_0 + |B_+|`, `B_+ := {b : drop ≥ 1}`, `ρ_0 := rank π_F(B_0)`, `B_0 := {b : drop 0, π_F b ≠ 0}`. A member of `B_0` has `ρb ≠ 0` and `z_i ∈ ⟨ℓ(supp ρb)⟩`: it is *z-carrying*. Hence **`cost_w(S) ≥ 64 + |I| + (Δ − ρ_0)` and `≥ 64 + Δ`.**
* **`Δ = 0`:** `ρS = 𝒞` (uniqueness, §5.1) and the `ρb` are the frame codewords, whose flats `W_j` contain no `z` (`β(z_i, z_j) = 1`), so `ρ_0 = 0`.
* **`Δ = 1`:** if `cost_w(ρS) = 64`, the nonzero `ρb` are 7 frame codewords and one weight-9 vector, so `ρ_0 ≤ 1`. If `cost_w(ρS) = 65`, peeling and the cost-65 classification (§5.2) give `d = 0`, `T = ⟨δ_t⟩`, and 8 weight-8 vectors `p_h + λδ_t`: `|Off(h)| ≤ 65`, so ≥ 47 P112 lines are ⊥ `h`, which forces an E7 subsystem (D7 has only 42: `flats_classify.py`), `h` a root or frame direction; frame: flat `W_j ∌ z`; root `r_s`, `s ≠ t`: weight 9 (`coloop2.py`); `r_t` with `t` cancelled: the root swap (unique up to scale). So `ρ_0 ≤ 1`.
* **Conclusion.** `Δ ≤ 1 ⇒ ρ_0 ≤ Δ ⇒ cost_w ≥ 64 + |I|`; `Δ ≥ 2 ⇒ cost_w ≥ 64 + Δ ≥ 66`, and `≥ 64 + |I|` if `|I| ≤ 2` (`ρ_0 ≤ |I|`). Therefore **`cost_w(S) ≥ 64 + min(|I|, 2)` for every `I` and every `S ⊇ 𝒞_{X_I}`**, and `≥ 64 + |I|` unless `Δ ≥ 2` and `ρ_0 > Δ`. Corrected P112 cost `≥ 64 − max(0, |I| − 2)`.
* **E8 (`I = [8]`):** every lift of the E8 root code has `cost_w ≥ 66`, and `≥ 72` unless the P112 restriction has excess `Δ ≥ 2`. (Consistent with the decoder-level `≥ 58 + 8`.)
This is the lift-level twin of the decoder-level corollary; the two routes (SMALL2: exchange + uniqueness; OS-CHARGE2: charging + frame rank) agree on `n_nf ≤ 2`. The same open residue appears in both: `Δ ≥ 2` with `ρ_0 > Δ`, i.e. ≥ 3 z-carrying restricted basis vectors with independent frame parts.

## 8. R5: Lemma N and the Pencil Lemma

**Lemma N (CHECKED).** For every 7-dimensional label subspace `F` (43,435 of them) and every set `L` of ≤ 4 P112 lines, at most **2** directions `h ≠ 0` have `rank ℓ(Off(h) ∖ F ∖ L) ≤ 7`.
*Completeness of the direction list (PROVEN from C3 + computation).* A qualifying `h` has `|Off(h)| ≤ 36 + 36 + |L| ≤ 76` (a 7-dim label subspace holds ≤ 36 lines), so ≥ 36 P112 lines are ⊥ `h`; `h^⊥ ∩ E8` is a flat of rank ≤ 7 with ≥ 36 lines: by `flats_classify.py` (C3) it is E7 (63), D7 (42), E6+A1 (37) or E6 (36). Rank 7: `h` is the primitive normal, a lattice vector of norm 2, 4 or 6 (determinant of the standard parabolic: `det = 2, 4, 6`), enumerated by `gen_targets.py` / `gen_t3.py` (counts 120 / 1080 / 3360 directions, matching `|W|/(2|W_J|)`); E6: an A2-pencil, and every one of the 1120 E6 flats contains ≥ 2 frame lines (`flats_classify.py`), so `|Off| ≥ 78`. Values found: root 53, frame 56, D7 70/73/76, E6+A1 ≥ 77: `targets76.txt` (1200 directions) is complete for `|Off| ≤ 76` (CHECKED: `gen_t3.py`; `lnprep.py` regenerates the same 1200 directions independently).
*Counts.* `ncount.c` (|L| = 1, exact, per `(F,t)`): max 2. `ncount2.c` (|L| = 2, exact, per `(F,pair)`): max 2. `mu76.c` (|L| ≤ 4: upper bound `#{h : some X, |X| ≤ 4, with Off(h)∖F∖X inside a 7-dim subspace}`): max 2. **Independent implementation** `lemmaN.c` (own direction list from `lnprep.py`, own minimal-exception-set bookkeeping, triple test): `F checked 43435, max active per F 2, violations 0`. Stronger form checked: the exceptional set `L` may be chosen separately for each direction.

**Pencil Lemma (PROVEN from Lemma N + circuit lemma).** `T` with min basis `q_1..q_a` (weights ≤ 7), `D = 𝒞 ∩ T` of dimension `d ≥ 1`, `λ: T → T/D ≅ K^e`, `e = a − d`; every `λ_j ≠ 0`. If `e − 1` pieces `A` have total support `L` with `|L| ≤ 4`, then `d ≤ 2`.
*Proof.* (1) `λ(A)` is independent: a dependency inside `A` is a codeword with `Off ⊆ L`, but `|Off| ≥ 53`. (2) `λ_x ∉ span λ(A)` for a piece `x ∉ A`: else `Off(h) ⊆ F_x ∪ L`, ≤ 40 < 53 lines. So `B = A ∪ {x}` is a basis of `K^e`. (3) For `y ∉ B` the fundamental circuit `C_y` contains `y` and `x` (else `Off ⊆ F_y ∪ L`, ≤ 40 lines); distinct `y` give distinct directions `h_y` with `Off(h_y) ∖ F_x ∖ L ⊆ F_y` of rank ≤ 7; by Lemma N at most 2 such directions exist. A piece `y` parallel to `x` also gives a circuit `{x,y}`, so all `d` non-anchor pieces other than `x` are counted: `d ≤ 2`. ∎ (Audited step by step; the Lemma N form used holds with a separate `L` per direction, which `lemmaN.c` checks.)

## 9. What remains OPEN (exactly)

1. **`Δ ≥ n_nf` for `n_nf ≥ 3`** (decoder level) and **`ρ_0 ≤ Δ` for `|I| ≥ 3` with `Δ ≥ 2`** (lift level). At `n_nf = 3` the reduction (OS-CHARGE2 §5 / SMALL2 §10, summarised in §6–7) leaves exactly the **six `d = 8` multisets** `[7^5,6^5,1]`, `[7^6,6^4]`, `[7^8,5,4,1]`, `[7^8,5,5]`, `[7^8,6,3,1]`, `[7^8,6,4]` The `d = 0` cases at `Δ = 2` are closed (SMALL2 §10: `T = ⟨δ_t, δ_u⟩` or one 2-piece on `{t,u}`, weight-8 columns are root swaps at `t`, `u` only, so at most 2 root swaps: `n_nf ≤ 2`; the `d = 0, Δ = 1` and `(δ,slack,c_8)` cases with `S = 𝒞` give `n_nf ≤ 1`); the `d = 4..7` cases die by LP + Pencil + triple rule (`land.py`). The remaining multisets are reproduced by `c66.py` and `land.py`; none has `e − 1` anchors on ≤ 4 lines, anchor sizes 5–12 lines; Lemma N would have to be extended to targets with `|Off| ≤ 84`, including E6 pencils where infinitely many directions share an `Off` set, each pencil counting at most 2). Another card of the author (SIX) works on them; no result of it is used or claimed here.
2. Two-sided decoders; case (c); other units; positive characteristic.
3. A proof that the cost-66 survivors do not occur gives `n_nf ≤ 3` ⇒ corrected cost ≥ 64; the root-swap family shows the inequality `Δ ≥ n_nf` cannot be improved beyond that.

## 10. Reproduction

`bash verify.sh [outdir]` (Python ≥ 3.11 with numpy, scipy, sympy; `cc`; two parallel streams, `nice 10`; about 12–15 minutes). Step 0 checks `MANIFEST.sha256`; the computations write one log per check; `checks/check_logs.py` turns every assertion of this file into a `PASS`/`FAIL` line.

| Claim | Script(s) | Assertion in `check_logs.py` |
|---|---|---|
| labels, pairing shape, `κ`-formula | `chk1.py`, `dump.py` (regenerates `data/data.json`) | `dump`, `chk1` |
| weight-8 hyperplanes `W_i` (Lemma 3.1) | `w8.py` | `w8` |
| `g(5..8)` | `g78.py`, `gsmall.py` | `g78`, `gsmall` |
| `N_u`; flats with ≥ 36 lines; E6 flats hold ≥ 2 frame lines | `flats_classify.py` | `flats_classify` |
| direction lists (`|Off| ≤ 73`, `≤ 76`) | `gen_targets.py`, `gen_t3.py`, `lnprep.py` | `gen_targets`, `gen_t3` |
| cover facts (14 / none / 15 / no 3-cover ≤ dim 6), capacities, 70-line targets | `cover.py` (~5 min), `cover761.py`, `symcheck.py`, `cover6.py`, `gT.py`, `d7.py` | `cover`, `cover761`, `symcheck`, `gT`, `d7`, `cover6` |
| DP and enumeration | `dp3.py`, `enum.py` | `dp3`, `enum` |
| LP certificates (exact integer / exact rational) | `lp2.py`, `lp3.py`, `symlp.py` | `lp3`, `symlp` |
| Theorem U′, cost 65 / 66 inputs | `eq.py`, `eq2.py`, `land.py`, `c65.py`, `c66.py`, `coloop.py`, `coloop2.py` | `eq`, `eq2`, `land`, `c65`, `c66`, `coloop`, `coloop2` |
| root-swap family and audit | `rootswap.py` (sympy, exact), `rootswap_audit.py` | `rootswap`, `rootswap_audit` |
| Lemma N | `ncount.c`, `ncount2.c` (~4 min), `mu76.c`, `lnprep.py` + `lemmaN.c` | `ncount`, `ncount2`, `mu76`, `lemmaN` |

`evidence/logs/` holds the logs of the run recorded at packaging time from a fresh `git archive` export (RECORDED; `verify.sh` regenerates them): **34 PASS / 0 FAIL in 714 s** (two processes, `nice 10`; `verify_run.log.txt`, `times.out.txt`). `SOURCES.json` pins every script to its working-card source.
**Caveats.** The finite inputs are exact (integer / `Fraction` / bitmask arithmetic; floats appear only in the unrepaired LP values, whose bounds are re-derived in exact arithmetic by `lp3.py` and `symlp.py`); the written proofs are not machine-checked (no Lean/DRAT). The proofs above were re-derived by a second, independent AI reviewer and key claims are checked by two implementations (LP: `lp3` vs `symlp`; Lemma N: `mu76` vs `lemmaN`; root swaps: `rootswap` vs `rootswap_audit`); no human review is claimed.
