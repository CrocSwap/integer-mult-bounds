import Pr73ProfileCertificate
import Mathlib.Analysis.SpecialFunctions.Pow.Real

/-! Actual real characteristic bound for the literal pinned PR73 finite profile.
The rational witness checks are imported as proved theorems. Both logarithm
and exponential enclosure validity are supplied by AnalyticEnclosures, not
assumed. Compiler-to-profile binding and tape/analytic multiplication transfer
remain separate; the conclusion here is an unconditional finite real inequality.
-/

namespace Pr73ProfileReal
open AnalyticEnclosures Pr73ProfileCertificate

theorem row_valid (r : Row) (hr : r ∈ rows) : valid r := by
  have h := List.all_eq_true.mp rows_checked r hr
  exact of_decide_eq_true h

theorem log_two_upper : Real.log 2 ≤ (logTwoUpper : ℝ) := by
  simpa using log_le_of_expPoly 2 logTwoUpper 24 (by decide)
    logTwo_certificate.1 logTwo_certificate.2

theorem row_log_upper (r : Row) (hr : r ∈ rows) :
    Real.log ((m : ℝ) / r.width) ≤ (logBound r : ℝ) := by
  rcases row_valid r hr with ⟨hw, _, hL, hpoly, _, _, _⟩
  have hwr : (0 : ℝ) < r.width := by exact_mod_cast hw
  have hratio : (0 : ℚ) < ratio r := by
    unfold ratio
    have hwidth : (0 : ℚ) < r.width := by exact_mod_cast hw
    norm_num [m]
    positivity
  have hlog := log_le_of_expPoly (ratio r) r.logSmall 24 hratio hL hpoly
  have heq : (m : ℝ) / r.width = (2 : ℝ) ^ r.scale * (ratio r : ℝ) := by
    simp only [ratio, Rat.cast_div, Rat.cast_natCast, Rat.cast_mul, Rat.cast_pow, Rat.cast_ofNat]
    field_simp
    ring
  have h := log_scale_upper ((m : ℝ) / r.width) (ratio r : ℝ)
    (r.logSmall : ℝ) (logTwoUpper : ℝ) r.scale (by exact_mod_cast hratio)
    heq hlog log_two_upper
  simpa [logBound] using h

theorem row_exp_upper (r : Row) (hr : r ∈ rows) :
    Real.exp ((saving : ℝ) * Real.log ((m : ℝ) / r.width)) ≤ (r.upper : ℝ) := by
  rcases row_valid r hr with ⟨_, _, _, _, harg, harg1, hupper⟩
  have hmon : Real.exp ((saving : ℝ) * Real.log ((m : ℝ) / r.width)) ≤
      Real.exp ((saving : ℝ) * (logBound r : ℝ)) := Real.exp_le_exp.mpr
    (mul_le_mul_of_nonneg_left (row_log_upper r hr) (by norm_num [saving]))
  have hx : Real.exp ((argument r : ℚ) : ℝ) ≤ (r.upper : ℝ) :=
    exp_le_of_expUpper (argument r) r.upper 8 harg harg1 (by decide) hupper
  exact hmon.trans (by simpa [argument] using hx)

noncomputable def exponentialCharacteristic : ℝ :=
  (rows.map (fun r => (weight r : ℝ) *
    Real.exp ((saving : ℝ) * Real.log ((m : ℝ) / r.width)))).sum

theorem real_characteristic_lt_one : exponentialCharacteristic < 1 := by
  have hrow : ∀ r ∈ rows,
      (weight r : ℝ) * Real.exp ((saving : ℝ) * Real.log ((m : ℝ) / r.width)) ≤
        ((weight r * r.upper : ℚ) : ℝ) := by
    intro r hr
    have hweight : (0 : ℝ) ≤ (weight r : ℝ) := by
      simp only [weight, Rat.cast_div, Rat.cast_mul, Rat.cast_natCast]
      positivity
    simpa using mul_le_mul_of_nonneg_left (row_exp_upper r hr) hweight
  have hsum := List.sum_le_sum hrow
  have hcast : (rows.map (fun r => ((weight r * r.upper : ℚ) : ℝ))).sum =
      (rationalUpper : ℝ) := by
    simp [rationalUpper, Function.comp_def]
  unfold exponentialCharacteristic
  rw [hcast] at hsum
  exact hsum.trans_lt (by exact_mod_cast rational_upper_lt_one)

/-- Exact term identity used to express the result in recurrence form. -/
theorem power_term_identity (n t m W a : ℝ) (ht : 0 < t) (hm : 0 < m) :
    (n / W) * (t / m) ^ (1 - a) =
      (n * t / (m * W)) * Real.exp (a * Real.log (m / t)) := by
  have hratio : 0 < t / m := div_pos ht hm
  have hlog : Real.log (t / m) = -Real.log (m / t) := by
    rw [Real.log_div ht.ne' hm.ne', Real.log_div hm.ne' ht.ne']
    ring
  have hpow : (t / m) ^ (1 - a) = (t / m) * Real.exp (a * Real.log (m / t)) := by
    rw [Real.rpow_def_of_pos hratio]
    have he : Real.log (t / m) * (1 - a) =
        Real.log (t / m) + a * Real.log (m / t) := by rw [hlog]; ring
    rw [he, Real.exp_add, Real.exp_log hratio]
  rw [hpow]
  ring

noncomputable def powerCharacteristic : ℝ :=
  (rows.map (fun r => (r.multiplicity : ℝ) / W *
    ((r.width : ℝ) / m) ^ (1 - (saving : ℝ)))).sum

/-- Kernel theorem: the literal pinned PR73 profile has actual real contraction
at a=12854322426487/250000000000000000. No enclosure premise remains. -/
theorem actual_power_characteristic_lt_one : powerCharacteristic < 1 := by
  have heq : powerCharacteristic = exponentialCharacteristic := by
    unfold powerCharacteristic exponentialCharacteristic
    congr 1
    apply List.map_congr_left
    intro r hr
    rw [power_term_identity _ _ _ _ _ (by exact_mod_cast (row_valid r hr).1) (by norm_num [m])]
    simp [weight]
  rw [heq]
  exact real_characteristic_lt_one

#print axioms row_valid
#print axioms log_two_upper
#print axioms row_log_upper
#print axioms row_exp_upper
#print axioms real_characteristic_lt_one
#print axioms power_term_identity
#print axioms actual_power_characteristic_lt_one

end Pr73ProfileReal
