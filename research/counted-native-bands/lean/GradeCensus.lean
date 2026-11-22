import Mathlib.Algebra.BigOperators.Group.List.Basic
import Mathlib.Tactic.Ring

/-! Rank products and multiplicities for ordered time labels. -/
namespace GradeCensus

abbrev Table := List (ℕ × ℕ)

def value (s : Table) (f : ℕ → ℕ) : ℕ :=
  (s.map fun q => q.2 * f q.1).sum

def literal (labels : List ℕ) (f : ℕ → ℕ) : ℕ :=
  (labels.map f).sum

def represents (s : Table) (labels : List ℕ) : Prop :=
  ∀ f, value s f = literal labels f

def joined (s t : Table) : Table :=
  s.flatMap fun a => t.map fun b => (a.1 * b.1, a.2 * b.2)

def paths (s t : List ℕ) : List ℕ :=
  s.flatMap fun a => t.map fun b => a*b

theorem sameGrade (k u v : ℕ) (rest : Table) (f : ℕ → ℕ) :
    value ((k,u)::(k,v)::rest) f = value ((k,u+v)::rest) f := by
  simp [value, add_mul, Nat.add_assoc]

theorem joined_value (s t : Table) (f : ℕ → ℕ) :
    value (joined s t) f = value s (fun k => value t (fun r => f (k*r))) := by
  induction s with
  | nil => simp [value, joined]
  | cons a s ih =>
    have h (u : Table) :
        value (u.map fun b => (a.1*b.1, a.2*b.2)) f =
        a.2 * value u (fun r => f (a.1*r)) := by
      induction u with
      | nil => simp [value]
      | cons b u hu =>
        simp only [List.map_cons, value, List.sum_cons] at hu ⊢
        rw [hu, Nat.mul_add, Nat.mul_assoc]
    simpa [joined, value, List.sum_append, Function.comp_def] using
      congrArg₂ (· + ·) (h t) ih

theorem paths_value (s t : List ℕ) (f : ℕ → ℕ) :
    literal (paths s t) f = literal s (fun k => literal t (fun r => f (k*r))) := by
  induction s with
  | nil => simp [literal, paths]
  | cons a s ih =>
    simpa [literal, paths, List.sum_append, Function.comp_def] using
      congrArg (fun n => literal t (fun r => f (a*r)) + n) ih

theorem composition {s t : Table} {a b : List ℕ}
    (hs : represents s a) (ht : represents t b) :
    represents (joined s t) (paths a b) := by
  intro f
  rw [joined_value, paths_value, hs]
  exact congrArg (literal a) (funext fun k => ht (fun r => f (k*r)))

#print axioms GradeCensus.sameGrade
#print axioms GradeCensus.composition
end GradeCensus
