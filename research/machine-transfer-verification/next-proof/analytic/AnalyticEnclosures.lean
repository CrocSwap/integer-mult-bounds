import Mathlib.Data.Complex.Exponential
import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Tactic

/-! Rational witnesses for actual real logarithmic and exponential bounds.
Every analytic implication is proved using pinned Mathlib theorems. The
remaining hypotheses are finite rational inequalities, intended for ordinary
kernel computation; no logarithm/Taylor enclosure is admitted as an axiom.
-/

namespace AnalyticEnclosures
open scoped BigOperators

def expPoly (x : ℚ) (n : ℕ) : ℚ :=
  ∑ i ∈ Finset.range n, x ^ i / (i.factorial : ℚ)

def expUpper (x : ℚ) (n : ℕ) : ℚ :=
  expPoly x n + x ^ n * (n + 1) / ((n.factorial : ℚ) * n)

theorem expPoly_cast (x : ℚ) (n : ℕ) :
    (expPoly x n : ℝ) = ∑ i ∈ Finset.range n, (x : ℝ) ^ i / (i.factorial : ℝ) := by
  simp [expPoly]

/-- A rational lower Taylor witness proves an upper bound for the real log. -/
theorem log_le_of_expPoly (q L : ℚ) (n : ℕ)
    (hq : 0 < q) (hL : 0 ≤ L) (certificate : q ≤ expPoly L n) :
    Real.log (q : ℝ) ≤ (L : ℝ) := by
  apply (Real.log_le_iff_le_exp (by exact_mod_cast hq)).mpr
  have hcert : (q : ℝ) ≤ (expPoly L n : ℝ) := by exact_mod_cast certificate
  rw [expPoly_cast] at hcert
  exact hcert.trans (Real.sum_le_exp_of_nonneg (by exact_mod_cast hL) n)

/-- A rational upper Taylor witness bounds the actual real exponential. -/
theorem exp_le_of_expUpper (x U : ℚ) (n : ℕ)
    (hx : 0 ≤ x) (hx1 : x ≤ 1) (hn : 0 < n) (certificate : expUpper x n ≤ U) :
    Real.exp (x : ℝ) ≤ (U : ℝ) := by
  have h := Real.exp_bound' (x := (x : ℝ)) (by exact_mod_cast hx)
    (by exact_mod_cast hx1) hn
  have he : (expUpper x n : ℝ) =
      (∑ i ∈ Finset.range n, (x : ℝ) ^ i / (i.factorial : ℝ)) +
        (x : ℝ) ^ n * (n + 1) / ((n.factorial : ℝ) * n) := by
    simp [expUpper, expPoly_cast]
  rw [← he] at h
  exact h.trans (by exact_mod_cast certificate)

/-- Range reduction combines separately proved log bounds, exactly. -/
theorem log_scale_upper (q r L Ltwo : ℝ) (k : ℕ)
    (hr : 0 < r) (hqr : q = (2 : ℝ) ^ k * r)
    (hrL : Real.log r ≤ L) (htwo : Real.log 2 ≤ Ltwo) :
    Real.log q ≤ (k : ℝ) * Ltwo + L := by
  rw [hqr, Real.log_mul (by positivity) hr.ne', Real.log_pow]
  exact add_le_add (mul_le_mul_of_nonneg_left htwo (Nat.cast_nonneg k)) hrL

#print axioms expPoly_cast
#print axioms log_le_of_expPoly
#print axioms exp_le_of_expUpper
#print axioms log_scale_upper

end AnalyticEnclosures
