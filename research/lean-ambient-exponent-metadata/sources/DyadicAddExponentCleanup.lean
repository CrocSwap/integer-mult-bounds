import DyadicAddSavedExponent
import Current1094Row2DyadicReference
import Init.Data.Nat.Bitwise.Lemmas

/-!
Explicit exponent-metadata cleanup after the accepted raw-Cell ADD undo.
The metadata instruction XORs the saved Nat register with the current target
exponent. It is an involution on every boundary state, saves an exponent when
started at zero, and clears it when that same exponent has been restored.

The boundary state contains the POST-ADD accumulator. Neither instruction
changes it or the source. The selected-reference join obtains both Cells from
the checked ADD program and retains its actual final accumulator; it does not
claim recovery of the accumulator that preceded the read/halve/add/write tape.
The saved exponent is the only retained target metadata; no old numerator or
assumed cleanup result is passed to the two-instruction cleanup program.

This is a new local reference instruction/domain. Its target restoration is
proved only on the literal aligned-ADD forward image. Lifting these boundary
operations back into flat memory, implementing the Nat XOR/Int division on a
bit machine, initializing/allocating metadata and recovering old scratch remain
separate. No primitive bit-cost, rounding or selected-runtime claim is made.
Reuses accepted analytic Cell/ADD and machine saved-exponent undo unchanged.
Apache-2.0; OpenAI-assisted. Selected kappa context remains
836330098538459/500000000000000000. Uncompiled source candidate.
-/
set_option Elab.async false
set_option autoImplicit false
namespace CurrentMain.DyadicAddExponentCleanup
open Current1094Row1DyadicReference DyadicCellAddition DyadicAddSavedExponent

/-- The accumulator is the actual dirty value at the post-ADD boundary. -/
structure BoundaryState where
  target : Cell
  source : Cell
  accumulator : Cell
  savedExponent : ℕ

inductive MetadataInstruction where
  | toggleExponent
  | restoreTarget

/-- Both operations leave the source and post-ADD accumulator untouched. -/
def step : MetadataInstruction → BoundaryState → BoundaryState
  | .toggleExponent, s =>
      { s with savedExponent := s.savedExponent ^^^ s.target.fractionalBits }
  | .restoreTarget, s =>
      { s with target := restoreCell s.target (halfCell s.source) s.savedExponent }

def run : List MetadataInstruction → BoundaryState → BoundaryState
  | [], s => s
  | op :: ops, s => run ops (step op s)

def Clean (s : BoundaryState) : Prop := s.savedExponent = 0

/-- A literal forward-image domain, with no inverse/cleanup equation assumed. -/
def Admissible (s : BoundaryState) : Prop :=
  ∃ original : Cell,
    s.target = addCell original (halfCell s.source) ∧
    s.savedExponent = original.fractionalBits

/-- The accumulator may be arbitrary; it is not silently reset to zero. -/
def forwardBoundary (target source dirty : Cell) : BoundaryState :=
  ⟨addCell target (halfCell source), source, dirty, target.fractionalBits⟩

def cleanupProgram : List MetadataInstruction := [.restoreTarget, .toggleExponent]

/-- Unlike destructive assignment to zero, the metadata operation is reversible. -/
theorem toggle_involutive (s : BoundaryState) :
    step .toggleExponent (step .toggleExponent s) = s := by
  cases s
  simp only [step, Nat.xor_assoc, Nat.xor_self, Nat.xor_zero]

/-- Recording the exponent requires a clean metadata register. -/
theorem toggle_saves (s : BoundaryState) (h : Clean s) :
    (step .toggleExponent s).savedExponent = s.target.fractionalBits := by
  change s.savedExponent ^^^ s.target.fractionalBits = s.target.fractionalBits
  rw [h, Nat.zero_xor]

/-- Clearing is justified by an explicit current-exponent match. -/
theorem toggle_clears (s : BoundaryState)
    (h : s.savedExponent = s.target.fractionalBits) :
    Clean (step .toggleExponent s) := by
  change s.savedExponent ^^^ s.target.fractionalBits = 0
  rw [h, Nat.xor_self]

/-- Every prefix preserves the source Cell and the supplied dirty accumulator. -/
theorem run_preserves_source_accumulator (ops : List MetadataInstruction)
    (s : BoundaryState) :
    (run ops s).source = s.source ∧ (run ops s).accumulator = s.accumulator := by
  induction ops generalizing s with
  | nil => exact ⟨rfl, rfl⟩
  | cons op ops ih =>
      have h := ih (step op s)
      cases op <;> simpa only [run, step] using h

/-- The accepted raw-Cell inverse restores the exponent; XOR then clears it.
No equality asserting cleanup, original numerator or divisibility is supplied. -/
theorem cleanup_forward (target source dirty : Cell) :
    run cleanupProgram (forwardBoundary target source dirty) =
      BoundaryState.mk target source dirty 0 := by
  simp only [cleanupProgram, run, step, forwardBoundary, restore_addCell,
    Nat.xor_self]

/-- The domain permits restoration and cleanup while retaining dirty scratch. -/
theorem cleanup_admissible (s : BoundaryState) (h : Admissible s) :
    ∃ original : Cell,
      run cleanupProgram s = BoundaryState.mk original s.source s.accumulator 0 := by
  rcases s with ⟨updated, source, dirty, saved⟩
  rcases h with ⟨original, ht, hm⟩
  dsimp only at ht hm
  subst updated
  subst saved
  exact ⟨original, cleanup_forward original source dirty⟩

open Current1094Row2AddReference Current1094Row2DyadicReference
open ComponentStoreFoldRefinement

/-- The actual checked selected-reference ADD supplies the forward image and
unchanged source. The final accumulator is preserved verbatim, not recovered.
The metadata input is explicitly the original target exponent. -/
theorem selected_program_cleanup (n : ℕ) (s : EncodedState) (slot : Slot (Fin n)) :
    let out := runAdd (selectedProgram n) s
    run cleanupProgram
      ⟨out.memory (address n selectedTargetFamily slot),
        out.memory (address n selectedSourceFamily slot), out.accumulator,
        (s.memory (address n selectedTargetFamily slot)).fractionalBits⟩ =
      BoundaryState.mk (s.memory (address n selectedTargetFamily slot))
        (s.memory (address n selectedSourceFamily slot)) out.accumulator 0 := by
  dsimp only
  simp only [selectedProgram]
  rw [program_cell n selectedTargetFamily selectedSourceFamily selected_families_ne,
    program_other_cell n selectedTargetFamily selectedSourceFamily selectedSourceFamily
      selected_families_ne]
  exact cleanup_forward _ _ _

end CurrentMain.DyadicAddExponentCleanup

#print axioms CurrentMain.DyadicAddExponentCleanup.toggle_involutive
#print axioms CurrentMain.DyadicAddExponentCleanup.toggle_saves
#print axioms CurrentMain.DyadicAddExponentCleanup.toggle_clears
#print axioms CurrentMain.DyadicAddExponentCleanup.run_preserves_source_accumulator
#print axioms CurrentMain.DyadicAddExponentCleanup.cleanup_forward
#print axioms CurrentMain.DyadicAddExponentCleanup.cleanup_admissible
#print axioms CurrentMain.DyadicAddExponentCleanup.selected_program_cleanup
#check @CurrentMain.DyadicAddExponentCleanup.cleanup_admissible
#check @CurrentMain.DyadicAddExponentCleanup.selected_program_cleanup
