import BinaryCounterZeroAllocation

/-! Concrete allocation/count sequencing on the same two tapes. Global states
0..2 are the allocator's active states;3..9 are the dispatcher's seven states.
The shared state3 needs no extra bridge transition. Actual successful-prefix
simulation reuses both accepted run theorems without a first-completion premise.
The counter starts pristine, is physically allocated from the word, and stores
its exact length. The cost is still the inherited pass receipt plus4n+4;
PR64 amortized transport, compact output, input4 control and Plan/Budget remain
separate. No new capacity or list-arithmetic induction is introduced. -/
namespace CurrentMain.BinaryAutomaticWidthCount
open FixedTapeMachine

private theorem fin4 (i : Fin 4) : i=0 ∨ i=1 ∨ i=2 ∨ i=3 := by
  exact (show ∀ j : Fin 4, j=0 ∨ j=1 ∨ j=2 ∨ j=3 by decide) i
private theorem fin7 (i : Fin 7) : i=0 ∨ i=1 ∨ i=2 ∨ i=3 ∨ i=4 ∨ i=5 ∨ i=6 := by
  exact (show ∀ j : Fin 7, j=0 ∨ j=1 ∨ j=2 ∨ j=3 ∨ j=4 ∨ j=5 ∨ j=6 by decide) i

def allocationState (s : Fin 4) : Fin 10 := ⟨s.val,by omega⟩
def countState (s : Fin 7) : Fin 10 := ⟨s.val+3,by omega⟩
def allocationAction (a : Action 2 4) : Action 2 10 :=
  ⟨allocationState a.state,a.writes,a.moves⟩
def countAction (a : Action 2 7) : Action 2 10 :=
  ⟨countState a.state,a.writes,a.moves⟩

def machine : Machine where
  tapes := 2
  states := 10
  initial := 0
  transition := fun s r =>
    if h : s.val<3 then
      (BinaryCounterZeroAllocation.machine.transition (⟨s.val,by omega⟩ : Fin 4) r).map allocationAction
    else
      (BinaryCountDispatcher.machine.transition (⟨s.val-3,by omega⟩ : Fin 7) r).map countAction

def embedAllocation (c : Configuration BinaryCounterZeroAllocation.machine) : Configuration machine :=
  ⟨allocationState c.state,c.tapes⟩
def embedCount (c : Configuration BinaryCountDispatcher.machine) : Configuration machine :=
  ⟨countState c.state,c.tapes⟩

def zeroBits (word : List Bool) : List Bool := List.replicate word.length false

def initialConfiguration (word : List Bool) : Configuration machine :=
  embedAllocation (BinaryCounterZeroAllocation.initialConfiguration word)
def finalConfiguration (word : List Bool) : Configuration machine :=
  embedCount (BinaryCountDispatcherMarkedInput.finalConfiguration word (zeroBits word))

private theorem allocation_live (s : Fin 4) (r : Fin 2 → Symbol) (a : Action 2 4)
    (h : BinaryCounterZeroAllocation.machine.transition s r=some a) : s.val<3 := by
  rcases fin4 s with rfl|rfl|rfl|rfl
  · decide
  · decide
  · decide
  · have hn : (none : Option (Action 2 4))=some a := h
    cases hn

private theorem transition_allocation (s : Fin 4) (r : Fin 2 → Symbol) (hs : s.val<3) :
    machine.transition (allocationState s) r=
      (BinaryCounterZeroAllocation.machine.transition s r).map allocationAction := by
  rcases fin4 s with rfl|rfl|rfl|rfl
  · rfl
  · rfl
  · rfl
  · omega

private theorem transition_count (s : Fin 7) (r : Fin 2 → Symbol) :
    machine.transition (countState s) r=
      (BinaryCountDispatcher.machine.transition s r).map countAction := by
  rcases fin7 s with rfl|rfl|rfl|rfl|rfl|rfl|rfl <;> rfl

/- Both private generic helpers are reused byte-for-byte from the accepted
actual-symbol dispatcher. Their hypotheses are discharged by the tables here. -/
private theorem step_of_transition (m : Machine) (c : Configuration m)
    (a : Action m.tapes m.states)
    (h : m.transition c.state (fun i => (c.tapes i).head) = some a) :
    step m c = some (Configuration.mk a.state
      (fun i => ((c.tapes i).write (a.writes i)).move (a.moves i))) := by
  unfold step
  rw [h]

private theorem step_allocation (c d : Configuration BinaryCounterZeroAllocation.machine)
    (h : step BinaryCounterZeroAllocation.machine c=some d) :
    step machine (embedAllocation c)=some (embedAllocation d) := by
  cases ht : BinaryCounterZeroAllocation.machine.transition c.state (fun i => (c.tapes i).head) with
  | none =>
    simp only [step,ht] at h
    cases h
  | some a =>
    simp only [step,ht,Option.some.injEq] at h
    subst d
    have hs := allocation_live c.state (fun i => (c.tapes i).head) a ht
    have outer : machine.transition (embedAllocation c).state
        (fun i : Fin 2 => ((embedAllocation c).tapes i).head)=some (allocationAction a) :=
      (transition_allocation c.state (fun i => (c.tapes i).head) hs).trans
        (congrArg (Option.map allocationAction) ht)
    refine (step_of_transition machine (embedAllocation c) (allocationAction a) outer).trans ?_
    rfl

private theorem step_count (c d : Configuration BinaryCountDispatcher.machine)
    (h : step BinaryCountDispatcher.machine c=some d) :
    step machine (embedCount c)=some (embedCount d) := by
  cases ht : BinaryCountDispatcher.machine.transition c.state (fun i => (c.tapes i).head) with
  | none =>
    simp only [step,ht] at h
    cases h
  | some a =>
    simp only [step,ht,Option.some.injEq] at h
    subst d
    have outer : machine.transition (embedCount c).state
        (fun i : Fin 2 => ((embedCount c).tapes i).head)=some (countAction a) :=
      (transition_count c.state (fun i => (c.tapes i).head)).trans
        (congrArg (Option.map countAction) ht)
    refine (step_of_transition machine (embedCount c) (countAction a) outer).trans ?_
    rfl

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

private theorem handoff (word : List Bool) :
    embedAllocation (BinaryCounterZeroAllocation.finalConfiguration word)=
      embedCount (BinaryCountDispatcherMarkedInput.initialConfiguration word (zeroBits word)) := by
  rfl

/-- The actual machine supplies the counter width before counting. Its cost is
an inherited physical pass receipt plus the allocation/controller overhead. -/
theorem count_run (word : List Bool) :
    ∃ t≤(CarryTape.pass word.length (zeroBits word)).2.reads+4*word.length+4,
      run machine t (initialConfiguration word)=finalConfiguration word := by
  have ah : Halted BinaryCounterZeroAllocation.machine
      (run BinaryCounterZeroAllocation.machine (2*word.length+3)
        (BinaryCounterZeroAllocation.initialConfiguration word)) := by
    rw [BinaryCounterZeroAllocation.allocate_run_exact]
    exact BinaryCounterZeroAllocation.final_halted word
  obtain ⟨a,ha,harun⟩ := simulate_to_halt BinaryCounterZeroAllocation.machine machine embedAllocation
    (fun c d h => step_allocation c d h) _ _ ah
  have haend : run machine a (initialConfiguration word)=
      embedAllocation (BinaryCounterZeroAllocation.finalConfiguration word) := by
    simpa only [initialConfiguration,BinaryCounterZeroAllocation.allocate_run_exact] using harun
  obtain ⟨t,ht,htrun⟩ := BinaryCountDispatcherMarkedInput.count_run word (zeroBits word)
  have ch : Halted BinaryCountDispatcher.machine
      (run BinaryCountDispatcher.machine t
        (BinaryCountDispatcherMarkedInput.initialConfiguration word (zeroBits word))) := by
    rw [htrun]
    exact BinaryCountDispatcherMarkedInput.final_halted word (zeroBits word)
  obtain ⟨c,hc,hcrun⟩ := simulate_to_halt BinaryCountDispatcher.machine machine embedCount
    (fun c d h => step_count c d h) _ _ ch
  have hcend : run machine c
      (embedCount (BinaryCountDispatcherMarkedInput.initialConfiguration word (zeroBits word)))=
      finalConfiguration word := by
    simpa only [htrun,finalConfiguration] using hcrun
  refine ⟨a+c,by omega,?_⟩
  rw [run_add machine a c,haend,handoff,hcend]

theorem final_halted (word : List Bool) : Halted machine (finalConfiguration word) := by
  rfl

theorem final_input (word : List Bool) :
    (finalConfiguration word).tapes (0 : Fin 2)=
      ⟨word.reverse.map bitSymbol++[.blank],.blank,[]⟩ := by
  rfl

theorem final_counter (word : List Bool) :
    (finalConfiguration word).tapes (1 : Fin 2)=
      BinaryCarryIncrement.homeTape (CarryTape.pass word.length (zeroBits word)).1 := by
  rfl

private theorem zero_value (word : List Bool) : wordValue (zeroBits word)=0 := by
  have h := IntegerConvolution.value_map_mul 2 0 (List.replicate word.length 0)
  change IntegerConvolution.value 2 ((zeroBits word).map (fun b => if b then 1 else 0))=0
  simpa only [zeroBits,List.map_replicate,Bool.false_eq_true,if_false,Nat.zero_mul] using h

theorem counter_width (word : List Bool) :
    (CarryTape.pass word.length (zeroBits word)).1.length=word.length :=
  (BinaryCountDispatcherMarkedInput.counter_length word (zeroBits word)).trans List.length_replicate

/-- The stored count is the actual input length, without a supplied capacity
premise. Existing core modular arithmetic also covers the empty input. -/
theorem counter_value (word : List Bool) :
    wordValue (CarryTape.pass word.length (zeroBits word)).1=word.length := by
  rw [BinaryCountDispatcherMarkedInput.counter_value,zero_value]
  simp only [Nat.zero_add,zeroBits,List.length_replicate,Nat.mod_two_pow_self]

end CurrentMain.BinaryAutomaticWidthCount
#print axioms CurrentMain.BinaryAutomaticWidthCount.count_run
#print axioms CurrentMain.BinaryAutomaticWidthCount.final_halted
#print axioms CurrentMain.BinaryAutomaticWidthCount.final_input
#print axioms CurrentMain.BinaryAutomaticWidthCount.final_counter
#print axioms CurrentMain.BinaryAutomaticWidthCount.counter_width
#print axioms CurrentMain.BinaryAutomaticWidthCount.counter_value
