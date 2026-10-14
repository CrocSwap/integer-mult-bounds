import PairedBitXorScan
import Lean.Elab.Tactic.Omega
import Mathlib.Tactic.Ring
import Mathlib.Tactic.LinearCombination

/-!
Executable little-endian bit addition in an explicitly counted sequential
bit-cell model. A paired-input specification is implemented below by one
finite-alphabet three-track tape machine: two source bits and one output bit
at each cell, seven Boolean registers, gate phases, one-cell head moves,
rewind, and explicit scratch clearing. Empty zipper boundaries are observed as supplied end-marker signals, as in
the imported paired-bit machine. A conventional single-symbol tape needs an
explicit marker/layout refinement before these counts become its bit time.
No Nat/Int arithmetic is executed by that machine; natural fuel and integer decoding are specifications only.

The result returns the head and clears all seven registers. It restores
initially clean scratch, but does not recover arbitrary old register contents. Source tracks
are preserved, while the output track is overwritten. It does not assert a
reversible restoration of arbitrary old output, or identify this tape with
the selected dyadic memory allocator. Input alignment, signed-width padding,
cell allocation, exponent computation and whole-program routing remain
separate implementation tasks. A zero-shift value/length lemma is included
as an unpriced specification for the next explicit padding implementation.

Signed inputs have explicit low bits and a sign bit. Two sign columns yield
an exact wider two's-complement result, including opposite-sign cancellation.
No table of selected numerical parameters is involved.

Attribution: elementary ripple-carry/full-adder arithmetic; the checked
per-cell dyadic SCALE/ADD representation and its all-prefix budget. This
generic module has no selected numerical table. Conditional context remains
kappa=836330098538459/500000000000000000. Apache-2.0; OpenAI-assisted.
UNCOMPILED source candidate.
-/
set_option Elab.async false
set_option autoImplicit false

namespace SequentialBitAddition

abbrev PairBit := Bool × Bool

def bit (b : Bool) : Int := if b then 1 else 0

def decode : List Bool → Int
  | [] => 0
  | b :: bs => bit b + 2 * decode bs

def leftBits (p : List PairBit) : List Bool := p.map Prod.fst
def rightBits (p : List PairBit) : List Bool := p.map Prod.snd

structure Registers where
  x : Bool
  y : Bool
  carry : Bool
  xorXY : Bool
  sum : Bool
  andXY : Bool
  andTC : Bool
  deriving DecidableEq

inductive Gate where
  | readLeft | readRight | xorInputs | xorCarry | andInputs | andCarry | orCarry | clearCarry
  deriving DecidableEq

/-- Every gate reads/writes only a constant number of individual Boolean cells. -/
def gateStep (input : PairBit) : Gate → Registers → Registers
  | .readLeft, r => { r with x := input.1 }
  | .readRight, r => { r with y := input.2 }
  | .xorInputs, r => { r with xorXY := r.x ^^ r.y }
  | .xorCarry, r => { r with sum := r.xorXY ^^ r.carry }
  | .andInputs, r => { r with andXY := r.x && r.y }
  | .andCarry, r => { r with andTC := r.xorXY && r.carry }
  | .orCarry, r => { r with carry := r.andXY || r.andTC }
  | .clearCarry, r => { r with carry := false }

def runGates (input : PairBit) : List Gate → Registers → Registers
  | [], r => r
  | g :: gs, r => runGates input gs (gateStep input g r)

def columnGates : List Gate :=
  [.readLeft, .readRight, .xorInputs, .xorCarry, .andInputs, .andCarry, .orCarry]

def column (input : PairBit) (r : Registers) : Registers :=
  runGates input columnGates r

def sumBit (a b c : Bool) : Bool := (a ^^ b) ^^ c
def carryBit (a b c : Bool) : Bool := (a && b) || ((a ^^ b) && c)

theorem column_exact (a b : Bool) (r : Registers) :
    (column (a,b) r).sum = sumBit a b r.carry ∧
    (column (a,b) r).carry = carryBit a b r.carry ∧
    (column (a,b) r).x = a ∧ (column (a,b) r).y = b := by
  exact ⟨rfl, rfl, rfl, rfl⟩

theorem full_adder_identity (a b c : Bool) :
    bit (sumBit a b c) + 2 * bit (carryBit a b c) = bit a + bit b + bit c := by
  cases a <;> cases b <;> cases c <;> decide

structure Result where
  output : List Bool
  registers : Registers

/-- Functional description of the forward scan. Each recursive call advances
to the next paired cell and records the concrete output bit. An explicit finite-alphabet tape execution below refines this recursive specification. -/
def scan : List PairBit → Registers → Result
  | [], r => ⟨[], r⟩
  | ab :: rest, r =>
      let next := column ab r
      let tail := scan rest next
      ⟨next.sum :: tail.output, tail.registers⟩

/-- The whole low-bit scan, with its final carry retained explicitly. -/
theorem scan_value (p : List PairBit) (r : Registers) :
    decode (scan p r).output + (2 : Int) ^ p.length * bit (scan p r).registers.carry =
      decode (leftBits p) + decode (rightBits p) + bit r.carry := by
  induction p generalizing r with
  | nil => simp [scan, decode, leftBits, rightBits]
  | cons ab rest ih =>
      have htail := ih (column ab r)
      have hcol := full_adder_identity ab.1 ab.2 r.carry
      have hs := (column_exact ab.1 ab.2 r).1
      have hc := (column_exact ab.1 ab.2 r).2.1
      simp only [scan, decode, leftBits, rightBits, List.map_cons, List.length_cons]
      rw [pow_succ]
      rw [← hs, ← hc] at hcol
      dsimp only [leftBits, rightBits] at htail
      linear_combination 2 * htail + hcol

theorem scan_storage (p : List PairBit) (r : Registers) :
    (scan p r).output.length = p.length := by
  induction p generalizing r with
  | nil => rfl
  | cons ab rest ih => simpa only [scan, List.length_cons] using congrArg Nat.succ (ih (column ab r))

/-- Source words are arguments, not mutable stores; this append identity also
makes sequential scan composition explicit, including all register state. -/
theorem scan_append_output (p q : List PairBit) (r : Registers) :
    (scan (p ++ q) r).output =
      (scan p r).output ++ (scan q (scan p r).registers).output ∧
    (scan (p ++ q) r).registers = (scan q (scan p r).registers).registers := by
  induction p generalizing r with
  | nil => simp [scan]
  | cons ab rest ih =>
      obtain ⟨ho, hr⟩ := ih (column ab r)
      constructor
      · simpa only [List.cons_append, scan, ho, hr]
      · simpa only [List.cons_append, scan] using hr

/-- Decoding of an explicitly sign-extended fixed-width word. The sign bit has
weight minus2^n; it is not an unbounded primitive integer representation. -/
def signedValue (low : List Bool) (sign : Bool) : Int :=
  decode low - bit sign * 2 ^ low.length

/-- Two extra identical sign columns remove signed overflow. This finite
Boolean identity is independent of the width and of all low input bits. -/
theorem sign_columns_identity (a b c : Bool) :
    bit (sumBit a b c) - 2 * bit (sumBit a b (carryBit a b c)) =
      bit c - bit a - bit b := by
  cases a <;> cases b <;> cases c <;> decide

def zeroCarry (r : Registers) : Registers := { r with carry := false }

def signedScan (p : List PairBit) (sa sb : Bool) (r : Registers) : Result :=
  scan (p ++ [(sa,sb), (sa,sb)]) (zeroCarry r)

/-- Identifies the actual emitted word: low sum, then one extra low bit, then
its sign bit. The final carry register is retained but not part of this word. -/
theorem signed_scan_exact (p : List PairBit) (sa sb : Bool) (r : Registers) :
    let low := scan p (zeroCarry r)
    let lastLow := sumBit sa sb low.registers.carry
    let sign := sumBit sa sb (carryBit sa sb low.registers.carry)
    (signedScan p sa sb r).output = low.output ++ [lastLow, sign] ∧
    signedValue (low.output ++ [lastLow]) sign =
      signedValue (leftBits p) sa + signedValue (rightBits p) sb := by
  dsimp only
  have hv := scan_value p (zeroCarry r)
  have hl := scan_storage p (zeroCarry r)
  have hc := sign_columns_identity sa sb (scan p (zeroCarry r)).registers.carry
  refine ⟨?_, ?_⟩
  · change (scan (p ++ [(sa,sb),(sa,sb)]) (zeroCarry r)).output = _
    rw [(scan_append_output p [(sa,sb),(sa,sb)] (zeroCarry r)).1]
    rfl
  · have append_one : ∀ xs : List Bool, ∀ z : Bool,
        decode (xs ++ [z]) = decode xs + (2 : Int)^xs.length * bit z := by
      intro xs z
      induction xs with
      | nil => simp [decode]
      | cons b bs ih => simp only [List.cons_append, decode, List.length_cons, pow_succ, ih]; ring
    simp only [signedValue, append_one, List.length_append, List.length_cons,
      List.length_nil, Nat.add_zero, leftBits, rightBits, List.length_map] at *
    rw [hl, pow_succ]
    have hzero : bit (zeroCarry r).carry = 0 := rfl
    rw [hzero, add_zero] at hv
    linear_combination hv + (2 : Int)^p.length * hc

theorem signed_scan_storage (p : List PairBit) (sa sb : Bool) (r : Registers) :
    (signedScan p sa sb r).output.length = p.length + 2 := by
  simp [signedScan, scan_storage]

/-- Materialize an unsigned left shift by writing low zeros; no Nat shift is
executed. Existing input bits are copied, not claimed to move for free. -/
def zeroShift : Nat → List Bool → List Bool
  | 0, xs => xs
  | d+1, xs => false :: zeroShift d xs

theorem zero_shift_value (d : Nat) (xs : List Bool) :
    decode (zeroShift d xs) = (2 : Int)^d * decode xs := by
  induction d with
  | zero => simp [zeroShift]
  | succ d ih => simp only [zeroShift, decode, bit, Bool.false_eq_true, if_false, zero_add, ih, pow_succ]; ring

theorem zero_shift_storage (d : Nat) (xs : List Bool) :
    (zeroShift d xs).length = d + xs.length := by
  induction d with
  | zero => simp only [zeroShift, Nat.zero_add]
  | succ d ih => simp only [zeroShift, List.length_cons, ih]; omega

/-! ## Concrete finite-alphabet tape implementation -/

abbrev Tape := CurrentMain.PairedBitXorScan.Tape
abbrev Row := PairBit × Bool

/-- A fixed seven-bit register bank, not an arbitrary-precision number. -/
def clearRegisters : Registers := ⟨false,false,false,false,false,false,false⟩

inductive ClearSlot where
  | x | y | carry | xorXY | sum | andXY | andTC
  deriving DecidableEq

inductive Phase where
  | initialize | test | gate (g : Gate) | write | advance | rewind
  | clear (slot : ClearSlot) | halt
  deriving DecidableEq

structure State where
  tape : Tape Row
  registers : Registers
  phase : Phase
  deriving DecidableEq

def nextGate : Gate → Phase
  | .readLeft => .gate .readRight
  | .readRight => .gate .xorInputs
  | .xorInputs => .gate .xorCarry
  | .xorCarry => .gate .andInputs
  | .andInputs => .gate .andCarry
  | .andCarry => .gate .orCarry
  | .orCarry => .write
  | .clearCarry => .test

def clearSlot (slot : ClearSlot) (r : Registers) : Registers :=
  match slot with
  | .x => { r with x := false }
  | .y => { r with y := false }
  | .carry => { r with carry := false }
  | .xorXY => { r with xorXY := false }
  | .sum => { r with sum := false }
  | .andXY => { r with andXY := false }
  | .andTC => { r with andTC := false }

def nextClear : ClearSlot → Phase
  | .x => .clear .y
  | .y => .clear .carry
  | .carry => .clear .xorXY
  | .xorXY => .clear .sum
  | .sum => .clear .andXY
  | .andXY => .clear .andTC
  | .andTC => .halt

/-- Each branch is one bounded-alphabet operation or a one-cell head move.
No Nat counter, indexing, addition, XOR or division appears in the transition. -/
def step (s : State) : State :=
  match s.phase with
  | .halt => s
  | .initialize => { s with registers := zeroCarry s.registers, phase := .test }
  | .test => match s.tape.right with
    | [] => { s with phase := .rewind }
    | _ :: _ => { s with phase := .gate .readLeft }
  | .gate g => match s.tape.right with
    | [] => { s with phase := .halt }
    | row :: _ => { s with registers := gateStep row.1 g s.registers, phase := nextGate g }
  | .write => match s.tape.right with
    | [] => { s with phase := .halt }
    | row :: rs =>
      ⟨⟨s.tape.left,(row.1,s.registers.sum) :: rs⟩,s.registers,.advance⟩
  | .advance => match s.tape.right with
    | [] => { s with phase := .halt }
    | row :: rs => { s with tape := ⟨row :: s.tape.left,rs⟩, phase := .test }
  | .rewind => match s.tape.left with
    | [] => { s with phase := .clear .x }
    | row :: ls => { s with tape := ⟨ls,row :: s.tape.right⟩ }
  | .clear slot => { s with registers := clearSlot slot s.registers, phase := nextClear slot }

/-- External observation fuel only; no runtime unary counter is introduced. -/
def run : Nat → State → State
  | 0, s => s
  | n+1, s => run n (step s)

inductive RunsToHalt : Nat → State → State → Prop where
  | done (s : State) (h : s.phase = .halt) : RunsToHalt 0 s s
  | next {n : Nat} {s t : State} (h : s.phase ≠ .halt)
      (tail : RunsToHalt n (step s) t) : RunsToHalt (n+1) s t

theorem runs_sound {n : Nat} {s t : State} (h : RunsToHalt n s t) : run n s = t := by
  induction h with
  | done => rfl
  | next _ _ ih => exact ih

/-- Mathematical output-word specification; not executed as a primitive step. -/
def transformed : List Row → Registers → List Row
  | [], _ => []
  | row :: rs, r =>
      let next := column row.1 r
      (row.1,next.sum) :: transformed rs next

def initial (rows : List Row) (scratch : Registers) : State :=
  ⟨⟨[],rows⟩,scratch,.initialize⟩
def final (rows : List Row) : State := ⟨⟨[],rows⟩,clearRegisters,.halt⟩

private theorem clear_seven (tape : Tape Row) (r : Registers) :
    RunsToHalt 7 ⟨tape,r,.clear .x⟩ ⟨tape,clearRegisters,.halt⟩ := by
  apply RunsToHalt.next (by simp [step, nextGate, nextClear, initial])
  apply RunsToHalt.next (by simp [step, nextGate, nextClear, initial])
  apply RunsToHalt.next (by simp [step, nextGate, nextClear, initial])
  apply RunsToHalt.next (by simp [step, nextGate, nextClear, initial])
  apply RunsToHalt.next (by simp [step, nextGate, nextClear, initial])
  apply RunsToHalt.next (by simp [step, nextGate, nextClear, initial])
  apply RunsToHalt.next (by simp [step, nextGate, nextClear, initial])
  exact RunsToHalt.done _ rfl

private theorem rewind_exact (ls rs : List Row) (r : Registers) :
    RunsToHalt (ls.length+8) ⟨⟨ls,rs⟩,r,.rewind⟩
      (final (ls.reverse ++ rs)) := by
  induction ls generalizing rs with
  | nil =>
      exact RunsToHalt.next (by simp [step, nextGate, nextClear, initial]) (clear_seven ⟨[],rs⟩ r)
  | cons row ls ih =>
      apply RunsToHalt.next (by simp [step, nextGate, nextClear, initial])
      simpa [step, final, List.reverse_cons, List.append_assoc] using ih (row::rs)

private theorem column_ten {n : Nat} (row : Row) (ls rs : List Row)
    (r : Registers) (t : State)
    (h : RunsToHalt n ⟨⟨(row.1,(column row.1 r).sum)::ls,rs⟩,column row.1 r,.test⟩ t) :
    RunsToHalt (n+10) ⟨⟨ls,row::rs⟩,r,.test⟩ t := by
  apply RunsToHalt.next (by simp [step, nextGate, nextClear, initial])
  apply RunsToHalt.next (by simp [step, nextGate, nextClear, initial])
  apply RunsToHalt.next (by simp [step, nextGate, nextClear, initial])
  apply RunsToHalt.next (by simp [step, nextGate, nextClear, initial])
  apply RunsToHalt.next (by simp [step, nextGate, nextClear, initial])
  apply RunsToHalt.next (by simp [step, nextGate, nextClear, initial])
  apply RunsToHalt.next (by simp [step, nextGate, nextClear, initial])
  apply RunsToHalt.next (by simp [step, nextGate, nextClear, initial])
  apply RunsToHalt.next (by simp [step, nextGate, nextClear, initial])
  apply RunsToHalt.next (by simp [step, nextGate, nextClear, initial])
  simpa only [step, nextGate, column, runGates, columnGates, gateStep] using h

private theorem scan_from (rs ls : List Row) (r : Registers) :
    RunsToHalt (11*rs.length+ls.length+9) ⟨⟨ls,rs⟩,r,.test⟩
      (final (ls.reverse ++ transformed rs r)) := by
  induction rs generalizing ls r with
  | nil =>
      simpa [step, transformed] using
        (RunsToHalt.next (s := (⟨⟨ls,[]⟩,r,.test⟩ : State))
          (by simp [step, nextGate, nextClear, initial]) (rewind_exact ls [] r))
  | cons row rs ih =>
      have h := column_ten row ls rs r _
        (ih ((row.1,(column row.1 r).sum)::ls) (column row.1 r))
      have hc : 11*rs.length + ((row.1,(column row.1 r).sum)::ls).length + 9 + 10 =
          11*(row::rs).length + ls.length + 9 := by
        simp only [List.length_cons]
        omega
      rw [hc] at h
      simpa [transformed, List.reverse_cons, List.append_assoc] using h

/-- Exact first-halt count for an actual finite-alphabet implementation:
ten transitions per forward column, n rewind moves, one carry reset,
two boundary transitions and seven scratch clears. All input bits survive. -/
theorem machine_exact (rows : List Row) (scratch : Registers) :
    RunsToHalt (11*rows.length+10) (initial rows scratch)
      (final (transformed rows (zeroCarry scratch))) := by
  have h := RunsToHalt.next (s := initial rows scratch) (by simp [step, nextGate, nextClear, initial])
    (scan_from rows [] (zeroCarry scratch))
  simpa [initial, step, Nat.add_assoc] using h

theorem machine_result (rows : List Row) (scratch : Registers) :
    run (11*rows.length+10) (initial rows scratch) =
      final (transformed rows (zeroCarry scratch)) := runs_sound (machine_exact rows scratch)

theorem transformed_sources (rows : List Row) (r : Registers) :
    (transformed rows r).map Prod.fst = rows.map Prod.fst := by
  induction rows generalizing r with
  | nil => rfl
  | cons row rs ih => simp only [transformed, List.map_cons, ih]

theorem transformed_output (rows : List Row) (r : Registers) :
    (transformed rows r).map Prod.snd = (scan (rows.map Prod.fst) r).output := by
  induction rows generalizing r with
  | nil => rfl
  | cons row rs ih => simp only [transformed, List.map_cons, scan, ih]

/-- Tape storage is unchanged by every primitive transition, even malformed
control states. The fixed seven-bit register bank is accounted for separately. -/
theorem step_storage (s : State) :
    (step s).tape.left.length+(step s).tape.right.length =
      s.tape.left.length+s.tape.right.length := by
  rcases s with ⟨⟨ls,rs⟩,r,phase⟩
  cases phase <;> cases ls <;> cases rs <;>
    simp [step, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]

theorem run_storage (n : Nat) (s : State) :
    (run n s).tape.left.length+(run n s).tape.right.length =
      s.tape.left.length+s.tape.right.length := by
  induction n generalizing s with
  | zero => rfl
  | succ n ih => exact (ih (step s)).trans (step_storage s)

/-- A signed scan uses n+2 supplied three-track cells. The two sign columns
are actual executed columns, not a convention silently dropped from cost. -/
theorem signed_machine_resources (p : List PairBit) (sa sb : Bool) (scratch : Registers) :
    let rows := (p ++ [(sa,sb),(sa,sb)]).map (fun ab => (ab,false))
    RunsToHalt (11*(p.length+2)+10) (initial rows scratch)
      (final (transformed rows (zeroCarry scratch))) ∧
    (transformed rows (zeroCarry scratch)).map Prod.snd = (signedScan p sa sb scratch).output := by
  dsimp only
  constructor
  · simpa using machine_exact ((p ++ [(sa,sb),(sa,sb)]).map (fun ab => (ab,false))) scratch
  · rw [transformed_output]
    simp only [List.map_map, Function.comp_def, List.map_id_fun']
    rfl

end SequentialBitAddition

#print axioms SequentialBitAddition.column_exact
#print axioms SequentialBitAddition.full_adder_identity
#print axioms SequentialBitAddition.scan_value
#print axioms SequentialBitAddition.scan_storage
#print axioms SequentialBitAddition.scan_append_output
#print axioms SequentialBitAddition.signed_scan_exact
#print axioms SequentialBitAddition.signed_scan_storage
#print axioms SequentialBitAddition.zero_shift_value
#print axioms SequentialBitAddition.zero_shift_storage
#check @SequentialBitAddition.signed_scan_exact

#print axioms SequentialBitAddition.machine_exact
#print axioms SequentialBitAddition.machine_result
#print axioms SequentialBitAddition.transformed_sources
#print axioms SequentialBitAddition.transformed_output
#print axioms SequentialBitAddition.step_storage
#print axioms SequentialBitAddition.run_storage
#print axioms SequentialBitAddition.signed_machine_resources
#check @SequentialBitAddition.machine_exact
