# Fixed-order positive one-read substitution

## Local identity and legality

Consider a consecutive block of scalar additions `t_j += q_j x`. All
registers are at the same full frame; `x` is never a target. The block
contains no scale, frame change, child, adapter, wrapper or center event.
Each target retains its original position and signed coefficient. The
existing private coefficient stream `w` is cleared initially and finally.

Write `a_j = abs(q_j)`. Binary Horner preparation constructs `w = a_0 x`
after erasing an arbitrary incoming `w`. At every target update, the stream
holds `a_j x`, so adding/subtracting it realizes the required signed update.
The permitted transitions are either `w *= 2^k`, when `a_j/a_(j-1)=2^k`, or

```text
w *= 2^u
w += x
w *= 2^v
```

with `(a_(j-1)*2^u + 1)*2^v = a_j`. This identity is over exact complex
values, component by component; no division of the live source is needed.
All halvings are inherited exact dyadic scalar primitives. Induction over
the target updates proves the same live-register map for arbitrary dirty
inputs, with no incoming private-work dependence and zero outgoing work.
There is no new helper or recursive child. Existing source access is paid
once for each `w += x`.

For example, a real source coefficient changes from `1/2` to `3/2` with
the single operation `w += x`. Clearing and rebuilding the latter costs six
real-component primitives before its target update. The transition saves
five in that component, or ten across real and imaginary components.

## Complete cost in this class

For a positive reduced dyadic `a = A / 2^d`, the selected binary-Horner
preparation costs

```text
P(a) = 1 + (bit_length(A)-1) + popcount(A) + d
```

including its initial clear. A standalone addition costs `P(a)+2`, adding
one target accumulation and one final clear. A block of `m` additions costs

```text
P(a_0) + m + sum(transition_cost_j) + 1.
```

A pure shift costs `abs(k)`. A one-read transition costs
`abs(u)+1+abs(v)`. The alternative cut between consecutive additions costs
`1+P(a_j)` (previous final clear plus next preparation). A transition is
selected only if strictly cheaper than that cut. Since its endpoint
coefficient is fixed, the saving for each admissible adjacent edge is
independent of all other edges. Taking each strict minimum and splitting
at all other edges therefore minimizes cost in the specified fixed-order
class. Ties prefer reset, then pure shifts, then lexicographically ordered
`(cost,u,v)`. This claim includes the fixed binary-Horner preparation and
does not assert unrestricted circuit optimality.

The constructor enumerates 33 values of `u`; the equation uniquely
determines `v`, if it is an integer. The independent implementation
enumerates all 1,089 pairs directly using exact integers. Thus the omitted
`v` loop in the constructor does not reduce the claimed finite coverage.
All 780 distinct magnitude pairs and all 4,298 occurrences are accounted
for, including unprofitable/infeasible cases. All 269 selected one-read
transitions have unequal odd numerators.

The full-program recount pays unchanged macro lowering outside the blocks.
It counts all target updates, boundary clears and work preparation inside
them. Non-scalar events are unchanged and their hashes and paid recursive
profiles are recorded. The finite forward count is 224,422; the backward
count remains 257,280. With the existing adapter/compiler allowances the
orientation maximum, and hence the conservative local invoice, is unchanged.

## Prefix envelope

Let `N_x` be the positive L1 envelope of the fixed live source. The work
stream has envelope exactly `a N_x`: preparation, shifts and the new source
read use positive coefficients. They introduce no cancellation in the
envelope. In the one-read route its maximum coefficient is

```text
max(a, a*2^u + 1, b).
```

The pre-read value `a*2^u` is smaller than the middle value and the shifts
are monotone between endpoints. Require this maximum to be at most
`max(a, numerator(b))`. The old execution has already reached `a N_x`
and its binary-Horner preparation for `b` reaches
`numerator(b) N_x`. The replacement therefore never exceeds the old
prefix envelope. Pure shifts are monotone between `a` and `b` and satisfy
the same comparison. Original target updates and all their positive
envelopes are unchanged. This argument allows unequal incoming target and
source envelopes and composes across every block.

The literal full-program replay independently measures the exact positive
envelope. It agrees with both selected SPEC values, not merely the 192-bit
cap. The integer implementation checks each block's dirty-input matrix and
local envelope with a common scale of `2^(D+32)`, where `D` is the maximum
input-coefficient denominator exponent. Two shifts of at most 16 cannot
exhaust that grid; divisibility is checked before every right shift.

## Scope of evidence

The algebraic block argument explains substitution in the inherited scalar
model. Exhaustive enumeration certifies only the stated finite route class.
The all-column literal replay checks finite endpoints, clearing, accounting
and positive envelopes. The unchanged native replay checks the original
macro frame/wrapper obligations. These checks do not independently prove
the all-size multiplication theorem or integrate a new production private-
work contract. In particular, no exponent improvement follows from the
unchanged maximum local invoice.
