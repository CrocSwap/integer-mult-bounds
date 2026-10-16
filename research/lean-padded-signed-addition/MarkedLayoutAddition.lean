import MarkedPairLayout

/-!
Copyright (c) 2026 James Chang. Apache-2.0. OpenAI-assisted.

An executable sequential controller joins paid marked pairing to the accepted
marked adder. The transition between the phases costs one actual finite-control
step. It retains both input tapes and signs, and reuses the produced output
and existing seven-register bank without copying or reformatting them.

Starting with two marked bit words, supplied sign bits, arbitrary seven scratch
bits and empty output, the complete first halt is 19*max(na,nb)+na+nb+59.
Both sign columns and all layout work are already included; every prefix has
at most na+nb+max(na,nb)+8 represented tape cells. The actual final marked
output encodes the exact signed sum. Input encoding/sign extraction, source
marker creation, dirty-output inversion and single-tape simulation are separate.
Author-checked context: kappa=836330098538459/500000000000000000.
Uncompiled source candidate; accepted results are recorded separately.
-/
set_option Elab.async false
set_option autoImplicit false

namespace MarkedLayoutAddition
open CurrentMain.PairedBitXorScan (Tape)

/-- Same three physical tapes in both modes. `addition` changes only the
control interpretation of the already built output tape and register bank. -/
inductive State where
  | layout (s : MarkedPairLayout.State)
  | addition (left right : Tape MarkedZeroPadding.Symbol) (sx sy : Bool)
      (s : MarkedBitAddition.State)
  deriving DecidableEq

def step : State → State
  | .layout s =>
      if s.phase = .halt then
        .addition s.leftTape s.rightTape s.leftSign s.rightSign (MarkedPairLayout.adderEntrance s)
      else .layout (MarkedPairLayout.step s)
  | .addition left right sx sy s => .addition left right sx sy (MarkedBitAddition.step s)

def Halted : State → Prop
  | .layout _ => False
  | .addition _ _ _ _ s => s.phase = .body .halt

def run : Nat → State → State
  | 0, s => s
  | k + 1, s => run k (step s)

inductive Trace : Nat → State → State → Prop where
  | nil (s : State) : Trace 0 s s
  | next {k : Nat} {s t : State} (live : ¬ Halted s)
      (tail : Trace k (step s) t) : Trace (k + 1) s t

private theorem trace_trans {m n : Nat} {s u t : State}
    (h : Trace m s u) (g : Trace n u t) : Trace (m + n) s t := by
  induction h with
  | nil => simpa using g
  | next live tail ih => simpa only [Nat.succ_add] using Trace.next live (ih g)

private theorem trace_sound {k : Nat} {s t : State} (h : Trace k s t) : run k s = t := by
  induction h with
  | nil => rfl
  | next _ _ ih => exact ih

private theorem trace_live {k : Nat} {s t : State} (h : Trace k s t)
    (j : Nat) (hj : j < k) : ¬ Halted (run j s) := by
  induction h generalizing j with
  | nil => omega
  | next live tail ih =>
      cases j with
      | zero => exact live
      | succ j => exact ih j (by omega)

private theorem layout_trace {n : Nat} {s t : MarkedPairLayout.State}
    (h : MarkedPairLayout.Trace n s t) : Trace n (.layout s) (.layout t) := by
  induction h with
  | nil => exact Trace.nil _
  | next live tail ih =>
      apply Trace.next (by simp [Halted])
      simpa only [step, if_neg live] using ih

private theorem addition_trace (left right : Tape MarkedZeroPadding.Symbol) (sx sy : Bool)
    {n : Nat} {s t : MarkedBitAddition.State} (h : MarkedBitAddition.RunsToHalt n s t) :
    Trace n (.addition left right sx sy s) (.addition left right sx sy t) := by
  induction h with
  | done => exact Trace.nil _
  | next live tail ih => exact Trace.next live ih

def initial (xs ys : List Bool) (sx sy : Bool) (r : SequentialBitAddition.Registers) : State :=
  .layout (MarkedPairLayout.initial xs sx ys sy r)

def outputRows (xs ys : List Bool) (sx sy : Bool) (r : SequentialBitAddition.Registers) :
    List SequentialBitAddition.Row :=
  SequentialBitAddition.transformed (MarkedPairLayout.rows xs sx ys sy)
    (SequentialBitAddition.zeroCarry (MarkedPairLayout.clearScratch r))

def final (xs ys : List Bool) (sx sy : Bool) (r : SequentialBitAddition.Registers) : State :=
  .addition (MarkedZeroPadding.marked (MarkedZeroPadding.bits xs))
    (MarkedZeroPadding.marked (MarkedZeroPadding.bits ys)) sx sy
    (MarkedBitAddition.final (outputRows xs ys sx sy r))

/-- A single real controller transition at the returned-head layout endpoint.
No tape symbol, tape head, sign bit or register changes during this handoff. -/
theorem handoff (xs ys : List Bool) (sx sy : Bool) (r : SequentialBitAddition.Registers) :
    step (.layout (MarkedPairLayout.final xs sx ys sy r)) =
      .addition (MarkedZeroPadding.marked (MarkedZeroPadding.bits xs))
        (MarkedZeroPadding.marked (MarkedZeroPadding.bits ys)) sx sy
        (MarkedBitAddition.initial (MarkedPairLayout.rows xs sx ys sy) (MarkedPairLayout.clearScratch r)) := rfl

/-- Entire implemented path, including paid pairing and the one-step handoff. -/
theorem machine_exact (xs ys : List Bool) (sx sy : Bool) (r : SequentialBitAddition.Registers) :
    Trace (19 * max xs.length ys.length + xs.length + ys.length + 59)
      (initial xs ys sx sy r) (final xs ys sx sy r) := by
  have hl := layout_trace (MarkedPairLayout.layout_exact xs ys sx sy r)
  have hh : Trace 1 (.layout (MarkedPairLayout.final xs sx ys sy r))
      (.addition (MarkedZeroPadding.marked (MarkedZeroPadding.bits xs))
        (MarkedZeroPadding.marked (MarkedZeroPadding.bits ys)) sx sy
        (MarkedBitAddition.initial (MarkedPairLayout.rows xs sx ys sy) (MarkedPairLayout.clearScratch r))) := by
    apply Trace.next (by simp [Halted])
    rw [handoff]
    exact Trace.nil _
  have ha := addition_trace
    (MarkedZeroPadding.marked (MarkedZeroPadding.bits xs))
    (MarkedZeroPadding.marked (MarkedZeroPadding.bits ys)) sx sy
    (MarkedBitAddition.machine_exact (MarkedPairLayout.rows xs sx ys sy) (MarkedPairLayout.clearScratch r))
  have h := trace_trans (trace_trans hl hh) ha
  have he : (8 * max xs.length ys.length + xs.length + ys.length + 24) + 1 +
      (11 * (MarkedPairLayout.rows xs sx ys sy).length + 12) =
      19 * max xs.length ys.length + xs.length + ys.length + 59 := by
    simp only [MarkedPairLayout.rows, List.length_map, List.length_append,
      List.length_cons, List.length_nil, SignedWordAlignment.aligned_length, SignedWordAlignment.width]
    omega
  rw [he] at h
  exact h

theorem machine_result (xs ys : List Bool) (sx sy : Bool) (r : SequentialBitAddition.Registers) :
    run (19 * max xs.length ys.length + xs.length + ys.length + 59) (initial xs ys sx sy r) =
      final xs ys sx sy r := trace_sound (machine_exact xs ys sx sy r)

theorem machine_first_halt (xs ys : List Bool) (sx sy : Bool) (r : SequentialBitAddition.Registers) :
    Halted (run (19 * max xs.length ys.length + xs.length + ys.length + 59) (initial xs ys sx sy r)) ∧
    ∀ k < 19 * max xs.length ys.length + xs.length + ys.length + 59,
      ¬ Halted (run k (initial xs ys sx sy r)) := by
  constructor
  · rw [machine_result]; rfl
  · exact trace_live (machine_exact xs ys sx sy r)

private theorem run_add (a b : Nat) (s : State) : run (a + b) s = run b (run a s) := by
  induction a generalizing s with
  | zero => simp only [Nat.zero_add, run]
  | succ a ih => simpa only [Nat.succ_add, run] using ih (step s)

private theorem addition_run (left right : Tape MarkedZeroPadding.Symbol) (sx sy : Bool)
    (s : MarkedBitAddition.State) (k : Nat) :
    run k (.addition left right sx sy s) = .addition left right sx sy (MarkedBitAddition.run k s) := by
  induction k generalizing s with
  | zero => rfl
  | succ k ih => exact ih (MarkedBitAddition.step s)

private theorem layout_prefix {n : Nat} {s t : MarkedPairLayout.State}
    (h : MarkedPairLayout.Trace n s t) (k : Nat) (hk : k ≤ n) :
    run k (.layout s) = .layout (MarkedPairLayout.run k s) := by
  induction h generalizing k with
  | nil =>
      have hk0 : k = 0 := by omega
      subst k
      rfl
  | next live tail ih =>
      cases k with
      | zero => rfl
      | succ k =>
          simpa only [run, step, if_neg live, MarkedPairLayout.run] using ih k (by omega)

def cells : State → Nat
  | .layout s => MarkedPairLayout.cells s
  | .addition left right _ _ s =>
      MarkedPairLayout.tapeCells left + MarkedPairLayout.tapeCells right + MarkedBitAddition.cells s

/-- The original source tapes are framed during every adder prefix. The
already allocated paired output is reused, so no second output buffer appears. -/
theorem machine_prefix_storage (xs ys : List Bool) (sx sy : Bool)
    (r : SequentialBitAddition.Registers) (k : Nat) :
    cells (run k (initial xs ys sx sy r)) ≤
      xs.length + ys.length + max xs.length ys.length + 8 := by
  let L := 8 * max xs.length ys.length + xs.length + ys.length + 24
  by_cases hk : k ≤ L
  · have h := layout_prefix (MarkedPairLayout.layout_exact xs ys sx sy r) k hk
    rw [initial, h]
    exact MarkedPairLayout.layout_prefix_storage xs ys sx sy r k
  · have he : k = L + 1 + (k - (L + 1)) := by omega
    rw [he, run_add]
    have hL : run (L + 1) (initial xs ys sx sy r) =
        .addition (MarkedZeroPadding.marked (MarkedZeroPadding.bits xs))
          (MarkedZeroPadding.marked (MarkedZeroPadding.bits ys)) sx sy
          (MarkedBitAddition.initial (MarkedPairLayout.rows xs sx ys sy) (MarkedPairLayout.clearScratch r)) := by
      rw [run_add]
      change run 1 (run L (.layout (MarkedPairLayout.initial xs sx ys sy r))) = _
      rw [layout_prefix (MarkedPairLayout.layout_exact xs ys sx sy r) L (Nat.le_refl _)]
      dsimp only [L]
      rw [MarkedPairLayout.layout_result]
      exact handoff xs ys sx sy r
    rw [hL, addition_run]
    simp [cells, MarkedBitAddition.machine_storage, MarkedPairLayout.tapeCells,
      MarkedZeroPadding.marked, MarkedZeroPadding.bits, MarkedPairLayout.rows,
      SignedWordAlignment.aligned_length, SignedWordAlignment.width,
      Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]

/-- Arithmetic of the actual completed marked output, with both generated sign
columns included in the execution and storage invoices above. -/
theorem output_signed_sum (xs ys : List Bool) (sx sy : Bool) (r : SequentialBitAddition.Registers) :
    let p := SignedWordAlignment.aligned xs sx ys sy
    let scratch := MarkedPairLayout.clearScratch r
    let low := SequentialBitAddition.scan p (SequentialBitAddition.zeroCarry scratch)
    let lastLow := SequentialBitAddition.sumBit sx sy low.registers.carry
    let sign := SequentialBitAddition.sumBit sx sy (SequentialBitAddition.carryBit sx sy low.registers.carry)
    (outputRows xs ys sx sy r).map Prod.snd = low.output ++ [lastLow, sign] ∧
      SequentialBitAddition.signedValue (low.output ++ [lastLow]) sign =
        SequentialBitAddition.signedValue xs sx + SequentialBitAddition.signedValue ys sy := by
  have h := SignedWordAlignment.aligned_signed_sum xs sx ys sy (MarkedPairLayout.clearScratch r)
  have ho := (MarkedBitAddition.signed_machine_resources
    (SignedWordAlignment.aligned xs sx ys sy) sx sy (MarkedPairLayout.clearScratch r)).2.1
  dsimp only at h ⊢
  constructor
  · exact ho.trans h.1
  · exact h.2

end MarkedLayoutAddition

#print axioms MarkedLayoutAddition.handoff
#print axioms MarkedLayoutAddition.machine_exact
#print axioms MarkedLayoutAddition.machine_result
#print axioms MarkedLayoutAddition.machine_first_halt
#print axioms MarkedLayoutAddition.machine_prefix_storage
#print axioms MarkedLayoutAddition.output_signed_sum
#check @MarkedLayoutAddition.machine_exact
#check @MarkedLayoutAddition.output_signed_sum
