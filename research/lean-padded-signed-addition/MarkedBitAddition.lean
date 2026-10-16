import MarkedBitXorScan
import SequentialBitAddition

/-!
Copyright (c) 2026 James Chang. Released under Apache 2.0.
Prepared with OpenAI assistance.

Literal marked-alphabet refinement of the accepted SequentialBitAddition
controller. Reuses its Boolean gates, transformed-word specification and
integer/signed arithmetic. The two boundary markers are real supplied cells.
No instruction can observe zipper emptiness. Format creation is caller work.
-/
set_option Elab.async false
set_option autoImplicit false

namespace MarkedBitAddition
open CurrentMain.PairedBitXorScan (Tape)

abbrev Row := SequentialBitAddition.Row
abbrev Registers := SequentialBitAddition.Registers

/-- Eleven symbols: blank, L, R and eight three-track bit rows. -/
inductive Symbol where
  | blank | leftMarker | rightMarker | data (row : Row)
  deriving DecidableEq

inductive Phase where
  | enter | body (p : SequentialBitAddition.Phase)
  deriving DecidableEq

structure State where
  tape : Tape Symbol
  registers : Registers
  phase : Phase
  deriving DecidableEq

/-- All branching is on finite control or the current finite-alphabet symbol.
The generic head operations charge one actual cell move. Gate and clear
operations are the unchanged accepted bounded Boolean-register operations. -/
def step (s : State) : State :=
  match s.phase with
  | .enter => match s.tape.readHead .blank with
    | .leftMarker => { s with tape := s.tape.moveRight .blank, phase := .body .initialize }
    | _ => { s with phase := .body .halt }
  | .body .halt => s
  | .body .initialize =>
      { s with registers := SequentialBitAddition.zeroCarry s.registers, phase := .body .test }
  | .body .test => match s.tape.readHead .blank with
    | .data _ => { s with phase := .body (.gate .readLeft) }
    | .rightMarker => { s with phase := .body .rewind }
    | _ => { s with phase := .body .halt }
  | .body (.gate g) => match s.tape.readHead .blank with
    | .data row =>
      { s with registers := SequentialBitAddition.gateStep row.1 g s.registers, phase := .body (SequentialBitAddition.nextGate g) }
    | _ => { s with phase := .body .halt }
  | .body .write => match s.tape.readHead .blank with
    | .data row =>
      { s with tape := s.tape.writeHead (.data (row.1, s.registers.sum)), phase := .body .advance }
    | _ => { s with phase := .body .halt }
  | .body .advance => { s with tape := s.tape.moveRight .blank, phase := .body .test }
  | .body .rewind => match s.tape.readHead .blank with
    | .leftMarker => { s with phase := .body (.clear .x) }
    | _ => { s with tape := s.tape.moveLeft .blank }
  | .body (.clear slot) =>
      { s with registers := SequentialBitAddition.clearSlot slot s.registers, phase := .body (SequentialBitAddition.nextClear slot) }

/-- External observation fuel, not a runtime arithmetic counter. -/
def run : Nat → State → State
  | 0, s => s
  | n + 1, s => run n (step s)

inductive RunsToHalt : Nat → State → State → Prop where
  | done (s : State) (h : s.phase = .body .halt) : RunsToHalt 0 s s
  | next {n : Nat} {s t : State} (h : s.phase ≠ .body .halt)
      (tail : RunsToHalt n (step s) t) : RunsToHalt (n + 1) s t

private theorem runs_sound {n : Nat} {s t : State} (h : RunsToHalt n s t) :
    run n s = t := by
  induction h with
  | done => rfl
  | next _ _ ih => exact ih

private theorem runs_live {n : Nat} {s t : State} (h : RunsToHalt n s t)
    (k : Nat) (hk : k < n) : (run k s).phase ≠ .body .halt := by
  induction h generalizing k with
  | done => omega
  | next live tail ih =>
      cases k with
      | zero => exact live
      | succ k => exact ih k (by omega)

private theorem halt_run (s : State) (h : s.phase = .body .halt) (k : Nat) :
    run k s = s := by
  induction k with
  | zero => rfl
  | succ k ih => simpa [run, step, h] using ih

def marked (rows : List Row) : Tape Symbol :=
  ⟨[], .leftMarker :: rows.map Symbol.data ++ [.rightMarker]⟩

def initial (rows : List Row) (scratch : Registers) : State :=
  ⟨marked rows, scratch, .enter⟩

def final (rows : List Row) : State :=
  ⟨marked rows, SequentialBitAddition.clearRegisters, .body .halt⟩

private theorem clear_seven (tape : Tape Symbol) (r : Registers) :
    RunsToHalt 7 ⟨tape, r, .body (.clear .x)⟩
      ⟨tape, SequentialBitAddition.clearRegisters, .body .halt⟩ := by
  apply RunsToHalt.next (by simp [step, SequentialBitAddition.nextClear])
  apply RunsToHalt.next (by simp [step, SequentialBitAddition.nextClear])
  apply RunsToHalt.next (by simp [step, SequentialBitAddition.nextClear])
  apply RunsToHalt.next (by simp [step, SequentialBitAddition.nextClear])
  apply RunsToHalt.next (by simp [step, SequentialBitAddition.nextClear])
  apply RunsToHalt.next (by simp [step, SequentialBitAddition.nextClear])
  apply RunsToHalt.next (by simp [step, SequentialBitAddition.nextClear])
  exact RunsToHalt.done _ rfl

/-- Rewind across actual data and R cells, then test the actual L cell.
The extra L-directed move is included, followed by seven explicit clears. -/
private theorem rewind_exact (ls rs : List Row) (r : Registers) :
    RunsToHalt (ls.length + 9)
      ⟨⟨ls.map Symbol.data ++ [.leftMarker], rs.map Symbol.data ++ [.rightMarker]⟩,
        r, .body .rewind⟩
      (final (ls.reverse ++ rs)) := by
  induction ls generalizing rs with
  | nil =>
      apply RunsToHalt.next (by simp)
      have hs : step (⟨⟨[.leftMarker], rs.map Symbol.data ++ [.rightMarker]⟩,
          r, .body .rewind⟩ : State) =
          ⟨marked rs, r, .body .rewind⟩ := by
        cases rs <;> rfl
      simp only [List.map_nil, List.nil_append, List.reverse_nil]
      rw [hs]
      apply RunsToHalt.next (by simp)
      simpa [step, marked, Tape.readHead, final] using clear_seven (marked rs) r
  | cons row ls ih =>
      apply RunsToHalt.next (by simp)
      have hs : step (⟨⟨(row :: ls).map Symbol.data ++ [.leftMarker],
          rs.map Symbol.data ++ [.rightMarker]⟩, r, .body .rewind⟩ : State) =
          ⟨⟨ls.map Symbol.data ++ [.leftMarker],
            (row :: rs).map Symbol.data ++ [.rightMarker]⟩, r, .body .rewind⟩ := by
        cases rs <;> rfl
      rw [hs]
      simpa [final, marked, List.reverse_cons, List.map_append, List.append_assoc] using
        ih (row :: rs)

private theorem column_ten {n : Nat} (row : Row) (ls rs : List Symbol)
    (r : Registers) (t : State)
    (h : RunsToHalt n
      ⟨⟨Symbol.data (row.1, (SequentialBitAddition.column row.1 r).sum) :: ls, rs⟩,
        SequentialBitAddition.column row.1 r, .body .test⟩ t) :
    RunsToHalt (n + 10) ⟨⟨ls, Symbol.data row :: rs⟩, r, .body .test⟩ t := by
  apply RunsToHalt.next (by simp [step, Tape.readHead, SequentialBitAddition.nextGate])
  apply RunsToHalt.next (by simp [step, Tape.readHead, SequentialBitAddition.nextGate])
  apply RunsToHalt.next (by simp [step, Tape.readHead, SequentialBitAddition.nextGate])
  apply RunsToHalt.next (by simp [step, Tape.readHead, SequentialBitAddition.nextGate])
  apply RunsToHalt.next (by simp [step, Tape.readHead, SequentialBitAddition.nextGate])
  apply RunsToHalt.next (by simp [step, Tape.readHead, SequentialBitAddition.nextGate])
  apply RunsToHalt.next (by simp [step, Tape.readHead, SequentialBitAddition.nextGate])
  apply RunsToHalt.next (by simp [step, Tape.readHead, SequentialBitAddition.nextGate])
  apply RunsToHalt.next (by simp [step, Tape.readHead, SequentialBitAddition.nextGate])
  apply RunsToHalt.next (by simp [step, Tape.readHead, SequentialBitAddition.nextGate])
  simpa only [step, Tape.readHead, Tape.writeHead, Tape.moveRight,
    SequentialBitAddition.nextGate, SequentialBitAddition.column,
    SequentialBitAddition.runGates, SequentialBitAddition.columnGates,
    SequentialBitAddition.gateStep] using h

private theorem scan_from (rs ls : List Row) (r : Registers) :
    RunsToHalt (11 * rs.length + ls.length + 10)
      ⟨⟨ls.map Symbol.data ++ [.leftMarker], rs.map Symbol.data ++ [.rightMarker]⟩,
        r, .body .test⟩
      (final (ls.reverse ++ SequentialBitAddition.transformed rs r)) := by
  induction rs generalizing ls r with
  | nil =>
      have h := RunsToHalt.next
        (s := (⟨⟨ls.map Symbol.data ++ [.leftMarker], [.rightMarker]⟩, r, .body .test⟩ : State))
        (by simp) (rewind_exact ls [] r)
      simpa [step, Tape.readHead, SequentialBitAddition.transformed] using h
  | cons row rs ih =>
      have h := column_ten row (ls.map Symbol.data ++ [.leftMarker])
        (rs.map Symbol.data ++ [.rightMarker]) r _
        (ih ((row.1, (SequentialBitAddition.column row.1 r).sum) :: ls)
          (SequentialBitAddition.column row.1 r))
      have hc : 11 * rs.length + ((row.1, (SequentialBitAddition.column row.1 r).sum) :: ls).length + 10 + 10 =
          11 * (row :: rs).length + ls.length + 10 := by
        simp only [List.length_cons]
        omega
      rw [hc] at h
      simpa [SequentialBitAddition.transformed, List.reverse_cons, List.append_assoc] using h

/-- Complete marked implementation. The 11n+12 invoice includes one entry
move, one carry reset, ten forward transitions per data row, R detection,
n+1 physical rewind moves, L detection and seven register clears. -/
theorem machine_exact (rows : List Row) (scratch : Registers) :
    RunsToHalt (11 * rows.length + 12) (initial rows scratch)
      (final (SequentialBitAddition.transformed rows (SequentialBitAddition.zeroCarry scratch))) := by
  apply RunsToHalt.next (by simp [initial])
  apply RunsToHalt.next (by simp [step, initial, marked, Tape.readHead])
  simpa [step, initial, marked, Tape.readHead, Tape.moveRight, Nat.add_assoc] using
    scan_from rows [] (SequentialBitAddition.zeroCarry scratch)

theorem machine_result (rows : List Row) (scratch : Registers) :
    run (11 * rows.length + 12) (initial rows scratch) =
      final (SequentialBitAddition.transformed rows (SequentialBitAddition.zeroCarry scratch)) :=
  runs_sound (machine_exact rows scratch)

theorem machine_first_halt (rows : List Row) (scratch : Registers) :
    (run (11 * rows.length + 12) (initial rows scratch)).phase = .body .halt ∧
      ∀ k < 11 * rows.length + 12, (run k (initial rows scratch)).phase ≠ .body .halt := by
  constructor
  · rw [machine_result]; rfl
  · exact runs_live (machine_exact rows scratch)

def tapeCells (t : Tape Symbol) : Nat := t.left.length + t.right.length
def cells (s : State) : Nat := tapeCells s.tape

private theorem write_cells (t : Tape Symbol) (a : Symbol) :
    tapeCells t ≤ tapeCells (t.writeHead a) := by
  rcases t with ⟨ls, rs⟩
  cases rs <;> simp [tapeCells, Tape.writeHead]

private theorem right_cells (t : Tape Symbol) :
    tapeCells t ≤ tapeCells (t.moveRight .blank) := by
  rcases t with ⟨ls, rs⟩
  cases rs <;> simp [tapeCells, Tape.moveRight, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]

private theorem left_cells (t : Tape Symbol) :
    tapeCells t ≤ tapeCells (t.moveLeft .blank) := by
  rcases t with ⟨ls, rs⟩
  cases ls <;> simp [tapeCells, Tape.moveLeft, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]

private theorem step_cells (s : State) : cells s ≤ cells (step s) := by
  cases hp : s.phase with
  | enter =>
      cases hs : s.tape.readHead .blank <;> simp only [step, hp, hs, cells]
      all_goals first | exact Nat.le_refl _ | exact right_cells s.tape
  | body p =>
      cases p with
      | halt => simp [step, hp]
      | «initialize» => simp [step, hp, cells]
      | test => cases hs : s.tape.readHead .blank <;> simp [step, hp, hs, cells]
      | gate g => cases hs : s.tape.readHead .blank <;> simp [step, hp, hs, cells]
      | write =>
          cases hs : s.tape.readHead .blank <;> simp only [step, hp, hs, cells]
          all_goals first | exact Nat.le_refl _ | exact write_cells s.tape _
      | advance => simpa [step, hp, cells] using right_cells s.tape
      | rewind =>
          cases hs : s.tape.readHead .blank <;> simp only [step, hp, hs, cells]
          all_goals first | exact Nat.le_refl _ | exact left_cells s.tape
      | clear slot => simp [step, hp, cells]

private theorem run_cells (k : Nat) (s : State) : cells s ≤ cells (run k s) := by
  induction k generalizing s with
  | zero => exact Nat.le_refl _
  | succ k ih => exact (step_cells s).trans (ih (step s))

private theorem trace_cells {n : Nat} {s t : State} (h : RunsToHalt n s t) (k : Nat) :
    cells (run k s) ≤ cells t := by
  induction h generalizing k with
  | done s halt => rw [halt_run s halt]
  | next live tail ih =>
      cases k with
      | zero => exact (step_cells _).trans (ih 0)
      | succ k => exact ih k

private theorem transformed_length (rows : List Row) (r : Registers) :
    (SequentialBitAddition.transformed rows r).length = rows.length := by
  have h := congrArg List.length (SequentialBitAddition.transformed_sources rows r)
  simpa only [List.length_map] using h

/-- Every prefix uses exactly the original n data cells and two real markers.
All seven Boolean registers and finite control are separate constant storage. -/
theorem machine_storage (rows : List Row) (scratch : Registers) (k : Nat) :
    cells (run k (initial rows scratch)) = rows.length + 2 := by
  have lower := run_cells k (initial rows scratch)
  have upper := trace_cells (machine_exact rows scratch) k
  simp only [initial, final, cells, tapeCells, marked, List.length_cons,
    List.length_append, List.length_map, List.length_nil, Nat.zero_add,
    transformed_length] at lower upper ⊢
  omega

/-- Endpoint refinement of the accepted boundary-aware implementation.
The two additional transitions are marker entry and the extra return move. -/
theorem zipper_refinement (rows : List Row) (scratch : Registers) :
    run (11 * rows.length + 12) (initial rows scratch) =
      let old := SequentialBitAddition.run (11 * rows.length + 10)
        (SequentialBitAddition.initial rows scratch)
      ⟨marked old.tape.right, old.registers, .body old.phase⟩ := by
  rw [machine_result, SequentialBitAddition.machine_result]
  rfl

/-- Both immutable input tracks and the existing output arithmetic survive
this operational refinement; no new full-adder arithmetic is introduced. -/
theorem output_refinement (rows : List Row) (scratch : Registers) :
    let out := SequentialBitAddition.transformed rows (SequentialBitAddition.zeroCarry scratch)
    out.map Prod.fst = rows.map Prod.fst ∧
    out.map Prod.snd = (SequentialBitAddition.scan (rows.map Prod.fst)
      (SequentialBitAddition.zeroCarry scratch)).output := by
  exact ⟨SequentialBitAddition.transformed_sources _ _,
    SequentialBitAddition.transformed_output _ _⟩

/-- Two supplied sign columns are executed and counted, as are both markers.
This does not construct the sign-column format or restore old dirty output. -/
theorem signed_machine_resources (p : List SequentialBitAddition.PairBit)
    (sa sb : Bool) (scratch : Registers) :
    let rows := (p ++ [(sa, sb), (sa, sb)]).map (fun ab => (ab, false))
    RunsToHalt (11 * (p.length + 2) + 12) (initial rows scratch)
      (final (SequentialBitAddition.transformed rows (SequentialBitAddition.zeroCarry scratch))) ∧
    (SequentialBitAddition.transformed rows (SequentialBitAddition.zeroCarry scratch)).map Prod.snd =
      (SequentialBitAddition.signedScan p sa sb scratch).output ∧
    ∀ k, cells (run k (initial rows scratch)) = p.length + 4 := by
  dsimp only
  constructor
  · simpa using machine_exact ((p ++ [(sa, sb), (sa, sb)]).map (fun ab => (ab, false))) scratch
  · constructor
    · exact (SequentialBitAddition.signed_machine_resources p sa sb scratch).2
    · intro k
      simpa [Nat.add_assoc] using
        machine_storage ((p ++ [(sa, sb), (sa, sb)]).map (fun ab => (ab, false))) scratch k

end MarkedBitAddition

#print axioms MarkedBitAddition.machine_exact
#print axioms MarkedBitAddition.machine_result
#print axioms MarkedBitAddition.machine_first_halt
#print axioms MarkedBitAddition.machine_storage
#print axioms MarkedBitAddition.zipper_refinement
#print axioms MarkedBitAddition.output_refinement
#print axioms MarkedBitAddition.signed_machine_resources
#check @MarkedBitAddition.machine_exact
#check @MarkedBitAddition.signed_machine_resources
