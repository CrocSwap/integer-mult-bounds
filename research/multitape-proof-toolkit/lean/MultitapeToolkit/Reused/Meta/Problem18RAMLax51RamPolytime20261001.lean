import MultitapeToolkit.Reused.Meta.Problem18RAMLax13Ram20261001
import MultitapeToolkit.Reused.Meta.Problem18RAMLax51BinaryWordEncoding20261001
import Mathlib.Algebra.Polynomial.Eval.Defs

set_option backward.isDefEq.respectTransparency false


/-!
---
title: Polynomial-time computation by a word RAM
type: definition
---
A total function from finite lists of natural numbers to finite lists of
natural numbers is computable in polynomial time by a word RAM when there
are one uniform program, a polynomial word-length bound, and a polynomial
running-time bound with the following property.

For an input whose canonical binary encoding has length *n*, the RAM receives
the physical tape `x.length :: x`. Every tape and output entry fits in a word
of the bounded length, and at every word length at least that bound the program
returns the exact output within the bounded number of RAM instructions. Both
polynomials are evaluated at *n*.

Measuring input size in bits, rather than in the number of entries, puts the
RAM and Turing machine on the same input-size scale. Requiring correctness
at every sufficiently large word length makes the program uniform in the
word length. Requiring a polynomial sufficient word length is what permits
a Turing machine to simulate each operation on a word in polynomial time.
No lower bound such as logarithmic word length is separately necessary:
the explicit fitting condition says directly that the length prefix, all
native input entries, and all exact output entries are representable.
-/

set_option autoImplicit false

namespace Lax51.RamPolytime

open Lax13.Ram
open Lax51.BinaryWordEncoding

/-- Every entry of `x` is representable by a word of `w` bits. -/
def FitsInWords (w : ℕ) (x : List ℕ) : Prop :=
  ∀ a ∈ x, a < 2 ^ w

/-- Polynomial-time computation by one uniform word-RAM program, measured
in the bit-size of the logical word-list input.  The physical input tape is
length-prefixed, so a program can consume exactly the logical input and then
continue computing even though the underlying RAM's exhausted-input behavior
is an unconditional halt. -/
def RamPolytime (f : List ℕ → List ℕ) : Prop :=
  ∃ (p : Program) (wordBound timeBound : Polynomial ℕ),
    ∀ x : List ℕ,
      FitsInWords (wordBound.eval (bitSize x)) ((x.length :: x) ++ f x) ∧
        ∀ w : ℕ, wordBound.eval (bitSize x) ≤ w →
          ∃ t ≤ timeBound.eval (bitSize x),
            RunsTo w p (x.length :: x) (f x) t

end Lax51.RamPolytime
