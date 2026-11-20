import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.Data.Fintype.Perm
/-!
LINCB (lane LEANCB).  CAUCHY-BINET, existence form (any commutative field):
if `Aᵀ * P` (n x n) is invertible, where A P : m x n, then there is an injective `f : Fin n → ι`
(an n-subset of the rows) with `A_f` and `P_f` BOTH invertible.
Proof: det(AᵀP) = Σ_f (∏ P(f i,i)) det A_f; non-injective f vanish; injective f are grouped by image,
each fibre is an orbit f0∘τ and sums to det A_f0 * det P_f0.
-/
open Matrix Finset Equiv

namespace LinCB
variable {F : Type*} [Field F] {ι : Type*} [Fintype ι] [DecidableEq ι] {n : ℕ}

lemma det_expand (A P : Matrix ι (Fin n) F) :
    (Aᵀ * P).det = ∑ f : Fin n → ι, (∏ i, P (f i) i) * (A.submatrix f id).det := by
  rw [det_apply']
  have h1 : ∀ σ : Perm (Fin n), ((Perm.sign σ : ℤˣ) : F) * ∏ i, (Aᵀ * P) (σ i) i =
      ∑ f : Fin n → ι, (∏ i, P (f i) i) * (((Perm.sign σ : ℤˣ) : F) * ∏ i, A (f i) (σ i)) := by
    intro σ
    simp only [Matrix.mul_apply, Matrix.transpose_apply]
    rw [Finset.prod_univ_sum, Finset.mul_sum]
    refine Finset.sum_congr (by simp [Fintype.piFinset_univ]) fun f _ => ?_
    rw [Finset.prod_mul_distrib]
    ring
  rw [Finset.sum_congr rfl fun σ _ => h1 σ, Finset.sum_comm]
  refine Finset.sum_congr rfl fun f _ => ?_
  rw [← Finset.mul_sum, ← det_transpose, det_apply']
  simp [Matrix.transpose_apply]

lemma det_noninj (A : Matrix ι (Fin n) F) (f : Fin n → ι) (hf : ¬ Function.Injective f) :
    (A.submatrix f id).det = 0 := by
  simp only [Function.Injective, not_forall] at hf
  obtain ⟨i, j, hij, hne⟩ := hf
  exact det_zero_of_row_eq hne (by ext k; simp [hij])

lemma fibre_sum (A P : Matrix ι (Fin n) F) (f0 : Fin n → ι) (h0 : Function.Injective f0) :
    ∑ f ∈ (Finset.univ.filter fun f : Fin n → ι => Function.Injective f ∧ Finset.univ.image f = Finset.univ.image f0),
      (∏ i, P (f i) i) * (A.submatrix f id).det =
    (A.submatrix f0 id).det * (P.submatrix f0 id).det := by
  have hset : (Finset.univ.filter fun f : Fin n → ι => Function.Injective f ∧
      Finset.univ.image f = Finset.univ.image f0) =
      Finset.univ.image (fun τ : Perm (Fin n) => f0 ∘ τ) := by
    ext f
    simp only [Finset.mem_filter, Finset.mem_univ, true_and, Finset.mem_image]
    constructor
    · rintro ⟨hf, himg⟩
      have hmem : ∀ i, ∃ j, f0 j = f i := by
        intro i
        have : f i ∈ Finset.univ.image f := Finset.mem_image_of_mem _ (Finset.mem_univ i)
        rw [himg] at this
        simpa using this
      choose g hg using hmem
      have ginj : Function.Injective g := by
        intro a b hab
        apply hf
        rw [← hg a, ← hg b, hab]
      refine ⟨Equiv.ofBijective g (Finite.injective_iff_bijective.1 ginj), ?_⟩
      ext i
      simp [hg]
    · rintro ⟨τ, rfl⟩
      refine ⟨h0.comp τ.injective, ?_⟩
      ext x
      simp only [Finset.mem_image, Finset.mem_univ, true_and, Function.comp_apply]
      constructor
      · rintro ⟨i, rfl⟩; exact ⟨τ i, rfl⟩
      · rintro ⟨i, rfl⟩; exact ⟨τ.symm i, by simp⟩
  have hinj : Function.Injective (fun τ : Perm (Fin n) => f0 ∘ τ) := by
    intro a b hab
    exact Equiv.ext fun i => h0 (congrFun hab i)
  rw [hset, Finset.sum_image (fun a _ b _ hab => hinj hab)]
  have : ∀ τ : Perm (Fin n), (∏ i, P ((f0 ∘ τ) i) i) * (A.submatrix (f0 ∘ τ) id).det =
      (A.submatrix f0 id).det * (((Perm.sign τ : ℤˣ) : F) * ∏ i, (P.submatrix f0 id) (τ i) i) := by
    intro τ
    have e : A.submatrix (f0 ∘ τ) id = (A.submatrix f0 id).submatrix τ id := rfl
    rw [e, det_permute]
    simp only [Function.comp_apply, Matrix.submatrix_apply, id]
    ring
  rw [Finset.sum_congr rfl fun τ _ => this τ, ← Finset.mul_sum, ← det_apply']

/-- Cauchy–Binet, existence form. -/
theorem cb_exists (A P : Matrix ι (Fin n) F) (h : (Aᵀ * P).det ≠ 0) :
    ∃ f : Fin n → ι, Function.Injective f ∧ (A.submatrix f id).det ≠ 0 ∧ (P.submatrix f id).det ≠ 0 := by
  by_contra hcon
  push Not at hcon
  apply h
  rw [det_expand]
  have hz : ∀ f : Fin n → ι, Function.Injective f → (A.submatrix f id).det * (P.submatrix f id).det = 0 := by
    intro f hf
    by_cases ha : (A.submatrix f id).det = 0
    · simp [ha]
    · simp [hcon f hf ha]
  have hnon : ∑ f ∈ (Finset.univ.filter fun f : Fin n → ι => ¬ Function.Injective f),
      (∏ i, P (f i) i) * (A.submatrix f id).det = 0 :=
    Finset.sum_eq_zero fun f hf => by
      rw [det_noninj A f (by simpa using hf), mul_zero]
  rw [← Finset.sum_filter_add_sum_filter_not Finset.univ (fun f : Fin n → ι => Function.Injective f),
    show (∑ f ∈ Finset.univ.filter fun f : Fin n → ι => ¬ Function.Injective f,
      (∏ i, P (f i) i) * (A.submatrix f id).det) = 0 from hnon, add_zero]
  rw [← Finset.sum_fiberwise_of_maps_to (s := Finset.univ.filter fun f : Fin n → ι => Function.Injective f)
    (t := Finset.univ) (g := fun f => Finset.univ.image f) (fun _ _ => Finset.mem_univ _)]
  refine Finset.sum_eq_zero fun I _ => ?_
  by_cases hex : ∃ f0 : Fin n → ι, Function.Injective f0 ∧ Finset.univ.image f0 = I
  · obtain ⟨f0, h0, rfl⟩ := hex
    have : (Finset.univ.filter fun f : Fin n → ι => Function.Injective f).filter
        (fun f => Finset.univ.image f = Finset.univ.image f0) =
        Finset.univ.filter fun f : Fin n → ι => Function.Injective f ∧
          Finset.univ.image f = Finset.univ.image f0 := by
      rw [Finset.filter_filter]
    rw [this, fibre_sum A P f0 h0, hz f0 h0]
  · apply Finset.sum_eq_zero
    intro f hf
    exfalso
    simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hf
    exact hex ⟨f, hf.1, hf.2⟩

end LinCB

#print axioms LinCB.cb_exists
