# The fixed A3+D5 nine-normal decoder has exact COPY cost 72

This contribution was produced by Nick Petalas. Apache-2.0.

Scoped algebraic proof with exhaustive finite premises. For the fixed
`A3 weights + D5 root basis` family in
[joaqcoo's PR1224](https://github.com/CrocSwap/integer-mult-bounds/pull/1224),
the minimum separate-term binary pairing-rank cost on all 120 E8 root lines
is exactly **72**, allowing arbitrary independent complex row shifts.
An exact nine-active-term witness has ranks `(1,8,9,9,9,9,9,9,9)`.

The source gives a sparsest-row cost-81 example and records three bounded
searches whose best cost is 81 for this unpunctured family. The new result
replaces that upper bound with a sharp optimum. Its ratio `72/120 = 3/5`
equals the ordinary eight-term P120 COPY bill. It does not improve the P112
ratio `4/7`, supply a physical supplier, change kappa or prove a complete
multiplication theorem. No literature-priority claim is intended.

## Exact model

Let `r_i` run over the 120 E8 root lines of squared norm two in eight
coordinates. Use the representative with first nonzero coordinate positive.
The doubled roots `x_i=2r_i` are the 56 vectors `2e_a +/- 2e_b`, `a<b`,
and the 64 sign vectors with first entry positive and even minus parity.
Order them reverse lexicographically, as in the source.

The following rows form the matrix `N` of nine normals, with eight entries
per row. The true reader normal is `b_k=N_k/8`. This is exactly the source's
A3+D5 frame, in its original column order.

```text
 3  5 -3 -1 -1 -1 -1 -1
-5 -3 -3 -1 -1 -1 -1 -1
-1  1  1  3  3  3  3  3
 3 -3  5 -1 -1 -1 -1 -1
 0  0  0  8 -8  0  0  0
 0  0  0  8  0 -8  0  0
 0  0  0  8  0  0 -8  0
 0  0  0  8  0  0  0 -8
 4 -4 -4  4  4  4 -4 -4
```

Set `T_ik = r_i dot b_k = x_i dot N_k / 16` and
`G_ij = r_i dot r_j`. The allowed complex matrix `D` satisfies the all-pairs
identity `D T^transpose = 2G`, with ordinary transpose. Charge term k by

```text
rho_k = rank_F2 B[X_k,Y_k],
B_ij = (G_ij+1) mod 2,
X_k = {i : D_ik != 0},     Y_k = {i : T_ik != 0}.
```

Every term is charged separately. This is the decoder COPY model of
DreamingOfClouds #717/#595/#446, not a whole recursive child invoice.

## Proof

### All complex decoders have four common-shift columns

The roots span eight dimensions. Thus the all-pairs identity is equivalent
to the 120 row equations `sum_k D_ik N_k = 8x_i`. The eight normals
`N_1,...,N_8` are independent, and the only dependency is
`N_0+N_1+N_2+N_3=0`. These are exact rational finite premises checked by the
verifier. Define the rational row `d_i` by `d_i0=0` and solve the remaining
eight-by-eight system. Every complex solution is exactly

```text
D_ik = d_ik + t_i   for k=0,1,2,3,
D_ik = d_ik         for k=4,...,8,
t_i arbitrary in C, independently for every root line.
```

No restriction to sampled shifts or a coefficient alphabet is used.

### Binary deficiency reduces the optimum to two finite statements

The binary matrix B has rank nine. Project its rows to nine independent
columns to obtain labels `l_i in F2^9`. This projection is an isomorphism
on the row space. Every reader restriction `B[:,Y_k]` still has rank nine,
so restriction to `Y_k` is also injective there. Consequently

```text
rho_k = dim span{l_i : i in X_k}.
```

The five fixed row supports, k=4,...,8, each have label rank nine, so they
always cost 45. For k=0,...,3 define their annihilators

```text
K_k = {w : w dot l_i=0 for every i with D_ik!=0},
delta_k = dim K_k.
```

The complete cost is `81 - sum_(k=0)^3 delta_k`. It suffices to bound that
deficiency sum by nine.

If `w in K_j` and `z in K_k` both evaluate to one at line i, then both
coefficients vanish. The common-shift formula forces `d_ij=d_ik`.
Call w and z compatible for this pair when that necessary condition holds
on every root line. For a plane `U=<a,b>` in `K_j`, put

```text
H_k(U) = {z : z is compatible with every member of U},  k!=j.
```

This is the annihilator of the labels on
`(supp(a) union supp(b)) intersect {i:d_ij!=d_ik}`. Checking the two basis
characters therefore checks the entire plane. Necessarily `K_k subset H_k(U)`.

The exhaustive finite premises are:

1. At every anchor j and every binary plane U, each of its three partner
   spaces `H_k(U)` has dimension at most one.
2. For every subset J of the nonzero partner spaces, let z_k be its unique
   nonzero character and let F be the span of all labels on
   `supp(z_k) intersect {i:d_ij!=d_ik}`, for k in J. Then `dim F >= |J|`.

If every delta is at most one, their sum is at most four. Otherwise choose
an anchor j with `delta_j>=2` and a plane U in `K_j`. Premise 1 makes every
other nonzero `K_k` one-dimensional; let J be exactly these k. Compatibility
forces all of `K_j` to annihilate F, so

```text
sum delta_k = delta_j + |J| <= 9-dim F+|J| <= 9.
```

This proves cost at least 72 for every complex shift assignment. The proof
adapts the deficiency-plane method of Philipp / mightyOil #1248 and the
forced-space argument of Adam Gall #2062, with their credit retained.
Their different normal families are not replayed or assumed to imply these
finite premises.

### Complete finite coverage

Characters are exactly the 512 nine-bit vectors. Every plane has three
nonzero vectors and the unique ordered representation `0<a<b<a xor b`.
Thus the increasing pair loop checks each plane once, giving
`511*510/6 = 43,435` planes per anchor. All four anchors are checked,
without assuming a symmetry transport.

For each anchor, the numbers of planes with zero, one, two and three nonzero
partner spaces are respectively `18,211, 18,144, 6,237, 843`. Their ordered
partner triples have 767 distinct values. The verifier checks all 3,453
triple/subset cases per anchor for premise 2, including the empty subset.
Grouping by the complete triple is exact because both its character values
and the anchor's forced spaces are retained.

The compatibility-table method also agrees with literal binary annihilator
evaluation for every partner and all 511 nonzero characters, giving 1,533
checks per anchor. This is a separate computation within one verifier, not
independent human review. Across all anchors the counts are 173,740 planes,
13,812 subset cases and 6,132 literal annihilator checks.

### Attainment

Take all shifts zero in the base solution `d_i0=0`. Its ranks are
`(0,9,9,9,9,9,9,9,9)`. To keep all nine terms active, change only the shift
at doubled root `(2,2,0,0,0,0,0,0)` to four. The ranks become
`(1,8,9,9,9,9,9,9,9)`. Both totals are 72. The verifier checks all 14,400
all-pairs identity entries for each witness and prices the literal restricted
binary pairing matrices, rather than accepting the deficiency formula as
their bill.

Controls reject an altered coefficient, an omitted fixed D5 term and a
swapped reader. A noncritical rational shift remains an exact positive
control. Each anchor also exhibits a subset where discarding its forced
constraint would falsely permit deficiency above nine. All scientific checks
use explicit exceptions and remain active under optimized Python.

## Reproduction

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/a3-d5-decoder-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/a3-d5-decoder-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/a3-d5-decoder-floor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/a3-d5-decoder-floor --check-source-history
```

Any CPython 3.12 executable can replace the displayed interpreter. Expected
markers are `PASS_A3_D5_DECODER_FLOOR`, `PASS_REGISTERED_RESEARCH_PACKAGE`
and `PASS_RESEARCH_COMMIT_BYTES`. Direct verification writes nothing unless
`--receipt /outside/package/new-file.json` is supplied. The generated JSON
receipt binds all five package files by SHA256. No receipt is handwritten.
The direct mathematical replay also works without Git or other packages.

## Sources, scope and limitations

The exact retained base is `ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c`, priority
revision 7. [SOURCES.json](SOURCES.json) binds the retained PR1224 source,
proof, candidate data and search record as historical provenance. The source
PR head is `00e6ed0810b8ebc7f6133e2c036d0f1c9a3a4162`. No predecessor code is
imported at replay. Credit joaqcoo for the normal form and candidate;
DreamingOfClouds for the separate pairing-rank model; Philipp / mightyOil and
Adam Gall for the proof method; and the retained E8 geometry, eight-term
decoder and selected-supplier lineage, including themilkman216 and woklerx.

[TASK.json](TASK.json) declares the changed scope from the physical
`complex-rank-shape-decoder` card to this fixed-family side result. Its
historical first-step command was attempted and fails with
`KeyError: complex_profile` on the changed selected schema. The current
`scripts/research_selected_baseline.py` source-binding orientation passed.
Neither orientation command supplies scientific evidence for this theorem.
[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19146053).

Live open PRs, the account's preceding 24 hours of contributions, recent
Discussion claims and local reservations were checked. Distinctive main-tree
README and merged-PR searches supplemented the overlap helper's complete
remote pagination. Its sparse local notes were incomplete. No same-family
optimum was found in that stated coverage; this is not proof of novelty.

The result is specific to this unpunctured fixed nine-normal frame and
separate-term binary pairing-rank billing. Changed normals, punctures,
masked-only exactness and shared COPY billing are outside scope. Source
preparation, transport, frames, dirty restoration, hosting, precision, stock,
compiler and the whole consumer invoice remain unknown. The family does not
justify a new construction round without those costs. No Lean, Docker,
selected operator replay or complete multiplication theorem was run or
claimed. Independent human and formal proof-kernel review are unclaimed.

Power of Ten inspection: no recursion, dynamic evaluation or subprocesses
occur in the verifier. All mathematical domains are fixed, with 120 roots,
nine-bit characters, four anchors and 43,435 planes per anchor. Elimination
has at most 120 bit steps per row. Functions are below 60 lines. Exceptions
check the exact identities, ranks, domain coverage and boundaries under both
normal and optimized execution. The five source files are capped at 1 MiB
each before receipt hashing. Python's exact integers, Fractions and temporary
collections allocate dynamically, a managed-runtime deviation from fixed
steady-state allocation. The fixed matrices, character tables and finite
signature sets bound live collections; allocation internals are not measured.
Warning-strict execution and AST inspection are used. A separate static
analyzer and a fixed-allocation native implementation are not supplied.

## Open next questions

Can this A3+D5 family beat the applicable COPY comparator after a specified
nontrivial puncture? Reader ranks, the five fixed-term costs and the finite
compatibility premises may change. First choose a geometrically justified
live set and derive all nine reader spans and fixed row-support ranks before
searching shifts. A replacement proof and the complete physical consumer
invoice remain blockers. This question is not reserved here.
