import Selected

/-!
Exact hypothesis controls for the recurrence implication. These are
countermodels to weakened premises, not counterexamples to PR2234.
Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
-/

open StoppedRecurrence

namespace RecurrenceCounterexamples

noncomputable def missedLeaf (n : ℕ) : ℝ := if n = 1 then 1 else 0

theorem omitted_leaf_all_other_widths (n : ℕ) (hn : 2 ≤ n) : missedLeaf n = 0 := by
  simp [missedLeaf, show n ≠ 1 by omega]

theorem omitted_leaf_fails : ¬missedLeaf 1 ≤ potential 0 1 1 1 := by
  norm_num [missedLeaf, potential]

theorem selected_power_le (n : ℕ) (hn : 1 ≤ n) :
    (n : ℝ) ^ SelectedStoppedRecurrence.exponent ≤ n := by
  calc
    (n : ℝ) ^ SelectedStoppedRecurrence.exponent ≤ (n : ℝ) ^ (1 : ℝ) :=
      Real.rpow_le_rpow_of_exponent_le (by exact_mod_cast hn)
        (by norm_num [SelectedStoppedRecurrence.exponent])
    _ = n := Real.rpow_one _

/-- An expanding recursive child can support quadratic cost despite both
moment margins and a linear local charge. All widths are covered. -/
theorem expanding_child_recurrence (n : ℕ) :
    (n : ℝ) ^ 2 ≤ (1 / 4 : ℝ) * (4 * (n / 2 : ℕ)) ^ 2 + 2 * (n + 1) := by
  have h : n ≤ 2 * (n / 2) + 1 := by omega
  have hr : (n : ℝ) ≤ 2 * (n / 2 : ℕ) + 1 := by exact_mod_cast h
  have hfloor : (0 : ℝ) ≤ (n / 2 : ℕ) := by positivity
  have hlower : (2 : ℝ) * (n / 2 : ℕ) ≤ n := by exact_mod_cast Nat.mul_div_le n 2
  nlinarith

theorem expanding_child_moments :
    (1 / 4 : ℝ) * (4 / 2) ≤ 199 / 200 ∧
    (1 / 4 : ℝ) * (4 / 2) ^ SelectedStoppedRecurrence.exponent ≤ 9999 / 10000 := by
  constructor
  · norm_num
  · have hp := selected_power_le 2 (by decide)
    norm_num only [Nat.cast_ofNat] at hp
    norm_num only [show (4 / 2 : ℝ) = 2 by norm_num]
    nlinarith

theorem expanding_child_fails :
    ¬(20401 : ℝ) ^ 2 ≤ potential 2 1 SelectedStoppedRecurrence.exponent 20401 := by
  intro h
  have hp := selected_power_le 20401 (by decide)
  norm_num only [Nat.cast_ofNat] at hp
  unfold potential at h
  nlinarith

/-- Allowing the supposedly fixed local coefficient to depend on width
makes the local estimate vacuous for a quadratic cost. -/
theorem width_dependent_charge (n : ℕ) : (n : ℝ) ^ 2 ≤ (n : ℝ) * (n + 1) := by
  nlinarith [show (0 : ℝ) ≤ n by positivity]

theorem no_uniform_constant : ¬∃ C : ℝ, 0 ≤ C ∧
    ∀ n : ℕ, (n : ℝ) ^ 2 ≤ potential C 1 SelectedStoppedRecurrence.exponent n := by
  rintro ⟨C, hC, all⟩
  obtain ⟨n, hn⟩ := exists_nat_gt (10200 * C + 1)
  have hn1 : (1 : ℝ) < n := by nlinarith
  have hnNat : 1 ≤ n := by exact_mod_cast hn1.le
  have hCpart := mul_le_mul_of_nonneg_left (selected_power_le n hnNat)
    (by positivity : 0 ≤ 10000 * C)
  have h := all n
  simp only [potential, mul_one] at h
  nlinarith

/-- A nonmonotone cost requires the genuine maximum, not its endpoint. -/
theorem endpoint_is_not_maximum : worst missedLeaf 2 > missedLeaf 2 := by
  have h : missedLeaf 1 ≤ worst missedLeaf 2 := Finset.le_sup' missedLeaf (by decide)
  norm_num [missedLeaf] at h ⊢
  linarith

end RecurrenceCounterexamples

#print axioms RecurrenceCounterexamples.omitted_leaf_fails
#print axioms RecurrenceCounterexamples.omitted_leaf_all_other_widths
#print axioms RecurrenceCounterexamples.expanding_child_recurrence
#print axioms RecurrenceCounterexamples.expanding_child_moments
#print axioms RecurrenceCounterexamples.expanding_child_fails
#print axioms RecurrenceCounterexamples.width_dependent_charge
#print axioms RecurrenceCounterexamples.no_uniform_constant
#print axioms RecurrenceCounterexamples.endpoint_is_not_maximum
