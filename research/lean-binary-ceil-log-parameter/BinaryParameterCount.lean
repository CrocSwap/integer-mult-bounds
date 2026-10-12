import BinaryCeilLogTokens
import BinaryCountReceiptAmortization

/-! A concrete fifteen-state/three-tape binary parameter computation. States
0..4 lift the actual lookahead token scan; one tape-preserving halt-interception
step enters states5..14, the accepted automatic-width counting machine. Its
right-blank token input and pristine counter are supplied by the first phase.
The final width-b marked record stores the exact token count, identified with
the least-power ceiling-log parameter on normalized input. The input and token
footprints remain explicit. No compact-b, first-completion, Real.log ceiling,
whole source-caller, remaining parameter setup, Plan or Budget is claimed. -/
namespace CurrentMain.BinaryParameterCount
open FixedTapeMachine
set_option Elab.async false

private theorem fin2 (i : Fin 2) : i=0 ∨ i=1 := by
  exact (show ∀ j : Fin 2, j=0 ∨ j=1 by decide) i
private theorem fin3 (i : Fin 3) : i=0 ∨ i=1 ∨ i=2 := by
  exact (show ∀ j : Fin 3, j=0 ∨ j=1 ∨ j=2 by decide) i

def scanState (s : Fin 5) : Fin 15 := ⟨s.val,by omega⟩
def countState (s : Fin 10) : Fin 15 := ⟨s.val+5,by omega⟩
def scanTape (i : Fin 2) : Fin 3 := ⟨i.val,by omega⟩
def scanReads (r : Fin 3 → Symbol) : Fin 2 → Symbol := fun i => r (scanTape i)
def countReads (r : Fin 3 → Symbol) : Fin 2 → Symbol :=
  fun i => if i=0 then r 1 else r 2

def scanAction (r : Fin 3 → Symbol) (a : Action 2 5) : Action 3 15 where
  state := scanState a.state
  writes := fun i => if h : i.val<2 then a.writes (⟨i.val,h⟩ : Fin 2) else r i
  moves := fun i => if h : i.val<2 then a.moves (⟨i.val,h⟩ : Fin 2) else .stay

def countAction (r : Fin 3 → Symbol) (a : Action 2 10) : Action 3 15 where
  state := countState a.state
  writes := fun i => if i=1 then a.writes 0 else if i=2 then a.writes 1 else r i
  moves := fun i => if i=1 then a.moves 0 else if i=2 then a.moves 1 else .stay

def bridgeAction (r : Fin 3 → Symbol) : Action 3 15 :=
  ⟨countState 0,r,fun _ => .stay⟩
def scanChoice (r : Fin 3 → Symbol) : Option (Action 2 5) → Option (Action 3 15)
  | some a => some (scanAction r a)
  | none => some (bridgeAction r)

def machine : Machine where
  tapes := 3
  states := 15
  initial := 0
  transition := fun s r =>
    if h : s.val<5 then
      scanChoice r (BinaryCeilLogTokens.machine.transition (⟨s.val,h⟩ : Fin 5) (scanReads r))
    else
      (BinaryAutomaticWidthCount.machine.transition (⟨s.val-5,by have := s.isLt; omega⟩ : Fin 10)
        (countReads r)).map (countAction r)

def embedScan (c : Configuration BinaryCeilLogTokens.machine) (extra : Tape) : Configuration machine :=
  ⟨scanState c.state,fun i => if h : i.val<2 then c.tapes (⟨i.val,h⟩ : Fin 2) else extra⟩
def embedCount (c : Configuration BinaryAutomaticWidthCount.machine) (extra : Tape) : Configuration machine :=
  ⟨countState c.state,fun i => if i=(0 : Fin 3) then extra
    else if i=(1 : Fin 3) then c.tapes (0 : Fin 2) else c.tapes (1 : Fin 2)⟩

def parameter (word : List Bool) : Nat := BinaryCeilLogTokens.tokenCount word
def tokenWord (word : List Bool) : List Bool := BinaryCeilLogTokens.tokens word
def counterBits (word : List Bool) : List Bool :=
  (CarryTape.pass (parameter word) (List.replicate (parameter word) false)).1

def initialConfiguration (word : List Bool) : Configuration machine :=
  embedScan (BinaryCeilLogTokens.initialConfiguration word) Tape.blank
def finalConfiguration (word : List Bool) : Configuration machine :=
  embedCount (BinaryAutomaticWidthCount.finalConfiguration (tokenWord word))
    (BinaryCeilLogTokens.endTape (word.reverse.map bitSymbol))

private theorem transition_scan (s : Fin 5) (r : Fin 3 → Symbol) :
    machine.transition (scanState s) r=scanChoice r (BinaryCeilLogTokens.machine.transition s (scanReads r)) := by
  cases s with
  | mk n hn => simp only [machine,scanState,hn,dif_pos]

private theorem transition_count (s : Fin 10) (r : Fin 3 → Symbol) :
    machine.transition (countState s) r=
      (BinaryAutomaticWidthCount.machine.transition s (countReads r)).map (countAction r) := by
  have h : ¬s.val+5<5 := by omega
  simp only [machine,countState,h,dif_neg,dite_false,Nat.add_sub_cancel]

private theorem reads_embedScan (c : Configuration BinaryCeilLogTokens.machine) (extra : Tape) :
    scanReads (fun i : Fin 3 => ((embedScan c extra).tapes i).head)=
      (fun i : Fin 2 => (c.tapes i).head) := by
  funext i
  have hi : i.val<2 := i.isLt
  simp only [scanReads,scanTape,embedScan,hi,dif_pos]

private theorem reads_embedCount (c : Configuration BinaryAutomaticWidthCount.machine) (extra : Tape) :
    countReads (fun i : Fin 3 => ((embedCount c extra).tapes i).head)=
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


private theorem step_scan (c d : Configuration BinaryCeilLogTokens.machine) (extra : Tape)
    (h : step BinaryCeilLogTokens.machine c=some d) :
    step machine (embedScan c extra)=some (embedScan d extra) := by
  cases ht : BinaryCeilLogTokens.machine.transition c.state (fun i => (c.tapes i).head) with
  | none =>
    simp only [step,ht] at h
    cases h
  | some a =>
    simp only [step,ht,Option.some.injEq] at h
    subst d
    let r : Fin 3 → Symbol := fun i => ((embedScan c extra).tapes i).head
    have lifted : BinaryCeilLogTokens.machine.transition c.state (scanReads r)=some a :=
      (congrArg (BinaryCeilLogTokens.machine.transition c.state) (reads_embedScan c extra)).trans ht
    have outer : machine.transition (embedScan c extra).state r=some (scanAction r a) :=
      (transition_scan c.state r).trans (congrArg (scanChoice r) lifted)
    refine (step_of_transition machine (embedScan c extra) (scanAction r a) outer).trans ?_
    dsimp only [scanAction,embedScan]
    apply congrArg some
    apply congrArg (@Configuration.mk machine (scanState a.state))
    funext i
    rcases fin3 i with rfl|rfl|rfl <;> rfl

private theorem step_count (c e : Configuration BinaryAutomaticWidthCount.machine) (extra : Tape)
    (h : step BinaryAutomaticWidthCount.machine c=some e) :
    step machine (embedCount c extra)=some (embedCount e extra) := by
  cases ht : BinaryAutomaticWidthCount.machine.transition c.state (fun i => (c.tapes i).head) with
  | none =>
    simp only [step,ht] at h
    cases h
  | some a =>
    simp only [step,ht,Option.some.injEq] at h
    subst e
    let r : Fin 3 → Symbol := fun i => ((embedCount c extra).tapes i).head
    have lifted : BinaryAutomaticWidthCount.machine.transition c.state (countReads r)=some a :=
      (congrArg (BinaryAutomaticWidthCount.machine.transition c.state) (reads_embedCount c extra)).trans ht
    have outer : machine.transition (embedCount c extra).state r=some (countAction r a) :=
      (transition_count c.state r).trans (congrArg (Option.map (countAction r)) lifted)
    refine (step_of_transition machine (embedCount c extra) (countAction r a) outer).trans ?_
    dsimp only [countAction,embedCount]
    apply congrArg some
    apply congrArg (@Configuration.mk machine (countState a.state))
    funext i
    rcases fin3 i with rfl|rfl|rfl <;> rfl

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


private theorem handoff_configuration (word : List Bool) :
    @Configuration.mk machine (countState (0 : Fin 10))
      (embedScan (BinaryCeilLogTokens.finalConfiguration word) Tape.blank).tapes =
      embedCount (BinaryAutomaticWidthCount.initialConfiguration (tokenWord word))
        (BinaryCeilLogTokens.endTape (word.reverse.map bitSymbol)) := by
  apply congrArg (@Configuration.mk machine (countState (0 : Fin 10)))
  funext i
  rcases fin3 i with rfl|rfl|rfl
  · rfl
  · change BinaryCeilLogTokens.tokenEnd (BinaryCeilLogTokens.tokenCount word)=
      ⟨(tokenWord word).reverse.map bitSymbol,.blank,[]⟩
    simp only [BinaryCeilLogTokens.tokenEnd,BinaryCeilLogTokens.endTape,tokenWord,
      BinaryCeilLogTokens.tokens,List.reverse_replicate,List.map_replicate,bitSymbol,
      Bool.false_eq_true,if_false]
  · rfl

private theorem bridge_handoff (word : List Bool) :
    step machine (embedScan (BinaryCeilLogTokens.finalConfiguration word) Tape.blank)=
      some (embedCount (BinaryAutomaticWidthCount.initialConfiguration (tokenWord word))
        (BinaryCeilLogTokens.endTape (word.reverse.map bitSymbol))) := by
  let c := BinaryCeilLogTokens.finalConfiguration word
  let r : Fin 3 → Symbol := fun i => ((embedScan c Tape.blank).tapes i).head
  have ht : BinaryCeilLogTokens.machine.transition c.state (fun i => (c.tapes i).head)=none := by rfl
  have lifted : BinaryCeilLogTokens.machine.transition c.state (scanReads r)=none :=
    (congrArg (BinaryCeilLogTokens.machine.transition c.state) (reads_embedScan c Tape.blank)).trans ht
  have outer : machine.transition (embedScan c Tape.blank).state r=some (bridgeAction r) :=
    (transition_scan c.state r).trans (congrArg (scanChoice r) lifted)
  have he : step machine (embedScan c Tape.blank)=
      some (@Configuration.mk machine (countState (0 : Fin 10)) (embedScan c Tape.blank).tapes) := by
    refine (step_of_transition machine (embedScan c Tape.blank) (bridgeAction r) outer).trans ?_
    apply congrArg some
    apply congrArg (@Configuration.mk machine (countState (0 : Fin 10)))
    funext i
    rfl
  exact he.trans (congrArg some (handoff_configuration word))

theorem token_length (word : List Bool) : (tokenWord word).length=parameter word := by
  simp only [tokenWord,BinaryCeilLogTokens.tokens,List.length_replicate,parameter]

theorem parameter_bound (word : List Bool) : parameter word≤word.length := by
  cases word with
  | nil => exact Nat.le_refl 0
  | cons b rest =>
    rw [parameter,BinaryCeilLogTokens.token_count_readback,List.length_dropLast_cons,List.length_cons]
    split <;> omega

theorem counter_width (word : List Bool) : (counterBits word).length=parameter word := by
  have h := BinaryAutomaticWidthCount.counter_width (tokenWord word)
  simpa only [counterBits,BinaryAutomaticWidthCount.zeroBits,token_length] using h

theorem counter_value (word : List Bool) : wordValue (counterBits word)=parameter word := by
  have h := BinaryAutomaticWidthCount.counter_value (tokenWord word)
  simpa only [counterBits,BinaryAutomaticWidthCount.zeroBits,token_length] using h

/-- An actual binary token-count record is allocated and populated from the
scan, including empty and single-bit inputs. The record is marked and width-b. -/
theorem parameter_run (word : List Bool) :
    ∃ t≤13*word.length+6, run machine t (initialConfiguration word)=finalConfiguration word := by
  have sr := BinaryCeilLogTokens.tokens_run_exact word
  have sh : Halted BinaryCeilLogTokens.machine
      (run BinaryCeilLogTokens.machine (word.length+1) (BinaryCeilLogTokens.initialConfiguration word)) := by
    rw [sr]
    exact BinaryCeilLogTokens.final_halted word
  obtain ⟨a,ha,harun⟩ := simulate_to_halt BinaryCeilLogTokens.machine machine
    (fun c => embedScan c Tape.blank) (fun c d h => step_scan c d Tape.blank h) _ _ sh
  have haend : run machine a (initialConfiguration word)=
      embedScan (BinaryCeilLogTokens.finalConfiguration word) Tape.blank := by
    simpa only [initialConfiguration,sr] using harun
  have habridge : run machine (a+1) (initialConfiguration word)=
      embedCount (BinaryAutomaticWidthCount.initialConfiguration (tokenWord word))
        (BinaryCeilLogTokens.endTape (word.reverse.map bitSymbol)) := by
    rw [run_add machine a 1,haend]
    simp only [run,bridge_handoff]
  obtain ⟨c,hc,hcrun⟩ := BinaryCountReceiptAmortization.count_run_linear (tokenWord word)
  have ch : Halted BinaryAutomaticWidthCount.machine
      (run BinaryAutomaticWidthCount.machine c
        (BinaryAutomaticWidthCount.initialConfiguration (tokenWord word))) := by
    rw [hcrun]
    exact BinaryAutomaticWidthCount.final_halted _
  obtain ⟨b,hb,hbrun⟩ := simulate_to_halt BinaryAutomaticWidthCount.machine machine
    (fun c => embedCount c (BinaryCeilLogTokens.endTape (word.reverse.map bitSymbol)))
    (fun c d h => step_count c d _ h) _ _ ch
  have hbend : run machine b
      (embedCount (BinaryAutomaticWidthCount.initialConfiguration (tokenWord word))
        (BinaryCeilLogTokens.endTape (word.reverse.map bitSymbol)))=finalConfiguration word := by
    simpa only [hcrun,finalConfiguration] using hbrun
  rw [token_length] at hc
  have hp := parameter_bound word
  refine ⟨a+1+b,by omega,?_⟩
  rw [run_add machine (a+1) b,habridge,hbend]

theorem normalized_parameter (bits : List Bool) :
    wordValue (counterBits (BinaryCounterCompactCopy.compact bits))=
      BinaryCeilLogTokens.ceilLog2 (wordValue bits) := by
  rw [counter_value,parameter,BinaryCeilLogTokens.token_count_ceil_log2]

theorem normalized_le_iff (bits : List Bool) (k : Nat) :
    wordValue (counterBits (BinaryCounterCompactCopy.compact bits))≤k ↔ wordValue bits≤2^k := by
  rw [counter_value,parameter]
  exact BinaryCeilLogTokens.parameter_le_iff bits k

theorem initial_word (word : List Bool) :
    (initialConfiguration word).tapes (0 : Fin 3)=Tape.ofWord word := by rfl
theorem initial_pristine (word : List Bool) :
    (initialConfiguration word).tapes (1 : Fin 3)=Tape.blank ∧
      (initialConfiguration word).tapes (2 : Fin 3)=Tape.blank := by exact ⟨rfl,rfl⟩
theorem final_halted (word : List Bool) : Halted machine (finalConfiguration word) := by rfl
theorem final_state (word : List Bool) : (finalConfiguration word).state=(14 : Fin 15) := by rfl

theorem final_input (word : List Bool) :
    (finalConfiguration word).tapes (0 : Fin 3)=
      BinaryCeilLogTokens.endTape (word.reverse.map bitSymbol) := by rfl

theorem final_tokens (word : List Bool) :
    (finalConfiguration word).tapes (1 : Fin 3)=
      ⟨(tokenWord word).reverse.map bitSymbol++[.blank],.blank,[]⟩ := by
  exact BinaryAutomaticWidthCount.final_input (tokenWord word)

theorem final_counter (word : List Bool) :
    (finalConfiguration word).tapes (2 : Fin 3)=BinaryCarryIncrement.homeTape (counterBits word) := by
  have h := BinaryAutomaticWidthCount.final_counter (tokenWord word)
  simpa only [counterBits,BinaryAutomaticWidthCount.zeroBits,token_length] using h

theorem empty_parameter : parameter []=0 := by rfl
theorem one_parameter : parameter [true]=0 := by rfl

end CurrentMain.BinaryParameterCount
#print axioms CurrentMain.BinaryParameterCount.token_length
#print axioms CurrentMain.BinaryParameterCount.parameter_bound
#print axioms CurrentMain.BinaryParameterCount.counter_width
#print axioms CurrentMain.BinaryParameterCount.counter_value
#print axioms CurrentMain.BinaryParameterCount.parameter_run
#print axioms CurrentMain.BinaryParameterCount.normalized_parameter
#print axioms CurrentMain.BinaryParameterCount.normalized_le_iff
#print axioms CurrentMain.BinaryParameterCount.initial_word
#print axioms CurrentMain.BinaryParameterCount.initial_pristine
#print axioms CurrentMain.BinaryParameterCount.final_halted
#print axioms CurrentMain.BinaryParameterCount.final_state
#print axioms CurrentMain.BinaryParameterCount.final_input
#print axioms CurrentMain.BinaryParameterCount.final_tokens
#print axioms CurrentMain.BinaryParameterCount.final_counter
#print axioms CurrentMain.BinaryParameterCount.empty_parameter
#print axioms CurrentMain.BinaryParameterCount.one_parameter
