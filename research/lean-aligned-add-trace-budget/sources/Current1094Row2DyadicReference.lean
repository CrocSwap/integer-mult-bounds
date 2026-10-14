import DyadicCellAddition
import Current1094Row2AddReference

/-!
Exact encoded implementation of selected raw2 ADD(L119,L169,1/2). The real
instruction type/program, bank-bound owner literals, family layout and address
separation are the machine reference definitions. Core instructions delegate
to the accepted dyadic SCALE interpreter. addMemory computes an explicit
common exponent and shifted integer sum; it neither assumes common grids nor
modifies either memory cell before the final target write.

Theorems derive full-state decoding for every prefix and the exact raw target
Cell for the whole disjoint-block program. Hence the proved alignment/carry
budget applies to the actual original source/target cells. Untouched cells
retain both numerator and exponent. Scratch retains the last arithmetic result.

This is exact unbounded Int/Nat reference execution. Shift/addition/metadata,
addressing, transport, cleanup and bit-level running time remain to implement
and charge. Common-chart/actual Hosting interpretation retains the predecessor's
explicit hypotheses; source frame0 alone does not discharge them. No rounding,
precision schedule, exact inverse cancellation, all-events implementation or
uniform cost C follows. Finite invoice C0 remains a separate reserve.
Attribution: PR1094 selected word071ecdac; bank owner routing; machine's explicit
ADD and accepted SCALE core; signed dyadic boundary. Apache-2.0, OpenAI-assisted.
Author-checked kappa836330098538459/500000000000000000 is unchanged.
-/
set_option Elab.async false
set_option autoImplicit false
namespace CurrentMain.Current1094Row2DyadicReference
open Current1094Row1DyadicReference DyadicCellAddition
open Current1094Row2AddReference ReferenceMinusHalfStore
open IndependentEntryFold ComponentStoreFoldRefinement Current1094Row1FamilyBlocks

/-- The only new encoded operation is explicit aligned integer addition. -/
def stepAdd : Instruction → EncodedState → EncodedState
  | .core op, s => Current1094Row1DyadicReference.step op s
  | .addMemory a, s => ⟨s.memory, addCell (s.memory a) s.accumulator⟩

def runAdd : List Instruction → EncodedState → EncodedState
  | [], s => s
  | op :: ops, s => runAdd ops (stepAdd op s)

theorem decode_stepAdd (op : Instruction) (s : EncodedState) :
    decodeState (stepAdd op s) = executeInstruction op (decodeState s) := by
  cases op with
  | core op => exact decode_step op s
  | addMemory a =>
      simp only [stepAdd, decodeState, executeInstruction, addMemory, addCell_value]

theorem decode_runAdd (ops : List Instruction) (s : EncodedState) :
    decodeState (runAdd ops s) = execute ops (decodeState s) := by
  induction ops generalizing s with
  | nil => rfl
  | cons op ops ih =>
      rw [runAdd, ih, decode_stepAdd]
      rfl

/-- Simulation applies also to actual interrupted selected-program cuts. -/
theorem selected_prefix_decodes (n k : ℕ) (s : EncodedState) :
    decodeState (runAdd ((selectedProgram n).take k) s) =
      execute ((selectedProgram n).take k) (decodeState s) := decode_runAdd _ _

/-- The four operations determine this exact Cell and visible accumulator. -/
theorem component_state (target source : ℕ) (s : EncodedState) :
    runAdd (componentCode target source) s =
      ⟨Function.update s.memory target (addCell (s.memory target) (halfCell (s.memory source))),
        addCell (s.memory target) (halfCell (s.memory source))⟩ := rfl

private theorem runAdd_append (xs ys : List Instruction) (s : EncodedState) :
    runAdd (xs ++ ys) s = runAdd ys (runAdd xs s) := by
  induction xs generalizing s with
  | nil => rfl
  | cons op ops ih => exact ih (stepAdd op s)

private def runRows {I : Type*} (target source : I → ℕ) :
    List I → EncodedState → EncodedState
  | [], s => s
  | i :: rest, s => runRows target source rest (runAdd (componentCode (target i) (source i)) s)

private theorem run_emit {I : Type*} (target source : I → ℕ)
    (order : List I) (s : EncodedState) :
    runAdd (emit target source order) s = runRows target source order s := by
  induction order generalizing s with
  | nil => rfl
  | cons i rest ih =>
      simpa only [emit, runAdd_append, runRows]
        using ih (runAdd (componentCode (target i) (source i)) s)

private theorem rows_target {I : Type*} [DecidableEq I]
    (target source : I → ℕ) (hinj : Function.Injective target)
    (hsep : ∀ i j, source i ≠ target j) (values : I → Cell)
    (order : List I) (s : EncodedState) (hread : ∀ i, s.memory (source i) = values i) :
    (fun i => (runRows target source order s).memory (target i)) =
      runUpdates (fun i c => addCell c (halfCell (values i))) order
        (fun i => s.memory (target i)) := by
  induction order generalizing s with
  | nil => rfl
  | cons j rest ih =>
      have hnext : ∀ i,
          (runAdd (componentCode (target j) (source j)) s).memory (source i) = values i := by
        intro i
        rw [component_state]
        dsimp only
        rw [Function.update_of_ne (hsep i j)]
        exact hread i
      have hupdate :
          (fun i => (runAdd (componentCode (target j) (source j)) s).memory (target i)) =
          Function.update (fun i => s.memory (target i)) j
            (addCell (s.memory (target j)) (halfCell (values j))) := by
        simp only [component_state]
        rw [hread j]
        exact Function.update_comp_eq_of_injective' s.memory hinj j _
      calc
        (fun i => (runRows target source (j :: rest) s).memory (target i)) =
            runUpdates (fun i c => addCell c (halfCell (values i))) rest
              (fun i => (runAdd (componentCode (target j) (source j)) s).memory (target i)) :=
          ih (runAdd (componentCode (target j) (source j)) s) hnext
        _ = runUpdates (fun i c => addCell c (halfCell (values i))) rest
              (Function.update (fun i => s.memory (target i)) j
                (addCell (s.memory (target j)) (halfCell (values j)))) := by rw [hupdate]
        _ = _ := rfl

/-- Whole-program raw result uses original source and target cells, derived
from disjoint blocks and the existing complete no-duplicate traversal. -/
theorem program_cell (n target source : ℕ) (hne : source ≠ target)
    (s : EncodedState) (slot : Slot (Fin n)) :
    (runAdd (program n target source) s).memory (address n target slot) =
      addCell (s.memory (address n target slot)) (halfCell (s.memory (address n source slot))) := by
  rw [program, run_emit]
  have h := rows_target (address n target) (address n source)
    (Current1094Row1FlatReference.flatAddress_injective n (familyBase n target))
    (address_separation n target source hne)
    (fun i => s.memory (address n source i))
    (Current1094Row1FlatReference.componentOrder n) s (fun _ => rfl)
  exact (congrFun h slot).trans
    (runUpdates_of_mem _ _ (Current1094Row1FlatReference.componentOrder_nodup n)
      slot (Current1094Row1FlatReference.componentOrder_complete n slot) _)

private theorem rows_outside {I : Type*} (target source : I → ℕ)
    (order : List I) (s : EncodedState) (a : ℕ) (ha : a ∉ order.map target) :
    (runRows target source order s).memory a = s.memory a := by
  induction order generalizing s with
  | nil => rfl
  | cons i rest ih =>
      have h : a ≠ target i ∧ a ∉ rest.map target := by
        simpa only [List.map_cons, List.mem_cons, not_or] using ha
      rw [runRows, ih _ h.2, component_state]
      dsimp only
      rw [Function.update_of_ne h.1]

/-- All cells outside the target block retain their exact stored representation. -/
theorem program_outside_cell (n target source : ℕ) (s : EncodedState) (a : ℕ)
    (hout : a < familyBase n target ∨ familyBase n target + 2 * n ≤ a) :
    (runAdd (program n target source) s).memory a = s.memory a := by
  rw [program, run_emit]
  apply rows_outside
  intro ha
  rcases List.mem_map.mp ha with ⟨slot, _, heq⟩
  have hb := Current1094Row1FlatReference.flatAddress_bounds n (familyBase n target) slot
  change Current1094Row1FlatReference.flatAddress (familyBase n target) slot = a at heq
  omega

/-- Source cells and all spectator-family cells retain numerator and exponent. -/
theorem program_other_cell (n target source other : ℕ) (hne : other ≠ target)
    (s : EncodedState) (slot : Slot (Fin n)) :
    (runAdd (program n target source) s).memory (address n other slot) =
      s.memory (address n other slot) := by
  apply program_outside_cell
  exact other_block_outside n target other hne slot

/-- No assumption of equal exponents: selected output uses max(pt,ps+1). -/
theorem selected_cell_grid (n : ℕ) (s : EncodedState) (slot : Slot (Fin n)) :
    ((runAdd (selectedProgram n) s).memory (address n selectedTargetFamily slot)).fractionalBits =
      max (s.memory (address n selectedTargetFamily slot)).fractionalBits
        ((s.memory (address n selectedSourceFamily slot)).fractionalBits + 1) := by
  rw [selectedProgram, program_cell n _ _ selected_families_ne]
  rfl

/-- Concrete selected numerator budget, including alignment shifts and one
carry bit. Exponent/sign/address metadata are outside this magnitude budget. -/
theorem selected_cell_bit_budget (n : ℕ) (s : EncodedState) (slot : Slot (Fin n))
    (bt bs : ℕ)
    (ht : (s.memory (address n selectedTargetFamily slot)).numerator.natAbs < 2 ^ bt)
    (hs : (s.memory (address n selectedSourceFamily slot)).numerator.natAbs < 2 ^ bs) :
    let target := s.memory (address n selectedTargetFamily slot)
    let source := s.memory (address n selectedSourceFamily slot)
    let q := max target.fractionalBits (source.fractionalBits + 1)
    ((runAdd (selectedProgram n) s).memory (address n selectedTargetFamily slot)).numerator.natAbs <
      2 ^ (max (bt + (q - target.fractionalBits))
        (bs + (q - (source.fractionalBits + 1))) + 1) := by
  dsimp only
  rw [selectedProgram, program_cell n _ _ selected_families_ne]
  exact addCell_bit_budget _ _ bt bs ht hs

/-- The actual selected program refines its accepted exact-real family update.
No decoded endpoint is supplied as a hypothesis. -/
theorem selected_decoded_family_update (n : ℕ) (s : EncodedState) :
    familyViews n (decodeState (runAdd (selectedProgram n) s)).memory =
      Function.update (familyViews n (decodeState s).memory) selectedTargetFamily
        (familyViews n (decodeState s).memory selectedTargetFamily +
          ((1 / 2 : ℝ) : ℂ) • familyViews n (decodeState s).memory selectedSourceFamily) := by
  rw [decode_runAdd]
  exact selected_familyViews_update n (decodeState s)

end CurrentMain.Current1094Row2DyadicReference

#print axioms CurrentMain.Current1094Row2DyadicReference.decode_stepAdd
#print axioms CurrentMain.Current1094Row2DyadicReference.decode_runAdd
#print axioms CurrentMain.Current1094Row2DyadicReference.selected_prefix_decodes
#print axioms CurrentMain.Current1094Row2DyadicReference.component_state
#print axioms CurrentMain.Current1094Row2DyadicReference.program_cell
#print axioms CurrentMain.Current1094Row2DyadicReference.program_outside_cell
#print axioms CurrentMain.Current1094Row2DyadicReference.program_other_cell
#print axioms CurrentMain.Current1094Row2DyadicReference.selected_cell_grid
#print axioms CurrentMain.Current1094Row2DyadicReference.selected_cell_bit_budget
#print axioms CurrentMain.Current1094Row2DyadicReference.selected_decoded_family_update
