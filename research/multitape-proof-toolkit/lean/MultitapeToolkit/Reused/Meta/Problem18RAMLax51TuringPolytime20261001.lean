import MultitapeToolkit.Reused.Meta.Problem18RAMLax51BinaryWordEncoding20261001
import Mathlib.Computability.TuringMachine.Computable

set_option backward.isDefEq.respectTransparency false


/-!
---
title: Polynomial-time computation by a Turing machine
type: definition
---
A total function from finite lists of natural numbers to finite lists of
natural numbers is Turing-computable in polynomial time when a finite
multi-tape Turing machine transforms the canonical binary encoding of every
input into the canonical binary encoding of its value within a polynomial
number of steps in the encoded input length.

The underlying machine and time bound are mathlib's
`Turing.TM2ComputableInPolyTime`: a bundled finite multi-stack Turing machine
and a polynomial over the natural numbers. Taking `Nonempty` forgets the
computational content of the bundle and retains the proposition that such a
machine exists.
-/

set_option autoImplicit false

namespace Lax51.TuringPolytime

open Lax51.BinaryWordEncoding

/-- Polynomial-time computation, on the canonical binary word encoding, by
a finite multi-tape Turing machine. -/
def TuringPolytime (f : List ℕ → List ℕ) : Prop :=
  Nonempty (Turing.TM2ComputableInPolyTime encode encode f)

end Lax51.TuringPolytime
