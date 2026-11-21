import ShiftedCarrier
import Mathlib.Analysis.Convex.SpecificFunctions.Basic
import Mathlib.Data.Nat.Prime.Basic

namespace CarrierInputFloor
open Set

theorem exp_chord (z : ℝ) (hz : 0≤z) (cap : z≤5000000000000000) :
    (2:ℝ)^(z/100000000000000) ≤ 1+z/4 := by
  let f := z/5000000000000000
  have h₀ : 0 ≤ f := by dsimp [f]; positivity
  have h₁ : 0 ≤ 1-f := by dsimp [f]; linarith
  have h := (convexOn_rpow_left (by norm_num : (0:ℝ)<2)).2 (x:=0) (y:=50)
    (mem_univ _) (mem_univ _) h₁ h₀ (by ring : 1-f+f=1)
  simp only [smul_eq_mul,mul_zero,zero_add,Real.rpow_zero,mul_one] at h
  have hp : (2:ℝ)^(50:ℝ) = 1125899906842624 := by norm_num
  rw [hp] at h
  dsimp [f] at h
  have eqn : z/5000000000000000*50 = z/100000000000000 := by ring
  rw [eqn] at h
  linarith

/-- These are the maximal-width and least-axis bounds in the pinned outer
rectangle. They already rule out a full family of distinct fine primes. -/
theorem impossible_geometry {p z widths axes : ℝ} (hp : 64 ≤ p) (hz : 6 ≤ z)
    (cap : z ≤ 5000000000000000)
    (width : widths ≤ 1+(1/3+6/p)*(2:ℝ)^(z/100000000000000))
    (axis : (2:ℝ)^((1-1/100000000000000)*z-1) ≤ axes) :
    (2:ℝ)^widths < axes := by
  have hy : 1/3+6/p ≤ (1:ℝ)/2 := by
    have h : 6/p ≤ (1:ℝ)/6 := by rw [div_le_div_iff₀ (by linarith) (by norm_num)]; linarith
    linarith
  have hch := exp_chord z (by linarith) cap
  have hw := mul_le_mul hy hch (by positivity) (by norm_num : (0:ℝ)≤1/2)
  have h : widths < (1-1/100000000000000)*z-1 := by linarith
  exact (Real.rpow_lt_rpow_of_exponent_lt (by norm_num : (1:ℝ)<2) h).trans_le axis

/-- The catalogue supplies finitely many nonzero integers. Their positive
absolute product D yields an effective finite prime with no common divisor. -/
theorem finite_prime (D : ℕ) (hd : 0<D) :
    ∃ q : ℕ, q.Prime ∧ 2<q ∧ q≤2*D+1 ∧ ¬ q∣D := by
  let n := 2*D+1
  have hn : n ≠ 1 := by dsimp [n]; omega
  have hpos : 0<n := by dsimp [n]; omega
  let q := n.minFac
  have hq : q.Prime := Nat.minFac_prime hn
  have hdiv : q∣n := Nat.minFac_dvd _
  have hq2 : q ≠ 2 := by
    intro he
    rw [he] at hdiv
    obtain ⟨k,hk⟩ := hdiv
    dsimp [n] at hk
    omega
  refine ⟨q,hq,by have := hq.two_le; omega,Nat.le_of_dvd hpos hdiv,?_⟩
  intro hv
  have ht : q ∣ 2*D := dvd_mul_of_dvd_right hv 2
  have h₁ : q ∣ 1 := by
    change q∣2*D+1 at hdiv
    exact (Nat.dvd_add_iff_right ht).mpr hdiv
  have hh := Nat.le_of_dvd Nat.one_pos h₁
  have := hq.two_le
  omega

#print axioms exp_chord
#print axioms impossible_geometry
#print axioms finite_prime
end CarrierInputFloor
