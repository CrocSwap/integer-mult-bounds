import Current741LogCheckpoints
import Mathlib.Analysis.SpecialFunctions.Log.Deriv

/-!
Real logarithm enclosure for the PR741 rank44 unit73/44, at z=29/117.
The generic remainder and cast proofs are byte-identical to the accepted
five-unit source. One new finite comparison bounds the six extra odd terms
and remainder by the exact source tail. The literal conclusion reuses the
finite checkpoint theorem with explicit Rat.cast_div/ofNat normalization.

Author-checked conditional context at7ee02b7:
kappa=1661202643272239/1000000000000000000=0.001661202643272239.
These two Real bounds do not establish a weighted native moment, either
fallback-bearing branch, supplier realization, bootstrap or all-size theorem.
Attribution: PR361 engine, PR741 profile, accepted analytic proof chain and
Mathlib's logarithm remainder theorem. Prepared with OpenAI assistance.
-/
namespace CurrentMain.Current741LogRealEnclosure
open scoped BigOperators
open Finset SelectedMomentLogCheckpoints Current741LogCheckpoints
set_option Elab.async false

private noncomputable def oddSum (z : ℝ) (n : Nat) : ℝ :=
  ∑ j ∈ range n, z^(2*j+1) / ((2*j+1 : Nat) : ℝ)

/-- Pair even and odd Taylor terms without expanding a 172-term expression. -/
private theorem paired_sum (z : ℝ) (m : Nat) :
    (∑ i ∈ range (2*m), z^(i+1) / ((i+1 : Nat) : ℝ)) -
      (∑ i ∈ range (2*m), (-z)^(i+1) / ((i+1 : Nat) : ℝ)) =
    2 * oddSum z m := by
  induction m with
  | zero => simp [oddSum]
  | succ m ih =>
    have ho : (-z)^(2*m+1) = -(z^(2*m+1)) := by
      simp [pow_add, pow_mul]
    have he : (-z)^(2*m+1+1) = z^(2*m+1+1) := by
      rw [show 2*m+1+1 = 2*(m+1) by omega]
      simp [pow_mul]
    rw [show 2*(m+1) = 2*m+1+1 by omega]
    simp only [Finset.sum_range_succ, oddSum] at ih ⊢
    rw [ho, he]
    simp only [neg_div]
    linarith

/-- The two signed library remainders give the required one-sided log bound. -/
private theorem log_auxiliary (z : ℝ) (hz : 0 ≤ z) (h1 : z < 1) :
    Real.log ((1+z)/(1-z)) ≤
      2 * oddSum z 86 + 2*z^173/(1-z) := by
  have hp := Real.abs_log_sub_add_sum_range_le
    (show |z| < 1 by simpa only [abs_of_nonneg hz] using h1) 172
  have hm := Real.abs_log_sub_add_sum_range_le
    (show |-z| < 1 by simpa only [abs_neg, abs_of_nonneg hz] using h1) 172
  simp only [abs_of_nonneg hz] at hp
  simp only [abs_neg, abs_of_nonneg hz, sub_neg_eq_add] at hm
  have hpair := paired_sum z 86
  have hlo := (abs_le.mp hp).1
  have hhi := (abs_le.mp hm).2
  have hplus : 1+z ≠ 0 := ne_of_gt (by linarith)
  have hminus : 1-z ≠ 0 := ne_of_gt (by linarith)
  rw [Real.log_div hplus hminus]
  simp only [Nat.cast_add, Nat.cast_one] at hpair
  change (∑ i ∈ range 172, z^(i+1) / ((i : ℝ)+1)) -
    (∑ i ∈ range 172, (-z)^(i+1) / ((i : ℝ)+1)) =
    2 * oddSum z 86 at hpair
  change -(z^173/(1-z)) ≤
    (∑ i ∈ range 172, z^(i+1)/((i : ℝ)+1)) + Real.log (1-z) at hlo
  change (∑ i ∈ range 172, (-z)^(i+1)/((i : ℝ)+1)) + Real.log (1+z) ≤
    z^173/(1-z) at hhi
  have hbound : Real.log (1+z) - Real.log (1-z) ≤
      2 * oddSum z 86 + 2 * (z^173/(1-z)) := by
    linarith only [hlo, hhi, hpair]
  simpa only [mul_div_assoc] using hbound

private theorem cast_power (n d exponent : Nat) :
    (powerFraction n d exponent : ℝ) = ((n : ℝ)/(d : ℝ))^exponent := by
  simp only [powerFraction, Rat.cast_div, Rat.cast_natCast, Nat.cast_pow, Rat.cast_pow, div_pow]

private theorem cast_term (n d j : Nat) :
    (logTerm n d j : ℝ) =
      ((n : ℝ)/(d : ℝ))^(2*j+1) / ((2*j+1 : Nat) : ℝ) := by
  simp only [logTerm, Rat.cast_div, cast_power, Rat.cast_natCast]

/-- Only eight additions are normalized at a time. -/
private theorem cast_block (n d start : Nat) (acc : Rat) :
    (logBlock n d start acc : ℝ) = (acc : ℝ) +
      ∑ j ∈ range 8, ((n : ℝ)/(d : ℝ))^(2*(start+j)+1) /
        ((2*(start+j)+1 : Nat) : ℝ) := by
  simp only [logBlock, Rat.cast_add, cast_term, Finset.sum_range_succ,
    Finset.sum_range_zero, add_zero, zero_add] <;> ring

private theorem cast_block_step (n d start : Nat) (acc : Rat)
    (hacc : (acc : ℝ) = oddSum ((n : ℝ)/(d : ℝ)) start) :
    (logBlock n d start acc : ℝ) = oddSum ((n : ℝ)/(d : ℝ)) (start+8) := by
  rw [cast_block, hacc]
  exact (Finset.sum_range_add _ start 8).symm

/-- Cast correspondence to the existing ten-block expression, not new evaluation. -/
private theorem cast_sum80 (n d : Nat) :
    (logSum80 n d : ℝ) = oddSum ((n : ℝ)/(d : ℝ)) 80 := by
  have h0 : ((0 : Rat) : ℝ) = oddSum ((n : ℝ)/(d : ℝ)) 0 := by
    simp [oddSum]
  have h8 := cast_block_step n d 0 0 h0
  have h16 := cast_block_step n d 8 _ h8
  have h24 := cast_block_step n d 16 _ h16
  have h32 := cast_block_step n d 24 _ h24
  have h40 := cast_block_step n d 32 _ h32
  have h48 := cast_block_step n d 40 _ h40
  have h56 := cast_block_step n d 48 _ h48
  have h64 := cast_block_step n d 56 _ h56
  have h72 := cast_block_step n d 64 _ h64
  have h80 := cast_block_step n d 72 _ h72
  exact h80

private def auxiliaryTail (n d : Nat) : Rat :=
  2 * (logTerm n d 80 + logTerm n d 81 + logTerm n d 82 +
    logTerm n d 83 + logTerm n d 84 + logTerm n d 85) +
  2 * powerFraction n d 173 / (1 - (n : Rat)/(d : Rat))

private def sourceTail (n d : Nat) : Rat :=
  2 * powerFraction n d 161 / (161 * (1 - powerFraction n d 2))

private theorem cast_auxiliaryTail (n d : Nat) :
    (auxiliaryTail n d : ℝ) =
    2 * (∑ j ∈ range 6, ((n : ℝ)/(d : ℝ))^(2*(80+j)+1) /
      ((2*(80+j)+1 : Nat) : ℝ)) +
    2 * ((n : ℝ)/(d : ℝ))^173 / (1 - (n : ℝ)/(d : ℝ)) := by
  simp only [auxiliaryTail, Rat.cast_add, Rat.cast_mul, Rat.cast_div,
    Rat.cast_sub, Rat.cast_natCast, Rat.cast_ofNat, cast_power, cast_term,
    Finset.sum_range_succ, Finset.sum_range_zero, add_zero, zero_add] <;> norm_num

private theorem cast_sourceTail (n d : Nat) :
    (sourceTail n d : ℝ) = 2 * ((n : ℝ)/(d : ℝ))^161 /
      (161 * (1 - ((n : ℝ)/(d : ℝ))^2)) := by
  simp only [sourceTail, Rat.cast_mul, Rat.cast_div, Rat.cast_sub,
    Rat.cast_ofNat, Rat.cast_one, cast_power]

private theorem cast_unitUpper (n d : Nat) :
    (unitUpper n d : ℝ) = 2 * oddSum ((n : ℝ)/(d : ℝ)) 80 +
      2 * ((n : ℝ)/(d : ℝ))^161 / (161 * (1 - ((n : ℝ)/(d : ℝ))^2)) := by
  change ((2 * logSum80 n d + sourceTail n d : Rat) : ℝ) = _
  simp only [Rat.cast_add, Rat.cast_mul, Rat.cast_ofNat, cast_sum80, cast_sourceTail]

private theorem tail_29_117 : auxiliaryTail 29 117 ≤ sourceTail 29 117 := by decide +kernel

private theorem unit_from_tail (n d : Nat)
    (hz : 0 ≤ (n : ℝ)/(d : ℝ)) (h1 : (n : ℝ)/(d : ℝ) < 1)
    (ht : auxiliaryTail n d ≤ sourceTail n d) :
    Real.log ((1+(n : ℝ)/(d : ℝ))/(1-(n : ℝ)/(d : ℝ))) ≤
      (unitUpper n d : ℝ) := by
  have ha := log_auxiliary ((n : ℝ)/(d : ℝ)) hz h1
  have hc : (auxiliaryTail n d : ℝ) ≤ (sourceTail n d : ℝ) := by
    exact_mod_cast ht
  rw [cast_auxiliaryTail, cast_sourceTail] at hc
  have hs : oddSum ((n : ℝ)/(d : ℝ)) 86 =
      oddSum ((n : ℝ)/(d : ℝ)) 80 +
      ∑ j ∈ range 6, ((n : ℝ)/(d : ℝ))^(2*(80+j)+1) /
        ((2*(80+j)+1 : Nat) : ℝ) := Finset.sum_range_add _ 80 6
  rw [hs] at ha
  rw [cast_unitUpper]
  linarith

theorem log_seventy_three_forty_four_upper :
    Real.log ((73 : ℝ)/44) ≤ (unitUpper 29 117 : ℝ) := by
  have h := unit_from_tail 29 117 (by norm_num) (by norm_num) tail_29_117
  convert h using 1 <;> norm_num

theorem log_seventy_three_forty_four_literal : Real.log ((73 : ℝ)/44) ≤
    (((25396970770050937459370700678349623199520868747673134854823117281998250419101833275239193052165778055321711430569099934194559048805576860540765557381644114250375455479979114698566608425935701392790004610327838271921325269721822876536965266801578064401396434555767803493121268701042096408070737161236451127912020843298800449716688276413912507129751809785570239448895124291070331217446271547797 : Rat) / 50164893120925325695437334276939176543090590626728836422344068188465065612953058834379853967601699621523450724442632343770589053536432025006251522594600216515254259387856770109507413760282115607985535788594944234555539613817766004809122763972675311797974206937607243568618576719790483516973693274207261490319155842413611681506088715824374004158165134728080688487594116402325906145213876011000) : ℝ) := by
  simpa only [z29_117_upper, Rat.cast_div, Rat.cast_ofNat] using log_seventy_three_forty_four_upper

#print axioms log_seventy_three_forty_four_upper
#print axioms log_seventy_three_forty_four_literal
end CurrentMain.Current741LogRealEnclosure
