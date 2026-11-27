import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp

namespace S008.NumericalCutoff

noncomputable def logTwo (z : ℝ) : ℝ := Real.log z / Real.log 2
noncomputable def phi (x : ℝ) : ℝ := (x ^ 2 * logTwo (x + 2)) ^ (1 / 3 : ℝ)

private theorem half_le_log_two : (1/2 : ℝ) ≤ Real.log 2 := by
  have h := Real.log_le_sub_one_of_pos (show (0 : ℝ) < 1 / 2 by norm_num)
  rw [Real.log_div (by norm_num) (by norm_num), Real.log_one] at h
  linarith

/-- One exact endpoint comparison covers every subsequent positive real input. -/
theorem log_control (D T : ℝ) (j : ℕ) (hD : 0 < D) (hT : 0 < T)
    (hroom : 2 * D ≤ T + 2) (htop : T + 2 ≤ (2 : ℝ)^j)
    (hweight : D * (j : ℝ) ≤ T) {x : ℝ} (hx : T ≤ x) :
    D * logTwo (x+2) ≤ x := by
  have h2 : 0 < Real.log (2 : ℝ) := Real.log_pos (by norm_num)
  have hTp : 0 < T+2 := by linarith
  have hxp : 0 < x+2 := by linarith
  have hlog := Real.log_le_log hTp htop
  rw [Real.log_pow] at hlog
  have ht := Real.log_le_sub_one_of_pos (div_pos hxp hTp)
  rw [Real.log_div (ne_of_gt hxp) (ne_of_gt hTp)] at ht
  have hquot : (x+2)/(T+2)-1 = (x-T)/(T+2) := by
    field_simp
    ring
  rw [hquot] at ht
  have hs : D ≤ (T+2)*Real.log 2 := by
    nlinarith [mul_nonneg (le_of_lt hTp) (sub_nonneg.mpr half_le_log_two)]
  have hh : D*((x-T)/(T+2)) ≤ (x-T)*Real.log 2 := by
    rw [← mul_div_assoc, div_le_iff₀ hTp]
    nlinarith [mul_nonneg (sub_nonneg.mpr hx) (sub_nonneg.mpr hs)]
  have hw := mul_le_mul_of_nonneg_right hweight (le_of_lt h2)
  have hw' := mul_le_mul_of_nonneg_left hlog (le_of_lt hD)
  have he := mul_le_mul_of_nonneg_left ht (le_of_lt hD)
  unfold logTwo
  rw [← mul_div_assoc, div_le_iff₀ h2]
  nlinarith

theorem phi_cube {x : ℝ} (hx : 0 ≤ x) :
    phi x ^ 3 = x ^ 2 * logTwo (x+2) := by
  have harg : 0 ≤ x^2 * logTwo (x+2) := by
    unfold logTwo
    exact mul_nonneg (sq_nonneg x) (div_nonneg (Real.log_nonneg (by linarith))
      (Real.log_nonneg (by norm_num)))
  unfold phi
  rw [← Real.rpow_natCast, ← Real.rpow_mul harg]
  norm_num

/-- The cubic comparison has no unknown constant. -/
theorem excess_from_log (C q x : ℝ) (hq : 0 < q) (hx : 0 ≤ x)
    (h : (q*C)^3 * logTwo (x+2) ≤ x) : C * phi x ≤ x/q := by
  have hc : (q*C*phi x)^3 ≤ x^3 := by
    rw [mul_pow, phi_cube hx]
    nlinarith [mul_le_mul_of_nonneg_left h (sq_nonneg x)]
  rw [le_div_iff₀ hq]
  have hle : q*C*phi x ≤ x := by
    exact le_of_pow_le_pow_left₀ (by norm_num : (3:ℕ) ≠ 0) hx hc
  linarith



theorem two_log_cancel {L : ℝ} (hL : 0 < L) :
    (2 : ℝ) ^ logTwo L = L := by
  have h2 : Real.log 2 ≠ 0 := ne_of_gt (Real.log_pos (by norm_num))
  rw [Real.rpow_def_of_pos (by norm_num), logTwo]
  have hh : Real.log 2 * (Real.log L / Real.log 2) = Real.log L := by field_simp
  rw [hh, Real.exp_log hL]

theorem multiplication_clock (n L C q T cost : ℝ) (j : ℕ)
    (hn : 0 ≤ n) (hL : 0 < L) (hC : 0 < C) (hq : 0 < q)
    (hT : 0 < T) (hroom : 2 * (q*C)^3 ≤ T + 2)
    (htop : T + 2 ≤ (2 : ℝ)^j) (hweight : (q*C)^3 * (j:ℝ) ≤ T)
    (hsize : T ≤ logTwo L)
    (hclock : cost ≤ n * Real.sqrt L * (2 : ℝ)^(C * phi (logTwo L))) :
    cost ≤ n * L ^ ((1/2:ℝ)+1/q) := by
  have hg := log_control ((q*C)^3) T j (by positivity) hT hroom htop hweight hsize
  have hd := excess_from_log C q (logTwo L) hq (by linarith) hg
  have hp := Real.rpow_le_rpow_of_exponent_le (show (1:ℝ) ≤ 2 by norm_num) hd
  have hpow : (2:ℝ)^(logTwo L / q) = L^(1/q) := by
    rw [div_eq_mul_one_div, Real.rpow_mul (by norm_num : (0:ℝ) ≤ 2), two_log_cancel hL]
  rw [hpow] at hp
  calc
    cost ≤ n * Real.sqrt L * (2 : ℝ)^(C * phi (logTwo L)) := hclock
    _ ≤ n * Real.sqrt L * L ^ (1/q) :=
      mul_le_mul_of_nonneg_left hp (mul_nonneg hn (Real.sqrt_nonneg L))
    _ = n * L ^ ((1/2:ℝ)+1/q) := by
      rw [Real.sqrt_eq_rpow, Real.rpow_add hL, mul_assoc]

/-- The 198-profile threshold, quantified over every later real scale and clock. -/

theorem logTwo_mono {v w : ℝ} (hv : 0 < v) (h : v ≤ w) : logTwo v ≤ logTwo w :=
  div_le_div_of_nonneg_right (Real.log_le_log hv h) (Real.log_nonneg (by norm_num))

theorem logTwo_two_rpow (z : ℝ) : logTwo ((2:ℝ)^z) = z := by
  unfold logTwo
  rw [Real.log_rpow (by norm_num)]
  have hn : Real.log 2 ≠ 0 := ne_of_gt (Real.log_pos (by norm_num))
  field_simp

theorem length_gate (n t : ℝ) (hn : (2:ℝ)^((2:ℝ)^t) ≤ n) :
    t ≤ logTwo (logTwo n) := by
  have hinner := logTwo_mono (Real.rpow_pos_of_pos (show (0:ℝ)<2 by norm_num) _) hn
  rw [logTwo_two_rpow] at hinner
  have houter := logTwo_mono (Real.rpow_pos_of_pos (show (0:ℝ)<2 by norm_num) _) hinner
  rwa [logTwo_two_rpow] at houter


end S008.NumericalCutoff
