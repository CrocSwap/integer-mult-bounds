import Lean

/-! A finite-alphabet, one-head, two-way tape incrementer.
The program has four control states and four tape symbols. Lists represent
only the two sides of its physical tape; the executable transition inspects
the current symbol and moves at most one cell. There is no Nat address or
remaining-count register in the transition. `run` fuel is proof instrumentation.
-/
namespace CurrentMain.CarryTape

inductive Symbol where
  | home | zero | one | stop
  deriving DecidableEq, Repr
inductive Phase where
  | enter | carry | rewind | halt
  deriving DecidableEq, Repr

structure Tape where
  left : List Symbol
  right : List Symbol
  phase : Phase
  deriving DecidableEq, Repr

/-- The current cell is the first right-hand symbol. Missing cells are stop
symbols; well-formed executions below never traverse outside both markers. -/
def read (s : Tape) : Symbol := s.right.headD .stop
def write (v : Symbol) (s : Tape) : Tape := {s with right := v :: s.right.tail}
def right (s : Tape) : Tape :=
  {s with left := read s :: s.left, right := s.right.tail}
def left (s : Tape) : Tape :=
  {s with left := s.left.tail, right := s.left.headD .home :: s.right}

structure Receipt where
  reads : Nat
  writes : Nat
  moves : Nat
  deriving DecidableEq, Repr

def Receipt.zero : Receipt := ⟨0, 0, 0⟩
def Receipt.add (a b : Receipt) : Receipt :=
  ⟨a.reads + b.reads, a.writes + b.writes, a.moves + b.moves⟩

/-- Each charge records the actual current-cell inspection, write, and head move.
Halting is inert; malformed enter/carry-home states halt after one inspection. -/
def step (s : Tape) : Tape × Receipt :=
  match s.phase, read s with
  | .halt, _ => (s, Receipt.zero)
  | .enter, .home => ({right s with phase := .carry}, ⟨1, 0, 1⟩)
  | .enter, _ => ({s with phase := .halt}, ⟨1, 0, 0⟩)
  | .carry, .zero => ({write .one s with phase := .rewind}, ⟨1, 1, 0⟩)
  | .carry, .one => (right (write .zero s), ⟨1, 1, 1⟩)
  | .carry, .stop => ({s with phase := .rewind}, ⟨1, 0, 0⟩)
  | .carry, .home => ({s with phase := .halt}, ⟨1, 0, 0⟩)
  | .rewind, .home => ({s with phase := .halt}, ⟨1, 0, 0⟩)
  | .rewind, _ => (left s, ⟨1, 0, 1⟩)

def run : Nat → Tape → Tape × Receipt
  | 0, s => (s, Receipt.zero)
  | n + 1, s =>
    let first := step s
    let rest := run n first.1
    (rest.1, first.2.add rest.2)

def encode : Bool → Symbol | false => .zero | true => .one
def cells (bits : List Bool) : List Symbol := bits.map encode ++ [.stop]
def homeTape (bits : List Bool) (phase : Phase) : Tape :=
  ⟨[], .home :: cells bits, phase⟩

def carryTape (pref bits : List Bool) : Tape :=
  ⟨pref.map encode ++ [.home], cells bits, .carry⟩
def rewindTape (pref bits : List Bool) : Tape :=
  ⟨pref.map encode ++ [.home], cells bits, .rewind⟩

/-- LSB-first modular increment, used only as the semantic specification. -/
def increment : List Bool → List Bool
  | [] => []
  | false :: bits => true :: bits
  | true :: bits => false :: increment bits

def trailingOnes : List Bool → Nat
  | [] => 0
  | false :: _ => 0
  | true :: bits => trailingOnes bits + 1

def bitWrites : List Bool → Nat
  | [] => 0
  | false :: _ => 1
  | true :: bits => bitWrites bits + 1

/-- The carry-stop configuration, preserving its actually live tape pref. -/
def carryFinish (pref : List Bool) : List Bool → Tape
  | [] => rewindTape pref []
  | false :: bits => rewindTape pref (true :: bits)
  | true :: bits => carryFinish (false :: pref) bits

theorem run_add (m n : Nat) (s : Tape) :
    run (m + n) s =
      let first := run m s
      let second := run n first.1
      (second.1, first.2.add second.2) := by
  induction m generalizing s with
  | zero => simp [run, Receipt.zero, Receipt.add]
  | succ m ih =>
    simp only [Nat.succ_add, run, ih]
    congr 1
    simp [Receipt.add, Nat.add_assoc]

theorem carry_execution (pref bits : List Bool) :
    run (trailingOnes bits + 1) (carryTape pref bits) =
      (carryFinish pref bits, ⟨trailingOnes bits + 1, bitWrites bits, trailingOnes bits⟩) := by
  induction bits generalizing pref with
  | nil => rfl
  | cons b bits ih =>
    cases b with
    | false => rfl
    | true =>
      simp only [trailingOnes, bitWrites, carryFinish, run]
      change (let rest := run (trailingOnes bits + 1) (carryTape (false :: pref) bits)
        (rest.1, (Receipt.mk 1 1 1).add rest.2)) = _
      rw [ih]
      simp [Receipt.add, Nat.add_comm]

theorem rewind_execution (pref bits : List Bool) :
    run (pref.length + 2) (rewindTape pref bits) =
      (homeTape (pref.reverse ++ bits) .halt, ⟨pref.length + 2, 0, pref.length + 1⟩) := by
  induction pref generalizing bits with
  | nil =>
    cases bits with
    | nil => rfl
    | cons b bits => cases b <;> rfl
  | cons b pref ih =>
    have hstep : step (rewindTape (b :: pref) bits) =
        (rewindTape pref (b :: bits), ⟨1, 0, 1⟩) := by
      cases bits with
      | nil => rfl
      | cons c bits => cases c <;> rfl
    rw [List.length_cons]
    change (let first := step (rewindTape (b :: pref) bits)
      let rest := run (pref.length + 2) first.1
      (rest.1, first.2.add rest.2)) = _
    simp only [hstep]
    rw [ih]
    simp [Receipt.add, List.reverse_cons, List.append_assoc, Nat.add_comm, Nat.add_left_comm]

theorem carryFinish_rewind (pref bits : List Bool) :
    run (pref.length + trailingOnes bits + 2) (carryFinish pref bits) =
      (homeTape (pref.reverse ++ increment bits) .halt,
        ⟨pref.length + trailingOnes bits + 2, 0, pref.length + trailingOnes bits + 1⟩) := by
  induction bits generalizing pref with
  | nil => simpa [carryFinish, trailingOnes, increment] using rewind_execution pref []
  | cons b bits ih =>
    cases b with
    | false => simpa [carryFinish, trailingOnes, increment] using rewind_execution pref (true :: bits)
    | true =>
      have h := ih (false :: pref)
      simpa [carryFinish, trailingOnes, increment, List.reverse_cons, List.append_assoc,
        Nat.add_assoc, Nat.add_comm, Nat.add_left_comm] using h

/-- Every input width and every bit pattern: exact increment, unchanged end
markers, head back at home, and exact paid tape-operation counts. -/
theorem increment_execution (bits : List Bool) :
    run (2 * trailingOnes bits + 4) (homeTape bits .enter) =
      (homeTape (increment bits) .halt,
        ⟨2 * trailingOnes bits + 4, bitWrites bits, 2 * trailingOnes bits + 2⟩) := by
  have hsplit : 2 * trailingOnes bits + 4 =
      1 + ((trailingOnes bits + 1) + (trailingOnes bits + 2)) := by omega
  rw [hsplit, run_add]
  have henter : run 1 (homeTape bits .enter) = (carryTape [] bits, ⟨1, 0, 1⟩) := rfl
  simp only [henter]
  rw [run_add]
  simp only [carry_execution]
  have hback := carryFinish_rewind [] bits
  simp only [List.length_nil, Nat.zero_add, List.reverse_nil, List.nil_append] at hback
  simp only [hback]
  simp only [Receipt.add]
  congr 2 <;> omega

theorem increment_length (bits : List Bool) : (increment bits).length = bits.length := by
  induction bits with
  | nil => rfl
  | cons b bits ih => cases b <;> simp [increment, ih]

/-- The exact receipt cannot be charged as O(1) per worst-case increment. -/
theorem all_ones_execution (n : Nat) :
    run (2 * n + 4) (homeTape (List.replicate n true) .enter) =
      (homeTape (List.replicate n false) .halt, ⟨2 * n + 4, n, 2 * n + 2⟩) := by
  have hi : increment (List.replicate n true) = List.replicate n false := by
    induction n with
    | zero => rfl
    | succ n ih => simp [List.replicate_succ, increment, ih]
  have ht : trailingOnes (List.replicate n true) = n := by
    clear hi
    induction n with
    | zero => rfl
    | succ n ih => simp [List.replicate_succ, trailingOnes, ih]
  have hw : bitWrites (List.replicate n true) = n := by
    clear hi ht
    induction n with
    | zero => rfl
    | succ n ih => simp [List.replicate_succ, bitWrites, ih]
  simpa [hi, ht, hw] using increment_execution (List.replicate n true)

end CurrentMain.CarryTape

#print axioms CurrentMain.CarryTape.run_add
#print axioms CurrentMain.CarryTape.carry_execution
#print axioms CurrentMain.CarryTape.rewind_execution
#print axioms CurrentMain.CarryTape.carryFinish_rewind
#print axioms CurrentMain.CarryTape.increment_execution
#print axioms CurrentMain.CarryTape.increment_length
#print axioms CurrentMain.CarryTape.all_ones_execution
