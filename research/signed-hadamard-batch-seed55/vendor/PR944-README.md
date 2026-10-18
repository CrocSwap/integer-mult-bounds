# Signed connector walks: an exact three-by-three obstruction and repair

**Research construction and finite restricted-query classification; no new
kappa.** The binary connector result in [PR934](https://github.com/CrocSwap/integer-mult-bounds/pull/934)
does not automatically extend to signed integer coefficients. We give the
precise three-by-three boundary and an explicit repair:

- Of all **19,683** matrices in `{-1,0,1}^(3 by 3)`, **19,395** attain two
  queries per active operator. This includes all 512 unsigned matrices.
- The other **288** matrices form one orbit under row/column permutations and
  sign changes. Every one needs **14 queries**, and an explicit 14-query word
  is supplied. The minimum is within the alphabet below, not general circuits.
- For the canonical example, recursively lowering six factor products of
  lengths 2 through 7 uses **308 leaf calls**, versus **388** for row stars or
  **676** for column stars. All three schedules use **four dirty arrays**.
  This is a charged operation comparison, not a measured speedup.

From the repository root, with standard-library Python 3.10 or later:

```sh
python3 -I -O -B research/signed-connector-obstruction/verify.py
```

The JSON result must have `status: PASS_SIGNED_CONNECTOR_OBSTRUCTION`,
`matrices: 19683`, `obstructed_minimum_14: 288`, and leaf counts
`row_stars: 388, column_stars: 676, signed_walk: 308`.
`test_package.py` checks relocation, deterministic regeneration and corruption.
The verifier does not import the generator or any predecessor implementation.

## Interface

Let `x_0,x_1,x_2,y_0,y_1,y_2,z` be seven distinct length-L arrays with arbitrary
initial contents. The A_i and B_j are fixed additive linear operators over Q
(integer matrices give an exact realization). They need not commute or be
invertible. We require the entire map

```
x_j -> x_j,       z -> z,
y_i -> y_i + sum_j M_ij A_i B_j x_j.
```

The only permitted queries, each charged separately, are

```
B_j^s: z   += s B_j x_j,
A_i^s: y_i += s A_i z,       s in {-1,+1}.
```

Every complete query preserves its source, other data, private scratch and
prescribed head positions. Its increment is independent of the target's old
contents. Negative means subtract the same increment, **not** apply the inverse
of the underlying linear operator. It is the inverse of the additive shear.
The six data arrays and z remain reserved and cannot enter child scratch.
Coefficients, input arrays, frames and port bindings remain fixed throughout.
No outside observer consumes intermediate output values.

Combined queries, arbitrary scalar coefficients in one query, extra connectors,
direct product queries, copies, overwrites and other data operations are
excluded from this alphabet. The lower bound requires correctness for free
generic operators. A particular zero map, special algebraic relation, or
restricted input can have a cheaper implementation. Characteristic two has a
different coefficient algebra; finite characteristic and rounded/nonlinear
readouts are not covered by the characteristic-zero minimum theorem.

## Canonical obstruction and fourteen-query word

Use

```
M = [ 1  1  1 ]
    [ 1  1 -1 ]
    [ 1 -1  0 ].
```

The following is the literal chronological program; all signs are essential:

```
B0- B0- A2- B0+ B1- A1- A2+ B2- A0- B0+ B1+ A1+ B2+ A0+
```

Write `z = z_initial + q_0 B_0 x_0 + q_1 B_1 x_1 + q_2 B_2 x_2`.
The successive q vectors after each B query are

```
(0,0,0), (-1,0,0), (-2,0,0), (-1,0,0), (-1,-1,0),
(-1,-1,-1), (0,-1,-1), (0,0,-1), (0,0,0).
```

Each output has one negative and one positive readout:

| Output | Negative read at q | Positive read at q | Difference |
|---|---|---|---|
| y_0 | (-1,-1,-1) | (0,0,0) | (1,1,1) |
| y_1 | (-1,-1,0) | (0,0,-1) | (1,1,-1) |
| y_2 | (-2,0,0) | (-1,-1,0) | (1,-1,0) |

Linearity cancels A_i z_initial and gives the desired rows of M. The connector
returns exactly to its initial dirt and no source is modified. This argument
holds at every L, including for noncommuting operators.

## Lower bound and exhaustive finite reduction

The signed sum of B_j query coefficients must be zero to restore z. A nonzero
column needs at least one B_j occurrence, hence at least two, of opposite sign.
Similarly the signed sum of A_i queries must be zero to eliminate A_i z_initial.
Every nonzero row needs at least two A_i calls. Consequently

```
N >= 2 (number of nonzero rows + number of nonzero columns),
```

and every operator's occurrence count is even. For the canonical matrix the
bound is 12. At 12 calls each B_j occurs once with each sign, and each output
has precisely two oppositely signed readouts. Thus a 12-call word exists **if
and only if** there is a closed source path consisting of one `+e_j` and one
`-e_j` for each j such that every row of M is a difference of two visited q
vectors. Output queries can be inserted at these visits in any order: they
do not change z, any x_j or another output, and their private scratch restores.

There are exactly `6!/(2!2!2!) * 2^3 = 720` such signed paths. The generator
uses multiset permutations and first signs. The independent verifier instead
uses a depth-first traversal of signed moves, admitting each coordinate twice
and forcing the second sign opposite to the first. It checks all 720 distinct
closed paths and all ordered pairs of their seven visited vertices. None
contains differences for all three canonical rows. The 720 coverage masks
have 38 distinct values, retained in the certificate with a path digest.

This is an exhaustive finite exclusion **after a proved reduction of every
possible 12-query word**. It is stronger than failure to find a word in a
heuristic search. Since all counts are even, 13 calls cannot work either.
The explicit word attains 14. This establishes the claimed minimum in this
fixed alphabet. It does not establish an impossibility for larger query
alphabets or the multiplication algorithm.

For each of the 19,683 matrices the verifier either constructs readouts on one
of those 720 paths, or finds it in the signed/permuted orbit of the canonical
obstruction. It replays each full word and its inverse in a free noncommutative
module on all seven independent input symbols. Zero rows have no readout;
queries for zero columns are deleted. Deleting them preserves every required
row difference because those coordinates have coefficient zero. This gives
the support bound also for degenerate patterns, including the empty matrix.

The 288 missing matrices are **exactly** the canonical orbit, so transformed
14-query words attain their common lower bound. Row sign changes negate the
corresponding A queries; column sign changes negate the corresponding B
queries, and permutations relabel them. Each missing matrix has full row and
column support. The certificate contains the whole missing set and the seed
fixture, index 53 in its lexicographic ordering. No stochastic pruning is used.
The stopping rule is completion of these finite domains, with no larger search.

These are written reductions plus exact executable finite certificates, not
proof-assistant verification and not a formal multiplication theorem.

## Complete recursive costs and physical scope

Let c_F(L,w) be a complete query cost at its fixed ports, using a common price
valid for both signs. It includes arithmetic, source/coefficient access,
target updates, private-work restoration, routing, head returns, and any
required frame conversion. If costs differ by sign, sum the actual signed
instruction costs instead; the unit-query minimum alone is not that optimum.
Preparation P_F and initial role/shape/layout admission I are separately paid.
The canonical word's complete bill is

```
C_walk = I + sum_F P_F + 4 c_B0 + 2 c_B1 + 2 c_B2
         + 2(c_A0 + c_A1 + c_A2) + D_walk.
C_row  = I + sum_F P_F + 6 c_B0 + 6 c_B1 + 4 c_B2
         + 2(c_A0 + c_A1 + c_A2) + D_row.
```

D charges stored instructions, selection and dispatch. Coefficients and ports
are the same in both programs. The recursive-query saving is
`2 c_B0 + 4 c_B1 + 2 c_B2`; an application must also compare D and layout.
No input access or full-row volume is divided by the number of outputs.

For factors in application order, split a product F into a right prefix R and
left suffix L. With a fresh dirty connector w and disjoint private child pool,
execute `R(x,w); L(w,y); inverse(R)(x,w); inverse(L)(w,y)`. The inverse of an
expanded word reverses its order and negates every sign. It includes every
restoration call. With complete restored/head-returning child interfaces,

```
C([f]) = c_f + dispatch_leaf,
C(F)   = 2 C(R) + 2 C(L) + dispatch_node,
h([f]) = 0,              h(F) = 1 + max(h(R),h(L)).
```

Balanced contiguous splits give `ell(1)=1` and
`ell(n)=2 ell(floor(n/2))+2 ell(ceil(n/2))`. For lengths 2..7 the prices are
`4,10,16,28,40,52`, assigned to `B0,B1,B2,A0,A1,A2` respectively.
The certificate supplies the literal 308-leaf word; it is independently
checked against the ordered products, not just against this recurrence.

| Schedule, same factors and ports | Queries | Leaf calls | Dirty arrays |
|---|---:|---:|---:|
| Row stars | 22 | 388 | 4 |
| Column stars | 22 | 676 | 4 |
| Signed walk | 14 | 308 | 4 |

All six data rows remain live. The batch connector plus maximum child depth
requires `1 + ceil(log2 7) = 4` dirty rows, for ten mutable rows total.
No clean length-L row, full-array copy, initialization or free frame change
is used. Scalar accumulators, loop indices and instructions are separate costs.

For any positive equal-by-sign query prices, an obstructed pattern costs at
least `2 sum_F c_F + 2 min_F c_F`: every count is even and at least one must
exceed two. Here the cheapest query is B0, and the word repeats precisely B0.
Thus 308 is also the weighted minimum for this fixed query alphabet and this
fixed lowering. It is not a minimum over alternative product decompositions,
echo trees, shared factor implementations, or primitives admitted by a supplier.

### A fully paid dense realization

For exact integer leaf matrices with entries bounded by H, use a dense dot
product for each target coordinate and then add/subtract it. All ten mutable
rows precede all 27 read-only coefficient matrices on one data tape. For each
term, visit its coefficient and source word; then visit the target word. Return
the head to cell zero after **each** complete leaf. No gather is free.
EXPECTED.json counts this literal trace and checks it against a separate
closed-form travel sum for L=1..5 and all three schedules.

At L=3 the walk has 2,772 coefficient reads, 2,772 source reads, 924 target
read/write pairs, 2,772 multiplications, 3,696 additions, 462 sign negations,
924 scalar accumulator resets, and 837,128 word-cell head moves. The row-star
comparator has 919,024 head moves; both use 30 mutable and 243 coefficient
words. Admission reads all 273 supplied words; producing those coefficients
from a different representation is additional P_F. The fixed layout supplies
disjoint ports and read-only coefficients. No Clifford/frame conversion occurs
in this dense realization; a supplier using other frames must price its own.

For initial magnitude D, a word of N leaves has intermediate infinity norm
at most `D(1+L H)^N`. Taking
`w = 2 + ceil(log2(max(1,D,H))) + N ceil(log2(1+L H))` signed bits suffices,
including scalar dot-product intermediates. Use N=676 for a common safe width
in all three comparisons. Charge w per word load/store/head-cell traversal,
the counts times integer multiplication/addition costs, and the scalar work.
Instruction storage is 14 bits per leaf here (5 for factor, 4 per port, 1 sign),
plus O(log L) loop/index registers. Sequential instruction reads/returns,
dispatch and per-data-access index arithmetic are charged in D. The finite
pattern selector or this fixed word and O(N) lowering/emission work are also
paid; no large precomputed schedule is treated as free advice.

The Python interpreters verify this algorithm; they are not a measured tape
implementation. Rational and modular dense cases are additional algebraic
checks, not claims that the integer word-size bound prices those domains.

## Failure controls and remaining obligations

The verifier checks all 19,683 complete free-operator maps and inverses, 330
dense basis/dirty/rational/modular cases for two fixtures, 22 mathematical
controls and 15 tape trace/formula comparisons. Controls include deletion of
each of the fourteen queries, a sign flip, unpaid optimum, a valid nonoptimal
word, dropping signs, a wrong recursive factor, aliased ports, mutable sources,
and nonlinear readouts. The nonlinear example restores z but changes output
with its initial dirt; exact restoration is not a substitute for linearity.
No rounded precision theorem is claimed by this integer construction.

The original experimental base is `91a2094f2e022930069e8cfdc810a3ea1b81cd09`,
whose accepted record was `1661634653669567/10^18` from #799/#589/#555.
Before submission main advanced to `47481c89fd30a43f8f882eb4b391e89c29273fd0`,
selecting #890 at `1661957774647029/10^18`. This branch is based on that
refreshed main; the certificate preserves its original experimental base.
The new selection, construction and review were inspected and are unchanged.
This abstract product pattern has **not** been located or physically hosted
inside the selected suppliers. Common-label/mutable-source realization,
compatible frames, owner admission, whole-row volume, all-size/tape compilation,
precision for approximate children and outer analytic assembly remain open or
inherited. We cannot infer a new kappa or which supplier would bind after an
actual integration. The coordinate-Fourier obstruction is not reopened:
every operator here is fully charged, with no free address transform.

The direct predecessors are PR889's signed common-factor star and PR934's
binary carried-connector walk. Their exact README and notice bytes are retained
under sources/, with Git and SHA256 pins. Their identity and pricing framework
are credited; no predecessor implementation is imported. This contribution
changes the coefficient contract and supplies a sign-order obstruction and
repair, rather than another binary experiment. See [NOTICE.md](NOTICE.md),
[SOURCES.json](SOURCES.json), [CLAIM.md](CLAIM.md), and
[VALIDATION.md](VALIDATION.md).
