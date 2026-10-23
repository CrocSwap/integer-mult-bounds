import PairedBitXorScan

/-!
Copyright (c) 2026 James Chang. Released under Apache 2.0.
Prepared with OpenAI assistance.

Explicit finite marked-alphabet refinement of PairedBitXorScan. Control reads
only the current symbol. There is no boundary-observation instruction. The two
sentinels are actual supplied cells; installing this input format is separate.
-/
namespace CurrentMain.PairedBitXorScan.Tape

/-- Unrepresented cells are blank; this is not a boundary detector. -/
def readHead {α : Type} (blank : α) (t : Tape α) : α :=
  match t.right with | [] => blank | a :: _ => a

def writeHead {α : Type} (a : α) (t : Tape α) : Tape α :=
  match t.right with
  | [] => ⟨t.left, [a]⟩
  | _ :: rs => ⟨t.left, a :: rs⟩

/-- One physical head move, extending the finite representation by a blank
when needed. The checked prepared execution never uses that extension. -/
def moveRight {α : Type} (blank : α) (t : Tape α) : Tape α :=
  match t.right with
  | [] => ⟨blank :: t.left, []⟩
  | a :: rs => ⟨a :: t.left, rs⟩

def moveLeft {α : Type} (blank : α) (t : Tape α) : Tape α :=
  match t.left with
  | [] => ⟨[], blank :: t.right⟩
  | a :: ls => ⟨ls, a :: t.right⟩

end CurrentMain.PairedBitXorScan.Tape

namespace CurrentMain.MarkedBitXorScan
open PairedBitXorScan (Tape Pair xorPair value)

/-- Seven tape symbols: blank, two distinct markers and four data pairs. -/
inductive Symbol where
  | blank | leftMarker | rightMarker | data (target source : Bool)
  deriving DecidableEq

inductive Phase where
  | enter | load | write | clear | advance | rewind | halt
  deriving DecidableEq

structure State where
  tape : Tape Symbol
  scratch : Bool
  phase : Phase
  deriving DecidableEq

/-- A single bounded finite-alphabet transition. No phase tests zipper length
or emptiness. Only generic head movement handles implicit outside blanks. -/
def step (s : State) : State :=
  match s.phase with
  | .halt => s
  | .enter => match s.tape.readHead .blank with
    | .leftMarker => { s with tape := s.tape.moveRight .blank, phase := .load }
    | _ => { s with phase := .halt }
  | .load => match s.tape.readHead .blank with
    | .data _ b => { s with scratch := s.scratch ^^ b, phase := .write }
    | .rightMarker => { s with phase := .rewind }
    | _ => { s with phase := .halt }
  | .write => match s.tape.readHead .blank with
    | .data a b => { s with tape := s.tape.writeHead (.data (a ^^ s.scratch) b), phase := .clear }
    | _ => { s with phase := .halt }
  | .clear => match s.tape.readHead .blank with
    | .data _ b => { s with scratch := s.scratch ^^ b, phase := .advance }
    | _ => { s with phase := .halt }
  | .advance => { s with tape := s.tape.moveRight .blank, phase := .load }
  | .rewind => match s.tape.readHead .blank with
    | .leftMarker => { s with phase := .halt }
    | _ => { s with tape := s.tape.moveLeft .blank }

def run : Nat → State → State
  | 0, s => s
  | n + 1, s => run n (step s)

def cells (s : State) : Nat := s.tape.left.length + s.tape.right.length

/-- Exact first-halt execution together with a derived no-allocation invariant
for each actual transition. The public execution theorem supplies every field. -/
inductive RunsToHalt : Nat → State → State → Prop where
  | done (s : State) (h : s.phase = .halt) : RunsToHalt 0 s s
  | next {n : Nat} {s t : State} (h : s.phase ≠ .halt)
      (hsize : cells (step s) = cells s)
      (tail : RunsToHalt n (step s) t) : RunsToHalt (n + 1) s t

private theorem runs_sound {n : Nat} {s t : State}
    (h : RunsToHalt n s t) : run n s = t := by
  induction h with
  | done => rfl
  | next _ _ _ ih => exact ih

private theorem halt_run (s : State) (h : s.phase = .halt) (k : Nat) : run k s = s := by
  induction k with
  | zero => rfl
  | succ k ih => simpa [run, step, h] using ih

private theorem runs_storage {n : Nat} {s t : State}
    (h : RunsToHalt n s t) (k : Nat) : cells (run k s) = cells s := by
  induction h generalizing k with
  | done s hh => rw [halt_run s hh]
  | next _ hsize _ ih =>
    cases k with
    | zero => rfl
    | succ k => exact (ih k).trans hsize

def dataSymbol (p : Pair) : Symbol := .data p.1 p.2

def marked (rows : List Pair) : List Symbol :=
  .leftMarker :: rows.map dataSymbol ++ [.rightMarker]

def initial (rows : List Pair) : State := ⟨⟨[], marked rows⟩, false, .enter⟩
def final (rows : List Pair) : State := ⟨⟨[], marked rows⟩, false, .halt⟩

private theorem rewind_step (ls rs : List Symbol) (b : Bool)
    (hhead : (⟨ls, rs⟩ : Tape Symbol).readHead .blank ≠ .leftMarker) :
    step ⟨⟨ls, rs⟩, b, .rewind⟩ =
      ⟨(⟨ls, rs⟩ : Tape Symbol).moveLeft .blank, b, .rewind⟩ := by
  cases he : (⟨ls, rs⟩ : Tape Symbol).readHead .blank <;> simp_all [step]

private theorem rewind_exact (ls : List Pair) (rs : List Symbol) (b : Bool)
    (hhead : (⟨[], rs⟩ : Tape Symbol).readHead .blank ≠ .leftMarker) :
    RunsToHalt (ls.length + 2)
      ⟨⟨ls.map dataSymbol ++ [.leftMarker], rs⟩, b, .rewind⟩
      ⟨⟨[], .leftMarker :: (ls.reverse.map dataSymbol ++ rs)⟩, b, .halt⟩ := by
  induction ls generalizing rs with
  | nil =>
    have hs : step (⟨⟨([] : List Pair).map dataSymbol ++ [Symbol.leftMarker], rs⟩,
        b, Phase.rewind⟩ : State) =
        ⟨(⟨([] : List Pair).map dataSymbol ++ [Symbol.leftMarker], rs⟩ : Tape Symbol).moveLeft
          Symbol.blank, b, Phase.rewind⟩ :=
      rewind_step (([] : List Pair).map dataSymbol ++ [Symbol.leftMarker]) rs b hhead
    apply RunsToHalt.next (by simp)
    · rw [hs]
      simp [cells, Tape.moveLeft, Nat.add_comm]
    · rw [hs]
      apply RunsToHalt.next (by simp [Tape.moveLeft])
      · simp [cells, step, Tape.readHead, Tape.moveLeft]
      · simpa [step, Tape.readHead, Tape.moveLeft] using
          RunsToHalt.done (⟨⟨[], .leftMarker :: rs⟩, b, .halt⟩ : State) rfl
  | cons row ls ih =>
    have hs : step (⟨⟨(row :: ls).map dataSymbol ++ [Symbol.leftMarker], rs⟩,
        b, Phase.rewind⟩ : State) =
        ⟨(⟨(row :: ls).map dataSymbol ++ [Symbol.leftMarker], rs⟩ : Tape Symbol).moveLeft
          Symbol.blank, b, Phase.rewind⟩ :=
      rewind_step ((row :: ls).map dataSymbol ++ [Symbol.leftMarker]) rs b hhead
    apply RunsToHalt.next (by simp)
    · rw [hs]
      simp [cells, Tape.moveLeft, Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
    · rw [hs]
      have h := ih (dataSymbol row :: rs) (by simp [Tape.readHead, dataSymbol])
      simpa [Tape.moveLeft, List.reverse_cons, List.map_append, List.append_assoc] using h

private theorem cell_four {n : Nat} (row : Pair) (ls : List Symbol)
    (rs : List Symbol) (t : State)
    (h : RunsToHalt n ⟨⟨dataSymbol (xorPair row) :: ls, rs⟩, false, .load⟩ t) :
    RunsToHalt (n + 4) ⟨⟨ls, dataSymbol row :: rs⟩, false, .load⟩ t := by
  rcases row with ⟨a, b⟩
  cases a <;> cases b
  all_goals
    apply RunsToHalt.next (by simp)
    · simp [cells, step, Tape.readHead, Tape.writeHead, Tape.moveRight, dataSymbol, xorPair]
    · apply RunsToHalt.next (by simp [step, Tape.readHead, dataSymbol])
      · simp [cells, step, Tape.readHead, Tape.writeHead, Tape.moveRight, dataSymbol, xorPair]
      · apply RunsToHalt.next (by simp [step, Tape.readHead, Tape.writeHead, dataSymbol])
        · simp [cells, step, Tape.readHead, Tape.writeHead, Tape.moveRight, dataSymbol, xorPair]
        · apply RunsToHalt.next (by simp [step, Tape.readHead, Tape.writeHead, dataSymbol])
          · simp [cells, step, Tape.readHead, Tape.writeHead, Tape.moveRight, dataSymbol, xorPair,
              Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
          · simpa [step, Tape.readHead, Tape.writeHead, Tape.moveRight, dataSymbol, xorPair] using h

private theorem scan_from (rs ls : List Pair) :
    RunsToHalt (5 * rs.length + ls.length + 3)
      ⟨⟨ls.map dataSymbol ++ [.leftMarker], rs.map dataSymbol ++ [.rightMarker]⟩, false, .load⟩
      (final (ls.reverse ++ rs.map xorPair)) := by
  induction rs generalizing ls with
  | nil =>
    apply RunsToHalt.next (by simp)
    · simp [cells, step, Tape.readHead]
    · simpa [step, final, marked, Tape.readHead, List.map_append] using
        rewind_exact ls [.rightMarker] false (by simp [Tape.readHead])
  | cons row rs ih =>
    have h := cell_four row (ls.map dataSymbol ++ [.leftMarker])
      (rs.map dataSymbol ++ [.rightMarker]) _ (ih (xorPair row :: ls))
    have hc : 5 * rs.length + (xorPair row :: ls).length + 3 + 4 =
        5 * (row :: rs).length + ls.length + 3 := by
      simp only [List.length_cons]
      omega
    rw [hc] at h
    simpa [final, marked, List.reverse_cons, List.map_append, List.append_assoc] using h

/-- Explicit markers replace the earlier boundary sensor. The count includes
one entry move, 4n forward steps, right-marker detection, n+1 rewind moves,
and left-marker detection: exactly 5n+4, including n=0. -/
theorem marked_scan_exact (rows : List Pair) :
    RunsToHalt (5 * rows.length + 4) (initial rows) (final (rows.map xorPair)) := by
  apply RunsToHalt.next (by simp [initial])
  · simp [cells, step, initial, marked, Tape.readHead, Tape.moveRight,
      Nat.add_assoc, Nat.add_comm, Nat.add_left_comm]
  · simpa [step, initial, marked, Tape.readHead, Tape.moveRight] using scan_from rows []

theorem marked_scan_result (rows : List Pair) :
    run (5 * rows.length + 4) (initial rows) = final (rows.map xorPair) :=
  runs_sound (marked_scan_exact rows)

/-- Actual tape footprint for every prefix, including time after halting. -/
theorem marked_scan_storage (rows : List Pair) (k : Nat) :
    cells (run k (initial rows)) = rows.length + 2 := by
  have h := runs_storage (marked_scan_exact rows) k
  simpa [cells, initial, marked] using h

/-- The two implementations have exactly the same data result; the marked
machine charges two additional transitions for explicit marker/head motion. -/
theorem zipper_refinement (rows : List Pair) :
    run (5 * rows.length + 4) (initial rows) =
      ⟨⟨[], marked (PairedBitXorScan.run (5 * rows.length + 2)
        (PairedBitXorScan.initial rows)).tape.right⟩, false, .halt⟩ := by
  rw [marked_scan_result, PairedBitXorScan.scan_result]
  rfl

/-- Reuse the accepted all-payload Nat XOR interpretation without reproving it. -/
theorem decoded_xor (rows : List Pair) :
    value ((rows.map xorPair).map Prod.fst) =
      value (rows.map Prod.fst) ^^^ value (rows.map Prod.snd) :=
  PairedBitXorScan.value_xor rows

end CurrentMain.MarkedBitXorScan

#print axioms CurrentMain.MarkedBitXorScan.marked_scan_exact
#print axioms CurrentMain.MarkedBitXorScan.marked_scan_result
#print axioms CurrentMain.MarkedBitXorScan.marked_scan_storage
#print axioms CurrentMain.MarkedBitXorScan.zipper_refinement
#print axioms CurrentMain.MarkedBitXorScan.decoded_xor
#check @CurrentMain.MarkedBitXorScan.marked_scan_exact
#check @CurrentMain.MarkedBitXorScan.marked_scan_storage
