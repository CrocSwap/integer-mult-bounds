import NormalizedCostEnvelopeDescent
import RoundedRecurrenceExistentialBudget
import Current1094SelectedExponent

/-!
Conditional assembly from complete physical cost suppliers to the exact
selected PR1094 exponent. No envelope recurrence or native_bound is assumed.
The accepted envelope/descent chain derives the recurrence; the accepted
existential-budget theorem constructs its finite A; the checked endpoint
bridge then weakens the native exponent to the author-checked selected kappa
836330098538459/500000000000000000.

State must encode EVERY timing-relevant variable: payload, volume, precision,
rounding/guard-bit policy, routing/layout, live ancestoral storage and machine
configuration. The predicate admissible is a supplied actual domain of such
states, with positive natural volume and a state at each positive width.
Its implementation is not constructed by this theorem. The functions cost
and localWork are supplied natural step counts of the actual complete program
and its non-child work. To instantiate them, the caller must prove their
correspondence to actual execution; an invoice or partial primitive count is
not sufficient. localWork must charge routing, markers, address movement,
conversion, precision setup, rounding, error control and every other operation
outside the counted complete child calls. The one constant C is uniform over
all admitted widths and complete states, including their admitted precision.

The base coefficients bound the ENTIRE admissible family at each positive
base width, not merely finitely many examples. Each selected child occurrence
is counted independently, is admissible at its exact upward-rounded width,
and has exact real volume parent/14336. For these natural volumes the latter
is a genuine divisibility/positive-role obligation, not integer division or
an unproved equal-row approximation. Neither child independence nor supremum
attainment is assumed. The source-defined eight-rank profile is fixed.

Scientific source ce7ad1b6ab09452c3478723a2e96ed5ff212dc08, preserved by later
source-applicability checks. This is a source-only successor until compiled.
It is a conditional normalized-width theorem, not an unconditional physical
multiplier or a full selected-kappa bit-complexity theorem.
Attribution: PR1094; PR585/PR605 and repaired PR799 enclosures; PR1379
normalization review; NormalizedCostEnvelope/Descent; ranked-pair
RoundedRecurrence; existential-budget and selected-exponent bridges.
Apache-2.0. Prepared with OpenAI assistance.
-/

set_option Elab.async false
set_option autoImplicit false
namespace CurrentMain.Current1094PhysicalCostBound
open scoped BigOperators
open NormalizedCostEnvelope NormalizedCostEnvelopeDescent
open Current1094ProfilePotential Current1094NativeUpperAggregate
open Current1094NativeRealEnclosure Current1094RoundedRecurrence
open Current1094SelectedExponent

private theorem rank_conditions (r : ℕ) (hr : r ∈ ranks) :
    (0 : ℝ) < r ∧ (r : ℝ) < 73 ∧ ((r : ℝ) / 73) * 3 + 1 < 3 := by
  simp only [ranks, Finset.mem_insert, Finset.mem_singleton] at hr
  rcases hr with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl <;> norm_num

/-- The fixed profile's upward-rounded children descend above width three.
This uses the accepted rounding lemma; no new induction is introduced. -/
theorem selected_child_descent (n r : ℕ) (hn : 3 < n) (hr : r ∈ ranks) :
    0 < ⌈((r : ℝ) / 73) * n⌉₊ ∧ ⌈((r : ℝ) / 73) * n⌉₊ < n := by
  obtain ⟨hpos, hlt, hthreshold⟩ := rank_conditions r hr
  exact RoundedRecurrence.rounded_child_lt ((r : ℝ) / 73) 3 n
    (div_pos hpos (by norm_num)) ((div_lt_one (by norm_num)).mpr hlt)
    (by simpa using hthreshold) hn

/-- A finite uniform selected-exponent cost bound follows from the explicit
base-family, full-state local-work and complete physical child-call suppliers.
All scalar recurrence, least-upper-bound, threshold and power-budget steps
are derived internally from previously accepted lemmas. -/
theorem selected_cost_bound_from_physical_suppliers
    {State : Type} (admissible : ℕ → State → Prop)
    (cost volume localWork : State → ℕ)
    (baseCoefficient : ℕ → ℕ) (C N₀ : ℕ)
    (hN₀ : 3 ≤ N₀)
    (hne : ∀ n, 0 < n → ∃ x, admissible n x)
    (hvolume : ∀ n, 0 < n → ∀ x, admissible n x → 0 < volume x)
    (base_cost : ∀ n, 0 < n → n ≤ N₀ → ∀ x, admissible n x →
      cost x ≤ baseCoefficient n * volume x)
    (local_work : ∀ n, N₀ < n → ∀ x, admissible n x →
      localWork x ≤ C * volume x)
    (physical_children : ∀ n, N₀ < n → ∀ x, admissible n x →
      ∃ child : ℕ → ℕ → State,
        (∀ r ∈ ranks, ∀ j ∈ Finset.range (Current1094ProfilePotential.multiplicity r),
          admissible ⌈((r : ℝ) / 73) * n⌉₊ (child r j) ∧
          (volume (child r j) : ℝ) = (volume x : ℝ) / 14336) ∧
        cost x ≤ localWork x + ∑ r ∈ ranks,
          ∑ j ∈ Finset.range (Current1094ProfilePotential.multiplicity r), cost (child r j)) :
    ∃ A : ℝ, 0 ≤ A ∧ ∀ n, 0 < n → ∀ x, admissible n x →
      (cost x : ℝ) ≤ A * (n : ℝ) ^ (1 - (selectedKappa : ℝ)) * (volume x : ℝ) := by
  let realCost : State → ℝ := fun x => (cost x : ℝ)
  let realVolume : State → ℝ := fun x => (volume x : ℝ)
  let childWidth : ℕ → ℕ → ℕ := fun n r => ⌈((r : ℝ) / 73) * n⌉₊
  have hvol : ∀ n, 0 < n → ∀ x, admissible n x → 0 < realVolume x := by
    intro n hn x hx
    dsimp [realVolume]
    exact_mod_cast hvolume n hn x hx
  have hbase : ∀ n, 0 < n → n ≤ N₀ →
      BddAbove (rates admissible realCost realVolume n) := by
    intro n hn hnN
    apply rates_bddAbove_of_uniform_bound admissible realCost realVolume n
      (baseCoefficient n : ℝ)
    intro x hx
    apply (div_le_iff₀ (hvol n hn x hx)).mpr
    dsimp [realCost, realVolume]
    exact_mod_cast base_cost n hn hnN x hx
  have hdescent : ∀ n, N₀ < n → ∀ r ∈ ranks,
      0 < childWidth n r ∧ childWidth n r < n := by
    intro n hn r hr
    exact selected_child_descent n r (lt_of_le_of_lt hN₀ hn) hr
  have hphysical : PhysicalCostDecomposition ranks Current1094ProfilePotential.multiplicity
      admissible realCost realVolume childWidth 14336 (C : ℝ) N₀ := by
    intro n hn x hx
    obtain ⟨child, hchildren, hcost⟩ := physical_children n hn x hx
    refine ⟨child, hchildren, ?_⟩
    have hraw : realCost x ≤ (localWork x : ℝ) + ∑ r ∈ ranks,
        ∑ j ∈ Finset.range (Current1094ProfilePotential.multiplicity r), realCost (child r j) := by
      dsimp [realCost]
      exact_mod_cast hcost
    have hwork : (localWork x : ℝ) ≤ (C : ℝ) * realVolume x := by
      dsimp [realVolume]
      exact_mod_cast local_work n hn x hx
    exact hraw.trans (add_le_add_right hwork _)
  have hfamily := envelope_family_of_base_and_descent ranks
    Current1094ProfilePotential.multiplicity admissible realCost realVolume
    childWidth 14336 (C : ℝ) N₀ (by norm_num) hne hvol hbase hdescent hphysical
  let f : ℕ → ℝ := envelope admissible realCost realVolume
  have hcharacteristic : RoundedRecurrence.expCharacteristic ranks
      (fun r => (Current1094ProfilePotential.multiplicity r : ℝ)) (fun r => (r : ℝ))
      73 14336 (bCurrent : ℝ) < 1 := by
    rw [current_characteristic_eq_real]
    exact currentRealMoment_strict
  obtain ⟨A, hA, hnative⟩ :=
    RoundedRecurrenceExistentialBudget.exists_network_power_majorant ranks
      (fun r => (Current1094ProfilePotential.multiplicity r : ℝ)) (fun r => (r : ℝ))
      73 14336 (bCurrent : ℝ) (C : ℝ) N₀ f
      (by norm_num) (by norm_num)
      (lt_trans endpoint_relation.2.1 endpoint_relation.2.2.1).le
      endpoint_relation.2.2.2
      (fun r _ => Nat.cast_nonneg _)
      (fun r hr => (rank_conditions r hr).1)
      (fun r hr => (rank_conditions r hr).2.1)
      hcharacteristic hfamily.2.2
  have hselected := native_power_bound_implies_selected f A hA hnative
  refine ⟨A, hA, ?_⟩
  intro n hn x hx
  exact cost_le_of_envelope_le admissible realCost realVolume n
    (hfamily.1 n hn) x hx (hvol n hn x hx)
    (A * (n : ℝ) ^ (1 - (selectedKappa : ℝ))) (hselected n hn)

end CurrentMain.Current1094PhysicalCostBound

#print axioms CurrentMain.Current1094PhysicalCostBound.selected_child_descent
#print axioms CurrentMain.Current1094PhysicalCostBound.selected_cost_bound_from_physical_suppliers
