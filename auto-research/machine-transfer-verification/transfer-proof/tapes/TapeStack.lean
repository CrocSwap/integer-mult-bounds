import Mathlib.Computability.Tape
import Mathlib.Tactic

/-!
A literal finite-control, three-tape parking-pop transducer.
Every transition reads only the current head symbols and performs at most one
write and one unit move per tape. No transition inspects a list, address,
length, ancestor, or recursion depth. Lists below specify tapes for the proof.
-/

namespace TapeStack
open Turing

inductive Symbol where
  | blank | separator | bit (value : Bool)
  deriving DecidableEq, Repr, Fintype
instance : Inhabited Symbol := ⟨.blank⟩
@[simp] theorem default_symbol : (default : Symbol) = .blank := rfl

inductive Mode where
  | enterDelimiter | enterPayload | copyPark | copyOutput | rewindOutput | done
  deriving DecidableEq, Repr, Fintype

theorem alphabet_card : Fintype.card Symbol = 4 := by decide
theorem state_card : Fintype.card Mode = 6 := by decide

structure Config where
  mode : Mode
  parking : Tape Symbol
  temporary : Tape Symbol
  output : Tape Symbol

def blankHalf : ListBlank Symbol := ListBlank.mk []

theorem blank_cons : blankHalf.cons Symbol.blank = blankHalf := by
  rw [blankHalf, ListBlank.cons_mk]
  apply Quotient.sound
  exact Or.inr ⟨1, rfl⟩

@[simp] theorem blank_mk : ListBlank.mk [Symbol.blank] = ListBlank.mk ([] : List Symbol) := by
  exact blank_cons

def atEnd (left : List Symbol) : Tape Symbol :=
  ⟨.blank, ListBlank.mk left, blankHalf⟩

/-- Nearest-first unread bits, followed by a separator and arbitrary ancestors. -/
def popReady (bits : List Bool) (ancestor : List Symbol) : Tape Symbol :=
  match bits with
  | [] => ⟨.separator, ListBlank.mk ancestor, blankHalf⟩
  | b :: rest => ⟨.bit b, ListBlank.mk (rest.map .bit ++ .separator :: ancestor), blankHalf⟩

def rewindReady (bits : List Bool) (right : List Symbol) : Tape Symbol :=
  match bits with
  | [] => ⟨.separator, ListBlank.mk [], ListBlank.mk right⟩
  | b :: rest => ⟨.bit b, ListBlank.mk (rest.map .bit ++ [.separator]), ListBlank.mk right⟩

/-- A deterministic transition table on six states and four symbols. -/
def step (c : Config) : Config :=
  match c.mode with
  | .enterDelimiter => {c with mode := .enterPayload, parking := c.parking.move .left}
  | .enterPayload =>
      {c with mode := .copyPark, parking := (c.parking.write .blank).move .left}
  | .copyPark => match c.parking.head with
      | .bit b => {c with parking := (c.parking.write .blank).move .left, temporary := (c.temporary.write (.bit b)).move .right}
      | .separator => {c with mode := .copyOutput, parking := c.parking.move .right, temporary := c.temporary.move .left}
      | .blank => {c with mode := .done}
  | .copyOutput => match c.temporary.head with
      | .bit b => {c with temporary := (c.temporary.write .blank).move .left, output := (c.output.write (.bit b)).move .right}
      | .separator => {c with mode := .rewindOutput, temporary := c.temporary.move .right, output := c.output.move .left}
      | .blank => {c with mode := .done}
  | .rewindOutput => match c.output.head with
      | .bit _ => {c with output := c.output.move .left}
      | .separator => {c with mode := .done, output := c.output.move .right}
      | .blank => {c with mode := .done}
  | .done => c

inductive Movement where
  | stay | left | right
  deriving DecidableEq, Fintype

structure Action where
  write : Option Symbol := none
  move : Movement := .stay
  deriving Fintype

def perform (action : Action) (tape : Tape Symbol) : Tape Symbol :=
  let written := match action.write with
    | none => tape
    | some symbol => tape.write symbol
  match action.move with
  | .stay => written
  | .left => written.move .left
  | .right => written.move .right

structure Instruction where
  next : Mode
  parking : Action := {}
  temporary : Action := {}
  output : Action := {}
  deriving Fintype

/-- This finite table receives no tapes, lists, sizes or positions. -/
def instruction (mode : Mode) (park temp out : Symbol) : Instruction :=
  match mode with
  | .enterDelimiter => ⟨.enterPayload, ⟨none, .left⟩, {}, {}⟩
  | .enterPayload => ⟨.copyPark, ⟨some .blank, .left⟩, {}, {}⟩
  | .copyPark => match park with
      | .bit b => ⟨.copyPark, ⟨some .blank, .left⟩, ⟨some (.bit b), .right⟩, {}⟩
      | .separator => ⟨.copyOutput, ⟨none, .right⟩, ⟨none, .left⟩, {}⟩
      | .blank => ⟨.done, {}, {}, {}⟩
  | .copyOutput => match temp with
      | .bit b => ⟨.copyOutput, {}, ⟨some .blank, .left⟩, ⟨some (.bit b), .right⟩⟩
      | .separator => ⟨.rewindOutput, {}, ⟨none, .right⟩, ⟨none, .left⟩⟩
      | .blank => ⟨.done, {}, {}, {}⟩
  | .rewindOutput => match out with
      | .bit _ => ⟨.rewindOutput, {}, {}, ⟨none, .left⟩⟩
      | .separator => ⟨.done, {}, {}, ⟨none, .right⟩⟩
      | .blank => ⟨.done, {}, {}, {}⟩
  | .done => ⟨.done, {}, {}, {}⟩

def machineStep (c : Config) : Config :=
  let command := instruction c.mode c.parking.head c.temporary.head c.output.head
  ⟨command.next, perform command.parking c.parking,
    perform command.temporary c.temporary, perform command.output c.output⟩

/-- The implementation is exactly a finite-state head-symbol transition
table with at most one write and one unit move per physical tape. -/
theorem head_local_refinement (c : Config) : step c = machineStep c := by
  rcases c with ⟨mode, park, temp, out⟩
  cases mode <;> cases hp : park.head <;> cases ht : temp.head <;> cases ho : out.head <;>
    simp [step, machineStep, instruction, perform, hp, ht, ho]

def run : ℕ → Config → Config
  | 0, c => c
  | n+1, c => run n (step c)

theorem run_add (n k : ℕ) (c : Config) : run (n+k) c = run k (run n c) := by
  induction n generalizing c with
  | zero => simp [run]
  | succ n ih => simpa only [Nat.succ_add, run] using ih (step c)

theorem erase_pop (b : Bool) (rest : List Bool) (ancestor : List Symbol) :
    ((popReady (b::rest) ancestor).write .blank).move .left = popReady rest ancestor := by
  cases rest <;>
    simp [popReady, Tape.write, Tape.move, Tape.right₀, blank_cons,
      ListBlank.head_mk, ListBlank.tail_mk, blankHalf]

theorem append_bit (b : Bool) (left : List Symbol) :
    ((atEnd left).write (.bit b)).move .right = atEnd (.bit b :: left) := by
  simp [atEnd, Tape.write, Tape.move, Tape.left₀, blankHalf,
    ListBlank.head_mk, ListBlank.tail_mk, ListBlank.cons_mk]

theorem separator_return (ancestor : List Symbol) :
    (popReady [] ancestor).move .right = atEnd (.separator :: ancestor) := by
  simp [popReady, Tape.move, Tape.left₀, atEnd, blankHalf,
    ListBlank.head_mk, ListBlank.tail_mk, ListBlank.cons_mk]

theorem enter_bits (bits : List Bool) (ancestor : List Symbol) :
    (atEnd (bits.map .bit ++ .separator :: ancestor)).move .left = popReady bits ancestor := by
  cases bits <;>
    simp [atEnd, Tape.move, Tape.right₀, popReady, blank_cons,
      ListBlank.head_mk, ListBlank.tail_mk, blankHalf]

theorem pop_to_rewind (bits : List Bool) : popReady bits [] = rewindReady bits [] := by
  cases bits <;> rfl

theorem rewind_bit (b : Bool) (rest : List Bool) (right : List Symbol) :
    (rewindReady (b::rest) right).move .left = rewindReady rest (.bit b :: right) := by
  cases rest <;>
    simp [rewindReady, Tape.move, Tape.right₀, ListBlank.head_mk,
      ListBlank.tail_mk, ListBlank.cons_mk]

theorem rewind_separator (right : List Symbol) :
    (rewindReady [] right).move .right = Tape.mk₂ [.separator] right := by
  simp [rewindReady, Tape.move, Tape.left₀, Tape.mk₂, Tape.mk',
    ListBlank.cons_mk]

theorem copy_park (bits acc : List Bool) (ancestor : List Symbol) (out : Tape Symbol) :
    run (bits.length + 1)
      ⟨.copyPark, popReady bits ancestor, atEnd (acc.map .bit ++ [.separator]), out⟩ =
      ⟨.copyOutput, atEnd (.separator :: ancestor), popReady (bits.reverse ++ acc) [], out⟩ := by
  induction bits generalizing acc with
  | nil =>
    change Config.mk .copyOutput ((popReady [] ancestor).move .right)
      ((atEnd (acc.map .bit ++ [.separator])).move .left) out =
      Config.mk .copyOutput (atEnd (.separator :: ancestor)) (popReady acc []) out
    rw [separator_return, enter_bits]
  | cons b rest ih =>
    rw [List.length_cons, Nat.succ_add, run]
    change run (rest.length + 1)
      ⟨.copyPark, ((popReady (b::rest) ancestor).write .blank).move .left,
        ((atEnd (acc.map .bit ++ [.separator])).write (.bit b)).move .right, out⟩ = _
    rw [erase_pop, append_bit]
    simpa [List.map_cons, List.reverse_cons, List.append_assoc] using ih (b::acc)

theorem copy_output (bits acc : List Bool) (park : Tape Symbol) :
    run (bits.length + 1)
      ⟨.copyOutput, park, popReady bits [], atEnd (acc.map .bit ++ [.separator])⟩ =
      ⟨.rewindOutput, park, atEnd [.separator], rewindReady (bits.reverse ++ acc) []⟩ := by
  induction bits generalizing acc with
  | nil =>
    change Config.mk .rewindOutput park ((popReady [] []).move .right)
      ((atEnd (acc.map .bit ++ [.separator])).move .left) =
      Config.mk .rewindOutput park (atEnd [.separator]) (rewindReady acc [])
    rw [separator_return, enter_bits, pop_to_rewind]
  | cons b rest ih =>
    rw [List.length_cons, Nat.succ_add, run]
    change run (rest.length + 1)
      ⟨.copyOutput, park, ((popReady (b::rest) []).write .blank).move .left,
        ((atEnd (acc.map .bit ++ [.separator])).write (.bit b)).move .right⟩ = _
    rw [erase_pop, append_bit]
    simpa [List.map_cons, List.reverse_cons, List.append_assoc] using ih (b::acc)

theorem rewind_output (bits : List Bool) (right : List Symbol) (park temp : Tape Symbol) :
    run (bits.length + 1) ⟨.rewindOutput, park, temp, rewindReady bits right⟩ =
      ⟨.done, park, temp, Tape.mk₂ [.separator] (bits.reverse.map .bit ++ right)⟩ := by
  induction bits generalizing right with
  | nil =>
    change Config.mk .done park temp ((rewindReady [] right).move .right) =
      Config.mk .done park temp (Tape.mk₂ [.separator] right)
    rw [rewind_separator]
  | cons b rest ih =>
    rw [List.length_cons, Nat.succ_add, run]
    change run (rest.length + 1)
      ⟨.rewindOutput, park, temp, (rewindReady (b::rest) right).move .left⟩ = _
    rw [rewind_bit]
    simpa [List.reverse_cons, List.map_append, List.append_assoc] using ih (.bit b :: right)

def initial (bits : List Bool) (ancestor : List Symbol) : Config :=
  ⟨.enterDelimiter, atEnd (.separator :: bits.reverse.map .bit ++ .separator :: ancestor),
    atEnd [.separator], atEnd [.separator]⟩

theorem atEnd_cons_left (symbol : Symbol) (left : List Symbol) :
    (atEnd (symbol::left)).move .left = ⟨symbol, ListBlank.mk left, blankHalf⟩ := by
  simp [atEnd, Tape.move, ListBlank.head_mk, ListBlank.tail_mk, blank_cons, blankHalf]

theorem enter_parked (bits : List Bool) (ancestor : List Symbol) :
    run 2 (initial bits ancestor) =
      ⟨.copyPark, popReady bits.reverse ancestor, atEnd [.separator], atEnd [.separator]⟩ := by
  change Config.mk .copyPark
    ((((atEnd (.separator :: (bits.reverse.map .bit ++ .separator :: ancestor))).move .left).write .blank).move .left)
    (atEnd [.separator]) (atEnd [.separator]) = _
  rw [atEnd_cons_left]
  change Config.mk .copyPark ((atEnd (bits.reverse.map .bit ++ .separator :: ancestor)).move .left)
    (atEnd [.separator]) (atEnd [.separator]) = _
  rw [enter_bits]

/-- A concrete linear-time restoration bound, uniformly in ancestor length.
The temporary is empty at its origin; output is in original left-to-right
order with its head at the first payload cell. The parking stack is restored
to its former top without modifying or traversing its ancestor suffix. -/
theorem pop_correct (bits : List Bool) (ancestor : List Symbol) :
    run (3 * bits.length + 5) (initial bits ancestor) =
      ⟨.done, atEnd (.separator :: ancestor), atEnd [.separator],
        Tape.mk₂ [.separator] (bits.map .bit)⟩ := by
  have hcount : 3 * bits.length + 5 =
      2 + (bits.length + 1) + (bits.length + 1) + (bits.length + 1) := by omega
  rw [hcount, run_add (2 + (bits.length+1) + (bits.length+1)) (bits.length+1),
    run_add (2 + (bits.length+1)) (bits.length+1), run_add 2 (bits.length+1), enter_parked]
  have first := copy_park bits.reverse [] ancestor (atEnd [.separator])
  simp only [List.length_reverse, List.map_nil, List.nil_append,
    List.reverse_reverse, List.append_nil] at first
  rw [first]
  have second := copy_output bits [] (atEnd (.separator :: ancestor))
  simp only [List.map_nil, List.nil_append, List.append_nil] at second
  rw [second]
  have third := rewind_output bits.reverse [] (atEnd (.separator :: ancestor)) (atEnd [.separator])
  simpa only [List.length_reverse, List.reverse_reverse, List.append_nil] using third

/-- Two head-local transitions: move left, then write and move right.
This installs or removes a boundary without changing the origin position. -/
def setBoundary (symbol : Symbol) (tape : Tape Symbol) : Tape Symbol :=
  ((tape.move .left).write symbol).move .right

theorem install_boundary (contents : List Symbol) :
    setBoundary .separator (Tape.mk₁ contents) = Tape.mk₂ [.separator] contents := by
  simp [setBoundary, Tape.mk₁, Tape.mk₂, Tape.mk', Tape.move, Tape.write,
    ListBlank.head_mk, ListBlank.tail_mk, ListBlank.cons_mk]

theorem remove_boundary (contents : List Symbol) :
    setBoundary .blank (Tape.mk₂ [.separator] contents) = Tape.mk₁ contents := by
  simp [setBoundary, Tape.mk₁, Tape.mk₂, Tape.mk', Tape.move, Tape.write,
    ListBlank.head_mk, ListBlank.tail_mk, ListBlank.cons_mk]

theorem remove_empty_boundary : setBoundary .blank (atEnd [.separator]) = Tape.mk₁ [] := by
  exact remove_boundary []

#print axioms default_symbol
#print axioms blank_cons
#print axioms blank_mk
#print axioms alphabet_card
#print axioms state_card
#print axioms head_local_refinement
#print axioms run_add
#print axioms erase_pop
#print axioms append_bit
#print axioms separator_return
#print axioms enter_bits
#print axioms pop_to_rewind
#print axioms rewind_bit
#print axioms rewind_separator
#print axioms copy_park
#print axioms copy_output
#print axioms rewind_output
#print axioms atEnd_cons_left
#print axioms enter_parked
#print axioms pop_correct
#print axioms install_boundary
#print axioms remove_boundary
#print axioms remove_empty_boundary

end TapeStack
