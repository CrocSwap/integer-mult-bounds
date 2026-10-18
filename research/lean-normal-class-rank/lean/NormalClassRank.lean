import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.Data.Finset.Max
import Mathlib.Tactic

open scoped BigOperators
open Matrix Module

set_option maxHeartbeats 2000000

namespace NormalClassRank

variable {F I Γ : Type*} [Field F] [Fintype I] [DecidableEq I] [LinearOrder Γ]

/-- A strictly increasing support graph cannot carry a fixed vector. -/
theorem strict_support_kernel (K : Matrix I I F) (w : I → Γ)
    (hK : ∀ i j, K i j ≠ 0 → w i < w j)
    (x : I → F) (hx : (1 - K).mulVec x = 0) : x = 0 := by
  classical
  by_contra h
  have hn : (Finset.univ.filter (fun i => x i ≠ 0)).Nonempty := by
    obtain ⟨j, hj⟩ : ∃ j, x j ≠ 0 := by
      simpa only [funext_iff, Pi.zero_apply, not_forall] using h
    exact ⟨j, Finset.mem_filter.mpr ⟨Finset.mem_univ j, hj⟩⟩
  obtain ⟨i, hi, hm⟩ := Finset.exists_max_image
    (Finset.univ.filter (fun i => x i ≠ 0)) w hn
  have hs : (∑ j, K i j * x j) = 0 := by
    apply Finset.sum_eq_zero
    intro j _
    by_cases hzero : x j = 0
    · simp [hzero]
    have hk : K i j = 0 := by
      by_contra hk
      exact (not_lt_of_ge (hm j (Finset.mem_filter.mpr ⟨Finset.mem_univ j, hzero⟩))) (hK i j hk)
    simp [hk]
  rw [Matrix.sub_mulVec, Matrix.one_mulVec] at hx
  have he : x i - ∑ j, K i j * x j = 0 := by
    simpa only [Pi.sub_apply, Pi.zero_apply, Matrix.mulVec, dotProduct] using congrFun hx i
  exact (Finset.mem_filter.mp hi).2 (by simpa [hs] using he)

theorem strict_support_rank (K : Matrix I I F) (w : I → Γ)
    (hK : ∀ i j, K i j ≠ 0 → w i < w j) :
    (1 - K).rank = Fintype.card I := by
  apply Matrix.rank_of_isUnit
  apply Matrix.mulVec_injective_iff_isUnit.mp
  exact (LinearMap.ker_eq_bot (f := (1-K).mulVecLin)).mp
    ((LinearMap.ker_eq_bot' (f := (1-K).mulVecLin)).mpr
      (fun x hx => strict_support_kernel K w hK x hx))

/-- Ascending class edges expose an invertible principal submatrix. -/
theorem ascending_count_le_rank (K : Matrix I I F) (α β : I → Γ)
    (hc : ∀ i j, K i j ≠ 0 → β i = α j) :
    Fintype.card {i : I // α i < β i} ≤ (1 - K).rank := by
  classical
  let S := {i : I // α i < β i}
  let f : S → I := Subtype.val
  have hstrict : ∀ i j : S, (K.submatrix f f) i j ≠ 0 → α i < α j := by
    intro i j hij
    exact i.property.trans_le (le_of_eq (hc i j hij))
  have hr := strict_support_rank (K.submatrix f f) (fun i : S => α i) hstrict
  have he : (1-K).submatrix f f = 1 - K.submatrix f f := by
    simp only [Matrix.submatrix_sub, Pi.sub_apply, Matrix.submatrix_one f Subtype.val_injective]
  rw [← he] at hr
  rw [← hr]
  exact Matrix.rank_submatrix_le (1-K) f f

/-- Reversing the support graph gives the other principal rank bound. -/
theorem descending_count_le_rank (K : Matrix I I F) (α β : I → Γ)
    (hc : ∀ i j, K i j ≠ 0 → β i = α j) :
    Fintype.card {i : I // β i < α i} ≤ (1 - K).rank := by
  have ht := ascending_count_le_rank K.transpose β α (fun i j h => (hc j i h).symm)
  have he : (1 - K.transpose) = (1-K).transpose := by
    ext i j
    simp [Matrix.transpose_apply, Matrix.sub_apply, Matrix.one_apply, eq_comm]
  rw [he, Matrix.rank_transpose] at ht
  exact ht

omit [DecidableEq I] in
/-- Distinct endpoints partition terms into the two orientations. -/
theorem class_partition (α β : I → Γ) (hne : ∀ i, α i ≠ β i) :
    Fintype.card {i : I // α i < β i} +
      Fintype.card {i : I // β i < α i} = Fintype.card I := by
  classical
  have hp : ∀ i, (β i < α i) ↔ ¬ (α i < β i) := by
    intro i
    rcases lt_trichotomy (α i) (β i) with h | h | h
    · simp [h, not_lt_of_ge (le_of_lt h)]
    · exact False.elim (hne i h)
    · simp [h, not_lt_of_ge (le_of_lt h)]
  simp_rw [Fintype.card_subtype, hp]
  simpa only [Finset.card_univ] using
    (Finset.card_filter_add_card_filter_not (s := Finset.univ) (fun i : I => α i < β i))

/-- Lemma K: normal-class compatibility forces rank at least half the term count. -/
theorem normal_class_rank (K : Matrix I I F) (α β : I → Γ)
    (hne : ∀ i, α i ≠ β i) (hc : ∀ i j, K i j ≠ 0 → β i = α j) :
    Fintype.card I ≤ 2 * (1-K).rank := by
  have hu := ascending_count_le_rank K α β hc
  have hd := descending_count_le_rank K α β hc
  have hp := class_partition α β hne
  omega

/-- The equivalent half-size kernel statement, including empty matrices. -/
theorem normal_class_half_kernel (K : Matrix I I F) (α β : I → Γ)
    (hne : ∀ i, α i ≠ β i) (hc : ∀ i j, K i j ≠ 0 → β i = α j) :
    2 * finrank F (LinearMap.ker (1-K).mulVecLin) ≤ Fintype.card I := by
  have hr := normal_class_rank K α β hne hc
  have hn : (1-K).rank + finrank F (LinearMap.ker (1-K).mulVecLin) = Fintype.card I := by
    simpa [Matrix.rank] using LinearMap.finrank_range_add_finrank_ker (1-K).mulVecLin
  omega

section Products
variable {V W : Type*} [AddCommGroup V] [Module F V] [AddCommGroup W] [Module F W]

lemma fixed_iff (f : V →ₗ[F] V) (x : V) :
    x ∈ LinearMap.ker (LinearMap.id - f) ↔ f x = x := by
  change x - f x = 0 ↔ f x = x
  rw [sub_eq_zero]
  exact eq_comm

/-- AB and BA have canonically isomorphic fixed spaces, without equal ambient dimensions. -/
noncomputable def product_fixed_equiv (A : W →ₗ[F] V) (C : V →ₗ[F] W) :
    LinearMap.ker (LinearMap.id - A.comp C) ≃ₗ[F]
      LinearMap.ker (LinearMap.id - C.comp A) where
  toFun x := ⟨C x, by
    rw [fixed_iff]
    have hx := (fixed_iff (A.comp C) x).mp x.property
    simpa using congrArg C hx⟩
  invFun y := ⟨A y, by
    rw [fixed_iff]
    have hy := (fixed_iff (C.comp A) y).mp y.property
    simpa using congrArg A hy⟩
  left_inv x := by
    apply Subtype.ext
    exact (fixed_iff (A.comp C) x).mp x.property
  right_inv y := by
    apply Subtype.ext
    exact (fixed_iff (C.comp A) y).mp y.property
  map_add' x y := by apply Subtype.ext; exact C.map_add x y
  map_smul' a x := by apply Subtype.ext; exact C.map_smul a x

end Products

section Matrices
variable {N J : Type*} [Fintype N] [DecidableEq N] [Fintype J] [DecidableEq J]

omit [DecidableEq I] in
lemma product_mulVecLin (A : Matrix N I F) (C : Matrix I N F) :
    (1-A*C).mulVecLin = LinearMap.id - A.mulVecLin.comp C.mulVecLin := by
  apply LinearMap.ext
  intro x
  funext i
  change ((1-A*C).mulVec x) i = (x - A.mulVec (C.mulVec x)) i
  rw [Matrix.sub_mulVec, Matrix.one_mulVec, Matrix.mulVec_mulVec]

/-- Rectangular transfer of the fixed-space dimension, not of the zero eigenspace. -/
theorem product_kernel_finrank (A : Matrix N I F) (C : Matrix I N F) :
    finrank F (LinearMap.ker (1-A*C).mulVecLin) =
      finrank F (LinearMap.ker (1-C*A).mulVecLin) := by
  rw [product_mulVecLin A C, product_mulVecLin C A]
  exact (product_fixed_equiv A.mulVecLin C.mulVecLin).finrank_eq

/-- The normal-class bound applies to any compatible rectangular factorization. -/
theorem product_half_kernel (A : Matrix N I F) (C : Matrix I N F) (α β : I → Γ)
    (hne : ∀ i, α i ≠ β i) (hc : ∀ i j, (C*A) i j ≠ 0 → β i = α j) :
    2 * finrank F (LinearMap.ker (1-A*C).mulVecLin) ≤ Fintype.card I := by
  rw [product_kernel_finrank A C]
  exact normal_class_half_kernel (C*A) α β hne hc

omit [DecidableEq J] in
/-- If the remaining n terms factor the residual, then 2N ≤ 2n+t. -/
theorem completed_count (A : Matrix N I F) (C : Matrix I N F)
    (D : Matrix N J F) (E : Matrix J N F) (α β : I → Γ)
    (hne : ∀ i, α i ≠ β i) (hc : ∀ i j, (C*A) i j ≠ 0 → β i = α j)
    (hcomplete : A*C + D*E = 1) :
    2 * Fintype.card N ≤ 2 * Fintype.card J + Fintype.card I := by
  have hhalf := product_half_kernel A C α β hne hc
  have he : 1-A*C = D*E := by rw [← hcomplete]; abel
  have hr : (1-A*C).rank ≤ Fintype.card J := by
    rw [he]
    exact (Matrix.rank_mul_le_left D E).trans (Matrix.rank_le_card_width D)
  have hn : (1-A*C).rank + finrank F (LinearMap.ker (1-A*C).mulVecLin) = Fintype.card N := by
    have hh := LinearMap.finrank_range_add_finrank_ker (1-A*C).mulVecLin
    rw [Module.finrank_pi F] at hh
    exact hh
  omega

end Matrices

/-- The count bound prices every low and high term, including the surplus. -/
theorem charged_count {N n t : ℕ} (hcount : 2*N ≤ 2*n+t)
    {lo hi : ℝ} (hhi : 0 ≤ hi) :
    (N : ℝ)*hi + (t : ℝ)*(lo-hi/2) ≤ (t : ℝ)*lo + (n : ℝ)*hi := by
  have hc : (2 : ℝ)*N ≤ 2*n+t := by exact_mod_cast hcount
  nlinarith [mul_nonneg (show 0 ≤ 2*(n : ℝ)+(t : ℝ)-2*(N : ℝ) by linarith) hhi]

/-- Exact power-bill consequence; the affine lower bound itself holds for every q. -/
theorem charged_power {N n t : ℕ} (hcount : 2*N ≤ 2*n+t) (q : ℝ) :
    (N : ℝ)*8^q + (t : ℝ)*(7^q-8^q/2) ≤ (t : ℝ)*7^q + (n : ℝ)*8^q :=
  charged_count hcount (le_of_lt (Real.rpow_pos_of_pos (by norm_num) q))

/-- At powers q ≤ 1 the low-rank surplus remains uniformly positive. -/
theorem power_surplus {q : ℝ} (hq : q ≤ 1) :
    (3/8 : ℝ)*8^q ≤ 7^q-8^q/2 := by
  have h := Real.rpow_le_rpow_of_exponent_le (x := (8/7 : ℝ)) (by norm_num) hq
  rw [Real.div_rpow (by norm_num) (by norm_num), Real.rpow_one] at h
  have hseven : (0 : ℝ) < 7^q := Real.rpow_pos_of_pos (by norm_num) q
  have hh := (div_le_iff₀ hseven).mp h
  linarith

/-- Specialization to the 8k-dimensional batch demand at ordinary rank prices. -/
theorem batch_linear_bill {k n t : ℕ} (hcount : 2*(8*k) ≤ 2*n+t) :
    64*k+3*t ≤ 7*t+8*n := by omega

/-- Every low term has a positive surplus for the concave power-pricing domain. -/
theorem batch_power_bill {k n t : ℕ} (hcount : 2*(8*k) ≤ 2*n+t)
    {q : ℝ} (hq : q ≤ 1) :
    (8*(k : ℝ))*8^q + (3/8 : ℝ)*(t : ℝ)*8^q ≤ (t : ℝ)*7^q + (n : ℝ)*8^q := by
  have hp := charged_power hcount q
  have hs := power_surplus hq
  have ht : (0 : ℝ) ≤ t := Nat.cast_nonneg t
  push_cast at hp
  nlinarith [mul_nonneg ht (sub_nonneg.mpr hs)]

end NormalClassRank
