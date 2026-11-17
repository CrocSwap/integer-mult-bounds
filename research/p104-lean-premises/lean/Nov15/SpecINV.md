# Nov15/SpecINV.lean 
Formalises the AUDITED R43 lemmas (internal notes, AUDIT43.md) on top of Nov15/SpecTSUR.lean.
Kernel-only: no sorry, no native_decide; all 14 printed theorems use [propext, Classical.choice, Quot.sound]. 8 s, 2.1 GB.
Matrices over a field K (`pp`, `refl = 1 - x yᵀ`, `ev/jobsP/uconj/ucount`, `UR_upper/UR_lower` imported from SpecTSUR).

## Result: no paper statement is false as written. Two points where the Lean form is sharper / differs
- INV needs only the FIRST factor to be a transvection (`y_0·x_0 = 0` is the only use of `q.p = 0`); the proof avoids N^-1: with Z = columns z_i (Z N = P) and I - g = Z Qᵀ, rank U gives Qᵀ Z = 2I, entry (0,0): q_0·z_0 = q_0·p_0 = 0 = 2.
- SPLIT det term is proved as `det J · ε ≠ σ ε^N` (N = dim V₁, σ = -1 iff H active; equivalent to the paper's `det J_K ≠ ε^{dim K}` because det J = σ det J_K). The U = 4 equality step is formalised in coordinates ADAPTED to V₁ = ⟨x_H⟩ ⊕ K (Fin 1 ⊕ Fin 2); the basis-change to those coordinates is NOT proved (a conjugation; ranks and involutivity are invariant, but it is a stated hypothesis form).
- (audit item, not re-proved) "md = 4 ⇒ dead" holds only inside the N = 10 family (U ≤ 4); the Lean results say U ≥ 5 (resp. rank bound) and nothing about md.

## Contents
1. `inv_rank`: char ≠ 2, `g = pp x y U` with y_0·x_0 = 0 (paper: all y_i·x_i = 0), g² = 1 ⇒ rank(1 - g) ≤ U - 1. `pp_shift`, `prod_units_pp`, `conj_form`, `uconj_forms` turn a word's conjugated units (`uconj w 1`) into a `pp` product; `inv_word`; `inv_DJ`: D, J commuting involutions (`ev w`, `jobsP w`) and transvection units ⇒ rank(D - J) ≤ U - 1 (g = D J⁻¹ = (uconj w 1).prod, D - J = (g - 1) J).
2. `UR_inv_combined`: d + |k - r₁| ≤ U - 1 (UR_lower + INV). `six_arith`/`six_survivors`: the two bound-4 patterns — (d, k, r₁) = (1, 3, 0) for R26 #10-#14 and (2, 3, 1) for #8 — give 5 ≤ U; character data are hypotheses `hpat` (pattern), hD, hJ, hD2/hJ2/hc.
3. SPLIT: `hub_mulVec`, `hub_vecMul`, `hub_data` (J x_H = σ x_H, y_H J = σ y_H, det J = (-1)^k from the pairing hypotheses y_i·x_H = 0 = y_H·x_i for the other active jobs i, y·x = 2); `split_key` (rank(ε - J) ≤ 1, ε ≠ σ ⇒ ε - J = ((ε-σ)/2) x_H y_Hᵀ, no basis of K needed), `split_det` (matrix determinant lemma), `split_rank_ge` (rank(ε - J) ≥ [ε ≠ σ] + [det term]), `split_DJ_rank` (with dark flips: rank(D - J) ≥ d + [x_H term] + [det term]), `split_R26_2_3`: d = 2, dim V₁ = 3, patterns (k=3, H∉S, ε=-1) and (k=4, H∈S, ε=+1) (R26#2 hub E μ=1,6,11,12; #3 hub F μ=9,14,11,12 are the same arithmetic) ⇒ rank(D - J) ≥ 4, so U ≥ 4, U = 3 dead (with UR_upper).
4. U = 4 equality: `two_by_two_invol` (2×2, det -1, rank(ε - J) ≤ 1, ε = ±1 ⇒ J² = I, via det(ε - J) = 0 ⇒ tr = 0 ⇒ Cayley-Hamilton by entries), `split_U4`: in adapted coordinates, D = ε ⊕ diag sd, J = (σ ⊕ J_K) ⊕ I, ε ≠ σ, det J_K ≠ ε², det J_K = ±1: `ucount w ≠ d + 2` (slack ⇒ rank(ε - J_K) ≤ 1 ⇒ J_K² = I ⇒ J², D², [D,J] ⇒ INV ⇒ rank(D - J) ≤ d + 1 < d + 2). With d = 2 this is U ≠ 4 for R26#2, #3; combined with U ≠ 3 above: U ≥ 5.
5. Counterexamples: `inv_needs_transvection` (ℚ, y·x = 2: involution with rank(I - g) = 1 > 0), `inv_needs_char` (ZMod 2, e₀/e₁: same). Both hypotheses are necessary.

## Hypotheses taken from the cards (not proved here)
Tight-set pairing y_H·x_j = 0 = y_j·x_H (R43 item 3 via Lemma TS), the hub being active or not, character data (ε, σ, k, d, dim V₁), D = scalar ε on V₁ (r₁ ∈ {0, m}), D ⊕ J block forms, that all active jobs form the listed product, units being transvections.

## Addendum : the change of basis in `split_U4` is now proved
`Phi B` (algebra equivalence `Matrix n n K ≃ₐ Matrix ι ι K`, coordinates in a basis `B` of `n → K`), `mapW`/`ev_mapW`/`jobsP_mapW`/`ucount_mapW` (word transport along a monoid hom), `Phi_refl`/`dot_Phi` (transvection form and `y·x = 0` preserved).
- `split_U4_basis`: any basis `B` indexed by `(Fin 1 ⊕ Fin 2) ⊕ nd` with `D`-eigen data (`ε` on the first three vectors, `sd` on the rest) and `J`-data (`σ`, a 2x2 block `JK`, identity) gives `U ≠ d + 2` for matrices on an arbitrary `n`.
- `split_U4_free` (basis-free): `V = A ⊕ K₀ ⊕ W` via `DirectSum.IsInternal ![A, K₀, W]`, `dim A = 1` (`A = ⟨x_H⟩`), `dim K₀ = 2`, `D` = `ε` on `A, K₀` and ±1 eigenbasis `bW` on `W`, `J` = `σ` on `A`, preserves `K₀` (det of the restriction `≠ ε²`, = ±1), identity on `W`. The adapted basis is BUILT (`collectedBasis` + `idxEquiv`). Conclusion `ucount w ≠ #{sd = -1} + 2`. `nd : Type` (universe 0, for `![Fin 1, Fin 2, nd]`). Kernel-only, standard axioms.
