import Invoice

namespace ShiftedCarrier
open CarrierGuards

abbrev threshold (v : Bound) : ℕ := 4*v.ambient
noncomputable abbrev ratio (v : Bound) : ℝ := v.num/v.den

private theorem bits_mono {a b : ℝ} (ha : 0<a) (hle : a≤b) : bitsLog a ≤ bitsLog b :=
  div_le_div_of_nonneg_right (Real.log_le_log ha hle) (Real.log_nonneg (by norm_num : (1:ℝ)≤2))

private theorem bits_log_mul {a b : ℝ} (ha : 0<a) (hb : 0<b) :
    bitsLog (a*b) = bitsLog a + bitsLog b := by
  simp only [bitsLog, Real.log_mul ha.ne' hb.ne', add_div]

private theorem bits_log_pow (x : ℝ) (n : ℕ) : bitsLog (x^n) = n*bitsLog x := by
  simp only [bitsLog,Real.log_pow,mul_div_assoc]

theorem fraction_pow (x : ℝ) (hx : 0≤x) (n d : ℕ) (hd : 0<d) :
    (x^((n:ℝ)/d))^d = x^n := by
  have hd' : (d:ℝ)≠0 := by exact_mod_cast hd.ne'
  rw [←Real.rpow_natCast _ d,←Real.rpow_mul hx,div_mul_cancel₀ _ hd',Real.rpow_natCast]

theorem upper_power (x M n d : ℕ) (hd : 0<d) (h : x^n ≤ M^d) :
    (x:ℝ)^((n:ℝ)/d) ≤ M := by
  apply le_of_pow_le_pow_left₀ hd.ne' (Nat.cast_nonneg _)
  rw [fraction_pow _ (Nat.cast_nonneg x) n d hd]
  exact_mod_cast h

structure RealGuards (v : Bound) (C : ℝ) : Prop where
  floor_price : (v.ceiling:ℝ) ≤ (v.floor:ℝ) ^ ratio v
  shrink : (1-ratio v)*v.shift ≤ ratio v * bitsLog (threshold v) - bitsLog v.ceiling
  log_ceiling : bitsLog (threshold v) ≤ v.maxLog
  base_price : C*(v.shift+v.maxLog) ≤ v.logPower
  exit_price : ((16/15:ℝ)*2*(threshold v:ℝ)^C)*(ratio v)^v.logPower ≤ (3:ℝ)/4

theorem real_guards {v : Bound} {a d : ℕ} {C : ℝ} (g : valid v a d)
    (hd : 0<d) (hX : 1 ≤ threshold v) (hr : 0<v.ceiling) (hC : C≤(a:ℝ)/d) :
    RealGuards v C := by
  obtain ⟨hn,hn',hfloor,hshift,hamp,hlog,hbase,hprice⟩ := g
  have hden : 0<v.den := hn.trans hn'
  have hden' : (0:ℝ)<v.den := by exact_mod_cast hden
  have hd' : (0:ℝ)<d := by exact_mod_cast hd
  have hxr : (1:ℝ) ≤ threshold v := by exact_mod_cast hX
  have hxx : (0:ℝ)<threshold v := by linarith
  have hr' : (0:ℝ)<v.ceiling := by exact_mod_cast hr
  have htheta : 0≤ratio v := div_nonneg (Nat.cast_nonneg _) hden'.le
  refine ⟨?_,?_,?_,?_,?_⟩
  · apply le_of_pow_le_pow_left₀ hden.ne' (Real.rpow_nonneg (Nat.cast_nonneg _) _)
    rw [fraction_pow _ (Nat.cast_nonneg _) v.num v.den hden]
    exact_mod_cast hfloor
  · have h : (2:ℝ)^(v.shift*(v.den-v.num))*(v.ceiling:ℝ)^v.den ≤ (threshold v:ℝ)^v.num := by
      exact_mod_cast hshift
    have hm := bits_mono (by positivity : (0:ℝ)<2^(v.shift*(v.den-v.num))*(v.ceiling:ℝ)^v.den) h
    rw [bits_log_mul (by positivity) (pow_pos hr' _),bitsLog_pow_two,bits_log_pow,bits_log_pow,
      Nat.cast_mul,Nat.cast_sub hn'.le] at hm
    dsimp [ratio]
    field_simp
    nlinarith
  · have h : (threshold v:ℝ) ≤ (2:ℝ)^v.maxLog := by exact_mod_cast hlog
    simpa only [bitsLog_pow_two] using bits_mono hxx h
  · have h : (a:ℝ)*(v.shift+v.maxLog) ≤ d*v.logPower := by exact_mod_cast hbase
    have hc := mul_le_mul_of_nonneg_right hC (by positivity : 0≤(v.shift:ℝ)+v.maxLog)
    apply hc.trans
    rw [div_mul_eq_mul_div,div_le_iff₀ hd']
    linarith
  · have amp := (Real.rpow_le_rpow_of_exponent_le hxr hC).trans (upper_power (threshold v) v.amplitude a d hd hamp)
    have bounded := mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_left amp
      (by norm_num : (0:ℝ)≤16/15*2)) (pow_nonneg htheta v.logPower)
    apply bounded.trans
    have hh : 128*(v.amplitude:ℝ)*(v.num:ℝ)^v.logPower ≤ 45*(v.den:ℝ)^v.logPower := by exact_mod_cast hprice
    dsimp [ratio]
    rw [div_pow,mul_div_assoc',div_le_div_iff₀ (pow_pos hden' _) (by norm_num : (0:ℝ)<4)]
    linarith

#print axioms real_guards
end ShiftedCarrier
