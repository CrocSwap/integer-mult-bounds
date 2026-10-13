import IntegerConvolution

/-! A fixed deterministic finite-control multitape machine. Every transition
reads one symbol per tape, writes one symbol per tape and moves every head at
most one cell. A missing transition halts. A program's finite tape/state counts
are fixed before all input and runtime quantifiers. -/
namespace CurrentMain.FixedTapeMachine

inductive Symbol where
  | blank | zero | one
  deriving DecidableEq, Repr

inductive Move where
  | left | stay | right
  deriving DecidableEq, Repr

structure Tape where
  left : List Symbol
  head : Symbol
  right : List Symbol
  deriving DecidableEq, Repr

def Tape.blank : Tape := ⟨[],.blank,[]⟩
def Tape.write (a : Symbol) (t : Tape) : Tape := { t with head := a }

def Tape.move (d : Move) (t : Tape) : Tape :=
  match d with
  | .stay => t
  | .left => match t.left with
    | [] => ⟨[],.blank,t.head::t.right⟩
    | a::xs => ⟨xs,a,t.head::t.right⟩
  | .right => match t.right with
    | [] => ⟨t.head::t.left,.blank,[]⟩
    | a::xs => ⟨t.head::t.left,a,xs⟩

structure Action (tapes states : Nat) where
  state : Fin states
  writes : Fin tapes → Symbol
  moves : Fin tapes → Move

structure Machine where
  tapes : Nat
  states : Nat
  initial : Fin states
  transition : Fin states → (Fin tapes → Symbol) → Option (Action tapes states)

structure Configuration (m : Machine) where
  state : Fin m.states
  tapes : Fin m.tapes → Tape

def step (m : Machine) (c : Configuration m) : Option (Configuration m) :=
  match m.transition c.state (fun i => (c.tapes i).head) with
  | none => none
  | some a => some ⟨a.state, fun i => (c.tapes i).write (a.writes i) |>.move (a.moves i)⟩

/-- Exactly t transition opportunities, with an already halted configuration
left unchanged. The additional halt predicate distinguishes a stopped run. -/
def run (m : Machine) : Nat → Configuration m → Configuration m
  | 0, c => c
  | t+1, c => match step m c with
    | none => c
    | some c' => run m t c'

def Halted (m : Machine) (c : Configuration m) : Prop := step m c = none

def bitSymbol (b : Bool) : Symbol := if b then .one else .zero

def Tape.ofWord (w : List Bool) : Tape :=
  match w with
  | [] => Tape.blank
  | b::bs => ⟨[],bitSymbol b,bs.map bitSymbol⟩

structure Convention (m : Machine) where
  inputA : Fin m.tapes
  inputB : Fin m.tapes
  output : Fin m.tapes
  inputs_distinct : inputA ≠ inputB
  output_ne_a : output ≠ inputA
  output_ne_b : output ≠ inputB

def initial (m : Machine) (v : Convention m) (x y : List Bool) : Configuration m :=
  ⟨m.initial, fun i => if i=v.inputA then Tape.ofWord x
    else if i=v.inputB then Tape.ofWord y else Tape.blank⟩

def wordValue (x : List Bool) : Nat :=
  IntegerConvolution.binaryValue (x.map (fun b => if b then 1 else 0))

/-- Exact execution with canonical output and halted finite machine control.
Input/work tapes need not be clean at halt; output head is at its first digit. -/
def Executes (m : Machine) (v : Convention m) (x y z : List Bool) (t : Nat) : Prop :=
  Halted m (run m t (initial m v x y)) ∧
    (run m t (initial m v x y)).tapes v.output = Tape.ofWord z

theorem initial_inputA (m : Machine) (v : Convention m) (x y : List Bool) :
    (initial m v x y).tapes v.inputA = Tape.ofWord x := by simp [initial]

theorem initial_inputB (m : Machine) (v : Convention m) (x y : List Bool) :
    (initial m v x y).tapes v.inputB = Tape.ofWord y := by
  simp [initial,Ne.symm v.inputs_distinct]

theorem initial_output (m : Machine) (v : Convention m) (x y : List Bool) :
    (initial m v x y).tapes v.output = Tape.blank := by
  simp [initial,v.output_ne_a,v.output_ne_b]

theorem run_halted (m : Machine) (c : Configuration m) (h : Halted m c) (t : Nat) :
    run m t c = c := by
  cases t with
  | zero => rfl
  | succ t => simp [run,Halted] at *; rw [h]

theorem run_add (m : Machine) (s t : Nat) (c : Configuration m) :
    run m (s+t) c = run m t (run m s c) := by
  induction s generalizing c with
  | zero => simp only [Nat.zero_add,run]
  | succ s ih =>
    rw [Nat.succ_add]
    cases h : step m c with
    | none => simp only [run,h]; exact (run_halted m c h t).symm
    | some c' => simp only [run,h]; exact ih c'

end CurrentMain.FixedTapeMachine
#print axioms CurrentMain.FixedTapeMachine.initial_inputA
#print axioms CurrentMain.FixedTapeMachine.initial_inputB
#print axioms CurrentMain.FixedTapeMachine.initial_output
#print axioms CurrentMain.FixedTapeMachine.run_halted
#print axioms CurrentMain.FixedTapeMachine.run_add
