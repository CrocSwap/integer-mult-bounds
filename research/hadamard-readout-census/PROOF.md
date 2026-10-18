# Exact readout census for the eight-source-call Hadamard interface

## Object and hypotheses

This extends Cinna Davis's PR997 at
`b3fda8d59436103b195069a6328cbf5d74f73bc0`. PR997 samples 4,000 source
paths and allows at most two signed differences per output. Here every
eight-source-call path is covered, with arbitrary repeated signed readouts.
The finite optimum below concerns this explicit class, not arbitrary circuits.

There are distinct read-only sources `x_j`, distinct accumulating outputs
`y_i`, and one arbitrary dirty connector `z`. A source query is
`z += s B_j x_j`; a readout is `y_i += s A_i z`, where `s` is +1 or -1.
Each `A_i` and `B_j` is an exact linear map. All private child workspace and
sources restore on return. Maps need not commute. Both signs have the same
complete query price, independent of state, placement and other queries.
No output is borrowed as scratch, no initialization of `z` is assumed,
and no further scalar operations on these rows are admitted in this class.
Correctness for the optimum means the coefficient identity for independent
formal A/B operators and independent initial-data symbols. Special maps with
additional relations (for example, a zero A map) can admit cheaper words and
are outside this lower bound. The emitted construction remains correct for
arbitrary exact linear maps, including singular ones.

The desired coefficient matrix, in fixed output/source order, is

```
H = [ + + + + ]
    [ + - + - ]
    [ + + - - ]
    [ + - - + ].
```

The restriction is **exactly one positive and one negative B query per
source**. Thus there are eight source calls and `8! = 40,320` source orders.
Readouts may be repeated arbitrarily at any visited connector state.

## Why finite enumeration covers arbitrary readout multiplicities

At a visit with source coefficient vector `q`, the connector is
`z_initial + sum_j q_j B_j x_j`. A signed readout contributes its sign to
the coefficient of `A_i z_initial` and contributes that sign times `q`
to row i of the desired product coefficients. Since the connector dirt is
arbitrary, positive and negative readout counts must be equal, say k each.
Consequently a correct readout is precisely

```
sum_{r=1}^k q_positive[r] - sum_{r=1}^k q_negative[r] = H[i].
```

The multisets can repeat states. Any integer coefficient representation
with zero coefficient sum has this form. Redundant cancellations cannot
improve a minimum with strictly positive readout prices. Each unit coordinate
difference is an edge of every admitted path; hence four differences always
realize every sign row of H. At most eight readout calls per output suffice.
Checking k=1,2,3,4 therefore finds a global minimum for that output on that
path, even though the original interface allows arbitrarily many readouts.

Each coordinate's first sign is independently + or -. Remove those signs:
each coordinate follows 0 -> 1 -> 0, so the unsigned event orders are exactly
the `8!/(2!^4) = 2,520` multiset permutations of `00112233`. The 16 first-sign
choices restore all 40,320 signed paths. `census.py` enumerates those paths,
builds all equal-cardinality sums of visited vertices, and tests the equation
above with integer tuples. It does not restrict readouts to two differences.

`verify.py` uses a different enumerator: all permutations of the eight
distinct signed events. Its readout calculation forms the difference set D
of visited states. A sign row needs two calls if it lies in D, four if in
D+D, six if it lies in D+D+D, and otherwise eight, by the unit-edge bound.
Both algorithms produce the exact same 114-profile frequency table.
The verifier caches 1,022 normalized vertex sets; it still counts every
distinct signed path, including different paths with the same visited set.

Output minima are jointly attainable: readouts at a visit do not alter the
connector or sources and commute across distinct outputs. They can all be
inserted at their respective visits. There is no competition for a tap.

This is an exact finite certificate with a written completeness argument.
It is not a proof-assistant verification or a proof of the multiplication
theorem. The finite histogram and all attaining words are in CERTIFICATE.json.

## Result: query optimum and weighted envelope

The 114 profiles have 22 undominated profiles. They are exactly all distinct
permutations of the following three patterns:

```
(2,4,4,4)    4 permutations
(2,2,6,6)    6 permutations
(2,2,4,8)   12 permutations.
```

The smallest total readout count is 14, so the minimum total query count
within this class is **22**. This independently closes PR997's unclaimed
finite optimum for the stated eight-source-call class. It excludes paths
with ten or more source calls, other query alphabets, output borrowing,
source-dependent prices, and non-linear or rounded children.

Let a <= b <= c <= d be the four positive, complete A-query prices in sorted
order. Sorting prices only selects an attaining profile in fixed row order;
it does not reorder the demanded matrix or the factors of any child. Since
all listed profile permutations are attained, exchange of unequal weights
gives the minimum in each family by assigning more calls to cheaper rows:

```
family (2,4,4,4):  4a + 4b + 4c + 2d
family (2,2,6,6):  6a + 6b + 2c + 2d
family (2,2,4,8):  8a + 4b + 2c + 2d.
```

The third family is no dearer than the second because `2a-2b <= 0`.
Thus the exact readout-price envelope is

```
R(a,b,c,d) = 4a + 4b + 2c + 2d + min(2c,4a).
```

Add `2 sum_j price(B_j)` for the complete query price. If c < 2a, a
22-query word attains the optimum. If c > 2a, a 24-query word attains it.
At c=2a both families tie. Query count alone does not choose the cheaper
word under unequal child prices. All 22 frontier words are independently
replayed, rather than inferring unattested profile permutations.

## Matched recursive lowering: 222 versus 238 leaves

Use PR997's factor lengths, A=[2,3,4,5] and B=[1,2,3,4]. Every factor has a
single exact additive shear. For a product of n ordered factors, split into
b=floor(n/2) first factors and a=ceil(n/2) last factors. A fresh dirty row u
implements the positive product through the literal word

```
u += B source; target += A u; u -= B source; target -= A u.
```

Each negative call is the complete reversed word with signs negated.
Linearity cancels u's arbitrary initial value and restores every scratch
row. Source and target rows are distinct from the pool; all ancestors'
active rows stay outside it. The factors retain their original order.
All children and inverses are included in

```
C(1)=1,              C(n)=2 C(b)+2 C(a)
I(1)=0,              I(n)=1+2 I(b)+2 I(a)
S(1)=0,              S(n)=1+max(S(b),S(a)).
```

C is executed primitive calls, I is executed internal echo nodes, and S is
simultaneously active child scratch. Lengths 1..5 give C=[1,4,10,16,28] and
I=[0,1,3,5,9]. The connector and three dirty child rows give four dirty rows
in both implementations. No clean data array is needed.

The minimum-price profile for this fixture is `(8,4,2,2)`. The complete bill
is `2(1+4+10+16) + 8*4+4*10+2*16+2*28 = 222` primitives.
PR997's pinned `(4,4,4,2)` word has 238. The new word has 24 queries and 66
internal echo nodes; the old word has 22 queries and 72 nodes. This is a
**16-call reduction (8/119, about 6.72%)**, with six fewer echo nodes and two
more top-level queries. No measured multiplication-runtime claim follows.

## Complete cost recurrence and physical obligations

Let E(L,w) price one exact primitive factor shear at row length L and a
common sufficient integer width w. It includes coefficient/phase/source
access, local arithmetic, validation, source restoration and scalar cleanup.
Let D(L,w) price one internal echo node's extra control, and let Q(L,w)
price outer-query dispatch/return and any constant, common port adapter.
Then the exact balanced child recurrence is

```
T_1=E,      T_n=2 T_b+2 T_a+D.
T_batch = P + sum_j 2 T_Bj + sum_i profile[i] T_Ai
          + (#queries) Q + R(word).
```

P includes preparing and restoring program/coefficient/control storage,
port admission, precision setup and final cleanup. There are 24 distinct
factor matrices in either fixture, so matrix input storage is `24 L^2 w`
bits, plus rows and metadata. R(word) explicitly charges placement-dependent
frame changes, coefficient routing, address dispatch and complete head
travel including final return. Every emitted child and inverse is counted.
There is no uncharged call outside this recurrence.

For a literal dense scalar backend, each primitive uses L^2 multiplications,
L^2 additions/subtractions (including the target update), L^2 coefficient
reads, L^2 source reads, L target reads and L target writes. Two scalar
work registers can be initialized once and cleared after every primitive;
the 4 dirty scratch rows and 8 data rows require `12 L w` bits. Arbitrary
initial dirt is represented independently in the free-operator interpreter.
Finite integers are exact; a physical bounded-word backend must choose w
from a proven prefix bound, or charge exact multiprecision arithmetic.
Rounded children are outside the restoration hypothesis.

For the matched finite dense fixtures, initial entries have magnitude at most
7 and each factor has infinity operator norm at most 6. The separate prefix
bound includes partial dot products, target addition before cancellation and
the appended literal inverses. Its exact common bound and sufficient signed
width are emitted in the verifier receipt for both words in this domain. This is
not an all-length precision theorem or a physical word/tape admission.

With common E,D,Q and the same P, the two displayed words cost

```
new: P + 222 E + 66 D + 24 Q + R(new)
old: P + 238 E + 72 D + 22 Q + R(old).
```

Their comparison requires `2Q + R(new)-R(old) < 16E+6D`.
If R is constant, the exact envelope switches at `Q=8E+3D`, consistent
with c=2a after including each query's dispatch in its price. If Q=100,
E=1,D=0,R=0, the new word is more expensive; the verifier retains this
negative control. No arbitrary-price dominance of the displayed word is
asserted. Applying the envelope with placement-dependent R requires a
different optimization; the census does not prove its optimum.

No selected supplier hosting, frame realization, tape compiler, rounded
restoration or improved moment has been supplied. The selected κ therefore
remains unchanged, conditional on its inherited interfaces.

## Attribution

PR997 is the direct four-by-four predecessor and supplies the comparison
fixture and interface. Martin's PR1088 (`b0396aad724fec58630fbd4d13a809c562f18d9e`)
establishes a different weighted three-by-three repair; it motivated checking
prices rather than query totals. CubeJerry's PR889, Ross Richardson's
PR934/943/944 and Chafik Boukhalfa's PR628 retain their respective fanout,
connector and balanced-echo credit. No predecessor executable code is
imported. Source notices and exact bytes are retained under sources/.
New work by Cinna Davis, with substantial OpenAI Codex assistance; Apache-2.0.
