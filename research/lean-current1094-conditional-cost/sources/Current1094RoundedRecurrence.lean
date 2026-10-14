import RoundedRecurrence
import Current1094ProfilePotential

/-!
A thin, source-only PR1094 instantiation of the preserved rounded-width
recurrence theorem. It reuses RoundedRecurrence.network_all_width_bound;
no replacement induction or new rounding lemma is introduced.

Scientific context: ce7ad1b6ab09452c3478723a2e96ed5ff212dc08.
Author-checked selected context:
kappa = 836330098538459/500000000000000000 = 0.001672660197076918.
The exponent below is 1-bCurrent, with the source-bound native endpoint
bCurrent = 67018507072324140917/40000000000000000000000. The selected
outer kappa is not substituted for that endpoint.

A, C, N, finite initial bounds, the rounding/additive-cost budget and an actual
ceil-width scalar recurrence are explicit inputs. No current physical
multiplier, operator/profile realization, cost supplier, bit recurrence,
precision/tape bound or selected-kappa multiplication theorem is supplied.

The current Real enclosure and potential interface are uncompiled proposals;
the historical RoundedRecurrence source has a preserved audit but its object
and wide Mathlib import closure remain unrecovered. This candidate has not
been elaborated or compiled. No runtime fit is claimed.

Attribution: the preserved ranked-pair RoundedRecurrence formalization and
its declared PR62/PR57/PR60/PR63 provenance; PR1094 profile; prior PR585/PR605
and PR799 enclosure machinery; ProfilePotentialTransfer. Apache-2.0.
Prepared with OpenAI assistance for independent source/API review.
-/

set_option Elab.async false
namespace CurrentMain.Current1094RoundedRecurrence
open scoped BigOperators
open Current1094NativeUpperAggregate Current1094NativeRealEnclosure
open Current1094ProfilePotential

/-- The historical characteristic is exactly the current ordered profile sum. -/
theorem current_characteristic_eq_real :
    RoundedRecurrence.expCharacteristic ranks
      (fun r => (Current1094ProfilePotential.multiplicity r : ℝ)) (fun r => (r : ℝ))
      73 14336 (bCurrent : ℝ) = currentRealMoment := by
  have h :
      RoundedRecurrence.expCharacteristic ranks
        (fun r => (Current1094ProfilePotential.multiplicity r : ℝ)) (fun r => (r : ℝ))
        73 14336 (bCurrent : ℝ) = normalizedMoment := by
    norm_num [RoundedRecurrence.expCharacteristic, normalizedMoment,
      ranks, Current1094ProfilePotential.multiplicity, ratio] <;> ring
  exact h.trans normalizedMoment_eq_current

/-- All-width consequence of an explicitly supplied rounded scalar recurrence.
The physical recurrence and its complete finite budget remain caller premises. -/
theorem conditional_all_width_bound
    (f : ℕ → ℝ) (A C : ℝ) (N : ℕ)
    (hA : 0 ≤ A)
    (hthreshold : ∀ r ∈ ranks, ((r : ℝ) / 73) * N + 1 < N)
    (hbudget : C + A * (∑ r ∈ ranks, (Current1094ProfilePotential.multiplicity r : ℝ) / 14336) ≤
      A * (1 - currentRealMoment) * (N : ℝ) ^ (1 - (bCurrent : ℝ)))
    (base : ∀ n, 0 < n → n ≤ N →
      f n ≤ A * (n : ℝ) ^ (1 - (bCurrent : ℝ)))
    (physical_recurrence : ∀ n, N < n → f n ≤ C +
      ∑ r ∈ ranks, ((Current1094ProfilePotential.multiplicity r : ℝ) / 14336) *
        f ⌈((r : ℝ) / 73) * n⌉₊) :
    ∀ n, 0 < n → f n ≤ A * (n : ℝ) ^ (1 - (bCurrent : ℝ)) := by
  have hrank : ∀ r ∈ ranks, (0 : ℝ) < (r : ℝ) ∧ (r : ℝ) < 73 := by
    intro r hr
    simp only [ranks, Finset.mem_insert, Finset.mem_singleton] at hr
    rcases hr with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl <;>
      norm_num
  apply RoundedRecurrence.network_all_width_bound ranks
    (fun r => (Current1094ProfilePotential.multiplicity r : ℝ)) (fun r => (r : ℝ))
    73 14336 (bCurrent : ℝ) A C N f
    (by norm_num) (by norm_num)
    (by norm_num [bCurrent]) (by norm_num [bCurrent]) hA
  · intro r _
    exact Nat.cast_nonneg _
  · intro r hr
    exact (hrank r hr).1
  · intro r hr
    exact (hrank r hr).2
  · rw [current_characteristic_eq_real]
    exact currentRealMoment_strict
  · exact hthreshold
  · simpa only [current_characteristic_eq_real] using hbudget
  · exact base
  · exact physical_recurrence

end CurrentMain.Current1094RoundedRecurrence

#print axioms CurrentMain.Current1094RoundedRecurrence.current_characteristic_eq_real
#print axioms CurrentMain.Current1094RoundedRecurrence.conditional_all_width_bound
