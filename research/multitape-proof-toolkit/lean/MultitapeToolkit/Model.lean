import Mathlib.Computability.TuringMachine.Tape
import Mathlib.Data.Fintype.Basic

/-!
# Deterministic finite-control multitape machines

Each transition reads the current symbol on every tape, changes finite control,
and performs at most one write and one unit head movement on each tape.
`Runs` counts precisely these simultaneous transitions, without padding after halt.
Tape symbols, tape indices and control states are explicitly finite.

The stack representation is a tape with its head at the blank immediately to the
left of a finite list of nonblank symbols.  Its elementary operations have exact
local tape identities, suitable for a constant-overhead stack-machine compiler.
-/

namespace MultitapeToolkit

open Turing

/-- A single unit of head motion, including staying in place. -/
inductive Move where
  | stay
  | left
  | right
  deriving DecidableEq, Inhabited

/-- Optional write followed by a unit move. `none` means leave the symbol alone. -/
structure Action (Γ : Type*) where
  write : Option Γ
  move : Move

/-- Interpret head motion on Mathlib's finitely supported, two-sided tape. -/
def moveTape {Γ : Type*} [Inhabited Γ] (m : Move) (t : Tape Γ) : Tape Γ :=
  match m with
  | .stay => t
  | .left => t.move .left
  | .right => t.move .right

/-- One local tape action; a read is always performed before this action. -/
def act {Γ : Type*} [Inhabited Γ] (a : Action Γ) (t : Tape Γ) : Tape Γ :=
  moveTape a.move (match a.write with | none => t | some b => t.write b)

/-- A finite collection of tapes and a control state. Tape contents are unbounded. -/
structure Config (ι Γ Q : Type*) [Inhabited Γ] where
  state : Q
  tapes : ι → Tape Γ

/-- A deterministic transition table on finite control and finite tape alphabets.
`none` is a halting transition. No unbounded register lives in finite control. -/
structure Machine (ι Γ Q : Type*) [Inhabited Γ]
    [Fintype ι] [Fintype Γ] [Fintype Q] where
  transition : Q → (ι → Γ) → Option (Q × (ι → Action Γ))

section Execution

variable {ι Γ Q : Type*} [Inhabited Γ]
  [Fintype ι] [Fintype Γ] [Fintype Q]

/-- One simultaneous multitape transition. -/
def step (M : Machine ι Γ Q) (c : Config ι Γ Q) : Option (Config ι Γ Q) :=
  (M.transition c.state (fun i => (c.tapes i).head)).map fun p =>
    ⟨p.1, fun i => act (p.2 i) (c.tapes i)⟩

/-- Exact execution length; halting is not silently counted as additional work. -/
inductive Runs (M : Machine ι Γ Q) : ℕ → Config ι Γ Q → Config ι Γ Q → Prop
  | refl (c) : Runs M 0 c c
  | cons {n c d e} : step M c = some d → Runs M n d e → Runs M (n + 1) c e

/-- A successful transition is an execution of length one. -/
theorem Runs.one {M : Machine ι Γ Q} {c d : Config ι Γ Q}
    (h : step M c = some d) : Runs M 1 c d :=
  .cons h (.refl d)

/-- Sequential execution adds transition counts exactly. -/
theorem Runs.trans {M : Machine ι Γ Q} {n m : ℕ} {c d e : Config ι Γ Q}
    (h : Runs M n c d) (h' : Runs M m d e) : Runs M (n + m) c e := by
  induction h with
  | refl => simpa using h'
  | @cons n c d e hs hr ih =>
    simpa [Nat.add_assoc, Nat.add_comm, Nat.add_left_comm] using Runs.cons hs (ih h')

/-- A completed exact execution can be used with any larger time budget. -/
def RunsWithin (M : Machine ι Γ Q) (budget : ℕ) (c d : Config ι Γ Q) : Prop :=
  ∃ n, n ≤ budget ∧ Runs M n c d

/-- Sequential bounded executions add their budgets. -/
theorem RunsWithin.trans {M : Machine ι Γ Q} {n m : ℕ} {c d e : Config ι Γ Q}
    (h : RunsWithin M n c d) (h' : RunsWithin M m d e) :
    RunsWithin M (n + m) c e := by
  rcases h with ⟨a, ha, h⟩
  rcases h' with ⟨b, hb, h'⟩
  exact ⟨a + b, Nat.add_le_add ha hb, h.trans h'⟩

/-- No further transition is available from a halting configuration. -/
def Halts (M : Machine ι Γ Q) (c : Config ι Γ Q) : Prop := step M c = none

/-- A computation reaches a halting configuration within the stated budget. -/
def ComputesWithin (M : Machine ι Γ Q) (budget : ℕ) (c d : Config ι Γ Q) : Prop :=
  RunsWithin M budget c d ∧ Halts M d

end Execution

section StackRepresentation

variable {Γ : Type*}

/-- Erased half-tape: adding one blank changes no tape contents. -/
@[simp] theorem blank_half :
    ListBlank.mk ([none] : List (Option Γ)) = ListBlank.mk [] := by
  exact Quotient.sound' (Or.inr ⟨1, rfl⟩)

/-- A list represented immediately to the right of the blank tape head. -/
def stackTape (s : List Γ) : Tape (Option Γ) :=
  ⟨none, ListBlank.mk [], ListBlank.mk (s.map some)⟩

@[simp] theorem stackTape_head (s : List Γ) : (stackTape s).head = none := rfl

/-- The symbol read after moving right is the optional top of the stack. -/
@[simp] theorem stackTape_move_right_head (s : List Γ) :
    ((stackTape s).move .right).head = s.head? := by
  cases s <;> rfl

/-- Push takes one write-and-left action. -/
theorem stackTape_push (a : Γ) (s : List Γ) :
    ((stackTape s).write (some a)).move .left = stackTape (a :: s) := by
  simp [stackTape, Tape.write, Tape.move, ListBlank.head_mk, ListBlank.tail_mk,
    ListBlank.cons_mk]
  rfl

/-- On a nonempty stack, moving right and erasing the top represents pop. -/
theorem stackTape_pop_cons (a : Γ) (s : List Γ) :
    ((stackTape (a :: s)).move .right).write none = stackTape s := by
  simp [stackTape, Tape.write, Tape.move, ListBlank.head_mk, ListBlank.tail_mk,
    ListBlank.cons_mk]

/-- An empty stack is restored by returning left after reading its blank. -/
theorem stackTape_pop_nil :
    ((stackTape ([] : List Γ)).move .right).move .left = stackTape [] := by
  exact Tape.move_right_left _

/-- A peek reads right and returns left without changing stack contents. -/
theorem stackTape_peek_restore (s : List Γ) :
    ((stackTape s).move .right).move .left = stackTape s := by
  exact Tape.move_right_left _

/-- The finite-control branching implementation of a pop at the read phase. -/
def finishPop (t : Tape (Option Γ)) : Tape (Option Γ) :=
  match t.head with
  | none => t.move .left
  | some _ => t.write none

/-- Pop is uniformly realized by a right move followed by one local branch. -/
theorem stackTape_pop (s : List Γ) :
    finishPop ((stackTape s).move .right) = stackTape s.tail := by
  cases s with
  | nil => simpa [finishPop] using (stackTape_pop_nil (Γ := Γ))
  | cons a s => simpa [finishPop] using stackTape_pop_cons a s

/-- Read at most `n` stack cells from an output tape, stopping at its first blank.
This observer is not a free preprocessing operation in machine execution. -/
def readStack : ℕ → Tape (Option Γ) → List Γ
  | 0, _ => []
  | n + 1, t =>
    let r := t.move .right
    match r.head with
    | none => []
    | some a => a :: readStack n (r.write none)

/-- The represented output list is recovered from exactly its length in cells. -/
theorem readStack_stackTape (s : List Γ) :
    readStack s.length (stackTape s) = s := by
  induction s with
  | nil => rfl
  | cons a s ih =>
    simpa [readStack, stackTape_move_right_head, stackTape_pop_cons] using
      congrArg (List.cons a) ih

/-- Canonical blank scratch tape. -/
theorem stackTape_nil : stackTape ([] : List Γ) = (default : Tape (Option Γ)) := rfl

end StackRepresentation

end MultitapeToolkit



