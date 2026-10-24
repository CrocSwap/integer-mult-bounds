/-
Apache-2.0. Cao Yifan; substantial OpenAI Codex assistance.
Conditional analytic cost lemma only. Finite phase-kernel support classification
is checked in Python, not formalized by this source. No multiplication theorem.
-/
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

namespace PhasePreprocessing

lemma factor_rpow (x t : ℝ) (hx : 0 < x) :
    x * x ^ (t-1) = x ^ t := by
  calc
    x * x ^ (t-1) = x ^ (1 : ℝ) * x ^ (t-1) := by rw [Real.rpow_one]
    _ = x ^ ((1 : ℝ)+(t-1)) := (Real.rpow_add hx _ _).symm
    _ = x ^ t := by congr 1; ring

theorem strict_subadditivity (g h t : ℝ) (hg : 0 < g) (hh : 0 < h) (ht : t < 1) :
    (g+h) ^ t < g ^ t + h ^ t := by
  have he : t-1 < 0 := by linarith
  have h₁ := mul_lt_mul_of_pos_left
    (Real.rpow_lt_rpow_of_neg hg (by linarith : g < g+h) he) hg
  have h₂ := mul_lt_mul_of_pos_left
    (Real.rpow_lt_rpow_of_neg hh (by linarith : h < g+h) he) hh
  rw [factor_rpow g t hg] at h₁
  rw [factor_rpow h t hh] at h₂
  have hs := add_lt_add h₁ h₂
  rw [← add_mul, factor_rpow (g+h) t (by linarith)] at hs
  exact hs

theorem one_helper_boundary_is_unprofitable (g h d t : ℝ)
    (hg : 0 < g) (hh : 0 < h) (hd : 0 ≤ d) (hdh : d ≤ h)
    (ht₀ : 0 < t) (ht₁ : t < 1) :
    (g+d) ^ t - g ^ t < h ^ t := by
  have hm := Real.rpow_le_rpow (by linarith : 0 ≤ g+d)
    (by linarith : g+d ≤ g+h) ht₀.le
  have hs := strict_subadditivity g h t hg hh ht₁
  linarith

theorem repeated_boundary_is_unprofitable (n g h d t : ℝ)
    (hn : 0 < n) (hg : 0 < g) (hh : 0 < h) (hd : 0 ≤ d) (hdh : d ≤ h)
    (ht₀ : 0 < t) (ht₁ : t < 1) :
    n * ((g+d)^t-g^t-h^t) < 0 := by
  have hneg : (g+d)^t-g^t-h^t < 0 := by
    have hs := one_helper_boundary_is_unprofitable g h d t hg hh hd hdh ht₀ ht₁
    linarith
  exact mul_neg_of_pos_of_neg hn hneg

end PhasePreprocessing

#print axioms PhasePreprocessing.factor_rpow
#print axioms PhasePreprocessing.strict_subadditivity
#print axioms PhasePreprocessing.one_helper_boundary_is_unprofitable
#print axioms PhasePreprocessing.repeated_boundary_is_unprofitable
