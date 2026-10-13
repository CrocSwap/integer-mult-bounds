import FixedTapeMachine

/-! A source-only, direct explicit-list-tape reversal primitive. This module does
not construct the outer multiplication Plan or port a quotient-tape machine.
The delayed output write avoids allocating a cell beyond the final word. -/
namespace CurrentMain.BinaryWordReversal
open FixedTapeMachine

/-- States: seek, load, copy zero, copy one, skip first, rewind. -/
structure Command where
  next : Fin 6
  inputMove : Move
  outputMove : Move
  outputWrite : Option Symbol

def buffered (b : Bool) : Fin 6 := if b then 3 else 2

def copyCommand (b : Bool) : Symbol → Command
  | .blank => ⟨4, .right, .stay, some (bitSymbol b)⟩
  | .zero => ⟨2, .left, .right, some (bitSymbol b)⟩
  | .one => ⟨3, .left, .right, some (bitSymbol b)⟩

def instruction (s : Fin 6) (a : Symbol) : Option Command :=
  match s.val with
  | 0 => some ⟨if a = .blank then 1 else 0,
      if a = .blank then .left else .right, .stay, none⟩
  | 1 => match a with
    | .blank => none
    | .zero => some ⟨2, .left, .stay, none⟩
    | .one => some ⟨3, .left, .stay, none⟩
  | 2 => some (copyCommand false a)
  | 3 => some (copyCommand true a)
  | 4 => some ⟨5, .right, .stay, none⟩
  | _ => if a = .blank then none else some ⟨5, .right, .left, none⟩

def action (read : Fin 3 → Symbol) (c : Command) : Action 3 6 where
  state := c.next
  writes := fun i => if i = 2 then c.outputWrite.getD (read i) else read i
  moves := fun i => if i = 0 then c.inputMove else if i = 2 then c.outputMove else .stay

def machine : Machine where
  tapes := 3
  states := 6
  initial := 0
  transition := fun s read => (instruction s (read 0)).map (action read)

def convention : Convention machine where
  inputA := (0 : Fin 3)
  inputB := (1 : Fin 3)
  output := (2 : Fin 3)
  inputs_distinct := by decide
  output_ne_a := by decide
  output_ne_b := by decide

def configuration (s : Fin 6) (input spare output : Tape) : Configuration machine :=
  ⟨s, fun i => if i = (0 : Fin 3) then input else if i = (1 : Fin 3) then spare else output⟩

/-- `fromRight` and `fromLeft` merely name exact finite-list configurations. -/
def fromRight (left right : List Symbol) : Tape :=
  match right with
  | [] => ⟨left, .blank, []⟩
  | a::rest => ⟨left, a, rest⟩

def fromLeft (left right : List Symbol) : Tape :=
  match left with
  | [] => ⟨[], .blank, right⟩
  | a::rest => ⟨rest, a, right⟩

def endTape (left : List Symbol) : Tape := ⟨left, .blank, []⟩

theorem step_command (s : Fin 6) (input spare output : Tape) (c : Command)
    (h : instruction s input.head = some c) :
    step machine (configuration s input spare output) =
      some (configuration c.next (input.move c.inputMove) spare
        ((output.write (c.outputWrite.getD output.head)).move c.outputMove)) := by
  unfold step
  have transition_eq :
      machine.transition (configuration s input spare output).state
        (fun i => ((configuration s input spare output).tapes i).head) =
      (instruction s input.head).map
        (action (fun i : Fin 3 => ((configuration s input spare output).tapes i).head)) := by
    simp [machine, configuration]
  rw [transition_eq, h]
  simp only [Option.map_some]
  dsimp only [action, configuration]
  apply congrArg some
  apply congrArg (fun tapes : Fin 3 → Tape =>
    (Configuration.mk c.next tapes : Configuration machine))
  funext i
  have cases_i : i = (0 : Fin 3) ∨ i = (1 : Fin 3) ∨ i = (2 : Fin 3) := by
    exact (show ∀ j : Fin 3, j = (0 : Fin 3) ∨ j = (1 : Fin 3) ∨ j = (2 : Fin 3)
      from by decide) i
  rcases cases_i with rfl | rfl | rfl <;>
    simp [configuration, action, Tape.write, Tape.move]

theorem run_step (n : Nat) (c d : Configuration machine)
    (h : step machine c = some d) : run machine (n+1) c = run machine n d := by
  simp only [run, h]

theorem seek_bit (b : Bool) (left : List Symbol) (rest : List Bool) (spare output : Tape) :
    step machine (configuration 0 (fromRight left ((b::rest).map bitSymbol)) spare output) =
      some (configuration 0 (fromRight (bitSymbol b::left) (rest.map bitSymbol)) spare output) := by
  have h := step_command 0 (fromRight left ((b::rest).map bitSymbol)) spare output
    ⟨0, .right, .stay, none⟩ (by cases b <;> rfl)
  cases rest <;> simpa only [fromRight, List.map_cons, List.map_nil, Tape.move,
    Tape.write, Option.getD_none] using h

theorem seek_run (bits : List Bool) (left : List Symbol) (spare output : Tape) :
    run machine bits.length (configuration 0 (fromRight left (bits.map bitSymbol)) spare output) =
      configuration 0 (endTape (bits.reverse.map bitSymbol ++ left)) spare output := by
  induction bits generalizing left with
  | nil => rfl
  | cons b rest ih =>
    rw [List.length_cons, run_step _ _ _ (seek_bit b left rest spare output), ih]
    simp only [List.reverse_cons, List.map_append, List.map_cons, List.map_nil,
      List.append_assoc, List.singleton_append]

theorem seek_end (left : List Symbol) (spare output : Tape) :
    step machine (configuration 0 (endTape left) spare output) =
      some (configuration 1 (fromLeft left [.blank]) spare output) := by
  have h := step_command 0 (endTape left) spare output ⟨1, .left, .stay, none⟩ rfl
  cases left <;> simpa only [endTape, fromLeft, Tape.move, Tape.write,
    Option.getD_none] using h

theorem load_bit (b : Bool) (rest : List Bool) (tail : List Symbol) (spare output : Tape) :
    step machine (configuration 1 (fromLeft ((b::rest).map bitSymbol) tail) spare output) =
      some (configuration (buffered b) (fromLeft (rest.map bitSymbol) (bitSymbol b::tail))
        spare output) := by
  have h := step_command 1 (fromLeft ((b::rest).map bitSymbol) tail) spare output
    ⟨buffered b, .left, .stay, none⟩ (by cases b <;> rfl)
  cases rest <;> simpa only [fromLeft, List.map_cons, List.map_nil, Tape.move,
    Tape.write, Option.getD_none] using h

theorem copy_bit (b c : Bool) (rest : List Bool) (tail left : List Symbol) (spare : Tape) :
    step machine (configuration (buffered b)
      (fromLeft ((c::rest).map bitSymbol) (bitSymbol b::tail)) spare (endTape left)) =
      some (configuration (buffered c)
        (fromLeft (rest.map bitSymbol) (bitSymbol c::bitSymbol b::tail)) spare
        (endTape (bitSymbol b::left))) := by
  have h := step_command (buffered b)
    (fromLeft ((c::rest).map bitSymbol) (bitSymbol b::tail)) spare (endTape left)
    ⟨buffered c, .left, .right, some (bitSymbol b)⟩ (by cases b <;> cases c <;> rfl)
  cases rest <;> simpa only [fromLeft, List.map_cons, List.map_nil, Tape.move,
    Tape.write, Option.getD_some, endTape] using h

theorem copy_last (b : Bool) (tail left : List Symbol) (spare : Tape) :
    step machine (configuration (buffered b) (fromLeft [] (bitSymbol b::tail))
      spare (endTape left)) =
      some (configuration 4 (fromRight [.blank] (bitSymbol b::tail)) spare
        (fromLeft (bitSymbol b::left) [])) := by
  have h := step_command (buffered b) (fromLeft [] (bitSymbol b::tail)) spare (endTape left)
    ⟨4, .right, .stay, some (bitSymbol b)⟩ (by cases b <;> rfl)
  simpa only [fromLeft, fromRight, Tape.move, Tape.write, Option.getD_some, endTape] using h

theorem copy_run (b : Bool) (rest : List Bool) (tail left : List Symbol) (spare : Tape) :
    run machine (rest.length+1)
      (configuration (buffered b) (fromLeft (rest.map bitSymbol) (bitSymbol b::tail))
        spare (endTape left)) =
      configuration 4 (fromRight [.blank] ((b::rest).reverse.map bitSymbol ++ tail)) spare
        (fromLeft ((b::rest).reverse.map bitSymbol ++ left) []) := by
  induction rest generalizing b tail left with
  | nil =>
    simp only [List.length_nil, List.map_nil]
    rw [run_step 0 _ _ (copy_last b tail left spare)]
    rfl
  | cons c rest ih =>
    rw [List.length_cons, Nat.succ_add, run_step _ _ _ (copy_bit b c rest tail left spare), ih]
    simp only [List.reverse_cons, List.map_append, List.map_cons, List.map_nil,
      List.append_assoc, List.singleton_append, List.cons_append, List.nil_append]

theorem skip_first (b : Bool) (rest : List Bool) (spare : Tape) :
    step machine (configuration 4
      (fromRight [.blank] ((b::rest).map bitSymbol ++ [.blank])) spare
      (fromLeft ((b::rest).map bitSymbol) [])) =
      some (configuration 5
        (fromRight [bitSymbol b, .blank] (rest.map bitSymbol ++ [.blank])) spare
        ⟨rest.map bitSymbol, bitSymbol b, []⟩) := by
  have h := step_command 4 (fromRight [.blank] ((b::rest).map bitSymbol ++ [.blank]))
    spare (fromLeft ((b::rest).map bitSymbol) []) ⟨5, .right, .stay, none⟩ rfl
  cases rest <;> simpa only [fromRight, fromLeft, List.map_cons, List.map_nil,
    List.cons_append, List.nil_append, Tape.move, Tape.write, Option.getD_none] using h

theorem rewind_bit (b : Bool) (rest : List Bool) (left right : List Symbol)
    (head : Symbol) (spare : Tape) :
    step machine (configuration 5
      (fromRight left ((b::rest).map bitSymbol ++ [.blank])) spare
      ⟨(b::rest).map bitSymbol, head, right⟩) =
      some (configuration 5
        (fromRight (bitSymbol b::left) (rest.map bitSymbol ++ [.blank])) spare
        ⟨rest.map bitSymbol, bitSymbol b, head::right⟩) := by
  have h := step_command 5 (fromRight left ((b::rest).map bitSymbol ++ [.blank]))
    spare ⟨(b::rest).map bitSymbol, head, right⟩ ⟨5, .right, .left, none⟩
    (by cases b <;> rfl)
  cases rest <;> simpa only [fromRight, List.map_cons, List.map_nil, List.cons_append,
    List.nil_append, Tape.move, Tape.write, Option.getD_none] using h

theorem rewind_run (bits : List Bool) (left right : List Symbol) (head : Symbol) (spare : Tape) :
    run machine bits.length (configuration 5
      (fromRight left (bits.map bitSymbol ++ [.blank])) spare
      ⟨bits.map bitSymbol, head, right⟩) =
      configuration 5 (endTape (bits.reverse.map bitSymbol ++ left)) spare
        (fromRight [] (bits.reverse.map bitSymbol ++ head::right)) := by
  induction bits generalizing left right head with
  | nil => rfl
  | cons b rest ih =>
    rw [List.length_cons, run_step _ _ _ (rewind_bit b rest left right head spare), ih]
    simp only [List.reverse_cons, List.map_append, List.map_cons, List.map_nil,
      List.append_assoc, List.singleton_append]

def elapsed (bits : List Bool) : Nat := if bits.isEmpty then 1 else 3*bits.length+2

def finalInput : List Bool → Tape
  | [] => ⟨[], .blank, [.blank]⟩
  | b::rest => endTape ((b::rest).reverse.map bitSymbol ++ [.blank])

def finalConfiguration (bits : List Bool) (spare : Tape) : Configuration machine :=
  configuration (if bits.isEmpty then 1 else 5) (finalInput bits) spare (Tape.ofWord bits.reverse)

theorem fromRight_word (bits : List Bool) : fromRight [] (bits.map bitSymbol) = Tape.ofWord bits := by
  cases bits <;> rfl

/-- Complete configuration, including the visited input-boundary blanks. -/
theorem reverse_run (bits : List Bool) (spare : Tape) :
    run machine (elapsed bits) (configuration 0 (Tape.ofWord bits) spare Tape.blank) =
      finalConfiguration bits spare := by
  cases bits with
  | nil =>
    change run machine 1 (configuration 0 (endTape []) spare Tape.blank) = _
    rw [run_step _ _ _ (seek_end [] spare Tape.blank)]
    rfl
  | cons a rest =>
    let bits := a::rest
    have nonempty : bits.reverse ≠ [] := by simp [bits]
    obtain ⟨b,tail,rev⟩ : ∃ b tail, bits.reverse=b::tail := List.exists_cons_of_ne_nil nonempty
    have lengths : tail.length=rest.length := by
      have hlen := congrArg List.length rev
      simp only [List.length_reverse, bits, List.length_cons] at hlen
      omega
    have count : elapsed bits = bits.length+1+1+(tail.length+1)+1+rest.length := by
      simp only [elapsed, bits, List.isEmpty_cons, Bool.false_eq_true, if_false, List.length_cons]
      omega
    rw [show a::rest=bits from rfl, count]
    rw [run_add machine (bits.length+1+1+(tail.length+1)+1) rest.length,
      run_add machine (bits.length+1+1+(tail.length+1)) 1,
      run_add machine (bits.length+1+1) (tail.length+1),
      run_add machine (bits.length+1) 1, run_add machine bits.length 1]
    rw [← fromRight_word, seek_run]
    rw [run_step _ _ _ (seek_end _ spare Tape.blank)]
    simp only [List.append_nil]
    change run machine rest.length (run machine 1 (run machine (tail.length+1)
      (run machine 1 (configuration 1 (fromLeft (bits.reverse.map bitSymbol) [.blank])
        spare Tape.blank)))) = _
    rw [rev, run_step _ _ _ (load_bit b tail [.blank] spare Tape.blank)]
    change run machine rest.length (run machine 1
      (run machine (tail.length+1) (configuration (buffered b)
        (fromLeft (tail.map bitSymbol) [bitSymbol b,.blank]) spare (endTape [])))) = _
    rw [copy_run]
    have reverseBack : (b::tail).reverse = bits := by rw [← rev, List.reverse_reverse]
    rw [reverseBack]
    simp only [List.append_nil]
    change run machine rest.length (run machine 1 (configuration 4
      (fromRight [.blank] ((a::rest).map bitSymbol ++ [.blank])) spare
      (fromLeft ((a::rest).map bitSymbol) []))) = _
    rw [run_step _ _ _ (skip_first a rest spare)]
    change run machine rest.length (configuration 5
      (fromRight [bitSymbol a, .blank] (rest.map bitSymbol ++ [.blank])) spare
      ⟨rest.map bitSymbol, bitSymbol a, []⟩) = _
    rw [rewind_run]
    simp only [finalConfiguration, bits, List.isEmpty_cons, Bool.false_eq_true, if_false,
      finalInput, List.reverse_cons, List.map_append, List.map_cons, List.map_nil,
      List.append_assoc, List.singleton_append]
    apply congrArg (fun output => configuration 5
      (endTape (rest.reverse.map bitSymbol ++ [bitSymbol a, .blank])) spare output)
    rw [← fromRight_word (rest.reverse ++ [a]), List.map_append]
    rfl

theorem final_halted (bits : List Bool) (spare : Tape) :
    Halted machine (finalConfiguration bits spare) := by
  cases bits <;> simp [Halted, step, finalConfiguration, finalInput, configuration,
    machine, instruction, endTape]

theorem elapsed_bound (bits : List Bool) : elapsed bits ≤ 3*bits.length+2 := by
  cases bits <;> simp [elapsed]

/-- A total three-tape program. The second input tape is untouched, the output
is canonical, and the input's final explicit representation is `finalInput`. -/
theorem reverse_executes (x y : List Bool) :
    Executes machine convention x y x.reverse (elapsed x) ∧ elapsed x ≤ 3*x.length+2 := by
  have start : initial machine convention x y = configuration 0 (Tape.ofWord x)
      (Tape.ofWord y) Tape.blank := rfl
  constructor
  · rw [Executes, start, reverse_run]
    exact ⟨final_halted x (Tape.ofWord y), by simp [finalConfiguration, configuration, convention]⟩
  · exact elapsed_bound x

def sourceMSBValue (bits : List Bool) : Nat := wordValue bits.reverse

theorem input_value (bits : List Bool) : sourceMSBValue bits.reverse = wordValue bits := by
  simp only [sourceMSBValue, List.reverse_reverse]

end CurrentMain.BinaryWordReversal
#print axioms CurrentMain.BinaryWordReversal.reverse_run
#print axioms CurrentMain.BinaryWordReversal.final_halted
#print axioms CurrentMain.BinaryWordReversal.reverse_executes
#print axioms CurrentMain.BinaryWordReversal.input_value
