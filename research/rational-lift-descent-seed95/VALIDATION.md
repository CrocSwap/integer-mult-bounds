# Verification record

Verified on 2026-10-13, macOS 26.5.2 arm64, with CPython 3.11.15 and 3.14.8.
Both interpreters use only their standard libraries. There is no numeric
tolerance, external solver, compiler, or unpinned executable dependency in
the mathematical checks. RTK 0.51.0 was the shell command proxy.

The normal and optimized verifier output is:

```text
PASS_RATIONAL_LIFT_DESCENT witnesses=9 scalar_lifts=162 controls=5 finite_field_pairs=4 new_kappa=false
```

The relocated CLI test passes on both interpreters:

```text
PASS_RATIONAL_LIFT_CLI relocated=1 certificate_rejections=4 source_rejections=1
```

The committed certificate is byte-identical to the output of `--emit`.
Its SHA256 is
`1d4cd17ba4970a62624d378c402422c074e5d5dcc73a3700df10077bc618f0d7`.
The default verifier also distinguishes Boolean and integer JSON values.
All checks use explicit exceptions and remain active under `-O`.

The separate pinned `geometry.py` APIs `build()` and `check_geometry()`
also pass. They produce the claimed 112 by 8 matrix with 896 entries in
{-1,0,1}, confirming the rational-X premise used in the P112 corollary.
This is a geometry check, not the predecessor's support/cost census.

## Proof review and finite coverage

The written argument was checked against these obligations:

1. Every element to which f is applied belongs to the finite span V.
   Zero entries extend by f(0)=0, including empty W.
2. The coordinate polynomial of a nonzero element is nonzero, and the
   union bound is N(d-1), or N(D-1) for a supplied larger space.
3. X has coefficients in the base field, so f commutes with multiplication
   by each X entry. Multiplicativity of f on two extension elements is
   never required.
4. Projection is applied to reciprocals of nonzero z entries. Equation (6)
   proves both directions of residual-support equality.
5. The original and rational full identities hold entrywise. Equal term
   support pairs imply equal support-only costs, without a physical-cost
   assertion.
6. The F4 counterexample satisfies the original identity, while every F2
   choice fails the required support pattern. The finite-field sufficient
   size condition is explicitly distinguished from a necessary condition.

This was the same assistant's reasoning review, not an independent review.
The finite evidence consists of nine worked examples, two complete 81-case
scalar grids, five mathematical controls, one polynomial-avoidance example,
and all four F2 candidates. The degree-two avoidance example checks general
linear-functional selection. It does not prove that the parameter bound is
sharp for W sets arising from single lifts.

The command-level controls alter one rational witness, the F2 result, the
control list, and the Boolean type, then alter one pinned proof source.
Every change is rejected. A fresh temporary root containing only this
package and the six named predecessor sources passes before mutation.

The run does not search arbitrary coefficient heights, multiple added
totals or physical suppliers. It does not rerun PR845's geometric census,
the full `make verify` suite, selected-supplier cold replay, Linux CI, or a
formal prover. The infinite-field theorem relies on the written proof;
the inherited P112 floor relies on its retained, credited source theorem.

## Coordination and publication boundary

Seed 95 selected research consolidation at base
`ba82555c64e1879e4b7decce28186f208fcb8262`. The local claim was made within
eight minutes after checking all 774 open PRs through #1120 and the absence
of a pinned sprint issue. Subsequent all-state title searches for rational
support, descent and single lift found no competing rational-descent result.
PR998 and PR845 retain their recorded reviewed heads. PR1098 and PR1112
have different objects. Publication requires one final metadata refresh;
its result is recorded in the completed claim and cycle handoff.
