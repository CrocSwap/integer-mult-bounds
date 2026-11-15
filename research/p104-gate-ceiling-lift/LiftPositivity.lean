/-
Toolchain status: checked under Lean v4.33.0-rc1 / Mathlib 55b7917 (with the import
Mathlib.Analysis.Complex.ExponentialBounds, its path in that Mathlib). The import below is the one
for the repository pin (Lean v4.21 / Mathlib 308445d): not yet built under that pin.

Input-lift positivity for the complex interval gate, on kappa in (0, 69/10000].

  lift kappa = 7^(1-k) + 3^(1-k) + 5^(1-k) - 9^(1-k) - 4^(1-k) - 2 * 1^(1-k)

This is the moment of the input-lift histogram (pos {7,3,5}, neg {9,4,1,1}) in
shared-wire-split-composition/interval_gate.py. Same style as AnalyticGain.lean
(research/kappa-lean-verification-20261022): a derivative sign on an interval,
strict monotonicity, and the endpoint value. The derivative sign is the SIGNED
curvature bound: only the negative-coefficient ranks (9, 4) are lowered via
exp x >= 1 + x; the positive ranks (7, 3, 5) are raised via r^t <= r (t <= 1).
Logarithms of 3, 5, 7 are bracketed from Mathlib's log 2 bounds and the
alternating log(1 - x) series remainder. Scope: this lemma only; it does not
formalize the gate's other checks, the native word or the compiler.
-/
import Mathlib.Analysis.SpecialFunctions.Pow.Deriv
import Mathlib.Analysis.Calculus.Deriv.MeanValue
import Mathlib.Analysis.SpecialFunctions.Log.Deriv
import Mathlib.Data.Complex.ExponentialBounds
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

namespace KappaInputLift

open Real

/-- Lift moment in the exponent t = 1 - kappa. -/
noncomputable def f (t : ℝ) : ℝ :=
  (7 : ℝ) ^ t + (3 : ℝ) ^ t + (5 : ℝ) ^ t - (9 : ℝ) ^ t - (4 : ℝ) ^ t - 2 * (1 : ℝ) ^ t

noncomputable def f' (t : ℝ) : ℝ :=
  (7 : ℝ) ^ t * Real.log 7 + (3 : ℝ) ^ t * Real.log 3 + (5 : ℝ) ^ t * Real.log 5
    - (9 : ℝ) ^ t * Real.log 9 - (4 : ℝ) ^ t * Real.log 4

/-- The lift as a function of kappa, exactly as the gate evaluates it. -/
noncomputable def lift (k : ℝ) : ℝ := f (1 - k)

lemma hasDerivAt_f (t : ℝ) : HasDerivAt f (f' t) t := by
  have d : ∀ a : ℝ, 0 < a → HasDerivAt (fun x : ℝ => a ^ x) (a ^ t * Real.log a) t :=
    fun a ha => (Real.hasStrictDerivAt_const_rpow ha t).hasDerivAt
  have h := (((((d 7 (by norm_num)).add (d 3 (by norm_num))).add (d 5 (by norm_num))).sub
    (d 9 (by norm_num))).sub (d 4 (by norm_num))).sub_const (2 : ℝ)
  have e : f = fun x : ℝ => (7 : ℝ) ^ x + (3 : ℝ) ^ x + (5 : ℝ) ^ x - (9 : ℝ) ^ x - (4 : ℝ) ^ x - 2 := by
    funext x; simp [f]
  rw [e]; exact h

/-- r^t <= r for r >= 1, t <= 1. -/
lemma rpow_le_self' {r t : ℝ} (hr : 1 ≤ r) (ht : t ≤ 1) : r ^ t ≤ r := by
  simpa only [Real.rpow_one] using Real.rpow_le_rpow_of_exponent_le hr ht

/-- r^t >= r (1 + (t-1) log r) for r > 0 (exp x >= 1 + x). -/
lemma rpow_ge_tangent {r : ℝ} (hr : 0 < r) (t : ℝ) :
    r * (Real.log r * (t - 1) + 1) ≤ r ^ t := by
  have e : r ^ t = r * Real.exp (Real.log r * (t - 1)) := by
    rw [Real.rpow_def_of_pos hr]
    have h : Real.log r * t = Real.log r + Real.log r * (t - 1) := by ring
    rw [h, Real.exp_add, Real.exp_log hr]
  rw [e]
  exact mul_le_mul_of_nonneg_left (by linarith [Real.add_one_le_exp (Real.log r * (t - 1))]) hr.le

/-- log(1 - x) brackets from the series remainder. -/
lemma log_one_sub_bounds (x : ℝ) (hx0 : 0 ≤ x) (hx : x < 1) (n : ℕ) :
    -(∑ i ∈ Finset.range n, x ^ (i + 1) / (i + 1)) - x ^ (n + 1) / (1 - x) ≤ Real.log (1 - x) ∧
    Real.log (1 - x) ≤ -(∑ i ∈ Finset.range n, x ^ (i + 1) / (i + 1)) + x ^ (n + 1) / (1 - x) := by
  have h := Real.abs_log_sub_add_sum_range_le (show |x| < 1 by rwa [abs_of_nonneg hx0]) n
  rw [abs_of_nonneg hx0] at h
  constructor <;> linarith [(abs_le.mp h).1, (abs_le.mp h).2]

lemma log2_lo : (0.6931471803 : ℝ) < Real.log 2 := Real.log_two_gt_d9
lemma log2_hi : Real.log 2 < (0.6931471808 : ℝ) := Real.log_two_lt_d9

lemma log4_eq : Real.log 4 = 2 * Real.log 2 := by
  have h := Real.log_pow (2 : ℝ) 2; norm_num at h; exact h
lemma log8_eq : Real.log 8 = 3 * Real.log 2 := by
  have h := Real.log_pow (2 : ℝ) 3; norm_num at h; exact h
lemma log9_eq : Real.log 9 = 2 * Real.log 3 := by
  have h := Real.log_pow (3 : ℝ) 2; norm_num at h; exact h

/-- log 3 = log 4 + log(1 - 1/4). -/
lemma log3_bounds : (1.0986 : ℝ) < Real.log 3 ∧ Real.log 3 < 1.09862 := by
  have e : Real.log 3 = Real.log 4 + Real.log (1 - 1/4) := by
    rw [← Real.log_mul (by norm_num) (by norm_num)]; norm_num
  obtain ⟨l, u⟩ := log_one_sub_bounds (1/4) (by norm_num) (by norm_num) 8
  simp only [Finset.sum_range_succ, Finset.sum_range_zero] at l u
  norm_num at l u
  rw [e, log4_eq]; constructor <;> nlinarith [log2_lo, log2_hi]

/-- log 5 = log 4 - log(1 - 1/5). -/
lemma log5_bounds : (1.60943 : ℝ) < Real.log 5 ∧ Real.log 5 < 1.60944 := by
  have e : Real.log 5 = Real.log 4 - Real.log (1 - 1/5) := by
    rw [← Real.log_div (by norm_num) (by norm_num)]; norm_num
  obtain ⟨l, u⟩ := log_one_sub_bounds (1/5) (by norm_num) (by norm_num) 8
  simp only [Finset.sum_range_succ, Finset.sum_range_zero] at l u
  norm_num at l u
  rw [e, log4_eq]; constructor <;> nlinarith [log2_lo, log2_hi]

/-- log 7 = log 8 + log(1 - 1/8). -/
lemma log7_bounds : (1.945909 : ℝ) < Real.log 7 ∧ Real.log 7 < 1.94592 := by
  have e : Real.log 7 = Real.log 8 + Real.log (1 - 1/8) := by
    rw [← Real.log_mul (by norm_num) (by norm_num)]; norm_num
  obtain ⟨l, u⟩ := log_one_sub_bounds (1/8) (by norm_num) (by norm_num) 6
  simp only [Finset.sum_range_succ, Finset.sum_range_zero] at l u
  norm_num at l u
  rw [e, log8_eq]; constructor <;> nlinarith [log2_lo, log2_hi]

/-- The gate inequality itself, in exact reals: with d1 = sum_pos r log r - sum_neg r log r
and the SIGNED curvature N = sum_neg r log^2 r, d1 + (69/10000) N < 0. -/
theorem signed_gate_inequality :
    (7 * Real.log 7 + 3 * Real.log 3 + 5 * Real.log 5 - 9 * Real.log 9 - 4 * Real.log 4)
      + (69 / 10000) * (9 * Real.log 9 ^ 2 + 4 * Real.log 4 ^ 2) < 0 := by
  obtain ⟨b0, b1⟩ := log3_bounds
  obtain ⟨c0, c1⟩ := log5_bounds
  obtain ⟨d0, d1⟩ := log7_bounds
  have a0 := log2_lo; have a1 := log2_hi
  rw [log9_eq, log4_eq]
  nlinarith [mul_lt_mul'' b1 b1 (by linarith) (by linarith),
    mul_lt_mul'' a1 a1 (by linarith) (by linarith)]

lemma f'_neg {t : ℝ} (ht0 : 9931 / 10000 ≤ t) (ht1 : t ≤ 1) : f' t < 0 := by
  have hl : ∀ r : ℝ, 1 ≤ r → 0 ≤ Real.log r := fun r hr => Real.log_nonneg hr
  have u7 := mul_le_mul_of_nonneg_right (rpow_le_self' (by norm_num : (1:ℝ) ≤ 7) ht1) (hl 7 (by norm_num))
  have u3 := mul_le_mul_of_nonneg_right (rpow_le_self' (by norm_num : (1:ℝ) ≤ 3) ht1) (hl 3 (by norm_num))
  have u5 := mul_le_mul_of_nonneg_right (rpow_le_self' (by norm_num : (1:ℝ) ≤ 5) ht1) (hl 5 (by norm_num))
  have l9 := mul_le_mul_of_nonneg_right (rpow_ge_tangent (by norm_num : (0:ℝ) < 9) t) (hl 9 (by norm_num))
  have l4 := mul_le_mul_of_nonneg_right (rpow_ge_tangent (by norm_num : (0:ℝ) < 4) t) (hl 4 (by norm_num))
  -- (t - 1) >= -69/10000 and log r >= 0, so log r (t - 1) >= -(69/10000) log r.
  have g9 : Real.log 9 * (t - 1) ≥ -(69/10000) * Real.log 9 := by
    nlinarith [hl 9 (by norm_num)]
  have g4 : Real.log 4 * (t - 1) ≥ -(69/10000) * Real.log 4 := by
    nlinarith [hl 4 (by norm_num)]
  have L9 : 9 * (-(69/10000) * Real.log 9 + 1) * Real.log 9 ≤ (9:ℝ) ^ t * Real.log 9 := by
    refine le_trans ?_ l9
    exact mul_le_mul_of_nonneg_right (by linarith) (hl 9 (by norm_num))
  have L4 : 4 * (-(69/10000) * Real.log 4 + 1) * Real.log 4 ≤ (4:ℝ) ^ t * Real.log 4 := by
    refine le_trans ?_ l4
    exact mul_le_mul_of_nonneg_right (by linarith) (hl 4 (by norm_num))
  have G := signed_gate_inequality
  unfold f'
  nlinarith [u7, u3, u5, L9, L4, G]

lemma f_continuous : Continuous f :=
  continuous_iff_continuousAt.mpr fun t => (hasDerivAt_f t).continuousAt

lemma f_strictAntiOn : StrictAntiOn f (Set.Icc (9931 / 10000 : ℝ) 1) := by
  apply strictAntiOn_of_deriv_neg (convex_Icc _ _) f_continuous.continuousOn
  intro t ht
  rw [interior_Icc] at ht
  rw [(hasDerivAt_f t).deriv]
  exact f'_neg ht.1.le ht.2.le

lemma f_one : f 1 = 0 := by norm_num [f]

lemma lift_zero : lift 0 = 0 := by simp [lift, f_one]

/-- Input-lift positivity: 0 < lift kappa for 0 < kappa <= 69/10000. -/
theorem lift_pos {k : ℝ} (hk0 : 0 < k) (hk1 : k ≤ 69 / 10000) : 0 < lift k := by
  have h := f_strictAntiOn (show 1 - k ∈ Set.Icc (9931 / 10000 : ℝ) 1 by
      constructor <;> linarith)
    (show (1 : ℝ) ∈ Set.Icc (9931 / 10000 : ℝ) 1 by constructor <;> norm_num)
    (by linarith)
  rw [f_one] at h
  exact h

/-- Monotone form used by the gate: lift is strictly increasing on [0, 69/10000]. -/
theorem lift_strictMonoOn : StrictMonoOn lift (Set.Icc (0 : ℝ) (69 / 10000)) := by
  intro a ha b hb hab
  exact f_strictAntiOn ⟨by linarith [hb.2], by linarith [hb.1]⟩
    ⟨by linarith [ha.2], by linarith [ha.1]⟩ (by linarith)

end KappaInputLift

#print axioms KappaInputLift.signed_gate_inequality
#print axioms KappaInputLift.lift_pos
#print axioms KappaInputLift.lift_strictMonoOn
