/-
SPECBREAK R68 (GC/II, TWIN, SPLIT-EQ) and R71 (L1), Sources: internal notes,AUDIT68}.md, R71/{RESULT71,AUDIT71}.md. See SpecGC.md.
Builds on Nov15/SpecTS.lean (model_commute, lemmaTS_model, refl_sq, ...), SpecINV.lean (inv_word),
PadLift.lean (rank_blockdiag), SpecTSUR.lean (ev/jobsP/uconj/ucount, UR_upper).
-/
import Nov15.SpecTS
import Nov15.SpecINV
import Nov15.PadLift
import Mathlib.LinearAlgebra.Matrix.Rank

open Matrix Finset SpecTSUR Module

set_option linter.unusedSectionVars false

namespace SpecGC

variable {K : Type*} [Field K]

/-! ## §A. rank helpers -/
section Rank
variable {n : Type*} [Fintype n] [DecidableEq n]

theorem eq_of_mulVec_eq (A B : Matrix n n K) (h : ∀ v, A *ᵥ v = B *ᵥ v) : A = B := by
  ext i j
  have := congrFun (h (Pi.single j 1)) i
  simpa [Matrix.mulVec_single_one] using this

theorem rank_mul_invol_left (X A : Matrix n n K) (hX : X * X = 1) : (X * A).rank = A.rank := by
  have hu : IsUnit X.det :=
    (Matrix.isUnit_iff_isUnit_det X).1 (⟨⟨X, X, hX, hX⟩, rfl⟩)
  exact Matrix.rank_mul_eq_right_of_isUnit_det X A hu

theorem rank_mul_invol_right (A X : Matrix n n K) (hX : X * X = 1) : (A * X).rank = A.rank := by
  have hu : IsUnit X.det :=
    (Matrix.isUnit_iff_isUnit_det X).1 (⟨⟨X, X, hX, hX⟩, rfl⟩)
  exact Matrix.rank_mul_eq_left_of_isUnit_det X A hu

theorem rank_smul_eq (c : K) (hc : c ≠ 0) (A : Matrix n n K) : (c • A).rank = A.rank := by
  have h1 : (c • A) = (diagonal fun _ : n => c) * A := by ext i j; simp [diagonal_mul]
  have h2 : A = (diagonal fun _ : n => c⁻¹) * (c • A) := by
    ext i j; simp [diagonal_mul, hc]
  apply le_antisymm
  · rw [h1]; exact rank_mul_le_right _ _
  · conv_lhs => rw [h2]
    exact rank_mul_le_right _ _

theorem rank_sub_comm (A B : Matrix n n K) : (A - B).rank = (B - A).rank := by
  rw [← neg_sub, SpecTSUR.rank_neg_eq]

/-- nested ranges: `rank(A-B) + rank B ≤ rank A` ⇒ `range B ⊆ range A`. -/
theorem range_le_of_rank (A B : Matrix n n K) (h : (A - B).rank + B.rank ≤ A.rank) (v : n → K) :
    ∃ z, A *ᵥ z = B *ᵥ v := by
  set S : Submodule K (n → K) :=
    LinearMap.range (A - B).mulVecLin ⊔ LinearMap.range B.mulVecLin with hS
  have hle : LinearMap.range A.mulVecLin ≤ S := by
    rintro _ ⟨w, rfl⟩
    have e : A *ᵥ w = (A - B) *ᵥ w + B *ᵥ w := by rw [Matrix.sub_mulVec]; abel
    show A *ᵥ w ∈ S
    rw [e]
    exact Submodule.add_mem_sup ⟨w, rfl⟩ ⟨w, rfl⟩
  have hfin : finrank K S ≤ finrank K (LinearMap.range A.mulVecLin) := by
    refine (Submodule.finrank_add_le_finrank_add_finrank _ _).trans ?_
    exact h
  have heq := Submodule.eq_of_le_of_finrank_le hle hfin
  have : B *ᵥ v ∈ LinearMap.range A.mulVecLin := by
    rw [heq]
    exact Submodule.mem_sup_right ⟨v, rfl⟩
  obtain ⟨z, hz⟩ := this
  exact ⟨z, hz⟩

/-- idempotents, `rank(P-Q) + rank Q ≤ rank P` ⇒ `P Q = Q`. -/
theorem idem_nested (P Q : Matrix n n K) (hP : P * P = P)
    (h : (P - Q).rank + Q.rank ≤ P.rank) : P * Q = Q := by
  apply eq_of_mulVec_eq
  intro v
  obtain ⟨z, hz⟩ := range_le_of_rank P Q h v
  rw [← Matrix.mulVec_mulVec, ← hz, Matrix.mulVec_mulVec, hP]

theorem idem_comm (P Q : Matrix n n K) (hP : P * P = P)
    (h : (P - Q).rank + Q.rank ≤ P.rank) : P * Q = Q * P := by
  have h1 := idem_nested P Q hP h
  have hPt : Pᵀ * Pᵀ = Pᵀ := by rw [← Matrix.transpose_mul, hP]
  have h' : (Pᵀ - Qᵀ).rank + Qᵀ.rank ≤ Pᵀ.rank := by
    rw [← Matrix.transpose_sub, Matrix.rank_transpose, Matrix.rank_transpose,
      Matrix.rank_transpose]
    exact h
  have h2 := idem_nested Pᵀ Qᵀ hPt h'
  have h3 : Q * P = Q := by
    have := congrArg Matrix.transpose h2
    rw [Matrix.transpose_mul, Matrix.transpose_transpose, Matrix.transpose_transpose] at this
    exact this
  rw [h1, h3]

/-- two involutions with `rank(D-K) + rank(1-K) ≤ rank(1-D)` commute. -/
theorem invol_commute (h2 : (2 : K) ≠ 0) (D K' : Matrix n n K) (hD : D * D = 1) (hK : K' * K' = 1)
    (h : (D - K').rank + (1 - K').rank ≤ (1 - D).rank) : D * K' = K' * D := by
  set P : Matrix n n K := (2 : K)⁻¹ • (1 - D) with hPdef
  set Q : Matrix n n K := (2 : K)⁻¹ • (1 - K') with hQdef
  have h2i : (2 : K) * (2 : K)⁻¹ = 1 := mul_inv_cancel₀ h2
  have hPD : D = 1 - (2 : K) • P := by
    rw [hPdef, smul_smul, h2i, one_smul]; abel
  have hQK : K' = 1 - (2 : K) • Q := by
    rw [hQdef, smul_smul, h2i, one_smul]; abel
  have hPP : P * P = P := by
    have : (1 - D) * (1 - D) = (2 : K) • (1 - D) := by
      have : (1 - D) * (1 - D) = 1 - D - D + D * D := by noncomm_ring
      rw [this, hD, two_smul]; abel
    rw [hPdef, smul_mul_smul_comm, this, smul_smul]
    congr 1; field_simp
  have hrP : P.rank = (1 - D).rank := rank_smul_eq _ (inv_ne_zero h2) _
  have hrQ : Q.rank = (1 - K').rank := rank_smul_eq _ (inv_ne_zero h2) _
  have hPQ : (P - Q).rank = (D - K').rank := by
    have : P - Q = (-(2 : K)⁻¹) • (D - K') := by
      rw [hPdef, hQdef, ← smul_sub, neg_smul, ← smul_neg]; congr 1; abel
    rw [this, rank_smul_eq _ (neg_ne_zero.2 (inv_ne_zero h2))]
  have hc := idem_comm P Q hPP (by rw [hPQ, hrQ, hrP]; exact h)
  rw [hPD, hQK]
  simp only [mul_sub, sub_mul, Matrix.mul_one, Matrix.one_mul, smul_mul_assoc, mul_smul_comm,
    hc]
  module

/-- the reflection `1 - x yᵀ` has `rank (· - 1) ≤ 1` -/
theorem refl_sub_one_rank (a b : n → K) : (SpecTSUR.refl a b - 1).rank ≤ 1 := by
  have : SpecTSUR.refl a b - 1 = -vecMulVec a b := by simp [SpecTSUR.refl]
  rw [this, SpecTSUR.rank_neg_eq]
  exact Matrix.rank_vecMulVec_le a b

theorem refl_one_sub_rank (a b : n → K) : (1 - SpecTSUR.refl a b).rank ≤ 1 := by
  rw [rank_sub_comm]; exact refl_sub_one_rank a b

/-- a rank-one drop forces `x` into the range of `A`. -/
theorem mem_range_of_rank_lt (A : Matrix n n K) (x y : n → K)
    (h : (A - vecMulVec x y).rank < A.rank) : ∃ z, A *ᵥ z = x := by
  by_contra hx
  push Not at hx
  set B : Matrix n n K := A - vecMulVec x y with hB
  have hker : LinearMap.ker B.mulVecLin ≤ LinearMap.ker A.mulVecLin := by
    intro v hv
    have hv' : B *ᵥ v = 0 := hv
    have e : B *ᵥ v = A *ᵥ v - (y ⬝ᵥ v) • x := by
      rw [hB, Matrix.sub_mulVec, Matrix.vecMulVec_mulVec]
      simp
    have hyv : y ⬝ᵥ v = 0 := by
      by_contra hne
      apply hx ((y ⬝ᵥ v)⁻¹ • v)
      rw [Matrix.mulVec_smul]
      have : A *ᵥ v = (y ⬝ᵥ v) • x := by rw [e] at hv'; exact sub_eq_zero.1 hv'
      rw [this, smul_smul, inv_mul_cancel₀ hne, one_smul]
    rw [hyv, zero_smul, sub_zero] at e
    show A *ᵥ v = 0
    rw [← e]; exact hv'
  have h1 := Submodule.finrank_mono hker
  have rA := LinearMap.finrank_range_add_finrank_ker A.mulVecLin
  have rB := LinearMap.finrank_range_add_finrank_ker B.mulVecLin
  have : A.rank ≤ B.rank := by
    unfold Matrix.rank; omega
  omega

end Rank

/-! ## §B. conjugating a reflection -/
section Conj
variable {n : Type*} [Fintype n] [DecidableEq n]

/-- conjugating `1 - a bᵀ` by a unit gives `1 - (P a)(b P⁻¹)ᵀ` with the same pairing `b·a`. -/
theorem conj_form_c (P t : (Matrix n n K)ˣ) (c : K) (a b : n → K) (hab : b ⬝ᵥ a = c)
    (ht : (t : Matrix n n K) = SpecTSUR.refl a b) :
    ∃ a' b' : n → K, b' ⬝ᵥ a' = c ∧
      ((P * t * P⁻¹ : (Matrix n n K)ˣ) : Matrix n n K) = SpecTSUR.refl a' b' := by
  refine ⟨(P : Matrix n n K) *ᵥ a, b ᵥ* ((P⁻¹ : (Matrix n n K)ˣ) : Matrix n n K), ?_, ?_⟩
  · rw [Matrix.dotProduct_mulVec, Matrix.vecMul_vecMul]
    have : ((P⁻¹ : (Matrix n n K)ˣ) : Matrix n n K) * (P : Matrix n n K) = 1 := P.inv_mul
    rw [this, Matrix.vecMul_one]
    exact hab
  · have hPP : (P : Matrix n n K) * ((P⁻¹ : (Matrix n n K)ˣ) : Matrix n n K) = 1 := P.mul_inv
    simp only [Units.val_mul, ht, SpecTSUR.refl, mul_sub, sub_mul, Matrix.mul_one,
      Matrix.mul_vecMulVec, Matrix.vecMulVec_mul, hPP]

end Conj

/-! ## §C. The commuting family `K`: involution, `rank(1 - K) = b` -/
section KFam
variable {n : Type*} [Fintype n] [DecidableEq n] [DecidableEq K]

/-- `b` reflections with Gram `y_i·x_j = 2 δ_ij` (the odd classes' target-pairs): their product `K` is an
involution and `rank(1 - K) = b`. -/
theorem K_data (h2 : (2 : K) ≠ 0) (b : ℕ) (x y : ℕ → n → K)
    (hg : ∀ i j : Fin b, y i ⬝ᵥ x j = if i = j then 2 else 0) :
    pp x y b * pp x y b = 1 ∧ (1 - pp x y b).rank = b := by
  have hc : ∀ i j, Commute (SpecTS.gJ x y b i) (SpecTS.gJ x y b j) := by
    intro i j
    by_cases hij : i = j
    · subst hij; exact Commute.refl _
    · exact SpecTS.refl_comm _ _ _ _ (by simp [hg i j, hij]) (by simp [hg j i, Ne.symm hij])
  have hs : ∀ i, SpecTS.gJ x y b i * SpecTS.gJ x y b i = 1 := fun i =>
    SpecTS.refl_sq _ _ (by simpa using hg i i)
  constructor
  · rw [SpecTS.pp_eq_prod, SpecTS.prod_ofFn_mul b _ _ (fun i j => hc i j)]
    have : (fun i : Fin b => SpecTS.gJ x y b i * SpecTS.gJ x y b i) = fun _ => 1 := funext hs
    rw [this]; simp
  · have hGm : (SpecTS.Ym y b)ᵀ * Xm x b = (2 : K) • (1 : Matrix (Fin b) (Fin b) K) := by
      ext i j
      have := gram_apply x y b i j
      simp only [SpecTS.Ym] at this ⊢
      rw [this, hg i j]
      simp [Matrix.one_apply]
    have hN : Nm x y b = 1 := by
      ext i j
      simp only [Nm, Matrix.add_apply, Matrix.of_apply]
      by_cases hij : i < j
      · simp [hij, hg i j, hij.ne]
      · simp [hij]
    have hZ : Zm x y b = Xm x b := by
      have := ZN_eq x y b
      rwa [hN, Matrix.mul_one] at this
    have e : 1 - pp x y b = Xm x b * (SpecTS.Ym y b)ᵀ := by
      rw [SpecINV.one_sub_pp, hZ]; rfl
    rw [e]
    apply le_antisymm
    · exact (rank_mul_le_left _ _).trans ((Matrix.rank_le_card_width _).trans (by simp))
    · have h4 : (4 : K) ≠ 0 := by
        have : (4 : K) = 2 * 2 := by norm_num
        rw [this]; exact mul_ne_zero h2 h2
      have hh : (SpecTS.Ym y b)ᵀ * (Xm x b * (SpecTS.Ym y b)ᵀ) * Xm x b = (4 : K) • (1 : Matrix (Fin b) (Fin b) K) := by
        calc (SpecTS.Ym y b)ᵀ * (Xm x b * (SpecTS.Ym y b)ᵀ) * Xm x b
            = ((SpecTS.Ym y b)ᵀ * Xm x b) * ((SpecTS.Ym y b)ᵀ * Xm x b) := by
              simp only [Matrix.mul_assoc]
          _ = _ := by
            rw [hGm, smul_mul_smul_comm, Matrix.mul_one]; congr 1; norm_num
      have hrk : ((4 : K) • (1 : Matrix (Fin b) (Fin b) K)).rank = b := by
        have : (4 : K) • (1 : Matrix (Fin b) (Fin b) K) = diagonal fun _ => (4 : K) := by
          ext i j; by_cases h : i = j <;> simp [Matrix.one_apply, diagonal_apply, h]
        rw [this, rank_diagonal]; simp [h4]
      have h5 : ((SpecTS.Ym y b)ᵀ * (Xm x b * (SpecTS.Ym y b)ᵀ) * Xm x b).rank ≤
          (Xm x b * (SpecTS.Ym y b)ᵀ).rank :=
        (rank_mul_le_left _ _).trans (rank_mul_le_right _ _)
      rw [hh, hrk] at h5
      exact h5

end KFam

/-! ## §D. The kill count (GC/II) -/
section Kill
variable {n : Type*} [Fintype n] [DecidableEq n] [DecidableEq K]

/-- interface to the unit-count budget: for a word `w` with transvection units, `D = ev w`,
`J = jobsP w`, `U = ucount w`: (up) `rank(D - J) ≤ U`; (inv) if `g = D J⁻¹` is an involution then
`rank(D - J) ≤ U - 1` (INV).  -/
theorem word_up_inv (h2 : (2 : K) ≠ 0)
    (w : List ((Matrix n n K)ˣ ⊕ (Matrix n n K)ˣ))
    (hform : ∀ t, Sum.inl t ∈ w → ∃ a b : n → K, b ⬝ᵥ a = 0 ∧ (t : Matrix n n K) = SpecTSUR.refl a b) :
    (((ev w : (Matrix n n K)ˣ) : Matrix n n K) - ((jobsP w : (Matrix n n K)ˣ) : Matrix n n K)).rank
        ≤ ucount w ∧
    ((((ev w : (Matrix n n K)ˣ) : Matrix n n K) * (((jobsP w)⁻¹ : (Matrix n n K)ˣ) : Matrix n n K)) *
        (((ev w : (Matrix n n K)ˣ) : Matrix n n K) * (((jobsP w)⁻¹ : (Matrix n n K)ˣ) : Matrix n n K)) = 1 →
      (((ev w : (Matrix n n K)ˣ) : Matrix n n K) - ((jobsP w : (Matrix n n K)ˣ) : Matrix n n K)).rank
        ≤ ucount w - 1) := by
  refine ⟨SpecTSUR.UR_upper w (fun t ht => ?_), fun hg => ?_⟩
  · obtain ⟨a, b, -, ht'⟩ := hform t ht
    rw [ht']
    exact refl_sub_one_rank a b
  · have h1 := ev_move w 1
    simp only [one_mul] at h1
    have hgu : (uconj w 1).prod = ev w * (jobsP w)⁻¹ := eq_mul_inv_of_mul_eq h1.symm
    have hg' : (((uconj w 1).prod : (Matrix n n K)ˣ) : Matrix n n K) *
        (((uconj w 1).prod : (Matrix n n K)ˣ) : Matrix n n K) = 1 := by
      rw [hgu]; simpa using hg
    have hINV := SpecINV.inv_word h2 w hform hg'
    have e : ((ev w : (Matrix n n K)ˣ) : Matrix n n K) - ((jobsP w : (Matrix n n K)ˣ) : Matrix n n K) =
        -((1 - (((uconj w 1).prod : (Matrix n n K)ˣ) : Matrix n n K)) *
          ((jobsP w : (Matrix n n K)ˣ) : Matrix n n K)) := by
      rw [h1]; simp [sub_mul]
    rw [e, SpecTSUR.rank_neg_eq]
    exact (rank_mul_le_left _ _).trans hINV

/-- if `J = R K` with involutions `R, K` then `J⁻¹ = K R` -/
theorem inv_of_RK (J : (Matrix n n K)ˣ) (R K' : Matrix n n K) (hR : R * R = 1) (hK : K' * K' = 1)
    (hJ : (J : Matrix n n K) = R * K') : ((J⁻¹ : (Matrix n n K)ˣ) : Matrix n n K) = K' * R := by
  have h1 : (J : Matrix n n K) * (K' * R) = 1 := by
    rw [hJ]; calc R * K' * (K' * R) = R * (K' * K') * R := by simp only [Matrix.mul_assoc]
      _ = 1 := by rw [hK, Matrix.mul_one, hR]
  calc ((J⁻¹ : (Matrix n n K)ˣ) : Matrix n n K) = ((J⁻¹ : (Matrix n n K)ˣ) : Matrix n n K) * 1 := by simp
    _ = ((J⁻¹ : (Matrix n n K)ˣ) : Matrix n n K) * ((J : Matrix n n K) * (K' * R)) := by rw [h1]
    _ = K' * R := by rw [← Matrix.mul_assoc, J.inv_mul, Matrix.one_mul]

/-- gap lower bound: `|r - b| ≤ rank(D - K)` for `r = rank(1 - D)`, `b = rank(1 - K)`. -/
theorem gap_le (D K' : Matrix n n K) :
    ((1 - D).rank - (1 - K').rank) + ((1 - K').rank - (1 - D).rank) ≤ (D - K').rank := by
  have h1 := rank_le_sub_add (1 - D) (1 - K')
  have h2 := rank_le_sub_add (1 - K') (1 - D)
  have e1 : (1 - D) - (1 - K') = K' - D := by abel
  have e2 : (1 - K') - (1 - D) = D - K' := by abel
  rw [e1, rank_sub_comm K' D] at h1
  rw [e2] at h2
  omega

/-- **GC/II, strict form.** `J = R K` with `rank(1 - R) ≤ h`: `rank(D - J) ≥ gap - h`; so
`U + h < gap` (`gap = |r - b|`) is a contradiction with `rank(D - J) ≤ U`. -/
theorem gc_strict (D K' R J : Matrix n n K) (h U : ℕ) (hJ : J = R * K') (hR : (1 - R).rank ≤ h)
    (hup : (D - J).rank ≤ U)
    (hgap : U + h < ((1 - D).rank - (1 - K').rank) + ((1 - K').rank - (1 - D).rank)) : False := by
  have h1 := gap_le D K'
  have e : D - K' = (D - J) - (1 - R) * K' := by rw [hJ]; noncomm_ring
  have h2 : (D - K').rank ≤ (D - J).rank + (1 - R).rank := by
    rw [e]
    refine (SpecTSUR.rank_sub_le' _ _).trans ?_
    have := rank_mul_le_left (1 - R) K'
    omega
  omega

/-- **GC/II, h = 0** (`J = K`): `U ≤ gap` is dead (strict by the upper bound, equality by INV). -/
theorem gc_h0 (h2 : (2 : K) ≠ 0) (D K' : Matrix n n K) (U : ℕ) (hU : 0 < U)
    (hD : D * D = 1) (hK : K' * K' = 1)
    (hup : (D - K').rank ≤ U) (hinv : D * K' = K' * D → (D - K').rank ≤ U - 1)
    (hgap : U ≤ ((1 - D).rank - (1 - K').rank) + ((1 - K').rank - (1 - D).rank)) : False := by
  have h1 := gap_le D K'
  have hc : D * K' = K' * D := by
    by_cases hrb : (1 - K').rank ≤ (1 - D).rank
    · exact invol_commute h2 D K' hD hK (by omega)
    · refine (invol_commute h2 K' D hK hD ?_).symm
      rw [rank_sub_comm]; omega
  have := hinv hc
  omega

/-- **GC/II, h = 1** (`J = R K`, `R = 1 - x yᵀ` a reflection, `y·x = 2`): `U + 1 ≤ gap` is dead.
Equality case: `rank(D - K) = gap` ⇒ `D, K` commute ⇒ `E = DK` involution; `rank(R - E) < rank(1 - E)` ⇒
`x ∈ col(1 - E)`, `y ∈ row(1 - E)` ⇒ `E x = -x`, `y E = -y` ⇒ `R E = E R` ⇒ `g = E R` involution ⇒ INV. -/
theorem gc_h1 (h2 : (2 : K) ≠ 0) (D K' : Matrix n n K) (x y : n → K) (J : Matrix n n K) (U : ℕ)
    (hU : 0 < U) (hD : D * D = 1) (hK : K' * K' = 1) (hxy : y ⬝ᵥ x = 2)
    (hJ : J = SpecTSUR.refl x y * K')
    (hup : (D - J).rank ≤ U)
    (hinv : (D * K' * SpecTSUR.refl x y) * (D * K' * SpecTSUR.refl x y) = 1 → (D - J).rank ≤ U - 1)
    (hgap : U + 1 ≤ ((1 - D).rank - (1 - K').rank) + ((1 - K').rank - (1 - D).rank)) : False := by
  set R := SpecTSUR.refl x y with hRdef
  have hR2 : R * R = 1 := SpecTS.refl_sq x y hxy
  have hRr : (1 - R).rank ≤ 1 := refl_one_sub_rank x y
  have hlow := gap_le D K'
  have hup' : (D - K').rank ≤ (D - J).rank + 1 := by
    have e : D - K' = (D - J) - (1 - R) * K' := by rw [hJ]; noncomm_ring
    rw [e]
    refine (SpecTSUR.rank_sub_le' _ _).trans ?_
    have := rank_mul_le_left (1 - R) K'
    omega
  have hc : D * K' = K' * D := by
    by_cases hrb : (1 - K').rank ≤ (1 - D).rank
    · exact invol_commute h2 D K' hD hK (by omega)
    · refine (invol_commute h2 K' D hK hD ?_).symm
      rw [rank_sub_comm]; omega
  have hE2' : (D * K') * (D * K') = 1 := by
    calc D * K' * (D * K') = D * (K' * D) * K' := by simp only [Matrix.mul_assoc]
      _ = D * (D * K') * K' := by rw [hc]
      _ = (D * D) * (K' * K') := by simp only [Matrix.mul_assoc]
      _ = 1 := by rw [hD, hK, Matrix.mul_one]
  set E := D * K' with hE
  have hE2 : E * E = 1 := hE2'
  -- rank(1 - E) = rank(D - K) ≥ gap
  have hrE : (1 - E).rank = (D - K').rank := by
    have : 1 - E = D * (D - K') := by rw [hE, mul_sub, hD]
    rw [this]; exact rank_mul_invol_left D _ hD
  -- rank(R - E) = rank(D - J)
  have hrRE : (R - E).rank = (D - J).rank := by
    have : D - J = (E - R) * K' := by
      rw [hJ, hE]; calc D - R * K' = D * (K' * K') - R * K' := by rw [hK, Matrix.mul_one]
        _ = _ := by noncomm_ring
    rw [this, rank_mul_invol_right _ _ hK, rank_sub_comm]
  have hlt : (R - E).rank < (1 - E).rank := by omega
  have eRE : R - E = (1 - E) - vecMulVec x y := by rw [hRdef]; simp [SpecTSUR.refl]; abel
  rw [eRE] at hlt
  obtain ⟨z, hz⟩ := mem_range_of_rank_lt (1 - E) x y hlt
  -- transpose version for y
  have hlt' : ((1 - E)ᵀ - vecMulVec y x).rank < (1 - E)ᵀ.rank := by
    rw [← Matrix.transpose_vecMulVec, ← Matrix.transpose_sub, Matrix.rank_transpose,
      Matrix.rank_transpose]
    exact hlt
  obtain ⟨w, hw⟩ := mem_range_of_rank_lt (1 - E)ᵀ y x hlt'
  have hEx : E *ᵥ x = -x := by
    rw [← hz, Matrix.mulVec_mulVec]
    have : E * (1 - E) = -(1 - E) := by rw [mul_sub, Matrix.mul_one, hE2]; abel
    rw [this, Matrix.neg_mulVec]
  have hyE : y ᵥ* E = -y := by
    rw [← hw, Matrix.mulVec_transpose, Matrix.vecMul_vecMul]
    have : (1 - E) * E = -(1 - E) := by rw [sub_mul, Matrix.one_mul, hE2]; abel
    rw [this, Matrix.vecMul_neg]
  have hcomm : E * R = R * E := by
    rw [hRdef]
    simp only [SpecTSUR.refl, mul_sub, sub_mul, Matrix.mul_one, Matrix.one_mul,
      Matrix.mul_vecMulVec, Matrix.vecMulVec_mul, hEx, hyE]
    ext i j; simp
  have hg2 : (E * R) * (E * R) = 1 := by
    calc E * R * (E * R) = E * (R * E) * R := by simp only [Matrix.mul_assoc]
      _ = E * (E * R) * R := by rw [hcomm]
      _ = (E * E) * (R * R) := by simp only [Matrix.mul_assoc]
      _ = 1 := by rw [hE2, hR2, Matrix.mul_one]
  have hfin := hinv hg2
  omega

end Kill

/-! ## §E. TWIN rule and commutation inside a tight set -/
section Twin
variable {n : Type*} [Fintype n] [DecidableEq n]

/-- coefficient formula: with Gram `2 I`, `v = Σ c_i x_i` has `c_t = (y_t·v)/2`. -/
theorem twin_coeff (h2 : (2 : K) ≠ 0) (k : ℕ) (x y : ℕ → n → K)
    (hg : ∀ i j : Fin k, y i ⬝ᵥ x j = if i = j then 2 else 0)
    (c : Fin k → K) (v : n → K) (hv : v = ∑ i : Fin k, c i • x i) (t : Fin k) :
    y t ⬝ᵥ v = 2 * c t := by
  rw [hv, dotProduct_sum]
  simp only [dotProduct_smul, smul_eq_mul, hg t]
  simp [mul_comm]

/-- **TWIN rule** (R68 T3).  `j` is a job with `x_j ∈ span{x_t}`, `y_j ∈ span{y_t}` (support inside the
tight set's row space), `y_j·x_j = 2`; all `t ≠ t₀` are adjacent to `j` (`y_t·x_j = 0 = y_j·x_t`).
Then `x_j = c x_{t₀}`, `y_j = d y_{t₀}`, `c d = 1` and the two jobs are EQUAL: `g_j = g_{t₀}`. -/
theorem twin_rule (h2 : (2 : K) ≠ 0) (k : ℕ) (x y : ℕ → n → K)
    (hg : ∀ i j : Fin k, y i ⬝ᵥ x j = if i = j then 2 else 0)
    (xj yj : n → K) (c d : Fin k → K)
    (hx : xj = ∑ i : Fin k, c i • x i) (hy : yj = ∑ i : Fin k, d i • y i)
    (hjj : yj ⬝ᵥ xj = 2) (t0 : Fin k)
    (hadj : ∀ t : Fin k, t ≠ t0 → y t ⬝ᵥ xj = 0 ∧ yj ⬝ᵥ x t = 0) :
    SpecTSUR.refl xj yj = SpecTSUR.refl (x t0) (y t0) := by
  have hc : ∀ t, t ≠ t0 → c t = 0 := by
    intro t ht
    have := twin_coeff h2 k x y hg c xj hx t
    rw [(hadj t ht).1] at this
    have h' : (2 : K) * c t = 0 := this.symm
    exact (mul_eq_zero.1 h').resolve_left h2
  have hd : ∀ t, t ≠ t0 → d t = 0 := by
    intro t ht
    have h1 : yj ⬝ᵥ x t = 2 * d t := by
      rw [hy, sum_dotProduct]
      simp only [smul_dotProduct, smul_eq_mul]
      have : ∀ i : Fin k, d i * (y i ⬝ᵥ x t) = if i = t then 2 * d i else 0 := by
        intro i; rw [hg i t]; by_cases h : i = t <;> simp [h, mul_comm]
      simp only [this]; simp
    rw [(hadj t ht).2] at h1
    exact (mul_eq_zero.1 h1.symm).resolve_left h2
  have hx' : xj = c t0 • x t0 := by
    rw [hx, Finset.sum_eq_single t0]
    · intro t _ ht; rw [hc t ht, zero_smul]
    · intro h; exact absurd (Finset.mem_univ _) h
  have hy' : yj = d t0 • y t0 := by
    rw [hy, Finset.sum_eq_single t0]
    · intro t _ ht; rw [hd t ht, zero_smul]
    · intro h; exact absurd (Finset.mem_univ _) h
  have hcd : c t0 * d t0 = 1 := by
    rw [hx', hy', dotProduct_smul, smul_dotProduct, hg t0 t0] at hjj
    simp only [smul_eq_mul, if_true] at hjj
    have : (2 : K) * (c t0 * d t0) = 2 * 1 := by linear_combination hjj
    exact mul_left_cancel₀ h2 this
  rw [hx', hy']
  simp only [SpecTSUR.refl, Matrix.smul_vecMulVec, Matrix.vecMulVec_smul, smul_smul]
  rw [mul_comm, hcd, one_smul]

/-- if every `t` is adjacent to `j` then `j` is dead (`x_j = 0` contradicts `y_j·x_j = 2`). -/
theorem twin_empty (h2 : (2 : K) ≠ 0) (k : ℕ) (x y : ℕ → n → K)
    (hg : ∀ i j : Fin k, y i ⬝ᵥ x j = if i = j then 2 else 0)
    (xj yj : n → K) (c : Fin k → K) (hx : xj = ∑ i : Fin k, c i • x i)
    (hjj : yj ⬝ᵥ xj = 2) (hadj : ∀ t : Fin k, y t ⬝ᵥ xj = 0) : False := by
  have hc : ∀ t, c t = 0 := by
    intro t
    have := twin_coeff h2 k x y hg c xj hx t
    rw [hadj t] at this
    exact (mul_eq_zero.1 this.symm).resolve_left h2
  have : xj = 0 := by rw [hx]; simp [hc]
  rw [this, dotProduct_zero] at hjj
  exact h2 (by linear_combination -hjj)

end Twin

section TwinModel
variable [DecidableEq K]
variable {τ α ι : Type*} [Fintype τ] [Fintype α] [Fintype ι] [DecidableEq τ] [DecidableEq α]

/-- GC/II fact (a): the jobs of one tight character pairwise commute (from Lemma TS). -/
theorem jobs_commute (h2 : (2 : K) ≠ 0) (μ : ι → ZMod 2) (t : τ → ι → ZMod 2) (k : ℕ)
    (x y : ℕ → τ ⊕ α → K) (hprod : pp x y k = SpecTS.Dmod μ t)
    (hcard : (univ.filter fun j : τ => μ ⬝ᵥ t j = 1).card = k) (i j : Fin k) :
    Commute (SpecTS.gJ x y k i) (SpecTS.gJ x y k j) :=
  SpecTS.model_commute h2 μ t k x y hprod hcard i j

/-- the TWIN rule in the model setting: the Gram hypothesis comes from Lemma TS. -/
theorem twin_model (h2 : (2 : K) ≠ 0) (μ : ι → ZMod 2) (t : τ → ι → ZMod 2) (k : ℕ)
    (x y : ℕ → τ ⊕ α → K) (hprod : pp x y k = SpecTS.Dmod μ t)
    (hcard : (univ.filter fun j : τ => μ ⬝ᵥ t j = 1).card = k)
    (xj yj : τ ⊕ α → K) (c d : Fin k → K)
    (hx : xj = ∑ i : Fin k, c i • x i) (hy : yj = ∑ i : Fin k, d i • y i)
    (hjj : yj ⬝ᵥ xj = 2) (t0 : Fin k)
    (hadj : ∀ t : Fin k, t ≠ t0 → y t ⬝ᵥ xj = 0 ∧ yj ⬝ᵥ x t = 0) :
    SpecTSUR.refl xj yj = SpecTSUR.refl (x t0) (y t0) :=
  twin_rule h2 k x y (SpecTS.lemmaTS_model h2 μ t k x y hprod hcard).1 xj yj c d hx hy hjj t0 hadj

end TwinModel

/-! ## §F. The split `J = R'_1 ⋯ R'_h · K` (only the H letters are conjugated) -/
section Split
variable {n : Type*} [Fintype n] [DecidableEq n] [DecidableEq K]

/-- group lemma: the ordered product of the `inr` letters of a word is an involution when the `inr`
letters are involutions that pairwise commute -/
theorem jobsP_commute {G : Type*} [Group G] (b : G) :
    ∀ w : List (G ⊕ G), (∀ j, Sum.inr j ∈ w → b * j = j * b) → b * jobsP w = jobsP w * b
  | [], _ => by simp [jobsP]
  | .inl _ :: w, h => jobsP_commute b w (fun j hj => h j (by simp [hj]))
  | .inr j :: w, h => by
    have h1 := h j (by simp)
    have h2 := jobsP_commute b w (fun j' hj' => h j' (by simp [hj']))
    simp only [jobsP]
    calc b * (j * jobsP w) = (b * j) * jobsP w := by rw [mul_assoc]
      _ = j * (b * jobsP w) := by rw [h1, mul_assoc]
      _ = j * (jobsP w * b) := by rw [h2]
      _ = _ := by rw [mul_assoc]

theorem jobsP_invol {G : Type*} [Group G] :
    ∀ w : List (G ⊕ G), (∀ j, Sum.inr j ∈ w → j * j = 1) →
      (∀ j j', Sum.inr j ∈ w → Sum.inr j' ∈ w → j * j' = j' * j) → jobsP w * jobsP w = 1
  | [], _, _ => by simp [jobsP]
  | .inl _ :: w, h1, h2 =>
    jobsP_invol w (fun j hj => h1 j (by simp [hj])) (fun j j' hj hj' => h2 j j' (by simp [hj]) (by simp [hj']))
  | .inr j :: w, h1, h2 => by
    have ih := jobsP_invol w (fun j hj => h1 j (by simp [hj]))
      (fun j j' hj hj' => h2 j j' (by simp [hj]) (by simp [hj']))
    have hc := jobsP_commute j w (fun j' hj' => h2 j j' (by simp) (by simp [hj']))
    simp only [jobsP]
    calc j * jobsP w * (j * jobsP w) = j * (jobsP w * j) * jobsP w := by simp only [mul_assoc]
      _ = j * (j * jobsP w) * jobsP w := by rw [← hc]
      _ = (j * j) * (jobsP w * jobsP w) := by simp only [mul_assoc]
      _ = 1 := by rw [h1 j (by simp), ih, mul_one]

/-- conjugates of reflections (pairing `c`) stay reflections with the same pairing -/
theorem uconj_forms_c (c : K) : ∀ (w : List ((Matrix n n K)ˣ ⊕ (Matrix n n K)ˣ)) (pre : (Matrix n n K)ˣ),
    (∀ t, Sum.inl t ∈ w → ∃ a b : n → K, b ⬝ᵥ a = c ∧ (t : Matrix n n K) = SpecTSUR.refl a b) →
    ∀ g ∈ uconj w pre, ∃ a b : n → K, b ⬝ᵥ a = c ∧ (g : Matrix n n K) = SpecTSUR.refl a b
  | [], _, _ => by simp [uconj]
  | .inl t :: w, pre, h => by
    intro g hg
    simp only [uconj, List.mem_cons] at hg
    rcases hg with rfl | hg
    · obtain ⟨a, b, hab, ht⟩ := h t (by simp)
      exact conj_form_c pre t c a b hab ht
    · exact uconj_forms_c c w pre (fun t ht => h t (by simp [ht])) g hg
  | .inr j :: w, pre, h => uconj_forms_c c w (pre * j) (fun t ht => h t (by simp [ht]))

/-- **Split.**  A word of job letters in which the `inl` letters are the `h` odd-man reflections
(`y·x = 2`) and the `inr` letters are the commuting involutions `K`.  Its ordered product is
`J = R · K` with `R = R'_1 ⋯ R'_h` (the conjugated reflections), `rank(1 - R) ≤ h`, and `K` an
involution; for `h = 1`, `R = 1 - x yᵀ` with `y·x = 2`. -/
theorem split_word
    (w : List ((Matrix n n K)ˣ ⊕ (Matrix n n K)ˣ))
    (hH : ∀ t, Sum.inl t ∈ w → ∃ a b : n → K, b ⬝ᵥ a = 2 ∧ (t : Matrix n n K) = SpecTSUR.refl a b)
    (hK1 : ∀ j, Sum.inr j ∈ w → j * j = 1)
    (hK2 : ∀ j j', Sum.inr j ∈ w → Sum.inr j' ∈ w → j * j' = j' * j) :
    ∃ R : Matrix n n K,
      ((ev w : (Matrix n n K)ˣ) : Matrix n n K) = R * ((jobsP w : (Matrix n n K)ˣ) : Matrix n n K) ∧
      (R - 1).rank ≤ ucount w ∧ jobsP w * jobsP w = 1 ∧
      (ucount w = 1 → ∃ x y : n → K, y ⬝ᵥ x = 2 ∧ R = SpecTSUR.refl x y) := by
  have h1 := ev_move w 1
  simp only [one_mul] at h1
  have hforms := uconj_forms_c 2 w 1 hH
  refine ⟨(((uconj w 1).prod : (Matrix n n K)ˣ) : Matrix n n K), ?_, ?_, jobsP_invol w hK1 hK2, ?_⟩
  · rw [h1]; simp
  · have := SpecTSUR.rank_prod_sub_one_le (uconj w 1) (fun g hg => by
      obtain ⟨a, b, -, hab⟩ := hforms g hg
      rw [hab]; exact refl_sub_one_rank a b)
    rwa [length_uconj] at this
  · intro hu
    have hlen := length_uconj w 1
    rw [hu] at hlen
    obtain ⟨g, hg⟩ := List.length_eq_one_iff.1 hlen
    obtain ⟨a, b, hab, hgm⟩ := hforms g (by rw [hg]; simp)
    refine ⟨a, b, hab, ?_⟩
    rw [hg]; simpa using hgm

end Split

/-! ## §G. GC/II for words -/
section GCWord
variable {n : Type*} [Fintype n] [DecidableEq n] [DecidableEq K]

theorem prod_invol_of_comm (D K' : Matrix n n K) (hD : D * D = 1) (hK : K' * K' = 1)
    (hc : D * K' = K' * D) : (D * K') * (D * K') = 1 := by
  calc D * K' * (D * K') = D * (K' * D) * K' := by simp only [Matrix.mul_assoc]
    _ = D * (D * K') * K' := by rw [hc]
    _ = (D * D) * (K' * K') := by simp only [Matrix.mul_assoc]
    _ = 1 := by rw [hD, hK, Matrix.mul_one]

/-- **GC/II, h = 0, for words.** `J = K` (a commuting involution), `D = ev w`.  Whenever
`U = ucount w ≥ 1` and `|r - b| ≥ U` (`r = rank(1 - D)`, `b = rank(1 - K)`) the character is dead. -/
theorem gc_dead_h0 (h2 : (2 : K) ≠ 0)
    (w : List ((Matrix n n K)ˣ ⊕ (Matrix n n K)ˣ))
    (hform : ∀ t, Sum.inl t ∈ w → ∃ a b : n → K, b ⬝ᵥ a = 0 ∧ (t : Matrix n n K) = SpecTSUR.refl a b)
    (K' : Matrix n n K) (hK : K' * K' = 1) (hJ : ((jobsP w : (Matrix n n K)ˣ) : Matrix n n K) = K')
    (hD : ((ev w : (Matrix n n K)ˣ) : Matrix n n K) * ((ev w : (Matrix n n K)ˣ) : Matrix n n K) = 1)
    (hU : 0 < ucount w)
    (hgap : ucount w ≤ ((1 - ((ev w : (Matrix n n K)ˣ) : Matrix n n K)).rank - (1 - K').rank) +
      ((1 - K').rank - (1 - ((ev w : (Matrix n n K)ˣ) : Matrix n n K)).rank)) : False := by
  obtain ⟨hup, hinv⟩ := word_up_inv h2 w hform
  have hJi : (((jobsP w)⁻¹ : (Matrix n n K)ˣ) : Matrix n n K) = K' := by
    simpa using inv_of_RK (jobsP w) 1 K' (by simp) hK (by rw [hJ]; simp)
  rw [hJ] at hup hinv
  rw [hJi] at hinv
  refine gc_h0 h2 _ K' (ucount w) hU hD hK hup (fun hc => hinv ?_) hgap
  exact prod_invol_of_comm _ K' hD hK hc

/-- **GC/II, h = 1, for words.** `J = R K` with `R = 1 - x yᵀ`, `y·x = 2` (the single odd-man
reflection, conjugated) and `K` an involution. `U ≥ 1` and `gap ≥ U + 1` is dead. -/
theorem gc_dead_h1 (h2 : (2 : K) ≠ 0)
    (w : List ((Matrix n n K)ˣ ⊕ (Matrix n n K)ˣ))
    (hform : ∀ t, Sum.inl t ∈ w → ∃ a b : n → K, b ⬝ᵥ a = 0 ∧ (t : Matrix n n K) = SpecTSUR.refl a b)
    (K' : Matrix n n K) (x y : n → K) (hxy : y ⬝ᵥ x = 2) (hK : K' * K' = 1)
    (hJ : ((jobsP w : (Matrix n n K)ˣ) : Matrix n n K) = SpecTSUR.refl x y * K')
    (hD : ((ev w : (Matrix n n K)ˣ) : Matrix n n K) * ((ev w : (Matrix n n K)ˣ) : Matrix n n K) = 1)
    (hU : 0 < ucount w)
    (hgap : ucount w + 1 ≤ ((1 - ((ev w : (Matrix n n K)ˣ) : Matrix n n K)).rank - (1 - K').rank) +
      ((1 - K').rank - (1 - ((ev w : (Matrix n n K)ˣ) : Matrix n n K)).rank)) : False := by
  obtain ⟨hup, hinv⟩ := word_up_inv h2 w hform
  have hR2 : SpecTSUR.refl x y * SpecTSUR.refl x y = 1 := SpecTS.refl_sq x y hxy
  have hJi : (((jobsP w)⁻¹ : (Matrix n n K)ˣ) : Matrix n n K) = K' * SpecTSUR.refl x y :=
    inv_of_RK (jobsP w) _ K' hR2 hK hJ
  rw [hJi] at hinv
  exact gc_h1 h2 _ K' x y _ (ucount w) hU hD hK hxy hJ hup
    (by simpa only [Matrix.mul_assoc] using hinv) hgap

/-- **GC/II, strict, for words.** `J = R K`, `rank(1 - R) ≤ h`: `U + h < gap` is dead. -/
theorem gc_dead_strict (h2 : (2 : K) ≠ 0)
    (w : List ((Matrix n n K)ˣ ⊕ (Matrix n n K)ˣ))
    (hform : ∀ t, Sum.inl t ∈ w → ∃ a b : n → K, b ⬝ᵥ a = 0 ∧ (t : Matrix n n K) = SpecTSUR.refl a b)
    (K' R : Matrix n n K) (h : ℕ) (hR : (1 - R).rank ≤ h)
    (hJ : ((jobsP w : (Matrix n n K)ˣ) : Matrix n n K) = R * K')
    (hgap : ucount w + h < ((1 - ((ev w : (Matrix n n K)ˣ) : Matrix n n K)).rank - (1 - K').rank) +
      ((1 - K').rank - (1 - ((ev w : (Matrix n n K)ˣ) : Matrix n n K)).rank)) : False :=
  gc_strict _ K' R _ h (ucount w) hJ hR (word_up_inv h2 w hform).1 hgap

end GCWord

/-! ## §H. L1 (R71): at `U = 1` every `M_μ = D J` is a transvection (unipotent, `rank(M - I) ≤ 1`) -/
section L1
variable {n : Type*} [Fintype n] [DecidableEq n] [DecidableEq K]

/-- **L1.** One unit letter (`ucount w = 1`, a transvection `1 - a bᵀ`, `b·a = 0`), `J = jobsP w` an
involution (`J² = I`), `M = D J` with `D = ev w`.  Then `M` is itself a transvection:
`(M - I)² = 0` (so `M` is unipotent), `rank(M - I) ≤ 1`, `tr M = n`, `det M = 1`. -/
theorem L1 (w : List ((Matrix n n K)ˣ ⊕ (Matrix n n K)ˣ))
    (hform : ∀ t, Sum.inl t ∈ w → ∃ a b : n → K, b ⬝ᵥ a = 0 ∧ (t : Matrix n n K) = SpecTSUR.refl a b)
    (hU : ucount w = 1) (hJ2 : jobsP w * jobsP w = 1) :
    (((ev w : (Matrix n n K)ˣ) : Matrix n n K) * ((jobsP w : (Matrix n n K)ˣ) : Matrix n n K) - 1) *
        (((ev w : (Matrix n n K)ˣ) : Matrix n n K) * ((jobsP w : (Matrix n n K)ˣ) : Matrix n n K) - 1) = 0 ∧
      (((ev w : (Matrix n n K)ˣ) : Matrix n n K) * ((jobsP w : (Matrix n n K)ˣ) : Matrix n n K) - 1).rank ≤ 1 ∧
      IsNilpotent (((ev w : (Matrix n n K)ˣ) : Matrix n n K) * ((jobsP w : (Matrix n n K)ˣ) : Matrix n n K) - 1) ∧
      (((ev w : (Matrix n n K)ˣ) : Matrix n n K) * ((jobsP w : (Matrix n n K)ˣ) : Matrix n n K)).trace =
        (Fintype.card n : K) ∧
      (((ev w : (Matrix n n K)ˣ) : Matrix n n K) * ((jobsP w : (Matrix n n K)ˣ) : Matrix n n K)).det = 1 := by
  have h1 := ev_move w 1
  simp only [one_mul] at h1
  have hlen := length_uconj w 1
  rw [hU] at hlen
  obtain ⟨g, hg⟩ := List.length_eq_one_iff.1 hlen
  obtain ⟨a, b, hab, hgm⟩ := SpecINV.uconj_forms w 1 hform g (by rw [hg]; simp)
  have hJJ : ((jobsP w : (Matrix n n K)ˣ) : Matrix n n K) * ((jobsP w : (Matrix n n K)ˣ) : Matrix n n K) = 1 := by
    rw [← Units.val_mul, hJ2]; rfl
  have hM : ((ev w : (Matrix n n K)ˣ) : Matrix n n K) * ((jobsP w : (Matrix n n K)ˣ) : Matrix n n K) =
      SpecTSUR.refl a b := by
    rw [h1, hg, ← hgm]
    simp only [List.prod_cons, List.prod_nil, mul_one, Units.val_mul]
    rw [Matrix.mul_assoc, hJJ, Matrix.mul_one]
  have hsub : SpecTSUR.refl a b - 1 = -vecMulVec a b := by simp [SpecTSUR.refl]
  have hsq : (SpecTSUR.refl a b - 1) * (SpecTSUR.refl a b - 1) = 0 := by
    rw [hsub, Matrix.neg_mul, Matrix.mul_neg, neg_neg, Matrix.vecMulVec_mul_vecMulVec, hab]
    simp
  rw [hM]
  refine ⟨hsq, refl_sub_one_rank a b, ⟨2, by rw [pow_two]; exact hsq⟩, ?_, ?_⟩
  · rw [SpecTSUR.refl, Matrix.trace_sub, Matrix.trace_one, Matrix.trace_vecMulVec, dotProduct_comm, hab]
    simp
  · rw [SpecINV.det_refl, hab]; simp

end L1

/-! ## §I. SPLIT-EQ (R68, with AUDIT68's fix `dim K = m - 1`) -/
section SplitEq
variable {n : Type*} [Fintype n] [DecidableEq n] [DecidableEq K]

theorem rank_le_one_exists (M : Matrix n n K) (h : M.rank ≤ 1) : ∃ u v : n → K, M = vecMulVec u v := by
  have h1 : finrank K (LinearMap.range M.mulVecLin) ≤ 1 := h
  obtain ⟨u, hu⟩ := finrank_le_one_iff.1 h1
  have hc : ∀ j : n, ∃ c : K, c • u.1 = M *ᵥ Pi.single j 1 := by
    intro j
    obtain ⟨c, hc⟩ := hu ⟨M *ᵥ Pi.single j 1, ⟨Pi.single j 1, rfl⟩⟩
    exact ⟨c, congrArg Subtype.val hc⟩
  choose v hv using hc
  refine ⟨u.1, v, ?_⟩
  ext i j
  have := congrFun (hv j) i
  simp only [Pi.smul_apply, smul_eq_mul, Matrix.mulVec_single_one] at this
  rw [vecMulVec_apply, mul_comm, this]; rfl

theorem rank_zero_eq_zero (M : Matrix n n K) (h : M.rank = 0) : M = 0 := by
  apply eq_of_mulVec_eq
  intro v
  have h0 : finrank K (LinearMap.range M.mulVecLin) = 0 := h
  rw [Submodule.finrank_eq_zero] at h0
  have : M *ᵥ v ∈ LinearMap.range M.mulVecLin := ⟨v, rfl⟩
  rw [h0] at this
  simpa using this

/-- **SPLIT-EQ core.**  `ε = ±1`, `det J_K = ±1`, `dim K = card n`, and
`rank(ε - J_K)` at (or below) the determinant bit `[det J_K ≠ ε^{dim K}]` ⇒ `J_K² = I`.
(The paper's "`det J_K = -ε^(m-1)`" is this with `dim K = m - 1`.) -/
theorem split_eq_invol (h2 : (2 : K) ≠ 0) (JK : Matrix n n K) (ε : K) (hε : ε = 1 ∨ ε = -1)
    (hdet : JK.det = 1 ∨ JK.det = -1)
    (hr : (ε • 1 - JK).rank ≤ if JK.det = ε ^ Fintype.card n then 0 else 1) : JK * JK = 1 := by
  have hε0 : ε ≠ 0 := by rcases hε with rfl | rfl <;> simp
  have hεε : ε * ε = 1 := by rcases hε with rfl | rfl <;> simp
  have hpow : ε ^ Fintype.card n = 1 ∨ ε ^ Fintype.card n = -1 := by
    rcases hε with rfl | rfl
    · simp
    · rcases neg_one_pow_eq_or K (Fintype.card n) with h | h <;> simp [h]
  have hne : (1 : K) ≠ -1 := by intro h; apply h2; linear_combination h
  by_cases hd : JK.det = ε ^ Fintype.card n
  · rw [if_pos hd] at hr
    have h0 := rank_zero_eq_zero _ (Nat.le_zero.1 hr)
    have : JK = ε • 1 := (sub_eq_zero.1 h0).symm
    rw [this, smul_mul_smul_comm, Matrix.one_mul, hεε, one_smul]
  · rw [if_neg hd] at hr
    obtain ⟨u, v, hM⟩ := rank_le_one_exists _ hr
    have h1 : JK = ε • 1 - vecMulVec u v := by rw [← hM]; abel
    have hdn : JK.det = -ε ^ Fintype.card n := by
      rcases hdet with h | h <;> rcases hpow with h' | h' <;> simp_all
    have hJ : JK = ε • (1 + replicateCol Unit ((-ε⁻¹) • u) * replicateRow Unit v) := by
      rw [← vecMulVec_eq Unit, h1]
      ext i j
      by_cases hij : i = j
      · subst hij
        simp only [Matrix.sub_apply, Matrix.smul_apply, Matrix.one_apply_eq, vecMulVec_apply,
          Pi.smul_apply, smul_eq_mul, Matrix.add_apply, Pi.neg_apply]
        field_simp
        ring
      · simp only [Matrix.sub_apply, Matrix.smul_apply, Matrix.one_apply_ne hij, vecMulVec_apply,
          Pi.smul_apply, smul_eq_mul, Matrix.add_apply, Pi.neg_apply]
        field_simp
        ring
    have hdet2 : JK.det = ε ^ Fintype.card n * (1 + (-ε⁻¹) * (v ⬝ᵥ u)) := by
      rw [hJ, Matrix.det_smul, det_one_add_replicateCol_mul_replicateRow, dotProduct_smul]
      simp only [smul_eq_mul]
    have hpn : ε ^ Fintype.card n ≠ 0 := pow_ne_zero _ hε0
    have hvu : v ⬝ᵥ u = 2 * ε := by
      have : ε ^ Fintype.card n * (1 + (-ε⁻¹) * (v ⬝ᵥ u)) = -ε ^ Fintype.card n := by
        rw [← hdet2, hdn]
      have h3 : (1 + (-ε⁻¹) * (v ⬝ᵥ u)) = -1 := by
        apply mul_left_cancel₀ hpn; rw [this]; ring
      field_simp at h3
      linear_combination -h3
    rw [h1]
    have e : (ε • 1 - vecMulVec u v) * (ε • 1 - vecMulVec u v) =
        (ε * ε) • (1 : Matrix n n K) - (2 * ε) • vecMulVec u v +
          (vecMulVec u v * vecMulVec u v) := by
      simp only [sub_mul, mul_sub, smul_mul_smul_comm, Matrix.one_mul, Matrix.mul_one,
        Matrix.smul_mul, Matrix.mul_smul]
      module
    rw [e, Matrix.vecMulVec_mul_vecMulVec, hvu, hεε, one_smul, Matrix.vecMulVec_smul]
    simp

end SplitEq

section SplitEqBlocks
variable {κ ω : Type*} [Fintype κ] [DecidableEq κ] [Fintype ω] [DecidableEq ω] [DecidableEq K]

/-- block form: `D - J = diag((ε - σ), ε - J_K, D_w - 1)`. -/
theorem DJ_blocks (ε σ : K) (JK : Matrix κ κ K) (Dw : Matrix ω ω K) :
    (fromBlocks (ε • (1 : Matrix (Unit ⊕ κ) (Unit ⊕ κ) K)) 0 0 Dw) -
        fromBlocks (fromBlocks (σ • (1 : Matrix Unit Unit K)) 0 0 JK) 0 0 1 =
      fromBlocks (fromBlocks ((ε - σ) • (1 : Matrix Unit Unit K)) 0 0 (ε • 1 - JK)) 0 0 (Dw - 1) := by
  ext i j
  rcases i with (i | i) | i <;> rcases j with (j | j) | j <;>
    simp [Matrix.one_apply, sub_smul] <;> (try split_ifs) <;> simp_all

theorem rank_unit_scalar (c : K) : ((c • (1 : Matrix Unit Unit K))).rank = if c ≠ 0 then 1 else 0 := by
  have : (c • (1 : Matrix Unit Unit K)) = diagonal fun _ => c := by
    ext i j; simp [Matrix.one_apply, diagonal_apply]
  rw [this, rank_diagonal]
  by_cases hc : c = 0 <;> simp [hc]

/-- **SPLIT-EQ for words, general block form.** Coordinates `((Unit ⊕ κ) ⊕ ω)`: `V₁ = ⟨x_H⟩ ⊕ K`
(hub, then `K = ker y_H|V₁`) and the dark part `ω`.  `D = ε` on `V₁`, `D_w` (an involution) on `ω`;
`J = σ ⊕ J_K ⊕ I`.  With `d = rank(D_w - 1)`, the SPLIT bound is
`d + [ε ≠ σ] + [det J_K ≠ ε^{dim K}] ≤ U`, and EQUALITY IS DEAD (equality ⇒ `rank(ε - J_K)` pinned at
the det bit ⇒ `J_K` involution ⇒ `g = D J` involution ⇒ INV gives `rank(D - J) ≤ U - 1`). -/
theorem split_eq_dead (h2 : (2 : K) ≠ 0)
    (w : List ((Matrix ((Unit ⊕ κ) ⊕ ω) ((Unit ⊕ κ) ⊕ ω) K)ˣ ⊕ (Matrix ((Unit ⊕ κ) ⊕ ω) ((Unit ⊕ κ) ⊕ ω) K)ˣ))
    (hform : ∀ t, Sum.inl t ∈ w → ∃ a b : (Unit ⊕ κ) ⊕ ω → K, b ⬝ᵥ a = 0 ∧
      (t : Matrix ((Unit ⊕ κ) ⊕ ω) ((Unit ⊕ κ) ⊕ ω) K) = SpecTSUR.refl a b)
    (ε σ : K) (hε : ε = 1 ∨ ε = -1) (hσ : σ = 1 ∨ σ = -1)
    (JK : Matrix κ κ K) (hdetJ : JK.det = 1 ∨ JK.det = -1)
    (Dw : Matrix ω ω K) (hDw : Dw * Dw = 1)
    (hD : ((ev w : (Matrix ((Unit ⊕ κ) ⊕ ω) ((Unit ⊕ κ) ⊕ ω) K)ˣ) : Matrix ((Unit ⊕ κ) ⊕ ω) ((Unit ⊕ κ) ⊕ ω) K) =
      fromBlocks (ε • (1 : Matrix (Unit ⊕ κ) (Unit ⊕ κ) K)) 0 0 Dw)
    (hJ : ((jobsP w : (Matrix ((Unit ⊕ κ) ⊕ ω) ((Unit ⊕ κ) ⊕ ω) K)ˣ) : Matrix ((Unit ⊕ κ) ⊕ ω) ((Unit ⊕ κ) ⊕ ω) K) =
      fromBlocks (fromBlocks (σ • (1 : Matrix Unit Unit K)) 0 0 JK) 0 0 1)
    (hU : 0 < ucount w) :
    (Dw - 1).rank + (if ε ≠ σ then 1 else 0) + (if JK.det ≠ ε ^ Fintype.card κ then 1 else 0) < ucount w := by
  obtain ⟨hup, hinv⟩ := word_up_inv h2 w hform
  have hεε : ε * ε = 1 := by rcases hε with rfl | rfl <;> simp
  have hσσ : σ * σ = 1 := by rcases hσ with rfl | rfl <;> simp
  set D := ((ev w : (Matrix ((Unit ⊕ κ) ⊕ ω) ((Unit ⊕ κ) ⊕ ω) K)ˣ) : Matrix ((Unit ⊕ κ) ⊕ ω) ((Unit ⊕ κ) ⊕ ω) K) with hDdef
  set J := ((jobsP w : (Matrix ((Unit ⊕ κ) ⊕ ω) ((Unit ⊕ κ) ⊕ ω) K)ˣ) : Matrix ((Unit ⊕ κ) ⊕ ω) ((Unit ⊕ κ) ⊕ ω) K) with hJdef
  have hrank : (D - J).rank = (Dw - 1).rank + (ε • 1 - JK).rank + ((ε - σ) • (1 : Matrix Unit Unit K)).rank := by
    rw [hD, hJ, DJ_blocks, PadLift.rank_blockdiag, PadLift.rank_blockdiag]; ring
  rw [rank_unit_scalar (ε - σ)] at hrank
  have hbit : (if JK.det ≠ ε ^ Fintype.card κ then 1 else 0) ≤ (ε • 1 - JK).rank := by
    by_cases hd : JK.det = ε ^ Fintype.card κ
    · simp [hd]
    · simp only [ne_eq, hd, not_false_eq_true, if_true]
      by_contra hlt
      have h0 := rank_zero_eq_zero (ε • 1 - JK) (by omega)
      have : JK = ε • 1 := (sub_eq_zero.1 h0).symm
      apply hd; rw [this, Matrix.det_smul, Matrix.det_one]; simp
  have hεσ : (if ε - σ ≠ 0 then 1 else 0) = (if ε ≠ σ then 1 else 0) := by
    by_cases h : ε = σ <;> simp [h, sub_eq_zero]
  rw [hεσ] at hrank
  by_contra hcon
  push Not at hcon
  -- equality: rank(D - J) = U = bound
  have hrK : (ε • 1 - JK).rank ≤ (if JK.det ≠ ε ^ Fintype.card κ then 1 else 0) := by omega
  have hK' : (ε • 1 - JK).rank ≤ if JK.det = ε ^ Fintype.card κ then 0 else 1 := by
    by_cases hd : JK.det = ε ^ Fintype.card κ
    · simpa [hd] using hrK
    · simpa [hd] using hrK
  have hJK2 := split_eq_invol h2 JK ε hε hdetJ hK'
  have hJ2 : J * J = 1 := by
    have hs : (σ • (1 : Matrix Unit Unit K)) * (σ • (1 : Matrix Unit Unit K)) = 1 := by
      rw [smul_mul_smul_comm, Matrix.one_mul, hσσ, one_smul]
    rw [hJ]
    simp only [Matrix.fromBlocks_multiply, Matrix.zero_mul, Matrix.mul_zero, add_zero, zero_add,
      Matrix.mul_one, hJK2, hs, Matrix.fromBlocks_one]
  have hD2 : D * D = 1 := by
    rw [hD]
    simp only [Matrix.fromBlocks_multiply, Matrix.zero_mul, Matrix.mul_zero, add_zero, zero_add, hDw]
    have : (ε • (1 : Matrix (Unit ⊕ κ) (Unit ⊕ κ) K)) * (ε • 1) = 1 := by
      rw [smul_mul_smul_comm, Matrix.one_mul, hεε, one_smul]
    rw [this, Matrix.fromBlocks_one]
  have hc : D * J = J * D := by
    rw [hD, hJ]
    simp only [Matrix.fromBlocks_multiply, Matrix.zero_mul, Matrix.mul_zero, add_zero, zero_add,
      Matrix.mul_one, Matrix.one_mul]
    congr 1
    rw [Matrix.smul_mul, Matrix.mul_smul, Matrix.one_mul, Matrix.mul_one]
  have hJi : ((((jobsP w)⁻¹ : (Matrix ((Unit ⊕ κ) ⊕ ω) ((Unit ⊕ κ) ⊕ ω) K)ˣ)) : Matrix ((Unit ⊕ κ) ⊕ ω) ((Unit ⊕ κ) ⊕ ω) K) = J := by
    simpa using inv_of_RK (jobsP w) 1 J (by simp) hJ2 (by simp [hJdef])
  rw [hJi] at hinv
  have := hinv (prod_invol_of_comm D J hD2 hJ2 hc)
  omega

end SplitEqBlocks

/-! ## Non-vacuity: `K_data` on the SpecTS example (one reflection, `y·x = 2`) -/
example : pp SpecTS.ex_x SpecTS.ex_y 1 * pp SpecTS.ex_x SpecTS.ex_y 1 = 1 ∧
    (1 - pp SpecTS.ex_x SpecTS.ex_y 1).rank = 1 :=
  K_data (K := ℚ) (by norm_num) 1 SpecTS.ex_x SpecTS.ex_y (by
    intro i j
    have hi : i = 0 := Subsingleton.elim _ _
    have hj : j = 0 := Subsingleton.elim _ _
    subst hi; subst hj
    simp [SpecTS.ex_x, SpecTS.ex_y, dotProduct, Fintype.sum_sum_type])

end SpecGC

open SpecGC in
#print axioms twin_rule
open SpecGC in
#print axioms twin_model
open SpecGC in
#print axioms jobs_commute
open SpecGC in
#print axioms K_data
open SpecGC in
#print axioms gc_strict
open SpecGC in
#print axioms gc_h0
open SpecGC in
#print axioms gc_h1
open SpecGC in
#print axioms split_word
open SpecGC in
#print axioms gc_dead_h0
open SpecGC in
#print axioms gc_dead_h1
open SpecGC in
#print axioms gc_dead_strict
open SpecGC in
#print axioms split_eq_invol
open SpecGC in
#print axioms split_eq_dead
open SpecGC in
#print axioms L1
