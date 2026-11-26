import S008.InputClock
import S008.ThreeSlope

namespace S008.InputClock63
open S008.NumericalCutoff S008.WholeProfile S008.Packing S008.InputClock

noncomputable def boxExponent (z:ℝ) : ℝ :=
  182+4*logTwo (z+2)+(499/8)*phi (z+2)

private theorem rpow_fixed (u v:ℝ) (h:u≤v) : (2:ℝ)^u ≤ (2:ℝ)^v :=
  Real.rpow_le_rpow_of_exponent_le (by norm_num) h

/-- Analytical join for the alternative fixed guard, with the exact natural input geometry. -/
theorem all_input_clock {n : ℕ} (hn : 2≤n) (cost : ℝ)
    (raw : n≤2^48 → cost ≤ (n:ℝ)*(2:ℝ)^(60:ℝ))
    (dyadic : 2^48<n → addressWidth n<2^4096 →
      cost ≤ (n:ℝ)*Real.sqrt (logTwo n)*(2:ℝ)^(61+(3/2)*logTwo (logTwo n)))
    (coprime : 2^48<n → 2^4096≤addressWidth n →
      cost ≤ (n:ℝ)*Real.sqrt (logTwo n)*(2:ℝ)^(boxExponent (logTwo (logTwo n)))) :
    cost ≤ (n:ℝ)*Real.sqrt (1+logTwo n)*(2:ℝ)^(63*phi (logTwo (1+logTwo n))) := by
  let ell := logTwo (n:ℝ)
  let x := logTwo (1+ell)
  let z := logTwo ell
  have hn0 : (0:ℝ)≤n := Nat.cast_nonneg n
  have nn : (2:ℝ) ≤ n := by exact_mod_cast hn
  have hlog2 : logTwo 2 = 1 := div_self (ne_of_gt (Real.log_pos (by norm_num)))
  have ell1 : 1 ≤ ell := by simpa only [hlog2] using logTwo_mono (by norm_num : (0:ℝ)<2) nn
  have x1 : 1 ≤ x := by
    have h := logTwo_mono (by norm_num : (0:ℝ)<2) (show 2≤1+ell by linarith)
    simpa only [hlog2] using h
  have hz : z ≤ x := logTwo_mono (by linarith : 0<ell) (by linarith : ell≤1+ell)
  have hz0 : 0≤z := by
    unfold z logTwo
    exact div_nonneg (Real.log_nonneg ell1) (Real.log_nonneg (by norm_num))
  have hphi := phi_mono hz0 hz
  have hroot : 1 ≤ Real.sqrt (1+ell) := by
    calc
      (1:ℝ) = Real.sqrt 1 := by simp
      _ ≤ Real.sqrt (1+ell) := Real.sqrt_le_sqrt (by linarith)
  have hscale : (n:ℝ) ≤ (n:ℝ)*Real.sqrt (1+ell) := by
    simpa only [mul_one] using mul_le_mul_of_nonneg_left hroot hn0
  have hs := mul_le_mul_of_nonneg_left
    (Real.sqrt_le_sqrt (show ell≤1+ell by linarith)) hn0
  have H (e:ℝ) (he:e≤63*phi z) : (n:ℝ)*Real.sqrt ell*(2:ℝ)^e ≤
      (n:ℝ)*Real.sqrt (1+ell)*(2:ℝ)^(63*phi x) :=
    mul_le_mul hs (rpow_fixed _ _ (by linarith only [he,hphi]))
      (Real.rpow_nonneg (by norm_num) _) (mul_nonneg hn0 (Real.sqrt_nonneg _))
  by_cases hsmall : n≤2^48
  · exact (raw hsmall).trans (mul_le_mul hscale (rpow_fixed _ _ (ThreeSlope.small_excess x1))
      (Real.rpow_nonneg (by norm_num) _) (mul_nonneg hn0 (Real.sqrt_nonneg _)))
  have hlarge := Nat.lt_of_not_ge hsmall
  obtain ⟨_,_,z5,zm,zb⟩ := input_geometry hlarge
  by_cases hm : addressWidth n<2^4096
  · exact (dyadic hlarge hm).trans (H _ (ThreeSlope.dyadic_middle z5 (zm hm)))
  · have hh := Nat.le_of_not_gt hm
    have he := ThreeSlope.coprime_excess (zb hh)
    exact (coprime hlarge hh).trans (H _ (by unfold boxExponent; linarith only [he]))

/-- For each reciprocal exponent a finite integer comparison gives a natural-log unit clock. -/
theorem reciprocal_clock (n L z C q t cost : ℝ) (j : ℕ)
    (hn : 0≤n) (hL : 0<L) (hC:0<C) (hz : z=logTwo L)
    (hl : L ≤ 2*Real.log n) (hq : 2≤q) (ht : 0<t)
    (hroom : 2*(q*C)^3 ≤ t+2) (htop : t+2 ≤ (2:ℝ)^j)
    (hweight : (q*C)^3*(j:ℝ) ≤ t) (hx : t≤z)
    (hclock : 2*cost ≤ n*Real.sqrt L*(2:ℝ)^(C*phi z)) :
    cost ≤ n*(Real.log n)^((1/2:ℝ)+1/q) := by
  subst z
  have hqp : 0<q := by linarith
  have hh := multiplication_clock n L C q t (2*cost) j hn hL hC hqp ht
    hroom htop hweight hx hclock
  have hw0 : 0≤Real.log n := by linarith
  have hp0 : 0≤(1/2:ℝ)+1/q := by positivity
  have hp1 : (1/2:ℝ)+1/q ≤ 1 := by
    have := (div_le_div_iff₀ hqp (by norm_num : (0:ℝ)<2)).2
      (show (1:ℝ)*2 ≤ 1*q by linarith)
    linarith
  have ham := Real.rpow_le_rpow hL.le hl hp0
  rw [Real.mul_rpow (by norm_num) hw0] at ham
  have hb := rpow_fixed _ _ hp1
  rw [Real.rpow_one] at hb
  have hp := mul_le_mul_of_nonneg_right hb (Real.rpow_nonneg hw0 ((1/2:ℝ)+1/q))
  nlinarith only [hh,mul_le_mul_of_nonneg_left (ham.trans hp) hn]

end S008.InputClock63
