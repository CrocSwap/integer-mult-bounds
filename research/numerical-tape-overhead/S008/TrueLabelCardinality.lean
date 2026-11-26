import S008.TrueLabelCurve
import Mathlib.Data.Nat.Choose.Bounds

namespace S008.TrueLabel
open S008.NumericalCutoff

private theorem log_mul {a b : ℝ} (ha : 0<a) (hb : 0<b) :
    logTwo (a*b)=logTwo a+logTwo b := by
  unfold logTwo
  rw [Real.log_mul ha.ne' hb.ne']
  ring

private theorem log_pow (a : ℝ) (n : ℕ) : logTwo (a^n)=(n:ℝ)*logTwo a := by
  unfold logTwo
  rw [Real.log_pow]
  ring

private theorem hlog_small (d : ℕ) (hd : 2≤d) : 2*d≤2^d := by
  induction d, hd using Nat.le_induction with
  | base => decide
  | succ i hi ih =>
    rw [pow_succ]
    omega

/-- The source binomial and letter-cardinality formula implies the entire
    logarithmic invoice, without replacing log(t) by log(s+2). -/
theorem cardinals_to_true_letter {d h t : ℕ} {s σ incidence : ℝ}
    (hd : 16≤d) (hh : h=2*d-1) (ht : 1≤t)
    (htop : (t:ℝ)≤s/d^2+3) (hincidence0 : 0 ≤ incidence)
    (hincidence : incidence ≤ (h.choose d:ℝ)^(d+1) * ((2:ℝ)^t-1)^d * (t:ℝ)^(d*(d-1)))
    (hmass : (2:ℝ)^σ ≤ (2:ℝ)^33*(4+2*(h:ℝ)*((2:ℝ)^t)^h)*(1+incidence)) :
    σ+2 ≤ 3*s/d+(d:ℝ)^2*(logTwo t+3) := by
  have hhP : 1≤h := by omega
  have hPr : (1:ℝ)≤h := by exact_mod_cast hhP
  have htP : (1:ℝ)≤t := by exact_mod_cast ht
  have hpos : (0:ℝ)<h := by linarith
  have tpos : (0:ℝ)<t := by linarith
  have hchoose : (h.choose d:ℝ) ≤ (2:ℝ)^h := by exact_mod_cast Nat.choose_le_two_pow h d
  have one2 (n:ℕ) : (1:ℝ)≤2^n := one_le_pow₀ (by norm_num)
  have ha := pow_le_pow_left₀ (show (0:ℝ)≤h.choose d by positivity) hchoose (d+1)
  have hb := pow_le_pow_left₀ (sub_nonneg.mpr (one2 t))
    (show (2:ℝ)^t-1≤2^t by linarith) d
  let k := ((2:ℝ)^h)^(d+1)*((2:ℝ)^t)^d*(t:ℝ)^(d*(d-1))
  have hK : incidence≤k := by
    exact hincidence.trans (mul_le_mul_of_nonneg_right
      (mul_le_mul ha hb (pow_nonneg (sub_nonneg.mpr (one2 t)) d) (by positivity))
      (by positivity))
  have hk1 : 1≤k := by
    exact one_le_mul_of_one_le_of_one_le
      (one_le_mul_of_one_le_of_one_le (one_le_pow₀ (one2 h)) (one_le_pow₀ (one2 t)))
      (one_le_pow₀ htP)
  have hD : 4+2*(h:ℝ)*((2:ℝ)^t)^h ≤ 8*(h:ℝ)*((2:ℝ)^t)^h := by
    nlinarith only [one_le_mul_of_one_le_of_one_le hPr (one_le_pow₀ (one2 t) (n:=h))]
  have hm' : (2:ℝ)^σ ≤ ((2:ℝ)^37*(h:ℝ)*((2:ℝ)^t)^h)*k := by
    apply hmass.trans
    have hmult := mul_le_mul (mul_le_mul_of_nonneg_left hD (by norm_num : (0:ℝ)≤2^33))
      (show 1+incidence≤2*k by linarith only [hK,hk1]) (by linarith : 0≤1+incidence)
      (show 0≤(2:ℝ)^33*(8*(h:ℝ)*((2:ℝ)^t)^h) by positivity)
    calc
      (2:ℝ)^33*(4+2*(h:ℝ)*((2:ℝ)^t)^h)*(1+incidence) ≤ _ := hmult
      _ = ((2:ℝ)^37*(h:ℝ)*((2:ℝ)^t)^h)*k := by ring
  have hlog := logTwo_mono (Real.rpow_pos_of_pos (show (0:ℝ)<2 by norm_num) _) hm'
  rw [logTwo_two_rpow] at hlog
  dsimp only [k] at hlog
  have hl2 : logTwo (2:ℝ)=1 := by unfold logTwo; rw [div_self (Real.log_pos (by norm_num : (1:ℝ)<2)).ne']
  simp (disch:=positivity) only [log_mul,log_pow,hl2,mul_one,Nat.cast_add,Nat.cast_one,
    Nat.cast_mul,Nat.cast_sub (show 1≤d by omega)] at hlog
  have hsmall := hlog_small d (by omega)
  have hhr : (h:ℝ) = 2*(d:ℝ)-1 := by
    rw [hh,Nat.cast_sub (by omega : 1≤2*d)]
    push_cast
    ring
  have hhd : logTwo (2*(d:ℝ)-1) ≤ d := by
    have hp : (h:ℝ)≤2^(d:ℕ) := by exact_mod_cast (show h≤2^d by omega)
    have hx := logTwo_mono hpos hp
    rw [log_pow,hl2,mul_one,hhr] at hx
    exact hx
  rw [hhr] at hlog
  apply true_letter_invoice (by exact_mod_cast hd) htP htop hhd
  norm_num at hlog
  linarith only [hlog]

end S008.TrueLabel
