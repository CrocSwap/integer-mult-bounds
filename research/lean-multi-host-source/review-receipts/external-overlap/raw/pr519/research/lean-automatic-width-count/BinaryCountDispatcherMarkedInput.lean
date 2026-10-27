import BinaryCountDispatcher

/-! An exact invocation adapter for the accepted dispatcher on a represented
home blank and terminal blank. The machine, counter arithmetic and count proof
are reused. This module changes only the input representation at invocation.
The private simulation is restricted to finite unread Boolean words, so a
blank head with an arbitrary nonempty right list is never silently identified
with a terminal blank. Allocation, the input4 tape choice, amortization and the
source caller/Plan remain separate obligations. -/
namespace CurrentMain.BinaryCountDispatcherMarkedInput
open FixedTapeMachine

private theorem fin2 (i : Fin 2) : i=0 ∨ i=1 := by
  exact (show ∀ j : Fin 2, j=0 ∨ j=1 by decide) i

/-- Both boundary cells are represented. For empty input the two blanks are
already the left home cell and the current terminal cell. -/
def inputTape : List Bool → Tape
  | [] => ⟨[.blank],.blank,[]⟩
  | b::rest => ⟨[.blank],bitSymbol b,rest.map bitSymbol++[.blank]⟩

def initialConfiguration (word bits : List Bool) :
    Configuration BinaryCountDispatcher.machine :=
  BinaryCountDispatcher.configuration 0 (inputTape word) (BinaryCarryIncrement.homeTape bits)

def finalConfiguration (word bits : List Bool) :
    Configuration BinaryCountDispatcher.machine :=
  BinaryCountDispatcher.configuration 6
    ⟨word.reverse.map bitSymbol++[.blank],.blank,[]⟩
    (BinaryCarryIncrement.homeTape (CarryTape.pass word.length bits).1)

private def markTape (t : Tape) : Tape :=
  ⟨t.left++[.blank],t.head,
    match t.head with
    | .blank => []
    | .zero | .one => t.right++[.blank]⟩

private def mark (c : Configuration BinaryCountDispatcher.machine) :
    Configuration BinaryCountDispatcher.machine :=
  ⟨c.state,fun i => if i=(0 : Fin 2) then markTape (c.tapes i) else c.tapes i⟩

private def WordInput (c : Configuration BinaryCountDispatcher.machine) : Prop :=
  ∃ left word, c.tapes (0 : Fin 2)=BinaryCountDispatcher.inputTape left word

private theorem reads_mark (c : Configuration BinaryCountDispatcher.machine) :
    (fun i : Fin 2 => ((mark c).tapes i).head) = fun i => (c.tapes i).head := by
  funext i
  rcases fin2 i with rfl|rfl <;> simp [mark,markTape]

/- This is a read-only consequence of the accepted transition table. Every
successful transition preserves the input symbol and either stays, or moves
right from a bit. No arbitrary instruction contract is assumed. -/
private theorem input_action (s : Fin 7) (r : Fin 2 → Symbol) (a : Action 2 7)
    (h : BinaryCountDispatcher.machine.transition s r=some a) :
    a.writes (0 : Fin 2)=r 0 ∧
      (a.moves (0 : Fin 2)=.stay ∨ (a.moves (0 : Fin 2)=.right ∧ r 0≠.blank)) := by
  dsimp only [BinaryCountDispatcher.machine] at h
  split at h
  · split at h <;> cases h <;>
      simp [BinaryCountDispatcher.liftAction,BinaryCountDispatcher.stayAction]
  · split at h
    · cases hr : r (0 : Fin 2) <;> simp only [hr] at h <;> cases h <;>
        simp [BinaryCountDispatcher.stayAction,BinaryCountDispatcher.advanceAction,hr]
    · cases h

private theorem tape_update (left : List Symbol) (word : List Bool) (d : Move)
    (hd : d=.stay ∨ (d=.right ∧ (BinaryCountDispatcher.inputTape left word).head≠.blank)) :
    markTape (((BinaryCountDispatcher.inputTape left word).write
        (BinaryCountDispatcher.inputTape left word).head).move d) =
      ((markTape (BinaryCountDispatcher.inputTape left word)).write
        (BinaryCountDispatcher.inputTape left word).head).move d ∧
    ∃ left' word', ((BinaryCountDispatcher.inputTape left word).write
        (BinaryCountDispatcher.inputTape left word).head).move d =
      BinaryCountDispatcher.inputTape left' word' := by
  rcases hd with rfl|⟨rfl,hbit⟩
  · constructor
    · cases word with
      | nil => rfl
      | cons b rest => cases b <;> rfl
    · exact ⟨left,word,by cases word <;> rfl⟩
  · cases word with
    | nil => exact False.elim (hbit rfl)
    | cons b rest =>
      constructor
      · cases rest with
        | nil => cases b <;> rfl
        | cons next rest => cases b <;> cases next <;> rfl
      · exact ⟨bitSymbol b::left,rest,by cases rest <;> rfl⟩

/- Reuse the abstract definitional step reduction, avoiding a reconstructed
concrete dependent Option matcher. -/
private theorem step_of_transition (m : Machine) (c : Configuration m)
    (a : Action m.tapes m.states)
    (h : m.transition c.state (fun i => (c.tapes i).head) = some a) :
    step m c = some (Configuration.mk a.state
      (fun i => ((c.tapes i).write (a.writes i)).move (a.moves i))) := by
  unfold step
  rw [h]

private theorem step_none_of_transition (m : Machine) (c : Configuration m)
    (h : m.transition c.state (fun i => (c.tapes i).head)=none) :
    step m c=none := by
  unfold step
  rw [h]

private theorem step_mark (c d : Configuration BinaryCountDispatcher.machine)
    (hc : WordInput c) (h : step BinaryCountDispatcher.machine c=some d) :
    step BinaryCountDispatcher.machine (mark c)=some (mark d) ∧ WordInput d := by
  obtain ⟨left,word,hi⟩ := hc
  cases ht : BinaryCountDispatcher.machine.transition c.state (fun i => (c.tapes i).head) with
  | none =>
    simp only [step,ht] at h
    cases h
  | some a =>
    simp only [step,ht,Option.some.injEq] at h
    subst d
    obtain ⟨hw,hm⟩ := input_action c.state (fun i => (c.tapes i).head) a ht
    have hu := tape_update left word (a.moves (0 : Fin 2))
      (by simpa only [hi] using hm)
    constructor
    · have outer : BinaryCountDispatcher.machine.transition (mark c).state
          (fun i : Fin 2 => ((mark c).tapes i).head)=some a :=
        (congrArg (BinaryCountDispatcher.machine.transition c.state) (reads_mark c)).trans ht
      refine (step_of_transition BinaryCountDispatcher.machine (mark c) a outer).trans ?_
      dsimp only [mark]
      apply congrArg some
      apply congrArg (fun tapes : Fin 2 → Tape =>
        (Configuration.mk a.state tapes : Configuration BinaryCountDispatcher.machine))
      funext i
      rcases fin2 i with rfl|rfl
      · simp only [if_pos rfl]
        rw [hw,hi]
        exact hu.1.symm
      · simp only [show (1 : Fin 2)≠0 by decide,if_neg,if_false]
    · change ∃ left' word', ((c.tapes (0 : Fin 2)).write (a.writes (0 : Fin 2))).move (a.moves (0 : Fin 2))=
        BinaryCountDispatcher.inputTape left' word'
      simpa only [hw,hi] using hu.2

private theorem none_mark (c : Configuration BinaryCountDispatcher.machine)
    (h : step BinaryCountDispatcher.machine c=none) :
    step BinaryCountDispatcher.machine (mark c)=none := by
  have ht : BinaryCountDispatcher.machine.transition c.state (fun i => (c.tapes i).head)=none := by
    cases he : BinaryCountDispatcher.machine.transition c.state (fun i => (c.tapes i).head) <;>
      simp_all [step]
  exact step_none_of_transition BinaryCountDispatcher.machine (mark c)
    ((congrArg (BinaryCountDispatcher.machine.transition c.state) (reads_mark c)).trans ht)

private theorem run_mark (t : Nat) (c : Configuration BinaryCountDispatcher.machine)
    (hc : WordInput c) :
    run BinaryCountDispatcher.machine t (mark c)=mark (run BinaryCountDispatcher.machine t c) ∧
      WordInput (run BinaryCountDispatcher.machine t c) := by
  induction t generalizing c with
  | zero => exact ⟨rfl,hc⟩
  | succ t ih =>
    cases hs : step BinaryCountDispatcher.machine c with
    | none =>
      simp only [run,hs,none_mark c hs]
      exact ⟨True.intro,hc⟩
    | some d =>
      obtain ⟨hd,hw⟩ := step_mark c d hc hs
      simpa only [run,hs,hd] using ih d hw

private theorem mark_configuration (s : Fin 7) (input counter : Tape) :
    mark (BinaryCountDispatcher.configuration s input counter)=
      BinaryCountDispatcher.configuration s (markTape input) counter := by
  dsimp only [mark,BinaryCountDispatcher.configuration]
  apply congrArg (fun tapes : Fin 2 → Tape =>
    (Configuration.mk s tapes : Configuration BinaryCountDispatcher.machine))
  funext i
  rcases fin2 i with rfl|rfl <;> simp

private theorem mark_initial (word bits : List Bool) :
    mark (BinaryCountDispatcher.initialConfiguration word bits)=initialConfiguration word bits := by
  unfold BinaryCountDispatcher.initialConfiguration initialConfiguration
  rw [mark_configuration]
  cases word with
  | nil => rfl
  | cons b rest => cases b <;> rfl

private theorem mark_final (word bits : List Bool) :
    mark (BinaryCountDispatcher.finalConfiguration word bits)=finalConfiguration word bits := by
  unfold BinaryCountDispatcher.finalConfiguration finalConfiguration
  rw [mark_configuration]
  rfl

/-- The accepted same-machine count theorem transports to the exact marked
input footprint. No allocation or caller-domain hypothesis is added. -/
theorem count_run (word bits : List Bool) :
    ∃ t≤(CarryTape.pass word.length bits).2.reads+2*word.length+1,
      run BinaryCountDispatcher.machine t (initialConfiguration word bits)=finalConfiguration word bits := by
  obtain ⟨t,ht,he⟩ := BinaryCountDispatcher.count_run word bits
  have hw : WordInput (BinaryCountDispatcher.initialConfiguration word bits) := by
    refine ⟨[],word,?_⟩
    cases word <;> rfl
  refine ⟨t,ht,?_⟩
  have transport := (run_mark t (BinaryCountDispatcher.initialConfiguration word bits) hw).1
  simpa only [mark_initial,he,mark_final] using transport

theorem final_halted (word bits : List Bool) :
    Halted BinaryCountDispatcher.machine (finalConfiguration word bits) := by
  rw [← mark_final]
  exact none_mark _ (BinaryCountDispatcher.final_halted word bits)

theorem counter_length (word bits : List Bool) :
    (CarryTape.pass word.length bits).1.length=bits.length :=
  BinaryCountDispatcher.counter_length word bits

theorem counter_value (word bits : List Bool) :
    wordValue (CarryTape.pass word.length bits).1 =
      (wordValue bits+word.length)%2^bits.length :=
  BinaryCountDispatcher.counter_value word bits

end CurrentMain.BinaryCountDispatcherMarkedInput
#print axioms CurrentMain.BinaryCountDispatcherMarkedInput.count_run
#print axioms CurrentMain.BinaryCountDispatcherMarkedInput.final_halted
#print axioms CurrentMain.BinaryCountDispatcherMarkedInput.counter_length
#print axioms CurrentMain.BinaryCountDispatcherMarkedInput.counter_value
