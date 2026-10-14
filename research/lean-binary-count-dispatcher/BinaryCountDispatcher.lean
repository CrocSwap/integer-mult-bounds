import BinaryCarryIncrement

/-! A finite symbol-driven controller for a preallocated, marked fixed-width
counter. This supplies the restart-controller boundary left explicit by PR64's
RippleCounter/CounterArithmetic and the local CarryTape pass specification.
The counter arithmetic and increment execution are reused, not reproved.

The seven-state/two-tape table scans an actual input word and dispatches one
increment per bit. Width is tape data, not an instruction argument. The final
input is at its visited right blank; the counter returns to its home blank.
The bound uses the existing pass receipt. Width allocation, amortization,
compact output, source prelude and Plan/Budget are separate obligations. -/
namespace CurrentMain.BinaryCountDispatcher
open FixedTapeMachine

private theorem fin1 (i : Fin 1) : i=0 := by
  exact (show ∀ j : Fin 1, j=0 by decide) i
private theorem fin2 (i : Fin 2) : i=0 ∨ i=1 := by
  exact (show ∀ j : Fin 2, j=0 ∨ j=1 by decide) i
private theorem fin5 (i : Fin 5) : i=0 ∨ i=1 ∨ i=2 ∨ i=3 ∨ i=4 := by
  exact (show ∀ j : Fin 5, j=0 ∨ j=1 ∨ j=2 ∨ j=3 ∨ j=4 by decide) i

def liftState (s : Fin 5) : Fin 7 := ⟨s.val+1, by omega⟩
def readCounter (r : Fin 2 → Symbol) : Fin 1 → Symbol := fun _ => r 1

def stayAction (next : Fin 7) (r : Fin 2 → Symbol) : Action 2 7 :=
  ⟨next,r,fun _ => .stay⟩
def advanceAction (r : Fin 2 → Symbol) : Action 2 7 :=
  ⟨1,r,fun i => if i=0 then .right else .stay⟩
def liftAction (r : Fin 2 → Symbol) (a : Action 1 5) : Action 2 7 where
  state := liftState a.state
  writes := fun i => if i=0 then r 0 else a.writes 0
  moves := fun i => if i=0 then .stay else a.moves 0

/-- Dispatcher0; renamed increment states1..5; terminal6. -/
def machine : Machine where
  tapes := 2
  states := 7
  initial := 0
  transition := fun s r =>
    if h : 1≤s.val ∧ s.val≤5 then
      match BinaryCarryIncrement.machine.transition (⟨s.val-1,by omega⟩ : Fin 5)
          (readCounter r) with
      | some a => some (liftAction r a)
      | none => some (stayAction 0 r)
    else if s.val=0 then
      match r (0 : Fin 2) with
      | .blank => some (stayAction 6 r)
      | .zero | .one => some (advanceAction r)
    else none

def configuration (s : Fin 7) (input counter : Tape) : Configuration machine :=
  ⟨s,fun i => if i=(0 : Fin 2) then input else counter⟩
def embed (c : Configuration BinaryCarryIncrement.machine) (input : Tape) :
    Configuration machine := configuration (liftState c.state) input (c.tapes (0 : Fin 1))

private theorem transition_lift (s : Fin 5) (r : Fin 2 → Symbol) :
    machine.transition (liftState s) r =
      match BinaryCarryIncrement.machine.transition s (readCounter r) with
      | some a => some (liftAction r a)
      | none => some (stayAction 0 r) := by
  rcases fin5 s with rfl|rfl|rfl|rfl|rfl <;> rfl

private theorem reads_embed (c : Configuration BinaryCarryIncrement.machine) (input : Tape) :
    readCounter (fun i : Fin 2 => ((embed c input).tapes i).head) =
      fun j : Fin 1 => (c.tapes j).head := by
  funext j
  rw [fin1 j]
  rfl

/- The next definitional reduction and successful-prefix induction reuse the
accepted BinaryInputPreparation proof bodies verbatim. They avoid reconstructing
concrete dependent matchers and do not assume a first-halting-time theorem. -/
private theorem step_of_transition (m : Machine) (c : Configuration m)
    (a : Action m.tapes m.states)
    (h : m.transition c.state (fun i => (c.tapes i).head) = some a) :
    step m c = some (Configuration.mk a.state
      (fun i => ((c.tapes i).write (a.writes i)).move (a.moves i))) := by
  unfold step
  rw [h]

private theorem step_embed (c d : Configuration BinaryCarryIncrement.machine) (input : Tape)
    (h : step BinaryCarryIncrement.machine c = some d) :
    step machine (embed c input) = some (embed d input) := by
  cases ht : BinaryCarryIncrement.machine.transition c.state (fun i => (c.tapes i).head) with
  | none =>
    simp only [step, ht] at h
    cases h
  | some a =>
    simp only [step, ht, Option.some.injEq] at h
    subst d
    have lifted : BinaryCarryIncrement.machine.transition c.state
        (readCounter (fun i : Fin 2 => ((embed c input).tapes i).head)) = some a :=
      (congrArg (fun reads : Fin 1 → Symbol =>
        BinaryCarryIncrement.machine.transition c.state reads) (reads_embed c input)).trans ht
    have outer : machine.transition (embed c input).state
        (fun i : Fin 2 => ((embed c input).tapes i).head) =
        some (liftAction (fun i : Fin 2 => ((embed c input).tapes i).head) a) :=
      (transition_lift c.state (fun i : Fin 2 => ((embed c input).tapes i).head)).trans
        (congrArg (fun q : Option (Action 1 5) =>
          match q with
          | some a => some (liftAction (fun i : Fin 2 => ((embed c input).tapes i).head) a)
          | none => some (stayAction 0 (fun i : Fin 2 => ((embed c input).tapes i).head))) lifted)
    refine (step_of_transition machine (embed c input) _ outer).trans ?_
    dsimp only [liftAction, embed, configuration]
    apply congrArg some
    apply congrArg (fun tapes : Fin 2 → Tape =>
      (Configuration.mk (liftState a.state) tapes : Configuration machine))
    funext i
    rcases fin2 i with rfl|rfl <;> simp [configuration, Tape.write, Tape.move]

private theorem halt_embed (c : Configuration BinaryCarryIncrement.machine) (input : Tape)
    (h : Halted BinaryCarryIncrement.machine c) :
    step machine (embed c input) = some (configuration 0 input (c.tapes (0 : Fin 1))) := by
  have ht : BinaryCarryIncrement.machine.transition c.state (fun i => (c.tapes i).head) = none := by
    cases he : BinaryCarryIncrement.machine.transition c.state (fun i => (c.tapes i).head) <;>
      simp_all [Halted, step]
  have lifted : BinaryCarryIncrement.machine.transition c.state
      (readCounter (fun i : Fin 2 => ((embed c input).tapes i).head)) = none :=
    (congrArg (fun reads : Fin 1 → Symbol =>
      BinaryCarryIncrement.machine.transition c.state reads) (reads_embed c input)).trans ht
  have outer : machine.transition (embed c input).state
      (fun i : Fin 2 => ((embed c input).tapes i).head) =
      some (stayAction 0 (fun i : Fin 2 => ((embed c input).tapes i).head)) :=
    (transition_lift c.state (fun i : Fin 2 => ((embed c input).tapes i).head)).trans
      (congrArg (fun q : Option (Action 1 5) =>
        match q with
        | some a => some (liftAction (fun i : Fin 2 => ((embed c input).tapes i).head) a)
        | none => some (stayAction 0 (fun i : Fin 2 => ((embed c input).tapes i).head))) lifted)
  refine (step_of_transition machine (embed c input) _ outer).trans ?_
  dsimp only [stayAction, embed, configuration]
  apply congrArg some
  apply congrArg (fun tapes : Fin 2 → Tape => (Configuration.mk (0 : Fin 7) tapes : Configuration machine))
  funext i
  rcases fin2 i with rfl|rfl <;> simp [Tape.write, Tape.move]

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

/-- Scanned input is retained nearest-first on the left; the unread finite word
ends at the first blank. This specifies the entire explicit tape footprint. -/
def inputTape (left : List Symbol) : List Bool → Tape
  | [] => ⟨left,.blank,[]⟩
  | b::rest => ⟨left,bitSymbol b,rest.map bitSymbol⟩

private theorem inputTape_word (word : List Bool) : inputTape [] word=Tape.ofWord word := by
  cases word <;> rfl

private theorem dispatch_step (b : Bool) (rest : List Bool) (left : List Symbol) (bits : List Bool) :
    step machine (configuration 0 (inputTape left (b::rest)) (BinaryCarryIncrement.homeTape bits)) =
      some (embed (BinaryCarryIncrement.initialConfiguration bits)
        (inputTape (bitSymbol b::left) rest)) := by
  have outer : machine.transition (0 : Fin 7)
      (fun i : Fin 2 => ((configuration 0 (inputTape left (b::rest))
        (BinaryCarryIncrement.homeTape bits)).tapes i).head) =
      some (advanceAction (fun i : Fin 2 => ((configuration 0 (inputTape left (b::rest))
        (BinaryCarryIncrement.homeTape bits)).tapes i).head)) := by
    cases b <;> rfl
  refine (step_of_transition machine _ _ outer).trans ?_
  dsimp only [advanceAction, embed, configuration, BinaryCarryIncrement.initialConfiguration,
    BinaryCarryIncrement.configuration, liftState]
  apply congrArg some
  apply congrArg (fun tapes : Fin 2 → Tape => (Configuration.mk (1 : Fin 7) tapes : Configuration machine))
  funext i
  rcases fin2 i with rfl|rfl <;>
    cases rest <;> simp [configuration, inputTape, Tape.write, Tape.move]

private theorem stop_step (left : List Symbol) (bits : List Bool) :
    step machine (configuration 0 (inputTape left []) (BinaryCarryIncrement.homeTape bits)) =
      some (configuration 6 (inputTape left []) (BinaryCarryIncrement.homeTape bits)) := by
  have outer : machine.transition (0 : Fin 7)
      (fun i : Fin 2 => ((configuration 0 (inputTape left [])
        (BinaryCarryIncrement.homeTape bits)).tapes i).head) =
      some (stayAction 6 (fun i : Fin 2 => ((configuration 0 (inputTape left [])
        (BinaryCarryIncrement.homeTape bits)).tapes i).head)) := rfl
  refine (step_of_transition machine _ _ outer).trans ?_
  dsimp only [stayAction, configuration]
  apply congrArg some
  apply congrArg (fun tapes : Fin 2 → Tape => (Configuration.mk (6 : Fin 7) tapes : Configuration machine))
  funext i
  rcases fin2 i with rfl|rfl <;> simp [Tape.write, Tape.move]

private theorem one_increment (bits : List Bool) (input : Tape) :
    ∃ k≤2*CarryTape.trailingOnes bits+4,
      run machine k (embed (BinaryCarryIncrement.initialConfiguration bits) input) =
        embed (BinaryCarryIncrement.finalConfiguration bits) input := by
  have halted : Halted BinaryCarryIncrement.machine
      (run BinaryCarryIncrement.machine (2*CarryTape.trailingOnes bits+4)
        (BinaryCarryIncrement.initialConfiguration bits)) := by
    rw [BinaryCarryIncrement.increment_run]
    exact BinaryCarryIncrement.final_halted bits
  obtain ⟨k,hk,he⟩ := simulate_to_halt BinaryCarryIncrement.machine machine (fun c => embed c input)
    (fun c d h => step_embed c d input h) _ _ halted
  exact ⟨k,hk,by simpa only [BinaryCarryIncrement.increment_run] using he⟩

private theorem loop_run (word : List Bool) (left : List Symbol) (bits : List Bool) :
    ∃ t≤(CarryTape.pass word.length bits).2.reads+2*word.length+1,
      run machine t (configuration 0 (inputTape left word) (BinaryCarryIncrement.homeTape bits)) =
        configuration 6 (inputTape (word.reverse.map bitSymbol++left) [])
          (BinaryCarryIncrement.homeTape (CarryTape.pass word.length bits).1) := by
  induction word generalizing left bits with
  | nil =>
    refine ⟨1,by simp [CarryTape.pass, CarryTape.Receipt.zero],?_⟩
    simpa only [run, stop_step, List.length_nil, CarryTape.pass, List.reverse_nil,
      List.map_nil, List.nil_append] using
      (rfl : configuration (6 : Fin 7) (inputTape left []) (BinaryCarryIncrement.homeTape bits) =
        configuration (6 : Fin 7) (inputTape left []) (BinaryCarryIncrement.homeTape bits))
  | cons b rest ih =>
    let next := inputTape (bitSymbol b::left) rest
    obtain ⟨k,hk,he⟩ := one_increment bits next
    obtain ⟨t,ht,hr⟩ := ih (bitSymbol b::left) (CarryTape.increment bits)
    have bridge : step machine (embed (BinaryCarryIncrement.finalConfiguration bits) next) =
        some (configuration 0 next (BinaryCarryIncrement.homeTape (CarryTape.increment bits))) := by
      simpa only [BinaryCarryIncrement.finalConfiguration, BinaryCarryIncrement.configuration]
        using halt_embed (BinaryCarryIncrement.finalConfiguration bits) next (BinaryCarryIncrement.final_halted bits)
    refine ⟨1+k+1+t,?_,?_⟩
    · simp only [List.length_cons, CarryTape.pass, CarryTape.incrementReceipt, CarryTape.Receipt.add]
      omega
    · rw [run_add machine (1+k+1) t, run_add machine (1+k) 1, run_add machine 1 k]
      simp only [run, dispatch_step]
      rw [he]
      simp only [run, bridge]
      simpa only [List.length_cons, CarryTape.pass, List.reverse_cons, List.map_append,
        List.map_cons, List.map_nil, List.append_assoc, List.singleton_append] using hr

def initialConfiguration (word bits : List Bool) : Configuration machine :=
  configuration 0 (Tape.ofWord word) (BinaryCarryIncrement.homeTape bits)
def finalConfiguration (word bits : List Bool) : Configuration machine :=
  configuration 6 (inputTape (word.reverse.map bitSymbol) [])
    (BinaryCarryIncrement.homeTape (CarryTape.pass word.length bits).1)

/-- Every actual input symbol dispatches one completed increment. The bound
charges the inherited physical receipt plus dispatcher/return/terminal steps. -/
theorem count_run (word bits : List Bool) :
    ∃ t≤(CarryTape.pass word.length bits).2.reads+2*word.length+1,
      run machine t (initialConfiguration word bits)=finalConfiguration word bits := by
  simpa only [initialConfiguration, finalConfiguration, inputTape_word, List.append_nil]
    using loop_run word [] bits

theorem final_halted (word bits : List Bool) : Halted machine (finalConfiguration word bits) := by
  rfl

theorem counter_length (word bits : List Bool) :
    (CarryTape.pass word.length bits).1.length=bits.length := CarryTape.pass_length _ _

theorem counter_value (word bits : List Bool) :
    wordValue (CarryTape.pass word.length bits).1 =
      (wordValue bits+word.length)%2^bits.length := by
  rw [← BinaryCarryIncrement.value_binding, ← BinaryCarryIncrement.value_binding]
  exact CarryTape.pass_value _ _

end CurrentMain.BinaryCountDispatcher
#print axioms CurrentMain.BinaryCountDispatcher.count_run
#print axioms CurrentMain.BinaryCountDispatcher.final_halted
#print axioms CurrentMain.BinaryCountDispatcher.counter_length
#print axioms CurrentMain.BinaryCountDispatcher.counter_value
