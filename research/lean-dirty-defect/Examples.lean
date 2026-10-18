import Bound
/- Prepared for ywz65 with OpenAI Codex assistance. Apache-2.0.
   See README for the formal/external boundary and predecessor credit. -/
namespace DirtyBound
def absq (x : Rat) : Rat := if x < 0 then -x else x
theorem absq_nonneg (x : Rat) : 0 ≤ absq x := by unfold absq; split <;> grind
theorem absq_add (x y : Rat) : absq (x+y) ≤ absq x + absq y := by
  unfold absq; split <;> split <;> split <;> grind
theorem absq_sub (x y : Rat) : absq (x-y) ≤ absq x + absq y := by
  unfold absq; split <;> split <;> split <;> grind
def unitNorm : Gauge (Fin 1) where
  norm := fun x => absq (x 0)
  nonneg := fun x => absq_nonneg (x 0)
  add_bound := fun x y => absq_add (x 0) (y 0)
  sub_bound := fun x y => absq_sub (x 0) (y 0)
def allSources : Domain (Fin 1) where
  mem := fun _ => True
  add_mem := by intros; trivial
  sub_mem := by intros; trivial
def twice : Shadow (Fin 1) where
  map := fun x i => 2*x i
  add_map := by intros; funext i; simp only [add]; grind
  sub_map := by intros; funext i; simp only [sub]; grind
def noisy (k : Rat) (x : V (Fin 1)) : V (Fin 1) :=
  fun i => k*x i + if x i ≤ 0 then -1 else 1
theorem twice_lip : Lipschitz unitNorm twice 2 := by
  intro x
  simp only [unitNorm, twice]
  unfold absq
  split <;> split <;> grind
theorem noisy_defect : Defect allSources unitNorm (noisy 2) twice 1 := by
  intro x _
  simp only [unitNorm, twice, sub, noisy]
  split <;> unfold absq <;> split <;> grind
theorem nonlinear_example (t : Tree) (d : Nat → V (Fin 1)) (x : V (Fin 1)) :
    unitNorm.norm (sub (delta (fun _ => noisy 2) t d x)
      ((product (fun _ => twice) t).map x)) ≤
      (leaves t : Rat) * 2^(leaves t-1) := by
  have h := all_tree_error allSources unitNorm (fun _ => noisy 2) (fun _ => twice)
    2 1 (by decide) (by decide) (fun _ => twice_lip) (fun _ => noisy_defect)
    (by intro _ _ _; trivial) t d (by intro _; trivial) x (by trivial)
  simpa using h
def pairTree : Tree := .node (.leaf 0) (.leaf 1)
theorem factor_two_needed :
    absq (delta (fun _ => noisy 2) pairTree (fun _ _ => 0) (fun _ => 1) 0 - 4) = 4 := by
  simp only [delta, pairTree, commutator, add, sub, noisy, absq]
  grind
theorem lower_L_fails :
    absq (delta (fun _ => noisy 1) pairTree (fun _ _ => 0) (fun _ => 1) 0 - 1) = 3 := by
  simp only [delta, pairTree, commutator, add, sub, noisy, absq]
  grind
end DirtyBound
