# The archived fitting-matrix statements

## Exact object

The root generator is the archived `hamming_e8` convention from PR620's copy
of the DreamingOfClouds geometry utility. It enumerates eight coordinate
lines `2 e_i`, then the fourteen weight-four words of the extended Hamming
code, sorted as coordinate tuples. For each support it fixes the first sign
positive and enumerates the other three signs in product order `(1,-1)`.
The four code generators are the rows

```
11110000
00111100
00001111
01010101
```

There are 120 distinct integer rows L_i of norm squared four. The integral
Gram matrix is `G_ij = L_i dot L_j / 2`, with diagonal two and off-diagonal
entries in {-1,0,1}. Delete the nine indices recorded in CLAIM and README;
the remaining 111 rows keep their original relative order.

A fitting matrix is an arbitrary **asymmetric** 111-by-111 matrix B over F2
such that `B_tt = 1` and `B_ts = 0` for every distinct pair whose roots have
nonzero Gram entry. The other 6,470 ordered off-diagonal entries are free;
there are 5,740 forced ordered zero entries. No equality between B_ts and
B_st is imposed. Let `B0 = (J+G_live) mod 2`, an admitted matrix.

The two checked statements are:

1. No fitting B has F2 rank at most eight.
2. Every fitting B of rank at most nine equals B0.

The literal positive factorization below has rank nine, so the minimum is
exactly nine. "Unique" means the **fitting matrix**; its source/sink label
factorizations are not unique. No statement about higher-rank fitting
matrices, other punctures, fields, copy costs or physical decoder realization
is inferred.

## Factorization and the gauge

A matrix has rank at most c iff it can be factored `B = W U^T`, with source
rows U and sink rows W in F2^c. One direction is rank submultiplicativity;
the other follows by taking a rank factorization and padding it with zeros.
The CNF therefore gives each of the 111 source and sink rows c independent
Boolean coordinates. It constrains their dot products on the diagonal and
the forced-zero pattern.

Eight pairwise nonorthogonal roots form an identity principal block of every
fitting matrix. Their indices in the full archival order are
`0, 64, 65, 72, 73, 108, 116, 118`; in the live order they are
`0, 61, 62, 68, 69, 101, 107, 109`. Thus `W_K U_K^T = I_8`.

The solver fixes both U_K and W_K to `[I_8 | 0]`. This loses no fitting
matrix, even in the asymmetric case. The eight rows of U_K are independent.
Their span intersects the annihilator of W_K only at zero: a combination
with coefficient vector a pairs with W_K to give a. That annihilator has
dimension c-8. Choose a basis Z for it, and let T have rows U_K followed
by Z. T is invertible. The transformations

```
U -> U T^-1,       W -> W T^T
```

preserve W U^T and take both anchor blocks to `[I_8 | 0]`. This proves the
gauge for c=8 and c=9, including padded lower-rank factorizations. The proof
does not assume the rest of U and W are equal.

## Formula and positive calibration

For each requested pairing, the generator adds AND gates for coordinate
products and a chain of XOR gates for their parity. Each AND has three
clauses and each XOR four; their truth tables are checked exhaustively.
Auxiliary outputs have a unique extension for any fixed input assignment.
Unit clauses enforce the fitting pattern and the gauge.

For c=8 the formula contains 1,776 input variables and 5,851 constrained
pairings, each needing 15 auxiliaries and 53 clauses including its unit
constraint. Add 128 gauge clauses: 89,541 variables and 310,231 clauses.

For c=9, the unequal-to-B0 query uses every one of the 12,321 pairings,
with 17 auxiliaries and 59 gate clauses per pairing. There are 1,998 input
variables, 5,851 fitting clauses, 144 gauge clauses, and one disjunction
requiring a free pairing to differ from B0. Totals: 211,455 variables and
732,935 clauses. Equality on the diagonal and forced zeros is already fixed,
so the final disjunction covers every possible way B can differ from B0.

For a positive calibration set

```
u_t[i] = B0[t,K_i]                       for 0 <= i < 8,
u_t[8] = 1 + sum_i B0[t,K_i]              in F2,
U = W = (u_t).
```

All 12,321 products are checked equal to B0. The anchor rows are the first
eight unit vectors. Independent bit elimination checks rank nine of both
the labels and B0. The resulting Boolean/Tseitin assignment violates exactly
the final disequality clause, satisfying all other 732,934 clauses. This is
a positive witness for the model, not an assumption of symmetry in the
negative formulas.

Every cold replay also executes PR620's unchanged clause-building methods
on these inputs. Two unused optional-library import statements are removed
from an in-memory AST, and the solver constructor is intercepted before
solving or model extraction. The pattern's iteration is explicitly sorted
in both implementations; membership and the mathematical constraint set
are unchanged. The entire clause stream agrees byte for byte. This checks
the transcription without requiring NumPy or a SAT solver. It is not a claim
that the historical unordered run used identical variable numbering.

## Proof checking, independent of the solver

PySAT 1.9.dev15's CaDiCaL 1.5.3 interface produced fresh DRAT traces for the
two deterministic formulas. The pinned DRAT-trim converter checked them
and emitted LRAT using its `-U` restriction to RUP additions. No RAT step
is used in either retained proof.

An addition consists of a fresh clause ID, its literal clause C, and an
ordered sequence of earlier clause IDs. The Python checker assumes every
literal of C false. For each referenced premise it requires that all but
one literals are false, allowing the last literal to be set true, or that
all literals are false, giving a contradiction. Satisfied and nonunit hints,
missing or forward references, reused IDs, invalid literals and incomplete
deductions are rejected. A contradiction proves that the current formula
entails C. Induction over additions therefore preserves satisfiability. The
last addition is the empty clause, proving the original formula unsatisfiable.

The checker accepts only the implemented positive-hint, deletion-free LRAT
subset and explicitly rejects RAT/deletion records. Deletions were removed
from the converter's output without changing IDs or additions: keeping extra
premises cannot invalidate these explicitly checked RUP deductions. Clause
IDs are strictly increasing, so no deleted ID is reused with another meaning.
It is therefore safe to retain all previously available clauses.

Cold replay regenerates and hashes the **entire** formula, then retains the
original clauses referenced by the proof. A deduction from that subset is
also a deduction from the complete formula. This reduces checker storage
without treating a digest as a proof of unsatisfiability. Every retained
addition and every propagation hint is checked.

The c=8 proof uses 890 original clauses, two additions and 1,338 hints. The
c=9 proof uses 151,651 original clauses, 37,042 additions and 1,408,137 hints.
The native `lrat-check.c`, implemented independently of the new Python
checker and generator, also accepts the full formulas and retained traces.
That check is additional execution evidence, not a formal verification of
either checker implementation.

For background on the proof format, see the primary
[DRAT-trim repository](https://github.com/marijnheule/drat-trim) and Cruz-Filipe,
Heule, Hunt, Kaufmann and Schneider-Kamp,
[*Efficient Certified RAT Verification*](https://arxiv.org/abs/1612.02353).
The SAT producer is optional; its API is documented by
[PySAT](https://pysathq.github.io/docs/html/api/solvers.html).

## Scope of the reconciliation

This supplies checkable evidence for PR620's two archived SAT answers and
preserves their original mathematical credit. It does not make the original
scripts' other reports portable or validate their numerical screens, solver
barriers, cold-end claims or later research appendices.

PR757 (Russell Seligmann) and PR761 (Cody Harris) already supplied algebraic
proofs of the fixed-label copied-rank floor for actual supplier fixtures and
documented the numbering discrepancy. Their cost theorems and this fitting
matrix result have different domains. The same literal puncture in the
archival ordering has 44 ordered orthogonal deleted-root pairs; the supplier
ordering cannot be substituted silently. The checker pins the complete root
and live order, not just a set of nine integer indices.

Neither this finite propositional certificate nor matrix uniqueness constructs
a physical COPY word or discharges source access, phases, frames, restoration,
hosting, uniform/all-size compilation, fixed-tape, precision, exact recovery
or analytic transfer assumptions. No selected frontier file is changed.
