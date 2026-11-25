import FreshComponentStoreFoldRefinement
import Mathlib.Tactic.Ring

/-!
Explicit reference semantics for one exact real-component SCALE(-1/2).
These are newly authored reference operations, not an extracted selected
physical executor. The selected emitter supplies the macro coefficient and
an arithmetic-operation count, but no component-address/read/write routine.

The read, halve and negate operations leave memory unchanged. The final write
stores the accumulator at exactly the requested slot. The accumulator remains
dirty afterward; no cleanup, scratch restoration or cost theorem is implied.
The memory refinement is proved from these definitions and the existing fold.

Exact arithmetic can refine a p-grid input to a (p+1)-grid output. No same-grid
closure, truncation, rounding or physical address admission is assumed here.
Prepared with OpenAI assistance. Apache-2.0. Uncompiled source proposal.
-/

noncomputable section
namespace CurrentMain.ReferenceMinusHalfStore

open IndependentEntryFold ComponentStoreFoldRefinement

structure RefState (I : Type*) where
  memory : I → ℝ
  accumulator : ℝ

variable {I : Type*} [DecidableEq I]

def readSlot (i : I) (s : RefState I) : RefState I :=
  ⟨s.memory, s.memory i⟩

def halve (s : RefState I) : RefState I :=
  ⟨s.memory, s.accumulator / 2⟩

def negate (s : RefState I) : RefState I :=
  ⟨s.memory, -s.accumulator⟩

def writeSlot (i : I) (s : RefState I) : RefState I :=
  ⟨Function.update s.memory i s.accumulator, s.accumulator⟩

/-- Chosen reference order: read, halve, negate, write. -/
def scalarStep (i : I) (s : RefState I) : RefState I :=
  writeSlot i (negate (halve (readSlot i s)))

/-- The first three real microsteps are memory stutters. -/
theorem memory_before_write (i : I) (s : RefState I) :
    (readSlot i s).memory = s.memory ∧
    (halve (readSlot i s)).memory = s.memory ∧
    (negate (halve (readSlot i s))).memory = s.memory := by
  exact ⟨rfl, rfl, rfl⟩

/-- Genuine memory refinement: derived from four explicit operations, without
assuming the final update or endpoint-mixture equation. -/
theorem scalarStep_memory (i : I) (s : RefState I) :
    (scalarStep i s).memory =
      Function.update s.memory i ((-1 / 2 : ℝ) * s.memory i) := by
  change Function.update s.memory i (-(s.memory i / 2)) =
    Function.update s.memory i ((-1 / 2 : ℝ) * s.memory i)
  have he : -(s.memory i / 2) = (-1 / 2 : ℝ) * s.memory i := by ring
  rw [he]

/-- Final scratch is visible in the contract, not silently declared erased. -/
theorem scalarStep_accumulator (i : I) (s : RefState I) :
    (scalarStep i s).accumulator = (-1 / 2 : ℝ) * s.memory i := by
  change -(s.memory i / 2) = (-1 / 2 : ℝ) * s.memory i
  ring

theorem scalarStep_unchanged (i j : I) (hne : j ≠ i) (s : RefState I) :
    (scalarStep i s).memory j = s.memory j := by
  rw [scalarStep_memory, Function.update_of_ne hne]

def referenceRun : List I → RefState I → RefState I
  | [], s => s
  | i :: rest, s => referenceRun rest (scalarStep i s)

/-- Each macro is refined before the list composition. No no-duplicate
assumption is needed for this exact operational correspondence. -/
theorem referenceRun_memory (order : List I) (s : RefState I) :
    (referenceRun order s).memory =
      runUpdates (fun _ v => (-1 / 2 : ℝ) * v) order s.memory := by
  induction order generalizing s with
  | nil => rfl
  | cons i rest ih =>
      rw [referenceRun, ih, scalarStep_memory]
      rfl

/-- Completed writes of this explicit reference routine satisfy the derived
component mixture. Before-write cuts stutter by memory_before_write. The
accumulator is separate from the Euclidean memory vector bounded by PR1309. -/
theorem reference_prefix_components {Coord : Type*}
    [Fintype Coord] [DecidableEq Coord]
    (order : List (Slot Coord)) (hnd : order.Nodup)
    (old : EuclideanSpace ℂ Coord) (scratch : ℝ) (k : ℕ) :
    decode (referenceRun (order.take k) (⟨encode old, scratch⟩ : RefState (Slot Coord))).memory =
      PrefixNorm.components (realDone (order.take k)) (imagDone (order.take k))
        old (((-1 / 2 : ℝ) : ℂ) • old) := by
  rw [referenceRun_memory]
  exact selected_minus_half_prefix order hnd old k

end CurrentMain.ReferenceMinusHalfStore

#print axioms CurrentMain.ReferenceMinusHalfStore.memory_before_write
#print axioms CurrentMain.ReferenceMinusHalfStore.scalarStep_memory
#print axioms CurrentMain.ReferenceMinusHalfStore.scalarStep_accumulator
#print axioms CurrentMain.ReferenceMinusHalfStore.scalarStep_unchanged
#print axioms CurrentMain.ReferenceMinusHalfStore.referenceRun_memory
#print axioms CurrentMain.ReferenceMinusHalfStore.reference_prefix_components
#check @CurrentMain.ReferenceMinusHalfStore.scalarStep_memory
#check @CurrentMain.ReferenceMinusHalfStore.reference_prefix_components
