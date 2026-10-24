import BinaryCountDispatcherMarkedInput

/-! A four-state, two-tape allocation scan for the exact marked-input dispatcher
interface. An actual input bit allocates one zero counter cell. The table has
no width, remaining-count or address argument. It starts at the input's right
blank and a pristine counter, then restores the marked input to its first bit
and the width-n zero counter to its home blank. Empty input takes three steps.

For input4 slot2/3, take word=(pad n x).reverse or (pad n y).reverse. Their
endTape left lists are exactly word.reverse.map bitSymbol. The first/second
input4 finalInput tapes are not interchangeable with these work copies.
This literal interface does not itself sequence the two machines, establish an
amortized counting cost, normalize a compact counter, or instantiate a caller
Plan/Budget. The accepted marked-input count theorem is the next consumer. -/
namespace CurrentMain.BinaryCounterZeroAllocation
open FixedTapeMachine

private theorem fin2 (i : Fin 2) : i=0 ∨ i=1 := by
  exact (show ∀ j : Fin 2, j=0 ∨ j=1 by decide) i

def action (next : Fin 4) (inputMove counterMove : Move)
    (counterWrite : Option Symbol) (r : Fin 2 → Symbol) : Action 2 4 where
  state := next
  writes := fun i => if i=0 then r 0 else counterWrite.getD (r 1)
  moves := fun i => if i=0 then inputMove else counterMove

/-- State0 enters both marked intervals;1 allocates from actual input symbols;
2 rewinds the zero counter;3 halts with the input at its first marked digit. -/
def machine : Machine where
  tapes := 2
  states := 4
  initial := 0
  transition := fun s r =>
    match s.val with
    | 0 => some (action 1 .left .right none r)
    | 1 => match r (0 : Fin 2) with
      | .blank => some (action 2 .stay .left none r)
      | .zero | .one => some (action 1 .left .right (some .zero) r)
    | 2 => match r (1 : Fin 2) with
      | .blank => some (action 3 .right .stay none r)
      | .zero | .one => some (action 2 .stay .left none r)
    | _ => none

def configuration (s : Fin 4) (input counter : Tape) : Configuration machine :=
  ⟨s,fun i => if i=(0 : Fin 2) then input else counter⟩

def initialConfiguration (word : List Bool) : Configuration machine :=
  configuration 0 ⟨word.reverse.map bitSymbol,.blank,[]⟩ Tape.blank

def finalConfiguration (word : List Bool) : Configuration machine :=
  configuration 3 (BinaryCountDispatcherMarkedInput.inputTape word)
    (BinaryCarryIncrement.homeTape (List.replicate word.length false))

private def scanInput : List Bool → List Symbol → Tape
  | [], right => ⟨[],.blank,right⟩
  | b::rest, right => ⟨rest.map bitSymbol,bitSymbol b,right⟩

private def counterEnd (n : Nat) : Tape :=
  ⟨List.replicate n .zero++[.blank],.blank,[]⟩

private def counterRewind : Nat → List Symbol → Tape
  | 0, right => ⟨[],.blank,right⟩
  | n+1, right => ⟨List.replicate n .zero++[.blank],.zero,right⟩

/- The accepted abstract step rule is reused verbatim. -/
private theorem step_of_transition (m : Machine) (c : Configuration m)
    (a : Action m.tapes m.states)
    (h : m.transition c.state (fun i => (c.tapes i).head) = some a) :
    step m c = some (Configuration.mk a.state
      (fun i => ((c.tapes i).write (a.writes i)).move (a.moves i))) := by
  unfold step
  rw [h]

private theorem step_action (s next : Fin 4) (input counter : Tape)
    (inputMove counterMove : Move) (counterWrite : Option Symbol)
    (h : machine.transition s (fun i : Fin 2 => ((configuration s input counter).tapes i).head)=
      some (action next inputMove counterMove counterWrite
        (fun i : Fin 2 => ((configuration s input counter).tapes i).head))) :
    step machine (configuration s input counter)=
      some (configuration next (input.move inputMove)
        ((counter.write (counterWrite.getD counter.head)).move counterMove)) := by
  refine (step_of_transition machine (configuration s input counter) _ h).trans ?_
  dsimp only [action,configuration]
  apply congrArg some
  apply congrArg (fun tapes : Fin 2 → Tape => (Configuration.mk next tapes : Configuration machine))
  funext i
  rcases fin2 i with rfl|rfl <;> simp [Tape.write]

private theorem start_step (remaining : List Bool) :
    step machine (configuration 0 ⟨remaining.map bitSymbol,.blank,[]⟩ Tape.blank)=
      some (configuration 1 (scanInput remaining [.blank]) (counterEnd 0)) := by
  have h := step_action 0 1 ⟨remaining.map bitSymbol,.blank,[]⟩ Tape.blank
    .left .right none (by rfl)
  cases remaining <;>
    simpa only [scanInput,counterEnd,Tape.blank,Tape.move,Tape.write,Option.getD_none,
      List.map_nil,List.map_cons,List.replicate_zero,List.nil_append] using h

private theorem allocate_step (b : Bool) (rest : List Bool) (right : List Symbol) (k : Nat) :
    step machine (configuration 1 (scanInput (b::rest) right) (counterEnd k))=
      some (configuration 1 (scanInput rest (bitSymbol b::right)) (counterEnd (k+1))) := by
  have h := step_action 1 1 (scanInput (b::rest) right) (counterEnd k)
    .left .right (some .zero) (by cases b <;> rfl)
  cases rest <;>
    simpa only [scanInput,counterEnd,Tape.move,Tape.write,Option.getD_some,
      List.map_nil,List.map_cons,List.replicate_succ,List.cons_append] using h

private theorem allocate_run (remaining : List Bool) (right : List Symbol) (k : Nat) :
    run machine remaining.length (configuration 1 (scanInput remaining right) (counterEnd k))=
      configuration 1 (scanInput [] (remaining.reverse.map bitSymbol++right))
        (counterEnd (k+remaining.length)) := by
  induction remaining generalizing right k with
  | nil => simp only [List.length_nil,run,List.reverse_nil,List.map_nil,List.nil_append,Nat.add_zero]
  | cons b rest ih =>
    simp only [List.length_cons,run,allocate_step]
    rw [ih]
    simp only [List.reverse_cons,List.map_append,List.map_cons,List.map_nil,List.append_assoc,
      List.singleton_append]
    congr 2
    omega

private theorem return_step (right : List Symbol) (k : Nat) :
    step machine (configuration 1 (scanInput [] right) (counterEnd k))=
      some (configuration 2 (scanInput [] right) (counterRewind k [.blank])) := by
  have h := step_action 1 2 (scanInput [] right) (counterEnd k) .stay .left none (by rfl)
  cases k <;>
    simpa only [counterEnd,counterRewind,Tape.move,Tape.write,Option.getD_none,
      List.replicate_zero,List.replicate_succ,List.nil_append,List.cons_append] using h

private theorem rewind_step (input : Tape) (k : Nat) (right : List Symbol) :
    step machine (configuration 2 input (counterRewind (k+1) right))=
      some (configuration 2 input (counterRewind k (.zero::right))) := by
  have h := step_action 2 2 input (counterRewind (k+1) right) .stay .left none (by rfl)
  cases k <;>
    simpa only [counterRewind,Tape.move,Tape.write,Option.getD_none,
      List.replicate_zero,List.replicate_succ,List.nil_append,List.cons_append] using h

private theorem rewind_run (input : Tape) (k : Nat) (right : List Symbol) :
    run machine k (configuration 2 input (counterRewind k right))=
      configuration 2 input (counterRewind 0 (List.replicate k .zero++right)) := by
  induction k generalizing right with
  | zero => rfl
  | succ k ih =>
    simp only [run,rewind_step]
    rw [ih]
    simp only [List.replicate_succ',List.append_assoc,List.singleton_append]

private theorem finish_step (input : Tape) (right : List Symbol) :
    step machine (configuration 2 input (counterRewind 0 right))=
      some (configuration 3 (input.move .right) (counterRewind 0 right)) := by
  have h := step_action 2 3 input (counterRewind 0 right) .right .stay none (by rfl)
  simpa only [counterRewind,Tape.move,Tape.write,Option.getD_none] using h

/-- Exactly one zero cell per actual input symbol is allocated. Both boundary
blanks, the restored input head, and the complete counter footprint are fixed.
The elapsed run index includes the empty-input branch without a size premise. -/
theorem allocate_run_exact (word : List Bool) :
    run machine (2*word.length+3) (initialConfiguration word)=finalConfiguration word := by
  have start : run machine 1 (initialConfiguration word)=
      configuration 1 (scanInput word.reverse [.blank]) (counterEnd 0) := by
    simp only [initialConfiguration,run,start_step]
  rw [show 2*word.length+3=1+word.length+1+word.length+1 by omega]
  rw [run_add machine (1+word.length+1+word.length) 1,
    run_add machine (1+word.length+1) word.length,
    run_add machine (1+word.length) 1,run_add machine 1 word.length,start]
  have allocation := allocate_run word.reverse [.blank] 0
  simp only [List.length_reverse,List.reverse_reverse,Nat.zero_add] at allocation
  rw [allocation]
  simp only [run,return_step]
  rw [rewind_run]
  simp only [run,finish_step]
  unfold finalConfiguration
  have counter : counterRewind 0 (List.replicate word.length .zero++[.blank])=
      BinaryCarryIncrement.homeTape (List.replicate word.length false) := by
    simp only [counterRewind,BinaryCarryIncrement.homeTape,List.map_replicate,bitSymbol,
      Bool.false_eq_true,if_false]
  rw [counter]
  cases word with
  | nil => rfl
  | cons b rest => rfl

theorem final_halted (word : List Bool) : Halted machine (finalConfiguration word) := by
  rfl

theorem allocated_width (word : List Bool) : (List.replicate word.length false).length=word.length :=
  List.length_replicate

end CurrentMain.BinaryCounterZeroAllocation
#print axioms CurrentMain.BinaryCounterZeroAllocation.allocate_run_exact
#print axioms CurrentMain.BinaryCounterZeroAllocation.final_halted
#print axioms CurrentMain.BinaryCounterZeroAllocation.allocated_width
