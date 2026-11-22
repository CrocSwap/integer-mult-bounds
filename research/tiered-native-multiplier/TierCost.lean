import Mathlib.Tactic

namespace TierCost

/-- Each admitted high fibre has enough cells to pay its coefficient clock. -/
theorem highFibre (k : ℕ) (hk : 30 ≤ k) : 2660000 * (k + 2) < 2 ^ k := by
  induction k, hk using Nat.le_induction with
  | base => decide
  | succ k hk ih =>
    rw [pow_succ]
    omega

/-- Convert a rate on a finite initial interval to the global rate. -/
theorem finitePrefix (x A lo hi : ℝ) (hx : 0 < x) (hA : x ≤ (2:ℝ)^A)
    (hh : lo ≤ hi) : x^(1-lo) ≤ x^(1-hi) * (2:ℝ)^(A*(hi-lo)) := by
  have h := Real.rpow_le_rpow hx.le hA (sub_nonneg.mpr hh)
  rw [← Real.rpow_mul (by norm_num : (0:ℝ) ≤ 2)] at h
  calc
    x^(1-lo) = x^(1-hi) * x^(hi-lo) := by
      rw [← Real.rpow_add hx]
      congr 1
      ring
    _ ≤ _ := mul_le_mul_of_nonneg_left h (Real.rpow_nonneg hx.le _)

theorem entryPrice (x : ℝ) (hx : 0 < x) (hA : x ≤ (2:ℝ)^(1274851:ℝ)) :
    x^(1-(345:ℝ)/100000) ≤ x^(1-(38982:ℝ)/10000000) * (2:ℝ)^(572:ℝ) := by
  apply (finitePrefix x 1274851 (345/100000) (38982/10000000) hx hA (by norm_num)).trans
  apply mul_le_mul_of_nonneg_left _ (Real.rpow_nonneg hx.le _)
  exact Real.rpow_le_rpow_of_exponent_le (by norm_num) (by norm_num)

theorem strictGain :
    (19491:ℚ)/5000000 - 7796346051/2000000000000 = 53949/2000000000000 := by norm_num

#print axioms highFibre
#print axioms finitePrefix
#print axioms entryPrice
#print axioms strictGain
end TierCost
