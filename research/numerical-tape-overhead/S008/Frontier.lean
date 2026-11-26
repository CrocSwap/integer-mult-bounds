import S008.ProfileLimit

namespace S008.Frontier
open S008.NumericalCutoff S008.WholeProfile

private theorem two_times {n L cost e p:ℝ} (hn : 0≤n) (hexp:e+1≤p)
    (h : cost≤n*Real.sqrt L*(2:ℝ)^e) :
    2*cost≤n*Real.sqrt L*(2:ℝ)^p := by
  have h2 := Real.rpow_le_rpow_of_exponent_le (by norm_num : (1:ℝ)≤2) hexp
  rw [Real.rpow_add (by norm_num),Real.rpow_one] at h2
  have hs := mul_le_mul_of_nonneg_left h2 (mul_nonneg hn (Real.sqrt_nonneg L))
  linarith only [hs,h]

/-- Apply any finite exponent receipt after the explicit coefficient-60 threshold. -/
theorem natural_reciprocal (n cost q t:ℝ) (j : ℕ) (hq:2≤q) (ht:0<t)
    (floor : 1572864480 ≤ logTwo (logTwo n))
    (hroom: 2*(q*60)^3≤t+2) (hpow:t+2≤(2:ℝ)^j) (hj:(q*60)^3*(j:ℝ)≤t)
    (hn:(2:ℝ)^((2:ℝ)^t)≤n)
    (bill : let z := logTwo (logTwo n)
      cost≤n*Real.sqrt (logTwo n)*
        (2:ℝ)^(182+4*logTwo (z+2)+(479/8)*phi (z+2))) :
    cost≤n*(Real.log n)^((1/2:ℝ)+1/q) := by
  have hn0 := lt_of_lt_of_le (Real.rpow_pos_of_pos (show (0:ℝ)<2 by norm_num) _) hn
  have hz := length_gate n t hn
  have hinner := logTwo_mono (Real.rpow_pos_of_pos (show (0:ℝ)<2 by norm_num) _) hn
  rw [logTwo_two_rpow] at hinner
  have hell := lt_of_lt_of_le (Real.rpow_pos_of_pos (show (0:ℝ)<2 by norm_num) _) hinner
  have h2pos := Real.log_pos (by norm_num : (1:ℝ)<2)
  have hln : 0≤Real.log n := by
    unfold logTwo at hell
    exact (div_pos_iff_of_pos_right h2pos).mp hell |>.le
  have hhalf : (1/2:ℝ)≤Real.log 2 := by
    have h := Real.log_le_sub_one_of_pos (show (0:ℝ)<1/2 by norm_num)
    rw [Real.log_div (by norm_num) (by norm_num),Real.log_one] at h
    linarith
  have hb : logTwo n≤2*Real.log n := by
    unfold logTwo
    rw [div_le_iff₀ h2pos]
    nlinarith only [mul_nonneg hln (sub_nonneg.mpr hhalf)]
  have hc := two_times hn0.le (S008.ProfileLimit.outer_sixty floor) bill
  exact S008.InputClock63.reciprocal_clock n (logTwo n) (logTwo (logTwo n)) 60 q t cost j
    hn0.le hell (by norm_num) rfl hb hq (by linarith only [ht]) hroom hpow hj hz hc

def receipt (q t j:ℕ) : Prop :=
  1572864480≤t ∧ 2*(q*60)^3≤t+2 ∧ t+2≤2^j ∧ (q*60)^3*j≤t

theorem table_receipts :
    receipt 10 7128000000 33 ∧ receipt 100 9504000000000 44 ∧
    receipt 1000 11664000000000000 54 ∧ receipt 10000 13824000000000000000 64 ∧
    receipt 100000 15984000000000000000000 74 := by
  norm_num [receipt]

end S008.Frontier
