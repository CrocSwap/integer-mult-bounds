import BinaryPreparedInputCount
import BinaryCounterCompactValue

/-! Actual six-tape prepared-input/compact-count composition. States0..23 lift
all 24 preparation/count states; an actual missing transition is intercepted by
one tape-preserving bridge to compact state0 at index24. States24..32 copy the
marked-home counter in slot4 to pristine slot5, preserving slots0..3 with their
actual visited footprints. The finite canonical output represents max input
length and has the explicit empty-zero/exact positive log2 length convention.
No first-completion, source zero-digit convention, full caller, Plan or Budget
claim is introduced. -/
namespace CurrentMain.BinaryPreparedCompactCount
open FixedTapeMachine
set_option Elab.async false

private theorem fin2 (i : Fin 2) : i=0 ∨ i=1 := by
  exact (show ∀ j : Fin 2, j=0 ∨ j=1 by decide) i
private theorem fin6 (i : Fin 6) : i=0 ∨ i=1 ∨ i=2 ∨ i=3 ∨ i=4 ∨ i=5 := by
  exact (show ∀ j : Fin 6, j=0 ∨ j=1 ∨ j=2 ∨ j=3 ∨ j=4 ∨ j=5 by decide) i

def prepState (s : Fin 24) : Fin 33 := ⟨s.val,by omega⟩
def copyState (s : Fin 9) : Fin 33 := ⟨s.val+24,by omega⟩
def prepTape (i : Fin 5) : Fin 6 := ⟨i.val,by omega⟩
def prepReads (r : Fin 6 → Symbol) : Fin 5 → Symbol := fun i => r (prepTape i)
def copyReads (r : Fin 6 → Symbol) : Fin 2 → Symbol :=
  fun i => if i=0 then r 4 else r 5

def prepAction (r : Fin 6 → Symbol) (a : Action 5 24) : Action 6 33 where
  state := prepState a.state
  writes := fun i => if h : i.val<5 then a.writes (⟨i.val,h⟩ : Fin 5) else r i
  moves := fun i => if h : i.val<5 then a.moves (⟨i.val,h⟩ : Fin 5) else .stay

def copyAction (r : Fin 6 → Symbol) (a : Action 2 9) : Action 6 33 where
  state := copyState a.state
  writes := fun i => if i=4 then a.writes 0 else if i=5 then a.writes 1 else r i
  moves := fun i => if i=4 then a.moves 0 else if i=5 then a.moves 1 else .stay

def bridgeAction (r : Fin 6 → Symbol) : Action 6 33 :=
  ⟨copyState 0,r,fun _ => .stay⟩
def prepChoice (r : Fin 6 → Symbol) : Option (Action 5 24) → Option (Action 6 33)
  | some a => some (prepAction r a)
  | none => some (bridgeAction r)

def machine : Machine where
  tapes := 6
  states := 33
  initial := 0
  transition := fun s r =>
    if h : s.val<24 then
      prepChoice r (BinaryPreparedInputCount.machine.transition (⟨s.val,h⟩ : Fin 24) (prepReads r))
    else
      (BinaryCounterCompactCopy.machine.transition (⟨s.val-24,by have := s.isLt; omega⟩ : Fin 9)
        (copyReads r)).map (copyAction r)

def embedPrep (c : Configuration BinaryPreparedInputCount.machine) (extra : Tape) : Configuration machine :=
  ⟨prepState c.state,fun i => if h : i.val<5 then c.tapes (⟨i.val,h⟩ : Fin 5) else extra⟩
def embedCopy (c : Configuration BinaryCounterCompactCopy.machine) (spectators : Fin 4 → Tape) : Configuration machine :=
  ⟨copyState c.state,fun i => if h : i.val<4 then spectators (⟨i.val,h⟩ : Fin 4)
    else if i=(4 : Fin 6) then c.tapes (0 : Fin 2) else c.tapes (1 : Fin 2)⟩

def width (x y : List Bool) : Nat := BinaryPreparedInputCount.width x y
def counterBits (x y : List Bool) : List Bool :=
  (CarryTape.pass (width x y) (List.replicate (width x y) false)).1
def outputBits (x y : List Bool) : List Bool := BinaryCounterCompactCopy.compact (counterBits x y)
def spectators (x y : List Bool) : Fin 4 → Tape :=
  fun i => (BinaryPreparedInputCount.finalConfiguration x y).tapes (⟨i.val,by have := i.isLt; omega⟩ : Fin 5)

def initialConfiguration (x y : List Bool) : Configuration machine :=
  embedPrep (BinaryPreparedInputCount.initialConfiguration x y) Tape.blank

def finalConfiguration (x y : List Bool) : Configuration machine :=
  embedCopy (BinaryCounterCompactCopy.finalConfiguration (counterBits x y)) (spectators x y)

private theorem transition_prep (s : Fin 24) (r : Fin 6 → Symbol) :
    machine.transition (prepState s) r=prepChoice r (BinaryPreparedInputCount.machine.transition s (prepReads r)) := by
  cases s with
  | mk n hn => simp only [machine,prepState,hn,dif_pos]

private theorem transition_copy (s : Fin 9) (r : Fin 6 → Symbol) :
    machine.transition (copyState s) r=
      (BinaryCounterCompactCopy.machine.transition s (copyReads r)).map (copyAction r) := by
  have h : ¬s.val+24<24 := by omega
  simp only [machine,copyState,h,dif_neg,dite_false,Nat.add_sub_cancel]

private theorem reads_embedPrep (c : Configuration BinaryPreparedInputCount.machine) (extra : Tape) :
    prepReads (fun i : Fin 6 => ((embedPrep c extra).tapes i).head)=
      (fun i : Fin 5 => (c.tapes i).head) := by
  funext i
  have hi : i.val<5 := i.isLt
  simp only [prepReads,prepTape,embedPrep,hi,dif_pos]

private theorem reads_embedCopy (c : Configuration BinaryCounterCompactCopy.machine) (sp : Fin 4 → Tape) :
    copyReads (fun i : Fin 6 => ((embedCopy c sp).tapes i).head)=
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


private theorem step_prep (c d : Configuration BinaryPreparedInputCount.machine) (extra : Tape)
    (h : step BinaryPreparedInputCount.machine c=some d) :
    step machine (embedPrep c extra)=some (embedPrep d extra) := by
  cases ht : BinaryPreparedInputCount.machine.transition c.state (fun i => (c.tapes i).head) with
  | none =>
    simp only [step,ht] at h
    cases h
  | some a =>
    simp only [step,ht,Option.some.injEq] at h
    subst d
    let r : Fin 6 → Symbol := fun i => ((embedPrep c extra).tapes i).head
    have lifted : BinaryPreparedInputCount.machine.transition c.state (prepReads r)=some a :=
      (congrArg (BinaryPreparedInputCount.machine.transition c.state) (reads_embedPrep c extra)).trans ht
    have outer : machine.transition (embedPrep c extra).state r=some (prepAction r a) :=
      (transition_prep c.state r).trans (congrArg (prepChoice r) lifted)
    refine (step_of_transition machine (embedPrep c extra) (prepAction r a) outer).trans ?_
    dsimp only [prepAction,embedPrep]
    apply congrArg some
    apply congrArg (@Configuration.mk machine (prepState a.state))
    funext i
    rcases fin6 i with rfl|rfl|rfl|rfl|rfl|rfl <;> rfl

private theorem step_copy (c e : Configuration BinaryCounterCompactCopy.machine) (sp : Fin 4 → Tape)
    (h : step BinaryCounterCompactCopy.machine c=some e) :
    step machine (embedCopy c sp)=some (embedCopy e sp) := by
  cases ht : BinaryCounterCompactCopy.machine.transition c.state (fun i => (c.tapes i).head) with
  | none =>
    simp only [step,ht] at h
    cases h
  | some action =>
    simp only [step,ht,Option.some.injEq] at h
    subst e
    let r : Fin 6 → Symbol := fun i => ((embedCopy c sp).tapes i).head
    have lifted : BinaryCounterCompactCopy.machine.transition c.state (copyReads r)=some action :=
      (congrArg (BinaryCounterCompactCopy.machine.transition c.state) (reads_embedCopy c sp)).trans ht
    have outer : machine.transition (embedCopy c sp).state r=some (copyAction r action) :=
      (transition_copy c.state r).trans (congrArg (Option.map (copyAction r)) lifted)
    refine (step_of_transition machine (embedCopy c sp) (copyAction r action) outer).trans ?_
    dsimp only [copyAction,embedCopy]
    apply congrArg some
    apply congrArg (@Configuration.mk machine (copyState action.state))
    funext i
    rcases fin6 i with rfl|rfl|rfl|rfl|rfl|rfl <;> rfl

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
    @Configuration.mk machine (copyState (0 : Fin 9))
      (embedPrep (BinaryPreparedInputCount.finalConfiguration x y) Tape.blank).tapes =
      embedCopy (BinaryCounterCompactCopy.initialConfiguration (counterBits x y)) (spectators x y) := by
  apply congrArg (@Configuration.mk machine (copyState (0 : Fin 9)))
  funext i
  rcases fin6 i with rfl|rfl|rfl|rfl|rfl|rfl
  · rfl
  · rfl
  · rfl
  · rfl
  · change (BinaryPreparedInputCount.finalConfiguration x y).tapes (4 : Fin 5)=
      BinaryCarryIncrement.homeTape (counterBits x y)
    exact BinaryPreparedInputCount.final_counter x y
  · rfl

private theorem bridge_handoff (x y : List Bool) :
    step machine (embedPrep (BinaryPreparedInputCount.finalConfiguration x y) Tape.blank)=
      some (embedCopy (BinaryCounterCompactCopy.initialConfiguration (counterBits x y)) (spectators x y)) := by
  let c := BinaryPreparedInputCount.finalConfiguration x y
  let r : Fin 6 → Symbol := fun i => ((embedPrep c Tape.blank).tapes i).head
  have ht : BinaryPreparedInputCount.machine.transition c.state (fun i => (c.tapes i).head)=none := by rfl
  have lifted : BinaryPreparedInputCount.machine.transition c.state (prepReads r)=none :=
    (congrArg (BinaryPreparedInputCount.machine.transition c.state) (reads_embedPrep c Tape.blank)).trans ht
  have outer : machine.transition (embedPrep c Tape.blank).state r=some (bridgeAction r) :=
    (transition_prep c.state r).trans (congrArg (prepChoice r) lifted)
  have he : step machine (embedPrep c Tape.blank)=
      some (@Configuration.mk machine (copyState (0 : Fin 9)) (embedPrep c Tape.blank).tapes) := by
    refine (step_of_transition machine (embedPrep c Tape.blank) (bridgeAction r) outer).trans ?_
    apply congrArg some
    apply congrArg (@Configuration.mk machine (copyState (0 : Fin 9)))
    funext i
    rfl
  exact he.trans (congrArg some (handoff_configuration x y))

theorem counter_width (x y : List Bool) : (counterBits x y).length=width x y :=
  BinaryPreparedInputCount.counter_width x y

theorem output_value (x y : List Bool) : wordValue (outputBits x y)=width x y := by
  rw [outputBits,BinaryCounterCompactValue.compact_value]
  exact BinaryPreparedInputCount.counter_value x y

theorem output_length (x y : List Bool) :
    (outputBits x y).length=if width x y=0 then 0 else (width x y).log2+1 := by
  rw [outputBits,BinaryCounterCompactValue.compact_length]
  change (if wordValue (counterBits x y)=0 then 0 else (wordValue (counterBits x y)).log2+1)=_
  rw [show wordValue (counterBits x y)=width x y from BinaryPreparedInputCount.counter_value x y]

/-- Actual six-tape composition, including one explicit bridge and pristine output. -/
theorem prepare_compact_run (x y : List Bool) :
    ∃ t≤22*width x y+17, run machine t (initialConfiguration x y)=finalConfiguration x y := by
  obtain ⟨p,hp,hprun⟩ := BinaryPreparedInputCount.prepare_count_run x y
  have ph : Halted BinaryPreparedInputCount.machine
      (run BinaryPreparedInputCount.machine p (BinaryPreparedInputCount.initialConfiguration x y)) := by
    rw [hprun]
    exact BinaryPreparedInputCount.final_halted x y
  obtain ⟨a,ha,harun⟩ := simulate_to_halt BinaryPreparedInputCount.machine machine
    (fun c => embedPrep c Tape.blank) (fun c d h => step_prep c d Tape.blank h) _ _ ph
  have haend : run machine a (initialConfiguration x y)=
      embedPrep (BinaryPreparedInputCount.finalConfiguration x y) Tape.blank := by
    simpa only [initialConfiguration,hprun] using harun
  have habridge : run machine (a+1) (initialConfiguration x y)=
      embedCopy (BinaryCounterCompactCopy.initialConfiguration (counterBits x y)) (spectators x y) := by
    rw [run_add machine a 1,haend]
    simp only [run,bridge_handoff]
  have htrun := BinaryCounterCompactCopy.compact_run_exact (counterBits x y)
  have ht := BinaryCounterCompactCopy.elapsed_bound (counterBits x y)
  have ch : Halted BinaryCounterCompactCopy.machine
      (run BinaryCounterCompactCopy.machine (BinaryCounterCompactCopy.elapsed (counterBits x y))
        (BinaryCounterCompactCopy.initialConfiguration (counterBits x y))) := by
    rw [htrun]
    exact BinaryCounterCompactCopy.final_halted _
  obtain ⟨b,hb,hbrun⟩ := simulate_to_halt BinaryCounterCompactCopy.machine machine
    (fun c => embedCopy c (spectators x y)) (fun c d h => step_copy c d (spectators x y) h) _ _ ch
  have hbend : run machine b
      (embedCopy (BinaryCounterCompactCopy.initialConfiguration (counterBits x y)) (spectators x y))=
      finalConfiguration x y := by
    simpa only [htrun,finalConfiguration] using hbrun
  rw [counter_width] at ht
  change p≤18*width x y+12 at hp
  refine ⟨a+1+b,by omega,?_⟩
  rw [run_add machine (a+1) b,habridge,hbend]

theorem initial_inputA (x y : List Bool) :
    (initialConfiguration x y).tapes (0 : Fin 6)=Tape.ofWord x := by rfl
theorem initial_inputB (x y : List Bool) :
    (initialConfiguration x y).tapes (1 : Fin 6)=Tape.ofWord y := by rfl
theorem initial_pristine (x y : List Bool) :
    (initialConfiguration x y).tapes (2 : Fin 6)=Tape.blank ∧
    (initialConfiguration x y).tapes (3 : Fin 6)=Tape.blank ∧
    (initialConfiguration x y).tapes (4 : Fin 6)=Tape.blank ∧
    (initialConfiguration x y).tapes (5 : Fin 6)=Tape.blank := by exact ⟨rfl,rfl,rfl,rfl⟩

theorem final_halted (x y : List Bool) : Halted machine (finalConfiguration x y) := by rfl
theorem final_state (x y : List Bool) : (finalConfiguration x y).state=(32 : Fin 33) := by rfl

theorem final_inputA (x y : List Bool) :
    (finalConfiguration x y).tapes (0 : Fin 6)=
      BinaryWordReversal.finalInput (BinaryPreparedInputCount.leftPad x y) := by
  exact BinaryPreparedInputCount.final_inputA x y
theorem final_inputB (x y : List Bool) :
    (finalConfiguration x y).tapes (1 : Fin 6)=
      BinaryWordReversal.finalInput (BinaryPreparedInputCount.rightPad x y) := by
  exact BinaryPreparedInputCount.final_inputB x y
theorem final_selected_work (x y : List Bool) :
    (finalConfiguration x y).tapes (2 : Fin 6)=
      ⟨(BinaryPreparedInputCount.leftPad x y).map bitSymbol++[.blank],.blank,[]⟩ := by
  exact BinaryPreparedInputCount.final_selected_work x y
theorem final_other_work (x y : List Bool) :
    (finalConfiguration x y).tapes (3 : Fin 6)=
      BinaryWordReversal.endTape ((BinaryPreparedInputCount.rightPad x y).map bitSymbol) := by
  exact BinaryPreparedInputCount.final_other_work x y
theorem final_counter (x y : List Bool) :
    (finalConfiguration x y).tapes (4 : Fin 6)=
      ⟨[],.blank,(outputBits x y).map bitSymbol++List.replicate (width x y-(outputBits x y).length+1) .blank⟩ := by
  change (BinaryCounterCompactCopy.finalConfiguration (counterBits x y)).tapes (0 : Fin 2)=_
  rw [BinaryCounterCompactCopy.final_counter,counter_width]
  rfl
theorem final_output (x y : List Bool) :
    (finalConfiguration x y).tapes (5 : Fin 6)=Tape.ofWord (outputBits x y) := by rfl

theorem empty_output : (finalConfiguration [] []).tapes (5 : Fin 6)=Tape.blank := by rfl

end CurrentMain.BinaryPreparedCompactCount
#print axioms CurrentMain.BinaryPreparedCompactCount.counter_width
#print axioms CurrentMain.BinaryPreparedCompactCount.output_value
#print axioms CurrentMain.BinaryPreparedCompactCount.output_length
#print axioms CurrentMain.BinaryPreparedCompactCount.prepare_compact_run
#print axioms CurrentMain.BinaryPreparedCompactCount.initial_inputA
#print axioms CurrentMain.BinaryPreparedCompactCount.initial_inputB
#print axioms CurrentMain.BinaryPreparedCompactCount.initial_pristine
#print axioms CurrentMain.BinaryPreparedCompactCount.final_halted
#print axioms CurrentMain.BinaryPreparedCompactCount.final_state
#print axioms CurrentMain.BinaryPreparedCompactCount.final_inputA
#print axioms CurrentMain.BinaryPreparedCompactCount.final_inputB
#print axioms CurrentMain.BinaryPreparedCompactCount.final_selected_work
#print axioms CurrentMain.BinaryPreparedCompactCount.final_other_work
#print axioms CurrentMain.BinaryPreparedCompactCount.final_counter
#print axioms CurrentMain.BinaryPreparedCompactCount.final_output
#print axioms CurrentMain.BinaryPreparedCompactCount.empty_output
