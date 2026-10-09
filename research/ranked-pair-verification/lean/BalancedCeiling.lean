import Mathlib.Tactic

/-!
A necessary global assembly ceiling for fixed bit saving `a`.
No multiplication theorem or sufficiency of all assembly conditions is claimed.
The hypotheses explicitly isolate the two final margins that impose the bound.
-/

namespace BalancedCeiling

/-- Every choice of epsilon obeys the universal two-margin upper bound. -/
theorem min_margin_le (a ε : ℝ) (ha : 0 ≤ a) :
    min (1 - ε) (ε * a) ≤ a / (1 + a) := by
  have hd : 0 < 1 + a := by linarith
  by_cases h : ε ≤ 1 / (1 + a)
  · calc
      min (1 - ε) (ε * a) ≤ ε * a := min_le_right _ _
      _ ≤ (1 / (1 + a)) * a := mul_le_mul_of_nonneg_right h ha
      _ = a / (1 + a) := by ring
  · have hε : 1 / (1 + a) < ε := lt_of_not_ge h
    have heq : 1 - 1 / (1 + a) = a / (1 + a) := by
      field_simp
    calc
      min (1 - ε) (ε * a) ≤ 1 - ε := min_le_left _ _
      _ ≤ 1 - 1 / (1 + a) := by linarith
      _ = a / (1 + a) := heq

/-- The two-margin relaxation attains this bound at epsilon = 1/(1+a).
This does not assert attainment under the full system's strict inequalities. -/
theorem balanced_attains (a : ℝ) (ha : 0 ≤ a) :
    min (1 - 1 / (1 + a)) ((1 / (1 + a)) * a) = a / (1 + a) := by
  have hd : 1 + a ≠ 0 := by linarith
  have hleft : 1 - 1 / (1 + a) = a / (1 + a) := by
    field_simp
  rw [hleft]
  have hright : (1 / (1 + a)) * a = a / (1 + a) := by ring
  rw [hright, min_self]

/-- If the achieved saving q is no larger than the certified bit saving a,
the two strict assembly margins force kappa strictly below a/(1+a). -/
theorem strict_ceiling (a q ε κ : ℝ) (ha : 0 ≤ a) (hε : 0 ≤ ε)
    (hq : q ≤ a) (hfirst : κ < 1 - ε) (hsecond : κ < ε * q) :
    κ < a / (1 + a) := by
  have hqa : ε * q ≤ ε * a := mul_le_mul_of_nonneg_left hq hε
  have hmin : κ < min (1 - ε) (ε * a) := lt_min hfirst (lt_of_lt_of_le hsecond hqa)
  exact lt_of_lt_of_le hmin (min_margin_le a ε ha)

#print axioms min_margin_le
#print axioms balanced_attains
#print axioms strict_ceiling

end BalancedCeiling
