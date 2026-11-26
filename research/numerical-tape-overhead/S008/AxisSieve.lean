import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Data.Nat.Prime.Basic
import Mathlib.Data.Nat.Choose.Sum
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp

namespace S008.AxisSieve

/-- At depth j, the sum of the retained band weights scaled by 2^j. -/
def degreeNumer : ℕ → ℕ
  | 0 => 0
  | j+1 => 2 * degreeNumer j + 2*(4+2*j)

theorem degree_tail (j : ℕ) :
    degreeNumer j + (12+4*j) = 12 * 2^j := by
  induction j with
  | zero => decide
  | succ j ih =>
    simp only [degreeNumer, pow_succ]
    omega

/-- Evaluate the even Bonferroni truncation when exactly n distinct primes divide an integer. -/
def truncated (n d : ℕ) : ℤ :=
  ∑ i ∈ Finset.range (2*d+1), (-1:ℤ)^i * (n.choose i : ℤ)

theorem bonferroni_indicator (n d : ℕ) :
    (if n = 0 then (1:ℤ) else 0) ≤ truncated n d ∧
    truncated n d - (if n = 0 then (1:ℤ) else 0) ≤ (n.choose (2*d+1) : ℤ) := by
  cases n with
  | zero =>
    simp [truncated, Finset.sum_range_succ']
  | succ n =>
    have hx : truncated (n+1) d = (n.choose (2*d) : ℤ) := by
      unfold truncated
      rw [Int.alternating_sum_range_choose_eq_choose]
      simp [pow_mul]
    rw [hx]
    simp only [Nat.succ_ne_zero, ↓reduceIte, sub_zero, Nat.choose_succ_succ',
      Nat.cast_add]
    omega

/-- Exact deviation of the interval's count of multiples, including a negative left endpoint. -/
theorem interval_divisor_discrepancy (a y d : ℤ) (hd : 0 < d) :
    |d*(((a+y)/d)-(a/d))-y| < d := by
  have hx := Int.emod_add_mul_ediv a d
  have hxy := Int.emod_add_mul_ediv (a+y) d
  have he : d*(((a+y)/d)-(a/d))-y = a%d-(a+y)%d := by nlinarith
  rw [he, abs_lt]
  have h1 := Int.emod_nonneg a hd.ne'
  have h2 := Int.emod_nonneg (a+y) hd.ne'
  have h3 := Int.emod_lt_of_pos a hd
  have h4 := Int.emod_lt_of_pos (a+y) hd
  omega

/-- A positive band indicator, its even truncation and the next symmetric term. -/
structure Band where
  h : ℝ
  upper : ℝ
  err : ℝ
  hnonneg : 0 ≤ h
  hle : h ≤ upper
  hgap : upper - h ≤ err

def actual : List Band → ℝ
  | [] => 1
  | r :: rest => r.h * actual rest

def upper : List Band → ℝ
  | [] => 1
  | r :: rest => r.upper * upper rest

/-- Every product summand involves just one selected error factor. -/
def oneError : List Band → ℝ
  | [] => 0
  | r :: rs => r.err * upper rs + r.upper * oneError rs

theorem product_bounds (rs : List Band) : 0 ≤ actual rs ∧ actual rs ≤ upper rs := by
  induction rs with
  | nil => simp [actual, upper]
  | cons r rest ih =>
    exact ⟨mul_nonneg r.hnonneg ih.1,
      mul_le_mul r.hle ih.2 ih.1 (le_trans r.hnonneg r.hle)⟩

theorem single_omission (rs : List Band) : upper rs - oneError rs ≤ actual rs := by
  induction rs with
  | nil => simp [upper, actual, oneError]
  | cons r rest ih =>
    obtain ⟨hn, hu⟩ := product_bounds rest
    have he : 0 ≤ r.err := le_trans (sub_nonneg.mpr r.hle) r.hgap
    have h1 := mul_le_mul_of_nonneg_right r.hgap hn
    have h2 := mul_le_mul_of_nonneg_left hu he
    have h3 := mul_le_mul_of_nonneg_left ih (le_trans r.hnonneg r.hle)
    simp only [upper, oneError, actual]
    nlinarith

private def smallPrimes := (List.range 257).filter (fun p => decide (Nat.Prime p))

private def primeBlock (s n : ℕ) := (List.range' s n).filter (fun p => decide (Nat.Prime p))

private theorem primeBlock_append (s m n : ℕ) :
    primeBlock s (m+n)=primeBlock s m ++ primeBlock (s+m) n := by
  unfold primeBlock
  rw [← List.range'_append_1, List.filter_append]

private theorem block_0 : primeBlock 0 16 = [2, 3, 5, 7, 11, 13] := by
  decide +kernel

private theorem block_16 : primeBlock 16 16 = [17, 19, 23, 29, 31] := by
  decide +kernel

private theorem block_32 : primeBlock 32 16 = [37, 41, 43, 47] := by
  decide +kernel

private theorem block_48 : primeBlock 48 16 = [53, 59, 61] := by
  decide +kernel

private theorem block_64 : primeBlock 64 16 = [67, 71, 73, 79] := by
  decide +kernel

private theorem block_80 : primeBlock 80 16 = [83, 89] := by
  decide +kernel

private theorem block_96 : primeBlock 96 16 = [97, 101, 103, 107, 109] := by
  decide +kernel

private theorem block_112 : primeBlock 112 16 = [113, 127] := by
  decide +kernel

private theorem block_128 : primeBlock 128 16 = [131, 137, 139] := by
  decide +kernel

private theorem block_144 : primeBlock 144 16 = [149, 151, 157] := by
  decide +kernel

private theorem block_160 : primeBlock 160 16 = [163, 167, 173] := by
  decide +kernel

private theorem block_176 : primeBlock 176 16 = [179, 181, 191] := by
  decide +kernel

private theorem block_192 : primeBlock 192 16 = [193, 197, 199] := by
  decide +kernel

private theorem block_208 : primeBlock 208 16 = [211, 223] := by
  decide +kernel

private theorem block_224 : primeBlock 224 16 = [227, 229, 233, 239] := by
  decide +kernel

private theorem block_240 : primeBlock 240 16 = [241, 251] := by
  decide +kernel

private theorem block_256 : primeBlock 256 1 = [] := by
  decide +kernel

private theorem assembled_primes : smallPrimes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251] := by
  unfold smallPrimes
  rw [List.range_eq_range']
  change primeBlock 0 257 = _
  rw [show primeBlock 0 257 = primeBlock 0 16 ++ primeBlock 16 241 from primeBlock_append 0 16 241, block_0]
  rw [show primeBlock 16 241 = primeBlock 16 16 ++ primeBlock 32 225 from primeBlock_append 16 16 225, block_16]
  rw [show primeBlock 32 225 = primeBlock 32 16 ++ primeBlock 48 209 from primeBlock_append 32 16 209, block_32]
  rw [show primeBlock 48 209 = primeBlock 48 16 ++ primeBlock 64 193 from primeBlock_append 48 16 193, block_48]
  rw [show primeBlock 64 193 = primeBlock 64 16 ++ primeBlock 80 177 from primeBlock_append 64 16 177, block_64]
  rw [show primeBlock 80 177 = primeBlock 80 16 ++ primeBlock 96 161 from primeBlock_append 80 16 161, block_80]
  rw [show primeBlock 96 161 = primeBlock 96 16 ++ primeBlock 112 145 from primeBlock_append 96 16 145, block_96]
  rw [show primeBlock 112 145 = primeBlock 112 16 ++ primeBlock 128 129 from primeBlock_append 112 16 129, block_112]
  rw [show primeBlock 128 129 = primeBlock 128 16 ++ primeBlock 144 113 from primeBlock_append 128 16 113, block_128]
  rw [show primeBlock 144 113 = primeBlock 144 16 ++ primeBlock 160 97 from primeBlock_append 144 16 97, block_144]
  rw [show primeBlock 160 97 = primeBlock 160 16 ++ primeBlock 176 81 from primeBlock_append 160 16 81, block_160]
  rw [show primeBlock 176 81 = primeBlock 176 16 ++ primeBlock 192 65 from primeBlock_append 176 16 65, block_176]
  rw [show primeBlock 192 65 = primeBlock 192 16 ++ primeBlock 208 49 from primeBlock_append 192 16 49, block_192]
  rw [show primeBlock 208 49 = primeBlock 208 16 ++ primeBlock 224 33 from primeBlock_append 208 16 33, block_208]
  rw [show primeBlock 224 33 = primeBlock 224 16 ++ primeBlock 240 17 from primeBlock_append 224 16 17, block_224]
  rw [show primeBlock 240 17 = primeBlock 240 16 ++ primeBlock 256 1 from primeBlock_append 240 16 1, block_240]
  rw [block_256]
  rfl

theorem exact_small_prime_product :
    smallPrimes.length = 54 ∧
    smallPrimes.prod < 10 * (smallPrimes.map (fun p => p-1)).prod := by
  rw [assembled_primes]
  decide +kernel

theorem bonferroni_relative :
    5*(8/5:ℚ)^5/120 + 7*(9/5:ℚ)^7/5040 + 12*(11/5:ℚ)^9/362880
      + 64*(3:ℚ)^11/39916800 + 64*(3:ℚ)^13/(6227020800*(1-9/(14*15:ℚ))) < 7/8 := by
  norm_num

private theorem log_two_lower : (1/2 : ℝ) ≤ Real.log 2 := by
  have h := Real.log_le_sub_one_of_pos (show (0 : ℝ) < 1 / 2 by norm_num)
  rw [Real.log_div (by norm_num) (by norm_num), Real.log_one] at h
  linarith

/-- Squared real scales times the exponential loss decrease from the initial threshold. -/
theorem decreasing_squared {t c : ℝ} (ht : 32 ≤ t) (hc : 1/8 ≤ c) :
    t^2 * (2 : ℝ)^(-c*t) ≤ 32^2 * (2 : ℝ)^(-c*32) := by
  have htpos : 0 < t := by linarith
  have hscale := Real.log_le_sub_one_of_pos (show (0:ℝ) < t/32 by positivity)
  rw [Real.log_div htpos.ne' (by norm_num)] at hscale
  have hcpos : 0 ≤ c := by linarith
  have hcl : (1/16:ℝ) ≤ c * Real.log 2 := by
    have h := mul_le_mul hc log_two_lower (by norm_num) hcpos
    linarith
  have hratio : 2*(Real.log t - Real.log 32) ≤ (t-32)*c*Real.log 2 := by
    nlinarith [mul_nonneg (sub_nonneg.mpr ht) (sub_nonneg.mpr hcl)]
  have hin := Real.exp_le_exp.mpr (show
      2*Real.log t + Real.log 2*(-c*t)
      ≤ 2*Real.log 32 + Real.log 2*(-c*32) by linarith)
  have ht2 : Real.exp (2*Real.log t) = t^2 := by
    rw [two_mul, Real.exp_add, Real.exp_log htpos, pow_two]
  have hb2 : Real.exp (2*Real.log (32:ℝ)) = 32^2 := by
    rw [two_mul, Real.exp_add, Real.exp_log (by norm_num), pow_two]
  rwa [Real.exp_add, Real.exp_add, ht2, hb2,
    ← Real.rpow_def_of_pos (by norm_num : (0:ℝ)<2),
    ← Real.rpow_def_of_pos (by norm_num : (0:ℝ)<2)] at hin


theorem leading_ratio {t : ℝ} (ht : 32 ≤ t) :
    (3/2) * (11*t/8)^2 * (2:ℝ)^(-(3/8:ℝ)*t) ≤ 363/512 := by
  have h := decreasing_squared (c:=3/8) ht (by norm_num)
  norm_num at h
  rw [neg_mul]
  nlinarith

theorem terminal_ratio {t : ℝ} (ht : 32 ≤ t) :
    3 * (11*t/8)^2 * (2:ℝ)^(-(17:ℝ)*t) < 1/1024 := by
  have h := decreasing_squared (c:=1) ht (by norm_num)
  norm_num at h
  have hex : (2:ℝ)^(-(17:ℝ)*t) ≤ 2^(-t) :=
    Real.rpow_le_rpow_of_exponent_le (by norm_num) (by linarith)
  nlinarith [mul_le_mul_of_nonneg_left hex (sq_nonneg t)]

theorem quartic_loss {t : ℝ} (ht : 0 ≤ t) :
    t^4 * (2:ℝ)^(-t/8) ≤ 64^4 := by
  have flex : t ≤ 64*(2:ℝ)^(t/32) := by
    have h := Real.add_one_le_exp (Real.log 2 * (t/32))
    rw [← Real.rpow_def_of_pos (by norm_num : (0:ℝ)<2)] at h
    nlinarith [mul_nonneg ht (sub_nonneg.mpr log_two_lower)]
  have h4 := pow_le_pow_left₀ ht flex 4
  have hcancel : ((2:ℝ)^(t/32))^4 * 2^(-t/8) = 1 := by
    rw [← Real.rpow_natCast, ← Real.rpow_mul (by norm_num : (0:ℝ)≤2),
      ← Real.rpow_add (by norm_num : (0:ℝ)<2)]
    convert Real.rpow_zero 2 using 2
    norm_num
    ring
  have h := mul_le_mul_of_nonneg_right h4
    (Real.rpow_nonneg (by norm_num : (0:ℝ)≤2) (-t/8))
  simpa [mul_pow, mul_assoc, hcancel] using h

theorem discrepancy_ratio {t : ℝ} (ht : 32 ≤ t) :
    3*t*(11*t/8)^3 * (2:ℝ)^(-(44:ℝ)-t/8) < 1/1024 := by
  have h := quartic_loss (show 0 ≤ t by linarith)
  have hr : (2:ℝ)^(-(44:ℝ)-t/8) = (1/(2^44):ℝ) * 2^(-t/8) := by
    rw [show (-(44:ℝ)-t/8) = -44 + -t/8 by ring, Real.rpow_add (by norm_num : (0:ℝ)<2)]
    norm_num
  rw [hr]
  nlinarith

/-- The interval survives whenever the combinatorial sieve supplies the three proved losses. -/
theorem positive_survivor {t expected relativeObserved : ℝ} (ht : 32 ≤ t)
    (hmain : 1 ≤ expected)
    (hlower : expected
      - (3*t*(11*t/8)^3*(2:ℝ)^(-(44:ℝ)-t/8))
      - ((3/2)*(11*t/8)^2*(2:ℝ)^(-(3/8:ℝ)*t))
      - (3*(11*t/8)^2*(2:ℝ)^(-(17:ℝ)*t)) ≤ relativeObserved) :
    0 < relativeObserved := by
  linarith [leading_ratio ht, terminal_ratio ht, discrepancy_ratio ht]

end S008.AxisSieve
