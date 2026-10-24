import Mathproof.Meta.Problem18RAMLax13ProofsImp20261001

set_option backward.isDefEq.respectTransparency false


/-!
The no-overflow side of the pipeline.

The machine reduces every value it produces modulo `2 ^ w`; IMP+ does
not. The two therefore agree exactly when no value of the IMP+ run
reaches `2 ^ w`, and that is the only extra obligation the pipeline
asks of its users. This file says what "no value of the run reaches
`B`" means, in the form the simulation consumes and the reasoning layer
can compose.

The bound is threaded through the big-step derivation. `Expr.evalB B`
is expression evaluation that additionally gets stuck as soon as some
value it produces reaches `B` — not only the value of the whole
expression, but the value of every subexpression, since `sub`, `div`,
the bitwise operators and the right shift can all return a small value
from large arguments, and the machine truncates the arguments too.
`BigStepB B` is then the big-step semantics driven by `Expr.evalB B`,
with the same constructors, the same costs and the same shape; it is a
refinement of `BigStep`, not a competitor to it, and `BigStepB.bigStep`
projects one to the other.

This is one derivation carrying two facts, which is what makes the
reasoning layer cheap: a Hoare-style rule proved for `BigStepB`
establishes cost and boundedness at once, and the plain semantics is
recovered by projection wherever functional correctness is argued.

Values that enter the run from the input tape are not produced by any
expression, so they are bounded separately, by `Env.InpBounded`; this
is the hypothesis that becomes "every entry of the input fits into a
word" at the boundary, where the concept's admissible sets already
carry conditions of that shape.
-/

namespace Lax13Proofs.Imp

/-- The value `v`, or `none` when `v` does not fit below `B`. -/
def fit (B v : ℕ) : Option ℕ := if v < B then some v else none

theorem fit_eq_some {B v u : ℕ} : fit B v = some u ↔ u = v ∧ v < B := by
  constructor
  · intro h
    by_cases hv : v < B
    · rw [fit, if_pos hv] at h
      exact ⟨(Option.some.inj h).symm, hv⟩
    · rw [fit, if_neg hv] at h; exact absurd h (by simp)
  · rintro ⟨rfl, h⟩; rw [fit, if_pos h]

theorem fit_self {B v : ℕ} (h : v < B) : fit B v = some v := by rw [fit, if_pos h]

/-! ### Bounded evaluation -/

/-- Expression evaluation that also refuses every value reaching `B`.
Every subexpression is checked, not only the outermost one, because the
machine truncates the arguments of an operator as well as its
result. -/
def Expr.evalB (B : ℕ) : Expr → Env → Option ℕ
  | lit n, _ => fit B n
  | var x, σ => fit B (σ.vars x)
  | get a i, σ => (i.evalB B σ).bind fun k => ((σ.arrs a)[k]?).bind (fit B)
  | bin op e f, σ =>
      (e.evalB B σ).bind fun m => (f.evalB B σ).bind fun n => fit B (op.apply m n)

/-- Bounded evaluation is evaluation, and its value is below `B`. The
two halves are used separately and are stated separately below; they
are proved together because the induction needs both. -/
theorem Expr.eval_and_lt_of_evalB {B : ℕ} {σ : Env} {e : Expr} {v : ℕ}
    (h : e.evalB B σ = some v) : e.eval σ = some v ∧ v < B := by
  induction e generalizing v with
  | lit n =>
      rw [Expr.evalB, fit_eq_some] at h
      obtain ⟨rfl, hn⟩ := h
      exact ⟨rfl, hn⟩
  | var x =>
      rw [Expr.evalB, fit_eq_some] at h
      obtain ⟨rfl, hn⟩ := h
      exact ⟨rfl, hn⟩
  | get a i ih =>
      rw [Expr.evalB, Option.bind_eq_some_iff] at h
      obtain ⟨k, hk, h⟩ := h
      rw [Option.bind_eq_some_iff] at h
      obtain ⟨u, hu, h⟩ := h
      rw [fit_eq_some] at h
      obtain ⟨rfl, hlt⟩ := h
      exact ⟨by rw [Expr.eval, (ih hk).1]; exact hu, hlt⟩
  | bin op e f ihe ihf =>
      rw [Expr.evalB, Option.bind_eq_some_iff] at h
      obtain ⟨m, hm, h⟩ := h
      rw [Option.bind_eq_some_iff] at h
      obtain ⟨n, hn, h⟩ := h
      rw [fit_eq_some] at h
      obtain ⟨rfl, hlt⟩ := h
      exact ⟨by rw [Expr.eval, (ihe hm).1, (ihf hn).1]; rfl, hlt⟩

/-- Bounded evaluation is evaluation. -/
theorem Expr.eval_of_evalB {B : ℕ} {σ : Env} {e : Expr} {v : ℕ}
    (h : e.evalB B σ = some v) : e.eval σ = some v := (eval_and_lt_of_evalB h).1

/-- The value of a bounded evaluation is below the bound. -/
theorem Expr.lt_of_evalB {B : ℕ} {σ : Env} {e : Expr} {v : ℕ}
    (h : e.evalB B σ = some v) : v < B := (eval_and_lt_of_evalB h).2

/-- Condition evaluation with the same bound on the two operands. -/
def Cond.evalB (B : ℕ) : Cond → Env → Option Bool
  | eq e f, σ => (e.evalB B σ).bind fun m => (f.evalB B σ).map fun n => m == n
  | lt e f, σ => (e.evalB B σ).bind fun m => (f.evalB B σ).map fun n => decide (m < n)

theorem Cond.eval_of_evalB {B : ℕ} {σ : Env} {b : Cond} {r : Bool}
    (h : b.evalB B σ = some r) : b.eval σ = some r := by
  cases b with
  | eq e f =>
      rw [Cond.evalB, Option.bind_eq_some_iff] at h
      obtain ⟨m, hm, h⟩ := h
      rw [Option.map_eq_some_iff] at h
      obtain ⟨n, hn, rfl⟩ := h
      rw [Cond.eval, Expr.eval_of_evalB hm, Expr.eval_of_evalB hn]; rfl
  | lt e f =>
      rw [Cond.evalB, Option.bind_eq_some_iff] at h
      obtain ⟨m, hm, h⟩ := h
      rw [Option.map_eq_some_iff] at h
      obtain ⟨n, hn, rfl⟩ := h
      rw [Cond.eval, Expr.eval_of_evalB hm, Expr.eval_of_evalB hn]; rfl

/-! ### The input tape -/

/-- Every number still on the input tape of `σ` is below `B`. Values
read from the tape are the only ones a run produces that no expression
evaluated, so they are the only ones needing a bound of their own. -/
def Env.InpBounded (B : ℕ) (σ : Env) : Prop := ∀ v ∈ σ.inp, v < B

/-! ### The bounded big-step semantics -/

/-- `BigStepB B c σ σ' k`: the big-step semantics of `Imp`, driven by
bounded evaluation. A derivation is a derivation of `BigStep` in which
every value produced by an expression is below `B`. -/
inductive BigStepB (B : ℕ) : Com → Env → Env → ℕ → Prop
  /-- `skip` changes nothing. -/
  | skip {σ : Env} : BigStepB B .skip σ σ 1
  /-- An assignment evaluates its expression and updates the
  variable. -/
  | assign {σ : Env} {x : String} {e : Expr} {v : ℕ} (h : e.evalB B σ = some v) :
      BigStepB B (.assign x e) σ (σ.setVar x v) (1 + e.size)
  /-- A store evaluates position and value and updates the array; it
  requires the position to be in range. -/
  | store {σ : Env} {a : String} {i e : Expr} {k v : ℕ}
      (hi : i.evalB B σ = some k) (he : e.evalB B σ = some v)
      (hk : k < (σ.arrs a).length) :
      BigStepB B (.store a i e) σ (σ.setArr a k v) (1 + i.size + e.size)
  /-- Costs of a sequence add up. -/
  | seq {c d : Com} {σ σ' σ'' : Env} {k k' : ℕ} :
      BigStepB B c σ σ' k → BigStepB B d σ' σ'' k' →
      BigStepB B (.seq c d) σ σ'' (k + k')
  /-- A conditional whose condition holds runs its first branch. -/
  | ite_true {b : Cond} {c d : Com} {σ σ' : Env} {k : ℕ}
      (hb : b.evalB B σ = some true) (hc : BigStepB B c σ σ' k) :
      BigStepB B (.ite b c d) σ σ' (1 + b.size + k)
  /-- A conditional whose condition fails runs its second branch. -/
  | ite_false {b : Cond} {c d : Com} {σ σ' : Env} {k : ℕ}
      (hb : b.evalB B σ = some false) (hd : BigStepB B d σ σ' k) :
      BigStepB B (.ite b c d) σ σ' (1 + b.size + k)
  /-- A loop whose condition holds runs its body once and then again. -/
  | while_true {b : Cond} {c : Com} {σ σ' σ'' : Env} {k k' : ℕ}
      (hb : b.evalB B σ = some true) (hc : BigStepB B c σ σ' k)
      (hw : BigStepB B (.while b c) σ' σ'' k') :
      BigStepB B (.while b c) σ σ'' (1 + b.size + k + k')
  /-- A loop whose condition fails does nothing. -/
  | while_false {b : Cond} {c : Com} {σ : Env} (hb : b.evalB B σ = some false) :
      BigStepB B (.while b c) σ σ (1 + b.size)
  /-- A read takes the next number off the input. -/
  | read {σ : Env} {x : String} {v : ℕ} {rest : List ℕ} (h : σ.inp = v :: rest) :
      BigStepB B (.read x) σ { σ.setVar x v with inp := rest } 1
  /-- A write appends the value of its expression to the output. -/
  | write {σ : Env} {e : Expr} {v : ℕ} (h : e.evalB B σ = some v) :
      BigStepB B (.write e) σ { σ with out := σ.out ++ [v] } (1 + e.size)

/-- A bounded derivation is a derivation: same final environment, same
cost. This is how functional correctness and cost, proved once against
the unbounded reference semantics, are available to a user who works
with the bounded one. -/
theorem BigStepB.bigStep {B : ℕ} {c : Com} {σ σ' : Env} {k : ℕ}
    (h : BigStepB B c σ σ' k) : BigStep c σ σ' k := by
  induction h with
  | skip => exact .skip
  | assign h => exact .assign (Expr.eval_of_evalB h)
  | store hi he hk => exact .store (Expr.eval_of_evalB hi) (Expr.eval_of_evalB he) hk
  | seq _ _ ih ih' => exact .seq ih ih'
  | ite_true hb _ ih => exact .ite_true (Cond.eval_of_evalB hb) ih
  | ite_false hb _ ih => exact .ite_false (Cond.eval_of_evalB hb) ih
  | while_true hb _ _ ih ih' => exact .while_true (Cond.eval_of_evalB hb) ih ih'
  | while_false hb => exact .while_false (Cond.eval_of_evalB hb)
  | read h => exact .read h
  | write h => exact .write (Expr.eval_of_evalB h)

/-- A run consumes the input tape, so a bound on it is preserved. -/
theorem BigStepB.inpBounded {B : ℕ} {c : Com} {σ σ' : Env} {k : ℕ}
    (h : BigStepB B c σ σ' k) (hσ : σ.InpBounded B) : σ'.InpBounded B := by
  induction h with
  | skip => exact hσ
  | assign _ => exact fun v hv => hσ v hv
  | store _ _ _ => exact fun v hv => hσ v hv
  | seq _ _ ih ih' => exact ih' (ih hσ)
  | ite_true _ _ ih => exact ih hσ
  | ite_false _ _ ih => exact ih hσ
  | while_true _ _ _ ih ih' => exact ih' (ih hσ)
  | while_false _ => exact hσ
  | read h =>
      intro v hv
      refine hσ v ?_
      rw [h]
      exact List.mem_cons_of_mem _ hv
  | write _ => exact fun v hv => hσ v hv

/-- The initial environment inherits the bound from the input word. -/
theorem initEnv_inpBounded {B : ℕ} (ext : String → ℕ) {x : List ℕ}
    (hx : ∀ v ∈ x, v < B) : (initEnv ext x).InpBounded B := hx

end Lax13Proofs.Imp
