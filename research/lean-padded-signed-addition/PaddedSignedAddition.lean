import MarkedLayoutAddition

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.

Sequentially execute both paid zero-padding machines, retain all four original
source/control tapes, and transfer their actual output tapes to the paid
pairing-plus-adder controller. Two explicit finite-control transitions perform
the handoffs. No bits are copied or re-encoded during a handoff. There are seven
physical tapes: two sources, two unary controls, two padded words and one sum.

Unary controls, initially marked source words, explicit signs, independent tapes
and blank output workspaces are inputs. They are not generated for free here.
The controller performs no runtime Nat/Int arithmetic; lengths and transition
counts below are external observers. Source Cell encoding, exponent arithmetic,
control generation, dirty-state inversion and single-tape simulation remain.
Author-checked context: kappa=836330098538459/500000000000000000.
Uncompiled source candidate.
-/
set_option Elab.async false
set_option autoImplicit false

namespace PaddedSignedAddition
open CurrentMain.PairedBitXorScan (Tape)

inductive State where
  | first (left right : MarkedZeroPadding.State) (output : Tape MarkedBitAddition.Symbol)
      (registers : SequentialBitAddition.Registers) (sx sy : Bool)
  | second (left right : MarkedZeroPadding.State) (output : Tape MarkedBitAddition.Symbol)
      (registers : SequentialBitAddition.Registers) (sx sy : Bool)
  | sum (leftData leftControl rightData rightControl : Tape MarkedZeroPadding.Symbol)
      (leftScratch rightScratch : Bool) (s : MarkedLayoutAddition.State)
  deriving DecidableEq

def enterSum (left right : MarkedZeroPadding.State) (output : Tape MarkedBitAddition.Symbol)
    (registers : SequentialBitAddition.Registers) (sx sy : Bool) : State :=
  .sum left.dataTape left.controlTape right.dataTape right.controlTape left.scratch right.scratch
    (.layout ⟨left.outputTape, right.outputTape, output, registers, sx, sy, .writeLeft⟩)

def step : State → State
  | .first left right output registers sx sy =>
      if left.phase = .halt then .second left right output registers sx sy
      else .first (MarkedZeroPadding.step left) right output registers sx sy
  | .second left right output registers sx sy =>
      if right.phase = .halt then enterSum left right output registers sx sy
      else .second left (MarkedZeroPadding.step right) output registers sx sy
  | .sum ld lc rd rc bl br s => .sum ld lc rd rc bl br (MarkedLayoutAddition.step s)

def Halted : State → Prop
  | .first .. => False
  | .second .. => False
  | .sum _ _ _ _ _ _ s => MarkedLayoutAddition.Halted s

def run : Nat → State → State
  | 0, s => s
  | n + 1, s => run n (step s)

inductive Trace : Nat → State → State → Prop where
  | nil (s : State) : Trace 0 s s
  | next {n : Nat} {s t : State} (live : ¬ Halted s)
      (tail : Trace n (step s) t) : Trace (n + 1) s t

private theorem trace_trans {m n : Nat} {s u t : State}
    (h : Trace m s u) (g : Trace n u t) : Trace (m + n) s t := by
  induction h with
  | nil => simpa using g
  | next live tail ih => simpa only [Nat.succ_add] using Trace.next live (ih g)

private theorem trace_sound {n : Nat} {s t : State} (h : Trace n s t) : run n s = t := by
  induction h with
  | nil => rfl
  | next _ _ ih => exact ih

private theorem trace_live {n : Nat} {s t : State} (h : Trace n s t)
    (k : Nat) (hk : k < n) : ¬ Halted (run k s) := by
  induction h generalizing k with
  | nil => omega
  | next live tail ih =>
      cases k with
      | zero => exact live
      | succ k => exact ih k (by omega)

private theorem first_trace {n : Nat} {s t : MarkedZeroPadding.State}
    (h : MarkedZeroPadding.Trace n s t) (right : MarkedZeroPadding.State)
    (output : Tape MarkedBitAddition.Symbol) (r : SequentialBitAddition.Registers) (sx sy : Bool) :
    Trace n (.first s right output r sx sy) (.first t right output r sx sy) := by
  induction h with
  | nil => exact Trace.nil _
  | next live tail ih =>
      apply Trace.next (by simp [Halted])
      simpa only [step, if_neg live] using ih

private theorem second_trace {n : Nat} {s t : MarkedZeroPadding.State}
    (h : MarkedZeroPadding.Trace n s t) (left : MarkedZeroPadding.State)
    (output : Tape MarkedBitAddition.Symbol) (r : SequentialBitAddition.Registers) (sx sy : Bool) :
    Trace n (.second left s output r sx sy) (.second left t output r sx sy) := by
  induction h with
  | nil => exact Trace.nil _
  | next live tail ih =>
      apply Trace.next (by simp [Halted])
      simpa only [step, if_neg live] using ih

private theorem sum_trace {n : Nat} {s t : MarkedLayoutAddition.State}
    (h : MarkedLayoutAddition.Trace n s t) (ld lc rd rc : Tape MarkedZeroPadding.Symbol) (bl br : Bool) :
    Trace n (.sum ld lc rd rc bl br s) (.sum ld lc rd rc bl br t) := by
  induction h with
  | nil => exact Trace.nil _
  | next live tail ih => exact Trace.next live ih

def initial (dx : Nat) (xs : List Bool) (sx : Bool) (dy : Nat) (ys : List Bool) (sy : Bool)
    (bl br : Bool) (r : SequentialBitAddition.Registers) : State :=
  .first (MarkedZeroPadding.initial dx xs bl) (MarkedZeroPadding.initial dy ys br) ⟨[], []⟩ r sx sy

def sumFrame (dx : Nat) (xs : List Bool) (dy : Nat) (ys : List Bool)
    (s : MarkedLayoutAddition.State) : State :=
  .sum (MarkedZeroPadding.marked (MarkedZeroPadding.bits xs))
    (MarkedZeroPadding.marked (MarkedZeroPadding.ticks dx))
    (MarkedZeroPadding.marked (MarkedZeroPadding.bits ys))
    (MarkedZeroPadding.marked (MarkedZeroPadding.ticks dy)) false false s

def final (dx : Nat) (xs : List Bool) (sx : Bool) (dy : Nat) (ys : List Bool) (sy : Bool)
    (r : SequentialBitAddition.Registers) : State :=
  sumFrame dx xs dy ys (MarkedLayoutAddition.final
    (MarkedZeroPadding.padded dx xs) (MarkedZeroPadding.padded dy ys) sx sy r)

def totalTime (dx : Nat) (xs : List Bool) (dy : Nat) (ys : List Bool) : Nat :=
  19 * max (dx + xs.length) (dy + ys.length) + 7 * ((dx + xs.length) + (dy + ys.length)) + 89

/-- The second switch transfers the two actual produced marked output tapes,
with no reformatting or source-copy operation. Original sources/controls remain. -/
theorem sum_handoff (dx : Nat) (xs : List Bool) (sx : Bool) (dy : Nat) (ys : List Bool)
    (sy : Bool) (r : SequentialBitAddition.Registers) :
    step (.second (MarkedZeroPadding.final dx xs) (MarkedZeroPadding.final dy ys) ⟨[], []⟩ r sx sy) =
      sumFrame dx xs dy ys (MarkedLayoutAddition.initial
        (MarkedZeroPadding.padded dx xs) (MarkedZeroPadding.padded dy ys) sx sy r) := rfl

/-- All seven tapes are explicit in the derived endpoint. Both padding
scratch bits and all arithmetic scratch are cleared by their actual machines. -/
theorem machine_exact (dx : Nat) (xs : List Bool) (sx : Bool) (dy : Nat) (ys : List Bool)
    (sy bl br : Bool) (r : SequentialBitAddition.Registers) :
    Trace (totalTime dx xs dy ys) (initial dx xs sx dy ys sy bl br r) (final dx xs sx dy ys sy r) := by
  have hl := first_trace (MarkedZeroPadding.padding_exact dx xs bl)
    (MarkedZeroPadding.initial dy ys br) ⟨[], []⟩ r sx sy
  have hswitch1 : Trace 1
      (.first (MarkedZeroPadding.final dx xs) (MarkedZeroPadding.initial dy ys br) ⟨[], []⟩ r sx sy)
      (.second (MarkedZeroPadding.final dx xs) (MarkedZeroPadding.initial dy ys br) ⟨[], []⟩ r sx sy) := by
    apply Trace.next (by simp [Halted])
    exact Trace.nil _
  have hr := second_trace (MarkedZeroPadding.padding_exact dy ys br)
    (MarkedZeroPadding.final dx xs) ⟨[], []⟩ r sx sy
  have hswitch2 : Trace 1
      (.second (MarkedZeroPadding.final dx xs) (MarkedZeroPadding.final dy ys) ⟨[], []⟩ r sx sy)
      (sumFrame dx xs dy ys (MarkedLayoutAddition.initial
        (MarkedZeroPadding.padded dx xs) (MarkedZeroPadding.padded dy ys) sx sy r)) := by
    apply Trace.next (by simp [Halted])
    rw [sum_handoff]
    exact Trace.nil _
  have ha := sum_trace (MarkedLayoutAddition.machine_exact
    (MarkedZeroPadding.padded dx xs) (MarkedZeroPadding.padded dy ys) sx sy r)
    (MarkedZeroPadding.marked (MarkedZeroPadding.bits xs))
    (MarkedZeroPadding.marked (MarkedZeroPadding.ticks dx))
    (MarkedZeroPadding.marked (MarkedZeroPadding.bits ys))
    (MarkedZeroPadding.marked (MarkedZeroPadding.ticks dy)) false false
  have h := trace_trans (trace_trans (trace_trans (trace_trans hl hswitch1) hr) hswitch2) ha
  have he : (6 * (dx + xs.length) + 14) + 1 + (6 * (dy + ys.length) + 14) + 1 +
      (19 * max (MarkedZeroPadding.padded dx xs).length (MarkedZeroPadding.padded dy ys).length +
        (MarkedZeroPadding.padded dx xs).length + (MarkedZeroPadding.padded dy ys).length + 59) =
      totalTime dx xs dy ys := by
    simp only [MarkedZeroPadding.padded, List.length_append, List.length_replicate, totalTime]
    omega
  rw [he] at h
  exact h

theorem machine_result (dx : Nat) (xs : List Bool) (sx : Bool) (dy : Nat) (ys : List Bool)
    (sy bl br : Bool) (r : SequentialBitAddition.Registers) :
    run (totalTime dx xs dy ys) (initial dx xs sx dy ys sy bl br r) = final dx xs sx dy ys sy r :=
  trace_sound (machine_exact dx xs sx dy ys sy bl br r)

theorem machine_first_halt (dx : Nat) (xs : List Bool) (sx : Bool) (dy : Nat) (ys : List Bool)
    (sy bl br : Bool) (r : SequentialBitAddition.Registers) :
    Halted (run (totalTime dx xs dy ys) (initial dx xs sx dy ys sy bl br r)) ∧
    ∀ k < totalTime dx xs dy ys, ¬ Halted (run k (initial dx xs sx dy ys sy bl br r)) := by
  constructor
  · rw [machine_result]; rfl
  · exact trace_live (machine_exact dx xs sx dy ys sy bl br r)

private theorem run_add (a b : Nat) (s : State) : run (a + b) s = run b (run a s) := by
  induction a generalizing s with
  | zero => simp only [Nat.zero_add, run]
  | succ a ih => simpa only [Nat.succ_add, run] using ih (step s)

private theorem first_prefix {n : Nat} {s t : MarkedZeroPadding.State}
    (h : MarkedZeroPadding.Trace n s t) (right : MarkedZeroPadding.State)
    (output : Tape MarkedBitAddition.Symbol) (r : SequentialBitAddition.Registers) (sx sy : Bool)
    (k : Nat) (hk : k ≤ n) :
    run k (.first s right output r sx sy) =
      .first (MarkedZeroPadding.run k s) right output r sx sy := by
  induction h generalizing k with
  | nil =>
      have hk0 : k = 0 := by omega
      subst k
      rfl
  | next live tail ih =>
      cases k with
      | zero => rfl
      | succ k => simpa only [run, step, if_neg live, MarkedZeroPadding.run] using ih k (by omega)

private theorem second_prefix {n : Nat} {s t : MarkedZeroPadding.State}
    (h : MarkedZeroPadding.Trace n s t) (left : MarkedZeroPadding.State)
    (output : Tape MarkedBitAddition.Symbol) (r : SequentialBitAddition.Registers) (sx sy : Bool)
    (k : Nat) (hk : k ≤ n) :
    run k (.second left s output r sx sy) =
      .second left (MarkedZeroPadding.run k s) output r sx sy := by
  induction h generalizing k with
  | nil =>
      have hk0 : k = 0 := by omega
      subst k
      rfl
  | next live tail ih =>
      cases k with
      | zero => rfl
      | succ k => simpa only [run, step, if_neg live, MarkedZeroPadding.run] using ih k (by omega)

private theorem sum_run (ld lc rd rc : Tape MarkedZeroPadding.Symbol) (bl br : Bool)
    (s : MarkedLayoutAddition.State) (k : Nat) :
    run k (.sum ld lc rd rc bl br s) = .sum ld lc rd rc bl br (MarkedLayoutAddition.run k s) := by
  induction k generalizing s with
  | zero => rfl
  | succ k ih => exact ih (MarkedLayoutAddition.step s)

def cells : State → Nat
  | .first left right output _ _ _ =>
      MarkedZeroPadding.cells left + MarkedZeroPadding.cells right + MarkedPairLayout.tapeCells output
  | .second left right output _ _ _ =>
      MarkedZeroPadding.cells left + MarkedZeroPadding.cells right + MarkedPairLayout.tapeCells output
  | .sum ld lc rd rc _ _ s =>
      MarkedPairLayout.tapeCells ld + MarkedPairLayout.tapeCells lc +
      MarkedPairLayout.tapeCells rd + MarkedPairLayout.tapeCells rc + MarkedLayoutAddition.cells s

private theorem padding_initial_cells (d : Nat) (xs : List Bool) (b : Bool) :
    MarkedZeroPadding.cells (MarkedZeroPadding.initial d xs b) = d + xs.length + 4 := by
  simp [MarkedZeroPadding.cells, MarkedZeroPadding.tapeCells, MarkedZeroPadding.initial,
    MarkedZeroPadding.marked, MarkedZeroPadding.bits, MarkedZeroPadding.ticks,
    Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]

private theorem padding_final_cells (d : Nat) (xs : List Bool) :
    MarkedZeroPadding.cells (MarkedZeroPadding.final d xs) = 2 * (d + xs.length) + 6 := by
  simp [MarkedZeroPadding.cells, MarkedZeroPadding.tapeCells, MarkedZeroPadding.final,
    MarkedZeroPadding.marked, MarkedZeroPadding.bits, MarkedZeroPadding.ticks,
    MarkedZeroPadding.padded, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm, Nat.two_mul]

private theorem sum_frame_cells (dx : Nat) (xs : List Bool) (dy : Nat) (ys : List Bool)
    (s : MarkedLayoutAddition.State) :
    cells (sumFrame dx xs dy ys s) = dx + xs.length + dy + ys.length + 8 + MarkedLayoutAddition.cells s := by
  simp [cells, sumFrame, MarkedPairLayout.tapeCells, MarkedZeroPadding.marked,
    MarkedZeroPadding.bits, MarkedZeroPadding.ticks, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]

/-- All seven represented tapes are charged at every actual prefix. Both
original sources and unary controls remain present throughout the sum phase.
Two Boolean padding scratches, seven arithmetic registers, signs/control are extra. -/
theorem machine_prefix_storage (dx : Nat) (xs : List Bool) (sx : Bool) (dy : Nat) (ys : List Bool)
    (sy bl br : Bool) (r : SequentialBitAddition.Registers) (k : Nat) :
    cells (run k (initial dx xs sx dy ys sy bl br r)) ≤
      2 * ((dx + xs.length) + (dy + ys.length)) + max (dx + xs.length) (dy + ys.length) + 16 := by
  let L := 6 * (dx + xs.length) + 14
  let R := 6 * (dy + ys.length) + 14
  have hL : run L (initial dx xs sx dy ys sy bl br r) =
      .first (MarkedZeroPadding.final dx xs) (MarkedZeroPadding.initial dy ys br) ⟨[], []⟩ r sx sy := by
    rw [initial, first_prefix (MarkedZeroPadding.padding_exact dx xs bl)
      (MarkedZeroPadding.initial dy ys br) ⟨[], []⟩ r sx sy L (Nat.le_refl _)]
    dsimp only [L]
    rw [MarkedZeroPadding.padding_result]
  have hL1 : run (L + 1) (initial dx xs sx dy ys sy bl br r) =
      .second (MarkedZeroPadding.final dx xs) (MarkedZeroPadding.initial dy ys br) ⟨[], []⟩ r sx sy := by
    rw [run_add, hL]
    rfl
  have hLR : run (L + 1 + R) (initial dx xs sx dy ys sy bl br r) =
      .second (MarkedZeroPadding.final dx xs) (MarkedZeroPadding.final dy ys) ⟨[], []⟩ r sx sy := by
    rw [run_add, hL1, second_prefix (MarkedZeroPadding.padding_exact dy ys br)
      (MarkedZeroPadding.final dx xs) ⟨[], []⟩ r sx sy R (Nat.le_refl _)]
    dsimp only [R]
    rw [MarkedZeroPadding.padding_result]
  have hSum : run (L + 1 + R + 1) (initial dx xs sx dy ys sy bl br r) =
      sumFrame dx xs dy ys (MarkedLayoutAddition.initial
        (MarkedZeroPadding.padded dx xs) (MarkedZeroPadding.padded dy ys) sx sy r) := by
    rw [run_add, hLR]
    exact sum_handoff dx xs sx dy ys sy r
  by_cases hk : k ≤ L
  · rw [initial, first_prefix (MarkedZeroPadding.padding_exact dx xs bl)
      (MarkedZeroPadding.initial dy ys br) ⟨[], []⟩ r sx sy k hk]
    have hp := MarkedZeroPadding.padding_prefix_storage dx xs bl k
    simp only [cells, padding_initial_cells, MarkedPairLayout.tapeCells,
      List.length_nil, Nat.zero_add, Nat.add_zero]
    omega
  · by_cases hkR : k ≤ L + 1 + R
    · have he : k = L + 1 + (k - (L + 1)) := by omega
      have hj : k - (L + 1) ≤ R := by omega
      rw [he, run_add, hL1, second_prefix (MarkedZeroPadding.padding_exact dy ys br)
        (MarkedZeroPadding.final dx xs) ⟨[], []⟩ r sx sy (k - (L + 1)) hj]
      have hp := MarkedZeroPadding.padding_prefix_storage dy ys br (k - (L + 1))
      simp only [cells, padding_final_cells, MarkedPairLayout.tapeCells,
        List.length_nil, Nat.zero_add, Nat.add_zero]
      omega
    · have he : k = (L + 1 + R + 1) + (k - (L + 1 + R + 1)) := by omega
      rw [he, run_add, hSum]
      change cells (run (k - (L + 1 + R + 1)) (.sum _ _ _ _ _ _ _)) ≤ _
      rw [sum_run]
      change cells (sumFrame dx xs dy ys (MarkedLayoutAddition.run
        (k - (L + 1 + R + 1)) (MarkedLayoutAddition.initial
          (MarkedZeroPadding.padded dx xs) (MarkedZeroPadding.padded dy ys) sx sy r))) ≤ _
      rw [sum_frame_cells]
      have hp := MarkedLayoutAddition.machine_prefix_storage
        (MarkedZeroPadding.padded dx xs) (MarkedZeroPadding.padded dy ys) sx sy r
        (k - (L + 1 + R + 1))
      simp only [MarkedZeroPadding.padded, List.length_append, List.length_replicate] at hp ⊢
      omega

/-- Signed arithmetic of the actual final marked sum. Independent padding
amounts are executed and charged; their unary encodings are entrance tapes. -/
theorem output_scaled_sum (dx : Nat) (xs : List Bool) (sx : Bool) (dy : Nat) (ys : List Bool)
    (sy : Bool) (r : SequentialBitAddition.Registers) :
    let px := MarkedZeroPadding.padded dx xs
    let py := MarkedZeroPadding.padded dy ys
    let p := SignedWordAlignment.aligned px sx py sy
    let scratch := MarkedPairLayout.clearScratch r
    let low := SequentialBitAddition.scan p (SequentialBitAddition.zeroCarry scratch)
    let lastLow := SequentialBitAddition.sumBit sx sy low.registers.carry
    let sign := SequentialBitAddition.sumBit sx sy (SequentialBitAddition.carryBit sx sy low.registers.carry)
    (MarkedLayoutAddition.outputRows px py sx sy r).map Prod.snd = low.output ++ [lastLow, sign] ∧
      SequentialBitAddition.signedValue (low.output ++ [lastLow]) sign =
        (2 : Int)^dx * SequentialBitAddition.signedValue xs sx +
        (2 : Int)^dy * SequentialBitAddition.signedValue ys sy := by
  simpa only [MarkedZeroPadding.signed_padding_value] using
    MarkedLayoutAddition.output_signed_sum (MarkedZeroPadding.padded dx xs) (MarkedZeroPadding.padded dy ys) sx sy r

end PaddedSignedAddition

#print axioms PaddedSignedAddition.sum_handoff
#print axioms PaddedSignedAddition.machine_exact
#print axioms PaddedSignedAddition.machine_result
#print axioms PaddedSignedAddition.machine_first_halt
#print axioms PaddedSignedAddition.machine_prefix_storage
#print axioms PaddedSignedAddition.output_scaled_sum
#check @PaddedSignedAddition.machine_exact
#check @PaddedSignedAddition.output_scaled_sum
