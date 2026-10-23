import Current1094RoundedRecurrence

/-!
Exact endpoint bookkeeping and monotone weakening for the source-bound PR1094
profile. The native moment endpoint bCurrent and the author-checked selected
outer kappa are different constants. This file does not identify them.

Scientific source: ce7ad1b6ab09452c3478723a2e96ed5ff212dc08, with selected kappa
836330098538459/500000000000000000. The preceding Real enclosure is checked;
the characteristic/potential wrappers and this new file await native checking.

The power-bound transfer takes a native power bound as an explicit premise.
It does not construct a physical recurrence, its cost family, precision budget,
profile realization or the complete selected-kappa multiplication theorem.
Attribution: PR1094 finite profile, PR585/PR605 and repaired PR799 enclosures,
ProfilePotentialTransfer and RoundedRecurrence. Apache-2.0.
Prepared with OpenAI assistance; source-only until independently checked.
-/

set_option Elab.async false
namespace CurrentMain.Current1094SelectedExponent
open scoped BigOperators
open Current1094NativeUpperAggregate Current1094NativeRealEnclosure
open Current1094ProfilePotential Current1094RoundedRecurrence

/-- The author-checked selected outer parameter, not the native endpoint. -/
def selectedKappa : Rat := 836330098538459 / 500000000000000000

/-- Exact positive gap, with all endpoint order conditions exposed. -/
theorem endpoint_relation :
    (bCurrent : ℝ) - (selectedKappa : ℝ) =
      (112099189247420917 : ℝ) / 40000000000000000000000 ∧
    0 < (selectedKappa : ℝ) ∧ (selectedKappa : ℝ) < (bCurrent : ℝ) ∧
    (bCurrent : ℝ) < 1 := by
  norm_num [selectedKappa, bCurrent]

/-- For this exact nonnegative profile, decreasing the endpoint preserves
strictness of the exponential characteristic. -/
theorem selected_characteristic_strict :
    RoundedRecurrence.expCharacteristic ranks
      (fun r => (multiplicity r : ℝ)) (fun r => (r : ℝ))
      73 14336 (selectedKappa : ℝ) < 1 := by
  have hle :
      RoundedRecurrence.expCharacteristic ranks
        (fun r => (multiplicity r : ℝ)) (fun r => (r : ℝ))
        73 14336 (selectedKappa : ℝ) ≤
      RoundedRecurrence.expCharacteristic ranks
        (fun r => (multiplicity r : ℝ)) (fun r => (r : ℝ))
        73 14336 (bCurrent : ℝ) := by
    unfold RoundedRecurrence.expCharacteristic
    apply Finset.sum_le_sum
    intro r hr
    have hlog : 0 ≤ Real.log (73 / (r : ℝ)) := by
      apply Real.log_nonneg
      simp only [ranks, Finset.mem_insert, Finset.mem_singleton] at hr
      rcases hr with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl <;> norm_num
    have hw : 0 ≤ (multiplicity r : ℝ) * (r : ℝ) / (73 * 14336) :=
      div_nonneg (mul_nonneg (Nat.cast_nonneg _) (Nat.cast_nonneg _))
        (by norm_num)
    exact mul_le_mul_of_nonneg_left
      (Real.exp_le_exp.mpr (mul_le_mul_of_nonneg_right endpoint_relation.2.2.1.le hlog)) hw
  exact lt_of_le_of_lt hle (by rw [current_characteristic_eq_real]; exact currentRealMoment_strict)

/-- A supplied native power bound weakens to the selected exponent at positive
integer widths. The nonnegative constant is essential for this implication. -/
theorem native_power_bound_implies_selected
    (f : ℕ → ℝ) (A : ℝ) (hA : 0 ≤ A)
    (native_bound : ∀ n, 0 < n → f n ≤ A * (n : ℝ) ^ (1 - (bCurrent : ℝ))) :
    ∀ n, 0 < n → f n ≤ A * (n : ℝ) ^ (1 - (selectedKappa : ℝ)) := by
  intro n hn
  have hn1 : (1 : ℝ) ≤ (n : ℝ) := by
    exact_mod_cast (Nat.succ_le_iff.mpr hn)
  exact (native_bound n hn).trans
    (mul_le_mul_of_nonneg_left
      (Real.rpow_le_rpow_of_exponent_le hn1
        (sub_le_sub_left endpoint_relation.2.2.1.le 1)) hA)

end CurrentMain.Current1094SelectedExponent

#print axioms CurrentMain.Current1094SelectedExponent.endpoint_relation
#print axioms CurrentMain.Current1094SelectedExponent.selected_characteristic_strict
#print axioms CurrentMain.Current1094SelectedExponent.native_power_bound_implies_selected

-- Diagnostic-only full signatures of the imported and new facts.
set_option pp.explicit true
set_option pp.fullNames true
#check CurrentMain.Current1094RoundedRecurrence.current_characteristic_eq_real
#check CurrentMain.Current1094RoundedRecurrence.conditional_all_width_bound
#check CurrentMain.Current1094SelectedExponent.endpoint_relation
#check CurrentMain.Current1094SelectedExponent.selected_characteristic_strict
#check CurrentMain.Current1094SelectedExponent.native_power_bound_implies_selected
