module

public import Mathlib.Computability.TuringMachine.Computable
public import Mathlib.Analysis.SpecialFunctions.Pow.Real
public import Mathlib.Analysis.Asymptotics.Defs

/-!
# Integer multiplication below `n log n`: the statement

Everything in this file is Mathlib vocabulary. The machine model is Mathlib's
`Turing.FinTM2`: finitely many stacks, a finite control state, a finite label set and a
finite input alphabet, where one time step executes one label's loop-free statement.
Two stacks simulate one tape with constant overhead and a stack is a restricted tape, so
time on `FinTM2` agrees with multitape Turing machine time up to a constant factor.

The input `(a, b)` is Mathlib's `encodingProd` of two copies of `encodingNatBool`: the
LSB-first binary word of `a` over `Sum.inl` symbols followed by that of `b` over
`Sum.inr` symbols. Its length `n` is `Nat.size a + Nat.size b`. The output is the
canonical LSB-first binary word of `a * b`. The time function bounds the number of steps
on every input of length `n`, so it is a worst-case bound.
-/

@[expose] public section

open Turing Computability Asymptotics Filter

namespace IntegerMultBounds.MathlibTM2

/-- The input encoding: `a` in binary over `Sum.inl`, then `b` in binary over `Sum.inr`. -/
abbrev pairEnc : ℕ × ℕ → List (Bool ⊕ Bool) :=
  (encodingProd encodingNatBool encodingNatBool).encode

/-- A fixed finite multi-stack machine multiplies two naturals in worst-case time
`O(n (log n) ^ (1 - κ))`, where `n` is the total input length. -/
def MulInTime (κ : ℝ) : Prop :=
  ∃ M : TM2ComputableInTime pairEnc encodingNatBool.encode (fun p : ℕ × ℕ => p.1 * p.2),
    (fun n : ℕ => (M.time n : ℝ)) =O[atTop] fun n : ℕ => (n : ℝ) * Real.log n ^ (1 - κ)

/-- Integer multiplication below `n log n` on multitape Turing machines. -/
def Statement : Prop := ∃ κ : ℝ, 0 < κ ∧ MulInTime κ

example : encodingNatBool.encode 6 = [false, true, true] := by decide
example : pairEnc (6, 1) = [.inl false, .inl true, .inl true, .inr true] := by decide

end IntegerMultBounds.MathlibTM2
