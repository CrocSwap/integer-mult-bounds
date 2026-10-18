import Mathlib.Analysis.Convex.SpecificFunctions.Pow
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum

/-! Sufficient cost certificates for removing a rank-four helper and returning
its owned four axes to a rank-one remainder, replacing ranks 1 and 4 by 5. -/
namespace IntegerMultBounds.BorrowDeletion

/-- Joining two positive ranks strictly lowers every sublinear real-power cost. -/
theorem strict_subadditive_rpow_pos (x y p : ℝ) (hx : 0 < x) (hy : 0 < y)
    (hp : 0 ≤ p) (hp1 : p < 1) : (x+y)^p < x^p + y^p := by
  rcases hp.eq_or_lt with hzero | hpos
  · subst p
    norm_num
  have hsum : 0 < x+y := add_pos hx hy
  have hweights : y/(x+y) + x/(x+y) = 1 := by
    field_simp
    ring
  have hweights' : x/(x+y) + y/(x+y) = 1 := by linarith [hweights]
  have h0 : (0 : ℝ) ∈ Set.Ici 0 := by norm_num
  have hs : x+y ∈ Set.Ici (0 : ℝ) := le_of_lt hsum
  have hne : (0 : ℝ) ≠ x+y := ne_of_lt hsum
  have ha := (Real.strictConcaveOn_rpow hpos hp1).2 h0 hs hne
    (div_pos hy hsum) (div_pos hx hsum) hweights
  have hb := (Real.strictConcaveOn_rpow hpos hp1).2 h0 hs hne
    (div_pos hx hsum) (div_pos hy hsum) hweights'
  simp only [smul_eq_mul, Real.zero_rpow (ne_of_gt hpos), mul_zero, zero_add,
    div_mul_cancel₀ _ (ne_of_gt hsum)] at ha hb
  have heq : y/(x+y) * (x+y)^p + x/(x+y) * (x+y)^p = (x+y)^p := by
    rw [← add_mul, hweights, one_mul]
  linarith

/-- The actual helper deletion changes C1+C4 into C5 and strictly saves cost. -/
theorem rank_four_deletion_strictly_cheaper (p : ℝ) (hp : 0 ≤ p) (hp1 : p < 1) :
    (5 : ℝ)^p - 1 - (4 : ℝ)^p < 0 := by
  have h := strict_subadditive_rpow_pos 1 4 p (by norm_num) (by norm_num) hp hp1
  norm_num at h
  linarith

/-- Any positive number of actual disjoint helper deletions gives a strict gain. -/
theorem repeated_deletion_strict (p count old : ℝ) (hp : 0 ≤ p) (hp1 : p < 1)
    (hcount : 0 < count) :
    old + count * ((5 : ℝ)^p - 1 - (4 : ℝ)^p) < old := by
  have h := mul_neg_of_pos_of_neg hcount (rank_four_deletion_strictly_cheaper p hp hp1)
  linarith

end IntegerMultBounds.BorrowDeletion
