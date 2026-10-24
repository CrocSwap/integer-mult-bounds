/-
Copyright (c) 2026. Released under the Apache 2.0 license.
Signed Cao Yifan. Substantial OpenAI Codex assistance.

Strict moment improvement for the changed joint native-contact census.
This analytic theorem does not formalize native-word semantics or the
integer-multiplication transfer.
-/
import Mathlib.Analysis.Convex.SpecificFunctions.Pow
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

namespace KappaChangedG

noncomputable def gain (t : ℝ) : ℝ :=
  2 * (4 : ℝ) ^ t - (3 : ℝ) ^ t - (5 : ℝ) ^ t

/-- Strict concavity at the distinct points 3 and 5, with midpoint 4. -/
theorem gain_pos {t : ℝ} (ht0 : 0 < t) (ht1 : t < 1) : 0 < gain t := by
  have h := (Real.strictConcaveOn_rpow ht0 ht1).2
    (show (3 : ℝ) ∈ Set.Ici 0 by norm_num)
    (show (5 : ℝ) ∈ Set.Ici 0 by norm_num)
    (by norm_num : (3 : ℝ) ≠ 5)
    (show (0 : ℝ) < 1 / 2 by norm_num)
    (show (0 : ℝ) < 1 / 2 by norm_num)
    (show (1 / 2 : ℝ) + 1 / 2 = 1 by norm_num)
  norm_num [smul_eq_mul] at h
  unfold gain
  linarith

noncomputable def oldPaidMoment (t : ℝ) : ℝ :=
  2201 * (1 : ℝ) ^ t + 412 * (2 : ℝ) ^ t + 506 * (3 : ℝ) ^ t +
    135 * (4 : ℝ) ^ t + 36 * (5 : ℝ) ^ t + 8 * (8 : ℝ) ^ t

noncomputable def newPaidMoment (t : ℝ) : ℝ :=
  2201 * (1 : ℝ) ^ t + 412 * (2 : ℝ) ^ t + 510 * (3 : ℝ) ^ t +
    127 * (4 : ℝ) ^ t + 40 * (5 : ℝ) ^ t + 8 * (8 : ℝ) ^ t

theorem paid_moment_difference (t : ℝ) :
    oldPaidMoment t - newPaidMoment t = 4 * gain t := by
  unfold oldPaidMoment newPaidMoment gain
  ring

theorem paid_moment_strict_improvement {t : ℝ} (ht0 : 0 < t) (ht1 : t < 1) :
    newPaidMoment t < oldPaidMoment t := by
  have h := mul_pos (by norm_num : (0 : ℝ) < 4) (gain_pos ht0 ht1)
  rw [← paid_moment_difference t] at h
  exact sub_pos.mp h

theorem strict_moment_savings {t : ℝ} (ht0 : 0 < t) (ht1 : t < 1) :
    newPaidMoment t < oldPaidMoment t :=
  paid_moment_strict_improvement ht0 ht1

theorem global_paid_moment_difference (t : ℝ) :
    18 * oldPaidMoment t - 18 * newPaidMoment t = 72 * gain t := by
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
