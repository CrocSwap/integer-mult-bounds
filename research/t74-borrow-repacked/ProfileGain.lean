import Mathlib.Analysis.Convex.SpecificFunctions.Pow
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.FieldSimp

/-! Standalone publication assembly of ProviderExchange.lean and BorrowDeletion.lean.
Use this module OR the two component modules: it intentionally preserves their
seven declaration names and proofs, and adds the actual complete-profile gain. -/


/-! Universal sufficient paid-profile exchange certificates for the T74 providers.
The exact rank-count difference is (-12, +8, +4, -4) at ranks (1,2,3,4).
No machine or compiler admission is assumed or asserted by these scalar lemmas. -/

namespace IntegerMultBounds.ProviderExchange

/-- Concavity bounds the rank-three term using ranks one and two. -/
theorem rank_three_bound (p : ℝ) (hp : 0 ≤ p) (hp1 : p ≤ 1) :
    (3 : ℝ)^p ≤ 2 * (2 : ℝ)^p - 1 := by
  have h := (Real.concaveOn_rpow hp hp1).2
    (show (1 : ℝ) ∈ Set.Ici 0 by norm_num)
    (show (3 : ℝ) ∈ Set.Ici 0 by norm_num)
    (show (0 : ℝ) ≤ 1/2 by norm_num)
    (show (0 : ℝ) ≤ 1/2 by norm_num)
    (show (1/2 : ℝ) + 1/2 = 1 by norm_num)
  norm_num at h
  linarith

/-- The improvement has an explicit quadratic lower bound, including p = 0. -/
theorem provider_gap_lower_bound (p : ℝ) (hp : 0 ≤ p) (hp1 : p ≤ 1) :
    4 * (2 - (2 : ℝ)^p)^2 ≤
      12 - 8 * (2 : ℝ)^p - 4 * (3 : ℝ)^p + 4 * (4 : ℝ)^p := by
  have h := rank_three_bound p hp hp1
  have h4 : (4 : ℝ)^p = (2 : ℝ)^p * (2 : ℝ)^p := by
    simpa only [show (4 : ℝ) = 2*2 by norm_num] using
      (Real.mul_rpow (show (0 : ℝ) ≤ 2 by norm_num)
        (show (0 : ℝ) ≤ 2 by norm_num) (z := p))
  nlinarith

/-- Replacing one complete gauge44 call by extra strictly lowers its moment. -/
theorem extra_provider_strictly_cheaper (p : ℝ) (hp : 0 ≤ p) (hp1 : p < 1) :
    (-12 : ℝ) + 8 * (2 : ℝ)^p + 4 * (3 : ℝ)^p - 4 * (4 : ℝ)^p < 0 := by
  have h := provider_gap_lower_bound p hp hp1.le
  have ht : (2 : ℝ)^p < 2 := by
    simpa using Real.rpow_lt_rpow_of_exponent_lt (show (1 : ℝ) < 2 by norm_num) hp1
  have hs := sq_pos_of_pos (sub_pos.mpr ht)
  nlinarith

/-- Any positive number of complete-call substitutions preserves strict improvement. -/
theorem repeated_exchange_strict (p t old : ℝ) (hp : 0 ≤ p) (hp1 : p < 1)
    (ht : 0 < t) :
    old + t * ((-12 : ℝ) + 8 * (2 : ℝ)^p + 4 * (3 : ℝ)^p - 4 * (4 : ℝ)^p) < old := by
  have h := mul_neg_of_pos_of_neg ht (extra_provider_strictly_cheaper p hp hp1)
  linarith

end IntegerMultBounds.ProviderExchange


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

namespace IntegerMultBounds.ProfileGain

/-- Every actual profile change from PR2269 saves cost uniformly throughout [0,1). -/
theorem entire_actual_profile_gain (p : ℝ) (hp : 0 ≤ p) (hp1 : p < 1) :
    249 * ((-12 : ℝ) + 8 * (2 : ℝ)^p + 4 * (3 : ℝ)^p - 4 * (4 : ℝ)^p) +
    666 * ((5 : ℝ)^p - 1 - (4 : ℝ)^p) + ((14 : ℝ)^p - 2 * (7 : ℝ)^p) < 0 := by
  have he := ProviderExchange.extra_provider_strictly_cheaper p hp hp1
  have hd := BorrowDeletion.rank_four_deletion_strictly_cheaper p hp hp1
  have hc := BorrowDeletion.strict_subadditive_rpow_pos 7 7 p (by norm_num) (by norm_num) hp hp1
  norm_num at hc
  linarith

/-- Exact coefficient identity of the source-bound complete new and old power sums. -/
theorem actual_paid_power_difference (p : ℝ) :
    (1581084 + 338994 * (2 : ℝ)^p + 287061 * (3 : ℝ)^p +
      82584 * (4 : ℝ)^p + 29451 * (5 : ℝ)^p + 148 * (7 : ℝ)^p +
      5328 * (8 : ℝ)^p + (14 : ℝ)^p + 24479 * (48 : ℝ)^p) -
    (1584738 + 337002 * (2 : ℝ)^p + 286065 * (3 : ℝ)^p +
      84246 * (4 : ℝ)^p + 28785 * (5 : ℝ)^p + 150 * (7 : ℝ)^p +
      5328 * (8 : ℝ)^p + 24479 * (48 : ℝ)^p) =
    249 * ((-12 : ℝ) + 8 * (2 : ℝ)^p + 4 * (3 : ℝ)^p - 4 * (4 : ℝ)^p) +
    666 * ((5 : ℝ)^p - 1 - (4 : ℝ)^p) + ((14 : ℝ)^p - 2 * (7 : ℝ)^p) := by
  ring

end IntegerMultBounds.ProfileGain
