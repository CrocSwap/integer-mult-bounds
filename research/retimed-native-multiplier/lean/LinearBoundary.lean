import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.MeasureTheory.Integral.IntervalIntegral.Basic
import Mathlib.Tactic.Ring

namespace LinearBoundary

open scoped BigOperators
open MeasureTheory Set

noncomputable def edge (x r k c : ℝ) := r*((x*(k/r))^c-x^c)/c
noncomputable def slope (r k c : ℝ) := r*((k/r)^c-1)/c

theorem factor_edge {x r k c : ℝ} (hx : 0 ≤ x) (hr : 0 < r) (hk : 0 ≤ k) :
    edge x r k c = x^c * slope r k c := by
  unfold edge slope
  rw [Real.mul_rpow hx (div_nonneg hk hr.le)]
  ring

theorem same_moment {ι : Type*} (s : Finset ι) (p r k : ι → ℝ) {a b c : ℝ}
    (ha : 0 ≤ a) (hb : 0 ≤ b)
    (hr : ∀ i ∈ s, 0 < r i) (hk : ∀ i ∈ s, 0 ≤ k i) :
    b^c*(∑ i ∈ s, p i*edge a (r i) (k i) c) =
      a^c*(∑ i ∈ s, p i*edge b (r i) (k i) c) := by
  rw [Finset.mul_sum, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro i hi
  rw [factor_edge ha (hr i hi) (hk i hi), factor_edge hb (hr i hi) (hk i hi)]
  ring

/-- The ordinary axis-size integral at either boundary is a dilation of one fixed integral. -/
theorem sized_integral {x r q c : ℝ} (hx : 0 < x) (hq : 1 ≤ q) :
    (∫ u in x..x*q, r * u^(c-1)) =
      x^c * (∫ u in (1:ℝ)..q, r * u^(c-1)) := by
  have change := intervalIntegral.smul_integral_comp_mul_left
    (a := (1:ℝ)) (b := q) (fun u : ℝ => r * u^(c-1)) x
  simp only [smul_eq_mul, mul_one] at change
  rw [← change]
  have equiv : (∫ u in (1:ℝ)..q, r * (x*u)^(c-1)) =
      x^(c-1) * (∫ u in (1:ℝ)..q, r * u^(c-1)) := by
    rw [← intervalIntegral.integral_const_mul]
    apply intervalIntegral.integral_congr
    intro u hu
    rw [Set.uIcc_of_le hq] at hu
    change r * (x*u)^(c-1) = x^(c-1) * (r * u^(c-1))
    rw [Real.mul_rpow hx.le (le_trans zero_le_one hu.1)]
    ring
  rw [equiv, Real.rpow_sub_one hx.ne']
  field_simp

/-- Both finite measures use precisely the same linear size moment. -/
theorem actual_boundaries {ι : Type*} (s : Finset ι) (weight r ratio : ι → ℝ)
    {L U c : ℝ} (hL : 0<L) (hU : 0<U) (hratio : ∀ i∈s, 1≤ratio i) :
    U^c * (∑ i∈s, weight i * ∫ x in L..L*ratio i, r i*x^(c-1)) =
      L^c * (∑ i∈s, weight i * ∫ x in U..U*ratio i, r i*x^(c-1)) := by
  rw [Finset.mul_sum, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro i hi
  rw [sized_integral hL (hratio i hi), sized_integral hU (hratio i hi)]
  ring

#print axioms factor_edge
#print axioms same_moment
#print axioms sized_integral
#print axioms actual_boundaries

end LinearBoundary
