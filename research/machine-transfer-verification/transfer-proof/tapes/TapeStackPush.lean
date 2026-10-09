import TapeStack

/-! The matching fixed-control push/erase primitive. Together with TapeStack's
pop it gives a literal tape round trip with no ancestor-size cost term. -/
namespace TapeStackPush
open Turing TapeStack

inductive Mode where
  | copy | rewind | done
  deriving DecidableEq, Fintype

structure Config where
  mode : Mode
  source : Tape Symbol
  parking : Tape Symbol

def step (c : Config) : Config :=
  match c.mode with
  | .copy => match c.source.head with
      | .bit b => ⟨.copy, (c.source.write .blank).move .right,
                    (c.parking.write (.bit b)).move .right⟩
      | .blank => ⟨.rewind, c.source.move .left,
                    (c.parking.write .separator).move .right⟩
      | .separator => {c with mode := .done}
  | .rewind => match c.source.head with
      | .blank => {c with source := c.source.move .left}
      | .separator => ⟨.done, c.source.move .right, c.parking⟩
      | .bit _ => {c with mode := .done}
  | .done => c

def run : ℕ → Config → Config
  | 0, c => c
  | n+1, c => run n (step c)

theorem run_add (n k : ℕ) (c : Config) : run (n+k) c = run k (run n c) := by
  induction n generalizing c with
  | zero => simp [run]
  | succ n ih => simpa only [Nat.succ_add, run] using ih (step c)

def reading (erased : ℕ) (bits : List Bool) : Tape Symbol :=
  Tape.mk₂ (List.replicate erased .blank ++ [.separator]) (bits.map .bit)

def rewinding : ℕ → Tape Symbol
  | 0 => ⟨.separator, ListBlank.mk [], blankHalf⟩
  | n+1 => ⟨.blank, ListBlank.mk (List.replicate n .blank ++ [.separator]), blankHalf⟩

theorem read_bit (k : ℕ) (b : Bool) (rest : List Bool) :
    ((reading k (b::rest)).write .blank).move .right = reading (k+1) rest := by
  simp [reading, Tape.mk₂, Tape.mk', Tape.write, Tape.move,
    ListBlank.head_mk, ListBlank.tail_mk, ListBlank.cons_mk, List.replicate_succ]

theorem reading_empty (k : ℕ) :
    reading k [] = atEnd (List.replicate k .blank ++ [.separator]) := by
  simp [reading, Tape.mk₂, Tape.mk', atEnd, blankHalf, ListBlank.head_mk, ListBlank.tail_mk]

theorem start_rewind (k : ℕ) : (reading k []).move .left = rewinding k := by
  rw [reading_empty]
  cases k <;> simp [atEnd, rewinding, Tape.move, blankHalf, blank_mk,
    ListBlank.head_mk, ListBlank.tail_mk, List.replicate_succ]

theorem rewind_blank (k : ℕ) : (rewinding (k+1)).move .left = rewinding k := by
  cases k <;> simp [rewinding, Tape.move, blankHalf, blank_mk,
    ListBlank.head_mk, ListBlank.tail_mk, List.replicate_succ]

theorem rewind_end : (rewinding 0).move .right = atEnd [.separator] := by
  simp [rewinding, Tape.move, atEnd, blankHalf,
    ListBlank.head_mk, ListBlank.tail_mk, ListBlank.cons_mk]

theorem append_delimiter (stack : List Symbol) :
    ((atEnd stack).write .separator).move .right = atEnd (.separator::stack) := by
  simp [atEnd, Tape.write, Tape.move, blankHalf,
    ListBlank.head_mk, ListBlank.tail_mk, ListBlank.cons_mk]

theorem copy_correct (bits : List Bool) (erased : ℕ) (stack : List Symbol) :
    run (bits.length+1) ⟨.copy, reading erased bits, atEnd stack⟩ =
      ⟨.rewind, rewinding (erased+bits.length),
        atEnd (.separator :: (bits.reverse.map .bit ++ stack))⟩ := by
  induction bits generalizing erased stack with
  | nil =>
    change Config.mk .rewind ((reading erased []).move .left)
      (((atEnd stack).write .separator).move .right) =
      Config.mk .rewind (rewinding (erased+0)) (atEnd (.separator::stack))
    rw [start_rewind, append_delimiter, Nat.add_zero]
  | cons b rest ih =>
    rw [List.length_cons, Nat.succ_add, run]
    change run (rest.length+1)
      ⟨.copy, ((reading erased (b::rest)).write .blank).move .right,
        ((atEnd stack).write (.bit b)).move .right⟩ = _
    rw [read_bit, append_bit]
    simpa [List.reverse_cons, List.map_append, List.append_assoc, Nat.add_assoc,
      Nat.add_left_comm, Nat.add_comm] using ih (erased+1) (.bit b::stack)

theorem rewind_correct (n : ℕ) (park : Tape Symbol) :
    run (n+1) ⟨.rewind, rewinding n, park⟩ = ⟨.done, atEnd [.separator], park⟩ := by
  induction n with
  | zero =>
    change Config.mk .done ((rewinding 0).move .right) park = _
    rw [rewind_end]
  | succ n ih =>
    rw [Nat.succ_add, run]
    change run (n+1) ⟨.rewind, (rewinding (n+1)).move .left, park⟩ = _
    rw [rewind_blank]
    exact ih

/-- Push one delimited bitstream, erase its source, and restore the source
head to its marker-defined origin, in at most 2*n+2 finite-control steps. -/
theorem push_correct (bits : List Bool) (ancestor : List Symbol) :
    run (2*bits.length+2)
      ⟨.copy, Tape.mk₂ [.separator] (bits.map .bit), atEnd (.separator::ancestor)⟩ =
      ⟨.done, atEnd [.separator],
        atEnd (.separator :: (bits.reverse.map .bit ++ .separator::ancestor))⟩ := by
  have count : 2*bits.length+2 = (bits.length+1)+(bits.length+1) := by omega
  rw [count, run_add]
  have hc := copy_correct bits 0 (.separator::ancestor)
  simp only [Nat.zero_add] at hc
  change run (bits.length+1) (run (bits.length+1)
    ⟨.copy, reading 0 bits, atEnd (.separator::ancestor)⟩) = _
  rw [hc, rewind_correct]

structure Instruction where
  next : Mode
  source : Action := {}
  parking : Action := {}
  deriving Fintype

def instruction (mode : Mode) (source : Symbol) : Instruction :=
  match mode with
  | .copy => match source with
      | .bit b => ⟨.copy, ⟨some .blank, .right⟩, ⟨some (.bit b), .right⟩⟩
      | .blank => ⟨.rewind, ⟨none, .left⟩, ⟨some .separator, .right⟩⟩
      | .separator => ⟨.done, {}, {}⟩
  | .rewind => match source with
      | .blank => ⟨.rewind, ⟨none, .left⟩, {}⟩
      | .separator => ⟨.done, ⟨none, .right⟩, {}⟩
      | .bit _ => ⟨.done, {}, {}⟩
  | .done => ⟨.done, {}, {}⟩

def machineStep (c : Config) : Config :=
  let command := instruction c.mode c.source.head
  ⟨command.next, perform command.source c.source, perform command.parking c.parking⟩

theorem head_local_refinement (c : Config) : step c = machineStep c := by
  rcases c with ⟨mode, source, parking⟩
  cases mode <;> cases hs : source.head <;>
    simp [step, machineStep, instruction, perform, hs]

theorem state_card : Fintype.card Mode = 3 := by decide

/-- A concrete parked state produced by push meets every pop precondition.
The source is erased, then reused as the output; the parking prefix is restored
and the stream returns in original order. No intervening child is modeled.
Scheduler glue must additionally preserve the parked parent record and stack
head, and return the source and temporary tapes in the stated empty forms. -/
theorem park_pop_round_trip (bits : List Bool) (ancestor : List Symbol) :
    let pushed := run (2*bits.length+2)
      ⟨.copy, Tape.mk₂ [.separator] (bits.map .bit), atEnd (.separator::ancestor)⟩
    pushed.source = atEnd [.separator] ∧
    TapeStack.run (3*bits.length+5)
      ⟨.enterDelimiter, pushed.parking, atEnd [.separator], pushed.source⟩ =
      ⟨.done, atEnd (.separator::ancestor), atEnd [.separator],
        Tape.mk₂ [.separator] (bits.map .bit)⟩ := by
  dsimp only
  rw [push_correct]
  constructor
  · rfl
  · exact TapeStack.pop_correct bits ancestor

#print axioms run_add
#print axioms read_bit
#print axioms reading_empty
#print axioms start_rewind
#print axioms rewind_blank
#print axioms rewind_end
#print axioms append_delimiter
#print axioms copy_correct
#print axioms rewind_correct
#print axioms push_correct
#print axioms head_local_refinement
#print axioms state_card
#print axioms park_pop_round_trip

end TapeStackPush
