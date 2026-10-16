import PaddedSignedAddition

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.

A uniform invoice derived for the fully specified seven-tape prepared routine,
using its actual represented entrance volume. No uniform running-time bound is
assumed: the accepted executed first-halt count proves time ≤ 26V, and the
accepted every-prefix footprint proves represented cells ≤ 3V. V includes the
two unary controls, both marked source words and all initially empty output
workspaces; fixed finite registers/control are recorded separately.

This coefficient belongs to this finite-alphabet seven-tape implementation.
It does not price generation of unary controls from binary exponents, creation
of source encodings, dirty-state reversibility, a single-tape simulation or
other selected program events. It is not the selected uniform cost supplier C.
Author-checked context: kappa=836330098538459/500000000000000000.
Uncompiled source candidate.
-/
set_option Elab.async false
set_option autoImplicit false

namespace PaddedAdditionLinearInvoice

def volume (dx : Nat) (xs : List Bool) (sx : Bool) (dy : Nat) (ys : List Bool)
    (sy bl br : Bool) (r : SequentialBitAddition.Registers) : Nat :=
  PaddedSignedAddition.cells (PaddedSignedAddition.initial dx xs sx dy ys sy bl br r)

/-- All seven tape fields are measured; the three output workspaces really
start empty. Four already-supplied source/control marker pairs contribute 8. -/
theorem volume_exact (dx : Nat) (xs : List Bool) (sx : Bool) (dy : Nat) (ys : List Bool)
    (sy bl br : Bool) (r : SequentialBitAddition.Registers) :
    volume dx xs sx dy ys sy bl br r = dx + xs.length + dy + ys.length + 8 := by
  simp [volume, PaddedSignedAddition.cells, PaddedSignedAddition.initial,
    MarkedZeroPadding.cells, MarkedZeroPadding.tapeCells, MarkedZeroPadding.initial,
    MarkedZeroPadding.marked, MarkedZeroPadding.bits, MarkedZeroPadding.ticks,
    MarkedPairLayout.tapeCells, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]

theorem volume_positive (dx : Nat) (xs : List Bool) (sx : Bool) (dy : Nat) (ys : List Bool)
    (sy bl br : Bool) (r : SequentialBitAddition.Registers) :
    0 < volume dx xs sx dy ys sy bl br r := by
  rw [volume_exact]
  omega

/-- Derived actual first-halt invoice; unary control length is charged in V. -/
theorem linear_time (dx : Nat) (xs : List Bool) (sx : Bool) (dy : Nat) (ys : List Bool)
    (sy bl br : Bool) (r : SequentialBitAddition.Registers) :
    PaddedSignedAddition.totalTime dx xs dy ys ≤ 26 * volume dx xs sx dy ys sy bl br r := by
  rw [volume_exact]
  simp only [PaddedSignedAddition.totalTime]
  omega

/-- Derived all-prefix tape-space invoice, including all original tapes and
both padded copies plus sum. Fixed Boolean/control capacity is additional. -/
theorem linear_space (dx : Nat) (xs : List Bool) (sx : Bool) (dy : Nat) (ys : List Bool)
    (sy bl br : Bool) (r : SequentialBitAddition.Registers) (k : Nat) :
    PaddedSignedAddition.cells
      (PaddedSignedAddition.run k (PaddedSignedAddition.initial dx xs sx dy ys sy bl br r)) ≤
        3 * volume dx xs sx dy ys sy bl br r := by
  have h := PaddedSignedAddition.machine_prefix_storage dx xs sx dy ys sy bl br r k
  rw [volume_exact]
  omega

/-- The bound is attached to the actual executed trace, not an abstract
cost family or a separately assumed uniform majorant. -/
theorem executed_linear_invoice (dx : Nat) (xs : List Bool) (sx : Bool) (dy : Nat)
    (ys : List Bool) (sy bl br : Bool) (r : SequentialBitAddition.Registers) :
    ∃ t ≤ 26 * volume dx xs sx dy ys sy bl br r,
      PaddedSignedAddition.Trace t (PaddedSignedAddition.initial dx xs sx dy ys sy bl br r)
        (PaddedSignedAddition.final dx xs sx dy ys sy r) ∧
      ∀ k, PaddedSignedAddition.cells
        (PaddedSignedAddition.run k (PaddedSignedAddition.initial dx xs sx dy ys sy bl br r)) ≤
          3 * volume dx xs sx dy ys sy bl br r :=
  ⟨PaddedSignedAddition.totalTime dx xs dy ys, linear_time dx xs sx dy ys sy bl br r,
    PaddedSignedAddition.machine_exact dx xs sx dy ys sy bl br r,
    linear_space dx xs sx dy ys sy bl br r⟩

end PaddedAdditionLinearInvoice

#print axioms PaddedAdditionLinearInvoice.volume_exact
#print axioms PaddedAdditionLinearInvoice.volume_positive
#print axioms PaddedAdditionLinearInvoice.linear_time
#print axioms PaddedAdditionLinearInvoice.linear_space
#print axioms PaddedAdditionLinearInvoice.executed_linear_invoice
#check @PaddedAdditionLinearInvoice.executed_linear_invoice
