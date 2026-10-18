# Generated-lattice parity cuts before mixed-target word search

Rational projection/rank cuts and determinant equality do not suffice to screen
an eight-call candidate for three invertible rational 3-by-3 targets. The exact
example in [EXAMPLE.json](EXAMPLE.json) passes both but violates a first-order
rank cut in the actual generated lattice modulo two. The cut excludes every
call order and scalar coupling, with any finite number of restored dirty roles.

The new contribution is a complete checker for this family of binary-character
rank cuts, its coverage proof and that explicit separation. It uses the retained
augmentation equation, not a new register model. A passing screen is still only
a necessary condition. There is no supplier, physical cost or new kappa claim.

## Model and proof

Let H be the additive subgroup generated over Z by nonzero rational rank-one
paid frames A_j. Work over F2[H], with paid factors

```text
I + ([A_j]-1) N_j,       N_j binary rank-one idempotent.
```

The desired full formal endpoint is
`diag([C_1],...,[C_W],1,...,1)`. All additional scalar roles start dirty and
must return unchanged. Targets may repeat or be zero. Free scalar mixing is
absorbed into the projectors; arbitrary free address maps and clean ancillas
are not included. Every target must lie in H, since every nonzero endpoint
exponent occurs in the paid word's subset-sum support.

For every additive character lambda from H to F2, define a homomorphism into
the dual numbers by

```text
[A] maps to 1 + lambda(A) epsilon,        epsilon^2 = 0.
```

Multiplicativity follows from additivity of lambda. Terms involving two or
more epsilon factors vanish. Equality of the epsilon coefficients therefore
requires

```text
sum_j lambda(A_j) N_j = diag(lambda(C_1),...,lambda(C_W),0,...,0).
```

The right side has binary rank equal to the number of retained target roles.
Rank subadditivity bounds the left side by the number of retained paid calls.
Thus every successful word satisfies

```text
#{j: lambda(A_j)=1} >= #{i: lambda(C_i)=1}.
```

This is the character-wise rank consequence of the first-order augmentation
equation in [mixed-target compression](../bit-mixed-target-register-compression/README.md).
It is independent of chronology and dirty-role count. In particular, if one
character retains just one paid call but three targets, a rank-one matrix would
have to equal a rank-three matrix. The rational projection/rank method is
retained from Ali Romman's [three-register proof](../bit-three-register-lower-bound/README.md).
Here the projection is into dual numbers, not the rational Laurent fraction
field used by [the rational-cut screen](../bit-rational-rank-cut-screen/README.md).

H is free abelian of rank d. An exact integer lattice basis identifies H/2H
with F2^d. Enumerating all 2^d assignments to that basis enumerates every
character exactly once. The minimum reported margin is consequently the exact
minimum over all such characters, including the zero character. It is not a
minimum over rational projections or over the full tensor factorization problem.

The implementation clears one common rational denominator, uses only swaps,
row sign changes and integer row additions to compute an echelon basis, and
solves for integral coordinates. These operations preserve H, rather than its
rational saturation. A failed integral coordinate division proves a target is
outside H. For accepted members the checker reconstructs every original row
from its lattice coordinates. Dividing rational matrix entries modulo two is
not a replacement for these steps. For example, the generator 2 has nonzero
class in 2Z/4Z, although its integer entry is even.

For the stated idempotent model, the checker also applies the inherited
determinant condition `sum A_j = sum C_i`: the determinant of each paid factor
is `[A_j]`. That condition is not new. Nonidempotent rank-one couplings require
a different determinant condition and are outside this CLI's contract.

## Exact eight-call separation

Write A_1 through A_8 for the matrices in EXAMPLE.json. They are `v v^T` for
v=(1,0,0), followed by twice `v v^T` for

```text
(1,-5,5), (4,3,-1), (-3,2,-4), (5,-1,-2),
(-4,3,-1), (-4,1,1), (0,2,-3).
```

They all have rational rank one. Set

```text
C_1 = A_1 + A_2 + A_3,
C_2 = A_1 + A_4 + A_5,
C_3 = -A_1 + A_6 + A_7 + A_8.
```

The three target determinants are exactly 400, 256 and 152. The sum of the
target frames equals the sum of all paid frames, so determinant equality holds. All frames are
symmetric and span a six-dimensional rational space. Every one of the 28
six-frame subsets is independent. Any rational functional nonzero on this
space therefore kills at most five paid frames, retaining at least three.
A functional zero on the whole span kills every target too. This proves all
rational rank cuts pass, without enumerating a bounded set of functionals.
The retained rational-cut CLI independently reports all 220 paid spans pass.

All entries are integers, so `lambda(X)=X_11 modulo 2` is a valid character on H.
It retains only A_1 but all three targets. The parity margin is 1-3=-2. These
three targets have distinct classes in H/2H; their classes in the computed basis
are

```text
(1,1,1,0,1,0), (1,1,0,1,1,0), (1,0,0,0,1,1).
```

Thus the example is outside the equal-class hypothesis of pending
[PR2934](https://github.com/CrocSwap/integer-mult-bounds/pull/2934), inspected at
`b12bbd839cebfcd109d57b0bb15084943f25d7ec`. This package does not depend on
that pending theorem or change its status. It rejects this unequal-class
candidate, not every unequal-class candidate.

## Run the screen and replay

Python 3.12 or later, standard library only, from the repository root:

```sh
python3.12 -I -B research/bit-generated-lattice-parity-cuts/verify.py --input research/bit-generated-lattice-parity-cuts/EXAMPLE.json
```

The intentional example exits 1 with `REJECT_GENERATED_LATTICE_PARITY_CUT`,
64 checked characters and minimum margin -2. Input uses the same three JSON
keys as the rational-cut screen. Matrices contain integers or rational strings,
not floats or booleans. Exit 0 means only that these necessary parity and
determinant tests pass. Exit 1 rejects; exit 2 means invalid input or a failed
verification. Membership and determinant failures have separate status names.

```sh
python3.12 -I -B scripts/research_package.py --package research/bit-generated-lattice-parity-cuts
python3 -I -O -B research/bit-generated-lattice-parity-cuts/verify.py
python3.12 -B -m unittest discover -s research/bit-generated-lattice-parity-cuts -p 'test_*.py' -v
```

Expected direct replay:

```text
PASS_GENERATED_LATTICE_PARITY_CUTS example=1<3 characters=64 oracle_cases=5676 no_new_kappa
```

[RESULT.json](RESULT.json) stores the exact lattice basis, coordinates, target
classes, cut witness, determinants and a passing direct nine-call word for
three identity targets. The replay checks the 28 independent six-frame subsets,
fractional, negative and even rescalings, and 5,676 independent small oracle
cases. For 36 independent ordered generator pairs, Cramer's rule supplies the
exact membership and character expectations for 81 target vectors per pair.
Another 216 triples use the integer gcd as a separate one-dimensional oracle.
For 318 rank-two generator triples, the primitive vector of signed 2-by-2 minors
generates the entire integer relation kernel. Its one parity equation enumerates
all four characters. Eight target coefficient choices per triple give 2,544
further cases, independently testing lattices with redundant generators.
No oracle uses the Euclidean lattice implementation to obtain its expectation.

Six behavioral test groups cover normal and optimized relocated CLI execution,
read-only behavior, literal rejection witnesses, malformed inputs, empty paid
lists, determinant-only failure, membership, rational values and all 4,096
characters at maximum lattice rank. Three actual implementation mutants fail
before receipt comparison: rational saturation, entrywise parity and skipped
cut rejection. A corrupted receipt also fails. Normal replay writes nothing;
`--write` regenerates only this package's RESULT.json.

Build the Lever led to the reusable bounded CLI. Prove It Works led to the
exact separation and independent Cramer/gcd oracles. Test Behavior, Not
Implementation led to actual CLI exit and witness checks plus semantic mutants.

## Scope, next questions and credit

The universal claim is the written necessary inequality and finite character
coverage argument. The finite example is an exact rejection certificate, not a
successful word or a complete multiplication theorem. Full formal word
coefficients, native realization, physical ownership/movement, precision/tape,
all-size compilation and complete supplier moments were not checked. No
predecessor full cold replay was rerun. The selected result is unchanged.

### Open next questions

Can one explicit unequal-class candidate pass rational cuts, determinant
equality and these generated-lattice parity cuts, then satisfy the full formal
endpoint? First retain the exact frame and target JSON and all screen results.
Only then search the bounded scalar-role domain from mixed-target compression
and state a complete native/consumer cost allowance. A passing candidate and
its full word are missing. This package narrows pre-search screening, rather
than justifying another construction campaign. [TASK.json](TASK.json) records
the scope change and this same handoff.

Nick Petalas. Apache-2.0. The first-order augmentation equation and image-space
reduction are retained from mixed-target compression and Tuafo's identical-target
argument. Ali Romman's PR468 supplies the original register/projection method,
with eumemic/PR288 and huxint/PR203 in its lineage. The retained rational-cut
screen supplies the comparison contract and exact input conventions. PR2934's
pending equal-class proof supplies the immediate unequal-class handoff and the
warning to preserve the actual lattice. Predecessor sources stay unchanged.
Evidence is author-checked; no independent human or proof-assistant review is
claimed. Exact source pins, environment and freshness are in SOURCES.json and
TASK.json. Canonical claim: [Discussion2898](https://github.com/CrocSwap/integer-mult-bounds/discussions/2898#discussioncomment-18973523).

## Implementation limits

Power of Ten review is limited to the two new Python files. The input boundary
allows address dimensions 1 through 4, at most 12 paid frames and 12 target
roles, reduced entry numerators and denominators at most 65,535, a common
denominator of at most 128 bits and files of at most 65,536 bytes. The lattice
rank is at most 12, so there are at most 4,096 characters. Lattice rows and
coordinate remainders are capped at 4,096 bits. Temporary row arithmetic needs
at most 8,193 bits, and coordinate reconstruction at most 8,196 bits. Each
pivot's Euclidean loop allows at most 98,316 rounds. With a nonzero remainder, the minimum nonzero
pivot magnitude decreases, and within two rounds it at least halves. Capacity
exhaustion fails with exit 2, never a mathematical pass or rejection.

There is no recursion or generated code in the checker. Functions are under
60 physical lines. Integer operations, exact Fraction elimination and explicit
runtime contracts remain active under optimization. State is local apart from
immutable capacity constants. Rule 3 deviation: Python and Fraction allocate
at runtime in this bounded research command. Enforced dimensions, integer
capacity and the finite character count bound live collections; the registered
command has a 120-second timeout. A fixed-memory implementation is needed
before use in a steady service. Rule 9 deviation: the tests use unittest's
fixed method dispatch and import one fixed local module. Sequential subprocesses
run only the current interpreter and local checker, with 60-second timeouts and
temporary-directory cleanup. Rule 10 uses Ruff diagnostics, warning-as-error
compilation and the registered replay, recorded in TASK.json. Shared runner or
predecessor refactors are outside scope.
