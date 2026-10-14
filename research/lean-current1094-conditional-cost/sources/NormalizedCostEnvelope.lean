import Mathlib.Data.Real.Archimedean
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.BigOperators.Field
import Mathlib.Tactic.Ring

/-!
Source-only normalized-cost envelope transfer. UNCOMPILED.

Admissible states include every timing-relevant parameter, in particular the
positive logical volume, payload, ancestors and physical layout. The state
type and predicates below supply none of those physical invariants themselves.

The envelope is the real supremum of actual cost/volume ratios, rather than an
arbitrary upper-bound sequence. A one-step physical cost decomposition and
bounded child-rate sets give a finite parent upper bound, its genuine least
upper bound, and the scalar recurrence. No maximizing state is assumed.

Current intended context: PR1094, immutable scientific main
ce7ad1b6ab09452c3478723a2e96ed5ff212dc08, author-checked outer
kappa = 836330098538459/500000000000000000. This generic file does not
instantiate that profile or prove its physical decomposition, uniform cost,
base bounds, precision, or final multiplication complexity. The native
recurrence exponent 1-bCurrent is not the outer kappa.

Attribution: the reviewed PR1379 two-parameter normalization map, its physical
source review, the preserved ranked-pair RoundedRecurrence formalization,
and Mathlib's real completeness and finite-sum lemmas. Apache-2.0.
Prepared with OpenAI assistance. No compiler or supplier execution.
-/

set_option Elab.async false

namespace NormalizedCostEnvelope
open scoped BigOperators

variable {State : Type*}

/-- Only rates of admissible states enter this set. Positivity of volume is
required separately whenever the normalized rate is used as a cost bound. -/
def rates (admissible : ℕ → State → Prop) (cost volume : State → ℝ)
    (n : ℕ) : Set ℝ :=
  {z | ∃ x, admissible n x ∧ cost x / volume x = z}

/-- This total expression is interpreted as a least upper bound only after
the explicit nonemptiness and boundedness hypotheses have been established. -/
noncomputable def envelope (admissible : ℕ → State → Prop)
    (cost volume : State → ℝ) (n : ℕ) : ℝ :=
  sSup (rates admissible cost volume n)

theorem rates_nonempty (admissible : ℕ → State → Prop)
    (cost volume : State → ℝ) (n : ℕ)
    (hne : ∃ x, admissible n x) : (rates admissible cost volume n).Nonempty := by
  obtain ⟨x, hx⟩ := hne
  exact ⟨cost x / volume x, x, hx, rfl⟩

/-- A uniform majorant proves boundedness; no recurrence for that majorant
is claimed. The majorant need not be attained by any admissible state. -/
theorem rates_bddAbove_of_uniform_bound (admissible : ℕ → State → Prop)
    (cost volume : State → ℝ) (n : ℕ) (B : ℝ)
    (hB : ∀ x, admissible n x → cost x / volume x ≤ B) :
    BddAbove (rates admissible cost volume n) := by
  refine ⟨B, ?_⟩
  rintro z ⟨x, hx, rfl⟩
  exact hB x hx

theorem envelope_isLUB (admissible : ℕ → State → Prop)
    (cost volume : State → ℝ) (n : ℕ)
    (hne : ∃ x, admissible n x)
    (hbdd : BddAbove (rates admissible cost volume n)) :
    IsLUB (rates admissible cost volume n) (envelope admissible cost volume n) := by
  exact isLUB_csSup (rates_nonempty admissible cost volume n hne) hbdd

theorem rate_le_envelope (admissible : ℕ → State → Prop)
    (cost volume : State → ℝ) (n : ℕ)
    (hbdd : BddAbove (rates admissible cost volume n))
    (x : State) (hx : admissible n x) :
    cost x / volume x ≤ envelope admissible cost volume n := by
  exact le_csSup hbdd ⟨x, hx, rfl⟩

/-- A bound on this envelope transports back to every actual positive-volume
state. It does not turn an arbitrary majorant into a recurrence solution. -/
theorem cost_le_of_envelope_le (admissible : ℕ → State → Prop)
    (cost volume : State → ℝ) (n : ℕ)
    (hbdd : BddAbove (rates admissible cost volume n))
    (x : State) (hx : admissible n x) (hvolume : 0 < volume x)
    (B : ℝ) (hB : envelope admissible cost volume n ≤ B) :
    cost x ≤ B * volume x := by
  exact (div_le_iff₀ hvolume).mp
    ((rate_le_envelope admissible cost volume n hbdd x hx).trans hB)

/-- The substantive transfer step. The same finite C, W, multiplicities and
child widths work for EVERY admissible parent state at this width. Children
may otherwise depend on its complete state. Their admissibility, exact
positive volume ratio and complete cost decomposition remain explicit.

Only child sets are assumed bounded. The parent bound is derived below.
The finite sum is over ranks and copies, so distinct calls remain distinct
even if two child states happen to be equal. No attainment or independence
of children/errors is used. There is no assumed scalar recurrence here.
-/
theorem envelope_step {ι : Type*} (s : Finset ι) (multiplicity : ι → ℕ)
    (admissible : ℕ → State → Prop) (cost volume : State → ℝ)
    (n : ℕ) (childWidth : ι → ℕ) (W C : ℝ)
    (hW : 0 < W)
    (hne : ∃ x, admissible n x)
    (hvolume : ∀ x, admissible n x → 0 < volume x)
    (hchild_bdd : ∀ r ∈ s,
      BddAbove (rates admissible cost volume (childWidth r)))
    (physical_cost : ∀ x, admissible n x →
      ∃ child : ι → ℕ → State,
        (∀ r ∈ s, ∀ j ∈ Finset.range (multiplicity r),
          admissible (childWidth r) (child r j) ∧
          volume (child r j) = volume x / W) ∧
        cost x ≤ C * volume x +
          ∑ r ∈ s, ∑ j ∈ Finset.range (multiplicity r), cost (child r j)) :
    BddAbove (rates admissible cost volume n) ∧
    IsLUB (rates admissible cost volume n) (envelope admissible cost volume n) ∧
    envelope admissible cost volume n ≤ C +
      ∑ r ∈ s, ((multiplicity r : ℝ) / W) *
        envelope admissible cost volume (childWidth r) := by
  classical
  have hpoint : ∀ x, admissible n x → cost x / volume x ≤ C +
      ∑ r ∈ s, ((multiplicity r : ℝ) / W) *
        envelope admissible cost volume (childWidth r) := by
    intro x hx
    have hV := hvolume x hx
    obtain ⟨child, hchild, hcost⟩ := physical_cost x hx
    have hterm : ∀ r ∈ s, ∀ j ∈ Finset.range (multiplicity r),
        cost (child r j) ≤
          (envelope admissible cost volume (childWidth r) / W) * volume x := by
      intro r hr j hj
      obtain ⟨hadm, hratio⟩ := hchild r hr j hj
      have hchildV : 0 < volume (child r j) := by
        rw [hratio]
        exact div_pos hV hW
      have hrate := rate_le_envelope admissible cost volume (childWidth r)
        (hchild_bdd r hr) (child r j) hadm
      calc
        cost (child r j) ≤
            envelope admissible cost volume (childWidth r) * volume (child r j) :=
          (div_le_iff₀ hchildV).mp hrate
        _ = (envelope admissible cost volume (childWidth r) / W) * volume x := by
          rw [hratio]
          ring
    apply (div_le_iff₀ hV).mpr
    calc
      cost x ≤ C * volume x +
          ∑ r ∈ s, ∑ j ∈ Finset.range (multiplicity r), cost (child r j) := hcost
      _ ≤ C * volume x + ∑ r ∈ s, ∑ _j ∈ Finset.range (multiplicity r),
          (envelope admissible cost volume (childWidth r) / W) * volume x := by
        apply add_le_add_left
        apply Finset.sum_le_sum
        intro r hr
        exact Finset.sum_le_sum (fun j hj => hterm r hr j hj)
      _ = (C + ∑ r ∈ s, ((multiplicity r : ℝ) / W) *
          envelope admissible cost volume (childWidth r)) * volume x := by
        simp only [Finset.sum_const, Finset.card_range, nsmul_eq_mul]
        rw [add_mul, Finset.sum_mul]
        congr 1
        apply Finset.sum_congr rfl
        intro r hr
        ring
  have hbdd := rates_bddAbove_of_uniform_bound admissible cost volume n _ hpoint
  refine ⟨hbdd, envelope_isLUB admissible cost volume n hne hbdd, ?_⟩
  apply csSup_le (rates_nonempty admissible cost volume n hne)
  rintro z ⟨x, hx, rfl⟩
  exact hpoint x hx

end NormalizedCostEnvelope

#print axioms NormalizedCostEnvelope.rates_nonempty
#print axioms NormalizedCostEnvelope.rates_bddAbove_of_uniform_bound
#print axioms NormalizedCostEnvelope.envelope_isLUB
#print axioms NormalizedCostEnvelope.rate_le_envelope
#print axioms NormalizedCostEnvelope.cost_le_of_envelope_le
#print axioms NormalizedCostEnvelope.envelope_step
