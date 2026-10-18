# The added dyadic frame cannot occur in an exact word

In the fixed positive five-address alphabet of Cinna Davis's
[PR2112](https://github.com/CrocSwap/integer-mult-bounds/pull/2112), every
exact word for its four-target endpoint has **eight calls and no R call**.
This holds with any finite number of restored dirty registers and any free
binary scalar mixing. A short determinant proof replaces scalar-word search.

Philippe Van Velzen already established the four-role minimum of eight in
[Discussion2091](https://github.com/CrocSwap/integer-mult-bounds/discussions/2091#discussioncomment-18935374),
with a quotient search at fork commit
[`b0b2cf8e30908e0285376c6d95e1114e55df26f6`](https://github.com/philippeVV/integer-mult-bounds/tree/b0b2cf8e30908e0285376c6d95e1114e55df26f6/research/five-address-seven-call-floor).
That minimum is not new here. The new result forbids R at every word length,
allows arbitrary restored dirty workspace, and classifies all
determinant-compatible label multiplicities without a word census.
No new supplier, physical storage saving or kappa is claimed.

## Model and theorem

The rank-one rational address matrices are

```text
A = [[1,0],[0,0]]       B = [[0,0],[0,1]]
P = [[1/2,1/2],[1/2,1/2]]
Q = [[1/2,-1/2],[-1/2,1/2]]
R = [[1,1/2],[1/2,1/4]].
```

They satisfy `P+Q=A+B` and `4R=2A-B+4P`. Work in the commutative
formal group algebra `F2[Lambda]`, where `Lambda=ZA+ZP+ZR` and
`[F][G]=[F+G]`. A paid call is `I+([F]-1)N`, for
`F in {A,B,P,Q,R}` and a binary rank-one idempotent N on any finite number
of scalar roles. Arbitrary address-independent binary invertible scalar
maps are free. The endpoint is

```text
diag([A+P], [A+Q], [B+P], [B+Q], 1, ..., 1).
```

All roles start arbitrary. The extra roles must be restored exactly, and
formal equality is required for the whole register matrix. Inverse address
labels and free address transformations are not allowed.

**Theorem.** Every such word has eight paid factors. Its R multiplicity is
zero. In label order `A,B,P,Q,R`, its multiplicities must be
`(b,b,4-b,4-b,0)` for an integer `0 <= b <= 4`.
The direct eight-call word attains the endpoint, so the minimum is eight
for every finite register count at least four. The five multiplicity
profiles are necessary conditions, not five claimed constructions.

## Proof

For a rank-one idempotent `N=xy^T`, `y^T x=1`. The determinant identity

```text
det(I+([F]-1)xy^T) = 1+([F]-1)y^T x = [F]
```

gives one exact address contribution per call. Each free binary invertible
matrix has determinant one. Taking determinants of the whole endpoint
therefore gives the rational matrix equality

```text
n_A A + n_B B + n_P P + n_Q Q + n_R R = 4(A+B) = 4I2.       (1)
```

The exponents in this equality are rational matrices, not their reductions
modulo two. All five frames are positive semidefinite. Their rational
traces are `1,1,1,1,5/4`. If k is the total number of paid calls, the trace
of equation 1 gives

```text
k + n_R/4 = 8.
```

Thus `n_R` is divisible by four. Now evaluate equation 1 on the rational
column vector `v=(2,1)^T`. Since every summand is positive semidefinite,

```text
n_R * v^T R v <= v^T (4I2) v,
(25/4) n_R <= 20,
n_R <= 16/5 < 4.
```

A nonnegative multiple of four below four is zero. Hence `n_R=0` and
`k=8`. With R absent, the off-diagonal entries of equation 1 give
`n_P=n_Q`; its two diagonal entries give `n_A=n_B=4-n_P`. These are
exactly the five stated profiles.

For attainment, use coordinate projectors and label pairs `(A,P)`,
`(A,Q)`, `(B,P)`, `(B,Q)` on the four active roles. Each pair sums to its
required target; other roles remain unchanged. This proves the result.
No register-count restriction or scalar normalization was used in the
lower bound.

## Evidence and reproduction

```sh
python3.12 -B scripts/research_package.py --package research/bit-fifth-frame-determinant-obstruction
python3 -I -O -B research/bit-fifth-frame-determinant-obstruction/verify.py
python3 -B -m unittest discover -s research/bit-fifth-frame-determinant-obstruction -p 'test_*.py'
```

The standard-library verifier checks the exact rational rank-one and
positive-semidefinite conditions, the integral basis and target sum, and
the trace/energy values used by the proof. A separate bounded enumeration
using scaled matrix entries, not the lattice equations, visits all 1,287
label multisets of length at most eight and finds exactly the five
profiles in [RESULT.json](RESULT.json). This finite check corroborates the
written all-length proof; it is not its coverage argument.

Full coefficientwise formal replay checks the eight-call construction on
4, 5 and 7 registers, both directly and with free scalar basis changes.
The 5- and 7-register cases mix an active role with a dirty role and still
restore the required endpoint. All 48 single-label replacements by R
reject. The six-call label multiset enumerated by PR2112 has trace `13/2`,
not eight, so it already fails equation 1 before scalar choices or ordering.

The CLI tests run normal and optimized interpreters, relocate the package,
reject altered receipts, and reject an actual implementation mutant that
omits the paid-factor update. Checks use explicit exceptions and
remain active under `-O`. The registered replay runs these tests as well.

Two boundary controls prevent broader readings:

- `3B+4Q+4R=6I2` is an eleven-label determinant-compatible multiset.
  It is not a formal word construction. The no-R conclusion is specific
  to the original target sum.
- A formal `D_N([R]) D_N([-R])` pair is identity. Allowing inverse labels
  permits an R-containing ten-call realization by appending this pair to
  the direct word. The positive-alphabet restriction is essential.

The new proof does not depend on replaying either predecessor's word
search. Their exact sources and existing evidence retain separate credit.
No independent human review, proof-kernel verification, native compiler,
hosting, precision or full selected-supplier replay is claimed.

## Open next questions

There is no justified construction follow-up inside this fixed alphabet
and endpoint. Its added R is unusable, even with more restored dirty
workspace. A changed candidate must first pass the exact determinant
constraint. A feasible first step for an independently motivated new
alphabet is to check its target sum, integral label counts and positive
quadratic forms before scalar search. Passing such checks would still
leave the formal word and its complete native/consumer costs unresolved.
This package does not start another construction round.

## Scope, implementation limits and credit

[TASK.json](TASK.json) records the changed scope from `bit-new-register-model`
to this fixed-alphabet audit, the overlap checks and the stopping decision.
[SOURCES.json](SOURCES.json) pins the source READMEs and assignment baseline.
The selected frontier and all frozen predecessors are unchanged.

The checker has no recursion, network access or subprocesses. Its largest
formal replay has eight factors and seven rows, with at most 256 exponent
terms. The matrix-entry enumeration has exactly 1,287 iterations; receipt
input is bounded to 64 KiB. Python and Fraction allocate dynamically, a
managed-runtime deviation from fixed-allocation rules. These fixed domains
bound the live data. A larger search needs a new capacity assessment rather
than removal of these bounds. The test runner uses bounded temporary
files and 30-second child timeouts. Python runtime and allocator internals
are not statically verified.

Cinna Davis supplied the four-address minimum in PR2085 and the five-address
model and six-call exclusion in PR2112. Philippe Van Velzen supplied the
prior four-role exact-eight finding and its two quotient-search
implementations. The determinant of a paid factor is standard algebra,
not a new general lemma. The retained bit-model lineage includes Ali
Romman, eumemic, huxint and the sources credited by those predecessors.
New material by Nick Petalas, Apache-2.0.
