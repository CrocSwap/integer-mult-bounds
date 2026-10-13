import BinaryWordReversal

/-! Concrete four-tape, fourteen-state input preparation. Input words are
little-endian and may have unequal lengths. The two pristine work tapes finish
with equal-length MSB words and heads just past their least significant bits.
No counter, radix conversion, source caller, Plan or analytic Budget is claimed. -/
namespace CurrentMain.BinaryInputPreparation
open FixedTapeMachine

private theorem fin3 (i : Fin 3) : i=0 ∨ i=1 ∨ i=2 :=
  (show ∀ j : Fin 3, j=0 ∨ j=1 ∨ j=2 from by decide) i
private theorem fin4 (i : Fin 4) : i=0 ∨ i=1 ∨ i=2 ∨ i=3 :=
  (show ∀ j : Fin 4, j=0 ∨ j=1 ∨ j=2 ∨ j=3 from by decide) i
private theorem fin6 (i : Fin 6) : i=0 ∨ i=1 ∨ i=2 ∨ i=3 ∨ i=4 ∨ i=5 :=
  (show ∀ j : Fin 6, j=0 ∨ j=1 ∨ j=2 ∨ j=3 ∨ j=4 ∨ j=5 from by decide) i

def stateA (s : Fin 6) : Fin 14 := ⟨s.val+1, by have := s.isLt; omega⟩
def stateB (s : Fin 6) : Fin 14 := ⟨s.val+7, by have := s.isLt; omega⟩
def readA (r : Fin 4 → Symbol) (i : Fin 3) : Symbol :=
  if i=0 then r 0 else if i=1 then r 1 else r 2
def readB (r : Fin 4 → Symbol) (i : Fin 3) : Symbol :=
  if i=0 then r 1 else if i=1 then r 0 else r 3

def stayAction (s : Fin 14) (r : Fin 4 → Symbol) : Action 4 14 :=
  ⟨s, r, fun _ => .stay⟩
def filled (s : Symbol) : Symbol := if s=.blank then .zero else s

def paddingAction (r : Fin 4 → Symbol) : Action 4 14 where
  state := 0
  writes := fun i => if i=0 ∨ i=1 then filled (r i) else r i
  moves := fun i => if i=0 ∨ i=1 then .right else .stay

def seekAction (r : Fin 4 → Symbol) : Action 4 14 where
  state := 13
  writes := r
  moves := fun i => if i=2 ∨ i=3 then .right else .stay

def liftActionA (r : Fin 4 → Symbol) (a : Action 3 6) : Action 4 14 where
  state := stateA a.state
  writes := fun i => if i=0 then a.writes 0 else if i=1 then a.writes 1
    else if i=2 then a.writes 2 else r i
  moves := fun i => if i=0 then a.moves 0 else if i=1 then a.moves 1
    else if i=2 then a.moves 2 else .stay

def liftActionB (r : Fin 4 → Symbol) (a : Action 3 6) : Action 4 14 where
  state := stateB a.state
  writes := fun i => if i=0 then a.writes 1 else if i=1 then a.writes 0
    else if i=3 then a.writes 2 else r i
  moves := fun i => if i=0 then a.moves 1 else if i=1 then a.moves 0
    else if i=3 then a.moves 2 else .stay

def machine : Machine where
  tapes := 4
  states := 14
  initial := 0
  transition := fun s r =>
    if hz : s.val=0 then
      some (if r 0=.blank ∧ r 1=.blank then stayAction 1 r else paddingAction r)
    else if ha : s.val≤6 then
      match BinaryWordReversal.machine.transition (⟨s.val-1, by have := s.isLt; omega⟩ : Fin 6) (readA r) with
      | some a => some (liftActionA r a)
      | none => some (stayAction 7 r)
    else if hb : s.val≤12 then
      match BinaryWordReversal.machine.transition (⟨s.val-7, by have := s.isLt; omega⟩ : Fin 6) (readB r) with
      | some a => some (liftActionB r a)
      | none => some (stayAction 13 r)
    else if r 2=.blank ∧ r 3=.blank then none else some (seekAction r)

def configuration (s : Fin 14) (a b x y : Tape) : Configuration machine :=
  ⟨s, fun i => if i=(0 : Fin 4) then a else if i=(1 : Fin 4) then b
    else if i=(2 : Fin 4) then x else y⟩

def embedA (c : Configuration BinaryWordReversal.machine) (extra : Tape) : Configuration machine :=
  configuration (stateA c.state) (c.tapes (0 : Fin 3)) (c.tapes (1 : Fin 3)) (c.tapes (2 : Fin 3)) extra

def embedB (c : Configuration BinaryWordReversal.machine) (extra : Tape) : Configuration machine :=
  configuration (stateB c.state) (c.tapes (1 : Fin 3)) (c.tapes (0 : Fin 3)) extra (c.tapes (2 : Fin 3))

private theorem transitionA (s : Fin 6) (r : Fin 4 → Symbol) :
    machine.transition (stateA s) r =
      match BinaryWordReversal.machine.transition s (readA r) with
      | some a => some (liftActionA r a)
      | none => some (stayAction 7 r) := by
  rcases fin6 s with rfl|rfl|rfl|rfl|rfl|rfl <;> rfl

private theorem transitionB (s : Fin 6) (r : Fin 4 → Symbol) :
    machine.transition (stateB s) r =
      match BinaryWordReversal.machine.transition s (readB r) with
      | some a => some (liftActionB r a)
      | none => some (stayAction 13 r) := by
  rcases fin6 s with rfl|rfl|rfl|rfl|rfl|rfl <;> rfl

private theorem reads_embedA (c : Configuration BinaryWordReversal.machine) (extra : Tape) :
    readA (fun i => ((embedA c extra).tapes i).head) = fun j => (c.tapes j).head := by
  funext j
  rcases fin3 j with rfl|rfl|rfl <;> rfl

private theorem reads_embedB (c : Configuration BinaryWordReversal.machine) (extra : Tape) :
    readB (fun i => ((embedB c extra).tapes i).head) = fun j => (c.tapes j).head := by
  funext j
  rcases fin3 j with rfl|rfl|rfl <;> rfl

private theorem step_of_transition (m : Machine) (c : Configuration m)
    (a : Action m.tapes m.states)
    (h : m.transition c.state (fun i => (c.tapes i).head) = some a) :
    step m c = some (Configuration.mk a.state
      (fun i => ((c.tapes i).write (a.writes i)).move (a.moves i))) := by
  unfold step
  rw [h]

/-- Only successful source transitions are simulated. No assumption that a
reported saturated run time is its first halt time is used. -/
private theorem step_embedA (c d : Configuration BinaryWordReversal.machine) (extra : Tape)
    (h : step BinaryWordReversal.machine c = some d) :
    step machine (embedA c extra) = some (embedA d extra) := by
  cases ht : BinaryWordReversal.machine.transition c.state (fun i => (c.tapes i).head) with
  | none =>
    simp only [step, ht] at h
    cases h
  | some a =>
    simp only [step, ht, Option.some.injEq] at h
    subst d
    have lifted : BinaryWordReversal.machine.transition c.state
        (readA (fun i : Fin 4 => ((embedA c extra).tapes i).head)) = some a :=
      (congrArg (fun reads : Fin 3 → Symbol =>
        BinaryWordReversal.machine.transition c.state reads) (reads_embedA c extra)).trans ht
    have outer : machine.transition (embedA c extra).state
        (fun i : Fin 4 => ((embedA c extra).tapes i).head) = some (liftActionA (fun i : Fin 4 => ((embedA c extra).tapes i).head) a) :=
      (transitionA c.state (fun i : Fin 4 => ((embedA c extra).tapes i).head)).trans
        (congrArg (fun q : Option (Action 3 6) =>
          match q with
          | some a => some (liftActionA (fun i : Fin 4 => ((embedA c extra).tapes i).head) a)
          | none => some (stayAction 7 (fun i : Fin 4 => ((embedA c extra).tapes i).head))) lifted)
    refine (step_of_transition machine (embedA c extra) _ outer).trans ?_
    dsimp only [liftActionA, embedA, configuration]
    apply congrArg some
    apply congrArg (fun tapes : Fin 4 → Tape =>
      (Configuration.mk (stateA a.state) tapes : Configuration machine))
    funext i
    rcases fin4 i with rfl|rfl|rfl|rfl <;> simp [configuration, Tape.write, Tape.move]

private theorem step_embedB (c d : Configuration BinaryWordReversal.machine) (extra : Tape)
    (h : step BinaryWordReversal.machine c = some d) :
    step machine (embedB c extra) = some (embedB d extra) := by
  cases ht : BinaryWordReversal.machine.transition c.state (fun i => (c.tapes i).head) with
  | none =>
    simp only [step, ht] at h
    cases h
  | some a =>
    simp only [step, ht, Option.some.injEq] at h
    subst d
    have lifted : BinaryWordReversal.machine.transition c.state
        (readB (fun i : Fin 4 => ((embedB c extra).tapes i).head)) = some a :=
      (congrArg (fun reads : Fin 3 → Symbol =>
        BinaryWordReversal.machine.transition c.state reads) (reads_embedB c extra)).trans ht
    have outer : machine.transition (embedB c extra).state
        (fun i : Fin 4 => ((embedB c extra).tapes i).head) = some (liftActionB (fun i : Fin 4 => ((embedB c extra).tapes i).head) a) :=
      (transitionB c.state (fun i : Fin 4 => ((embedB c extra).tapes i).head)).trans
        (congrArg (fun q : Option (Action 3 6) =>
          match q with
          | some a => some (liftActionB (fun i : Fin 4 => ((embedB c extra).tapes i).head) a)
          | none => some (stayAction 13 (fun i : Fin 4 => ((embedB c extra).tapes i).head))) lifted)
    refine (step_of_transition machine (embedB c extra) _ outer).trans ?_
    dsimp only [liftActionB, embedB, configuration]
    apply congrArg some
    apply congrArg (fun tapes : Fin 4 → Tape =>
      (Configuration.mk (stateB a.state) tapes : Configuration machine))
    funext i
    rcases fin4 i with rfl|rfl|rfl|rfl <;> simp [configuration, Tape.write, Tape.move]

private theorem halt_embedA (c : Configuration BinaryWordReversal.machine) (extra : Tape)
    (h : Halted BinaryWordReversal.machine c) : step machine (embedA c extra) =
      some (configuration 7 (c.tapes (0 : Fin 3)) (c.tapes (1 : Fin 3)) (c.tapes (2 : Fin 3)) extra) := by
  have ht : BinaryWordReversal.machine.transition c.state (fun i => (c.tapes i).head) = none := by
    cases he : BinaryWordReversal.machine.transition c.state (fun i => (c.tapes i).head) <;>
      simp_all [Halted, step]
  have lifted : BinaryWordReversal.machine.transition c.state
      (readA (fun i : Fin 4 => ((embedA c extra).tapes i).head)) = none :=
    (congrArg (fun reads : Fin 3 → Symbol =>
      BinaryWordReversal.machine.transition c.state reads) (reads_embedA c extra)).trans ht
  have outer : machine.transition (embedA c extra).state
      (fun i : Fin 4 => ((embedA c extra).tapes i).head) = some (stayAction 7 (fun i : Fin 4 => ((embedA c extra).tapes i).head)) :=
    (transitionA c.state (fun i : Fin 4 => ((embedA c extra).tapes i).head)).trans
      (congrArg (fun q : Option (Action 3 6) =>
        match q with
        | some a => some (liftActionA (fun i : Fin 4 => ((embedA c extra).tapes i).head) a)
        | none => some (stayAction 7 (fun i : Fin 4 => ((embedA c extra).tapes i).head))) lifted)
  refine (step_of_transition machine (embedA c extra) _ outer).trans ?_
  dsimp only [stayAction, embedA, configuration]
  apply congrArg some
  apply congrArg (fun tapes : Fin 4 → Tape => (Configuration.mk (7 : Fin 14) tapes : Configuration machine))
  funext i
  rcases fin4 i with rfl|rfl|rfl|rfl <;> simp [Tape.write, Tape.move]

private theorem halt_embedB (c : Configuration BinaryWordReversal.machine) (extra : Tape)
    (h : Halted BinaryWordReversal.machine c) : step machine (embedB c extra) =
      some (configuration 13 (c.tapes (1 : Fin 3)) (c.tapes (0 : Fin 3)) extra (c.tapes (2 : Fin 3))) := by
  have ht : BinaryWordReversal.machine.transition c.state (fun i => (c.tapes i).head) = none := by
    cases he : BinaryWordReversal.machine.transition c.state (fun i => (c.tapes i).head) <;>
      simp_all [Halted, step]
  have lifted : BinaryWordReversal.machine.transition c.state
      (readB (fun i : Fin 4 => ((embedB c extra).tapes i).head)) = none :=
    (congrArg (fun reads : Fin 3 → Symbol =>
      BinaryWordReversal.machine.transition c.state reads) (reads_embedB c extra)).trans ht
  have outer : machine.transition (embedB c extra).state
      (fun i : Fin 4 => ((embedB c extra).tapes i).head) = some (stayAction 13 (fun i : Fin 4 => ((embedB c extra).tapes i).head)) :=
    (transitionB c.state (fun i : Fin 4 => ((embedB c extra).tapes i).head)).trans
      (congrArg (fun q : Option (Action 3 6) =>
        match q with
        | some a => some (liftActionB (fun i : Fin 4 => ((embedB c extra).tapes i).head) a)
        | none => some (stayAction 13 (fun i : Fin 4 => ((embedB c extra).tapes i).head))) lifted)
  refine (step_of_transition machine (embedB c extra) _ outer).trans ?_
  dsimp only [stayAction, embedB, configuration]
  apply congrArg some
  apply congrArg (fun tapes : Fin 4 → Tape => (Configuration.mk (13 : Fin 14) tapes : Configuration machine))
  funext i
  rcases fin4 i with rfl|rfl|rfl|rfl <;> simp [Tape.write, Tape.move]

/-- A finite proof-local lift: existence of a halted source endpoint suffices
for a bounded successful-prefix simulation, without an extra progress premise. -/
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

def pad (n : Nat) (w : List Bool) : List Bool := w ++ List.replicate (n-w.length) false

theorem pad_length (n : Nat) (w : List Bool) (h : w.length≤n) : (pad n w).length=n := by
  simp only [pad, List.length_append, List.length_replicate]
  omega

private theorem pad_succ (n : Nat) (w : List Bool) :
    pad (n+1) w = w.headD false :: pad n w.tail := by
  cases w with
  | nil => simp [pad, List.replicate_succ]
  | cons b rest => simp [pad, Nat.add_sub_add_right]

private theorem filled_move (left : List Symbol) (w : List Bool) :
    ((BinaryWordReversal.fromRight left (w.map bitSymbol)).write
      (filled (BinaryWordReversal.fromRight left (w.map bitSymbol)).head)).move .right =
      BinaryWordReversal.fromRight (bitSymbol (w.headD false)::left) (w.tail.map bitSymbol) := by
  cases w with
  | nil => rfl
  | cons b rest => cases b <;> cases rest <;> rfl

private theorem padding_step (x y : List Bool) (lx ly : List Symbol) (a b : Tape)
    (h : x≠[] ∨ y≠[]) :
    step machine (configuration 0 (BinaryWordReversal.fromRight lx (x.map bitSymbol))
      (BinaryWordReversal.fromRight ly (y.map bitSymbol)) a b) =
      some (configuration 0
        (BinaryWordReversal.fromRight (bitSymbol (x.headD false)::lx) (x.tail.map bitSymbol))
        (BinaryWordReversal.fromRight (bitSymbol (y.headD false)::ly) (y.tail.map bitSymbol)) a b) := by
  have hn : ¬ ((BinaryWordReversal.fromRight lx (x.map bitSymbol)).head=.blank ∧
      (BinaryWordReversal.fromRight ly (y.map bitSymbol)).head=.blank) := by
    cases x with
    | nil => cases y with
      | nil => simp at h
      | cons c rest => cases c <;> simp [BinaryWordReversal.fromRight, bitSymbol]
    | cons c rest => cases c <;> simp [BinaryWordReversal.fromRight, bitSymbol]
  have tr : machine.transition
      (configuration 0 (BinaryWordReversal.fromRight lx (x.map bitSymbol))
        (BinaryWordReversal.fromRight ly (y.map bitSymbol)) a b).state
      (fun i => ((configuration 0 (BinaryWordReversal.fromRight lx (x.map bitSymbol))
        (BinaryWordReversal.fromRight ly (y.map bitSymbol)) a b).tapes i).head) =
      some (paddingAction (fun i => ((configuration 0
        (BinaryWordReversal.fromRight lx (x.map bitSymbol))
        (BinaryWordReversal.fromRight ly (y.map bitSymbol)) a b).tapes i).head)) := by
    simp [machine, configuration, hn]
  unfold step
  rw [tr]
  dsimp only [paddingAction, configuration]
  apply congrArg some
  apply congrArg (fun tapes : Fin 4 → Tape => (Configuration.mk (0 : Fin 14) tapes : Configuration machine))
  funext i
  rcases fin4 i with rfl|rfl|rfl|rfl
  · simpa using filled_move lx x
  · simpa using filled_move ly y
  · simp [Tape.write, Tape.move]
  · simp [Tape.write, Tape.move]

private theorem padding_run (n : Nat) (x y : List Bool) (lx ly : List Symbol) (a b : Tape)
    (h : max x.length y.length=n) :
    run machine n (configuration 0 (BinaryWordReversal.fromRight lx (x.map bitSymbol))
      (BinaryWordReversal.fromRight ly (y.map bitSymbol)) a b) =
      configuration 0 (BinaryWordReversal.endTape ((pad n x).reverse.map bitSymbol ++ lx))
        (BinaryWordReversal.endTape ((pad n y).reverse.map bitSymbol ++ ly)) a b := by
  induction n generalizing x y lx ly with
  | zero =>
    have hx : x=[] := List.length_eq_zero.mp (by omega)
    have hy : y=[] := List.length_eq_zero.mp (by omega)
    subst x; subst y; rfl
  | succ n ih =>
    have hne : x≠[] ∨ y≠[] := by cases x <;> cases y <;> simp_all
    have ht : max x.tail.length y.tail.length=n := by
      simp only [List.length_tail]; omega
    rw [run, padding_step x y lx ly a b hne]
    dsimp only
    rw [ih x.tail y.tail _ _ ht]
    simp only [pad_succ, List.reverse_cons, List.map_append, List.map_cons,
      List.map_nil, List.append_assoc, List.singleton_append]

private theorem enterA (lx ly : List Symbol) (a b : Tape) :
    step machine (configuration 0 (BinaryWordReversal.endTape lx) (BinaryWordReversal.endTape ly) a b) =
      some (embedA (BinaryWordReversal.configuration 0 (BinaryWordReversal.endTape lx) (BinaryWordReversal.endTape ly) a) b) := by
  unfold step
  dsimp only [machine, configuration, BinaryWordReversal.endTape, embedA, BinaryWordReversal.configuration, stateA, stayAction]
  apply congrArg some
  apply congrArg (fun tapes : Fin 4 → Tape => (Configuration.mk (1 : Fin 14) tapes : Configuration machine))
  funext i
  rcases fin4 i with rfl|rfl|rfl|rfl <;> simp [Tape.write, Tape.move]

def residual (w : List Bool) : Nat := if w.isEmpty then 1 else 2*w.length+2

private theorem reverse_from_end (w : List Bool) (spare : Tape) :
    run BinaryWordReversal.machine (residual w)
      (BinaryWordReversal.configuration 0 (BinaryWordReversal.endTape (w.reverse.map bitSymbol)) spare Tape.blank) =
      BinaryWordReversal.finalConfiguration w spare := by
  have count : BinaryWordReversal.elapsed w=w.length+residual w := by
    cases w <;> simp [BinaryWordReversal.elapsed, residual] <;> omega
  have h := BinaryWordReversal.reverse_run w spare
  rw [count, run_add] at h
  rw [← BinaryWordReversal.fromRight_word, BinaryWordReversal.seek_run] at h
  simpa only [List.append_nil] using h

private theorem seek_step (a b : Tape) (c d : Bool) (x y : List Bool) (lx ly : List Symbol) :
    step machine (configuration 13 a b (BinaryWordReversal.fromRight lx ((c::x).map bitSymbol))
      (BinaryWordReversal.fromRight ly ((d::y).map bitSymbol))) =
      some (configuration 13 a b (BinaryWordReversal.fromRight (bitSymbol c::lx) (x.map bitSymbol))
        (BinaryWordReversal.fromRight (bitSymbol d::ly) (y.map bitSymbol))) := by
  unfold step
  cases c <;> cases d <;>
    dsimp only [machine, configuration, BinaryWordReversal.fromRight, List.map_cons, bitSymbol, seekAction]
  all_goals
    apply congrArg some
    apply congrArg (fun tapes : Fin 4 → Tape => (Configuration.mk (13 : Fin 14) tapes : Configuration machine))
    funext i
    rcases fin4 i with rfl|rfl|rfl|rfl <;>
      cases x <;> cases y <;> simp [BinaryWordReversal.fromRight, Tape.write, Tape.move]

private theorem seek_run (x y : List Bool) (a b : Tape) (lx ly : List Symbol)
    (h : x.length=y.length) :
    run machine x.length (configuration 13 a b (BinaryWordReversal.fromRight lx (x.map bitSymbol))
      (BinaryWordReversal.fromRight ly (y.map bitSymbol))) =
      configuration 13 a b (BinaryWordReversal.endTape (x.reverse.map bitSymbol ++ lx))
        (BinaryWordReversal.endTape (y.reverse.map bitSymbol ++ ly)) := by
  induction x generalizing y lx ly with
  | nil => have hy : y=[] := List.length_eq_zero.mp h.symm; subst y; rfl
  | cons c x ih =>
    cases y with
    | nil => simp at h
    | cons d y =>
      have ht : x.length=y.length := Nat.succ.inj h
      rw [List.length_cons, run, seek_step]
      dsimp only
      rw [ih y _ _ ht]
      simp only [List.reverse_cons, List.map_append, List.map_cons, List.map_nil,
        List.append_assoc, List.singleton_append]

def initialConfiguration (x y : List Bool) : Configuration machine :=
  configuration 0 (Tape.ofWord x) (Tape.ofWord y) Tape.blank Tape.blank

def finalConfiguration (x y : List Bool) : Configuration machine :=
  let n := max x.length y.length
  configuration 13 (BinaryWordReversal.finalInput (pad n x)) (BinaryWordReversal.finalInput (pad n y))
    (BinaryWordReversal.endTape ((pad n x).map bitSymbol)) (BinaryWordReversal.endTape ((pad n y).map bitSymbol))

/-- Exact all-input work-copy preparation. The bound concerns actual successful
transitions of this table; original input tapes retain their visited blanks. -/
theorem prepare_run (x y : List Bool) :
    ∃ t, t≤6*(max x.length y.length)+7 ∧
      run machine t (initialConfiguration x y)=finalConfiguration x y := by
  let n := max x.length y.length
  let px := pad n x
  let py := pad n y
  have hx : px.length=n := pad_length n x (Nat.le_max_left _ _)
  have hy : py.length=n := pad_length n y (Nat.le_max_right _ _)
  let a0 := BinaryWordReversal.configuration 0 (BinaryWordReversal.endTape (px.reverse.map bitSymbol))
    (BinaryWordReversal.endTape (py.reverse.map bitSymbol)) Tape.blank
  let af := BinaryWordReversal.finalConfiguration px (BinaryWordReversal.endTape (py.reverse.map bitSymbol))
  let b0 := BinaryWordReversal.configuration 0 (BinaryWordReversal.endTape (py.reverse.map bitSymbol)) (BinaryWordReversal.finalInput px) Tape.blank
  let bf := BinaryWordReversal.finalConfiguration py (BinaryWordReversal.finalInput px)
  have arun : run BinaryWordReversal.machine (residual px) a0=af := reverse_from_end _ _
  have brun : run BinaryWordReversal.machine (residual py) b0=bf := reverse_from_end _ _
  have ah : Halted BinaryWordReversal.machine (run BinaryWordReversal.machine (residual px) a0) := by
    rw [arun]; exact BinaryWordReversal.final_halted _ _
  have bh : Halted BinaryWordReversal.machine (run BinaryWordReversal.machine (residual py) b0) := by
    rw [brun]; exact BinaryWordReversal.final_halted _ _
  obtain ⟨ka,hka,ha⟩ := simulate_to_halt BinaryWordReversal.machine machine (fun c => embedA c Tape.blank)
    (fun c d h => step_embedA c d Tape.blank h) (residual px) a0 ah
  rw [arun] at ha
  obtain ⟨kb,hkb,hb⟩ := simulate_to_halt BinaryWordReversal.machine machine (fun c => embedB c (Tape.ofWord px.reverse))
    (fun c d h => step_embedB c d (Tape.ofWord px.reverse) h) (residual py) b0 bh
  rw [brun] at hb
  have start : run machine n (initialConfiguration x y)=
      configuration 0 (BinaryWordReversal.endTape (px.reverse.map bitSymbol)) (BinaryWordReversal.endTape (py.reverse.map bitSymbol))
        Tape.blank Tape.blank := by
    unfold initialConfiguration
    rw [← BinaryWordReversal.fromRight_word x, ← BinaryWordReversal.fromRight_word y, padding_run n x y [] [] _ _ rfl]
    simp only [List.append_nil]; rfl
  have entry : step machine (configuration 0 (BinaryWordReversal.endTape (px.reverse.map bitSymbol))
      (BinaryWordReversal.endTape (py.reverse.map bitSymbol)) Tape.blank Tape.blank)=some (embedA a0 Tape.blank) := enterA _ _ _ _
  have bridge : step machine (embedA af Tape.blank)=some (embedB b0 (Tape.ofWord px.reverse)) := by
    simpa only [af, b0, embedB, BinaryWordReversal.finalConfiguration, BinaryWordReversal.configuration, configuration, stateB]
      using halt_embedA af Tape.blank (BinaryWordReversal.final_halted _ _)
  have finish : step machine (embedB bf (Tape.ofWord px.reverse))=
      some (configuration 13 (BinaryWordReversal.finalInput px) (BinaryWordReversal.finalInput py)
        (Tape.ofWord px.reverse) (Tape.ofWord py.reverse)) := by
    simpa only [bf, BinaryWordReversal.finalConfiguration, BinaryWordReversal.configuration, configuration]
      using halt_embedB bf (Tape.ofWord px.reverse) (BinaryWordReversal.final_halted _ _)
  have scan : run machine n (configuration 13 (BinaryWordReversal.finalInput px) (BinaryWordReversal.finalInput py)
      (Tape.ofWord px.reverse) (Tape.ofWord py.reverse))=finalConfiguration x y := by
    have lengths : px.reverse.length=py.reverse.length := by simp [hx, hy]
    have h := seek_run px.reverse py.reverse (BinaryWordReversal.finalInput px) (BinaryWordReversal.finalInput py) [] [] lengths
    simpa only [List.length_reverse, hx, BinaryWordReversal.fromRight_word, List.reverse_reverse,
      List.append_nil] using h
  refine ⟨n+1+ka+1+kb+1+n, ?_, ?_⟩
  · have hpa : residual px≤2*n+2 := by unfold residual; split <;> omega
    have hpb : residual py≤2*n+2 := by unfold residual; split <;> omega
    change n+1+ka+1+kb+1+n≤6*n+7
    omega
  · rw [run_add machine (n+1+ka+1+kb+1) n,
      run_add machine (n+1+ka+1+kb) 1,
      run_add machine (n+1+ka+1) kb,
      run_add machine (n+1+ka) 1,
      run_add machine (n+1) ka, run_add machine n 1, start]
    simp only [run, entry]
    rw [ha]
    simp only [run, bridge]
    rw [hb]
    simp only [run, finish]
    exact scan

theorem final_halted (x y : List Bool) : Halted machine (finalConfiguration x y) := by
  rfl

private theorem zero_value (base k : Nat) :
    IntegerConvolution.value base (List.replicate k 0)=0 := by
  induction k with
  | zero => rfl
  | succ k ih => simp only [List.replicate_succ, IntegerConvolution.value, ih, Nat.mul_zero, Nat.zero_add]

private theorem append_zero_value (base : Nat) (w : List Nat) (k : Nat) :
    IntegerConvolution.value base (w ++ List.replicate k 0)=IntegerConvolution.value base w := by
  induction w with
  | nil => exact zero_value base k
  | cons a w ih => simp only [List.cons_append, IntegerConvolution.value, ih]

theorem pad_value (n : Nat) (w : List Bool) : wordValue (pad n w)=wordValue w := by
  unfold wordValue IntegerConvolution.binaryValue pad
  rw [List.map_append]
  simp only [List.map_replicate, Bool.false_eq_true, if_false]
  exact append_zero_value 2 _ _

theorem source_values (x y : List Bool) :
    BinaryWordReversal.sourceMSBValue (pad (max x.length y.length) x).reverse=wordValue x ∧
    BinaryWordReversal.sourceMSBValue (pad (max x.length y.length) y).reverse=wordValue y := by
  constructor <;> rw [BinaryWordReversal.input_value, pad_value]

theorem work_words_length (x y : List Bool) :
    (pad (max x.length y.length) x).reverse.length=max x.length y.length ∧
    (pad (max x.length y.length) y).reverse.length=max x.length y.length := by
  simp only [List.length_reverse]
  exact ⟨pad_length _ _ (Nat.le_max_left _ _), pad_length _ _ (Nat.le_max_right _ _)⟩

end CurrentMain.BinaryInputPreparation
#print axioms CurrentMain.BinaryInputPreparation.prepare_run
#print axioms CurrentMain.BinaryInputPreparation.final_halted
#print axioms CurrentMain.BinaryInputPreparation.pad_value
#print axioms CurrentMain.BinaryInputPreparation.source_values
#print axioms CurrentMain.BinaryInputPreparation.work_words_length
