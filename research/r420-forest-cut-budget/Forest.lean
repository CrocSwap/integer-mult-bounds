import Init

/-!
Generic Boolean semantics for target-forest compensation.

The circuit theorems below quantify over arbitrary register types, arbitrary
initial target/helper values, and arbitrary finite lists of legal XOR gates.
The inverse is the literal reversed gate list. No concrete R420 word, geometry,
cost bound, COPY/ERASE lifecycle, or physical frame transport is asserted here.
Prepared with OpenAI assistance; original project attribution is retained.
-/

namespace TargetForest

set_option Elab.async false

abbrev State (Reg : Type) := Reg → Bool

/-- A reversible target transvection; self-addition is excluded at the boundary. -/
structure Gate (Reg : Type) where
  dst : Reg
  src : Reg
  distinct : dst ≠ src

variable {Reg : Type} [DecidableEq Reg]

def add (x y : State Reg) : State Reg := fun r => x r ^^ y r

def step (g : Gate Reg) (x : State Reg) : State Reg :=
  fun r => if r = g.dst then x r ^^ x g.src else x r

/-- Execute from left to right, exactly as a sequential gate word. -/
def run : List (Gate Reg) → State Reg → State Reg
  | [], x => x
  | g :: gs, x => run gs (step g x)

private theorem xor_shuffle (a b c d : Bool) :
    ((a ^^ b) ^^ (c ^^ d)) = ((a ^^ c) ^^ (b ^^ d)) := by
  cases a <;> cases b <;> cases c <;> cases d <;> rfl

private theorem xor_cancel (a b : Bool) : ((a ^^ b) ^^ b) = a := by
  cases a <;> cases b <;> rfl

theorem step_add (g : Gate Reg) (x y : State Reg) :
    step g (add x y) = add (step g x) (step g y) := by
  funext r
  by_cases hr : r = g.dst
  · simp only [step, add, if_pos hr]
    exact xor_shuffle _ _ _ _
  · simp only [step, add, if_neg hr]

theorem step_involutive (g : Gate Reg) (x : State Reg) :
    step g (step g x) = x := by
  funext r
  by_cases hr : r = g.dst
  · have hs : g.src ≠ g.dst := Ne.symm g.distinct
    simp only [step, if_pos hr, if_neg hs]
    exact xor_cancel _ _
  · simp only [step, if_neg hr]

theorem run_add (gs : List (Gate Reg)) (x y : State Reg) :
    run gs (add x y) = add (run gs x) (run gs y) := by
  induction gs generalizing x y with
  | nil => rfl
  | cons g gs ih =>
    simp only [run, step_add, ih]

theorem run_append (as bs : List (Gate Reg)) (x : State Reg) :
    run (as ++ bs) x = run bs (run as x) := by
  induction as generalizing x with
  | nil => rfl
  | cons a as ih =>
    exact ih (step a x)

/-- Reversing a legal XOR word constructs its inverse, for every initial state. -/
theorem run_reverse (gs : List (Gate Reg)) (x : State Reg) :
    run gs.reverse (run gs x) = x := by
  induction gs generalizing x with
  | nil => rfl
  | cons g gs ih =>
    simp only [List.reverse_cons, run_append, run]
    rw [ih, step_involutive]

/-- Core compensation identity: prepare by A, inject A d, then undo A. -/
theorem compensated_injection (gs : List (Gate Reg)) (x d : State Reg) :
    run gs.reverse (add (run gs x) (run gs d)) = add x d := by
  rw [← run_add, run_reverse]

/-- Every destination occurs once, and a parent is changed only after its children.
Roots need no gate. The condition also permits parents outside the target list. -/
def ForestOrdered : List (Gate Reg) → Prop
  | [] => True
  | g :: gs => ForestOrdered gs ∧
      ∀ h ∈ gs, g.dst ≠ h.dst ∧ g.dst ≠ h.src

/-- The parent edge encoded by a child's unique gate. -/
def parent : List (Gate Reg) → Reg → Option Reg
  | [], _ => none
  | g :: gs, r => if r = g.dst then some g.src else parent gs r

/-- The sparse forest matrix I + P, expressed without a matrix library. -/
def forestAction (gs : List (Gate Reg)) (x : State Reg) : State Reg :=
  fun r => match parent gs r with
    | none => x r
    | some p => x r ^^ x p

theorem run_untouched (gs : List (Gate Reg)) (x : State Reg) (r : Reg)
    (h : ∀ g ∈ gs, r ≠ g.dst) : run gs x r = x r := by
  induction gs generalizing x with
  | nil => rfl
  | cons g gs ih =>
    change run gs (step g x) r = x r
    rw [ih (step g x) (fun q hq => h q (List.mem_cons_of_mem g hq))]
    simp only [step, if_neg (h g List.mem_cons_self)]

private theorem parent_some (gs : List (Gate Reg)) (r p : Reg)
    (h : parent gs r = some p) :
    ∃ g ∈ gs, r = g.dst ∧ p = g.src := by
  induction gs with
  | nil => simp [parent] at h
  | cons g gs ih =>
    by_cases hr : r = g.dst
    · simp only [parent, if_pos hr, Option.some.injEq] at h
      exact ⟨g, List.mem_cons_self, hr, h.symm⟩
    · simp only [parent, if_neg hr] at h
      obtain ⟨q, hq, hrq, hpq⟩ := ih h
      exact ⟨q, List.mem_cons_of_mem g hq, hrq, hpq⟩

private theorem forestAction_step (gs : List (Gate Reg)) (g : Gate Reg)
    (h : ∀ q ∈ gs, g.dst ≠ q.src) (x : State Reg) (r : Reg)
    (hr : r ≠ g.dst) : forestAction gs (step g x) r = forestAction gs x r := by
  unfold forestAction
  cases hp : parent gs r with
  | none => simp only [step, if_neg hr]
  | some p =>
    obtain ⟨q, hq, _, hpq⟩ := parent_some gs r p hp
    have hpg : p ≠ g.dst := by
      rw [hpq]
      exact Ne.symm (h q hq)
    simp only [step, if_neg hr, if_neg hpg]

/-- Children-before-parent execution really is A = I + P on all initial bits. -/
theorem run_forestAction (gs : List (Gate Reg)) (ordered : ForestOrdered gs)
    (x : State Reg) : run gs x = forestAction gs x := by
  induction gs generalizing x with
  | nil => rfl
  | cons g gs ih =>
    rcases ordered with ⟨tail, fresh⟩
    funext r
    by_cases hr : r = g.dst
    · subst r
      change run gs (step g x) g.dst = _
      rw [run_untouched gs (step g x) g.dst (fun q hq => (fresh q hq).1)]
      simp [step, forestAction, parent]
    · change run gs (step g x) r = _
      rw [ih tail (step g x)]
      rw [forestAction_step gs g (fun q hq => (fresh q hq).2) x r hr]
      simp only [forestAction, parent, if_neg hr]

/-- Forest compensation uses exactly the local increment d(child) XOR d(parent). -/
theorem forest_compensated_injection (gs : List (Gate Reg))
    (ordered : ForestOrdered gs) (x d : State Reg) :
    run gs.reverse (add (run gs x) (forestAction gs d)) = add x d := by
  rw [← run_forestAction gs ordered d]
  exact compensated_injection gs x d

/-- A register bank split explicitly into arbitrary helpers and targets. -/
structure Banks (Helper Target : Type) where
  helpers : State Helper
  targets : State Target

variable {Helper : Type}

/-- The unchanged helpers determine the intended target increment `K h`.
The executed middle injection uses the compensated increment `A (K h)`.
`K` can be any function; linearity is needed only for the target circuit A. -/
def compensatedShear (gs : List (Gate Reg))
    (K : State Helper → State Reg) (s : Banks Helper Reg) : Banks Helper Reg :=
  { helpers := s.helpers
    targets := run gs.reverse (add (run gs s.targets) (run gs (K s.helpers))) }

/-- Exact dirty-helper/dirty-target semantics of the three-stage construction. -/
theorem compensatedShear_correct (gs : List (Gate Reg))
    (K : State Helper → State Reg) (s : Banks Helper Reg) :
    compensatedShear gs K s =
      { helpers := s.helpers, targets := add s.targets (K s.helpers) } := by
  simp only [compensatedShear, compensated_injection]

/-- The same bank operation, using the explicit one-parent compensation formula. -/
def forestShear (gs : List (Gate Reg))
    (K : State Helper → State Reg) (s : Banks Helper Reg) : Banks Helper Reg :=
  { helpers := s.helpers
    targets := run gs.reverse
      (add (run gs s.targets) (forestAction gs (K s.helpers))) }

/-- Local forest compensation preserves arbitrary helpers and adds K h to
arbitrary initial targets; no clean-register assumption occurs in the theorem. -/
theorem forestShear_correct (gs : List (Gate Reg))
    (ordered : ForestOrdered gs) (K : State Helper → State Reg)
    (s : Banks Helper Reg) :
    forestShear gs K s =
      { helpers := s.helpers, targets := add s.targets (K s.helpers) } := by
  simp only [forestShear, forest_compensated_injection gs ordered]

end TargetForest

#print axioms TargetForest.run_add
#print axioms TargetForest.run_reverse
#print axioms TargetForest.compensated_injection
#print axioms TargetForest.run_forestAction
#print axioms TargetForest.forest_compensated_injection
#print axioms TargetForest.compensatedShear_correct
#print axioms TargetForest.forestShear_correct
