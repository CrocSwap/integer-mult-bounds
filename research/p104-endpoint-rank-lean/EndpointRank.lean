import Mathlib.Data.Matrix.Rank
import Mathlib.Data.Matrix.Block
import Mathlib.Analysis.MeanInequalitiesPow

/-! The rank lower bound of PR2662, for actual block matrices over any field.
No Clifford, phase, geometry, or supplier realization is assumed by these lemmas.
Those are separate premises when applying the result to a physical program. -/

namespace EndpointRank

open Matrix
variable {K n : Type*} [Field K] [Fintype n]

private theorem rank_add_le (A B : Matrix n n K) :
    (A + B).rank ≤ A.rank + B.rank := by
  have h : LinearMap.range (A + B).mulVecLin ≤
      LinearMap.range A.mulVecLin ⊔ LinearMap.range B.mulVecLin := by
    rintro _ ⟨x, rfl⟩
    change (A + B) *ᵥ x ∈ _
    rw [Matrix.add_mulVec]
    exact Submodule.add_mem_sup (LinearMap.mem_range_self _ x)
      (LinearMap.mem_range_self _ x)
  exact (Submodule.finrank_mono h).trans
    (Submodule.finrank_add_le_finrank_add_finrank _ _)

/-- The input-Z to output-X block. -/
def mixing (U : Matrix (n ⊕ n) (n ⊕ n) K) : Matrix n n K := U.toBlocks₁₂

/-- Block multiplication, with no invertibility or symplectic hypothesis. -/
theorem mixing_mul (U V : Matrix (n ⊕ n) (n ⊕ n) K) :
    mixing (U * V) = U.toBlocks₁₁ * mixing V + mixing U * V.toBlocks₂₂ := by
  ext i j
  simp [mixing, Matrix.toBlocks₁₁, Matrix.toBlocks₁₂, Matrix.toBlocks₂₂,
    Matrix.mul_apply, Fintype.sum_sum_type]

/-- Subadditivity is an inequality, not rank additivity. -/
theorem mixing_rank_mul_le (U V : Matrix (n ⊕ n) (n ⊕ n) K) :
    (mixing (U * V)).rank ≤ (mixing U).rank + (mixing V).rank := by
  rw [mixing_mul]
  exact (rank_add_le _ _).trans (by
    have h₁ := Matrix.rank_mul_le_right U.toBlocks₁₁ (mixing V)
    have h₂ := Matrix.rank_mul_le_left (mixing U) V.toBlocks₂₂
    omega)

/-- Any finite decomposition pays at least the mixing rank of its product.
The charge can overestimate each factor's mixing rank; monomials can pay zero. -/
theorem word_rank_le [DecidableEq n] (word : List (Matrix (n ⊕ n) (n ⊕ n) K))
    (charge : Matrix (n ⊕ n) (n ⊕ n) K → ℕ)
    (hcharge : ∀ U ∈ word, (mixing U).rank ≤ charge U) :
    (mixing word.prod).rank ≤ (word.map charge).sum := by
  classical
  induction word with
  | nil =>
    have hz : mixing (1 : Matrix (n ⊕ n) (n ⊕ n) K) = 0 := by
      ext i j
      simp [mixing, Matrix.toBlocks₁₂]
    simp [hz]
  | cons U rest ih =>
    simp only [List.prod_cons, List.map_cons, List.sum_cons]
    exact (mixing_rank_mul_le U rest.prod).trans
      (Nat.add_le_add (hcharge U (by simp))
        (ih (fun V hV => hcharge V (by simp [hV]))))

/-- The analytic step for any finite natural-rank invoice, including empty ones. -/
theorem moment_lower_bound (ranks : List ℕ) (target : ℕ)
    (hbudget : target ≤ ranks.sum) {p : ℝ} (hp : 0 < p) (hp1 : p ≤ 1) :
    (target : ℝ) ^ p ≤ (ranks.map (fun r => (r : ℝ) ^ p)).sum := by
  have hsum : (ranks.sum : ℝ) ^ p ≤
      (ranks.map (fun r => (r : ℝ) ^ p)).sum := by
    clear hbudget
    induction ranks with
    | nil => simp [hp.ne']
    | cons r rest ih =>
      simp only [List.sum_cons, List.map_cons, Nat.cast_add]
      exact (Real.rpow_add_le_add_rpow (by positivity) (by positivity) hp.le hp1).trans
        (add_le_add_left ih _)
  exact (Real.rpow_le_rpow (by positivity) (by exact_mod_cast hbudget) hp.le).trans hsum

/-- Whole-word local moment lower bound from explicit per-factor charges. -/
theorem word_moment_le [DecidableEq n]
    (word : List (Matrix (n ⊕ n) (n ⊕ n) K))
    (charge : Matrix (n ⊕ n) (n ⊕ n) K → ℕ)
    (hcharge : ∀ U ∈ word, (mixing U).rank ≤ charge U)
    {p : ℝ} (hp : 0 < p) (hp1 : p ≤ 1) :
    ((mixing word.prod).rank : ℝ) ^ p ≤
      ((word.map charge).map (fun r => (r : ℝ) ^ p)).sum :=
  moment_lower_bound _ _ (word_rank_le word charge hcharge) hp hp1

#print axioms word_moment_le
#print axioms mixing_mul
#print axioms mixing_rank_mul_le
#print axioms word_rank_le
#print axioms moment_lower_bound
end EndpointRank
