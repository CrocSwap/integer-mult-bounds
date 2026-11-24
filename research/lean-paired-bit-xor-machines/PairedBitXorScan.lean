import Init.Data.List.Lemmas
import Init.Data.Nat.Bitwise.Lemmas

/-!
Copyright (c) 2026 James Chang. Released under Apache 2.0.
Prepared with OpenAI assistance. Uses the Lean core List and Nat bitwise APIs.

An explicit finite-alphabet, two-track in-place XOR machine. The zipper is a
mathematical tape representation: `left` is behind the head in reverse order,
`right` starts at the head. Each transition inspects only the current pair,
changes at most one bit, or moves the head by one cell. Empty-list boundaries
represent supplied end markers; no runtime length counter or Nat XOR is used.
-/
namespace CurrentMain.PairedBitXorScan

structure Tape (α : Type) where
  left : List α
  right : List α
  deriving DecidableEq

abbrev Pair := Bool × Bool

inductive Phase where
  | load | write | clear | advance | rewind | halt
  deriving DecidableEq

structure State where
  tape : Tape Pair
  scratch : Bool
  phase : Phase
  deriving DecidableEq

/-- One finite-alphabet transition. The source track is never written. -/
def step (s : State) : State :=
  match s.phase with
  | .halt => s
  | .load => match s.tape.right with
    | [] => { s with phase := .rewind }
    | row :: _ => { s with scratch := s.scratch ^^ row.2, phase := .write }
  | .write => match s.tape.right with
    | [] => { s with phase := .halt }
    | row :: rs =>
      ⟨⟨s.tape.left, (row.1 ^^ s.scratch, row.2) :: rs⟩, s.scratch, .clear⟩
  | .clear => match s.tape.right with
    | [] => { s with phase := .halt }
    | row :: _ => { s with scratch := s.scratch ^^ row.2, phase := .advance }
  | .advance => match s.tape.right with
    | [] => { s with phase := .halt }
    | row :: rs =>
      { s with tape := ⟨row :: s.tape.left, rs⟩, phase := .load }
  | .rewind => match s.tape.left with
    | [] => { s with phase := .halt }
    | row :: ls => { s with tape := ⟨ls, row :: s.tape.right⟩ }

/-- External observation fuel, not a register or an executed unary counter. -/
def run : Nat → State → State
  | 0, s => s
  | n + 1, s => run n (step s)

/-- Counts transitions up to the first halt, disallowing padded halt steps. -/
inductive RunsToHalt : Nat → State → State → Prop where
  | done (s : State) (h : s.phase = .halt) : RunsToHalt 0 s s
  | next {n : Nat} {s t : State} (h : s.phase ≠ .halt)
      (tail : RunsToHalt n (step s) t) : RunsToHalt (n + 1) s t

private theorem runs_sound {n : Nat} {s t : State}
    (h : RunsToHalt n s t) : run n s = t := by
  induction h with
  | done => rfl
  | next _ _ ih => exact ih

/-- A transformed tape cell; this specification is not executed in one step. -/
def xorPair (p : Pair) : Pair := (p.1 ^^ p.2, p.2)

def initial (rows : List Pair) : State := ⟨⟨[], rows⟩, false, .load⟩
def final (rows : List Pair) : State := ⟨⟨[], rows⟩, false, .halt⟩

private theorem rewind_exact (ls rs : List Pair) (b : Bool) :
    RunsToHalt (ls.length + 1) ⟨⟨ls, rs⟩, b, .rewind⟩
      ⟨⟨[], ls.reverse ++ rs⟩, b, .halt⟩ := by
  induction ls generalizing rs with
  | nil =>
    exact RunsToHalt.next (by simp [step]) (RunsToHalt.done _ rfl)
  | cons row ls ih =>
    apply RunsToHalt.next (by simp [step])
    simpa [step, List.reverse_cons, List.append_assoc] using ih (row :: rs)

private theorem cell_four {n : Nat} (row : Pair) (ls rs : List Pair) (t : State)
    (h : RunsToHalt n ⟨⟨xorPair row :: ls, rs⟩, false, .load⟩ t) :
    RunsToHalt (n + 4) ⟨⟨ls, row :: rs⟩, false, .load⟩ t := by
  rcases row with ⟨a, b⟩
  cases a <;> cases b
  all_goals
    apply RunsToHalt.next (by simp [step])
    apply RunsToHalt.next (by simp [step])
    apply RunsToHalt.next (by simp [step])
    apply RunsToHalt.next (by simp [step])
    simpa [step, xorPair] using h

private theorem scan_from (rs ls : List Pair) :
    RunsToHalt (5 * rs.length + ls.length + 2)
      ⟨⟨ls, rs⟩, false, .load⟩
      (final (ls.reverse ++ rs.map xorPair)) := by
  induction rs generalizing ls with
  | nil =>
    simpa [step, final] using
      (RunsToHalt.next (s := (⟨⟨ls, []⟩, false, .load⟩ : State))
        (by simp [step]) (rewind_exact ls [] false))
  | cons row rs ih =>
    have h := cell_four row ls rs _ (ih (xorPair row :: ls))
    have hc : 5 * rs.length + (xorPair row :: ls).length + 2 + 4 =
        5 * (row :: rs).length + ls.length + 2 := by
      simp only [List.length_cons]
      omega
    rw [hc] at h
    simpa [final, List.reverse_cons, List.append_assoc] using h

/-- Exact first-halt count: four forward transitions per pair, n rewind moves,
and two end-marker transitions. Head and clean scratch are returned. -/
theorem scan_exact (rows : List Pair) :
    RunsToHalt (5 * rows.length + 2) (initial rows)
      (final (rows.map xorPair)) := by
  simpa [initial] using scan_from rows []

theorem scan_result (rows : List Pair) :
    run (5 * rows.length + 2) (initial rows) = final (rows.map xorPair) :=
  runs_sound (scan_exact rows)

/-- Little-endian unsigned interpretation. This is a specification decoder. -/
def value : List Bool → Nat
  | [] => 0
  | b :: bs => 2 * value bs + b.toNat

private theorem low_testBit (x : Nat) (b : Bool) (i : Nat) :
    (2 * x + b.toNat).testBit i =
      match i with | 0 => b | j + 1 => x.testBit j := by
  have h := Nat.testBit_two_pow_mul_add x (b := b.toNat) (i := 1)
    (by cases b <;> decide) i
  cases i with
  | zero => cases b <;> simp
  | succ i => simpa using h

private theorem xor_low (x y : Nat) (a b : Bool) :
    (2 * x + a.toNat) ^^^ (2 * y + b.toNat) =
      2 * (x ^^^ y) + (a ^^ b).toNat := by
  apply Nat.eq_of_testBit_eq
  intro i
  rw [Nat.testBit_xor, low_testBit, low_testBit, low_testBit]
  cases i <;> simp [Nat.testBit_xor]

/-- All-width decoded XOR, with no finite decision or input-value enumeration. -/
theorem value_xor (rows : List Pair) :
    value ((rows.map xorPair).map Prod.fst) =
      value (rows.map Prod.fst) ^^^ value (rows.map Prod.snd) := by
  induction rows with
  | nil => simp [value]
  | cons row rows ih =>
    simp only [List.map_cons, value, xorPair]
    rw [ih, xor_low]

theorem source_preserved (rows : List Pair) :
    (rows.map xorPair).map Prod.snd = rows.map Prod.snd := by
  induction rows with
  | nil => rfl
  | cons row rows ih => exact congrArg (row.2 :: ·) ih

theorem xor_twice (rows : List Pair) :
    (rows.map xorPair).map xorPair = rows := by
  induction rows with
  | nil => rfl
  | cons row rows ih =>
    have hr : xorPair (xorPair row) = row := by
      rcases row with ⟨a, b⟩
      cases a <;> cases b <;> rfl
    simpa only [List.map_cons, hr] using congrArg (row :: ·) ih

/-- Two consecutive invocations, including their explicit reset of the halt
control state to load; each invocation returns the head and clean scratch. -/
theorem two_scans (rows : List Pair) :
    run (5 * rows.length + 2)
      { run (5 * rows.length + 2) (initial rows) with phase := .load } =
      final rows := by
  rw [scan_result]
  change run (5 * rows.length + 2) (initial (rows.map xorPair)) = final rows
  have h := scan_result (rows.map xorPair)
  simpa only [List.length_map, xor_twice] using h

/-- No tape cells are allocated or discarded by any transition, including
malformed-control states. One scratch bit and finite control are separate. -/
theorem step_storage (s : State) :
    (step s).tape.left.length + (step s).tape.right.length =
      s.tape.left.length + s.tape.right.length := by
  rcases s with ⟨⟨ls, rs⟩, b, phase⟩
  cases phase <;> cases ls <;> cases rs <;>
    simp [step, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]

theorem run_storage (n : Nat) (s : State) :
    (run n s).tape.left.length + (run n s).tape.right.length =
      s.tape.left.length + s.tape.right.length := by
  induction n generalizing s with
  | zero => rfl
  | succ n ih => exact (ih (step s)).trans (step_storage s)

end CurrentMain.PairedBitXorScan

#print axioms CurrentMain.PairedBitXorScan.scan_exact
#print axioms CurrentMain.PairedBitXorScan.scan_result
#print axioms CurrentMain.PairedBitXorScan.value_xor
#print axioms CurrentMain.PairedBitXorScan.source_preserved
#print axioms CurrentMain.PairedBitXorScan.xor_twice
#print axioms CurrentMain.PairedBitXorScan.two_scans
#print axioms CurrentMain.PairedBitXorScan.step_storage
#print axioms CurrentMain.PairedBitXorScan.run_storage
#check @CurrentMain.PairedBitXorScan.scan_exact
#check @CurrentMain.PairedBitXorScan.value_xor
