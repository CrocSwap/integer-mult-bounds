import Current588LogCheckpoints
import Mathlib.Analysis.SpecialFunctions.Log.Deriv

/-!
Current PR588 rank30 Real log-unit enclosure:73/30=(73/60)*2, whose new
unit is z=13/133. The private remainder and cast chain below is copied
verbatim from the accepted historical five-unit module, with exact source
correspondence recorded separately. One finite six-term tail comparison
and its Real instantiation are new. The literal bound substitutes the
accepted finite eighty-term identity.

Author-checked conditional source context at main9594:
kappa=400569730495803/250000000000000000=0.001602278921983212.
The selected native complex branch has no fallback; conservative complex
and PR543 bit retain independently rounded fallback. This unit theorem
establishes neither model, current weighted moment, physical realization
nor the all-size selected-kappa theorem. Historical sources are preserved.
Attribution: PR361 base_two_moment.py as retained in PR588 complex-multicold,
the accepted analytic log proof chain, and Mathlib's Taylor remainder.
Prepared with OpenAI assistance; the new finite decision uses the kernel.
-/
namespace CurrentMain.Current588LogRealEnclosure
open scoped BigOperators
open Finset SelectedMomentLogCheckpoints Current588LogCheckpoints
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

/-- One finite comparison, with six extra terms and two rational tails. -/
private theorem tail_13_133 : auxiliaryTail 13 133 ≤ sourceTail 13 133 := by decide +kernel

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

theorem log_seventy_three_sixty_upper :
    Real.log ((73 : ℝ)/60) ≤ (unitUpper 13 133 : ℝ) := by
  have h := unit_from_tail 13 133 (by norm_num) (by norm_num) tail_13_133
  convert h using 1 <;> norm_num

theorem log_seventy_three_sixty_literal : Real.log ((73 : ℝ)/60) ≤
    (((41084636859487488459851583995985331403909728810838422252951930013308366142692193046408974212389609970372571524323420166461081079347135078567101410137900977278802448853191255963220845015800175466804754066241234534573343041034243675853244835771007797152536034843413592640768476220744731794282791317750302083585459583386107987062220865291988620488411332817357927408442059510161493766776163852693625509259 : Rat) / 209492706950241663303783951795049103929930413114400258113587468881304493298208358972607965100013705918466544112277030499979500160834492350919552896372673401459385140574863349571215887358984601627434015701802515389545299439334650541014753657535696747303089460104162381456563617703491199975333217763768623082597286857733776519403148518879517776807755551901797226342087337444728799891515696140491024689000) : ℝ) := by
  simpa only [z13_133_upper, Rat.cast_div, Rat.cast_ofNat] using log_seventy_three_sixty_upper

#print axioms log_seventy_three_sixty_upper
#print axioms log_seventy_three_sixty_literal
end CurrentMain.Current588LogRealEnclosure
