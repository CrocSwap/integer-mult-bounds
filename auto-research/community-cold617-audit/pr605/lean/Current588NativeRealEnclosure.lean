import Current588NativeUpperAggregate
import SelectedMomentExpEnclosure
import SelectedRoundedLogEnclosure
import Current588LogRealEnclosure

/-!
Current PR588 native complex Real moment at the pinned main9594 source inputs.
The nine whole weighted exponentials follow the exact supplied profile order.
The rank-eight rounded-log proof is copied from its accepted public proof body;
the new rank-thirty identity uses the accepted Real.log(73/60) enclosure.
Seven remaining rounded-log bounds and the generic exponential enclosure are
reused. This native branch applies one outward ceiling and has no fallback.

Author-checked conditional source context:
kappa=400569730495803/250000000000000000=0.001602278921983212.
The supplied native recurrence, physical/operator/profile realization, the
conservative and PR543 bit branches, initial saving validity, bootstrap/outer
interpretation and a complete all-size selected-kappa theorem remain separate.
Attribution: PR588 complex-571-free4fc8/assemble.py, PR361 base-two engine,
and accepted finite/Real certificate interfaces. OpenAI-assisted preparation.
-/
namespace CurrentMain.Current588NativeRealEnclosure
open Current588NativeUpperAggregate SelectedMomentUpperAggregate SelectedMomentExpEnclosure
open SelectedMomentLogCheckpoints SelectedMomentLogUnitEnclosure
open SelectedRoundedLogEnclosure Current588LogRealEnclosure
set_option Elab.async false

private theorem log_rank8_upper :
    Real.log ((73 : ℝ)/8) ≤ (roundedLog 3 9 137 : ℝ) := by
  have h2 := mul_le_mul_of_nonneg_left log_two_upper
    (by norm_num : (0 : ℝ) ≤ 3)
  have hs := add_le_add log_73_64_upper h2
  have he : Real.log ((73 : ℝ)/8) =
      Real.log ((73 : ℝ)/64) + 3*Real.log 2 := by
    rw [show (73 : ℝ)/8 = ((73 : ℝ)/64)*(2:ℝ)^3 by norm_num]
    rw [Real.log_mul (by norm_num) (by norm_num)]
    rw [Real.log_pow]
    norm_num
  have hc : ((unitUpper 9 137 + (3:Rat)*unitUpper 1 3 : Rat):ℝ) ≤
      (roundedLog 3 9 137 : ℝ) := by
    change ((unitUpper 9 137 + (3:Rat)*unitUpper 1 3 : Rat):ℝ) ≤
      (ceilGrid (unitUpper 9 137 + (3:Rat)*unitUpper 1 3):ℝ)
    exact_mod_cast (ceilGrid_outward (unitUpper 9 137 + (3:Rat)*unitUpper 1 3))
  calc
    Real.log ((73:ℝ)/8) = Real.log ((73:ℝ)/64) + 3*Real.log 2 := he
    _ ≤ ((unitUpper 9 137 + (3:Rat)*unitUpper 1 3 : Rat):ℝ) := by
      simpa only [Rat.cast_add, Rat.cast_mul, Rat.cast_ofNat] using hs
    _ ≤ (roundedLog 3 9 137 : ℝ) := hc

theorem log_rank30_upper :
    Real.log ((73 : ℝ)/30) ≤ (roundedLog 1 13 133 : ℝ) := by
  have h2 := mul_le_mul_of_nonneg_left log_two_upper
    (by norm_num : (0 : ℝ) ≤ 1)
  have hs := add_le_add log_seventy_three_sixty_upper h2
  have he : Real.log ((73 : ℝ)/30) =
      Real.log ((73 : ℝ)/60) + 1*Real.log 2 := by
    rw [show (73 : ℝ)/30 = ((73 : ℝ)/60)*(2:ℝ)^1 by norm_num]
    rw [Real.log_mul (by norm_num) (by norm_num)]
    rw [Real.log_pow]
    norm_num
  have hc : ((unitUpper 13 133 + (1:Rat)*unitUpper 1 3 : Rat):ℝ) ≤
      (roundedLog 1 13 133 : ℝ) := by
    change ((unitUpper 13 133 + (1:Rat)*unitUpper 1 3 : Rat):ℝ) ≤
      (ceilGrid (unitUpper 13 133 + (1:Rat)*unitUpper 1 3):ℝ)
    exact_mod_cast (ceilGrid_outward (unitUpper 13 133 + (1:Rat)*unitUpper 1 3))
  calc
    Real.log ((73:ℝ)/30) = Real.log ((73:ℝ)/60) + 1*Real.log 2 := he
    _ ≤ ((unitUpper 13 133 + (1:Rat)*unitUpper 1 3 : Rat):ℝ) := by
      simpa only [Rat.cast_add, Rat.cast_mul, Rat.cast_ofNat, Rat.cast_one] using hs
    _ ≤ (roundedLog 1 13 133 : ℝ) := hc

/-- The source rational sum, before its one outward ceiling. -/
private def ordinaryUnrounded : Rat :=
  ((((((((((0 : Rat) + (((1 * 173404 : Nat) : Rat) / ((73 * 7168 : Nat) : Rat) * expUpper (bCurrent * roundedLog 6 9 137))) + (((2 * 40632 : Nat) : Rat) / ((73 * 7168 : Nat) : Rat) * expUpper (bCurrent * roundedLog 5 9 137))) + (((3 * 23928 : Nat) : Rat) / ((73 * 7168 : Nat) : Rat) * expUpper (bCurrent * roundedLog 4 25 121))) + (((4 * 14024 : Nat) : Rat) / ((73 * 7168 : Nat) : Rat) * expUpper (bCurrent * roundedLog 4 9 137))) + (((5 * 4038 : Nat) : Rat) / ((73 * 7168 : Nat) : Rat) * expUpper (bCurrent * roundedLog 3 33 113))) + (((6 * 4032 : Nat) : Rat) / ((73 * 7168 : Nat) : Rat) * expUpper (bCurrent * roundedLog 3 25 121))) + (((8 * 576 : Nat) : Rat) / ((73 * 7168 : Nat) : Rat) * expUpper (bCurrent * roundedLog 3 9 137))) + (((30 * 1 : Nat) : Rat) / ((73 * 7168 : Nat) : Rat) * expUpper (bCurrent * roundedLog 1 13 133))) + (((48 * 1857 : Nat) : Rat) / ((73 * 7168 : Nat) : Rat) * expUpper (bCurrent * roundedLog 0 25 121)))

/-- The actual native real expression in the source profile order. -/
private noncomputable def ordinaryRealMoment : ℝ :=
  (0 : ℝ) +
    (((1 * 173404 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ) * Real.exp ((bCurrent : ℝ) * Real.log (73 : ℝ))) +
    (((2 * 40632 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ) * Real.exp ((bCurrent : ℝ) * Real.log ((73 : ℝ) / 2))) +
    (((3 * 23928 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ) * Real.exp ((bCurrent : ℝ) * Real.log ((73 : ℝ) / 3))) +
    (((4 * 14024 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ) * Real.exp ((bCurrent : ℝ) * Real.log ((73 : ℝ) / 4))) +
    (((5 * 4038 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ) * Real.exp ((bCurrent : ℝ) * Real.log ((73 : ℝ) / 5))) +
    (((6 * 4032 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ) * Real.exp ((bCurrent : ℝ) * Real.log ((73 : ℝ) / 6))) +
    (((8 * 576 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ) * Real.exp ((bCurrent : ℝ) * Real.log ((73 : ℝ) / 8))) +
    (((30 * 1 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ) * Real.exp ((bCurrent : ℝ) * Real.log ((73 : ℝ) / 30))) +
    (((48 * 1857 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ) * Real.exp ((bCurrent : ℝ) * Real.log ((73 : ℝ) / 48)))

/-- Selected native complex moment, with no fallback summand. -/
noncomputable def currentRealMoment : ℝ := ordinaryRealMoment

private theorem saving_nonnegative : (0 : ℝ) ≤ (bCurrent : ℝ) := by
  norm_num [bCurrent]

private theorem exp_from_log (x : ℝ) (q : Rat)
    (hl : x ≤ (q : ℝ))
    (he : Real.exp ((bCurrent*q : Rat) : ℝ) ≤ (expUpper (bCurrent*q) : ℝ)) :
    Real.exp ((bCurrent : ℝ)*x) ≤ (expUpper (bCurrent*q) : ℝ) := by
  have hm := mul_le_mul_of_nonneg_left hl saving_nonnegative
  refine (Real.exp_le_exp.mpr hm).trans ?_
  simpa only [Rat.cast_mul] using he

private theorem source_term_enclosures :
    Real.exp ((bCurrent : ℝ) * (Real.log (73 : ℝ))) ≤ (expUpper (bCurrent * roundedLog 6 9 137) : ℝ) ∧
    Real.exp ((bCurrent : ℝ) * (Real.log ((73 : ℝ)/2))) ≤ (expUpper (bCurrent * roundedLog 5 9 137) : ℝ) ∧
    Real.exp ((bCurrent : ℝ) * (Real.log ((73 : ℝ)/3))) ≤ (expUpper (bCurrent * roundedLog 4 25 121) : ℝ) ∧
    Real.exp ((bCurrent : ℝ) * (Real.log ((73 : ℝ)/4))) ≤ (expUpper (bCurrent * roundedLog 4 9 137) : ℝ) ∧
    Real.exp ((bCurrent : ℝ) * (Real.log ((73 : ℝ)/5))) ≤ (expUpper (bCurrent * roundedLog 3 33 113) : ℝ) ∧
    Real.exp ((bCurrent : ℝ) * (Real.log ((73 : ℝ)/6))) ≤ (expUpper (bCurrent * roundedLog 3 25 121) : ℝ) ∧
    Real.exp ((bCurrent : ℝ) * (Real.log ((73 : ℝ)/8))) ≤ (expUpper (bCurrent * roundedLog 3 9 137) : ℝ) ∧
    Real.exp ((bCurrent : ℝ) * (Real.log ((73 : ℝ)/30))) ≤ (expUpper (bCurrent * roundedLog 1 13 133) : ℝ) ∧
    Real.exp ((bCurrent : ℝ) * (Real.log ((73 : ℝ)/48))) ≤ (expUpper (bCurrent * roundedLog 0 25 121) : ℝ) := by
  rcases selected_rounded_log_enclosures with ⟨l1, l2, l3, l4, l5, l6, l7, l8, l9⟩
  rcases current_domains with ⟨_, _, _, _, _, _, _, _, _, d1, d2, d3, d4, d5, d6, d7, d8, d9⟩
  have e1 := expUpper_real_enclosure _ d1.1 d1.2
  have e2 := expUpper_real_enclosure _ d2.1 d2.2
  have e3 := expUpper_real_enclosure _ d3.1 d3.2
  have e4 := expUpper_real_enclosure _ d4.1 d4.2
  have e5 := expUpper_real_enclosure _ d5.1 d5.2
  have e6 := expUpper_real_enclosure _ d6.1 d6.2
  have e7 := expUpper_real_enclosure _ d7.1 d7.2
  have e8 := expUpper_real_enclosure _ d8.1 d8.2
  have e9 := expUpper_real_enclosure _ d9.1 d9.2
  exact ⟨exp_from_log _ _ l1 e1,
    exp_from_log _ _ l2 e2,
    exp_from_log _ _ l3 e3,
    exp_from_log _ _ l4 e4,
    exp_from_log _ _ l5 e5,
    exp_from_log _ _ l6 e6,
    exp_from_log _ _ log_rank8_upper e7,
    exp_from_log _ _ log_rank30_upper e8,
    exp_from_log _ _ l9 e9⟩

private theorem ordinary_real_upper : ordinaryRealMoment ≤ (currentOrdinaryRounded : ℝ) := by
  rcases source_term_enclosures with ⟨e1, e2, e3, e4, e5, e6, e7, e8, e9⟩
  have h1 := mul_le_mul_of_nonneg_left e1
    (by positivity : (0 : ℝ) ≤ (((1 * 173404 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ)))
  have h2 := mul_le_mul_of_nonneg_left e2
    (by positivity : (0 : ℝ) ≤ (((2 * 40632 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ)))
  have h3 := mul_le_mul_of_nonneg_left e3
    (by positivity : (0 : ℝ) ≤ (((3 * 23928 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ)))
  have h4 := mul_le_mul_of_nonneg_left e4
    (by positivity : (0 : ℝ) ≤ (((4 * 14024 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ)))
  have h5 := mul_le_mul_of_nonneg_left e5
    (by positivity : (0 : ℝ) ≤ (((5 * 4038 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ)))
  have h6 := mul_le_mul_of_nonneg_left e6
    (by positivity : (0 : ℝ) ≤ (((6 * 4032 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ)))
  have h7 := mul_le_mul_of_nonneg_left e7
    (by positivity : (0 : ℝ) ≤ (((8 * 576 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ)))
  have h8 := mul_le_mul_of_nonneg_left e8
    (by positivity : (0 : ℝ) ≤ (((30 * 1 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ)))
  have h9 := mul_le_mul_of_nonneg_left e9
    (by positivity : (0 : ℝ) ≤ (((48 * 1857 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ)))
  have hs : ordinaryRealMoment ≤ (ordinaryUnrounded : ℝ) := by
    unfold ordinaryRealMoment ordinaryUnrounded
    simp only [Rat.cast_add, Rat.cast_mul, Rat.cast_div, Rat.cast_natCast, Rat.cast_zero]
    exact (add_le_add (add_le_add (add_le_add (add_le_add (add_le_add (add_le_add (add_le_add (add_le_add (add_le_add (le_refl (0 : ℝ)) h1) h2) h3) h4) h5) h6) h7) h8) h9)
  have hc : (ordinaryUnrounded : ℝ) ≤ (currentOrdinaryRounded : ℝ) := by
    change (ordinaryUnrounded : ℝ) ≤ (ceilGrid ordinaryUnrounded : ℝ)
    exact_mod_cast (ceilGrid_outward ordinaryUnrounded)
  exact hs.trans hc

/-- The source ordinary ceiling bounds the complete native real expression. -/
theorem currentRealMoment_le_upper : currentRealMoment ≤ (currentUpper : ℝ) := by
  exact ordinary_real_upper

/-- The selected native finite real moment is strictly below one. -/
theorem currentRealMoment_strict : currentRealMoment < 1 := by
  refine currentRealMoment_le_upper.trans_lt ?_
  exact_mod_cast current_upper_strict

#print axioms log_rank30_upper
#print axioms currentRealMoment_le_upper
#print axioms currentRealMoment_strict
end CurrentMain.Current588NativeRealEnclosure
