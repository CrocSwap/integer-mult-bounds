import S008.Packing
import S008.WholeProfile

namespace S008.InputClock
open S008.NumericalCutoff S008.Packing

set_option exponentiation.threshold 8192

private theorem log_two_nat_pow (k : ℕ) : logTwo ((2:ℝ)^k) = (k:ℝ) := by
  simpa only [Real.rpow_natCast] using logTwo_two_rpow (k:ℝ)

/-- Transfer the ceiling-division geometry to the real input-size branches. -/
theorem input_geometry {n : ℕ} (hn : 2^48<n) :
    (addressWidth n:ℝ) ≤ logTwo n ∧ logTwo n < 2*(addressWidth n:ℝ) ∧
    5 ≤ logTwo (logTwo n) ∧
    (addressWidth n < 2^4096 → logTwo (logTwo n) ≤ 4097) ∧
    (2^4096 ≤ addressWidth n → 4096 ≤ logTwo (logTwo n)) := by
  obtain ⟨h32,hb,hN,_⟩ := physical_sizes hn
  have hlNat : 2^(addressWidth n)<n := hN
  have hl : (2:ℝ)^(addressWidth n) ≤ (n:ℝ) := by exact_mod_cast hlNat.le
  have huNat := Nat.le_pow_clog (by decide : 1<2) n
  change n ≤ 2^digitWidth n at huNat
  have hu : (n:ℝ) ≤ (2:ℝ)^(digitWidth n) := by exact_mod_cast huNat
  have lp := logTwo_mono (pow_pos (by norm_num : (0:ℝ)<2) _) hl
  rw [log_two_nat_pow] at lp
  have np : (0:ℝ)<(n:ℝ) := by exact_mod_cast (show 0<n by omega)
  have up := logTwo_mono np hu
  rw [log_two_nat_pow] at up
  have hbr : (digitWidth n:ℝ)<2*(addressWidth n:ℝ) := by exact_mod_cast hb
  have hr := lt_of_le_of_lt up hbr
  have h32r : (2:ℝ)^5 ≤ (addressWidth n:ℝ) := by exact_mod_cast h32
  have hs := logTwo_mono (pow_pos (by norm_num : (0:ℝ)<2) 5) (h32r.trans lp)
  rw [log_two_nat_pow] at hs
  have hlog_pos : 0 < logTwo n := lt_of_lt_of_le (pow_pos (by norm_num : (0:ℝ)<2) 5) (h32r.trans lp)
  refine ⟨lp,hr,by exact_mod_cast hs,?_,?_⟩
  · intro hk
    have hkr : (addressWidth n:ℝ) < (2:ℝ)^4096 := by exact_mod_cast hk
    have hr' : logTwo n ≤ (2:ℝ)^4097 := by
      rw [pow_succ]
      linarith only [hr,hkr]
    have hf := logTwo_mono hlog_pos hr'
    rw [log_two_nat_pow] at hf
    exact_mod_cast hf
  · intro hk
    have hkr : (2:ℝ)^4096 ≤ (addressWidth n:ℝ) := by exact_mod_cast hk
    have hf := logTwo_mono (pow_pos (by norm_num : (0:ℝ)<2) 4096) (hkr.trans lp)
    rw [log_two_nat_pow] at hf
    exact_mod_cast hf

theorem phi_mono {x y : ℝ} (hx : 0 ≤ x) (hxy : x ≤ y) : phi x ≤ phi y := by
  have hl := logTwo_mono (show 0<x+2 by linarith) (show x+2≤y+2 by linarith)
  have h0 : 0≤logTwo (x+2) := by
    unfold logTwo
    exact div_nonneg (Real.log_nonneg (by linarith)) (Real.log_nonneg (by norm_num))
  have hs : x^2 ≤ y^2 := by nlinarith [mul_nonneg (sub_nonneg.mpr hxy) (by linarith : 0≤y+x)]
  have hh := mul_le_mul hs hl h0 (sq_nonneg y)
  unfold phi
  exact Real.rpow_le_rpow (mul_nonneg (sq_nonneg x) h0) hh (by norm_num)



end S008.InputClock
