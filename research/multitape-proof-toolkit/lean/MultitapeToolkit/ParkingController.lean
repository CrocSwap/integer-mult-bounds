import MultitapeToolkit.MarkedStreams
import MultitapeToolkit.ParkStack
import MultitapeToolkit.ControlEmbedding
import MultitapeToolkit.SubroutineContracts
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum

/-!
# One concrete charged park/call/restore boundary

Five physical tapes and a fixed finite tagged phase bank implement an actual
inactive push, active move, child call, active return, and inactive pop. An
initial halted component charges the first dispatch through the real scheduler.
The primitive tables follow the credited PR64/PR1379 lineage. Child contracts
are actual executions on literal entry and return banks. The closed bit-flip
instance has no child premise and restores the entire arbitrary parking prefix.
-/
namespace MultitapeToolkit.Absolute.ParkingController

open scoped BigOperators
open MarkedStreams ParkStack ControlEmbedding Subroutines

abbrev Tapes := Fin 5
abbrev State (Q : Type*) := MovePhase ⊕ (PushPhase ⊕ (Q ⊕ PopPhase))
abbrev Control (Q : Type*) := Fin 6 × State Q

variable {Q : Type*} [Fintype Q]

def encodeMove (q : MovePhase) : State Q := .inl q
def encodePush (q : PushPhase) : State Q := .inr (.inl q)
def encodeChild (q : Q) : State Q := .inr (.inr (.inl q))
def encodePop (q : PopPhase) : State Q := .inr (.inr (.inr q))

def decodeMove : State Q → Option MovePhase
  | .inl q => some q
  | _ => none

def decodePush : State Q → Option PushPhase
  | .inr (.inl q) => some q
  | _ => none

def decodeChild : State Q → Option Q
  | .inr (.inr (.inl q)) => some q
  | _ => none

def decodePop : State Q → Option PopPhase
  | .inr (.inr (.inr q)) => some q
  | _ => none

omit [Fintype Q] in
@[simp] theorem decodeMove_encode (q : MovePhase) : decodeMove (encodeMove (Q:=Q) q) = some q := rfl
omit [Fintype Q] in
@[simp] theorem decodePush_encode (q : PushPhase) : decodePush (encodePush (Q:=Q) q) = some q := rfl
omit [Fintype Q] in
@[simp] theorem decodeChild_encode (q : Q) : decodeChild (encodeChild q) = some q := rfl
omit [Fintype Q] in
@[simp] theorem decodePop_encode (q : PopPhase) : decodePop (encodePop (Q:=Q) q) = some q := rfl

/-- Component zero is halted; the physical scheduler performs its entry handoff. -/
def initialStage : Program Tapes Symbol (State Q) where
  transition _ _ := none

def stages (child : Program Tapes Symbol Q) : Fin 6 → Program Tapes Symbol (State Q)
  | i => match i.val with
    | 0 => initialStage
    | 1 => liftProgram (pushProgram (1:Tapes) 3) encodePush decodePush
    | 2 => liftProgram (moveProgram (0:Tapes) 2) encodeMove decodeMove
    | 3 => liftProgram child encodeChild decodeChild
    | 4 => liftProgram (moveProgram (2:Tapes) 0) encodeMove decodeMove
    | _ => liftProgram (popProgram (1:Tapes) 4 3) encodePop decodePop

def entry (childEntry : Q) : Fin 6 → State Q
  | i => match i.val with
    | 1 => encodePush .copy
    | 3 => encodeChild childEntry
    | 5 => encodePop .enterDelimiter
    | _ => encodeMove .copy

/-- The fixed table, before any stream length or parked contents are chosen. -/
def wrapper (child : Program Tapes Symbol Q) (childEntry : Q) :
    Program Tapes Symbol (Control Q) := scheduler (stages child) (entry childEntry)

def homeHeads (h : ℤ) : Tapes → ℤ := fun i => if i = 3 then h else 0

def parkedHeads (y : List Bool) (h : ℤ) : Tapes → ℤ :=
  homeHeads (h + y.length + 1)

def initialCells (x y : List Bool) (h : ℤ) (past : ℤ → Symbol) : Tapes → ℤ → Symbol :=
  fun i => if i = 0 then word x else if i = 1 then word y
    else if i = 3 then parkBase h past else word []

def parkedCells (x y : List Bool) (h : ℤ) (past : ℤ → Symbol) : Tapes → ℤ → Symbol :=
  fun i => if i = 0 then word x else if i = 3 then parkRecord y h past else word []

def callCells (x y : List Bool) (h : ℤ) (past : ℤ → Symbol) : Tapes → ℤ → Symbol :=
  fun i => if i = 2 then word x else if i = 3 then parkRecord y h past else word []

/-- Exact physical child entry: all role/temp streams empty, active x on IO. -/
def childInput (childEntry : Q) (x y : List Bool) (h : ℤ) (past : ℤ → Symbol) :
    Config Tapes Symbol Q := ⟨childEntry, parkedHeads y h, callCells x y h past⟩

/-- Exact child return contract, including parking, heads and reused workspace. -/
def childOutput (childExit : Q) (z y : List Bool) (h : ℤ) (past : ℤ → Symbol) :
    Config Tapes Symbol Q := ⟨childExit, parkedHeads y h, callCells z y h past⟩

def wrapperInput (childEntry : Q) (x y : List Bool) (h : ℤ) (past : ℤ → Symbol) :
    Config Tapes Symbol (Control Q) :=
  stageCfg 0 ⟨entry childEntry 0, homeHeads h, initialCells x y h past⟩

def wrapperOutput (z y : List Bool) (h : ℤ) (past : ℤ → Symbol) :
    Config Tapes Symbol (Control Q) :=
  stageCfg (Fin.last 5) ⟨encodePop .done, homeHeads h, initialCells z y h past⟩

/-- Concrete length-preserving child: flip every real bit and restore the IO head. -/
def bitFlipChild : Program Tapes Symbol FlipPhase := flipProgram (2:Tapes)

def boundaryMachine : Program Tapes Symbol (Control FlipPhase) :=
  wrapper bitFlipChild .copy

def boundaryInput (x y : List Bool) (h : ℤ) (past : ℤ → Symbol) :
    Config Tapes Symbol (Control FlipPhase) := wrapperInput .copy x y h past

def boundaryOutput (x y : List Bool) (h : ℤ) (past : ℤ → Symbol) :
    Config Tapes Symbol (Control FlipPhase) := wrapperOutput (x.map Bool.not) y h past

end MultitapeToolkit.Absolute.ParkingController
namespace MultitapeToolkit.Absolute.ParkingController
open scoped BigOperators
open MarkedStreams ParkStack ControlEmbedding Subroutines
variable {Q : Type*} [Fintype Q]

def begins (childEntry : Q) (x y z : List Bool) (h : ℤ) (past : ℤ → Symbol) :
    Fin 6 → Config Tapes Symbol (State Q)
  | i => match i.val with
    | 0 => ⟨entry childEntry 0, homeHeads h, initialCells x y h past⟩
    | 1 => taggedCfg encodePush (pushInput (1:Tapes) 3 y h past (homeHeads h) (initialCells x y h past))
    | 2 => taggedCfg encodeMove (moveInput (0:Tapes) 2 x clean clean (parkedHeads y h) (parkedCells x y h past))
    | 3 => taggedCfg encodeChild (childInput childEntry x y h past)
    | 4 => taggedCfg encodeMove (moveInput (2:Tapes) 0 z clean clean (parkedHeads y h) (callCells z y h past))
    | _ => taggedCfg encodePop (popInput (1:Tapes) 4 3 y h past (parkedHeads y h) (parkedCells z y h past))

def finishes (childEntry childExit : Q) (x y z : List Bool) (h : ℤ) (past : ℤ → Symbol) :
    Fin 6 → Config Tapes Symbol (State Q)
  | i => match i.val with
    | 0 => ⟨entry childEntry 0, homeHeads h, initialCells x y h past⟩
    | 1 => taggedCfg encodePush (pushFinal (1:Tapes) 3 y h past (homeHeads h) (initialCells x y h past))
    | 2 => taggedCfg encodeMove (moveOutput (0:Tapes) 2 x clean clean (parkedHeads y h) (parkedCells x y h past))
    | 3 => taggedCfg encodeChild (childOutput childExit z y h past)
    | 4 => taggedCfg encodeMove (moveOutput (2:Tapes) 0 z clean clean (parkedHeads y h) (callCells z y h past))
    | _ => taggedCfg encodePop (popFinal (1:Tapes) 4 3 y h past (parkedHeads y h) (parkedCells z y h past))

def stageTimes (x y z : List Bool) (childTime : ℕ) : Fin 6 → ℕ
  | i => match i.val with
    | 0 => 0
    | 1 => 2*y.length+2
    | 2 => 2*x.length+2
    | 3 => childTime
    | 4 => 2*z.length+2
    | _ => 3*y.length+5

omit [Fintype Q] in
theorem begins_entry (childEntry : Q) (x y z : List Bool) (h : ℤ) (past : ℤ → Symbol) :
    ∀ i, (begins childEntry x y z h past i).state = entry childEntry i := by
  intro i
  fin_cases i <;> rfl

/-- Every component run is an actual execution of its explicitly tagged table. -/
theorem stages_run (child : Program Tapes Symbol Q) (childEntry childExit : Q)
    (x y z : List Bool) (h : ℤ) (past : ℤ → Symbol) (t : ℕ)
    (hc : Runs child t (childInput childEntry x y h past) (childOutput childExit z y h past)) :
    ∀ i, Runs (stages child i) (stageTimes x y z t i)
      (begins childEntry x y z h past i) (finishes childEntry childExit x y z h past i) := by
  intro i
  fin_cases i
  · exact .refl _
  · exact lift_runs (pushProgram (1:Tapes) 3) encodePush decodePush (fun _ => rfl)
      (push_correct (1:Tapes) 3 (by decide) y h past (homeHeads h) (initialCells x y h past))
  · exact lift_runs (moveProgram (0:Tapes) 2) encodeMove decodeMove (fun _ => rfl)
      (move_runs (0:Tapes) 2 (by decide) x clean clean (parkedHeads y h) (parkedCells x y h past))
  · exact lift_runs child encodeChild decodeChild (fun _ => rfl) hc
  · exact lift_runs (moveProgram (2:Tapes) 0) encodeMove decodeMove (fun _ => rfl)
      (move_runs (2:Tapes) 0 (by decide) z clean clean (parkedHeads y h) (callCells z y h past))
  · exact lift_runs (popProgram (1:Tapes) 4 3) encodePop decodePop (fun _ => rfl)
      (pop_correct (1:Tapes) 4 3 (by decide) (by decide) (by decide) y h past
        (parkedHeads y h) (parkedCells z y h past))

theorem stages_halt (child : Program Tapes Symbol Q) (childEntry childExit : Q)
    (x y z : List Bool) (h : ℤ) (past : ℤ → Symbol)
    (hc : Halts child (childOutput childExit z y h past)) :
    ∀ i, Halts (stages child i) (finishes childEntry childExit x y z h past i) := by
  intro i
  fin_cases i
  · rfl
  · exact (lift_halts (pushProgram (1:Tapes) 3) encodePush decodePush (fun _ => rfl) _).2
      (pushFinal_halts (1:Tapes) 3 y h past (homeHeads h) (initialCells x y h past))
  · exact (lift_halts (moveProgram (0:Tapes) 2) encodeMove decodeMove (fun _ => rfl) _).2
      (move_halts (0:Tapes) 2 x clean clean (parkedHeads y h) (parkedCells x y h past))
  · exact (lift_halts child encodeChild decodeChild (fun _ => rfl) _).2 hc
  · exact (lift_halts (moveProgram (2:Tapes) 0) encodeMove decodeMove (fun _ => rfl) _).2
      (move_halts (2:Tapes) 0 z clean clean (parkedHeads y h) (callCells z y h past))
  · exact (lift_halts (popProgram (1:Tapes) 4 3) encodePop decodePop (fun _ => rfl) _).2
      (popFinal_halts (1:Tapes) 4 3 y h past (parkedHeads y h) (parkedCells z y h past))

omit [Fintype Q] in
/-- All handoffs have exact head and entire-cell agreement; no bank reset occurs. -/
theorem literal_boundaries (childEntry childExit : Q) (x y z : List Bool)
    (h : ℤ) (past : ℤ → Symbol) :
    Boundaries (begins childEntry x y z h past) (finishes childEntry childExit x y z h past) := by
  intro i hi
  fin_cases i <;> try (norm_num at hi)
  all_goals constructor
  all_goals funext j
  all_goals fin_cases j <;>
    simp [begins, finishes, nextStage, taggedCfg, pushInput, pushFinal, popInput, popFinal,
      moveInput, moveOutput, childInput, childOutput, bank2, bank3,
      reading, atEnd, streamTape, homeHeads, parkedHeads,
      initialCells, parkedCells, callCells, TapeData.cell, word, markedStream,
      parkBase, parkRecord, ParkStack.clean] <;> rfl

omit [Fintype Q] in
theorem final_bank (childEntry childExit : Q) (x y z : List Bool) (h : ℤ) (past : ℤ → Symbol) :
    stageCfg (Fin.last 5) (finishes childEntry childExit x y z h past (Fin.last 5)) =
      wrapperOutput z y h past := by
  apply Config.ext
  · rfl
  · funext i; fin_cases i <;>
      simp [stageCfg,finishes,wrapperOutput,taggedCfg,popFinal,bank3,bank2,
        atEnd,reading,homeHeads,parkedHeads]
  · funext i; fin_cases i <;>
      simp [stageCfg,finishes,wrapperOutput,taggedCfg,popFinal,bank3,bank2,
        atEnd,TapeData.cell,homeHeads,parkedHeads,initialCells,parkedCells,
        word,markedStream,reading,parkBase,ParkStack.clean] <;> rfl

/-- Actual finite caller, exact cost, full output and true halt for every
supplied actual child execution on the literal bank, even if its size changes. -/
theorem wrapper_correct (child : Program Tapes Symbol Q) (childEntry childExit : Q)
    (x y z : List Bool) (h : ℤ) (past : ℤ → Symbol) (t : ℕ)
    (hr : Runs child t (childInput childEntry x y h past) (childOutput childExit z y h past))
    (hh : Halts child (childOutput childExit z y h past)) :
    Runs (wrapper child childEntry) (2*x.length+2*z.length+5*y.length+16+t)
      (wrapperInput childEntry x y h past) (wrapperOutput z y h past) ∧
    Halts (wrapper child childEntry) (wrapperOutput z y h past) := by
  have H := scheduler_assembly (stages child) (entry childEntry)
    (begins childEntry x y z h past) (finishes childEntry childExit x y z h past)
    (stageTimes x y z t) (begins_entry childEntry x y z h past)
    (stages_run child childEntry childExit x y z h past t hr)
    (stages_halt child childEntry childExit x y z h past hh)
    (literal_boundaries childEntry childExit x y z h past)
  have hsum : (∑ i, stageTimes x y z t i) + 5 = 2*x.length+2*z.length+5*y.length+16+t := by
    simp only [Fin.sum_univ_succ,Fin.sum_univ_zero]
    simp [stageTimes]
    omega
  rw [hsum, final_bank] at H
  exact H

end MultitapeToolkit.Absolute.ParkingController
namespace MultitapeToolkit.Absolute.ParkingController
open MarkedStreams ParkStack

 theorem flip_entry_bank (x y : List Bool) (h : ℤ) (past : ℤ → Symbol) :
    flipInput (2:Tapes) x ParkStack.clean (parkedHeads y h) (callCells x y h past) =
      childInput MovePhase.copy x y h past := by
  apply Config.ext
  · rfl
  · funext i; fin_cases i <;> simp [flipInput,bank1,childInput,streamTape,parkedHeads,homeHeads]
  · funext i; fin_cases i <;> simp [flipInput,bank1,childInput,streamTape,TapeData.cell,
      callCells,word,markedStream,ParkStack.clean] <;> rfl

 theorem flip_return_bank (x y : List Bool) (h : ℤ) (past : ℤ → Symbol) :
    flipOutput (2:Tapes) x ParkStack.clean (parkedHeads y h) (callCells x y h past) =
      childOutput MovePhase.done (x.map Bool.not) y h past := by
  apply Config.ext
  · rfl
  · funext i; fin_cases i <;> simp [flipOutput,bank1,childOutput,streamTape,parkedHeads,homeHeads]
  · funext i; fin_cases i <;> simp [flipOutput,bank1,childOutput,streamTape,TapeData.cell,
      callCells,word,markedStream,ParkStack.clean] <;> rfl

/-- One fixed five-tape, four-symbol finite controller executes every bit-flip
boundary in exactly the displayed number of physical transitions. No child
premise appears: push/copy/flip/return/pop, every handoff and the empty cases are
proved. The complete inactive stream, arbitrary ancestor contents and heads are
restored literally. This is a reusable caller basis, not a multiplication bound. -/
theorem boundary_machine_correct (x y : List Bool) (h : ℤ) (past : ℤ → Symbol) :
    Runs boundaryMachine (6*x.length+5*y.length+18)
      (boundaryInput x y h past) (boundaryOutput x y h past) ∧
    Halts boundaryMachine (boundaryOutput x y h past) := by
  have hr := flip_runs (2:Tapes) x ParkStack.clean (parkedHeads y h) (callCells x y h past)
  have hh := flip_halts (2:Tapes) x ParkStack.clean (parkedHeads y h) (callCells x y h past)
  rw [flip_entry_bank,flip_return_bank] at hr
  rw [flip_return_bank] at hh
  have result := wrapper_correct bitFlipChild MovePhase.copy MovePhase.done x y
    (x.map Bool.not) h past (2*x.length+2) hr hh
  have hcost : 2*x.length+2*(x.map Bool.not).length+5*y.length+16+(2*x.length+2) =
      6*x.length+5*y.length+18 := by simp only [List.length_map]; omega
  rw [hcost] at result
  exact result

 theorem boundary_states : Fintype.card (Control FlipPhase) = 90 := by decide
 theorem boundary_tapes : Fintype.card Tapes = 5 := by decide

end MultitapeToolkit.Absolute.ParkingController