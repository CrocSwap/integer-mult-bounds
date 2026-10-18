import Mathlib

/-!
Rational square certificates for binary real-power enclosures.
Certificate proposals are untrusted: every step is proved in the kernel.
Gareth Davidson with substantial OpenAI Codex assistance. Apache-2.0.
-/

namespace DyadicPower

/-- One binary digit transforms exponent e to (e+b)/2. Nonnegativity of the
proposed bound is essential when passing from squares to ordered reals. -/
theorem half_step {x e b u v : ℝ} (hx : 0 < x)
    (previous : x ^ e ≤ u) (hv : 0 ≤ v)
    (square : u * x ^ b ≤ v ^ 2) : x ^ ((e + b) / 2) ≤ v := by
  apply (sq_le_sq₀ (Real.rpow_nonneg hx.le _) hv).mp
  calc
    (x ^ ((e + b) / 2)) ^ 2 = x ^ (e + b) := by
      rw [← Real.rpow_natCast, ← Real.rpow_mul hx.le]
      congr 1
      norm_num
    _ = x ^ e * x ^ b := Real.rpow_add hx e b
    _ ≤ u * x ^ b := mul_le_mul_of_nonneg_right previous (Real.rpow_nonneg hx.le _)
    _ ≤ v ^ 2 := square

/-- For bases below one, rounding the exponent down gives an upper bound. -/
theorem upper_of_rounded_exponent {x q t u : ℝ} (hx : 0 < x) (hx1 : x ≤ 1)
    (hqt : q ≤ t) (bound : x ^ q ≤ u) : x ^ t ≤ u :=
  (Real.rpow_le_rpow_of_exponent_ge hx hx1 hqt).trans bound

theorem negative_square_is_not_upper :
    (1 : ℝ) ≤ (-1 : ℝ) ^ 2 ∧ ¬ (1 : ℝ) ^ (1 / 2 : ℝ) ≤ -1 := by
  norm_num

theorem upward_exponent_is_not_upper :
    (1 / 64 : ℝ) ^ (130850 / 131072 : ℝ) < (1 / 64 : ℝ) ^ (9983 / 10000 : ℝ) := by
  exact (Real.rpow_lt_rpow_left_iff_of_base_lt_one (by norm_num) (by norm_num)).mpr
    (by norm_num)

end DyadicPower

#print axioms DyadicPower.half_step
#print axioms DyadicPower.upper_of_rounded_exponent
#print axioms DyadicPower.negative_square_is_not_upper
#print axioms DyadicPower.upward_exponent_is_not_upper
