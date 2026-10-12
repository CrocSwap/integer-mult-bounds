import BinaryPreparedCompactCount
import BinaryParameterCount

/-! A literal eight-tape prelude supplying both width n and its binary b record.
States0..32 lift the accepted six-tape prepared/compact-width computation;
one actual halt-interception step enters the accepted fifteen-state parameter
machine at states33..47 on slots5/6/7. Slots6/7 are pristine at that handoff,
and slots0..4 retain their full visited footprints. The canonical n word is
scanned to its right blank; b is a width-b marked record, not a new compact-b
claim. The entry is two finite operand lists. No one-string x#y source caller,
first completion, remaining size setup, Plan, Budget or multiplier is claimed. -/
namespace CurrentMain.BinaryPreparedParameters
open FixedTapeMachine
set_option Elab.async false

private theorem fin3 (i : Fin 3) : i=0 ∨ i=1 ∨ i=2 := by
  exact (show ∀ j : Fin 3, j=0 ∨ j=1 ∨ j=2 by decide) i
private theorem fin8 (i : Fin 8) : i=0 ∨ i=1 ∨ i=2 ∨ i=3 ∨ i=4 ∨ i=5 ∨ i=6 ∨ i=7 := by
  exact (show ∀ j : Fin 8, j=0 ∨ j=1 ∨ j=2 ∨ j=3 ∨ j=4 ∨ j=5 ∨ j=6 ∨ j=7 by decide) i

def prepState (s : Fin 33) : Fin 48 := ⟨s.val,by omega⟩
def parameterState (s : Fin 15) : Fin 48 := ⟨s.val+33,by omega⟩
def prepTape (i : Fin 6) : Fin 8 := ⟨i.val,by omega⟩
def prepReads (r : Fin 8 → Symbol) : Fin 6 → Symbol := fun i => r (prepTape i)
def parameterReads (r : Fin 8 → Symbol) : Fin 3 → Symbol :=
  fun i => if i=0 then r 5 else if i=1 then r 6 else r 7

def prepAction (r : Fin 8 → Symbol) (a : Action 6 33) : Action 8 48 where
  state := prepState a.state
  writes := fun i => if h : i.val<6 then a.writes (⟨i.val,h⟩ : Fin 6) else r i
  moves := fun i => if h : i.val<6 then a.moves (⟨i.val,h⟩ : Fin 6) else .stay

def parameterAction (r : Fin 8 → Symbol) (a : Action 3 15) : Action 8 48 where
  state := parameterState a.state
  writes := fun i => if i=5 then a.writes 0 else if i=6 then a.writes 1 else if i=7 then a.writes 2 else r i
  moves := fun i => if i=5 then a.moves 0 else if i=6 then a.moves 1 else if i=7 then a.moves 2 else .stay

def bridgeAction (r : Fin 8 → Symbol) : Action 8 48 :=
  ⟨parameterState 0,r,fun _ => .stay⟩
def prepChoice (r : Fin 8 → Symbol) : Option (Action 6 33) → Option (Action 8 48)
  | some a => some (prepAction r a)
  | none => some (bridgeAction r)

def machine : Machine where
  tapes := 8
  states := 48
  initial := 0
  transition := fun s r =>
    if h : s.val<33 then
      prepChoice r (BinaryPreparedCompactCount.machine.transition (⟨s.val,h⟩ : Fin 33) (prepReads r))
    else
      (BinaryParameterCount.machine.transition (⟨s.val-33,by have := s.isLt; omega⟩ : Fin 15)
        (parameterReads r)).map (parameterAction r)

def embedPrep (c : Configuration BinaryPreparedCompactCount.machine) (extra : Fin 2 → Tape) : Configuration machine :=
  ⟨prepState c.state,fun i => if h : i.val<6 then c.tapes (⟨i.val,h⟩ : Fin 6)
    else if i=(6 : Fin 8) then extra 0 else extra 1⟩
def embedParameter (c : Configuration BinaryParameterCount.machine) (sp : Fin 5 → Tape) : Configuration machine :=
  ⟨parameterState c.state,fun i => if h : i.val<5 then sp (⟨i.val,h⟩ : Fin 5)
    else if i=(5 : Fin 8) then c.tapes (0 : Fin 3)
    else if i=(6 : Fin 8) then c.tapes (1 : Fin 3) else c.tapes (2 : Fin 3)⟩

def width (x y : List Bool) : Nat := BinaryPreparedCompactCount.width x y
def widthBits (x y : List Bool) : List Bool := BinaryPreparedCompactCount.outputBits x y
def parameterBits (x y : List Bool) : List Bool := BinaryParameterCount.counterBits (widthBits x y)
def spectators (x y : List Bool) : Fin 5 → Tape :=
  fun i => (BinaryPreparedCompactCount.finalConfiguration x y).tapes (⟨i.val,by have := i.isLt; omega⟩ : Fin 6)

def initialConfiguration (x y : List Bool) : Configuration machine :=
  embedPrep (BinaryPreparedCompactCount.initialConfiguration x y) (fun _ => Tape.blank)
def finalConfiguration (x y : List Bool) : Configuration machine :=
  embedParameter (BinaryParameterCount.finalConfiguration (widthBits x y)) (spectators x y)

private theorem transition_prep (s : Fin 33) (r : Fin 8 → Symbol) :
    machine.transition (prepState s) r=prepChoice r (BinaryPreparedCompactCount.machine.transition s (prepReads r)) := by
  cases s with
  | mk n hn => simp only [machine,prepState,hn,dif_pos]

private theorem transition_parameter (s : Fin 15) (r : Fin 8 → Symbol) :
    machine.transition (parameterState s) r=
      (BinaryParameterCount.machine.transition s (parameterReads r)).map (parameterAction r) := by
  have h : ¬s.val+33<33 := by omega
  simp only [machine,parameterState,h,dif_neg,dite_false,Nat.add_sub_cancel]

private theorem reads_embedPrep (c : Configuration BinaryPreparedCompactCount.machine) (extra : Fin 2 → Tape) :
    prepReads (fun i : Fin 8 => ((embedPrep c extra).tapes i).head)=
      (fun i : Fin 6 => (c.tapes i).head) := by
  funext i
  have hi : i.val<6 := i.isLt
  simp only [prepReads,prepTape,embedPrep,hi,dif_pos]

private theorem reads_embedParameter (c : Configuration BinaryParameterCount.machine) (sp : Fin 5 → Tape) :
    parameterReads (fun i : Fin 8 => ((embedParameter c sp).tapes i).head)=
      (fun i : Fin 3 => (c.tapes i).head) := by
  funext i
  rcases fin3 i with rfl|rfl|rfl <;> rfl

private theorem step_of_transition (m : Machine) (c : Configuration m)
    (a : Action m.tapes m.states)
    (h : m.transition c.state (fun i => (c.tapes i).head) = some a) :
    step m c = some (Configuration.mk a.state
      (fun i => ((c.tapes i).write (a.writes i)).move (a.moves i))) := by
  unfold step
  rw [h]


private theorem step_prep (c d : Configuration BinaryPreparedCompactCount.machine) (extra : Fin 2 → Tape)
    (h : step BinaryPreparedCompactCount.machine c=some d) :
    step machine (embedPrep c extra)=some (embedPrep d extra) := by
  cases ht : BinaryPreparedCompactCount.machine.transition c.state (fun i => (c.tapes i).head) with
  | none =>
    simp only [step,ht] at h
    cases h
  | some a =>
    simp only [step,ht,Option.some.injEq] at h
    subst d
    let r : Fin 8 → Symbol := fun i => ((embedPrep c extra).tapes i).head
    have lifted : BinaryPreparedCompactCount.machine.transition c.state (prepReads r)=some a :=
      (congrArg (BinaryPreparedCompactCount.machine.transition c.state) (reads_embedPrep c extra)).trans ht
    have outer : machine.transition (embedPrep c extra).state r=some (prepAction r a) :=
      (transition_prep c.state r).trans (congrArg (prepChoice r) lifted)
    refine (step_of_transition machine (embedPrep c extra) (prepAction r a) outer).trans ?_
    dsimp only [prepAction,embedPrep]
    apply congrArg some
    apply congrArg (@Configuration.mk machine (prepState a.state))
    funext i
    rcases fin8 i with rfl|rfl|rfl|rfl|rfl|rfl|rfl|rfl <;> rfl

private theorem step_parameter (c e : Configuration BinaryParameterCount.machine) (sp : Fin 5 → Tape)
    (h : step BinaryParameterCount.machine c=some e) :
    step machine (embedParameter c sp)=some (embedParameter e sp) := by
  cases ht : BinaryParameterCount.machine.transition c.state (fun i => (c.tapes i).head) with
  | none =>
    simp only [step,ht] at h
    cases h
  | some a =>
    simp only [step,ht,Option.some.injEq] at h
    subst e
    let r : Fin 8 → Symbol := fun i => ((embedParameter c sp).tapes i).head
    have lifted : BinaryParameterCount.machine.transition c.state (parameterReads r)=some a :=
      (congrArg (BinaryParameterCount.machine.transition c.state) (reads_embedParameter c sp)).trans ht
    have outer : machine.transition (embedParameter c sp).state r=some (parameterAction r a) :=
      (transition_parameter c.state r).trans (congrArg (Option.map (parameterAction r)) lifted)
    refine (step_of_transition machine (embedParameter c sp) (parameterAction r a) outer).trans ?_
    dsimp only [parameterAction,embedParameter]
    apply congrArg some
    apply congrArg (@Configuration.mk machine (parameterState a.state))
    funext i
    rcases fin8 i with rfl|rfl|rfl|rfl|rfl|rfl|rfl|rfl <;> rfl

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
    @Configuration.mk machine (parameterState (0 : Fin 15))
      (embedPrep (BinaryPreparedCompactCount.finalConfiguration x y) (fun _ => Tape.blank)).tapes =
      embedParameter (BinaryParameterCount.initialConfiguration (widthBits x y)) (spectators x y) := by
  apply congrArg (@Configuration.mk machine (parameterState (0 : Fin 15)))
  funext i
  rcases fin8 i with rfl|rfl|rfl|rfl|rfl|rfl|rfl|rfl
  · rfl
  · rfl
  · rfl
  · rfl
  · rfl
  · change (BinaryPreparedCompactCount.finalConfiguration x y).tapes (5 : Fin 6)=Tape.ofWord (widthBits x y)
    exact BinaryPreparedCompactCount.final_output x y
  · rfl
  · rfl

private theorem bridge_handoff (x y : List Bool) :
    step machine (embedPrep (BinaryPreparedCompactCount.finalConfiguration x y) (fun _ => Tape.blank))=
      some (embedParameter (BinaryParameterCount.initialConfiguration (widthBits x y)) (spectators x y)) := by
  let c := BinaryPreparedCompactCount.finalConfiguration x y
  let extra : Fin 2 → Tape := fun _ => Tape.blank
  let r : Fin 8 → Symbol := fun i => ((embedPrep c extra).tapes i).head
  have ht : BinaryPreparedCompactCount.machine.transition c.state (fun i => (c.tapes i).head)=none := by rfl
  have lifted : BinaryPreparedCompactCount.machine.transition c.state (prepReads r)=none :=
    (congrArg (BinaryPreparedCompactCount.machine.transition c.state) (reads_embedPrep c extra)).trans ht
  have outer : machine.transition (embedPrep c extra).state r=some (bridgeAction r) :=
    (transition_prep c.state r).trans (congrArg (prepChoice r) lifted)
  have he : step machine (embedPrep c extra)=
      some (@Configuration.mk machine (parameterState (0 : Fin 15)) (embedPrep c extra).tapes) := by
    refine (step_of_transition machine (embedPrep c extra) (bridgeAction r) outer).trans ?_
    apply congrArg some
    apply congrArg (@Configuration.mk machine (parameterState (0 : Fin 15)))
    funext i
    rfl
  exact he.trans (congrArg some (handoff_configuration x y))

theorem width_value (x y : List Bool) : wordValue (widthBits x y)=width x y :=
  BinaryPreparedCompactCount.output_value x y

theorem width_length (x y : List Bool) :
    (widthBits x y).length=if width x y=0 then 0 else (width x y).log2+1 :=
  BinaryPreparedCompactCount.output_length x y

theorem width_length_le (x y : List Bool) : (widthBits x y).length≤width x y := by
  have hl := width_length x y
  by_cases hn : width x y=0
  · rw [if_pos hn] at hl
    omega
  · have hlog : (width x y).log2<width x y := (Nat.log2_lt hn).2 Nat.lt_two_pow_self
    rw [if_neg hn] at hl
    omega

theorem parameter_value (x y : List Bool) :
    wordValue (parameterBits x y)=BinaryCeilLogTokens.ceilLog2 (width x y) := by
  have h := BinaryParameterCount.normalized_parameter (BinaryPreparedCompactCount.counterBits x y)
  have hc : wordValue (BinaryPreparedCompactCount.counterBits x y)=width x y :=
    BinaryPreparedInputCount.counter_value x y
  rw [hc] at h
  exact h

theorem parameter_width (x y : List Bool) :
    (parameterBits x y).length=BinaryCeilLogTokens.ceilLog2 (width x y) := by
  have hl := BinaryParameterCount.counter_width (widthBits x y)
  have hv := BinaryParameterCount.counter_value (widthBits x y)
  have h := parameter_value x y
  change wordValue (BinaryParameterCount.counterBits (widthBits x y))=_ at h
  rw [hv] at h
  exact hl.trans h

/-- The full physical join exposes the actual n-record scan length m. -/
theorem prepare_parameters_run (x y : List Bool) :
    ∃ t≤22*width x y+13*(widthBits x y).length+24,
      run machine t (initialConfiguration x y)=finalConfiguration x y := by
  obtain ⟨p,hp,hprun⟩ := BinaryPreparedCompactCount.prepare_compact_run x y
  have ph : Halted BinaryPreparedCompactCount.machine
      (run BinaryPreparedCompactCount.machine p (BinaryPreparedCompactCount.initialConfiguration x y)) := by
    rw [hprun]
    exact BinaryPreparedCompactCount.final_halted x y
  obtain ⟨a,ha,harun⟩ := simulate_to_halt BinaryPreparedCompactCount.machine machine
    (fun c => embedPrep c (fun _ => Tape.blank)) (fun c d h => step_prep c d _ h) _ _ ph
  have haend : run machine a (initialConfiguration x y)=
      embedPrep (BinaryPreparedCompactCount.finalConfiguration x y) (fun _ => Tape.blank) := by
    simpa only [initialConfiguration,hprun] using harun
  have habridge : run machine (a+1) (initialConfiguration x y)=
      embedParameter (BinaryParameterCount.initialConfiguration (widthBits x y)) (spectators x y) := by
    rw [run_add machine a 1,haend]
    simp only [run,bridge_handoff]
  obtain ⟨c,hc,hcrun⟩ := BinaryParameterCount.parameter_run (widthBits x y)
  have ch : Halted BinaryParameterCount.machine
      (run BinaryParameterCount.machine c (BinaryParameterCount.initialConfiguration (widthBits x y))) := by
    rw [hcrun]
    exact BinaryParameterCount.final_halted _
  obtain ⟨b,hb,hbrun⟩ := simulate_to_halt BinaryParameterCount.machine machine
    (fun c => embedParameter c (spectators x y)) (fun c d h => step_parameter c d _ h) _ _ ch
  have hbend : run machine b
      (embedParameter (BinaryParameterCount.initialConfiguration (widthBits x y)) (spectators x y))=
      finalConfiguration x y := by
    simpa only [hcrun,finalConfiguration] using hbrun
  change p≤22*width x y+17 at hp
  refine ⟨a+1+b,by omega,?_⟩
  rw [run_add machine (a+1) b,habridge,hbend]

theorem prepare_parameters_run_linear (x y : List Bool) :
    ∃ t≤35*width x y+24, run machine t (initialConfiguration x y)=finalConfiguration x y := by
  obtain ⟨t,ht,hr⟩ := prepare_parameters_run x y
  have h := width_length_le x y
  exact ⟨t,by omega,hr⟩

theorem initial_inputA (x y : List Bool) : (initialConfiguration x y).tapes (0 : Fin 8)=Tape.ofWord x := by rfl
theorem initial_inputB (x y : List Bool) : (initialConfiguration x y).tapes (1 : Fin 8)=Tape.ofWord y := by rfl
theorem initial_pristine (x y : List Bool) :
    (initialConfiguration x y).tapes (2 : Fin 8)=Tape.blank ∧
    (initialConfiguration x y).tapes (3 : Fin 8)=Tape.blank ∧
    (initialConfiguration x y).tapes (4 : Fin 8)=Tape.blank ∧
    (initialConfiguration x y).tapes (5 : Fin 8)=Tape.blank ∧
    (initialConfiguration x y).tapes (6 : Fin 8)=Tape.blank ∧
    (initialConfiguration x y).tapes (7 : Fin 8)=Tape.blank := by exact ⟨rfl,rfl,rfl,rfl,rfl,rfl⟩
theorem final_halted (x y : List Bool) : Halted machine (finalConfiguration x y) := by rfl
theorem final_state (x y : List Bool) : (finalConfiguration x y).state=(47 : Fin 48) := by rfl

theorem final_inputA (x y : List Bool) :
    (finalConfiguration x y).tapes (0 : Fin 8)=
      BinaryWordReversal.finalInput (BinaryPreparedInputCount.leftPad x y) :=
  BinaryPreparedCompactCount.final_inputA x y
theorem final_inputB (x y : List Bool) :
    (finalConfiguration x y).tapes (1 : Fin 8)=
      BinaryWordReversal.finalInput (BinaryPreparedInputCount.rightPad x y) :=
  BinaryPreparedCompactCount.final_inputB x y
theorem final_selected_work (x y : List Bool) :
    (finalConfiguration x y).tapes (2 : Fin 8)=
      ⟨(BinaryPreparedInputCount.leftPad x y).map bitSymbol++[.blank],.blank,[]⟩ :=
  BinaryPreparedCompactCount.final_selected_work x y
theorem final_other_work (x y : List Bool) :
    (finalConfiguration x y).tapes (3 : Fin 8)=
      BinaryWordReversal.endTape ((BinaryPreparedInputCount.rightPad x y).map bitSymbol) :=
  BinaryPreparedCompactCount.final_other_work x y
theorem final_old_counter (x y : List Bool) :
    (finalConfiguration x y).tapes (4 : Fin 8)=
      ⟨[],.blank,(widthBits x y).map bitSymbol++List.replicate (width x y-(widthBits x y).length+1) .blank⟩ :=
  BinaryPreparedCompactCount.final_counter x y

theorem final_width_record (x y : List Bool) :
    (finalConfiguration x y).tapes (5 : Fin 8)=
      BinaryCeilLogTokens.endTape ((widthBits x y).reverse.map bitSymbol) :=
  BinaryParameterCount.final_input (widthBits x y)
theorem final_tokens (x y : List Bool) :
    (finalConfiguration x y).tapes (6 : Fin 8)=
      ⟨(BinaryParameterCount.tokenWord (widthBits x y)).reverse.map bitSymbol++[.blank],.blank,[]⟩ :=
  BinaryParameterCount.final_tokens (widthBits x y)
theorem final_parameter (x y : List Bool) :
    (finalConfiguration x y).tapes (7 : Fin 8)=BinaryCarryIncrement.homeTape (parameterBits x y) :=
  BinaryParameterCount.final_counter (widthBits x y)

theorem empty_width_record : widthBits [] []=[] := by rfl
theorem empty_parameter : parameterBits [] []=[] := by rfl

end CurrentMain.BinaryPreparedParameters
#print axioms CurrentMain.BinaryPreparedParameters.width_value
#print axioms CurrentMain.BinaryPreparedParameters.width_length
#print axioms CurrentMain.BinaryPreparedParameters.width_length_le
#print axioms CurrentMain.BinaryPreparedParameters.parameter_value
#print axioms CurrentMain.BinaryPreparedParameters.parameter_width
#print axioms CurrentMain.BinaryPreparedParameters.prepare_parameters_run
#print axioms CurrentMain.BinaryPreparedParameters.prepare_parameters_run_linear
#print axioms CurrentMain.BinaryPreparedParameters.initial_inputA
#print axioms CurrentMain.BinaryPreparedParameters.initial_inputB
#print axioms CurrentMain.BinaryPreparedParameters.initial_pristine
#print axioms CurrentMain.BinaryPreparedParameters.final_halted
#print axioms CurrentMain.BinaryPreparedParameters.final_state
#print axioms CurrentMain.BinaryPreparedParameters.final_inputA
#print axioms CurrentMain.BinaryPreparedParameters.final_inputB
#print axioms CurrentMain.BinaryPreparedParameters.final_selected_work
#print axioms CurrentMain.BinaryPreparedParameters.final_other_work
#print axioms CurrentMain.BinaryPreparedParameters.final_old_counter
#print axioms CurrentMain.BinaryPreparedParameters.final_width_record
#print axioms CurrentMain.BinaryPreparedParameters.final_tokens
#print axioms CurrentMain.BinaryPreparedParameters.final_parameter
#print axioms CurrentMain.BinaryPreparedParameters.empty_width_record
#print axioms CurrentMain.BinaryPreparedParameters.empty_parameter
