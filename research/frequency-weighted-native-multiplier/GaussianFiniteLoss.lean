import Mathlib.Tactic
import Mathlib.Analysis.SpecialFunctions.Log.Deriv
import Mathlib.Analysis.SpecialFunctions.Pow.Real

namespace GaussianFiniteLoss

/-- The rational three-term estimate applies to the true marginal cost of every edge. -/
theorem threeTerms (z c : ℝ) (hz : 1 ≤ z) (hc : 0 < c) :
    let u := (z - 1) / (z + 1)
    2 * (u + u^3/3 + u^5/5) ≤ (z^c - 1)/c := by
  dsimp only
  let u := (z - 1) / (z + 1)
  have hu : 0 ≤ u := div_nonneg (by linarith) (by linarith)
  have hs : HasSum (fun i : ℕ => (2 : ℝ) * (1 / (2 * i + 1)) * u ^ (2 * i + 1))
      (Real.log z) := by
    simpa only [u, show 1 + (z - 1) = z by ring, show z - 1 + 2 = z + 1 by ring]
      using Real.hasSum_log_one_add (a := z - 1) (by linarith)
  have hp := hs.summable.sum_le_tsum (Finset.range 3) (fun j _ => by positivity)
  rw [hs.tsum_eq] at hp
  norm_num [Finset.sum_range_succ] at hp
  have hl : 2*(u+u^3/3+u^5/5) ≤ Real.log z := by linarith
  have he := Real.add_one_le_exp (Real.log z * c)
  rw [← Real.rpow_def_of_pos (by linarith : 0 < z) c] at he
  apply (le_div_iff₀ hc).2
  change (2*(u+u^3/3+u^5/5)) * c ≤ _
  nlinarith [mul_le_mul_of_nonneg_right hl hc.le]

/-- The active cost at one depth needs the child-volume bound with ratio one. -/
theorem activeDepth (M D F x a b : ℝ) (j : ℕ)
    (hM : 1 ≤ M) (hD : 0 ≤ D) (hF : 0 ≤ F) (volume : F ≤ M^(1-b))
    (ha : a ≤ 1) (hab : a ≤ b) (hx : 0 ≤ x) (width : x ≤ D / M^j) :
    F^j * x^(1-a) ≤ D^(1-a) := by
  have hM0 : 0 < M := by linarith
  have hp : 0 < M^j := pow_pos hM0 _
  have hv : F ≤ M^(1-a) :=
    volume.trans (Real.rpow_le_rpow_of_exponent_le hM (by linarith))
  have hj : F^j ≤ (M^j)^(1-a) := by
    rw [← Real.rpow_pow_comm hM0.le]
    exact pow_le_pow_left₀ hF hv j
  calc
    _ ≤ (M^j)^(1-a) * (D/M^j)^(1-a) :=
      mul_le_mul hj (Real.rpow_le_rpow hx width (by linarith))
        (Real.rpow_nonneg hx _) (Real.rpow_nonneg hp.le _)
    _ = D^(1-a) := by
      rw [← Real.mul_rpow hp.le (div_nonneg hD hp.le)]
      congr 1
      field_simp

#print axioms activeDepth

#print axioms threeTerms
end GaussianFiniteLoss
