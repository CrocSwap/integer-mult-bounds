import Mathlib.Tactic

set_option backward.isDefEq.respectTransparency false


/-!
IMP+: a structured while-language with scalar variables and named
arrays, given a big-step semantics indexed by a cost. It is the layer
at which the flatness of the machine is dealt with once and for all:
the compiler to machine programs lowers control flow to jumps and array
indexing to indirect addressing, and everything above IMP+ reasons
structurally.

IMP+ is the *unbounded* reference semantics: its values are natural
numbers, nothing is ever reduced modulo `2 ^ w`, and the word length
does not occur in this file at all. That is the whole point of the
tower — functional correctness and cost are proved on clean
natural-number arithmetic, and the word length enters exactly once, at
the boundary, through the value bound of `Bounds` and the simulation
theorem. The operators are the standard word-RAM operations at the
level of numbers: subtraction is truncated, division rounds down with
`x / 0 = 0`, the bitwise operations are those of `Nat`, and the shifts
are multiplication and division by a power of two. Six of them are
machine instructions; the other three — `or`, `xor` and `shiftr` — are
lowered by the compiler to fixed blocks of three or four instructions,
so the choice of operators here is not a choice about the machine.

Three design points carry the weight.

*Aliasing is impossible by construction.* An environment maps names to
values and names to arrays, so distinct names denote disjoint objects
and no statement anywhere in the tower has to reason about overlap.
This is what replaces separation logic.

*Out-of-bounds access is stuck, not defaulted.* Expression evaluation
is `Option`-valued and an out-of-range array read has no value; an
out-of-range store has no derivation. A semantics that defaulted to
zero would diverge from what the flat machine memory returns, and the
layout simulation would then be false.

*Input and output are commands.* The environment carries the two tapes
and `read`/`write` are ordinary constructs, so their cost is part of
the cost of the run and the compiled program needs neither a prologue
that copies the input into memory nor an epilogue that writes the
output out. Array lengths are not declared anywhere: they belong to the
initial environment, because the compiled machine program never
represents them — memory starts zeroed, so an array of any length is
there for free, and its length exists only to make an out-of-range
access stuck.

The cost of a derivation is the number of executed constructs, each
weighted by the size of the expressions it evaluates. Constants are
never tight anywhere in this development; this measure is chosen only
so that it is bounded below by the number of steps of the compiled
machine program divided by a program-dependent constant.

The binary operators are collected into one type `Bop` rather than
given one `Expr` constructor each: they all evaluate the same way and
compile to one block each, so a single `bin` node turns nine cases into
one everywhere downstream, and the six that are machine instructions
are told apart from the three that are lowered in exactly one place,
the compiler's `binCode`.
The nine familiar names are available as abbreviations, so `.add e f`
still writes a sum.
-/

namespace Lax13Proofs.Imp

/-- The binary operators of IMP+, one for each of the machine's
arithmetic and bitwise instructions. -/
inductive Bop
  /-- Addition. -/
  | add
  /-- Truncated subtraction. -/
  | sub
  /-- Multiplication. -/
  | mul
  /-- Division, rounding down, by zero yielding zero. -/
  | div
  /-- Bitwise conjunction. -/
  | and
  /-- Bitwise disjunction. -/
  | or
  /-- Bitwise exclusive or. -/
  | xor
  /-- Left shift, that is multiplication by a power of two. -/
  | shiftl
  /-- Right shift, that is division by a power of two. -/
  | shiftr
  deriving DecidableEq, Repr

/-- The meaning of a binary operator on natural numbers. It is the
meaning of the corresponding machine instruction with the truncation
removed. -/
def Bop.apply : Bop → ℕ → ℕ → ℕ
  | add, m, n => m + n
  | sub, m, n => m - n
  | mul, m, n => m * n
  | div, m, n => m / n
  | and, m, n => Nat.land m n
  | or, m, n => Nat.lor m n
  | xor, m, n => Nat.xor m n
  | shiftl, m, n => m * 2 ^ n
  | shiftr, m, n => m / 2 ^ n

@[simp] theorem Bop.apply_add (m n : ℕ) : Bop.add.apply m n = m + n := rfl
@[simp] theorem Bop.apply_sub (m n : ℕ) : Bop.sub.apply m n = m - n := rfl
@[simp] theorem Bop.apply_mul (m n : ℕ) : Bop.mul.apply m n = m * n := rfl
@[simp] theorem Bop.apply_div (m n : ℕ) : Bop.div.apply m n = m / n := rfl
@[simp] theorem Bop.apply_and (m n : ℕ) : Bop.and.apply m n = Nat.land m n := rfl
@[simp] theorem Bop.apply_or (m n : ℕ) : Bop.or.apply m n = Nat.lor m n := rfl
@[simp] theorem Bop.apply_xor (m n : ℕ) : Bop.xor.apply m n = Nat.xor m n := rfl
@[simp] theorem Bop.apply_shiftl (m n : ℕ) : Bop.shiftl.apply m n = m * 2 ^ n := rfl
@[simp] theorem Bop.apply_shiftr (m n : ℕ) : Bop.shiftr.apply m n = m / 2 ^ n := rfl

/-- Arithmetic expressions: literals, scalar variables, array reads, and
a binary operator applied to two expressions. -/
inductive Expr
  /-- The literal `n`. -/
  | lit (n : ℕ)
  /-- The value of the scalar variable `x`. -/
  | var (x : String)
  /-- The entry of array `a` at the position given by `i`. -/
  | get (a : String) (i : Expr)
  /-- The operator `op` applied to the values of two expressions. -/
  | bin (op : Bop) (e f : Expr)

/-- The sum of two expressions. -/
abbrev Expr.add (e f : Expr) : Expr := .bin .add e f
/-- The truncated difference of two expressions. -/
abbrev Expr.sub (e f : Expr) : Expr := .bin .sub e f
/-- The product of two expressions. -/
abbrev Expr.mul (e f : Expr) : Expr := .bin .mul e f
/-- The quotient of two expressions. -/
abbrev Expr.div (e f : Expr) : Expr := .bin .div e f
/-- The bitwise conjunction of two expressions. -/
abbrev Expr.and (e f : Expr) : Expr := .bin .and e f
/-- The bitwise disjunction of two expressions. -/
abbrev Expr.or (e f : Expr) : Expr := .bin .or e f
/-- The bitwise exclusive or of two expressions. -/
abbrev Expr.xor (e f : Expr) : Expr := .bin .xor e f
/-- The first expression shifted left by the second. -/
abbrev Expr.shiftl (e f : Expr) : Expr := .bin .shiftl e f
/-- The first expression shifted right by the second. -/
abbrev Expr.shiftr (e f : Expr) : Expr := .bin .shiftr e f

@[simp] theorem Expr.add_def (e f : Expr) : Expr.add e f = .bin .add e f := rfl
@[simp] theorem Expr.sub_def (e f : Expr) : Expr.sub e f = .bin .sub e f := rfl
@[simp] theorem Expr.mul_def (e f : Expr) : Expr.mul e f = .bin .mul e f := rfl
@[simp] theorem Expr.div_def (e f : Expr) : Expr.div e f = .bin .div e f := rfl
@[simp] theorem Expr.and_def (e f : Expr) : Expr.and e f = .bin .and e f := rfl
@[simp] theorem Expr.or_def (e f : Expr) : Expr.or e f = .bin .or e f := rfl
@[simp] theorem Expr.xor_def (e f : Expr) : Expr.xor e f = .bin .xor e f := rfl
@[simp] theorem Expr.shiftl_def (e f : Expr) : Expr.shiftl e f = .bin .shiftl e f := rfl
@[simp] theorem Expr.shiftr_def (e f : Expr) : Expr.shiftr e f = .bin .shiftr e f := rfl

/-- Conditions: equality and strict order of two expressions. -/
inductive Cond
  /-- The two expressions have equal values. -/
  | eq (e f : Expr)
  /-- The first value is smaller than the second. -/
  | lt (e f : Expr)

/-- Commands: the usual structured constructs, a store into an array
cell, and the two tape operations. -/
inductive Com
  /-- Do nothing. -/
  | skip
  /-- Assign the value of `e` to the scalar variable `x`. -/
  | assign (x : String) (e : Expr)
  /-- Store the value of `e` into array `a` at position `i`. -/
  | store (a : String) (i e : Expr)
  /-- Run `c`, then `d`. -/
  | seq (c d : Com)
  /-- Run `c` or `d` according to the condition. -/
  | ite (b : Cond) (c d : Com)
  /-- Run the body while the condition holds. -/
  | while (b : Cond) (c : Com)
  /-- Read the next number of the input into the scalar variable `x`. -/
  | read (x : String)
  /-- Write the value of `e` to the output. -/
  | write (e : Expr)

/-- An environment: the value of every scalar variable, the contents of
every array, and the two tapes. Distinct names are distinct objects, so
no two names can alias. -/
structure Env where
  /-- The value of each scalar variable. -/
  vars : String → ℕ
  /-- The contents of each array. -/
  arrs : String → List ℕ
  /-- The input not yet read. -/
  inp : List ℕ
  /-- The output written so far. -/
  out : List ℕ

/-- The environment with the scalar variable `x` set to `v`. -/
def Env.setVar (σ : Env) (x : String) (v : ℕ) : Env :=
  { σ with vars := fun y => if y = x then v else σ.vars y }

/-- The environment with position `i` of array `a` set to `v`. -/
def Env.setArr (σ : Env) (a : String) (i v : ℕ) : Env :=
  { σ with arrs := fun b => if b = a then (σ.arrs a).set i v else σ.arrs b }

/-- The value of an expression, or `none` if an array is read out of
range. -/
def Expr.eval : Expr → Env → Option ℕ
  | lit n, _ => some n
  | var x, σ => some (σ.vars x)
  | get a i, σ => (i.eval σ).bind fun k => (σ.arrs a)[k]?
  | bin op e f, σ => (e.eval σ).bind fun m => (f.eval σ).map fun n => op.apply m n

/-- The size of an expression, which is what evaluating it costs. -/
def Expr.size : Expr → ℕ
  | lit _ => 1
  | var _ => 1
  | get _ i => i.size + 1
  | bin _ e f => e.size + f.size + 1

/-- Whether a condition holds, or `none` if an array is read out of
range. -/
def Cond.eval : Cond → Env → Option Bool
  | eq e f, σ => (e.eval σ).bind fun m => (f.eval σ).map fun n => m == n
  | lt e f, σ => (e.eval σ).bind fun m => (f.eval σ).map fun n => decide (m < n)

/-- The size of a condition, which is what evaluating it costs. -/
def Cond.size : Cond → ℕ
  | eq e f => e.size + f.size + 1
  | lt e f => e.size + f.size + 1

/-- `BigStep c σ σ' k`: running `c` in `σ` terminates in `σ'` at cost
`k`. There is no derivation when an array is accessed out of range, so
such a program is stuck rather than continuing with a default value. -/
inductive BigStep : Com → Env → Env → ℕ → Prop
  /-- `skip` changes nothing. -/
  | skip {σ : Env} : BigStep .skip σ σ 1
  /-- An assignment evaluates its expression and updates the
  variable. -/
  | assign {σ : Env} {x : String} {e : Expr} {v : ℕ} (h : e.eval σ = some v) :
      BigStep (.assign x e) σ (σ.setVar x v) (1 + e.size)
  /-- A store evaluates position and value and updates the array; it
  requires the position to be in range. -/
  | store {σ : Env} {a : String} {i e : Expr} {k v : ℕ}
      (hi : i.eval σ = some k) (he : e.eval σ = some v)
      (hk : k < (σ.arrs a).length) :
      BigStep (.store a i e) σ (σ.setArr a k v) (1 + i.size + e.size)
  /-- Costs of a sequence add up. -/
  | seq {c d : Com} {σ σ' σ'' : Env} {k k' : ℕ} :
      BigStep c σ σ' k → BigStep d σ' σ'' k' →
      BigStep (.seq c d) σ σ'' (k + k')
  /-- A conditional whose condition holds runs its first branch. -/
  | ite_true {b : Cond} {c d : Com} {σ σ' : Env} {k : ℕ}
      (hb : b.eval σ = some true) (hc : BigStep c σ σ' k) :
      BigStep (.ite b c d) σ σ' (1 + b.size + k)
  /-- A conditional whose condition fails runs its second branch. -/
  | ite_false {b : Cond} {c d : Com} {σ σ' : Env} {k : ℕ}
      (hb : b.eval σ = some false) (hd : BigStep d σ σ' k) :
      BigStep (.ite b c d) σ σ' (1 + b.size + k)
  /-- A loop whose condition holds runs its body once and then again. -/
  | while_true {b : Cond} {c : Com} {σ σ' σ'' : Env} {k k' : ℕ}
      (hb : b.eval σ = some true) (hc : BigStep c σ σ' k)
      (hw : BigStep (.while b c) σ' σ'' k') :
      BigStep (.while b c) σ σ'' (1 + b.size + k + k')
  /-- A loop whose condition fails does nothing. -/
  | while_false {b : Cond} {c : Com} {σ : Env} (hb : b.eval σ = some false) :
      BigStep (.while b c) σ σ (1 + b.size)
  /-- A read takes the next number off the input; there is no
  derivation once the input is exhausted, just as the machine halts on
  a read from an exhausted tape. -/
  | read {σ : Env} {x : String} {v : ℕ} {rest : List ℕ} (h : σ.inp = v :: rest) :
      BigStep (.read x) σ { σ.setVar x v with inp := rest } 1
  /-- A write appends the value of its expression to the output. -/
  | write {σ : Env} {e : Expr} {v : ℕ} (h : e.eval σ = some v) :
      BigStep (.write e) σ { σ with out := σ.out ++ [v] } (1 + e.size)

/-- The semantics is deterministic in both the final environment and
the cost: a command run in a given environment has at most one outcome.
So the cost of a terminating run is a function of the program and its
input, not a quantity the prover gets to choose. -/
theorem BigStep.unique {c : Com} {σ σ₁ σ₂ : Env} {k₁ k₂ : ℕ}
    (h₁ : BigStep c σ σ₁ k₁) (h₂ : BigStep c σ σ₂ k₂) : σ₁ = σ₂ ∧ k₁ = k₂ := by
  induction h₁ generalizing σ₂ k₂ with
  | skip => cases h₂; exact ⟨rfl, rfl⟩
  | assign h => cases h₂ with
    | assign h' => rw [h] at h'; cases h'; exact ⟨rfl, rfl⟩
  | store hi he _ => cases h₂ with
    | store hi' he' _ =>
      rw [hi] at hi'; rw [he] at he'; cases hi'; cases he'; exact ⟨rfl, rfl⟩
  | seq _ _ ih ih' => cases h₂ with
    | seq h h' =>
      obtain ⟨rfl, rfl⟩ := ih h
      obtain ⟨rfl, rfl⟩ := ih' h'
      exact ⟨rfl, rfl⟩
  | ite_true hb _ ih => cases h₂ with
    | ite_true hb' h => obtain ⟨rfl, rfl⟩ := ih h; exact ⟨rfl, rfl⟩
    | ite_false hb' _ => rw [hb] at hb'; exact absurd hb' (by simp)
  | ite_false hb _ ih => cases h₂ with
    | ite_true hb' _ => rw [hb] at hb'; exact absurd hb' (by simp)
    | ite_false hb' h => obtain ⟨rfl, rfl⟩ := ih h; exact ⟨rfl, rfl⟩
  | while_true hb _ _ ih ih' => cases h₂ with
    | while_true hb' h h' =>
      obtain ⟨rfl, rfl⟩ := ih h
      obtain ⟨rfl, rfl⟩ := ih' h'
      exact ⟨rfl, rfl⟩
    | while_false hb' => rw [hb] at hb'; exact absurd hb' (by simp)
  | while_false hb => cases h₂ with
    | while_true hb' _ _ => rw [hb] at hb'; exact absurd hb' (by simp)
    | while_false hb' => exact ⟨rfl, rfl⟩
  | read h => cases h₂ with
    | read h' => rw [h] at h'; cases h'; exact ⟨rfl, rfl⟩
  | write h => cases h₂ with
    | write h' => rw [h] at h'; cases h'; exact ⟨rfl, rfl⟩

/-- The initial environment on input `x`: every scalar zero, the array
`a` holding `ext a` zeros, nothing written yet. The array lengths are
chosen by whoever uses the simulation theorem: an array costs nothing,
since the machine's memory starts zeroed, and the lengths exist only to
make an out-of-range access stuck. -/
def initEnv (ext : String → ℕ) (x : List ℕ) : Env where
  vars := fun _ => 0
  arrs := fun a => List.replicate (ext a) 0
  inp := x
  out := []

end Lax13Proofs.Imp
