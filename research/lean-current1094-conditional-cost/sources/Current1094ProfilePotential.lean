import Current1094NativeRealEnclosure
import ProfilePotentialTransfer

/-!
PR1094 eight-term potential interface at immutable scientific main
ce7ad1b6ab09452c3478723a2e96ed5ff212dc08. The supplied rank/count profile,
live normalization 14336 and native saving are those of the source-bound
finite aggregate. This joins its proposed Real enclosure to the accepted
generic logarithmic-potential factorization without replaying checkpoints.

Author-checked conditional context:
kappa=836330098538459/500000000000000000=0.001672660197076918.
The final rounded-child inequality and additive-cost budget are explicit
premises. No rounding rule, recurrence license, saving interpretation,
realized provider/operator/profile, physical execution, bit supplier,
precision/tape bound or all-size multiplication theorem is supplied here.
The Real enclosure and this new interface remain uncompiled in the recovered
runtime. This is a new proposal, not restoration of an unbacked older file.
Attribution: PR1094 profile; PR585/PR605 and repaired PR799 Real machinery;
the accepted ProfilePotentialTransfer factorization. Apache-2.0.
Prepared with OpenAI assistance for independent source review.
-/

set_option Elab.async false
namespace CurrentMain.Current1094ProfilePotential
open scoped BigOperators
open ProfilePotentialTransfer Current1094NativeUpperAggregate
open Current1094NativeRealEnclosure

/-- Exactly the eight ranks in the selected native profile. -/
def ranks : Finset Nat := {1, 2, 3, 4, 5, 7, 8, 48}

/-- Multiplicities are supplied source data; this does not realize the profile. -/
def multiplicity (r : Nat) : Nat :=
  if r = 1 then 349604 else
  if r = 2 then 60192 else
  if r = 3 then 62585 else
  if r = 4 then 20448 else
  if r = 5 then 11808 else
  if r = 7 then 7 else
  if r = 8 then 1152 else
  if r = 48 then 4866 else 0

noncomputable def ratio (r : Nat) : ℝ := (r : ℝ) / 73

noncomputable def normalizedMoment : ℝ :=
  ∑ r ∈ ranks, ((multiplicity r : ℝ) * ratio r / 14336) *
    Real.exp ((bCurrent : ℝ) * Real.log (1 / ratio r))

noncomputable def weightedPotential (child : Nat → ℝ) : ℝ :=
  ∑ r ∈ ranks, (multiplicity r : ℝ) * logPotential (bCurrent : ℝ) (child r)

noncomputable def idealPotential (t : ℝ) : ℝ :=
  weightedPotential (fun r => ratio r * t)

/-- The outward finite upper bound leaves an explicit potential budget. -/
noncomputable def availableSlack (t : ℝ) : ℝ :=
  14336 * (1 - (currentUpper : ℝ)) * logPotential (bCurrent : ℝ) t

private theorem ratio_positive (r : Nat) (hr : r ∈ ranks) : 0 < ratio r := by
  simp only [ranks, Finset.mem_insert, Finset.mem_singleton] at hr
  rcases hr with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl <;>
    norm_num [ratio]

/-- Whole weighted terms, not separately rounded coefficients, match the bridge. -/
theorem normalizedMoment_eq_current : normalizedMoment = currentRealMoment := by
  change normalizedMoment =
    (0 : ℝ) +
      (((1 * 349604 : Nat) : ℝ) / ((73 * 14336 : Nat) : ℝ) * Real.exp ((bCurrent : ℝ) * Real.log ((73 : ℝ)/1))) +
      (((2 * 60192 : Nat) : ℝ) / ((73 * 14336 : Nat) : ℝ) * Real.exp ((bCurrent : ℝ) * Real.log ((73 : ℝ)/2))) +
      (((3 * 62585 : Nat) : ℝ) / ((73 * 14336 : Nat) : ℝ) * Real.exp ((bCurrent : ℝ) * Real.log ((73 : ℝ)/3))) +
      (((4 * 20448 : Nat) : ℝ) / ((73 * 14336 : Nat) : ℝ) * Real.exp ((bCurrent : ℝ) * Real.log ((73 : ℝ)/4))) +
      (((5 * 11808 : Nat) : ℝ) / ((73 * 14336 : Nat) : ℝ) * Real.exp ((bCurrent : ℝ) * Real.log ((73 : ℝ)/5))) +
      (((7 * 7 : Nat) : ℝ) / ((73 * 14336 : Nat) : ℝ) * Real.exp ((bCurrent : ℝ) * Real.log ((73 : ℝ)/7))) +
      (((8 * 1152 : Nat) : ℝ) / ((73 * 14336 : Nat) : ℝ) * Real.exp ((bCurrent : ℝ) * Real.log ((73 : ℝ)/8))) +
      (((48 * 4866 : Nat) : ℝ) / ((73 * 14336 : Nat) : ℝ) * Real.exp ((bCurrent : ℝ) * Real.log ((73 : ℝ)/48)))
  norm_num [normalizedMoment, ranks, multiplicity, ratio] <;> ring

/-- The source-bound Real bridge supplies the strict normalized moment. -/
theorem normalizedMoment_strict : normalizedMoment < 1 := by
  rw [normalizedMoment_eq_current]
  exact currentRealMoment_strict

/-- Exact factorization at every positive scale, with normalization exposed. -/
theorem idealPotential_factorization (t : ℝ) (ht : 0 < t) :
    idealPotential t =
      (14336 * normalizedMoment) * logPotential (bCurrent : ℝ) t := by
  have hcoef :
      (∑ r ∈ ranks, (multiplicity r : ℝ) * ratio r *
        Real.exp ((bCurrent : ℝ) * Real.log (1 / ratio r))) =
        14336 * normalizedMoment := by
    unfold normalizedMoment
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro r hr
    ring
  unfold idealPotential weightedPotential
  rw [weighted_logPotential_factorization ranks (fun r => (multiplicity r : ℝ))
    ratio (bCurrent : ℝ) t ratio_positive ht, hcoef]

/-- Ideal scaled children strictly contract the supplied normalization. -/
theorem idealPotential_strict (t : ℝ) (ht : 0 < t) :
    idealPotential t < 14336 * logPotential (bCurrent : ℝ) t := by
  exact normalized_moment_strict_contraction ranks
    (fun r => (multiplicity r : ℝ)) ratio (bCurrent : ℝ) 14336 t
    ratio_positive (by norm_num) ht normalizedMoment_strict

/-- The rational upper certificate provides quantitative, rather than only strict, slack. -/
theorem idealPotential_le_upper (t : ℝ) (ht : 0 < t) :
    idealPotential t ≤
      (14336 * (currentUpper : ℝ)) * logPotential (bCurrent : ℝ) t := by
  have hm : normalizedMoment ≤ (currentUpper : ℝ) := by
    rw [normalizedMoment_eq_current]
    exact currentRealMoment_le_upper
  rw [idealPotential_factorization t ht]
  apply mul_le_mul_of_nonneg_right
    (mul_le_mul_of_nonneg_left hm (by norm_num : (0 : ℝ) ≤ 14336))
  exact le_of_lt (Real.exp_pos _)

/-- The budget is positive; exponential positivity does not require t > 0 here. -/
theorem availableSlack_positive (t : ℝ) : 0 < availableSlack t := by
  have hu : (currentUpper : ℝ) < 1 := by
    exact_mod_cast current_upper_strict
  unfold availableSlack
  exact mul_pos (mul_pos (by norm_num) (sub_pos.mpr hu)) (Real.exp_pos _)

/-- Rounding error and additive work must be supplied and paid for explicitly. -/
theorem rounded_children_and_cost_absorbed
    (child : Nat → ℝ) (t roundingError additiveCost : ℝ) (ht : 0 < t)
    (hRounded : weightedPotential child ≤ idealPotential t + roundingError)
    (hBudget : roundingError + additiveCost ≤ availableSlack t) :
    weightedPotential child + additiveCost ≤
      14336 * logPotential (bCurrent : ℝ) t := by
  calc
    weightedPotential child + additiveCost ≤
        (idealPotential t + roundingError) + additiveCost :=
      add_le_add_right hRounded additiveCost
    _ = idealPotential t + (roundingError + additiveCost) := by ring
    _ ≤ (14336 * (currentUpper : ℝ)) * logPotential (bCurrent : ℝ) t +
        availableSlack t := add_le_add (idealPotential_le_upper t ht) hBudget
    _ = 14336 * logPotential (bCurrent : ℝ) t := by
      unfold availableSlack
      ring

end CurrentMain.Current1094ProfilePotential

#print axioms CurrentMain.Current1094ProfilePotential.normalizedMoment_eq_current
#print axioms CurrentMain.Current1094ProfilePotential.normalizedMoment_strict
#print axioms CurrentMain.Current1094ProfilePotential.idealPotential_factorization
#print axioms CurrentMain.Current1094ProfilePotential.idealPotential_strict
#print axioms CurrentMain.Current1094ProfilePotential.idealPotential_le_upper
#print axioms CurrentMain.Current1094ProfilePotential.availableSlack_positive
#print axioms CurrentMain.Current1094ProfilePotential.rounded_children_and_cost_absorbed
