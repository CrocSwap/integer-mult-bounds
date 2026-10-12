import BinaryCarryIncrement

/-! A concrete nine-state/two-tape compact-copy helper. A marked home counter
is scanned, its high zero cells are blanked, and its retained little-endian
prefix is copied onto a pristine tape. Lookahead and a paired rewind avoid
allocating an extra output blank. The old counter footprint is retained.
Empty/all-zero words produce canonical empty output. This module establishes
representation and physical cost only; value/logarithmic-size adapters and the
six-tape prepared-input caller composition are separate obligations. -/
namespace CurrentMain.BinaryCounterCompactCopy
open FixedTapeMachine
set_option Elab.async false

private theorem fin2 (i : Fin 2) : i=0 ∨ i=1 := by
  exact (show ∀ j : Fin 2, j=0 ∨ j=1 by decide) i

def fromRight (left : List Symbol) : List Symbol → Tape
  | [] => ⟨left,.blank,[]⟩
  | a::rest => ⟨left,a,rest⟩
def fromLeft : List Symbol → List Symbol → Tape
  | [], right => ⟨[],.blank,right⟩
  | a::rest, right => ⟨rest,a,right⟩
def endTape (left : List Symbol) : Tape := ⟨left,.blank,[]⟩
def buffered (b : Bool) : Fin 9 := if b then 6 else 5

def action (next : Fin 9) (inputMove outputMove : Move)
    (inputWrite outputWrite : Option Symbol) (r : Fin 2 → Symbol) : Action 2 9 where
  state := next
  writes := fun i => if i=0 then inputWrite.getD (r 0) else outputWrite.getD (r 1)
  moves := fun i => if i=0 then inputMove else outputMove

def machine : Machine where
  tapes := 2
  states := 9
  initial := 0
  transition := fun s r =>
    match s.val with
    | 0 => some (action 1 .right .stay none none r)
    | 1 => match r (0 : Fin 2) with
      | .blank => some (action 2 .left .stay none none r)
      | .zero | .one => some (action 1 .right .stay none none r)
    | 2 => match r (0 : Fin 2) with
      | .zero => some (action 2 .left .stay (some .blank) none r)
      | .one => some (action 3 .left .stay none none r)
      | .blank => some (action 8 .stay .stay none none r)
    | 3 => match r (0 : Fin 2) with
      | .blank => some (action 4 .right .stay none none r)
      | .zero | .one => some (action 3 .left .stay none none r)
    | 4 => match r (0 : Fin 2) with
      | .zero => some (action 5 .right .stay none none r)
      | .one => some (action 6 .right .stay none none r)
      | .blank => none
    | 5 => match r (0 : Fin 2) with
      | .zero => some (action 5 .right .right none (some .zero) r)
      | .one => some (action 6 .right .right none (some .zero) r)
      | .blank => some (action 7 .left .stay none (some .zero) r)
    | 6 => match r (0 : Fin 2) with
      | .zero => some (action 5 .right .right none (some .one) r)
      | .one => some (action 6 .right .right none (some .one) r)
      | .blank => some (action 7 .left .stay none (some .one) r)
    | 7 => some (action 8 .left .stay none none r)
    | _ => match r (0 : Fin 2) with
      | .blank => none
      | .zero | .one => some (action 8 .left .left none none r)

def configuration (s : Fin 9) (input output : Tape) : Configuration machine :=
  ⟨s,fun i => if i=(0 : Fin 2) then input else output⟩

def dropHighZeros : List Bool → List Bool
  | false::rest => dropHighZeros rest
  | rest => rest

def compact (bits : List Bool) : List Bool := (dropHighZeros bits.reverse).reverse

def initialConfiguration (bits : List Bool) : Configuration machine :=
  configuration 0 (BinaryCarryIncrement.homeTape bits) Tape.blank

def finalInput (bits : List Bool) : Tape :=
  ⟨[],.blank,(compact bits).map bitSymbol ++ List.replicate (bits.length-(compact bits).length+1) .blank⟩

def finalConfiguration (bits : List Bool) : Configuration machine :=
  configuration 8 (finalInput bits) (Tape.ofWord (compact bits))

def elapsed (bits : List Bool) : Nat :=
  if (compact bits).isEmpty then 2*bits.length+3 else 2*bits.length+2*(compact bits).length+4

/- The accepted abstract step rule is reused verbatim. -/
private theorem step_of_transition (m : Machine) (c : Configuration m)
    (a : Action m.tapes m.states)
    (h : m.transition c.state (fun i => (c.tapes i).head) = some a) :
    step m c = some (Configuration.mk a.state
      (fun i => ((c.tapes i).write (a.writes i)).move (a.moves i))) := by
  unfold step
  rw [h]

private theorem step_action (s next : Fin 9) (input output : Tape)
    (inputMove outputMove : Move) (inputWrite outputWrite : Option Symbol)
    (h : machine.transition s (fun i : Fin 2 => ((configuration s input output).tapes i).head)=
      some (action next inputMove outputMove inputWrite outputWrite
        (fun i : Fin 2 => ((configuration s input output).tapes i).head))) :
    step machine (configuration s input output)=
      some (configuration next
        ((input.write (inputWrite.getD input.head)).move inputMove)
        ((output.write (outputWrite.getD output.head)).move outputMove)) := by
  refine (step_of_transition machine (configuration s input output) _ h).trans ?_
  dsimp only [action,configuration]
  apply congrArg some
  apply congrArg (@Configuration.mk machine next)
  funext i
  rcases fin2 i with rfl|rfl <;> rfl

private theorem run_step (n : Nat) (c d : Configuration machine) (h : step machine c=some d) :
    run machine (n+1) c=run machine n d := by simp only [run,h]

private theorem enter_step (bits : List Bool) :
    step machine (initialConfiguration bits)=
      some (configuration 1 (fromRight [.blank] (bits.map bitSymbol++[.blank])) Tape.blank) := by
  have h := step_action 0 1 (BinaryCarryIncrement.homeTape bits) Tape.blank .right .stay none none (by rfl)
  cases bits <;> simpa only [initialConfiguration,BinaryCarryIncrement.homeTape,
    List.map_nil,List.map_cons,List.nil_append,List.cons_append,fromRight,Tape.write,Tape.move,Option.getD_none] using h

private theorem seek_bit (b : Bool) (rest : List Bool) (left : List Symbol) (output : Tape) :
    step machine (configuration 1 (fromRight left ((b::rest).map bitSymbol++[.blank])) output)=
      some (configuration 1 (fromRight (bitSymbol b::left) (rest.map bitSymbol++[.blank])) output) := by
  have h := step_action 1 1 (fromRight left ((b::rest).map bitSymbol++[.blank])) output
    .right .stay none none (by cases b <;> rfl)
  cases rest <;> simpa only [fromRight,List.map_cons,List.map_nil,List.cons_append,
    List.nil_append,Tape.write,Tape.move,Option.getD_none] using h

private theorem seek_run (bits : List Bool) (left : List Symbol) (output : Tape) :
    run machine bits.length (configuration 1 (fromRight left (bits.map bitSymbol++[.blank])) output)=
      configuration 1 (endTape (bits.reverse.map bitSymbol++left)) output := by
  induction bits generalizing left with
  | nil => rfl
  | cons b rest ih =>
    rw [List.length_cons,run_step _ _ _ (seek_bit b rest left output),ih]
    simp only [List.reverse_cons,List.map_append,List.map_cons,List.map_nil,
      List.append_assoc,List.singleton_append]

private theorem end_step (left : List Symbol) (output : Tape) :
    step machine (configuration 1 (endTape left) output)=
      some (configuration 2 (fromLeft left [.blank]) output) := by
  have h := step_action 1 2 (endTape left) output .left .stay none none (by rfl)
  cases left <;> simpa only [endTape,fromLeft,Tape.write,Tape.move,Option.getD_none] using h

private theorem seek_complete (bits : List Bool) :
    run machine (bits.length+2) (initialConfiguration bits)=
      configuration 2 (fromLeft (bits.reverse.map bitSymbol++[.blank]) [.blank]) Tape.blank := by
  rw [show bits.length+2=1+bits.length+1 by omega,run_add machine (1+bits.length) 1,
    run_add machine 1 bits.length,run_step 0 _ _ (enter_step bits)]
  change run machine 1 (run machine bits.length
    (configuration 1 (fromRight [.blank] (bits.map bitSymbol++[.blank])) Tape.blank))=_
  rw [seek_run,run_step 0 _ _ (end_step _ Tape.blank)]
  rfl

private theorem trim_zero_step (rest : List Bool) (right : List Symbol) (output : Tape) :
    step machine (configuration 2 (fromLeft ((false::rest).map bitSymbol++[.blank]) right) output)=
      some (configuration 2 (fromLeft (rest.map bitSymbol++[.blank]) (.blank::right)) output) := by
  have h := step_action 2 2 (fromLeft ((false::rest).map bitSymbol++[.blank]) right) output
    .left .stay (some .blank) none (by rfl)
  cases rest <;> simpa only [fromLeft,List.map_cons,List.map_nil,List.cons_append,
    List.nil_append,Tape.write,Tape.move,Option.getD_none,Option.getD_some] using h

private theorem trim_zeros_run (k : Nat) (rest : List Bool) (right : List Symbol) (output : Tape) :
    run machine k (configuration 2 (fromLeft ((List.replicate k false++rest).map bitSymbol++[.blank]) right) output)=
      configuration 2 (fromLeft (rest.map bitSymbol++[.blank]) (List.replicate k .blank++right)) output := by
  induction k generalizing right with
  | zero => rfl
  | succ k ih =>
    simp only [List.replicate_succ,List.cons_append]
    rw [run_step _ _ _ (trim_zero_step _ right output),ih]
    have pads := congrArg (fun xs : List Symbol => xs++right)
      (List.replicate_succ' (n:=k) (a:=Symbol.blank))
    simp only [List.replicate_succ,List.cons_append,List.append_assoc,List.singleton_append,List.nil_append] at pads
    rw [pads]

private theorem trim_finish (right : List Symbol) (output : Tape) :
    step machine (configuration 2 (fromLeft [.blank] right) output)=
      some (configuration 8 (fromLeft [.blank] right) output) := by
  have h := step_action 2 8 (fromLeft [.blank] right) output .stay .stay none none (by rfl)
  simpa only [Tape.write,Tape.move,Option.getD_none] using h

private theorem highest_one_step (rest : List Bool) (right : List Symbol) (output : Tape) :
    step machine (configuration 2 (fromLeft ((true::rest).map bitSymbol++[.blank]) right) output)=
      some (configuration 3 (fromLeft (rest.map bitSymbol++[.blank]) (.one::right)) output) := by
  have h := step_action 2 3 (fromLeft ((true::rest).map bitSymbol++[.blank]) right) output
    .left .stay none none (by rfl)
  cases rest <;> simpa only [fromLeft,List.map_cons,List.map_nil,List.cons_append,
    List.nil_append,Tape.write,Tape.move,Option.getD_none,bitSymbol,if_true] using h

private theorem home_bit (b : Bool) (rest : List Bool) (right : List Symbol) (output : Tape) :
    step machine (configuration 3 (fromLeft ((b::rest).map bitSymbol++[.blank]) right) output)=
      some (configuration 3 (fromLeft (rest.map bitSymbol++[.blank]) (bitSymbol b::right)) output) := by
  have h := step_action 3 3 (fromLeft ((b::rest).map bitSymbol++[.blank]) right) output
    .left .stay none none (by cases b <;> rfl)
  cases rest <;> simpa only [fromLeft,List.map_cons,List.map_nil,List.cons_append,
    List.nil_append,Tape.write,Tape.move,Option.getD_none] using h

private theorem home_run (bits : List Bool) (right : List Symbol) (output : Tape) :
    run machine bits.length (configuration 3 (fromLeft (bits.map bitSymbol++[.blank]) right) output)=
      configuration 3 (fromLeft [.blank] (bits.reverse.map bitSymbol++right)) output := by
  induction bits generalizing right with
  | nil => rfl
  | cons b rest ih =>
    rw [List.length_cons,run_step _ _ _ (home_bit b rest right output),ih]
    simp only [List.reverse_cons,List.map_append,List.map_cons,List.map_nil,List.append_assoc,List.singleton_append]

private theorem home_end_step (right : List Symbol) (output : Tape) :
    step machine (configuration 3 (fromLeft [.blank] right) output)=
      some (configuration 4 (fromRight [.blank] right) output) := by
  have h := step_action 3 4 (fromLeft [.blank] right) output .right .stay none none (by rfl)
  cases right <;> simpa only [fromLeft,fromRight,Tape.write,Tape.move,Option.getD_none] using h

private theorem load_bit (b : Bool) (rest : List Bool) (tail : List Symbol) (output : Tape) :
    step machine (configuration 4 (fromRight [.blank] ((b::rest).map bitSymbol++(.blank::tail))) output)=
      some (configuration (buffered b) (fromRight [bitSymbol b,.blank] (rest.map bitSymbol++(.blank::tail))) output) := by
  have h := step_action 4 (buffered b) (fromRight [.blank] ((b::rest).map bitSymbol++(.blank::tail))) output
    .right .stay none none (by cases b <;> rfl)
  cases rest <;> simpa only [fromRight,List.map_cons,List.map_nil,List.cons_append,List.nil_append,
    Tape.write,Tape.move,Option.getD_none] using h

private theorem copy_bit (b c : Bool) (rest : List Bool) (tail left outLeft : List Symbol) :
    step machine (configuration (buffered b) (fromRight (bitSymbol b::left) ((c::rest).map bitSymbol++(.blank::tail))) (endTape outLeft))=
      some (configuration (buffered c) (fromRight (bitSymbol c::bitSymbol b::left) (rest.map bitSymbol++(.blank::tail)))
        (endTape (bitSymbol b::outLeft))) := by
  have h := step_action (buffered b) (buffered c)
    (fromRight (bitSymbol b::left) ((c::rest).map bitSymbol++(.blank::tail))) (endTape outLeft)
    .right .right none (some (bitSymbol b)) (by cases b <;> cases c <;> rfl)
  cases rest <;> simpa only [fromRight,endTape,List.map_cons,List.map_nil,List.cons_append,
    List.nil_append,Tape.write,Tape.move,Option.getD_none,Option.getD_some] using h

private theorem copy_last (b : Bool) (tail left outLeft : List Symbol) :
    step machine (configuration (buffered b) (fromRight (bitSymbol b::left) (.blank::tail)) (endTape outLeft))=
      some (configuration 7 (fromLeft (bitSymbol b::left) (.blank::tail)) (fromLeft (bitSymbol b::outLeft) [])) := by
  have h := step_action (buffered b) 7 (fromRight (bitSymbol b::left) (.blank::tail)) (endTape outLeft)
    .left .stay none (some (bitSymbol b)) (by cases b <;> rfl)
  simpa only [fromRight,fromLeft,endTape,Tape.write,Tape.move,Option.getD_none,Option.getD_some] using h

private theorem copy_run (b : Bool) (rest : List Bool) (tail left outLeft : List Symbol) :
    run machine (rest.length+1)
      (configuration (buffered b) (fromRight (bitSymbol b::left) (rest.map bitSymbol++(.blank::tail))) (endTape outLeft))=
      configuration 7 (fromLeft ((b::rest).reverse.map bitSymbol++left) (.blank::tail))
        (fromLeft ((b::rest).reverse.map bitSymbol++outLeft) []) := by
  induction rest generalizing b left outLeft with
  | nil =>
    simp only [List.length_nil,Nat.zero_add,List.map_nil,List.nil_append]
    rw [run_step 0 _ _ (copy_last b tail left outLeft)]
    rfl
  | cons c rest ih =>
    rw [List.length_cons,Nat.succ_add,run_step _ _ _ (copy_bit b c rest tail left outLeft),ih]
    simp only [List.reverse_cons,List.map_append,List.map_cons,List.map_nil,List.append_assoc,List.singleton_append,List.cons_append,List.nil_append]

private theorem skip_last (b : Bool) (rest : List Bool) (tail : List Symbol) :
    step machine (configuration 7 (fromLeft ((b::rest).map bitSymbol++[.blank]) tail) (fromLeft ((b::rest).map bitSymbol) []))=
      some (configuration 8 (fromLeft (rest.map bitSymbol++[.blank]) (bitSymbol b::tail))
        ⟨rest.map bitSymbol,bitSymbol b,[]⟩) := by
  have h := step_action 7 8 (fromLeft ((b::rest).map bitSymbol++[.blank]) tail) (fromLeft ((b::rest).map bitSymbol) [])
    .left .stay none none (by rfl)
  cases rest <;> simpa only [fromLeft,List.map_cons,List.map_nil,List.cons_append,List.nil_append,
    Tape.write,Tape.move,Option.getD_none] using h

private theorem rewind_bit (b : Bool) (rest : List Bool) (tail right : List Symbol) (head : Symbol) :
    step machine (configuration 8 (fromLeft ((b::rest).map bitSymbol++[.blank]) tail) ⟨(b::rest).map bitSymbol,head,right⟩)=
      some (configuration 8 (fromLeft (rest.map bitSymbol++[.blank]) (bitSymbol b::tail))
        ⟨rest.map bitSymbol,bitSymbol b,head::right⟩) := by
  have h := step_action 8 8 (fromLeft ((b::rest).map bitSymbol++[.blank]) tail) ⟨(b::rest).map bitSymbol,head,right⟩
    .left .left none none (by cases b <;> rfl)
  cases rest <;> simpa only [fromLeft,List.map_cons,List.map_nil,List.cons_append,List.nil_append,
    Tape.write,Tape.move,Option.getD_none] using h

private theorem rewind_run (bits : List Bool) (tail right : List Symbol) (head : Symbol) :
    run machine bits.length (configuration 8 (fromLeft (bits.map bitSymbol++[.blank]) tail) ⟨bits.map bitSymbol,head,right⟩)=
      configuration 8 (fromLeft [.blank] (bits.reverse.map bitSymbol++tail))
        (fromRight [] (bits.reverse.map bitSymbol++head::right)) := by
  induction bits generalizing tail right head with
  | nil => rfl
  | cons b rest ih =>
    rw [List.length_cons,run_step _ _ _ (rewind_bit b rest tail right head),ih]
    simp only [List.reverse_cons,List.map_append,List.map_cons,List.map_nil,List.append_assoc,List.singleton_append]

private theorem fromRight_word (bits : List Bool) : fromRight [] (bits.map bitSymbol)=Tape.ofWord bits := by
  cases bits <;> rfl

private theorem finish_run (bits : List Bool) (tail : List Symbol) (hn : bits≠[]) :
    run machine bits.length (configuration 7 (fromLeft (bits.map bitSymbol++[.blank]) tail) (fromLeft (bits.map bitSymbol) []))=
      configuration 8 (fromLeft [.blank] (bits.reverse.map bitSymbol++tail)) (Tape.ofWord bits.reverse) := by
  cases bits with
  | nil => exact False.elim (hn rfl)
  | cons b rest =>
    rw [List.length_cons,run_step _ _ _ (skip_last b rest tail),rewind_run]
    simp only [List.reverse_cons,List.map_append,List.map_cons,List.map_nil,List.append_assoc,List.singleton_append]
    rw [← fromRight_word (rest.reverse++[b]),List.map_append]
    rfl

private theorem drop_zeros (k : Nat) (rest : List Bool) :
    dropHighZeros (List.replicate k false++rest)=dropHighZeros rest := by
  induction k with
  | zero => rfl
  | succ k ih => simpa only [List.replicate_succ,List.cons_append,dropHighZeros] using ih

private theorem compact_zero (k : Nat) : compact (List.replicate k false)=[] := by
  simpa only [compact,List.reverse_replicate,List.append_nil,dropHighZeros,List.reverse_nil]
    using congrArg List.reverse (drop_zeros k [])

private theorem compact_nonzero (q : List Bool) (k : Nat) :
    compact ((q++[true])++List.replicate k false)=q++[true] := by
  simp only [compact,List.reverse_append,List.reverse_replicate,List.reverse_cons,List.reverse_nil,
    List.nil_append,List.singleton_append,drop_zeros,dropHighZeros,List.reverse_reverse]

private theorem drop_shape (xs : List Bool) :
    ∃ k ys, xs=List.replicate k false++ys ∧ dropHighZeros xs=ys ∧
      (ys=[] ∨ ∃ rest, ys=true::rest) := by
  induction xs with
  | nil => exact ⟨0,[],rfl,rfl,Or.inl rfl⟩
  | cons b rest ih =>
    cases b with
    | false =>
      obtain ⟨k,ys,hx,hd,hy⟩ := ih
      refine ⟨k+1,ys,?_,hd,hy⟩
      simpa only [List.replicate_succ,List.cons_append] using congrArg (List.cons false) hx
    | true => exact ⟨0,true::rest,rfl,rfl,Or.inr ⟨rest,rfl⟩⟩

private theorem word_shape (bits : List Bool) :
    (∃ k, bits=List.replicate k false) ∨
      ∃ q k, bits=(q++[true])++List.replicate k false := by
  obtain ⟨k,ys,hx,_,hy⟩ := drop_shape bits.reverse
  have back := congrArg List.reverse hx
  rcases hy with hy|⟨rest,hy⟩
  · left
    refine ⟨k,?_⟩
    simpa only [hy,List.append_nil,List.reverse_reverse,List.reverse_replicate] using back
  · right
    refine ⟨rest.reverse,k,?_⟩
    simpa only [hy,List.reverse_reverse,List.reverse_append,List.reverse_replicate,
      List.reverse_cons] using back

private theorem zero_run (k : Nat) :
    run machine (2*k+3) (initialConfiguration (List.replicate k false))=
      finalConfiguration (List.replicate k false) := by
  rw [show 2*k+3=(k+2)+k+1 by omega,run_add machine (k+2+k) 1,run_add machine (k+2) k]
  have seek := seek_complete (List.replicate k false)
  simp only [List.length_replicate,List.reverse_replicate] at seek
  rw [seek]
  have trim := trim_zeros_run k [] [.blank] Tape.blank
  simp only [List.append_nil,List.map_nil,List.nil_append] at trim
  rw [trim,run_step 0 _ _ (trim_finish _ Tape.blank)]
  simp only [finalConfiguration,finalInput,compact_zero,List.length_replicate,List.length_nil,
    Nat.sub_zero,List.map_nil,List.nil_append,Tape.ofWord]
  simp only [List.replicate_succ',List.singleton_append,fromLeft,run]

private theorem nonzero_run (q : List Bool) (k : Nat) :
    run machine (2*((q++[true]).length+k)+2*(q++[true]).length+4)
      (initialConfiguration ((q++[true])++List.replicate k false))=
      finalConfiguration ((q++[true])++List.replicate k false) := by
  let p := q++[true]
  have hp : p≠[] := by simp [p]
  obtain ⟨b,rest,hpcons⟩ := List.exists_cons_of_ne_nil hp
  have plen : p.length=q.length+1 := by simp [p]
  have rlen : rest.length+1=p.length := by rw [hpcons]; rfl
  have revnonempty : p.reverse≠[] := by simpa using hp
  let tail : List Symbol := List.replicate k .blank
  have blanks : List.replicate k .blank++[.blank]=.blank::tail := by
    simp only [tail,← List.replicate_succ',List.replicate_succ]
  have seek : run machine ((p++List.replicate k false).length+2)
      (initialConfiguration (p++List.replicate k false))=
      configuration 2 (fromLeft ((List.replicate k false++(true::q.reverse)).map bitSymbol++[.blank]) [.blank]) Tape.blank := by
    simpa only [p,List.reverse_append,List.reverse_replicate,List.reverse_cons,List.reverse_nil,
      List.nil_append,List.singleton_append] using seek_complete (p++List.replicate k false)
  have trim : run machine k
      (configuration 2 (fromLeft ((List.replicate k false++(true::q.reverse)).map bitSymbol++[.blank]) [.blank]) Tape.blank)=
      configuration 2 (fromLeft ((true::q.reverse).map bitSymbol++[.blank]) (.blank::tail)) Tape.blank := by
    simpa only [blanks] using trim_zeros_run k (true::q.reverse) [.blank] Tape.blank
  have seekHome : run machine (q.length+1)
      (configuration 2 (fromLeft ((true::q.reverse).map bitSymbol++[.blank]) (.blank::tail)) Tape.blank)=
      configuration 3 (fromLeft [.blank] (p.map bitSymbol++(.blank::tail))) Tape.blank := by
    rw [run_step _ _ _ (highest_one_step q.reverse (.blank::tail) Tape.blank)]
    have h := home_run q.reverse (.one::.blank::tail) Tape.blank
    simp only [List.length_reverse,List.reverse_reverse] at h
    rw [h]
    simp only [p,List.map_append,List.map_cons,List.map_nil,List.append_assoc,List.singleton_append,
      bitSymbol,if_true]
  have copying : run machine (1+1+p.length+p.length)
      (configuration 3 (fromLeft [.blank] (p.map bitSymbol++(.blank::tail))) Tape.blank)=
      configuration 8 (fromLeft [.blank] (p.map bitSymbol++(.blank::tail))) (Tape.ofWord p) := by
    rw [run_add machine (1+1+p.length) p.length,run_add machine (1+1) p.length,
      run_add machine 1 1,run_step 0 _ _ (home_end_step _ Tape.blank)]
    change run machine p.length (run machine p.length (run machine 1
      (configuration 4 (fromRight [.blank] (p.map bitSymbol++(.blank::tail))) Tape.blank)))=_
    rw [hpcons,run_step 0 _ _ (load_bit b rest tail Tape.blank)]
    change run machine (b::rest).length (run machine (rest.length+1)
      (configuration (buffered b) (fromRight (bitSymbol b::[.blank]) (rest.map bitSymbol++(.blank::tail))) (endTape [])))=_
    rw [copy_run]
    simp only [List.append_nil]
    have hfinish := finish_run (b::rest).reverse (.blank::tail) (by simp)
    simp only [List.length_reverse,List.reverse_reverse] at hfinish
    rw [hfinish]
  have nlen : (p++List.replicate k false).length=p.length+k := by simp
  have total : 2*(p.length+k)+2*p.length+4=
      ((p++List.replicate k false).length+2)+k+(q.length+1)+(1+1+p.length+p.length) := by omega
  change run machine (2*(p.length+k)+2*p.length+4) (initialConfiguration (p++List.replicate k false))=_
  rw [total,run_add machine (((p++List.replicate k false).length+2)+k+(q.length+1)) (1+1+p.length+p.length),
    run_add machine (((p++List.replicate k false).length+2)+k) (q.length+1),
    run_add machine ((p++List.replicate k false).length+2) k,seek,trim,seekHome,copying]
  simp only [finalConfiguration,finalInput,p,compact_nonzero,List.length_append,List.length_replicate,
    Nat.add_sub_cancel_left,List.replicate_succ] <;> rfl

/-- Complete physical scan/copy endpoint. The run index covers the empty and
all-zero branches, and the output is a canonical finite tape. -/
theorem compact_run_exact (bits : List Bool) :
    run machine (elapsed bits) (initialConfiguration bits)=finalConfiguration bits := by
  rcases word_shape bits with ⟨k,rfl⟩|⟨q,k,rfl⟩
  · simpa only [elapsed,compact_zero,List.isEmpty_nil,if_true,List.length_replicate] using zero_run k
  · have he : (q++[true]).isEmpty=false := by cases q <;> rfl
    simpa only [elapsed,compact_nonzero,he,Bool.false_eq_true,if_false,
      List.length_append,List.length_replicate] using nonzero_run q k

theorem elapsed_bound (bits : List Bool) : elapsed bits≤4*bits.length+4 := by
  rcases word_shape bits with ⟨k,rfl⟩|⟨q,k,rfl⟩
  · simp only [elapsed,compact_zero,List.isEmpty_nil,if_true,List.length_replicate]
    omega
  · have he : (q++[true]).isEmpty=false := by cases q <;> rfl
    simp only [elapsed,compact_nonzero,he,Bool.false_eq_true,if_false,
      List.length_append,List.length_replicate]
    omega

theorem initial_counter (bits : List Bool) :
    (initialConfiguration bits).tapes (0 : Fin 2)=BinaryCarryIncrement.homeTape bits := by rfl

theorem initial_pristine (bits : List Bool) :
    (initialConfiguration bits).tapes (1 : Fin 2)=Tape.blank := by rfl

theorem final_halted (bits : List Bool) : Halted machine (finalConfiguration bits) := by rfl

theorem final_counter (bits : List Bool) :
    (finalConfiguration bits).tapes (0 : Fin 2)=
      ⟨[],.blank,(compact bits).map bitSymbol++List.replicate (bits.length-(compact bits).length+1) .blank⟩ := by rfl

theorem final_output (bits : List Bool) :
    (finalConfiguration bits).tapes (1 : Fin 2)=Tape.ofWord (compact bits) := by rfl

theorem zero_output (k : Nat) :
    (finalConfiguration (List.replicate k false)).tapes (1 : Fin 2)=Tape.blank := by
  rw [final_output,compact_zero]
  rfl

theorem empty_elapsed : elapsed []=3 := by rfl

end CurrentMain.BinaryCounterCompactCopy
#print axioms CurrentMain.BinaryCounterCompactCopy.compact_run_exact
#print axioms CurrentMain.BinaryCounterCompactCopy.elapsed_bound
#print axioms CurrentMain.BinaryCounterCompactCopy.initial_counter
#print axioms CurrentMain.BinaryCounterCompactCopy.initial_pristine
#print axioms CurrentMain.BinaryCounterCompactCopy.final_halted
#print axioms CurrentMain.BinaryCounterCompactCopy.final_counter
#print axioms CurrentMain.BinaryCounterCompactCopy.final_output
#print axioms CurrentMain.BinaryCounterCompactCopy.zero_output
#print axioms CurrentMain.BinaryCounterCompactCopy.empty_elapsed
