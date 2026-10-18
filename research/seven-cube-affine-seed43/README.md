# Affine seven-cube decoding: copy floor 128, peak floor 30

**Scoped structural negative result. No new kappa or physical supplier.**

The smallest seven-port cube admits a cubic, drop-free correction geometry.
Even after arbitrary affine recoding and any finite number of delivered
terms, its algebraic copy-rank sum is at least **128**, equal to its port
count. Two terms attain `64+64`; four attain `32+32+32+32`.

Unlike the affine five-cube result, the sum and peak optima cannot be attained
together. The smallest possible peak term rank is **30**, attained here by
eight terms of total cost 240. Among total-cost-128 decoders, the smallest
peak is **32**. We do **not** claim that 240 is the minimum total under cap 30.

Under the explicitly inherited additive stage ledger, the favorable complete
budget is `D <= (s-1)*128 - s*C <= -128` for every `s>=3`. This grants all
gathers, source access, helpers, arithmetic, frame changes, restoration,
recursive overhead and other nonnegative expenses zero cost. The resulting
negative deficit already excludes positive saving in that model. No circuit
implementation or further supplier optimization is warranted by this result.

## Object and exact scope

Identify the 128 ports selecting one coordinate from each of seven pairs
with `x in F2^7`. Write `j=7-|x XOR y|` for intersection size and use

```
G[x,y] = (4/3)(j-1)(j-3)(j-5)
       = sum_{S subset {0,...,6}, |S|<=3} (-1)^(sum_{i in S}(x_i+y_i)).
```

Thus G is an integral positive semidefinite Gram matrix of rank 64,
realized by the 64 Walsh features of degree at most three. Distinct ports
with odd intersection 1, 3 or 5 are orthogonal. Coordinate-star decoding
has matrix

```
B[x,y] = j mod2 = 1+p(x)+p(y),    p(x)=x0+...+x6 in F2.
```

Adding the intersection-1/3/5 corrections gives the identity. This is
PR231's star-family identity specialized to seven ports. The common
coordinate-star code is exactly the eight-dimensional affine code
`C={a dot x+c}`. The constant is available as the XOR of two complementary
coordinate stars; no free empty-star observation is assumed.

Allow every finite binary factorization `B=sum_i f_i g_i^T`, with nonzero
`f_i,g_i in C`, including nonsymmetric and redundant factorizations.
Equality is required on **all** 16,384 port pairs, not only on a correction
mask. Its objective is

```
C_total = sum_i rank_Q G[support(f_i), support(g_i)].
```

This is an algebraic lower bound under the inherited per-total copy rule,
not an invoice that realizes either witness. Changed Gram matrices,
non-affine masks, masked identities, extra ports (`p>7`), interactive
delivery and information retained between stages are outside the result.

## Exhaustive finite evidence

An affine form is encoded by an integer 1 through 255: bits 0 through 6
are linear coefficients and bit 7 is the constant. Simultaneous cube
translation and coordinate permutation preserve G. For linear parts a,b,
the orbit key counts coordinates of types `(1,0),(0,1),(1,1)`; when a=b is
nonzero it also records the XOR of the constants. Independent a,b allow
both constants to be normalized by a translation. A zero linear part is
necessarily the nonzero constant form. These observations cover all cases.

There are **127 ordered orbits**, covering all **65,025 ordered pairs**.
The separate checker verifies multiplicities both combinatorially and by
enumerating the 255 forms. Both compute exact rational ranks, with no
floating-point or finite-field acceptance decision.

| Rank | Ordered pairs | Maximum diagonal coverage |
|---:|---:|---:|
| 20 | 56 | 0 |
| 30 | 1,680 | 32 |
| 32 | 644 | 32 |
| 33 | 3,360 | 32 |
| 36 | 4,704 | 32 |
| 39 | 12,320 | 32 |
| 42 | 21,000 | 64 |
| 44 | 56 | 0 |
| 45 | 7,840 | 32 |
| 48 | 11,620 | 64 |
| 54 | 1,736 | 64 |
| 64 | 9 | 128 |

The certificate also contains the full reduced factorization census:

| Terms | Reader sets/multisets | Source assignments, including zeros | All factors nonzero | Minimum |
|---:|---:|---:|---:|---:|
| 2 | 3 | 3 | 3 | 128 |
| 3 | 7 | 1,792 | 1,777 | 138 |
| 4, distinct readers in a rank-three space | 2,205 | 564,480 | 494,802 | 128 |

Full cost histograms and attaining words are in [CERTIFICATE.json](CERTIFICATE.json).
The enumeration stops at the end of these exact domains; there is no
heuristic search, numerical tolerance, timeout exclusion or novelty claim
based on a different random seed.

## Why this proves the unrestricted finite-term floor

The binary rank of B is two; its row and column code is
`U=span{1,p}`. If A and D list the n reader and source columns, respectively,
`B=A D^T` and Sylvester's inequality gives `rank(A)+rank(D)<=n+2`.
Each span contains U. Transposition preserves every pairing cost.

For two terms, both spans equal U: the three unordered bases are exhausted.
For three terms, one span equals U: after transposition its nonzero columns
are a multiset from the three nonzero members of U. Exactly seven such
multisets span U. The census includes repetitions and gives the exact
three-term minimum 138.

For four terms, one factor span has dimension at most three. Repeated
reader columns can be merged by XORing their source columns. This cannot
increase cost: the XOR support lies in the union of the two old supports,
and concatenation rank is subadditive. Zero factors can then be discarded.
The resulting two-/three-term decoder already costs at least 128. If four
distinct reader columns remain, their span has dimension three and contains
U. There are `(256-4)/4=63` such spaces, each with seven nonzero vectors and
35 four-element subsets. Each subset spans its space, and each of the
eight source coefficient columns has a one-dimensional solution freedom.
That is exactly `63*35*256=564480` assignments. The minimum is 128.

The diagonal of B is one everywhere, so the sum of the intersection sizes
`|support(f_i) intersect support(g_i)|` must be at least 128. Using the
table, the largest possible coverage for five terms of cost at most 127 is
64; for six it is zero. These are deliberately optimistic type-multiset
relaxations, checked by dynamic programming and independent enumeration.
Seven or more terms cost at least `7*20=140`. Zero or one term cannot have binary
rank two. All finite term counts are therefore covered.

The three-/four-term enumeration is necessary here: unlike the five-cube
argument, the seven-cube diagonal relaxation alone permits four rank-30
terms, and the one-U-factor estimate permits three rank-42 terms. Neither
relaxed tuple solves the full decoder identity. They are explicit controls
against claiming the floor from counting alone.

## Sharp witnesses and the peak separation

The two parity totals give `B=p p^T+(1+p)(1+p)^T`, each of rank 64.
For the four-term witness take `h=x1` (seed43 mod7) and `q=p+h`:

```
B = h q^T + q(1+h)^T + (1+h)(1+q)^T + (1+q)h^T.
```

Each term has rank 32. To attain peak 30, let
`a=x0`, `b=x1+x2`, `c=x3+x4`, `d=x5+x6`. The eight pairs of forms are

```
(b,1+a), (1+b,a), (a,1+b), (1+a,b),
(c,d), (d,1+c), (1+c,1+d), (1+d,c).
```

Their binary sum is B and each has rank 30. Every term of smaller rank
has rank 20 and zero diagonal, so peak 30 is sharp.

For total cost 128, the same diagonal relaxation at budget **128** excludes
five and six terms; seven already cost 140. Two terms have peak 64, three
terms cost at least 138, and four terms of peak at most 30 would have total
at most 120, contradicting the proved sum floor. The rank table has no
rank 31, and the four-term witness attains peak 32. Thus the two optima
cannot be attained together. The exact total optimum under peak cap 30
is not established; its diagonal/term-count relaxation gives a lower
bound 140 and the displayed word gives an upper bound 240.

## Reproduce and verification scope

From the repository root, Python 3.12 and the standard library:

```sh
python3.12 -I -B scripts/research_package.py --package research/seven-cube-affine-seed43
```

This runs both implementations. Expected markers:

```
PASS_SEVEN_CUBE_AFFINE pairs=65025 orbits=127 assignments=566275 copy_floor=128 peak_floor=30 controls=10 no_new_kappa
PASS_SEVEN_CUBE_INDEPENDENT pairs=65025 orbits=127 assignments=566275 literal_entries=49152 controls=10 no_new_kappa
```

`verify.py` uses the intersection polynomial, gcd-normalized integer
elimination and subset-syndrome solutions. `independent.py` imports no
generator or predecessor code: it builds Walsh features, uses Fraction
elimination and solves coefficient equations by binary RREF. It checks
the 64 coefficient equations for every enumerated source assignment.
Both compare every certificate field, check the three witnesses literally
on 49,152 port pairs, and run ten semantic or proof-boundary controls.
Both work under `-I -O -B`. Certificate generation is explicit and refuses
to overwrite an existing path. The optional command
`python3.12 -I -B research/seven-cube-affine-seed43/test_package.py` checks
both programs in a read-only relocated checkout and rejects five artifact/source
corruptions with both implementations. [VALIDATION.json](VALIDATION.json) records
the local environment and executed checks; hosted CI is separate.

This is exact finite evidence supporting the written scoped argument,
not proof-assistant verification, independent human review, or a proof
of the multiplication theorem. The selected cold replay, native supplier,
hosting, precision/tape, all-size/compiler, common-label/mutable-source,
bit H1-H5 and analytic transfer obligations are not discharged here.

## Provenance, overlap and credit

Assignment seed **43**, drawn with OS randomness, selected the structural
decoder track. Exact base: `64039f1bd3b6a523b96083fd858ad040a75e3030`.
The selected conditional result at this base is PR1094,
`kappa=836330098538459/500000000000000000`, with complex binding and bit
supplier PR589. Its source manifest, actual T16 construction and maintainer
review were followed. This package changes none of them or `upstream/`.

[TASK.json](TASK.json) records the three candidate scopes and local claim;
[SOURCES.json](SOURCES.json) pins the base, Git blobs and SHA256 digests;
[OVERLAP.json](OVERLAP.json) records the bounded live scan and its limits.
No pinned sprint issue existed, so the donor's local-claim fallback was used.
The catalogue card is marked changed: this is a seven-port binary/cubic
side result, not an E8 complex masked-decoder construction.

Credit **Joel Pulikkan / GamingPuzzled (PR231)** for the star-family parity
identity; **Ross Richardson (PR958)** for the five-port geometry and
optimistic-budget approach; **martinxxx9 (PR1046)** for the affine five-cube
copy floor and factor-span reduction; and **icekylinx/eumemic**, with the
retained **DreamingOfClouds, Jacob Sussman and Zhihao Chen** copy/frame
lineage. PR1046 is incorporated; this does not reopen its five-cube search.
Pending PR1177, PR1222 and PR1482 treat nonlinear masks on that five-cube,
not this seven-cube. They are overlap context, not theorem dependencies.

Prepared by **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex
assistance** in mathematics, both implementations, verification and prose.
Apache-2.0. The separate implementation is by the same AI-assisted author.

## Open next questions

Can a fully priced two-stage construction retain one of the four displayed
coded totals and thereby change the additive `s*C` charge? That premise
must change before this geometry could help the supplier. A feasible first
step is an exact arbitrary-dirty two-stage map using the explicit four-term
decoder, charging source access, all frame transitions and restoration.
The blocker is the absence of such a legal physical interface; a rank-table
optimization alone cannot remove the present negative deficit. This is an
unclaimed next question, not evidence that retention is possible.
