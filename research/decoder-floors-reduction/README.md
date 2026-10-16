# Decoder floors: universality, projection transfer and batching reductions; C(P120) ≥ 72 reduced to named conjectures (no κ claim)

**Status: research note. No κ claim, no supplier word, no new floor for the full problem.** Every claim below is a written proof in this file plus exact finite computations that `verify.sh` re-runs
(about 5 minutes, at most 3 parallel processes, no SAT solver). Only `research/decoder-floors-reduction/` is added; nothing existing is changed.

Labels: **PROVEN** (written proof here; finite inputs listed), **CHECKED** (exact script in `checks/`, re-run by `verify.sh`, assertion in `checks/check_logs.py`),
**FROM #n** (a statement of another PR, cited, not re-derived; where that PR is not merged the dependent claim is marked **CONDITIONAL on #n**), **RECORDED** (a number from the author's cards, not re-run here), **OPEN**.

## 0. The map

**Target.** philippeVV's gain law (Discussion #1587, follow-up 6): the gain `|L| − C(L)` of masked line decoders is monotone under restriction and superadditive under block-diagonal padding. Hence
"decoder optimisation is dead" for every E8 line set is the single statement **C(P120) ≥ 72** (gain ≤ 48). It implies P112 ≥ 64, P111 ≥ 63, P104 ≥ 56 by monotonicity; **the converse direction does not hold**: closing P112 does not close P120.
philippeVV's follow-up 8 closes all *lift* cases of C(P120) ≥ 72 (credit to them) and names residues R1–R4 (§6).

**Structure (new here, §2).** For any E8 line set `L` with the dense h = 9 table, every decoder of every masked realisation is, after adding cost-0 single-entry terms, a decoder of the one matrix `N₀ = G/2` at the same cost.
So `C(L) = min cost over decoders of N₀(L)`; ranks of realisations are not invariants of the problem, and the case split *inside / one-sided / two-sided* **of N₀** is exhaustive.
Because this is a full-class statement it survives the gain-law padding (rank-class statements do not: padding adds rank).

| Slice (P112 unless stated; h = 9 dense table) | Status | Where |
|---|---|---|
| Both factor families in the root code `𝒞 = col N₀` (inside), any `m` | ≥ 64 | #2338 (merged; Theorems P, R) |
| Rank-8 realisations are `D₁ G D₂` (rigidity) | proven | #1212 (merged) |
| One side outside `𝒞`, `m = 9` | ≥ 64; P104 ≥ 56 | #2724 |
| One side outside, every `m`, no corrections | ≥ 64, unique optimum | #2816 |
| One side outside, every `m`, ≤ 2 non-full corrections | ≥ 64; lift level ≥ 64 + min(\|I\|,2) | #2816 |
| … ≤ 3 non-full corrections | ≥ 64 except six weight multisets | #2826 (draft) |
| Rank-9 realisations of E8: classification (B-form / A2 family) | proven | #2819 |
| A2 family, square and `m ≥ 10` | ≥ 64 / 56 / 72 | #2784 (+ B-locus follow-up) |
| Label windows h = 10, 11 | every term ≥ 8 / ≥ 7 | #2639 + #1212 |
| Punctured E8 units (Model C) | closed for p ≤ 46, 48–56, and p = 47 with m ≥ 8 | #2639, #2806 |
| D_n units | floors | #2719 |
| **Every realisation, every rank, any line set ⇒ decoders of N₀** | **PROVEN (§2.1)** | **here** |
| **Two-sided decoders of N₀: outside factors free; Sylvester ⇒ m ≥ 10, m = 10 ⇒ (s,t) = (1,1)** | **PROVEN (§2.2), any line set** | **here** |
| **Two-sided ⇒ one-sided + outside corrections (projection transfer)** | **PROVEN (§3.1)** | **here** |
| **Pivot bound** `cost ≥ 64 − (|I|−2)₊ + Σ_Π cost_k − Σ_{J_Q∖Π} ε_k` | **PROVEN, CONDITIONAL on #2816 R4 (§3.2)** | **here** |
| **Two-sided, `m = 10`, a 2-element circuit on either side** | **≥ 64 (§3.3; from #2724, #2338)** | **here** |
| **Catalogue of outside-column corrections (511 classes × 1200 directions)** | **CHECKED (§3.4)** | **here** |
| **t = 1: pair lemma, low-column collinearity, ≤ 2 weight-7 columns, saving count** | **PROVEN (§3.5; 8.2 CONDITIONAL on #2816 cover facts)** | **here** |
| **Batching ⇒ single-call floor**, except rank-(2,2) multi-diagonal terms; twin-chart fold; fold barrier | **PROVEN / CHECKED (§4)** | **here** |
| **One shared term, square coordinate restrictions, 8 charts: closed unconditionally in 277/512 cases** | **CHECKED (§4.7)** | **here** |

**Conditional kill shot.** Decoder optimisation is dead on every slice above. The full master `C(P120) ≥ 72` follows from Conjecture **K-P120** (§5), and on P112 the statement `C(P112) ≥ 64` is equivalent to K1 ∧ K2 below.
Nothing in this package proves K-P120; it reduces the master to it and shrinks the P112 residue to one finite-looking family (Conjecture K3).

## 1. Setting and imported results

Model of #2338 / #2724 / #2816: lines `t ∈ L ⊆ E8` (P112 = E8 minus the frame F0 unless stated), labels `ℓ_t = u_t ∈ F2⁹`, dense pairing `Bd[t,s] = Ω(u_t,u_s)`; on E8 lines `Bd[t,s] = 1` iff `t = s` or `t ⊥ s`
(equivalently `Bd = (1 + Gram) mod 2` with the Gram matrix of the norm-2 roots). A **masked realisation** is `N ∈ K^{L×L}` (char `K` = 0) with `N_tt ≠ 0` and `N_ts = 0` for `t ⊥ s`; a **decoder** is `P, Q ∈ K^{L×m}` with
`(PQᵀ)_ts = N_ts` on all mask positions (`Bd = 1`), cost `Σ_k ρ(R_k, A_k)`, `ρ(R,A) := rank_F2 Bd[R,A] = w(R) − dim(U_R ∩ Z_A)`, `R_k = supp p_k`, `A_k = supp q_k`, `w(R) = dim U_R`, `U_R = span ℓ(R)`, `Z_A = U_A^⊥`.
`N₀ := G/2` (diagonal 1). `𝒞 = col N₀` = root code (dimension 8), `c_t` = frame coordinates of line `t`, `Off(h) = supp(C h)`, `z_i` = the label class of the frame root `f_i`, `W_i = z_i^⊥`.

* **FROM #2338 (merged), Theorem R:** every fitting table of F2-rank ≤ 9 is the dense table. **Theorem P:** inside decoders cost ≥ 64 (P112).
* **FROM #1212 (merged):** rank-8 realisations are `D₁ G D₂` (char 0).
* **FROM #2816:** Lemma 3.1 (`ℓ(Off(y))` spans F2⁹ unless `y ∝ f_i`, then `W_i`); R1–R4 of that note (one-sided floors, lift level `cost_w(S) ≥ 64 + min(|I|,2)` for `S ⊇ 𝒞_{X_I}`, Theorem U′); the cover facts (C1), (C3) (`cover.py`, `d7.py`); the completeness proof of the 1200-direction list with `|Off| ≤ 76`; `g(5) = 12`.
* philippeVV (#1587 follow-ups 6, 8): gain law; lift cases; R1–R4.

## 2. Universality and structure (PROVEN; any E8 line set L with the dense table)

### 2.1 Universality
**Theorem U0.** Let `N` be any masked realisation on `L`. Rescale `N ↦ D N` with `D = diag(1/N_tt)` (rows of `P` rescale, supports and cost unchanged), so `N_tt = 1`. Then every decoder of `N` becomes a decoder of `N₀` of the same cost.
*Proof.* `D′ := N₀ − N` vanishes on the diagonal and on orthogonal pairs, so it is supported on non-orthogonal pairs `t ≠ s`, where `Bd[t,s] = 0`. For each such pair add the term `(D′_ts e_t) e_sᵀ`; its cost is `ρ({t},{s}) = Bd[t,s] = 0`.
The new decoder matches `N₀` on every mask position. ∎
**Consequences.** (a) `C(L) = min cost over decoders of N₀(L)`. A decoder of a rank-ρ realisation is a decoder of `N₀` with extra cost-0 terms `e_t e_sᵀ`, which lie outside `𝒞` on both sides; so rank-9 realisations (#2819), "rank ≥ 10" and every other realisation class embed in the two-sided class of `N₀`.
(b) The split (a) inside / (b) one-sided / (c) two-sided **of N₀** is exhaustive; closing two-sided `N₀` for all `m` IS the master on that line set. (c) No argument blind to cost-0 terms can reduce "two-sided" to the closed cases; every reduction below keeps them in the bookkeeping.
(d) The theorem is a full-class statement, so it is compatible with the gain-law padding.

### 2.2 Outside factors are free
`N₀ = CCᵀ` (absorb the 1/2). Write `P = [C E]X̂`, `Q = [C F]Ŷ`, `X̂ = [X; X₂]`, `Ŷ = [Y; Y₂]` with `E ∈ K^{L×s}`, `F ∈ K^{L×t}` of full column rank and independent of `𝒞`. Then `PQᵀ = CCᵀ ⇔ X̂Ŷᵀ = diag(I₈, 0)`, and conversely for **any** `E′, F′`:
`[C E′] X̂Ŷᵀ [C F′]ᵀ = CCᵀ`. So a decoder is term-space data `(X̂, Ŷ)` plus free `E, F`; `p_k = C x_k + E x2_k`, `q_k = C y_k + F y2_k`. `J_P := {k : x2_k ≠ 0}`, `J_Q := {k : y2_k ≠ 0}`.
Sylvester on `X̂Ŷᵀ = diag(I₈,0)`: `s + t ≤ m − 8`, so two-sided needs `m ≥ 10` and `m = 10` forces `(s,t) = (1,1)`. From `P Y₂ᵀ = 0`: **Σ_{k∈J_Q} p_k(t) y2_k = 0 for every line t** (per-row cancellation). ∎
(Here exactness is used on all positions; the masked version reduces to it by §2.1 applied to `N = PQᵀ`, which is itself a realisation.)

### 2.3 Lemma-D normal form
Two terms with proportional `p` (or proportional `q`) merge into one: supports go to the union, cost does not rise, `N` is unchanged (Lemma D of #2338).
**Lemma 2.3.** In a merged decoder `|J_Q| ≥ t + 2` and `|J_P| ≥ s + 2`.
*Proof.* Each row restriction `p(t)|_{J_Q}` lies in `ker Y₂[:,J_Q]`, of dimension `|J_Q| − t`. If `|J_Q| = t + 1`, `P_{J_Q} = p cᵀ`, so all `p_k`, `k ∈ J_Q`, are proportional: excluded. `|J_Q| ≤ t` is impossible for nonzero terms. ∎
Merging the whole block gives the column `Q_{J_Q}c` with `Y₂[:,J_Q]c = 0`, an inside column; a non-normalised minimal circuit is never genuinely two-sided.

## 3. Two-sided decoders of N₀ on P112

### 3.1 Projection transfer identity (PROVEN, uses #2816 Lemma 3.1)
For `H ∈ K^{8×t}` put `Q_H := C(Y + H Y₂)` (i.e. `F′ = CH` in §2.2). Then `(P, Q_H)` is a decoder of `N₀` with `Q_H ⊆ 𝒞`: a one-sided decoder with the same row supports `R_k`. For `k ∉ J_Q` the column is unchanged; for `k ∈ J_Q`,
`y_k + H y2_k` is, for generic `H`, nonzero and not proportional to any `f_i` (`H ↦ H y2_k` is onto `K⁸`), so `ℓ(Off(y_k + H y2_k))` spans F2⁹ and its correction is 0. Hence
**cost(P,Q) = cost(P,Q_H) − Σ_{k∈J_Q} ε^col_k** (`ε^col_k := dim(U_{R_k} ∩ Z_{A_k})`, the column correction), and dually **cost(P,Q) = cost(P_{H′},Q) − Σ_{k∈J_P} ε^row_k.** ∎
So a two-sided decoder below 64 needs outside-term corrections, and by #2816 (`≥ 64` when `n_nf ≤ 2`) these are the only new ingredient.

### 3.2 Pivot bound (PROVEN, CONDITIONAL on #2816 R4)
**Lemma 3.2.** If `Π ⊆ J_Q` and `Y₂[:,Π]` is invertible then `col P_{−Π} = col P`. *Proof.* `P_Π Y₂[:,Π]ᵀ = −P_{−Π} Y₂[:,−Π]ᵀ`. ∎ (For `t = 1` every single `k₀ ∈ J_Q` is a pivot.)
**Phantom rows survive.** Inside corrected terms `k ∉ J_Q` (`q_k ∝ C f_i`, `z_i ∈ U_{R_k}`; one per `i` after merging) take a phantom row `f_i` with `p(f_i) = e_k`; since `y2_k = 0` the extended `P_ext` still satisfies `P_ext Y₂ᵀ = 0`, and `col P_ext ⊇ 𝒞_{X_I}` (the lift code of #2816 §7, `I` = inside corrected terms). Lemma 3.2 applies to `P_ext`.
**Theorem 3.3.** For every pivot set `Π ⊆ J_Q`: `cost = Σ_{k∉Π}(w(R_k) − ε^col_k) + Σ_{k∈Π} cost_k ≥ cost_w(col P_ext) − |I| − Σ_{k∈J_Q∖Π} ε^col_k + Σ_{k∈Π} cost_k`, and by #2816 R4
**cost ≥ 64 − (|I| − 2)₊ + Σ_{k∈Π} cost_k − Σ_{k∈J_Q∖Π} ε^col_k.** Dually for `J_P`. ∎
Pivot terms' own corrections are free of charge; only non-pivot outside corrections can push below 64. (Also `col P ⊋ 𝒞` in the two-sided case, so `cost_w(col P) ≥ 65` by #2816 Theorem U′.)

### 3.3 Small circuits close (PROVEN from #2724, #2338)
**Corollary 3.4.** A two-sided decoder of `N₀` with `m = 10` and `|J_Q| = 2` or `|J_P| = 2` costs ≥ 64: by Lemma 2.3 (`t = 1`) the two terms are proportional on one side; merging gives a decoder of `N₀` with ≤ 9 terms, one-sided (`m = 9`, #2724) or inside (#2338). ∎
More generally any `m = 10` decoder with two proportional columns on either side merges to `m ≤ 9` and is closed by the same citations.

### 3.4 Catalogue of outside-column corrections (CHECKED `cat1.py`, `cat2.py`; completeness of the direction list FROM #2816)
A correction of term `k` at class `z ∈ U_{R_k} ∩ Z_{A_k}` means `q_k` vanishes on `O_z := {s : Ω(u_s, z) = 1}` (`|O_z| ≥ 48`, CHECKED). Write `q_k = Ch + μ′` (`μ′` the outside part). On `O_z ∖ supp μ′` the codeword `Ch` vanishes, so
**|Off(h) ∩ O_z| ≤ |supp μ′ ∩ O_z|.** `cat1.py` computes `min_z |O_z ∩ Off(h)|` over all 511 classes and all 1200 directions with `|Off(h)| ≤ 76` (roots and norm-4 vectors; it regenerates 1200 directions with `|Off|`-distribution 56:8, 53:112, 76:56, 73:896, 70:128, matching #2816's list, whose completeness is proved there). Directions with `|Off| ≥ 77` meet every `O_z` in ≥ 77 − 64 = 13 lines.

| h | \|Off(h)\| | min_z \|O_z ∩ Off(h)\| | attained at | next two |
|---|---|---|---|---|
| frame root `f_i` (8) | 56 | 0 | `z = z_i` | 24, 24 |
| root `r_v`, `v ∈ P112` (112) | 53 | 1 | `z = u_v`, intersection `{v}` | 20, 20 |
| norm 4, \|Off\| 76 (56) | 76 | 12 | one non-line class | 32, 32 |
| norm 4, \|Off\| 73 (896) / 70 (128) | 73 / 70 | 13 / 14 | | |

**Theorem 3.5.** If `|supp μ′ ∩ O_z| ≤ 11`, the corrected column is (i) pure outside (`h = 0`), (ii) frame type (`h ∝ f_i`, `z = z_i`), or (iii) a column root swap (`h ∝ r_v`, `z = u_v`, `v ∈ supp μ′`). ∎ (Immediate from the table.)
**Corollary 3.6 (t = 1).** With `q_k = y2_k(μ + Cη_k)` for `k ∈ J_Q` and `z` not a frame class: if `z ∈ Z_{A_k} ∩ Z_{A_{k′}}` then `C(η_k − η_{k′})` vanishes on `O_z`, impossible unless `η_k = η_{k′}` (table: 0 only at `(f_i, z_i)`).
So after merging each non-frame class is killed by at most one outside column, and `Z_{A_k} ∩ Z_{A_{k′}} ⊆ {0} ∪ {z_i}`.

### 3.5 Outside columns in one coset (t = 1)
Setting `t = 1`: `q_k = y2_k v_k`, `v_k := μ + Cη_k` (`k ∈ J_Q`), all in the coset `μ + 𝒞`, the `η_k` distinct (merging). `w_k := w(A_k)`, `d_k := 9 − w_k = dim Z_{A_k}`. Label-flat sizes `g(8,7,6) = 64, 36, 20` (CHECKED `gtab.py`).
**Lemma 3.7 (pair lemma, PROVEN).** For `a ≠ b` in `J_Q`, `v_a − v_b = C(η_a − η_b)`, so `Off(η_a − η_b) ⊆ A_a ∪ A_b`. Hence `|A_a| + |A_b| ≥ 53` and `Z_{A_a} ∩ Z_{A_b} ⊆ ⟨z_i⟩` (#2816 Lemma 3.1). ∎
**Lemma 3.8 (low-column collinearity; PROVEN, CONDITIONAL on #2816 (C1), (C3)).** Call a column *low* if `w_k ≤ 7`.
(a) For two low columns `a, b`, `Off(η_a − η_b)` is covered by two label flats of dimension ≤ 7; by #2816 (C1) the only pair-coverable targets are the frame targets `Off(f_c)`, with cheapest cover 7 + 7. So `η_a − η_b ∝ f_c` and `w_a = w_b = 7`.
`pair2.py` (CHECKED) confirms independently, over all 1200 directions with `|Off| ≤ 76` and all 2-dimensional classes `Z_a, Z_b`, that `O(Z_a) ∩ O(Z_b) ∩ Off(h) = ∅` (both columns vanish there, so `C h` does) happens only for frame roots (`|Off| = 56`); for `|Off(h)| ≥ 77` it is impossible since `|O(Z_a) ∩ O(Z_b)| ≥ 2(112 − g(7)) − 112 = 40 > 112 − 77`.
(b) Three low columns span ≤ 2 dimensions (else the monochromatic-triangle argument of #2816 (C3) applies verbatim), so all low columns are `v₀ + α_k C f_c` for one `c`. ∎
Consequences: at most one outside column has weight ≤ 6, and then it is the only low column; otherwise all low columns have weight 7, lie on one frame line, and pairwise cover `Off(f_c)`.
**Lemma 3.9 (at most two weight-7 columns, PROVEN).** If low columns `v_k = v₀ + α_k C f_c` (distinct `α_k`) have weight 7, their agreement sets `G_k := L ∖ A_k` have `|G_k| ≥ 112 − g(7) = 76`. A line `t ∈ Off(f_c)` lies in `G_k` only for `α_k = −v₀(t)/⟨c_t, f_c⟩`, so the sets `G_k ∩ Off(f_c)` are pairwise disjoint, each of size ≥ 76 − 56 = 20. Hence `20r ≤ 56`: **r ≤ 2.** ∎
**Saving count (PROVEN), disjoint `(1,1)`, `m = 10`, merged, `J_P ∩ J_Q = ∅`.** Write `cost_k = 9 − s_k`. Inside-both terms: `s_k ≤ 1` (`s_k = 1` iff `x_k` or `y_k` is ∝ a frame vector, as `β(z_i,z_j) = 1`). `k ∈ J_Q` (rows inside, `R_k = Off(x_k)`): `s_k = d_k` if `x_k` is generic, `s_k = 1 + dim(W_j ∩ Z_{A_k}) ≤ d_k + 1` if `x_k ∝ f_j`;
frame-type corrected columns have `s_k = 1`; `d_k = 0 ⇒ s_k ≤ 1`. Same for `J_P` with rows and columns exchanged. Then **cost ≤ 63 ⇔ Σ s_k ≥ 27 ⇔ E_Q + E_P ≥ 17**, `E_Q := Σ_{k∈J_Q}(s_k − 1)`.
Pattern bounds: one column with `d_a ≥ 4` gives `E_Q ≤ 9` (+1 at `d_a = 4`); otherwise `E_Q ≤ 4 + #(ii)` by Lemmas 3.8–3.9, where (ii) are `d = 1` columns of a non-frame class `z` with frame rows `x ∝ f_j`, `Ω(z, z_j) = 0` (distinct `j`, so ≤ min(8, |J_Q| − 1)). The best current total is 18 ≥ 17: a finite gap (Conjecture K3).

### 3.6 The smallest unresolved configuration (OPEN, exact)
`m = 10`, `(s,t) = (1,1)`, merged, `|J_P| ≥ 3`, `|J_Q| ≥ 3`; rows `p(t) = c_t X + λ_t x2`, columns `q(s) = c_s Y + μ_s y2` (`λ, μ ∈ K^L` arbitrary), `x2·y2 = 0`. A decoder of cost ≤ 63 must satisfy (`|I| ≤ 2`):
(N1) for every `k₀ ∈ J_Q`: `Σ_{k∈J_Q∖k₀} ε^col_k ≥ cost_{k₀} + 1`, and dually (Theorem 3.3); (N2) terms outside `J_P ∪ J_Q` cost ≥ 8 each; (N3) every corrected outside column is of the §3.4 types, at most one per non-frame class.

## 4. Batching reduces to the single-call floor except rank-(2,2) multi-diagonal terms

Model of #2338's batch section: `k` calls on P112, one h = 9 joint table, charts `Φ_c ∈ O(9)`; a term `j = (p_j^c, q_j^c)_c` is charged once, `cost_j = ρ(S_j, T_j)` on its union label spans. `μ_j := #{c : p_j^c ≠ 0 ≠ q_j^c}`; MD (multi-diagonal) means `μ_j ≥ 2`.
`c(Y)` = minimal single-call masked cost of a target `Y`; **H** := every single-call decoder of every masked realisation costs ≥ 64 (= `C(P112) ≥ 64`, i.e. K1 ∧ K2 of §5).

### 4.1 Multiplicity inequality and converse (PROVEN)
**Lemma 4.1.** `D_c := {j : p_j^c ≠ 0 ≠ q_j^c}` is a single-call decoder of `M_c` with term costs `x_j^c ≤ cost_j` (a submatrix of `Bd[R_j, A_j]` up to the call's isometric chart).
**Theorem A.** `Σ_j μ_j cost_j ≥ Σ_c Σ_{j∈D_c} x_j^c ≥ Σ_c floor₁(M_c)`. Under H: `cost ≥ 64k − Σ_j (μ_j − 1)₊ cost_j`; **a batch with no MD term costs ≥ 64k.** With `m = 8k + e` terms, H is needed only for single calls with ≤ `8 + e` terms. ∎
**Converse.** The batch floor `64k` implies H: put a single-call decoder of cost κ in call 1 and coordinate decoders (cost 64) in calls 2..k. Batching is never easier than the single call. ∎
**Theorem C (rank budget).** `P^c Q^{c′ᵀ} = 0` for `c ≠ c′` gives `r(P^c) ≤ m − 8(k−1)` (CHECKED arithmetic `c_batch_arith.py`). At `m = 17`, `k = 2`, if all four factor ranks are 8 every factor lies in `col/row M_c` and #2338 Theorem B closes the batch; the rank-9 cases are OPEN.

### 4.2 Twin fold (Theorem TF, PROVEN; CHECKED on the anchor batches `fold.py`)
A chart `Φ` is *twin* if `Φ(L) = L`; then `σ` (call-1 line `s` ↦ the call-0 line with label `Φu_s`) is a bijection with `B₀₁(r,s) = B₀₀(r,σs)`; twin charts are exactly the `Aut(P112)` images in `O(9)` (labels are linear in B-rows), and relabelling makes the chart common.
**Theorem TF.** For twin (or common) charts and all `λ, μ ∈ K^×`:
**cost ≥ c(M₀) + c(M₁) + Σ_{j∈MD} (cost_j − φ⁰_j(λ) − φ¹_j(μ)) − Σ_{j row-dangling} ε_j**, with `φ⁰_j(λ) = ρ(S_j⁰, T(q_j⁰ + λσq_j¹))`, `φ¹_j(μ) = ρ(S_j¹, T(q_j¹ + μσ⁻¹q_j⁰))`, and `ε_j = ρ(S^c,T) + ρ(S_d,T) − ρ(S^c+S_d,T)` for a diagonal term with row dangling `S_d`.
*Proof.* `Fold₀(λ) := {(p_j⁰, q_j⁰ + λσq_j¹)}` decodes `M₀`: entry `(r,t)` is `M₀(r,t) + λX₀₁(r, σ⁻¹t)`, and `B₀₀(r,t) = 1 ⇒ B₀₁(r,σ⁻¹t) = 1`, where the cross block `X₀₁` vanishes. Its term costs are ≤ batch costs (`supp(q⁰ + λσq¹) ⊆ supp q⁰ ∪ σ supp q¹`, `σ` preserves labels, `ρ` monotone). Likewise `Fold₁(μ)` decodes `M₁`.
Per class: call-c diagonal terms (with column dangling) appear in one fold at ≤ cost; pure-cross cancellers appear once in each fold, ≤ cost total; diagonal terms with row dangling appear in both, total ≤ cost + ε_j; MD terms appear in both with charges `φ⁰ + φ¹`. Summing gives TF. Row folds give the mirror statement. ∎
**Consequence.** An MD term with twin-proportional input halves (`q¹ = κσ⁻¹q⁰`) vanishes from both folds (`λ = −1/κ`, `μ = −κ`) and counts `+cost_j`. **Under H, a twin-chart batch whose MD terms all have proportional input halves (or all proportional output halves) and no dangling of the charged orientation costs ≥ 128 + Σ_MD cost_j.** Duplicated shared terms never help.
**k calls.** `Fold_c = {(p_j^c, Σ_{c′} λ_{cc′} σq_j^{c′})}` (`λ_cc = 1`) decodes `M_c`; if every MD input matrix has row space in a subspace `𝒦 ⊆ K^k` containing no `e_c`, choose `λ_c ∈ 𝒦^⊥`: cost ≥ `Σ_c c(M_c) + Σ_MD cost_j −` (row-dangling overlaps), ≥ `64k + 8·#MD` under H. ∎
**Partial twins.** For a general chart, the same holds with `σ` applied to `q¹` restricted to `Λ = {s : Φu_s ∈ L}` (dropping the other columns is a restriction).
`fold.py` (Φ = I; coordinate decoders in both calls, coordinate `i` of call 0 merged with `j` of call 1, two cancellers): both folds decode `M` on the mask and every folded term costs ≤ its batch cost; `(0,0)`, λ = −1: folds 64 + 64 (shared term vanishes), batch 136; `(0,1)`, `(0,5)`: folds 72 + 72, shared term charged 8 + 8 against batch cost 9.

### 4.3 Transport lemma (PROVEN + CHECKED `transport.py`)
A call-1 column `s` can be moved onto call-0 column `t` without breaking the mask iff `b(u_r, Φu_s) = 1` for all `r ∈ R_t = {t} ∪ t^⊥` (affine conditions in `y = Φu_s`). `span lab(R_t)` has dimension 8 for all 112 lines (CHECKED), so the solutions are exactly `{u_t, u_t + d_t}` (`d_t` the normal).
`y = u_t` is a twin; `y = u_t + d_t` replaces the label and is not cost-monotone. So TF with partial twins is the most general line-wise cost-monotone fold.

### 4.4 Fold barrier (PROVEN)
With a common chart, a cost-monotone fold is `(P_jα, Q_jλ)` for call-index functionals `α, λ ∈ K²` (`P_j = [p_j⁰ p_j¹]`); the folded target is `Σ_c α_cλ_c M_c`. A term with `rank P_j = rank Q_j = 2` has `(P_jα)(Q_jλ)ᵀ ≠ 0` for all nonzero `α, λ`, so both covering folds see it.
**Hence the overlap `dim((S⁰+T^⊥) ∩ (S¹+T^⊥)) − dim T^⊥` of a rank-(2,2) MD term (7 for the (0,1) and (0,5) anchor terms) cannot be removed by any fold / restriction / mixing argument.** Closing it needs an *excess* statement for single-call decoders containing a cancelled residual (Conjecture K5).

### 4.5 Relative rank, free dangling, covering ceiling (PROVEN)
**Lemma RR.** For a bilinear pairing and `S₀ ⊆ S`, `T₀ ⊆ T`: `ρ(S,T) ≥ ρ(S₀,T₀) + ρ(S ∩ T₀^⊥, T ∩ S₀^⊥)`. *Proof.* Pick dual bases `s_a ∈ S₀`, `t_b ∈ T₀` of the rank-`r` part; `S = ⟨s⟩ ⊕ (S ∩ ⟨t⟩^⊥)`, `T = ⟨t⟩ ⊕ (T ∩ ⟨s⟩^⊥)`, the pairing is `I_r ⊕ β′`, and `S ∩ T₀^⊥ ⊆ S ∩ ⟨t⟩^⊥`, `T ∩ S₀^⊥ ⊆ T ∩ ⟨s⟩^⊥`. ∎
**Free dangling.** If `ρ(S^c, T^c) = dim S^c` then any input dangling is free (`ρ(S^c,T′) ≤ dim S^c`); every square-restriction term has this property (#2338 (P2)).
**Covering lemma and ceiling.** For an induced matching `Π` of `B_cc′` each term pays `≥ #`(covered positions), so cancellers pay ≥ the number of `Π`-positions with nonzero residual; but `|Π| ≤ rank_F2 B_cc′ ≤ 9`. Certificates from induced families of all-ones bicliques certify ≤ 9 per cross block, so an `s`-scalable cancellation floor must be value-level.

### 4.6 Lemma K′, Lemma E, Theorems D and M (PROVEN; arithmetic CHECKED)
**Lemma K′ (GL(9) charts).** If `S` is a set of rank-7 terms whose K-digraph is acyclic, `rank(I_t − K) ≥ |S|`, `d := corank(I_{8k} − ACᵀ) ≤ t − α`, and `cost ≥ 7t + 8(8k − d) ≥ 64k − t + 8α` (`α` = largest acyclic set); closed whenever `α ≥ t/8`.
The 9-term digon clique (`x_j = e_j`, `y_i = 𝟙 − e_i`) has `α = 1`, `corank(I − K) = 8` and counting floor `64k − 1` (CHECKED `c_batch_arith.py`, `c_clique_lemmaE.py`). **Lemma E.** If the non-rank-7 terms number exactly `rank(I − N)`, their factors span `col E` / `row E`; for the clique `rank E = 64` and `col E ∩ span(O_j) = 0`, `row E ∩ span(I_i) = 0` for all 9 classes (CHECKED exactly, `c_clique_lemmaE.py`),
so the cost-9 terms alone carry `E` (cost ≥ `64k + 63`); otherwise ≥ `8k − 7` non-rank-7 terms and cost ≥ `64k + 7`. **The clique obeys the floor.** (Lemma E is script-checked only; the GL(9, F2) charts realising the 72 arcs are RECORDED from the author's card, not shipped; the floor does not depend on them.) GL charts with `k ≥ 3` in general: OPEN, non-physical (the physical table is symmetric, #2338 Theorem Bk).
**Theorem D (common chart).** `min cost(C ⊗ M) = min cost(I_{rank C} ⊗ M)` within any factor class closed under call-mixing and restriction: mix with invertible `G, H` (label spans only shrink), take `GCHᵀ = I_r ⊕ 0`, drop calls `r+1..k`. Recovers #1714's `64·rank C`. Distinct charts with `C ≠ I`: OPEN.
**Theorem M (Gram root codes, factors in col M).** One P112 call plus `k₂` P104 calls (#968's unit): cost ≥ `64 + 56k₂`. *Proof.* No cost-7 term has both factors nonzero in the P112 call (that would be a P112 out/in hyperplane pair, rank 8: `p104prem.py`, pair ranks `{8: 64}`), so `N_PP = 0`, `rank(I − N) = 8 + rank(S) ≥ 8 + 8k₂ − t`; all other terms cost ≥ 8: `cost ≥ 7t + 8(8 + max(0, 8k₂ − t)) ≥ 64 + 56k₂` (minimisation CHECKED). ∎
For `k₁ ≥ 2` P112 calls (O(9) charts) `rank(I − N) ≥ max(8k − t, 8k₁ − t/2)` gives `cost ≥ 64k₁ + 48k₂` (CHECKED minimisation); `64k₁ + 56k₂` is OPEN. Premises CHECKED (`p104prem.py`): P112 has 8 avoidable hyperplane classes and within-call pair ranks `{8: 64}`; P104 (#968's unit and three further frame representatives) 16 avoidable classes, pair ranks `{8: 192, 7: 64}`.
Sharpness of Theorem M assumes each P104 call's coordinate decoder costs 56 (not re-checked here).

### 4.7 One shared term: dangling-proof witness bound (PROVEN; closure CHECKED `twinblk.py`, `s1close.py`)
Setting: `k = 2`, square coordinate restrictions in both calls (Gram decoders `{(Xe_k, Xe_k)}`), call-0 coordinate `i` merged with call-1 coordinate `j`; all other nonzero-cost terms are restriction terms carrying dangling, or pure-cross cancellers. No H is used (#2338 Theorem P).
**Ledger.** `batch ≥ 128 − saving + κ₀₁ + κ₁₀`, `saving = 16 − cost(shared)`, `κ` = canceller cost per cross block.
**Witnesses.** `Ω` on block (0,1) with (a) `supp Ω ⊆ {B₀₁ = 1}`, (b) `Ωᵀ Xe_k = 0` for non-shared call-0 coordinates and `Ω Xe_l = 0` for non-shared call-1 coordinates (kills all dangling), (c) `⟨Ω, Xe_i(Xe_j)ᵀ⟩ ≠ 0`. On the mask, block (0,1) is residual + dangling + cancellers = 0, so some canceller meets `supp Ω` on both sides.
For an induced family of `n` witnesses on all-ones bicliques a canceller's block restricted to them is block-diagonal all-ones, so `κ₀₁ ≥ n`. **Twin witnesses:** each line `r` of `N(f_i)` has exactly one `i`-twin `r′` (`x_r = c·x_{r′}` off coordinate `i`, `x_{r,i} = −c·x_{r′,i}`; 28 pairs, CHECKED); `Ω = (e_r − c e_{r′})(e_s − c′e_{s′})ᵀ` satisfies (b), and (c) holds since `⟨Ω, Z⟩ = 2x_{r,i}·2x_{s,j} ≠ 0`; it is a witness iff the 2×2 block is all-ones in `B₀₁`.
**CHECKED (`s1close.py`, 8 charts: Φ = I and 7 seeded random O(9) charts; greedy lower bounds on `n`, exact F2 ranks):** closed (`n₀₁ + n₁₀ ≥ saving`) in **277 of 512** `(i, j, chart)` cases, including all 56 cases `i ≠ j` at Φ = I.
The 235 open cases have no twin block (saving 7: 224; saving 8: 11, of which the 8 cases `i = j` at Φ = I are aligned and covered by TF under H). Greedy bounds are lower bounds; a larger true `n` only helps. Ceiling: `n ≤ 9` per block, so this method cannot close `s ≥ 3` shared terms.

## 5. Named conjectures (the remaining gaps)

* **K-P120 (master).** Every decoder of `N₀(P120)` (dense table) costs ≥ 72. By §2.1 this **is** `C(P120) ≥ 72`, hence (gain law) `gain ≤ 48` on every E8 line set, and P112 ≥ 64, P111 ≥ 63, P104 ≥ 56.
* **K1 (two-sided floor, P112).** Every two-sided decoder of `N₀(P112)` costs ≥ 64. By §3.1 equivalent to: *outside corrections never exceed the excess of the one-sided projection*. Together with K2 and #2338, K1 ⇔ `C(P112) ≥ 64` (§2.1).
* **K2 (excess pays for corrections, one-sided).** `Δ ≥ n_nf` for `n_nf ≥ 3` (#2816 proves `n_nf ≤ 2`; the root-swap family is tight; #2826 leaves six weight multisets at `n_nf = 3`).
* **K3 (smallest two-sided case).** For disjoint `(1,1)`, `m = 10`, merged decoders, `E_Q + E_P ≤ 16` (§3.5: current bound 18); and the non-disjoint case `|J_P ∩ J_Q| ≥ 2`.
* **K4 (P120 versions).** The one-sided results of #2816 and §3 on P120 (E8 lifts are ≥ 67 so far, against 72); P112 certification of #2819. §2 already holds on P120.
* **K5 (batching, H×).** A single-call decoder containing a term `a(c + λd)ᵀ` with `d` outside the span of the other input halves on the mask costs ≥ 64 + 7. With TF this closes rank-(2,2) MD terms for twin charts; non-twin charts and both-orientation dangling remain.
* **K6 (label windows h ≥ 12).** A per-term floor at h ≥ 12; RECORDED break-even prices 51 / 46 / 42 at h = 12 / 13 / 14 (author's pricing model, not re-run here). The master as stated is at the dense h = 9 table.

Earlier map items "B-form rank-9 floors" and "extra zeros at rank 9" are **no longer needed for the master**: by §2.1 they are sub-slices of K1 / K-P120.
Working cards on K2 and K3 (PAYS, RESIDUE) have no proven results yet; nothing is claimed from them.

## 6. Relation to philippeVV's R1–R4 (#1587 follow-up 8)

philippeVV closes all lift cases of `C(P120) ≥ 72` and names: **R1** every rank-9 completion is a lift; **R2** rank-8 rigidity; **R3** dependent non-clique `S`; **R4** rank-8 `N` with 9 terms on P120, `m ≥ 10`, `h ≥ 10`.
* **R1, R2.** Universality (§2.1) makes these realisation-level questions unnecessary for the master: `C(P120)` is the minimum over decoders of the single matrix `N₀(P120)`, whatever the realisation's rank or zero pattern. It does **not** prove R1 or R2.
  (R2 on P112 / P120 is #1212; #2819 classifies rank-9 realisations of the iff pattern, which allow no extra zeros, so R1 does not follow from it.)
* **R4.** The `m ≥ 10` part is K-P120 (two-sided and one-sided parts); its P112 shadow is K1 ∧ K2, with the first open configuration in K3. The P112 nine-term case is #2724. `h ≥ 10`: #2639 (h = 10, 11), K6.
* **R3** is not addressed here.

## 7. Reproduce

`bash verify.sh [/fresh/output/dir]` (Python ≥ 3.10 with numpy; `PYTHON=` to choose). Steps: manifest; three parallel streams (all `timeout 1200`): `s1close.py` (~2 min), `twinblk.py` (~0.5 min), and the fast group
(`cat1`, `cat2`, `gtab`, `pair2`, `fold`, `transport`, `p104prem`, `c_batch_arith`, `c_clique_lemmaE`; ~5 min, `pair2` the slowest); then `check_logs.py` asserts every number quoted above.

| Claim | Script |
|---|---|
| catalogue table, `|O_z| ≥ 48`, 1200 directions | `cat1.py`, `cat2.py` |
| `g(8,7,6) = 64, 36, 20` | `gtab.py` |
| Lemma 3.8 independent check | `pair2.py` |
| TF on anchors; transport | `fold.py`, `transport.py` (common data `hb.py`, `e8.py`) |
| twin pairs (28 per coordinate); 277/512 | `twinblk.py`, `s1close.py` (uses `dangle.py` for the random charts) |
| Theorem M premises / minimisations; K′, E, C arithmetic | `p104prem.py`, `c_batch_arith.py`, `c_clique_lemmaE.py` |
