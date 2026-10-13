import Current799NativeUpperAggregate
import SelectedMomentExpEnclosure
import SelectedRoundedLogEnclosure
import Current741LogRealEnclosure

/-!
Current PR799 native complex Real moment at exact main f567884.
The eight complete weight-times-exponential terms follow the source profile.
The accepted generic binary logarithm reduction and executable outward ceiling
are reused verbatim for every rank, including rank44 through its new Real unit.
The selected native branch has one ordinary ceiling and no fallback term.

Author-checked conditional source context:
kappa=1661634653669567/1000000000000000000=0.001661634653669567.
Supplier/profile/operator and native recurrence validity, conservative and PR589
bit branches, current bootstrap/outer interpretation and physical/all-size
selected-kappa transfer remain separate. No supplied endpoint is imported as
an analytic theorem without the exact source-bound finite predecessor.
Attribution: PR799 gauge44-frames-x assembler, inherited PR361 engine,
accepted finite/Real certificates and Mathlib. OpenAI-assisted preparation.
-/
namespace CurrentMain.Current799NativeRealEnclosure
open Current799NativeUpperAggregate SelectedMomentUpperAggregate SelectedMomentExpEnclosure
open SelectedMomentLogCheckpoints SelectedMomentLogUnitEnclosure
open SelectedRoundedLogEnclosure Current741LogRealEnclosure
set_option Elab.async false

private theorem rounded_from_domain (rank count k n d : Nat)
    (hd : sourceLogDomain rank count k n d)
    (hu : Real.log (((d+n : Nat) : ℝ) / ((d-n : Nat) : ℝ)) ≤
      (unitUpper n d : ℝ)) :
    Real.log ((73 : ℝ)/(rank : ℝ)) ≤ (roundedLog k n d : ℝ) := by
  rcases hd with ⟨hr, _, _, he, hlo, _⟩
  have hp : (0 : ℝ) < ((2^k : Nat) : ℝ) := by
    exact_mod_cast Nat.two_pow_pos k
  have hq : (0 : ℝ) < ((d+n : Nat) : ℝ) / ((d-n : Nat) : ℝ) := by
    have hh : (1 : ℝ) < ((d+n : Nat) : ℝ) / ((d-n : Nat) : ℝ) := by
      have hc : ((1 : Rat) : ℝ) <
          ((((d+n : Nat) : Rat) / ((d-n : Nat) : Rat)) : ℝ) := by
        exact_mod_cast hlo
      simpa only [Rat.cast_one, Rat.cast_div, Rat.cast_natCast] using hc
    linarith
  have heR : (73 : ℝ)/(rank : ℝ)/((2^k : Nat) : ℝ) =
      ((d+n : Nat) : ℝ)/((d-n : Nat) : ℝ) := by
    have hc := congrArg (fun q : Rat => (q : ℝ)) he
    simpa only [Rat.cast_div, Rat.cast_ofNat, Rat.cast_natCast] using hc
  have hx := (div_eq_iff (ne_of_gt hp)).mp heR
  have htw := mul_le_mul_of_nonneg_left log_two_upper
    (Nat.cast_nonneg k : (0 : ℝ) ≤ (k : ℝ))
  have hout := ceilGrid_outward (unitUpper n d + (k : Rat) * unitUpper 1 3)
  have hcast : ((unitUpper n d + (k : Rat) * unitUpper 1 3 : Rat) : ℝ) ≤
      (ceilGrid (unitUpper n d + (k : Rat) * unitUpper 1 3) : ℝ) := by
    exact_mod_cast hout
  have hrounded : (unitUpper n d : ℝ) + (k : ℝ) * (unitUpper 1 3 : ℝ) ≤
      (roundedLog k n d : ℝ) := by
    simpa only [roundedLog, Rat.cast_add, Rat.cast_mul, Rat.cast_natCast] using hcast
  calc
    Real.log ((73 : ℝ)/(rank : ℝ)) =
        Real.log (((d+n : Nat) : ℝ)/((d-n : Nat) : ℝ)) +
          (k : ℝ) * Real.log 2 := by
      rw [hx, Real.log_mul (ne_of_gt hq) (ne_of_gt hp)]
      norm_num only [Nat.cast_pow, Nat.cast_ofNat, Real.log_pow]
    _ ≤ (unitUpper n d : ℝ) + (k : ℝ) * (unitUpper 1 3 : ℝ) :=
      add_le_add hu htw
    _ ≤ (roundedLog k n d : ℝ) := hrounded

/-- Eight current source arguments, each rounded outward after binary reduction. -/
theorem current_rounded_log_enclosures :
    Real.log ((73 : ℝ)/1) ≤ (roundedLog 6 9 137 : ℝ) ∧
    Real.log ((73 : ℝ)/2) ≤ (roundedLog 5 9 137 : ℝ) ∧
    Real.log ((73 : ℝ)/3) ≤ (roundedLog 4 25 121 : ℝ) ∧
    Real.log ((73 : ℝ)/4) ≤ (roundedLog 4 9 137 : ℝ) ∧
    Real.log ((73 : ℝ)/5) ≤ (roundedLog 3 33 113 : ℝ) ∧
    Real.log ((73 : ℝ)/8) ≤ (roundedLog 3 9 137 : ℝ) ∧
    Real.log ((73 : ℝ)/44) ≤ (roundedLog 0 29 117 : ℝ) ∧
    Real.log ((73 : ℝ)/48) ≤ (roundedLog 0 25 121 : ℝ) := by
  have hu9 : Real.log (((137+9 : Nat) : ℝ)/((137-9 : Nat) : ℝ)) ≤
      (unitUpper 9 137 : ℝ) := by
    convert log_73_64_upper using 1 <;> norm_num
  have hu25 : Real.log (((121+25 : Nat) : ℝ)/((121-25 : Nat) : ℝ)) ≤
      (unitUpper 25 121 : ℝ) := by
    convert log_73_48_upper using 1 <;> norm_num
  have hu33 : Real.log (((113+33 : Nat) : ℝ)/((113-33 : Nat) : ℝ)) ≤
      (unitUpper 33 113 : ℝ) := by
    convert log_73_40_upper using 1 <;> norm_num
  have hu29 : Real.log (((117+29 : Nat) : ℝ)/((117-29 : Nat) : ℝ)) ≤
      (unitUpper 29 117 : ℝ) := by
    convert log_seventy_three_forty_four_upper using 1 <;> norm_num
  rcases current_domains with ⟨h1, h2, h3, h4, h5, h6, h7, h8, _⟩
  exact ⟨(by simpa only [Nat.cast_one] using (rounded_from_domain 1 183457 6 9 137 h1 hu9)),
    rounded_from_domain 2 24336 5 9 137 h2 hu9,
    rounded_from_domain 3 30961 4 25 121 h3 hu25,
    rounded_from_domain 4 13968 4 9 137 h4 hu9,
    rounded_from_domain 5 4032 3 33 113 h5 hu33,
    rounded_from_domain 8 576 3 9 137 h6 hu9,
    rounded_from_domain 44 1 0 29 117 h7 hu29,
    rounded_from_domain 48 2396 0 25 121 h8 hu25⟩

/-- Exact rational source sum before its single outward ceiling. -/
private def ordinaryUnrounded : Rat :=
  (((((((((0 : Rat) + (((1 * 183457 : Nat) : Rat) / ((73 * 7168 : Nat) : Rat) * expUpper (bCurrent * roundedLog 6 9 137))) + (((2 * 24336 : Nat) : Rat) / ((73 * 7168 : Nat) : Rat) * expUpper (bCurrent * roundedLog 5 9 137))) + (((3 * 30961 : Nat) : Rat) / ((73 * 7168 : Nat) : Rat) * expUpper (bCurrent * roundedLog 4 25 121))) + (((4 * 13968 : Nat) : Rat) / ((73 * 7168 : Nat) : Rat) * expUpper (bCurrent * roundedLog 4 9 137))) + (((5 * 4032 : Nat) : Rat) / ((73 * 7168 : Nat) : Rat) * expUpper (bCurrent * roundedLog 3 33 113))) + (((8 * 576 : Nat) : Rat) / ((73 * 7168 : Nat) : Rat) * expUpper (bCurrent * roundedLog 3 9 137))) + (((44 * 1 : Nat) : Rat) / ((73 * 7168 : Nat) : Rat) * expUpper (bCurrent * roundedLog 0 29 117))) + (((48 * 2396 : Nat) : Rat) / ((73 * 7168 : Nat) : Rat) * expUpper (bCurrent * roundedLog 0 25 121)))

/-- Actual native real expression, with every full weighted summand explicit. -/
private noncomputable def ordinaryRealMoment : ℝ :=
  (0 : ℝ) +
    (((1 * 183457 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ) * Real.exp ((bCurrent : ℝ) * (Real.log ((73 : ℝ)/1)))) +
    (((2 * 24336 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ) * Real.exp ((bCurrent : ℝ) * (Real.log ((73 : ℝ)/2)))) +
    (((3 * 30961 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ) * Real.exp ((bCurrent : ℝ) * (Real.log ((73 : ℝ)/3)))) +
    (((4 * 13968 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ) * Real.exp ((bCurrent : ℝ) * (Real.log ((73 : ℝ)/4)))) +
    (((5 * 4032 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ) * Real.exp ((bCurrent : ℝ) * (Real.log ((73 : ℝ)/5)))) +
    (((8 * 576 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ) * Real.exp ((bCurrent : ℝ) * (Real.log ((73 : ℝ)/8)))) +
    (((44 * 1 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ) * Real.exp ((bCurrent : ℝ) * (Real.log ((73 : ℝ)/44)))) +
    (((48 * 2396 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ) * Real.exp ((bCurrent : ℝ) * (Real.log ((73 : ℝ)/48))))

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
    Real.exp ((bCurrent : ℝ) * (Real.log ((73 : ℝ)/1))) ≤ (expUpper (bCurrent * roundedLog 6 9 137) : ℝ) ∧
    Real.exp ((bCurrent : ℝ) * (Real.log ((73 : ℝ)/2))) ≤ (expUpper (bCurrent * roundedLog 5 9 137) : ℝ) ∧
    Real.exp ((bCurrent : ℝ) * (Real.log ((73 : ℝ)/3))) ≤ (expUpper (bCurrent * roundedLog 4 25 121) : ℝ) ∧
    Real.exp ((bCurrent : ℝ) * (Real.log ((73 : ℝ)/4))) ≤ (expUpper (bCurrent * roundedLog 4 9 137) : ℝ) ∧
    Real.exp ((bCurrent : ℝ) * (Real.log ((73 : ℝ)/5))) ≤ (expUpper (bCurrent * roundedLog 3 33 113) : ℝ) ∧
    Real.exp ((bCurrent : ℝ) * (Real.log ((73 : ℝ)/8))) ≤ (expUpper (bCurrent * roundedLog 3 9 137) : ℝ) ∧
    Real.exp ((bCurrent : ℝ) * (Real.log ((73 : ℝ)/44))) ≤ (expUpper (bCurrent * roundedLog 0 29 117) : ℝ) ∧
    Real.exp ((bCurrent : ℝ) * (Real.log ((73 : ℝ)/48))) ≤ (expUpper (bCurrent * roundedLog 0 25 121) : ℝ) := by
  rcases current_rounded_log_enclosures with ⟨l1, l2, l3, l4, l5, l6, l7, l8⟩
  rcases current_domains with ⟨_, _, _, _, _, _, _, _, d1, d2, d3, d4, d5, d6, d7, d8⟩
  have e1 := expUpper_real_enclosure _ d1.1 d1.2
  have e2 := expUpper_real_enclosure _ d2.1 d2.2
  have e3 := expUpper_real_enclosure _ d3.1 d3.2
  have e4 := expUpper_real_enclosure _ d4.1 d4.2
  have e5 := expUpper_real_enclosure _ d5.1 d5.2
  have e6 := expUpper_real_enclosure _ d6.1 d6.2
  have e7 := expUpper_real_enclosure _ d7.1 d7.2
  have e8 := expUpper_real_enclosure _ d8.1 d8.2
  exact ⟨exp_from_log _ _ l1 e1,
    exp_from_log _ _ l2 e2,
    exp_from_log _ _ l3 e3,
    exp_from_log _ _ l4 e4,
    exp_from_log _ _ l5 e5,
    exp_from_log _ _ l6 e6,
    exp_from_log _ _ l7 e7,
    exp_from_log _ _ l8 e8⟩

private theorem ordinary_real_upper : ordinaryRealMoment ≤ (currentOrdinaryRounded : ℝ) := by
  rcases source_term_enclosures with ⟨e1, e2, e3, e4, e5, e6, e7, e8⟩
  have h1 := mul_le_mul_of_nonneg_left e1
    (by positivity : (0 : ℝ) ≤ (((1 * 183457 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ)))
  have h2 := mul_le_mul_of_nonneg_left e2
    (by positivity : (0 : ℝ) ≤ (((2 * 24336 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ)))
  have h3 := mul_le_mul_of_nonneg_left e3
    (by positivity : (0 : ℝ) ≤ (((3 * 30961 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ)))
  have h4 := mul_le_mul_of_nonneg_left e4
    (by positivity : (0 : ℝ) ≤ (((4 * 13968 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ)))
  have h5 := mul_le_mul_of_nonneg_left e5
    (by positivity : (0 : ℝ) ≤ (((5 * 4032 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ)))
  have h6 := mul_le_mul_of_nonneg_left e6
    (by positivity : (0 : ℝ) ≤ (((8 * 576 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ)))
  have h7 := mul_le_mul_of_nonneg_left e7
    (by positivity : (0 : ℝ) ≤ (((44 * 1 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ)))
  have h8 := mul_le_mul_of_nonneg_left e8
    (by positivity : (0 : ℝ) ≤ (((48 * 2396 : Nat) : ℝ) / ((73 * 7168 : Nat) : ℝ)))
  have hs : ordinaryRealMoment ≤ (ordinaryUnrounded : ℝ) := by
    unfold ordinaryRealMoment ordinaryUnrounded
    simp only [Rat.cast_add, Rat.cast_mul, Rat.cast_div, Rat.cast_natCast, Rat.cast_zero]
    exact (add_le_add (add_le_add (add_le_add (add_le_add (add_le_add (add_le_add (add_le_add (add_le_add (le_refl (0 : ℝ)) h1) h2) h3) h4) h5) h6) h7) h8)
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


#print axioms current_rounded_log_enclosures
#print axioms currentRealMoment_le_upper
#print axioms currentRealMoment_strict
end CurrentMain.Current799NativeRealEnclosure
