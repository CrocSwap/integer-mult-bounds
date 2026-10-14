import Current1094Row1FlatReference

/-!
Concrete per-cell integer-numerator/fractional-exponent implementation of the
selected call000 raw1 SCALE(-1/2) reference instruction stream. The decoded
real interpreter, exact flat address order and source macro binding are reused.
Each memory cell and the visible accumulator have their own exponent. Halving
increments only the accumulator exponent; writing copies that pair into one
cell. There is no global exponent change that would alter untouched cells.

This is a newly defined exact dyadic representation, not an extracted selected
bit implementation. It uses unbounded Int/Nat operations and proves their exact
real interpretation. No truncation, same-grid closure, finite-word overflow
bound, bit-operation timing, scratch erasure or inverse cancellation is assumed
or concluded. The instruction stream has the already proved 8*n abstract
operations; its arithmetic and exponent-update costs still require bit-level
refinement. The selected invoice's C0=2^210000 is a precision/tape reserve,
not the uniform local-work cost C in the normalized physical-cost theorem.

The one written cell changes (z,p) to (-z,p+1), retaining numerator magnitude.
This implements the arithmetic direction of signed's SelectedMinusHalfGrid
source lemma without importing that currently uncompiled object. The actual
selected encoding, all other scalar/non-scalar events, precision scheduling,
padding and physical tapes remain separate. No selected 512-bit p is inferred.

Attribution: selected PR1094 forward word071ecdac, raw1 L119 scale(-1/2);
machine's accepted exact flat reference and generic independent updates;
signed's rational-grid source boundary. Apache-2.0. OpenAI-assisted.
Author-checked selected kappa836330098538459/500000000000000000 is unchanged.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.Current1094Row1DyadicReference
open Current1094Row1FlatReference ReferenceMinusHalfStore
open IndependentEntryFold ComponentStoreFoldRefinement

structure Cell where
  numerator : ℤ
  fractionalBits : ℕ

structure EncodedState where
  memory : ℕ → Cell
  accumulator : Cell

noncomputable def value (c : Cell) : ℝ :=
  (c.numerator : ℝ) / (2 : ℝ) ^ c.fractionalBits

noncomputable def decodeState (s : EncodedState) : RefState ℕ :=
  ⟨fun a => value (s.memory a), value s.accumulator⟩

def halfCell (c : Cell) : Cell := ⟨c.numerator, c.fractionalBits + 1⟩
def negCell (c : Cell) : Cell := ⟨-c.numerator, c.fractionalBits⟩
def minusHalfCell (c : Cell) : Cell := ⟨-c.numerator, c.fractionalBits + 1⟩

/-- Integer/exponent state transitions, sharing the exact existing instruction
constructors. No real arithmetic occurs in this implementation. -/
def step : Instruction → EncodedState → EncodedState
  | .read a, s => ⟨s.memory, s.memory a⟩
  | .halve, s => ⟨s.memory, halfCell s.accumulator⟩
  | .negate, s => ⟨s.memory, negCell s.accumulator⟩
  | .write a, s => ⟨Function.update s.memory a s.accumulator, s.accumulator⟩

def run : List Instruction → EncodedState → EncodedState
  | [], s => s
  | op :: ops, s => run ops (step op s)

private theorem value_half (c : Cell) : value (halfCell c) = value c / 2 := by
  change (c.numerator : ℝ) / (2 : ℝ) ^ (c.fractionalBits + 1) =
    ((c.numerator : ℝ) / (2 : ℝ) ^ c.fractionalBits) / 2
  rw [pow_succ, div_mul_eq_div_div]

private theorem value_neg (c : Cell) : value (negCell c) = -value c := by
  simp only [value, negCell, Int.cast_neg, neg_div]

/-- Full memory AND visible scratch decode correctly after every instruction. -/
theorem decode_step (op : Instruction) (s : EncodedState) :
    decodeState (step op s) = executeInstruction op (decodeState s) := by
  cases op with
  | read a => rfl
  | halve =>
      simp only [step, decodeState, executeInstruction, halve, value_half]
  | negate =>
      simp only [step, decodeState, executeInstruction, negate, value_neg]
  | write a =>
      change (⟨fun j => value ((Function.update s.memory a s.accumulator) j),
        value s.accumulator⟩ : RefState ℕ) =
        ⟨Function.update (fun j => value (s.memory j)) a (value s.accumulator),
          value s.accumulator⟩
      apply congrArg (fun m : ℕ → ℝ => (⟨m, value s.accumulator⟩ : RefState ℕ))
      exact Function.comp_update value s.memory a s.accumulator

/-- The implementation simulates the accepted real interpreter on any list,
including every partial instruction prefix. This is not an endpoint premise. -/
theorem decode_run (ops : List Instruction) (s : EncodedState) :
    decodeState (run ops s) = execute ops (decodeState s) := by
  induction ops generalizing s with
  | nil => rfl
  | cons op ops ih =>
      rw [run, ih, decode_step]
      rfl

/-- A concrete interrupted program cut also retains the exact scratch state. -/
theorem decode_program_prefix (n base k : ℕ) (s : EncodedState) :
    decodeState (run ((program n base).take k) s) =
      execute ((program n base).take k) (decodeState s) :=
  decode_run _ _

private theorem run_append (ops rest : List Instruction) (s : EncodedState) :
    run (ops ++ rest) s = run rest (run ops s) := by
  induction ops generalizing s with
  | nil => rfl
  | cons op ops ih => exact ih (step op s)

/-- Exact encoded result of one complete read/halve/negate/write sequence. -/
theorem run_component (a : ℕ) (s : EncodedState) :
    run (componentCode a) s =
      ⟨Function.update s.memory a (minusHalfCell (s.memory a)),
        minusHalfCell (s.memory a)⟩ := rfl

private theorem run_emit_memory (addresses : List ℕ) (s : EncodedState) :
    (run (emit addresses) s).memory =
      runUpdates (fun _ c => minusHalfCell c) addresses s.memory := by
  induction addresses generalizing s with
  | nil => rfl
  | cons a rest ih =>
      rw [emit, run_append, ih, run_component]
      rfl

/-- The existing proved no-duplicate flat traversal yields each raw encoded
cell's result, without a new traversal or no-alias supplier. -/
theorem program_cell (n base : ℕ) (s : EncodedState) (slot : Slot (Fin n)) :
    (run (program n base) s).memory (flatAddress base slot) =
      minusHalfCell (s.memory (flatAddress base slot)) := by
  rw [program, run_emit_memory]
  exact runUpdates_of_mem _ _
    (List.Nodup.map (flatAddress_injective n base) (componentOrder_nodup n))
    _ (List.mem_map.mpr ⟨slot, componentOrder_complete n slot, rfl⟩) _

/-- Numerator magnitude does not grow. Only this written cell's denominator
exponent increases, once. This is exact-grid refinement, not same-grid rounding. -/
theorem program_cell_budget (n base : ℕ) (s : EncodedState) (slot : Slot (Fin n)) :
    ((run (program n base) s).memory (flatAddress base slot)).numerator.natAbs =
        (s.memory (flatAddress base slot)).numerator.natAbs ∧
    ((run (program n base) s).memory (flatAddress base slot)).fractionalBits =
        (s.memory (flatAddress base slot)).fractionalBits + 1 := by
  rw [program_cell]
  simp only [minusHalfCell, Int.natAbs_neg, and_self]

/-- All outside cells retain both numerator AND exponent verbatim. -/
theorem program_outside_cell (n base : ℕ) (s : EncodedState) (a : ℕ)
    (hout : a < base ∨ base + 2 * n ≤ a) :
    (run (program n base) s).memory a = s.memory a := by
  rw [program, run_emit_memory]
  apply runUpdates_of_not_mem
  intro ha
  rcases List.mem_map.mp ha with ⟨slot, _, heq⟩
  have hb := flatAddress_bounds n base slot
  omega

/-- Decode the implemented program using the already accepted real endpoint. -/
theorem program_value (n base : ℕ) (s : EncodedState) (slot : Slot (Fin n)) :
    value ((run (program n base) s).memory (flatAddress base slot)) =
      (-1 / 2 : ℝ) * value (s.memory (flatAddress base slot)) := by
  have h := congrArg (fun t : RefState ℕ => t.memory (flatAddress base slot))
    (decode_run (program n base) s)
  exact h.trans (program_slot n base (decodeState s) slot)

end CurrentMain.Current1094Row1DyadicReference

#print axioms CurrentMain.Current1094Row1DyadicReference.decode_step
#print axioms CurrentMain.Current1094Row1DyadicReference.decode_run
#print axioms CurrentMain.Current1094Row1DyadicReference.decode_program_prefix
#print axioms CurrentMain.Current1094Row1DyadicReference.run_component
#print axioms CurrentMain.Current1094Row1DyadicReference.program_cell
#print axioms CurrentMain.Current1094Row1DyadicReference.program_cell_budget
#print axioms CurrentMain.Current1094Row1DyadicReference.program_outside_cell
#print axioms CurrentMain.Current1094Row1DyadicReference.program_value
