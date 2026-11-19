import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.NumberTheory.Padics.RingHoms
import Nov15.DecoderWall

/-!
# DecoderWall2 : equality half of the row-price law, dimension-sum bound, rank-8 reduction
-/
open Matrix

namespace DecoderWall

section Equality
variable {κ D S : Type*} [Fintype κ] [Fintype D] [Fintype S]

/-- `Φ_S v = (s ↦ q_s · v)`. -/
noncomputable def Phi (qS : S → κ → ZMod 2) : (κ → ZMod 2) →ₗ[ZMod 2] (S → ZMod 2) :=
  (Matrix.of fun (s : S) (i : κ) => qS s i).mulVecLin

theorem Phi_apply (qS : S → κ → ZMod 2) (v : κ → ZMod 2) (s : S) : Phi qS v s = dot v (qS s) := by
  simp only [Phi, Matrix.mulVecLin_apply, Matrix.mulVec, dot, dotProduct, Matrix.of_apply]
  exact Finset.sum_congr rfl fun i _ => mul_comm _ _

/-- `A^⊥` for the span `A` of the gathered labels. -/
noncomputable def annS (qS : S → κ → ZMod 2) : Submodule (ZMod 2) (κ → ZMod 2) :=
  LinearMap.ker (Phi qS)

/-- **Row-price law, equality half (DECMINRANK Lemma 1).**  With `B = span qD`, `A = span qS`:
`rank [qD_t·qS_s] = dim B − dim (B ∩ A^⊥)` (stated additively). -/
theorem pairing_rank_eq (qD : D → κ → ZMod 2) (qS : S → κ → ZMod 2) :
    (Matrix.of fun (t : D) (s : S) => dot (qD t) (qS s)).rank
      + Module.finrank (ZMod 2) (↥(Submodule.span (ZMod 2) (Set.range qD) ⊓ annS qS))
      = Module.finrank (ZMod 2) (Submodule.span (ZMod 2) (Set.range qD)) := by
  classical
  set B := Submodule.span (ZMod 2) (Set.range qD) with hB
  set G : Matrix D S (ZMod 2) := Matrix.of fun t s => dot (qD t) (qS s) with hG
  let Ψ := Phi qS ∘ₗ B.subtype
  have hrange : LinearMap.range Gᵀ.mulVecLin = LinearMap.range Ψ := by
    apply le_antisymm
    · rintro _ ⟨c, rfl⟩
      have hv : (∑ t, c t • qD t) ∈ B :=
        Submodule.sum_mem _ fun t _ => Submodule.smul_mem _ _ (Submodule.subset_span ⟨t, rfl⟩)
      refine ⟨⟨_, hv⟩, ?_⟩
      ext s
      simp only [Ψ, LinearMap.comp_apply, Submodule.subtype_apply, Phi_apply, Matrix.mulVecLin_apply,
        Matrix.mulVec, dotProduct, Matrix.transpose_apply, hG, Matrix.of_apply, dot,
        Finset.sum_apply, Pi.smul_apply, smul_eq_mul, Finset.sum_mul]
      rw [Finset.sum_comm]
      refine Finset.sum_congr rfl fun t _ => ?_
      refine Finset.sum_congr rfl fun i _ => ?_
      ring
    · rintro _ ⟨⟨v, hv⟩, rfl⟩
      obtain ⟨c, rfl⟩ := (Submodule.mem_span_range_iff_exists_fun (ZMod 2)).1 hv
      refine ⟨c, ?_⟩
      ext s
      simp only [Ψ, LinearMap.comp_apply, Submodule.subtype_apply, Phi_apply, Matrix.mulVecLin_apply,
        Matrix.mulVec, dotProduct, Matrix.transpose_apply, hG, Matrix.of_apply, dot,
        Finset.sum_apply, Pi.smul_apply, smul_eq_mul, Finset.sum_mul]
      rw [Finset.sum_comm]
      refine Finset.sum_congr rfl fun t _ => ?_
      refine Finset.sum_congr rfl fun i _ => ?_
      ring
  have hker : LinearMap.ker Ψ = (B ⊓ annS qS).comap B.subtype := by
    ext x
    simp [Ψ, annS, LinearMap.mem_ker]
  have h1 := LinearMap.finrank_range_add_finrank_ker Ψ
  have h2 : Module.finrank (ZMod 2) ((B ⊓ annS qS).comap B.subtype)
      = Module.finrank (ZMod 2) (↥(B ⊓ annS qS)) :=
    LinearEquiv.finrank_eq (Submodule.comapSubtypeEquivOfLe inf_le_left)
  have h4 : G.rank = Gᵀ.rank := (Matrix.rank_transpose G).symm
  have h5 : Gᵀ.rank = Module.finrank (ZMod 2) (LinearMap.range Ψ) := by
    rw [← hrange]; rfl
  rw [hker, h2] at h1
  omega

/-- `dim A^⊥ + dim A = h` (nondegeneracy of the dot product on `𝔽₂^h`). -/
theorem finrank_annS_add (qS : S → κ → ZMod 2) :
    Module.finrank (ZMod 2) (annS qS)
      + Module.finrank (ZMod 2) (Submodule.span (ZMod 2) (Set.range qS)) = Fintype.card κ := by
  classical
  let N : Matrix S κ (ZMod 2) := Matrix.of fun s i => qS s i
  have h1 := LinearMap.finrank_range_add_finrank_ker N.mulVecLin
  have h2 : N.rank = Module.finrank (ZMod 2) (Submodule.span (ZMod 2) (Set.range qS)) := by
    rw [Matrix.rank_eq_finrank_span_row]; rfl
  have h3 : Module.finrank (ZMod 2) (LinearMap.range N.mulVecLin) = N.rank := rfl
  have h4 : Module.finrank (ZMod 2) (κ → ZMod 2) = Fintype.card κ := by simp
  have h5 : annS qS = LinearMap.ker N.mulVecLin := rfl
  rw [h5]; omega

/-- **Dimension-sum bound (PR968 eq. 2).**  `rank ≥ dim B + dim A − h`. -/
theorem pairing_rank_ge (qD : D → κ → ZMod 2) (qS : S → κ → ZMod 2) :
    Module.finrank (ZMod 2) (Submodule.span (ZMod 2) (Set.range qD))
      + Module.finrank (ZMod 2) (Submodule.span (ZMod 2) (Set.range qS)) ≤
    (Matrix.of fun (t : D) (s : S) => dot (qD t) (qS s)).rank + Fintype.card κ := by
  have h1 := pairing_rank_eq qD qS
  have h2 := finrank_annS_add qS
  have h3 : Module.finrank (ZMod 2) (↥(Submodule.span (ZMod 2) (Set.range qD) ⊓ annS qS))
      ≤ Module.finrank (ZMod 2) (annS qS) := Submodule.finrank_mono inf_le_right
  omega

end Equality


section Rank8
variable {κ ι T : Type*} [Fintype κ] [Fintype ι] [DecidableEq ι] [Fintype T]

/-- NAMED FINITE HYPOTHESIS `Rank8Spans` (computed, never an axiom): every row of the decoder has
deposit-label span and gather-label span of dimension ≥ 8.  Data: `DECMINRANK/r8flats.out` (only the 16
kernel hyperplanes give a span below 9; no codim-2 subspace does; 43,435 checked) plus the rank-8
rigidity `D1·G·D2` [Q DYADICPORTS rigid.py]. -/
def Rank8Spans {R : Type*} [Zero R] (q : ι → κ → ZMod 2) (W U : ι → T → R) : Prop :=
  ∀ k, 8 ≤ Module.finrank (ZMod 2) (Submodule.span (ZMod 2) (Set.range fun t : dep W k => q t)) ∧
       8 ≤ Module.finrank (ZMod 2) (Submodule.span (ZMod 2) (Set.range fun s : gat U k => q s))

theorem rowPrice_ge {R : Type*} [Zero R] (q : ι → κ → ZMod 2) (W U : ι → T → R) (k : T) :
    Module.finrank (ZMod 2) (Submodule.span (ZMod 2) (Set.range fun t : dep W k => q t))
      + Module.finrank (ZMod 2) (Submodule.span (ZMod 2) (Set.range fun s : gat U k => q s))
      ≤ rowPrice q W U k + Fintype.card κ :=
  pairing_rank_ge (fun t : dep W k => q t) (fun s : gat U k => q s)

/-- `h = 9`: a row with both spans of dimension ≥ 8 costs ≥ 7 (the hyperplane row of E8). -/
theorem rowPrice_ge_seven {R : Type*} [Zero R] (q : ι → κ → ZMod 2) (W U : ι → T → R)
    (h9 : Fintype.card κ = 9) (hs : Rank8Spans q W U) (k : T) : 7 ≤ rowPrice q W U k := by
  have := rowPrice_ge q W U k
  have := hs k
  omega

/-- A pairwise-odd family of 8 ports needs ≥ 8 rows (an `I₈` block of `W Uᵀ`). -/
theorem rows_ge_eight {K : Type*} [Field K] (q : ι → κ → ZMod 2) (W U : ι → T → K)
    (hd : IsDecoder q W U) (c : Fin 8 → ι) (hc : Function.Injective c)
    (hodd : ∀ i j, i ≠ j → dot (q (c i)) (q (c j)) = 1) : 8 ≤ Fintype.card T := by
  classical
  let A : Matrix (Fin 8) T K := Matrix.of fun i k => W (c i) k
  let B : Matrix (Fin 8) T K := Matrix.of fun j k => U (c j) k
  have h : A * Bᵀ = 1 := by
    ext i j
    simp only [A, B, Matrix.mul_apply, Matrix.transpose_apply, Matrix.of_apply, Matrix.one_apply]
    by_cases hij : i = j
    · subst hij; simpa using hd.diag (c i)
    · rw [if_neg hij]; exact hd.odd _ _ (fun e => hij (hc e)) (hodd i j hij)
  have h1 : (A * Bᵀ).rank ≤ A.rank := Matrix.rank_mul_le_left _ _
  have h2 : A.rank ≤ Fintype.card T := Matrix.rank_le_card_width A
  rw [h, Matrix.rank_one] at h1
  simpa using h1.trans h2

/-- **Rank-8 floor = 56 as a reduction.**  Given `Rank8Spans` (the one named finite hypothesis), `h = 9` and
8 pairwise-odd ports, every decoder over a field has mass ≥ 7·8 = 56. -/
theorem rank8_floor {K : Type*} [Field K] (q : ι → κ → ZMod 2) (W U : ι → T → K)
    (hd : IsDecoder q W U) (h9 : Fintype.card κ = 9) (hs : Rank8Spans q W U)
    (c : Fin 8 → ι) (hc : Function.Injective c)
    (hodd : ∀ i j, i ≠ j → dot (q (c i)) (q (c j)) = 1) : 56 ≤ mass q W U := by
  have h1 := rows_ge_eight q W U hd c hc hodd
  have h2 : ∑ _k : T, 7 ≤ mass q W U := Finset.sum_le_sum fun k _ => rowPrice_ge_seven q W U h9 hs k
  simp only [Finset.sum_const, Finset.card_univ, smul_eq_mul] at h2
  omega

end Rank8


section Graded
variable {κ ι T : Type*} [Fintype κ] [Fintype ι] [DecidableEq ι] [Fintype T]

/-- 0/1 integer lift of the odd-cell matrix. -/
noncomputable def Qi (q : ι → κ → ZMod 2) : Matrix ι ι ℤ_[2] :=
  Matrix.of fun t s => ((Qm q t s).val : ℤ_[2])

/-- `1 + 2X` is invertible over `ℤ_[2]` (its determinant reduces to 1 mod 2). -/
theorem isUnit_det_one_add_two (X : Matrix ι ι ℤ_[2]) : IsUnit (1 + (2 : ℤ_[2]) • X).det := by
  rw [← IsLocalRing.notMem_maximalIdeal, ← PadicInt.ker_toZMod, RingHom.mem_ker]
  have h := RingHom.map_det (PadicInt.toZMod : ℤ_[2] →+* ZMod 2) (1 + (2 : ℤ_[2]) • X)
  have h2 : (PadicInt.toZMod : ℤ_[2] →+* ZMod 2).mapMatrix (1 + (2 : ℤ_[2]) • X) = 1 := by
    ext a b
    have h2z : (PadicInt.toZMod : ℤ_[2] →+* ZMod 2) 2 = 0 := by
      have h1 := map_natCast (PadicInt.toZMod : ℤ_[2] →+* ZMod 2) 2
      have h3 : ((2 : ℕ) : ZMod 2) = 0 := by decide
      rw [h3] at h1
      exact_mod_cast h1
    by_cases hab : a = b
    · subst hab; simp [h2z]
    · simp [Matrix.one_apply, hab, h2z]
  rw [h2, Matrix.det_one] at h
  rw [h]; exact one_ne_zero

/-- **Graded 2-adic floor, level e = 1 (ADICWALL §2).**  Rows `k` with `W`, `V = 2U` 2-adically
integral (denominators ≤ 2): `Σ_k W t k V s k` is `2` on the diagonal, `0` on odd cells.  If `L_k ≡ Q`
(mod 4) on the support `D_k × S_k`, then `n ≤ Σ_k rank_{ℚ₂} L_k[D_k, S_k]`.
(`s_k` of the card = this rank for the best lift `L_k`.) -/
theorem graded_floor_e1 (q : ι → κ → ZMod 2) (hodd : ∀ t, dot (q t) (q t) = 1)
    (W V : ι → T → ℤ_[2])
    (hoff : ∀ t s, t ≠ s → dot (q t) (q s) = 1 → ∑ k, W t k * V s k = 0)
    (hdiag : ∀ t, ∑ k, W t k * V t k = 2)
    (L : T → Matrix ι ι ℤ_[2])
    (hL : ∀ k t s, W t k ≠ 0 → V s k ≠ 0 → ∃ e : ℤ_[2], L k t s = Qi q t s + 4 * e) :
    Fintype.card ι ≤ ∑ k, Matrix.rank (((PadicInt.Coe.ringHom : ℤ_[2] →+* ℚ_[2]).mapMatrix (L k)).submatrix
        ((↑) : dep W k → ι) ((↑) : gat V k → ι)) := by
  classical
  let c : ℤ_[2] →+* ℚ_[2] := PadicInt.Coe.ringHom
  have hc0 : ∀ x : ℤ_[2], c x = 0 → x = 0 := fun x hx => by
    exact PadicInt.coe_eq_zero.1 hx
  let E : T → ι → ι → ℤ_[2] := fun k t s =>
    if h : W t k ≠ 0 ∧ V s k ≠ 0 then Classical.choose (hL k t s h.1 h.2) else 0
  let X : Matrix ι ι ℤ_[2] := Matrix.of fun t s => ∑ k, W t k * E k t s * V s k
  have hterm : ∀ k t s, W t k * L k t s * V s k = W t k * Qi q t s * V s k + 4 * (W t k * E k t s * V s k) := by
    intro k t s
    by_cases h : W t k ≠ 0 ∧ V s k ≠ 0
    · have := Classical.choose_spec (hL k t s h.1 h.2)
      simp only [E, dif_pos h]
      generalize Classical.choose (hL k t s h.1 h.2) = e at this ⊢
      rw [this]; ring
    · have : W t k = 0 ∨ V s k = 0 := by tauto
      rcases this with h0 | h0 <;> simp [h0]
  have hsum : ∑ k, (Matrix.diagonal (fun t => W t k) * L k * Matrix.diagonal (fun s => V s k))
      = (2 : ℤ_[2]) • (1 + (2 : ℤ_[2]) • X) := by
    ext t s
    simp only [Matrix.sum_apply, Matrix.mul_diagonal, Matrix.diagonal_mul, Matrix.smul_apply,
      Matrix.add_apply, X, Matrix.of_apply, smul_eq_mul]
    have e1 : ∀ k, W t k * L k t s * V s k = W t k * Qi q t s * V s k + 4 * (W t k * E k t s * V s k) :=
      fun k => hterm k t s
    simp only [e1, Finset.sum_add_distrib, ← Finset.mul_sum]
    have e2 : ∑ k, W t k * Qi q t s * V s k = Qi q t s * ∑ k, W t k * V s k := by
      rw [Finset.mul_sum]; exact Finset.sum_congr rfl fun k _ => by ring
    rw [e2]
    by_cases hts : t = s
    · subst hts
      have hq1 : Qm q t t = 1 := by simpa [Qm] using hodd t
      have : Qi q t t = 1 := by
        simp only [Qi, Matrix.of_apply, hq1]
        rw [show (1 : ZMod 2).val = 1 from rfl]; simp
      rw [this, hdiag, Matrix.one_apply_eq]; ring
    · rw [Matrix.one_apply_ne hts]
      by_cases hd : dot (q t) (q s) = 1
      · rw [hoff t s hts hd]; ring
      · have h0 : dot (q t) (q s) = 0 := by
          revert hd; generalize dot (q t) (q s) = z; revert z; decide
        have : Qi q t s = 0 := by simp [Qi, Qm, h0]
        rw [this]; ring
  -- map to ℚ₂
  have hmap : ∑ k, Matrix.diagonal (fun t => c (W t k)) * c.mapMatrix (L k) * Matrix.diagonal (fun s => c (V s k))
      = c.mapMatrix ((2 : ℤ_[2]) • (1 + (2 : ℤ_[2]) • X)) := by
    rw [← hsum, map_sum]
    refine Finset.sum_congr rfl fun k _ => ?_
    rw [map_mul, map_mul]
    congr 2 <;> ext a b <;> simp [Matrix.diagonal_apply] <;> split_ifs <;> simp
  have hrank : (c.mapMatrix ((2 : ℤ_[2]) • (1 + (2 : ℤ_[2]) • X))).rank = Fintype.card ι := by
    apply Matrix.rank_of_isUnit
    rw [Matrix.isUnit_iff_isUnit_det]
    have hd := isUnit_det_one_add_two X
    have heq : (c.mapMatrix ((2 : ℤ_[2]) • (1 + (2 : ℤ_[2]) • X))) = (c 2) • c.mapMatrix (1 + (2 : ℤ_[2]) • X) := by
      ext a b
      simp [RingHom.mapMatrix_apply, Matrix.smul_apply]
      ring
    rw [heq, Matrix.det_smul, ← RingHom.map_det]
    have h2 : c 2 ≠ 0 := by
      intro h; have := hc0 2 h; exact absurd this (by norm_num)
    have h3 : c (1 + (2 : ℤ_[2]) • X).det ≠ 0 := by
      intro h; exact hd.ne_zero (hc0 _ h)
    exact (mul_ne_zero (pow_ne_zero _ h2) h3).isUnit
  have hle : ∀ k, (Matrix.diagonal (fun t => c (W t k)) * c.mapMatrix (L k) * Matrix.diagonal (fun s => c (V s k))).rank
      ≤ ((c.mapMatrix (L k)).submatrix ((↑) : dep W k → ι) ((↑) : gat V k → ι)).rank := by
    intro k
    apply rank_diag_mul_mul_diag_le _ _ _ (dep W k) (gat V k)
    · intro t ht
      simp only [dep, Finset.mem_filter, Finset.mem_univ, true_and]
      intro h0; apply ht; rw [h0, map_zero]
    · intro s hs
      simp only [gat, Finset.mem_filter, Finset.mem_univ, true_and]
      intro h0; apply hs; rw [h0, map_zero]
  calc Fintype.card ι = (∑ k, Matrix.diagonal (fun t => c (W t k)) * c.mapMatrix (L k) * Matrix.diagonal (fun s => c (V s k))).rank := by
        rw [hmap, hrank]
    _ ≤ ∑ k, (Matrix.diagonal (fun t => c (W t k)) * c.mapMatrix (L k) * Matrix.diagonal (fun s => c (V s k))).rank := rank_sum_le _ _
    _ ≤ _ := Finset.sum_le_sum fun k _ => hle k


theorem rowPrice_le_card {R : Type*} [Zero R] (q : ι → κ → ZMod 2) (W U : ι → T → R) (k : T) :
    rowPrice q W U k ≤ Fintype.card κ := by
  have h := pairing_rank_eq (fun t : dep W k => q t) (fun s : gat U k => q s)
  have h2 : Module.finrank (ZMod 2) (Submodule.span (ZMod 2) (Set.range fun t : dep W k => q t))
      ≤ Fintype.card κ := by
    have := Submodule.finrank_le (Submodule.span (ZMod 2) (Set.range fun t : dep W k => q t))
    simpa using this
  have h3 : rowPrice q W U k = (Matrix.of fun (t : dep W k) (s : gat U k) => dot (q t) (q s)).rank := rfl
  omega

/-- NAMED HYPOTHESIS `LiftRankBound` (paper, ADICWALL §2 last bullet; not formalised): the mod-4 lift
`L_k` of the pairing block can be chosen with `2·rank_ℚ L_k ≤ r_k (r_k + 1)`, `r_k` the row price
(lift an 𝔽₂ factorisation `ΦΨᵀ`; the mod-4 correction has 𝔽₂-rank ≤ C(r,2)). -/
def LiftRankBound (q : ι → κ → ZMod 2) (W V : ι → T → ℤ_[2]) (L : T → Matrix ι ι ℤ_[2]) : Prop :=
  ∀ k, 2 * Matrix.rank (((PadicInt.Coe.ringHom : ℤ_[2] →+* ℚ_[2]).mapMatrix (L k)).submatrix
        ((↑) : dep W k → ι) ((↑) : gat V k → ι)) ≤ rowPrice q W V k * (rowPrice q W V k + 1)

/-- Half-integer decoders (e = 1): `2n ≤ (h+1)·C`, i.e. `C ≥ 2n/(h+1)`.  At `n = 104`, `h = 9`: `C ≥ 21`. -/
theorem half_integer_floor (q : ι → κ → ZMod 2) (hodd : ∀ t, dot (q t) (q t) = 1)
    (W V : ι → T → ℤ_[2])
    (hoff : ∀ t s, t ≠ s → dot (q t) (q s) = 1 → ∑ k, W t k * V s k = 0)
    (hdiag : ∀ t, ∑ k, W t k * V t k = 2)
    (L : T → Matrix ι ι ℤ_[2])
    (hL : ∀ k t s, W t k ≠ 0 → V s k ≠ 0 → ∃ e : ℤ_[2], L k t s = Qi q t s + 4 * e)
    (hlift : LiftRankBound q W V L) :
    2 * Fintype.card ι ≤ (Fintype.card κ + 1) * mass q W V := by
  have h1 := graded_floor_e1 q hodd W V hoff hdiag L hL
  have h2 : 2 * ∑ k, Matrix.rank (((PadicInt.Coe.ringHom : ℤ_[2] →+* ℚ_[2]).mapMatrix (L k)).submatrix
        ((↑) : dep W k → ι) ((↑) : gat V k → ι)) ≤ ∑ k, rowPrice q W V k * (rowPrice q W V k + 1) := by
    rw [Finset.mul_sum]; exact Finset.sum_le_sum fun k _ => hlift k
  have h3 : ∑ k, rowPrice q W V k * (rowPrice q W V k + 1) ≤ ∑ k, (Fintype.card κ + 1) * rowPrice q W V k :=
    Finset.sum_le_sum fun k _ => by
      have := rowPrice_le_card q W V k
      nlinarith [Nat.zero_le (rowPrice q W V k)]
  rw [← Finset.mul_sum] at h3
  exact le_trans (by omega) (h3.trans (le_of_eq (by rw [mass])))

theorem half_integer_floor_104 (q : ι → κ → ZMod 2) (hodd : ∀ t, dot (q t) (q t) = 1)
    (W V : ι → T → ℤ_[2])
    (hoff : ∀ t s, t ≠ s → dot (q t) (q s) = 1 → ∑ k, W t k * V s k = 0)
    (hdiag : ∀ t, ∑ k, W t k * V t k = 2)
    (L : T → Matrix ι ι ℤ_[2])
    (hL : ∀ k t s, W t k ≠ 0 → V s k ≠ 0 → ∃ e : ℤ_[2], L k t s = Qi q t s + 4 * e)
    (hlift : LiftRankBound q W V L) (hn : Fintype.card ι = 104) (hh : Fintype.card κ = 9) :
    21 ≤ mass q W V := by
  have := half_integer_floor q hodd W V hoff hdiag L hL hlift
  rw [hn, hh] at this
  omega

end Graded


section OrthCover
variable {ι T : Type*} [Fintype ι] [DecidableEq ι] [Fintype T]

/-- h = 3, subcase "without j" (ADICWALL §4), any ring `R ≠ 0`: every port needs a row that both deposits
into and gathers from it, so `n ≤ Σ_k |D_k ∩ S_k|`.  For an orthonormal label set `Qm = 1` and the
price of a row is `|D_k ∩ S_k|`, giving `C ≥ n` for every field.  (Only the counting step is
kernel-checked; the equality price = `|D ∩ S|` for `Qm = 1` is not.) -/
theorem card_le_sum_inter {R : Type*} [CommRing R] [Nontrivial R] (W U : ι → T → R)
    (hdiag : ∀ t, ∑ k, W t k * U t k = 1) :
    Fintype.card ι ≤ ∑ k, (dep W k ∩ gat U k).card := by
  classical
  have h1 : ∀ t : ι, 1 ≤ ∑ k, (if t ∈ dep W k ∩ gat U k then 1 else 0) := by
    intro t
    by_contra hlt
    rw [not_le] at hlt
    have hz : ∑ k, (if t ∈ dep W k ∩ gat U k then 1 else 0) = 0 := by omega
    have hk : ∀ k, t ∉ dep W k ∩ gat U k := by
      intro k hk
      have := (Finset.sum_eq_zero_iff.1 hz) k (Finset.mem_univ k)
      simp [hk] at this
    have : ∑ k, W t k * U t k = 0 := Finset.sum_eq_zero fun k _ => by
      by_contra hne
      apply hk k
      simp only [dep, gat, Finset.mem_inter, Finset.mem_filter, Finset.mem_univ, true_and]
      exact ⟨left_ne_zero_of_mul hne, right_ne_zero_of_mul hne⟩
    rw [hdiag t] at this
    exact one_ne_zero this
  calc Fintype.card ι = ∑ _t : ι, 1 := by simp
    _ ≤ ∑ t : ι, ∑ k, (if t ∈ dep W k ∩ gat U k then 1 else 0) := Finset.sum_le_sum fun t _ => h1 t
    _ = ∑ k, ∑ t : ι, (if t ∈ dep W k ∩ gat U k then 1 else 0) := Finset.sum_comm
    _ = ∑ k, (dep W k ∩ gat U k).card :=
        Finset.sum_congr rfl fun k _ => by
          rw [Finset.sum_boole, Nat.cast_id]
          exact congrArg Finset.card (by ext t; simp)

end OrthCover

end DecoderWall

#print axioms DecoderWall.pairing_rank_eq
#print axioms DecoderWall.pairing_rank_ge
#print axioms DecoderWall.rank8_floor
#print axioms DecoderWall.graded_floor_e1
#print axioms DecoderWall.half_integer_floor_104
#print axioms DecoderWall.card_le_sum_inter
