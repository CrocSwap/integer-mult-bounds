/-
Copyright (c) 2026. Released under the Apache 2.0 license.
Substantial OpenAI Codex assistance.

Two real-power capacity inequalities at the explicit tested saving. These are
scoped scalar inequalities, not a formalization of the multiplication compiler.
-/
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith

namespace KappaChangedG

noncomputable def capacitySaving : ℝ := 302153 / 100000000
noncomputable def capacityT : ℝ := 1 - capacitySaving
noncomputable def capacityExponent : ℝ := 1024 * capacitySaving
noncomputable def capacityEta : ℝ := capacityT * (145 : ℝ) ^ (-capacityExponent)

lemma root145_lt_two : (145 : ℝ) ^ (1 / 8 : ℝ) < 2 := by
  rw [show (1 / 8 : ℝ) = (8 : ℝ)⁻¹ by norm_num]
  apply (Real.rpow_inv_lt_iff_of_pos (by norm_num : (0 : ℝ) ≤ 145)
    (by norm_num : (0 : ℝ) ≤ 2) (by norm_num : (0 : ℝ) < 8)).mpr
  norm_num

lemma capacity_power_upper : (145 : ℝ) ^ capacityExponent < 6097250 := by
  calc
    (145 : ℝ) ^ capacityExponent < (145 : ℝ) ^ (3 + 1 / 8 : ℝ) :=
      Real.rpow_lt_rpow_of_exponent_lt (by norm_num : (1 : ℝ) < 145)
        (by norm_num [capacityExponent, capacitySaving])
    _ = (145 : ℝ) ^ (3 : ℕ) * (145 : ℝ) ^ (1 / 8 : ℝ) := by
      rw [Real.rpow_add (by norm_num : (0 : ℝ) < 145)]
      simp
    _ < (145 : ℝ) ^ (3 : ℕ) * 2 :=
      mul_lt_mul_of_pos_left root145_lt_two (by norm_num)
    _ = 6097250 := by norm_num

lemma capacity_eta_lower : capacityT / 6097250 < capacityEta := by
  have hp : (0 : ℝ) < (145 : ℝ) ^ capacityExponent :=
    Real.rpow_pos_of_pos (by norm_num) _
  have hinv : (1 : ℝ) / 6097250 < 1 / (145 : ℝ) ^ capacityExponent :=
    one_div_lt_one_div_of_lt hp capacity_power_upper
  have ht : (0 : ℝ) < capacityT := by norm_num [capacityT, capacitySaving]
  have h := mul_lt_mul_of_pos_left hinv ht
  simpa only [capacityEta, Real.rpow_neg (by norm_num : (0 : ℝ) ≤ 145),
    div_eq_mul_inv, one_mul] using h

theorem compiler_eta_capacity : (63 / 64 : ℝ) ^ (1000 : ℕ) < capacityEta := by
  calc
    (63 / 64 : ℝ) ^ (1000 : ℕ) < capacityT / 6097250 := by
      norm_num [capacityT, capacitySaving]
    _ < capacityEta := capacity_eta_lower

theorem compiler_initial_range :
    (145 : ℝ) ^ capacityExponent < (2 : ℝ) ^ (1000 : ℕ) := by
  calc
    (145 : ℝ) ^ capacityExponent < 6097250 := capacity_power_upper
    _ < (2 : ℝ) ^ (1000 : ℕ) := by norm_num

end KappaChangedG

#print axioms KappaChangedG.root145_lt_two
#print axioms KappaChangedG.capacity_power_upper
#print axioms KappaChangedG.capacity_eta_lower
#print axioms KappaChangedG.compiler_eta_capacity
#print axioms KappaChangedG.compiler_initial_range
