import BinaryInputPreparation
import BinaryCountReceiptAmortization

/-! Concrete five-tape preparation/count composition. States0..13 reproduce
input preparation, including its live state13 seek loop. States14..23 are the
renamed automatic-width counter. A missing preparation transition is intercepted
by exactly one tape-preserving bridge into state14. Counter input is prepared
slot2; slot4 is a pristine counter. Slots0,1,3 retain the preparation endpoint
throughout counting. The actual tables, accepted successful-prefix simulations
and PR64 receipt transport yield18*max(input lengths)+12. No first completion,
compact record, full source caller, Plan or represented-list Budget is claimed. -/
namespace CurrentMain.BinaryPreparedInputCount
open FixedTapeMachine
set_option Elab.async false

private theorem fin2 (i : Fin 2) : i=0 ∨ i=1 := by
  exact (show ∀ j : Fin 2, j=0 ∨ j=1 by decide) i
private theorem fin5 (i : Fin 5) : i=0 ∨ i=1 ∨ i=2 ∨ i=3 ∨ i=4 := by
  exact (show ∀ j : Fin 5, j=0 ∨ j=1 ∨ j=2 ∨ j=3 ∨ j=4 by decide) i

def prepState (s : Fin 14) : Fin 24 := ⟨s.val,by omega⟩
def countState (s : Fin 10) : Fin 24 := ⟨s.val+14,by omega⟩
def prepTape (i : Fin 4) : Fin 5 := ⟨i.val,by omega⟩
def prepReads (r : Fin 5 → Symbol) : Fin 4 → Symbol := fun i => r (prepTape i)
def countReads (r : Fin 5 → Symbol) : Fin 2 → Symbol :=
  fun i => if i=0 then r 2 else r 4

def prepAction (r : Fin 5 → Symbol) (a : Action 4 14) : Action 5 24 where
  state := prepState a.state
  writes := fun i => if h : i.val<4 then a.writes (⟨i.val,h⟩ : Fin 4) else r i
  moves := fun i => if h : i.val<4 then a.moves (⟨i.val,h⟩ : Fin 4) else .stay

def countAction (r : Fin 5 → Symbol) (a : Action 2 10) : Action 5 24 where
  state := countState a.state
  writes := fun i => if i=2 then a.writes 0 else if i=4 then a.writes 1 else r i
  moves := fun i => if i=2 then a.moves 0 else if i=4 then a.moves 1 else .stay

def bridgeAction (r : Fin 5 → Symbol) : Action 5 24 :=
  ⟨countState 0,r,fun _ => .stay⟩
def prepChoice (r : Fin 5 → Symbol) : Option (Action 4 14) → Option (Action 5 24)
  | some a => some (prepAction r a)
  | none => some (bridgeAction r)

def machine : Machine where
  tapes := 5
  states := 24
  initial := 0
  transition := fun s r =>
    if h : s.val<14 then
      prepChoice r (BinaryInputPreparation.machine.transition (⟨s.val,h⟩ : Fin 14) (prepReads r))
    else
      (BinaryAutomaticWidthCount.machine.transition (⟨s.val-14,by have := s.isLt; omega⟩ : Fin 10)
        (countReads r)).map (countAction r)

def embedPrep (c : Configuration BinaryInputPreparation.machine) (extra : Tape) : Configuration machine :=
  ⟨prepState c.state,fun i => if h : i.val<4 then c.tapes (⟨i.val,h⟩ : Fin 4) else extra⟩
def embedCount (c : Configuration BinaryAutomaticWidthCount.machine) (a b d : Tape) : Configuration machine :=
  ⟨countState c.state,fun i => if i=(0 : Fin 5) then a else if i=(1 : Fin 5) then b
    else if i=(2 : Fin 5) then c.tapes (0 : Fin 2) else if i=(3 : Fin 5) then d else c.tapes (1 : Fin 2)⟩

def width (x y : List Bool) : Nat := max x.length y.length
def leftPad (x y : List Bool) : List Bool := BinaryInputPreparation.pad (width x y) x
def rightPad (x y : List Bool) : List Bool := BinaryInputPreparation.pad (width x y) y
def sourceWord (x y : List Bool) : List Bool := (leftPad x y).reverse

def initialConfiguration (x y : List Bool) : Configuration machine :=
  embedPrep (BinaryInputPreparation.initialConfiguration x y) Tape.blank

def finalConfiguration (x y : List Bool) : Configuration machine :=
  embedCount (BinaryAutomaticWidthCount.finalConfiguration (sourceWord x y))
    (BinaryWordReversal.finalInput (leftPad x y)) (BinaryWordReversal.finalInput (rightPad x y))
    (BinaryWordReversal.endTape ((rightPad x y).map bitSymbol))

private theorem transition_prep (s : Fin 14) (r : Fin 5 → Symbol) :
    machine.transition (prepState s) r=prepChoice r (BinaryInputPreparation.machine.transition s (prepReads r)) := by
  cases s with
  | mk n hn => simp only [machine,prepState,hn,dif_pos]

private theorem transition_count (s : Fin 10) (r : Fin 5 → Symbol) :
    machine.transition (countState s) r=
      (BinaryAutomaticWidthCount.machine.transition s (countReads r)).map (countAction r) := by
  have h : ¬s.val+14<14 := by omega
  simp only [machine,countState,h,dif_neg,dite_false,Nat.add_sub_cancel]

private theorem reads_embedPrep (c : Configuration BinaryInputPreparation.machine) (extra : Tape) :
    prepReads (fun i : Fin 5 => ((embedPrep c extra).tapes i).head)=
      (fun i : Fin 4 => (c.tapes i).head) := by
  funext i
  have hi : i.val<4 := i.isLt
  simp only [prepReads,prepTape,embedPrep,hi,dif_pos]

private theorem reads_embedCount (c : Configuration BinaryAutomaticWidthCount.machine) (a b d : Tape) :
    countReads (fun i : Fin 5 => ((embedCount c a b d).tapes i).head)=
      (fun i : Fin 2 => (c.tapes i).head) := by
  funext i
  rcases fin2 i with rfl|rfl <;> rfl

private theorem step_of_transition (m : Machine) (c : Configuration m)
    (a : Action m.tapes m.states)
    (h : m.transition c.state (fun i => (c.tapes i).head) = some a) :
    step m c = some (Configuration.mk a.state
      (fun i => ((c.tapes i).write (a.writes i)).move (a.moves i))) := by
  unfold step
  rw [h]


private theorem step_prep (c d : Configuration BinaryInputPreparation.machine) (extra : Tape)
    (h : step BinaryInputPreparation.machine c=some d) :
    step machine (embedPrep c extra)=some (embedPrep d extra) := by
  cases ht : BinaryInputPreparation.machine.transition c.state (fun i => (c.tapes i).head) with
  | none =>
    simp only [step,ht] at h
    cases h
  | some a =>
    simp only [step,ht,Option.some.injEq] at h
    subst d
    let r : Fin 5 → Symbol := fun i => ((embedPrep c extra).tapes i).head
    have lifted : BinaryInputPreparation.machine.transition c.state (prepReads r)=some a :=
      (congrArg (BinaryInputPreparation.machine.transition c.state) (reads_embedPrep c extra)).trans ht
    have outer : machine.transition (embedPrep c extra).state r=some (prepAction r a) :=
      (transition_prep c.state r).trans (congrArg (prepChoice r) lifted)
    refine (step_of_transition machine (embedPrep c extra) (prepAction r a) outer).trans ?_
    dsimp only [prepAction,embedPrep]
    apply congrArg some
    apply congrArg (@Configuration.mk machine (prepState a.state))
    funext i
    rcases fin5 i with rfl|rfl|rfl|rfl|rfl <;> rfl

private theorem step_count (c e : Configuration BinaryAutomaticWidthCount.machine) (a b d : Tape)
    (h : step BinaryAutomaticWidthCount.machine c=some e) :
    step machine (embedCount c a b d)=some (embedCount e a b d) := by
  cases ht : BinaryAutomaticWidthCount.machine.transition c.state (fun i => (c.tapes i).head) with
  | none =>
    simp only [step,ht] at h
    cases h
  | some action =>
    simp only [step,ht,Option.some.injEq] at h
    subst e
    let r : Fin 5 → Symbol := fun i => ((embedCount c a b d).tapes i).head
    have lifted : BinaryAutomaticWidthCount.machine.transition c.state (countReads r)=some action :=
      (congrArg (BinaryAutomaticWidthCount.machine.transition c.state) (reads_embedCount c a b d)).trans ht
    have outer : machine.transition (embedCount c a b d).state r=some (countAction r action) :=
      (transition_count c.state r).trans (congrArg (Option.map (countAction r)) lifted)
    refine (step_of_transition machine (embedCount c a b d) (countAction r action) outer).trans ?_
    dsimp only [countAction,embedCount]
    apply congrArg some
    apply congrArg (@Configuration.mk machine (countState action.state))
    funext i
    rcases fin5 i with rfl|rfl|rfl|rfl|rfl <;> rfl

private theorem simulate_to_halt (source target : Machine)
    (embed : Configuration source → Configuration target)
    (sim : ∀ c d, step source c=some d → step target (embed c)=some (embed d))
    (budget : Nat) (c : Configuration source) (h : Halted source (run source budget c)) :
    ∃ k≤budget, run target k (embed c)=embed (run source budget c) := by
  induction budget generalizing c with
  | zero => exact ⟨0, Nat.le_refl _, rfl⟩
  | succ budget ih =>
    cases hs : step source c with
    | none =>
      refine ⟨0, Nat.zero_le _, ?_⟩
      simp only [run, hs]
    | some d =>
      have hd : Halted source (run source budget d) := by simpa only [run, hs] using h
      obtain ⟨k,hk,he⟩ := ih d hd
      refine ⟨k+1, by omega, ?_⟩
      simpa only [run, hs, sim c d hs] using he


private theorem handoff_configuration (x y : List Bool) :
    Configuration.mk (countState (0 : Fin 10))
      (embedPrep (BinaryInputPreparation.finalConfiguration x y) Tape.blank).tapes =
      embedCount (BinaryAutomaticWidthCount.initialConfiguration (sourceWord x y))
        (BinaryWordReversal.finalInput (leftPad x y)) (BinaryWordReversal.finalInput (rightPad x y))
        (BinaryWordReversal.endTape ((rightPad x y).map bitSymbol)) := by
  apply congrArg (@Configuration.mk machine (countState (0 : Fin 10)))
  funext i
  rcases fin5 i with rfl|rfl|rfl|rfl|rfl <;>
    simp only [embedPrep,embedCount,BinaryInputPreparation.finalConfiguration,BinaryInputPreparation.configuration,
      BinaryAutomaticWidthCount.initialConfiguration,BinaryAutomaticWidthCount.embedAllocation,BinaryCounterZeroAllocation.initialConfiguration,
      BinaryCounterZeroAllocation.configuration,sourceWord,leftPad,rightPad,width,
      BinaryWordReversal.endTape,List.reverse_reverse] <;> rfl

private theorem bridge_handoff (x y : List Bool) :
    step machine (embedPrep (BinaryInputPreparation.finalConfiguration x y) Tape.blank)=
      some (embedCount (BinaryAutomaticWidthCount.initialConfiguration (sourceWord x y))
        (BinaryWordReversal.finalInput (leftPad x y)) (BinaryWordReversal.finalInput (rightPad x y))
        (BinaryWordReversal.endTape ((rightPad x y).map bitSymbol))) := by
  let c := BinaryInputPreparation.finalConfiguration x y
  let r : Fin 5 → Symbol := fun i => ((embedPrep c Tape.blank).tapes i).head
  have ht : BinaryInputPreparation.machine.transition c.state (fun i => (c.tapes i).head)=none := by rfl
  have lifted : BinaryInputPreparation.machine.transition c.state (prepReads r)=none :=
    (congrArg (BinaryInputPreparation.machine.transition c.state) (reads_embedPrep c Tape.blank)).trans ht
  have outer : machine.transition (embedPrep c Tape.blank).state r=some (bridgeAction r) :=
    (transition_prep c.state r).trans (congrArg (prepChoice r) lifted)
  have he : step machine (embedPrep c Tape.blank)=
      some (Configuration.mk (countState (0 : Fin 10)) (embedPrep c Tape.blank).tapes) := by
    refine (step_of_transition machine (embedPrep c Tape.blank) (bridgeAction r) outer).trans ?_
    apply congrArg some
    apply congrArg (@Configuration.mk machine (countState (0 : Fin 10)))
    funext i
    rfl
  exact he.trans (congrArg some (handoff_configuration x y))

theorem sourceWord_length (x y : List Bool) : (sourceWord x y).length=width x y := by
  simp only [sourceWord,List.length_reverse,leftPad]
  exact BinaryInputPreparation.pad_length _ _ (Nat.le_max_left _ _)

/-- Actual five-tape preparation and counting, including one explicit bridge.
The counter capacity is physically allocated; no external width is supplied. -/
theorem prepare_count_run (x y : List Bool) :
    ∃ t≤18*width x y+12, run machine t (initialConfiguration x y)=finalConfiguration x y := by
  obtain ⟨p,hp,hprun⟩ := BinaryInputPreparation.prepare_run x y
  have ph : Halted BinaryInputPreparation.machine (run BinaryInputPreparation.machine p (BinaryInputPreparation.initialConfiguration x y)) := by
    rw [hprun]
    exact BinaryInputPreparation.final_halted x y
  obtain ⟨a,ha,harun⟩ := simulate_to_halt BinaryInputPreparation.machine machine
    (fun c => embedPrep c Tape.blank) (fun c d h => step_prep c d Tape.blank h) _ _ ph
  have haend : run machine a (initialConfiguration x y)=
      embedPrep (BinaryInputPreparation.finalConfiguration x y) Tape.blank := by
    simpa only [initialConfiguration,hprun] using harun
  have habridge : run machine (a+1) (initialConfiguration x y)=
      embedCount (BinaryAutomaticWidthCount.initialConfiguration (sourceWord x y))
        (BinaryWordReversal.finalInput (leftPad x y)) (BinaryWordReversal.finalInput (rightPad x y))
        (BinaryWordReversal.endTape ((rightPad x y).map bitSymbol)) := by
    rw [run_add machine a 1,haend]
    simp only [run,bridge_handoff]
  obtain ⟨t,ht,htrun⟩ := BinaryCountReceiptAmortization.count_run_linear (sourceWord x y)
  have ch : Halted BinaryAutomaticWidthCount.machine
      (run BinaryAutomaticWidthCount.machine t (BinaryAutomaticWidthCount.initialConfiguration (sourceWord x y))) := by
    rw [htrun]
    exact BinaryAutomaticWidthCount.final_halted _
  obtain ⟨b,hb,hbrun⟩ := simulate_to_halt BinaryAutomaticWidthCount.machine machine
    (fun c => embedCount c (BinaryWordReversal.finalInput (leftPad x y)) (BinaryWordReversal.finalInput (rightPad x y))
      (BinaryWordReversal.endTape ((rightPad x y).map bitSymbol)))
    (fun c d h => step_count c d _ _ _ h) _ _ ch
  have hbend : run machine b
      (embedCount (BinaryAutomaticWidthCount.initialConfiguration (sourceWord x y))
        (BinaryWordReversal.finalInput (leftPad x y)) (BinaryWordReversal.finalInput (rightPad x y))
        (BinaryWordReversal.endTape ((rightPad x y).map bitSymbol)))=finalConfiguration x y := by
    simpa only [htrun,finalConfiguration] using hbrun
  rw [sourceWord_length] at ht
  change p≤6*width x y+7 at hp
  refine ⟨a+1+b,by omega,?_⟩
  rw [run_add machine (a+1) b,habridge,hbend]

theorem initial_inputA (x y : List Bool) :
    (initialConfiguration x y).tapes (0 : Fin 5)=Tape.ofWord x := by rfl
theorem initial_inputB (x y : List Bool) :
    (initialConfiguration x y).tapes (1 : Fin 5)=Tape.ofWord y := by rfl
theorem initial_pristine (x y : List Bool) :
    (initialConfiguration x y).tapes (2 : Fin 5)=Tape.blank ∧
    (initialConfiguration x y).tapes (3 : Fin 5)=Tape.blank ∧
    (initialConfiguration x y).tapes (4 : Fin 5)=Tape.blank := by exact ⟨rfl,rfl,rfl⟩

theorem final_halted (x y : List Bool) : Halted machine (finalConfiguration x y) := by rfl
theorem final_state (x y : List Bool) : (finalConfiguration x y).state=(23 : Fin 24) := by rfl

theorem final_inputA (x y : List Bool) :
    (finalConfiguration x y).tapes (0 : Fin 5)=BinaryWordReversal.finalInput (leftPad x y) := by rfl
theorem final_inputB (x y : List Bool) :
    (finalConfiguration x y).tapes (1 : Fin 5)=BinaryWordReversal.finalInput (rightPad x y) := by rfl
theorem final_selected_work (x y : List Bool) :
    (finalConfiguration x y).tapes (2 : Fin 5)=
      ⟨(leftPad x y).map bitSymbol++[.blank],.blank,[]⟩ := by
  change (BinaryAutomaticWidthCount.finalConfiguration (sourceWord x y)).tapes (0 : Fin 2)=_
  rw [BinaryAutomaticWidthCount.final_input]
  simp only [sourceWord,List.reverse_reverse]
theorem final_other_work (x y : List Bool) :
    (finalConfiguration x y).tapes (3 : Fin 5)=
      BinaryWordReversal.endTape ((rightPad x y).map bitSymbol) := by rfl

theorem final_counter (x y : List Bool) :
    (finalConfiguration x y).tapes (4 : Fin 5)=
      BinaryCarryIncrement.homeTape (CarryTape.pass (width x y) (List.replicate (width x y) false)).1 := by
  change (BinaryAutomaticWidthCount.finalConfiguration (sourceWord x y)).tapes (1 : Fin 2)=_
  rw [BinaryAutomaticWidthCount.final_counter]
  simp only [BinaryAutomaticWidthCount.zeroBits,sourceWord_length]
theorem counter_width (x y : List Bool) :
    (CarryTape.pass (width x y) (List.replicate (width x y) false)).1.length=width x y := by
  simpa only [BinaryAutomaticWidthCount.zeroBits,sourceWord_length] using BinaryAutomaticWidthCount.counter_width (sourceWord x y)
theorem counter_value (x y : List Bool) :
    wordValue (CarryTape.pass (width x y) (List.replicate (width x y) false)).1=width x y := by
  simpa only [BinaryAutomaticWidthCount.zeroBits,sourceWord_length] using BinaryAutomaticWidthCount.counter_value (sourceWord x y)

end CurrentMain.BinaryPreparedInputCount
#print axioms CurrentMain.BinaryPreparedInputCount.sourceWord_length
#print axioms CurrentMain.BinaryPreparedInputCount.prepare_count_run
#print axioms CurrentMain.BinaryPreparedInputCount.initial_inputA
#print axioms CurrentMain.BinaryPreparedInputCount.initial_inputB
#print axioms CurrentMain.BinaryPreparedInputCount.initial_pristine
#print axioms CurrentMain.BinaryPreparedInputCount.final_halted
#print axioms CurrentMain.BinaryPreparedInputCount.final_state
#print axioms CurrentMain.BinaryPreparedInputCount.final_inputA
#print axioms CurrentMain.BinaryPreparedInputCount.final_inputB
#print axioms CurrentMain.BinaryPreparedInputCount.final_selected_work
#print axioms CurrentMain.BinaryPreparedInputCount.final_other_work
#print axioms CurrentMain.BinaryPreparedInputCount.final_counter
#print axioms CurrentMain.BinaryPreparedInputCount.counter_width
#print axioms CurrentMain.BinaryPreparedInputCount.counter_value
