# Restored binary connector walks for all 3-by-3 product patterns

**Recursive-interface construction with a finite optimality certificate. No new
kappa.** In the six-query model below, every binary 3-by-3 coefficient matrix
can be implemented with exactly two calls to each active operator. This attains
the support lower bound, including for arbitrary positive per-operator prices.
The certificate contains all 512 explicit words; it is not an inference from
a sample or a claim about general circuits.

For the six-edge cycle, carrying partial sums in one dirty connector reduces
18 complete queries for separate row/column stars to **12**. With the six
queries themselves lowered as binary products of lengths 1 through 6, the
same change reduces the better star comparator from **228 to 198 complete
leaf calls**, with **four borrowed dirty arrays** in either schedule.
These are operation counts, not measured speedups or a supplier exponent.

```sh
python3 -I -O -B research/binary-connector-walk/verify.py
```

Expected: `PASS_BINARY_CONNECTOR_WALK targets=512 dense_cases=23040 controls=11
cycle=18->12 lowered=228->198`. Python 3.10+ and its standard library suffice.
`search.py` regenerates only this package's `CERTIFICATE.json`;
`verify.py --write-summary` regenerates only `EXPECTED.json`.
`test_package.py` also checks exact regeneration, relocation and file corruption.

## Contract and model

Let x_0,x_1,x_2, y_0,y_1,y_2 and z be seven distinct, arbitrary length-L
binary arrays. The maps B_j and A_i are fixed, exact F2-linear operators.
They need not commute or be invertible. Coefficients are read-only. The desired
map for M in F2^(3 by 3) is

    x_j -> x_j;  z -> z;
    y_i -> y_i + sum_j M_ij A_i B_j x_j.

Only six complete queries are permitted:

- B_j: `z += B_j x_j`;
- A_i: `y_i += A_i z`.

Addition is XOR. Each query preserves its source, every other data array and
its private scratch. A child returns its scratch and prescribed tape heads to
their entry state. Its action is independent of the previous target contents.
All six data arrays and the connector are excluded from child scratch. They
remain reserved throughout the batch; no external observer consumes temporary
outputs. Coefficients, source arrays, role bindings and frames cannot change.

The alphabet excludes combined queries, direct A_i B_j calls, extra connector
arrays, free copies, overwrites, changing the physical role assignment, and
other data operations. The optimum below is relative to this alphabet. It is
not a lower bound for the actual selected supplier or general bit circuits.

This extends the single-source fanout interface in
[PR889](https://github.com/CrocSwap/integer-mult-bounds/pull/889). Its connector
is restored between individual stars in the comparator. Here independent
sources can enter/leave the connector at different times, and output readouts
cancel its original dirt only at the end. The difference is the interface and
schedule, not a different random seed for the same echo-tree search.

## Explicit six-edge cycle

For M with rows `(1,1,0), (0,1,1), (1,0,1)`, execute

    A0 A1 B0 A2 B1 A0 B0 B2 A1 B1 A2 B2.

The connector's source subsets at the paired readouts are:

| Output | First subset | Second subset | XOR difference |
|---|---|---|---|
| y_0 | empty | {0,1} | {0,1} |
| y_1 | empty | {1,2} | {1,2} |
| y_2 | {0} | {2} | {0,2} |

Each A_i reads the initial dirty z twice, so that term cancels. Each B_j occurs
twice, restoring z. The x_j arrays are never targets. This proves the displayed
identity for arbitrary L and exact linear maps, with no commutativity assumption.
It also explains why deleting an apparent final cleanup query is invalid.

## General lower bound and complete three-by-three certificate

Work with free formal operators and independent input symbols. In any valid
word, the coefficient of B_j x_j in final z is the parity of the B_j count.
Restoration forces this count to be even. A nonzero column of M requires at
least one B_j call, hence at least two. The coefficient of A_i z_initial in
final y_i is the parity of the A_i count. Independence from connector dirt
forces it to be even; a nonzero row requires at least two A_i calls.

Thus every word that works for arbitrary maps has query count at least

    2 (number of nonzero rows + number of nonzero columns).

For positive, fixed complete prices c_Ai,c_Bj, the corresponding bound is
`2 sum_active c_F`. This is a generic-operator bound: specialized zero maps,
relations between maps or restricted inputs can have different optima.

The certificate's 512 words each have exactly these multiplicities and are
checked in an independent free noncommutative algebra. Therefore the lower
bound is attained for every 3-by-3 binary M, including degenerate and empty
patterns. This finite constructive result also covers smaller matrices by
zero padding the *operator pattern*, without dividing charged payload volume.
It does not establish the same property for four or more inputs/outputs.

The search state is `(q,e,M)` with q,e in F2^3 and M in F2^(3 by 3):
`z=z_initial+sum q_j B_j x_j`, and
`y_i=y_i_initial+e_i A_i z_initial+sum M_ij A_i B_j x_j`.
A B_j toggles q_j. An A_i toggles e_i and adds q to row i of M. This gives
32,768 states and six edges per state. The breadth-first search exhausts all
196,608 directed edges and stops when its queue is empty. Seed 51 selects
dimension `2+51%2` and rotates the generator order for deterministic witnesses.
All 512 restored target states have q=e=0. No stochastic pruning is used.

The independent verifier does **not** trust or replay the BFS transition code
or its reported distances. It interprets each literal query on free polynomial
expressions in all seven independent inputs, checks the full target map and
inverse, and checks equality with the proved support bound. The BFS statistics
are search provenance, checked separately by deterministic regeneration.
This is an exact finite certificate with a written reduction, not a Lean proof
or formal verification of the multiplication theorem.

For 418 of 512 patterns, the word is shorter than both the whole-row and
whole-column star schedules. These are explicit comparators, not an asserted
optimum among every possible partition into stars. The zero pattern is included.

## Complete cost recurrence and storage

Let c_F(L) be a **complete** additive query cost on a full length-L row at its
specified ports. Include source/coefficient access, arithmetic, target update,
private scratch restoration, head returns, and any required entry/exit frame
conversion. Let P_F be reusable coefficient preparation/admission, paid once
per active F. No such preparation is needed for the already supplied binary
matrix fixtures beyond their explicit validation scans. Then

    C_M(L) = sum_active P_F + I_M(L)
             + 2 sum_active c_F(L) + D_M,

where I_M pays role/shape/bit validation and initial layout, and D_M pays word
selection, instruction reads and dispatch. No copy or frame change is emitted
by this interface itself. If a caller's representation is incompatible, its
conversions must be added to c_F or I_M; they are not silently omitted.
Seven full data rows remain live, plus the maximum private scratch of an active
query. One of the seven rows, z, is borrowed and dirty. No clean length-L row is
required; scalar arithmetic/control registers and instruction storage are paid.
Outputs and sources cannot be reused as recursive scratch.

For explicit recursive lowering, let F=F_left F_right, in application order
right then left. With another distinct dirty connector w, use
`R L reverse(R) reverse(L)`. Every elementary binary shear is self-inverse, so
these are literal inverse words, including all children. In the same complete
entry/exit convention,

    C([f]) = c_f + dispatch_leaf,
    C(F) = 2 C(F_right) + 2 C(F_left) + dispatch_node.

The generator uses balanced contiguous splits. Its leaf recurrence is
`ell(1)=1`, `ell(n)=2 ell(floor(n/2))+2 ell(ceil(n/2))` and its scratch depth is
`h(1)=0`, `h(n)=1+max(h(floor(n/2)),h(ceil(n/2)))=ceil(log2 n)`.
The batch needs `1+max h(n_F)` borrowed dirty arrays in addition to six data
rows. A sibling reuses private scratch only after the preceding call returns.
The inverse of a child does not duplicate its peak workspace.

For B0,B1,B2,A0,A1,A2 with factor lengths 1,2,3,4,5,6, the leaf prices are
1,4,10,16,28,40. The literal 198-leaf program is included and independently
checked on ten arbitrary initial arrays in the free algebra.

| Schedule for the six-edge cycle | Root calls | Lowered leaf calls | Dirty arrays |
|---|---:|---:|---:|
| Three column stars | 18 | 366 | 4 |
| Three row stars | 18 | 228 | 4 |
| Carried connector walk | 12 | 198 | 4 |

The comparison preserves the same six factor products and their lowering.
It does not optimize alternative product splits or other echo architectures.
Preparation and admission are the same; every active oracle is called twice
in the walk, so any positive fixed complete per-oracle price attains the same
support bound. A nonuniform physical price is not replaced by unit cost.

### Explicit dense tape invoice

`EXPECTED.json` includes a concrete, deliberately slow dense implementation.
All mutable binary arrays precede the read-only matrices on one data tape;
for every target entry, the trace visits each matrix coefficient and matching
source bit, computes a scalar dot product, then updates the target bit. It
returns to cell zero after **each** complete leaf. The exact invoice counts
coefficient/source reads, target read/write pairs, AND/XOR operations and every
head move. It includes all live data and coefficient bits and validation reads.
Each of N leaves has L^2 coefficient reads, L^2 source reads, L target updates,
L^2 ANDs, and L(L+1) XORs (including accumulation and target update).

Control uses an explicitly stored instruction tape: charge N instruction
records with O(log(R+K)) bits per record for R roles and K matrices, sequential
instruction reads, O(N) dispatches, and indexing/control work per data access.
The finite root lookup table has 512 entries and bounded size; alternatively
the displayed word is hard-coded for the cycle. Initial placement and coefficient
production from other input formats remain separately charged in I_M and P_F.
The matrix fixtures are supplied in the stated layout. No rounding or precision
approximation occurs over F2. The verifier's Python copies are validation code,
not a wall-time implementation claim for this tape algorithm.

## Scope, controls and inherited obligations

The independent replay checks all 512 witnesses and both star comparators in
free algebra, plus every input basis column for deterministic dense maps at
L=1,2,3 and combined dirty inputs: 23,040 dense cases, each with the appropriate
inverse check for the basis cases. The lowered program is checked symbolically.
Eleven controls reject missing coverage, omitted restoration, reordered queries,
a correct but nonoptimal word, the wrong target pattern, a wrong child factor,
aliased ports, an unpaid child, underpriced scratch, odd characteristic and a
nonlinear readout. Odd-characteristic/nonlinear cases are **counterexamples to
extending this binary exact contract**, not failures of the admitted construction.

The current selected conditional exponent at the exact base is
1661634653669567/10^18 (#799 with #589/#555). This package has not located these
independent-source/product obligations inside that supplier. Common-label and
mutable-source realization, frames, ownership, full-row volume, compiler/tape
integration and the outer analytic constraints remain uninstantiated. A cheaper
abstract query word cannot establish a new kappa, nor show which supplier would
bind after an actual integration. No selected profile, certificate or upstream
manuscript is changed. The coordinate-Fourier obstruction is not bypassed by a
free address transform: every black-box child here has its full charged cost.

See [CLAIM.md](CLAIM.md), [SOURCES.json](SOURCES.json), [VALIDATION.md](VALIDATION.md)
and [NOTICE.md](NOTICE.md) for base, search domain, evidence, predecessors,
attribution and substantial AI assistance.
