import Mathlib.Analysis.Convex.SpecificFunctions.Pow
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum

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
