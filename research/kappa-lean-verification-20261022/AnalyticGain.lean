/-
Copyright (c) 2026. Released under the Apache 2.0 license.
Substantial OpenAI Codex assistance.

Scoped analytic theorem for the frozen changed-G paid profile. This file does
not formalize native-word correctness or the multiplication compiler.
-/
import Mathlib.Analysis.SpecialFunctions.Pow.Deriv
import Mathlib.Analysis.Calculus.Deriv.MeanValue
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

namespace KappaChangedG

noncomputable def gain (t : ℝ) : ℝ :=
  3 + (4 : ℝ) ^ t - 2 * (2 : ℝ) ^ t - (3 : ℝ) ^ t

noncomputable def gainDerivative (t : ℝ) : ℝ :=
  Real.log 4 * (4 : ℝ) ^ t -
    2 * (Real.log 2 * (2 : ℝ) ^ t) - Real.log 3 * (3 : ℝ) ^ t

lemma log_four : Real.log 4 = 2 * Real.log 2 := by
  have h := Real.log_pow (2 : ℝ) 2
  norm_num at h
  exact h

lemma log_bound : (4 / 3 : ℝ) * Real.log 2 - Real.log 3 < 0 := by
  have h := Real.log_lt_log (by norm_num : (0 : ℝ) < 16)
    (by norm_num : (16 : ℝ) < 27)
  have h16 := Real.log_pow (2 : ℝ) 4
  have h27 := Real.log_pow (3 : ℝ) 3
  norm_num at h16 h27
  rw [h16, h27] at h
  linarith

lemma gain_hasDerivAt (t : ℝ) : HasDerivAt gain (gainDerivative t) t := by
  have h4 : HasDerivAt (fun x : ℝ => (4 : ℝ) ^ x)
      (Real.log 4 * (4 : ℝ) ^ t) t := by
    simpa only [mul_comm] using
      (Real.hasStrictDerivAt_const_rpow (by norm_num : (0 : ℝ) < 4) t).hasDerivAt
  have h2 : HasDerivAt (fun x : ℝ => (2 : ℝ) ^ x)
      (Real.log 2 * (2 : ℝ) ^ t) t := by
    simpa only [mul_comm] using
      (Real.hasStrictDerivAt_const_rpow (by norm_num : (0 : ℝ) < 2) t).hasDerivAt
  have h3 : HasDerivAt (fun x : ℝ => (3 : ℝ) ^ x)
      (Real.log 3 * (3 : ℝ) ^ t) t := by
    simpa only [mul_comm] using
      (Real.hasStrictDerivAt_const_rpow (by norm_num : (0 : ℝ) < 3) t).hasDerivAt
  simpa only [gain, gainDerivative, zero_add] using
    (((hasDerivAt_const t (3 : ℝ)).add h4).sub (h2.const_mul 2)).sub h3

lemma gainDerivative_neg {t : ℝ} (ht : t ≤ 1) : gainDerivative t < 0 := by
  have hp3 : (0 : ℝ) < (3 : ℝ) ^ t := Real.rpow_pos_of_pos (by norm_num) t
  have hlog2 : 0 ≤ Real.log 2 := (Real.log_pos (by norm_num : (1 : ℝ) < 2)).le
  have h4 : (4 : ℝ) ^ t ≤ (4 / 3 : ℝ) * (3 : ℝ) ^ t := by
    have h := Real.rpow_le_self_of_one_le (by norm_num : (1 : ℝ) ≤ 4 / 3) ht
    rw [Real.div_rpow (by norm_num : (0 : ℝ) ≤ 4)
      (by norm_num : (0 : ℝ) ≤ 3)] at h
    exact (div_le_iff₀ hp3).mp h
  have h2 : (2 / 3 : ℝ) * (3 : ℝ) ^ t ≤ (2 : ℝ) ^ t := by
    have h := Real.self_le_rpow_of_le_one (by norm_num : (0 : ℝ) ≤ 2 / 3)
      (by norm_num : (2 / 3 : ℝ) ≤ 1) ht
    rw [Real.div_rpow (by norm_num : (0 : ℝ) ≤ 2)
      (by norm_num : (0 : ℝ) ≤ 3)] at h
    exact (le_div_iff₀ hp3).mp h
  have h4' := mul_le_mul_of_nonneg_left h4 (mul_nonneg (by norm_num : (0 : ℝ) ≤ 2) hlog2)
  have h2' := mul_le_mul_of_nonneg_left h2 (mul_nonneg (by norm_num : (0 : ℝ) ≤ 2) hlog2)
  have hnegative := mul_neg_of_pos_of_neg hp3 log_bound
  rw [gainDerivative, log_four]
  nlinarith

lemma gain_continuous : Continuous gain :=
  continuous_iff_continuousAt.mpr fun t => (gain_hasDerivAt t).continuousAt

lemma gain_strictAntiOn : StrictAntiOn gain (Set.Iic (1 : ℝ)) := by
  apply strictAntiOn_of_deriv_neg (convex_Iic (1 : ℝ)) gain_continuous.continuousOn
  intro t ht
  rw [(gain_hasDerivAt t).deriv]
  have ht' : t < 1 := by simpa only [interior_Iic, Set.mem_Iio] using ht
  exact gainDerivative_neg ht'.le

theorem gain_pos {t : ℝ} (ht : t < 1) : 0 < gain t := by
  have h := gain_strictAntiOn (show t ∈ Set.Iic (1 : ℝ) from ht.le)
    (show (1 : ℝ) ∈ Set.Iic (1 : ℝ) by simp) ht
  have hzero : gain 1 = 0 := by norm_num [gain]
  rw [hzero] at h
  exact h

noncomputable def oldPaidMoment (t : ℝ) : ℝ :=
  2237 * (1 : ℝ) ^ t + 388 * (2 : ℝ) ^ t + 494 * (3 : ℝ) ^ t +
    147 * (4 : ℝ) ^ t + 36 * (5 : ℝ) ^ t + 8 * (8 : ℝ) ^ t

noncomputable def newPaidMoment (t : ℝ) : ℝ :=
  2201 * (1 : ℝ) ^ t + 412 * (2 : ℝ) ^ t + 506 * (3 : ℝ) ^ t +
    135 * (4 : ℝ) ^ t + 36 * (5 : ℝ) ^ t + 8 * (8 : ℝ) ^ t

theorem paid_moment_difference (t : ℝ) :
    oldPaidMoment t - newPaidMoment t = 12 * gain t := by
  simp only [oldPaidMoment, newPaidMoment, gain, Real.one_rpow]
  ring

theorem paid_moment_strict_improvement {t : ℝ} (_ht0 : 0 < t) (ht1 : t < 1) :
    newPaidMoment t < oldPaidMoment t := by
  have h := mul_pos (by norm_num : (0 : ℝ) < 12) (gain_pos ht1)
  rw [← paid_moment_difference t] at h
  exact sub_pos.mp h

theorem global_paid_moment_difference (t : ℝ) :
    18 * oldPaidMoment t - 18 * newPaidMoment t = 216 * gain t := by
  nlinarith [paid_moment_difference t]

theorem global_paid_moment_strict_improvement {t : ℝ} (ht0 : 0 < t) (ht1 : t < 1) :
    18 * newPaidMoment t < 18 * oldPaidMoment t :=
  mul_lt_mul_of_pos_left (paid_moment_strict_improvement ht0 ht1) (by norm_num)

end KappaChangedG

#print axioms KappaChangedG.gain_pos
#print axioms KappaChangedG.paid_moment_difference
#print axioms KappaChangedG.paid_moment_strict_improvement
#print axioms KappaChangedG.global_paid_moment_difference
#print axioms KappaChangedG.global_paid_moment_strict_improvement
