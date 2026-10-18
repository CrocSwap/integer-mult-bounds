import Std

/-
Copyright (c) 2026 Gareth Davidson (@bitplane). Apache-2.0.
Prepared with substantial OpenAI Codex assistance.
Formalizes the binary nonlinear restoration argument of PR628 / PR663.
Leaves are completed source-restoring shears with fixed external data.
-/

set_option autoImplicit false

namespace NonlinearEcho

abbrev Value (width : Nat) := Fin width → Int
abbrev Dirt (width depth : Nat) := Fin depth → Value width

def add {w : Nat} (a b : Value w) : Value w := fun i => a i + b i
def sub {w : Nat} (a b : Value w) : Value w := fun i => a i - b i

theorem add_sub_cancel {w : Nat} (a b : Value w) : sub (add a b) b = a := by
  funext i
  simp [add, sub]

theorem sub_add_cancel {w : Nat} (a b : Value w) : add (sub a b) b = a := by
  funext i
  simp [add, sub]

theorem target_forward {w : Nat} (y a b : Value w) :
    sub (add y a) b = add y (sub a b) := by
  funext i
  simp only [add, sub]
  omega

theorem target_inverse {w : Nat} (y a b : Value w) :
    sub (add y b) a = sub y (sub a b) := by
  funext i
  simp only [add, sub]
  omega

theorem add_sub_left {w : Nat} (a b : Value w) : sub (add a b) a = b := by
  funext i
  simp only [add, sub]
  omega

def head {w d : Nat} (s : Dirt w (d+1)) : Value w := s 0
def tail {w d : Nat} (s : Dirt w (d+1)) : Dirt w d := fun i => s i.succ
def join {w d : Nat} (z : Value w) (s : Dirt w d) : Dirt w (d+1) := Fin.cases z s

theorem join_head_tail {w d : Nat} (s : Dirt w (d+1)) : join (head s) (tail s) = s := by
  funext i
  refine Fin.cases ?_ (fun j => ?_) i
  · rfl
  · rfl

/-- Binary factor trees, indexed by available disjoint deeper scratch.
Leaves may leave capacity unused; both children reuse the same deeper pool. -/
inductive Tree : Nat → Type where
  | leaf (depth label : Nat) : Tree depth
  | node {depth : Nat} (left right : Tree depth) : Tree (depth+1)

/-- The literal four-call sequence, including the true reverse word.
The source is an immutable argument of the completed-leaf interface.
Scratch arrays and target are separate typed components. -/
def run {w d : Nat} (f : Nat → Value w → Value w) (t : Tree d)
    (positive : Bool) (x y : Value w) (s : Dirt w d) : Value w × Dirt w d :=
  match t with
  | .leaf _ label => (if positive then add y (f label x) else sub y (f label x), s)
  | .node left right =>
    let z := head s
    let rest := tail s
    if positive then
      let (z1, s1) := run f left true x z rest
      let (y1, s2) := run f right true z1 y s1
      let (z2, s3) := run f left false x z1 s2
      let (y2, s4) := run f right false z2 y1 s3
      (y2, join z2 s4)
    else
      let (y1, s1) := run f right true z y rest
      let (z1, s2) := run f left true x z s1
      let (y2, s3) := run f right false z1 y1 s2
      let (z2, s4) := run f left false x z1 s3
      (y2, join z2 s4)

/-- A recursively composed nonlinear increment can depend on initial dirt. -/
def delta {w d : Nat} (f : Nat → Value w → Value w) (t : Tree d)
    (x : Value w) (s : Dirt w d) : Value w :=
  match t with
  | .leaf _ label => f label x
  | .node left right =>
    sub (delta f right (add (head s) (delta f left x (tail s))) (tail s))
      (delta f right (head s) (tail s))

/-- All finite trees, widths, integer arrays, and deterministic nonlinear leaves. -/
theorem run_eq {w d : Nat} (f : Nat → Value w → Value w) (t : Tree d)
    (positive : Bool) (x y : Value w) (s : Dirt w d) :
    run f t positive x y s =
      (if positive then add y (delta f t x s) else sub y (delta f t x s), s) := by
  induction t generalizing positive x y with
  | leaf depth label => rfl
  | node left right ihl ihr =>
    cases positive <;>
      simp only [run, Bool.false_eq_true, ↓reduceIte, ihl, ihr,
        add_sub_cancel, join_head_tail, delta]
    · rw [target_inverse]
    · rw [target_forward]

theorem scratch_restored {w d : Nat} (f : Nat → Value w → Value w) (t : Tree d)
    (positive : Bool) (x y : Value w) (s : Dirt w d) :
    (run f t positive x y s).2 = s := by
  rw [run_eq]

theorem positive_increment {w d : Nat} (f : Nat → Value w → Value w) (t : Tree d)
    (x y : Value w) (s : Dirt w d) :
    sub (run f t true x y s).1 y = delta f t x s := by
  rw [run_eq]
  exact add_sub_left y _

theorem exact_inverse {w d : Nat} (f : Nat → Value w → Value w) (t : Tree d)
    (x y : Value w) (s : Dirt w d) :
    let forward := run f t true x y s
    run f t false x forward.1 forward.2 = (y,s) := by
  simp only [run_eq, Bool.false_eq_true, ↓reduceIte, add_sub_cancel]

theorem inverse_then_forward {w d : Nat} (f : Nat → Value w → Value w) (t : Tree d)
    (x y : Value w) (s : Dirt w d) :
    let backward := run f t false x y s
    run f t true x backward.1 backward.2 = (y,s) := by
  simp only [run_eq, Bool.false_eq_true, ↓reduceIte, sub_add_cancel]

def IsAdditive {w : Nat} (f : Value w → Value w) : Prop :=
  ∀ a b, f (add a b) = add (f a) (f b)

/-- Factors apply in left-to-right leaf order: right after left.
No interchange of factor maps is used. -/
def product {w d : Nat} (f : Nat → Value w → Value w) (t : Tree d)
    (x : Value w) : Value w :=
  match t with
  | .leaf _ label => f label x
  | .node left right => product f right (product f left x)

theorem product_additive {w d : Nat} (f : Nat → Value w → Value w)
    (hf : ∀ label, IsAdditive (f label)) (t : Tree d) : IsAdditive (product f t) := by
  induction t with
  | leaf depth label => exact hf label
  | node left right ihl ihr =>
    intro a b
    simp only [product, ihl a b, ihr (product f left a) (product f left b)]

/-- Ideal additive maps give the ordered product, independently of all dirt. -/
theorem delta_eq_product {w d : Nat} (f : Nat → Value w → Value w)
    (hf : ∀ label, IsAdditive (f label)) (t : Tree d) (x : Value w) (s : Dirt w d) :
    delta f t x s = product f t x := by
  induction t generalizing x with
  | leaf depth label => rfl
  | node left right ihl ihr =>
    simp only [delta, ihl, ihr, product]
    have hadd := product_additive f hf right (head s) (product f left x)
    rw [hadd, add_sub_left]

theorem ideal_execution {w d : Nat} (f : Nat → Value w → Value w)
    (hf : ∀ label, IsAdditive (f label)) (t : Tree d)
    (positive : Bool) (x y : Value w) (s : Dirt w d) :
    run f t positive x y s =
      (if positive then add y (product f t x) else sub y (product f t x), s) := by
  rw [run_eq, delta_eq_product f hf]

structure State (width depth : Nat) where
  source : Value width
  target : Value width
  dirty : Dirt width depth

def execute {w d : Nat} (f : Nat → Value w → Value w) (t : Tree d)
    (positive : Bool) (state : State w d) : State w d :=
  let result := run f t positive state.source state.target state.dirty
  ⟨state.source, result.1, result.2⟩

/-- Source restoration is the assumed completed-leaf interface; the scratch
restoration and target formula follow from the recursive semantics proof. -/
theorem full_execution {w d : Nat} (f : Nat → Value w → Value w) (t : Tree d)
    (positive : Bool) (state : State w d) :
    execute f t positive state =
      ⟨state.source,
       if positive then add state.target (delta f t state.source state.dirty)
         else sub state.target (delta f t state.source state.dirty),
       state.dirty⟩ := by
  simp only [execute, run_eq]

def twoLeaf : Tree 1 := .node (.leaf 0 0) (.leaf 0 1)
def nonlinearLeaves (label : Nat) (x : Value 1) : Value 1 :=
  if label = 0 then x else fun i => x i * x i

/-- Exact restoration alone does not imply independence from initial dirt. -/
theorem nonlinear_dirt_counterexample :
    delta nonlinearLeaves twoLeaf (fun _ => 1) (fun _ _ => 0) ≠
      delta nonlinearLeaves twoLeaf (fun _ => 1) (fun _ _ => 1) := by
  intro h
  have hi := congrFun h 0
  change (1 : Int) = 3 at hi
  omega

structure Instruction where
  factor : Nat
  source : Nat
  target : Nat
  positive : Bool
  deriving DecidableEq, Repr

def flip (i : Instruction) : Instruction := { i with positive := !i.positive }
def inverseWord (xs : List Instruction) : List Instruction := xs.reverse.map flip

theorem inverse_append (xs ys : List Instruction) :
    inverseWord (xs ++ ys) = inverseWord ys ++ inverseWord xs := by
  simp [inverseWord, List.reverse_append]

theorem inverse_involutive (xs : List Instruction) : inverseWord (inverseWord xs) = xs := by
  simp [inverseWord, List.map_reverse, List.map_map, Function.comp_def, flip]

/-- Address-level lowering of the same four-call macro grammar.
The caller assigns source/target below `fresh`; deeper scratch starts above it. -/
def positiveWord {d : Nat} (t : Tree d) (source target fresh : Nat) : List Instruction :=
  match t with
  | .leaf _ label => [⟨label, source, target, true⟩]
  | .node left right =>
    let a := positiveWord left source fresh (fresh+1)
    let b := positiveWord right fresh target (fresh+1)
    a ++ b ++ inverseWord a ++ inverseWord b

def word {d : Nat} (t : Tree d) (positive : Bool) (source target fresh : Nat) : List Instruction :=
  if positive then positiveWord t source target fresh
  else inverseWord (positiveWord t source target fresh)

theorem negative_node_order {d : Nat} (left right : Tree d) (source target fresh : Nat) :
    word (.node left right) false source target fresh =
      word right true fresh target (fresh+1) ++ word left true source fresh (fresh+1) ++
      word right false fresh target (fresh+1) ++ word left false source fresh (fresh+1) := by
  simp [word, positiveWord, inverse_append, inverse_involutive, List.append_assoc]

#print axioms run_eq
#print axioms scratch_restored
#print axioms positive_increment
#print axioms exact_inverse
#print axioms inverse_then_forward
#print axioms product_additive
#print axioms delta_eq_product
#print axioms ideal_execution
#print axioms full_execution
#print axioms nonlinear_dirt_counterexample
#print axioms inverse_involutive
#print axioms negative_node_order

end NonlinearEcho
