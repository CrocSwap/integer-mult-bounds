# Exact transition obligation and the symbolic lift

Fix a positive integer Q. For an axis with radix t>=2 and index 0<=j<t, let
A be a residue modulo Q. The modular invariant is

```text
v = A*j², Δ = A*(2j+1), E = U+v  (all modulo Q),
```

where U is the sum of the other axes' contributions.

## Ordinary increment

Under j+1<t, the source updates E and v by the old Δ, updates Δ by 2A,
and then increments j. The complete algebraic differences are

```text
A*j² + A*(2*j+1) - A*(j+1)² = 0,
A*(2*j+1) + 2*A - A*(2*(j+1)+1) = 0,
U + A*j² + A*(2*j+1) - (U + A*(j+1)²) = 0.
```

These are polynomial equalities over the integers, hence hold modulo every
positive Q. Radix, coefficient and the other axes remain unchanged.

## Wrapped increment

Under j=t-1, the source subtracts the old v from E and resets j=v=0,
Δ=A. The resulting phase is U and the axis contributes A*0²=0. In particular,
the reset of Δ is needed for the next use of the axis. The transition then
visits the preceding axis rather than emitting an intermediate phase.

## Composition and complete period

Order axes from slowest to fastest. For an address with k final digits, apply
the wrapped rule to those k trailing axes and then the ordinary rule to the
preceding axis, if present. Each local update preserves the sum invariant.
No earlier axis is touched. This is exactly mixed-radix lexicographic successor.
If all digits were final, every v is removed, E=0, every j=v=0 and Δ=A;
the source returns false. Induction over the number of wrapped axes proves
this composition for arbitrary dimension. Induction over addresses, starting
from the zero state, proves the exact stream and final restoration. This is a
written elementary argument, not a machine-checked control-flow theorem.

For a complete period T=product(t_i), including the last rollover, axis i is
visited once per combination of coordinates through i. Therefore

```text
visits = sum_i product_(j<=i) t_j
       = sum_i T / product_(j>i) t_j < 2T.
```

The strict geometric bound uses every radix being at least two. It does not
extend to arbitrary singleton-axis strings. The finite checker validates
per-transition instrumentation and sums it over its entire declared domain;
it does not use that sum to certify a physical tape implementation.

## Connection to the actual pinned Python source

The target is imported only after checking all five preserved source files.
The actual `advance` method is executed on independently implemented sparse
polynomials. Addition, subtraction, multiplication and powers operate in
Z[A_i,J_i,T_i]. Every modulo operation must use the same symbolic Q token.
Reduction can be erased because the quotient map into Z/QZ is a ring
homomorphism and none of the target's mathematical branches depends on a
residue value. Every nonconstant index comparison must match the explicitly
registered ordinary-branch guard. The wrapped test reduces to T_i<T_i and is
false. Unknown comparisons fail; they are not guessed or sampled.

`bit_length()` returns a dummy zero only for the source's diagnostic maximum.
Reading the pinned method shows that diagnostic does not influence any phase,
axis, branch, return flag or traversal counter. Concrete integer checks
separately validate the recorded upper bound. This erasure and the branch
assumptions are part of the verifier's trusted model, made explicit here.

For dimensions 1..6 and each possible carry suffix, every post-state polynomial
is compared with the invariant at the expected next address. All coefficient
differences vanish. These symbolic executions range over arbitrary integer
coefficients and index variables within their guards, not a finite selection of
coefficient values. The finite number of compound patterns does **not** alone
prove the arbitrary-dimension loop. The preceding composition argument supplies
that separate written step.

The symbolic lift establishes congruences, not canonical integer representatives.
The source's initialization `A=-s*(r/t) mod 2r` and its explicit positive-modulus
reductions supply canonical representatives in the valid source domain. The
checker independently tests initialization and every register's exact integer
value on its fixed finite domain. Six controls that pass the congruence stage
fail that separate layer, demonstrating why the two claims must stay distinct.

All positive controls, rejecting controls and polynomial-engine tests are
additional failure-detection evidence. They are not a formal proof of the
verifier or a discharge of the multiplication framework's inherited premises.
