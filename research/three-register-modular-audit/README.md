# Audit of PR468's modular arithmetic obligations

**Result:** the pinned modulo-101 arithmetic passes an independent audit of
its rational row reconstruction, subset-collision keys, and two-frame target
membership. No arithmetic counterexample was found in the stated coverage.
This package also gives concrete failure examples for smaller primes and for
taking parity directly from residues. It does not rerun or reprove the full
nine-call lower bound, and makes no new κ claim.

Author: David Govea (`davidgovea`), with substantial OpenAI Codex assistance
in selecting the obligation, deriving the argument, implementing the audit,
and preparing the text. New files are Apache-2.0, under the repository license.

## Object and provenance

This audits section 9 and the arithmetic routines of Ali Romman's
[PR #468](https://github.com/CrocSwap/integer-mult-bounds/pull/468),
head `07a78bf335b0b5039a1fecd7cd74a0fe1d1605ea`, as preserved in
[`../bit-three-register-lower-bound/`](../bit-three-register-lower-bound/).
The inspected upstream `f101.cpp` Git blob is
`e3fad6c59ca00250fdb9fca7be77a48a9bf05d9d`, identical to the base's file.
The predecessor already supplies two full search implementations. This audit
adds a determinant-based oracle that calls the actual modular kernels directly,
plus explicit separation of rank preservation from parity reconstruction.
The lower-bound theorem, its reductions, and its original dual replay remain
Ali Romman's contribution, building on eumemic's #288 and huxint's #203.

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
[`SOURCES.json`](SOURCES.json) pins the exact proof and implementation bytes.
Assignment seed **66** came from OS randomness (`secrets.randbelow(100)`).
The three candidates were this modular exactness obligation, PR468's span-four
common-flag reduction, and PR559's complex bad-class surcharge removal.
`66 mod 3 = 0` selected the first, with an independent determinant method;
the other candidates needed a broader symbolic audit or overlapped an existing
review. No pinned coordination issue existed when checked, so the claim was
recorded locally outside the submitted package. The selected construction at this base is #626
with #543, conditional κ = **0.001635527380375392**; this audit changes neither
that selection nor its suppliers.

## Reproduce

From the repository root, with Python 3.9+ and a C++17 compiler:

```sh
python3 -B -S research/three-register-modular-audit/verify.py
```

The first output line must be `PASS_PR468_MODULAR_ARITHMETIC_AUDIT`.
The following JSON must report:

| Check | Completed coverage |
| --- | ---: |
| Nonsingular cube pivot matrices, dimensions 1 / 2 / 3 | 2 / 48 / 11,808 |
| Pivot matrix plus every cube column | 6 / 432 / 318,816 |
| Total small matrices checked against actual production kernels | 319,254 |
| Additional deterministic matrices of width eight | 192 |
| All unordered subset pairs in those width-eight matrices | 6,266,880 |
| All 256 subset targets in each width-eight matrix | 49,152 |
| Targets outside every two-coordinate span | 36,835 |

The last count checks that the target test exercises both answers. These
matrices are arithmetic fixtures, not admitted scalar words or candidate
constructions. The width-eight cases are **not exhaustive**: a fixed 32-bit
linear congruential sequence, seed 66, supplies 64 nonsingular-prefix matrices
at each relation rank 1, 2 and 3. The stopping rule is 192 accepted matrices
within 10,000 attempts; failure to finish is an error. The complete small
matrix census and determinant argument below have a different, explicit scope.

The driver uses only the Python standard library, copies the pinned C++ source
to a temporary directory, and compiles the probe against that copy. `CXX` may
select a compiler and flags. Ordinary replay writes no repository artifact.
`--write-certificate` explicitly regenerates this package's `EXPECTED.json`.
There is no source download, solver, or floating-point arithmetic in replay.

## Why the modular calculation is exact in this domain

Let a *cube row* have entries in `{−1,0,1}`. Search states are rational spans
of at most three cube rows: each inserted generator is the difference of two
original subset indicators. This is the domain being audited, not arbitrary
integer relation matrices.

**Ranks and membership.** The production decisions concern these rows, at most
one further cube row or binary target row, and at most two coordinate rows.
In any square minor, expand along the coordinate rows. A nonzero remaining
minor has at most four cube rows. For size `s ≤ 4`, Hadamard's inequality gives
absolute determinant at most `s^(s/2) ≤ 16`. Thus every nonzero rational minor
is nonzero modulo 101, and every zero minor stays zero. Ranks, subset collisions,
zero-coordinate membership, insertion ranks and the target test

```
c ∈ span_Q(relations, e_i, e_j)
```

are consequently preserved. This is a uniform argument for the stated row
domain; it does not depend on sampling the width-eight matrices.

The independent Python check enumerates all 19,767 square cube matrices of
sizes 1 through 3. Their sharp determinant bounds are 1, 2 and 4. It also
checks all 65,536 sign vertices of the 4×4 entry cube, whose maximum absolute
determinant is 16. A determinant is affine in each entry separately, so its
absolute maximum on the entire real cube is attained at a sign vertex. This
vertex check must not be described as an enumeration of all `3^16` cube matrices.
The certificate retains complete determinant histograms and a sharp witness.

**Rational reconstruction.** Choose an invertible pivot minor `B` of `r ≤ 3`
independent cube rows. Every nonpivot RREF entry is a Cramer ratio
`det(B with one column replaced) / det(B)`. Both determinants are integers
of absolute value at most 4. Reduction to lowest terms therefore leaves
`|numerator| ≤ 4` and `1 ≤ denominator ≤ 4`. The 23 distinct fractions in
that envelope have distinct residues modulo 101: a difference has cross
numerator of absolute value at most 32, smaller than 101. The implementation
actually initializes a larger table with bound 5 and 39 fractions; its cross
numerator bound is 50, so this table is also unambiguous. Both complete tables
are reconstructed independently in the certificate.

After recovering each rational entry, clearing denominators and dividing by
the row gcd gives the primitive integral row. Only then is reduction modulo
two valid. This certifies the representation used by the parity calculation;
it does not independently prove the search's first-order parity-pruning lemma.

**Canonical-state equality.** The proof above also addresses comparing two
stored modular bases. Equal modular RREFs have the same pivots, and uniqueness
of each bounded rational entry forces equal rational RREFs. One need not apply
the four-row minor argument to the union of two three-row relation bases,
which would be outside that argument's domain. Finally, the production subset
key stores eight residues in disjoint seven-bit fields. Residues 0 through 100
fit those fields and use 56 bits, so packing introduces no additional alias.
The direct probe checks the residual vectors before this packing step.

## Independent oracle and controls

`kernel_probe.cpp` includes the pinned implementation under a renamed entry
point and invokes `insert`, `primitive_parity`, `residual`, and `target_small`.
The oracle computes determinants by the Leibniz formula, constructs Cramer
numerators, and checks two-vector membership using 2×2 and 3×3 minors. It does
not import the predecessor's rational engine or implement a second Gaussian
elimination. Python independently uses Laplace expansion for its determinant
certificate. The probe checks all nonsingular cube pivot matrices with every
extra cube column, then the documented width-eight cases, including reversed
generator order for canonical-basis equality.

The fixed negative controls are mathematical distinctions, not new failures
of the pinned engine:

1. A displayed 4×4 cube matrix with binary final row has determinant −5 and
   a rank-three prefix modulo 5. Adding its final row raises rational rank
   to four while rank modulo 5 stays three. An arbitrary small prime is unsafe.
2. Prime 19 is larger than the rank bound 16, but `−4` and `3/4` both map
   to residue 15. Rows `(1,−4)` and `(1,3/4)` have primitive parities `(1,0)`
   and `(0,1)`. Rank preservation alone does not justify coefficient decoding.
   This example concerns the bounded reconstruction envelope; it does not
   assert that a complete production state collides modulo 19.
3. Modulo 101, `(1,1/2)` becomes `(1,51)`. Taking parity of residues yields
   `(1,1)`, whereas the correct primitive row `(2,1)` has parity `(0,1)`.

Four deliberately damaged copies of the actual implementation must compile
and then fail a named oracle comparison: direct residue parity, accepting
every target, rejecting every target, and dropping the last residual coordinate.
The driver also rejects a modified source digest. It compares the entire
generated certificate with `EXPECTED.json`. Checks use explicit exceptions,
so optimized Python does not silently disable them.

## Limits and validation

This is an adversarial arithmetic audit with a supporting mathematical
argument, not a proof-assistant theorem. No counterexample to the pinned
arithmetic was found in the completed domain. It does not inspect every search
branch, reproduce all 21,317,520 scalar orders, validate every symbolic reduction
in sections 2–8, or certify the full nine-call theorem. The full predecessor
replay and its search-completeness arguments remain separate evidence. Nor
does it verify integer multiplication, all-size compilation, physical hosting,
precision, tape, or analytic transfer.

Only this new research directory is changed. The expensive repository-wide
suite and selected-frontier cold replay are not needed for this isolated audit
and were not rerun. Local commands and environments are recorded in
[`VALIDATION.json`](VALIDATION.json); no remote CI outcome is inferred from them.
