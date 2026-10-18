# The eleven-piece `4,5^2,6^8` profile is impossible

## Statement and dependencies

Use the pinned P112 root representatives `r_t`, binary labels `ell(t)` and any
characteristic-zero field `K`. For `h in K^8`, write `c_h(t)=<r_t,h>` and
`C={c_h}`. A piece has weight equal to the binary rank of the labels in its
support. There do not exist eleven independent pieces spanning `T`, with
`dim(T intersect C)>=7` and respective weight upper bounds

```
4,5,5,6,6,6,6,6,6,6,6.
```

This excludes one actual TWOSIDE `(b,t)=(7,4)` profile from DreamingOfClouds's
PR3154 at `708f0ad8928c383de8294aea3c126e9461d2066d`. It does not close that
cell, C5, the P112 decoder floor, supplier admission or an exponent claim.

The retained [root-simplex proof](vendor/ROOT-SIMPLEX-PROOF.md), following the
E8/P112 lineage in [SOURCES.json](SOURCES.json), supplies these premises:

- A binary label flat of dimensions four, five or six supports at most eight,
  twelve or twenty live root lines. On full120 a five-flat also contains at
  most twelve lines. The latter is replayed on all 3,309,747 five-flats here.
  The four-flat bound eight follows directly from the labels' leading bit one.
- `h -> c_h` is injective and a nonzero codeword has at least 53 live entries.
- Any subspace of dimension at most six contains at most 36 full120 root lines.
- Seven-node chamber faces contain respectively `42,28,22,14,16,23,37,63`
  root lines. The 42-line face has a D7 normal and the 63-line face a root normal.
- Independent scalar-root directions with scalar-root pair differences have
  one common scale and orientations making them norm-two roots with pairwise
  inner product one. This follows from the root-plane A2 classification.

The standard Weyl-chamber theorem remains an explicit mathematical dependency.
The replay checks the simple-root positivity, 960 reflection tests and all
7,140 root planes. It is not a proof-kernel formalization of that theorem.

## Quotient reduction to eight vertices

Let `D=T intersect C` and `lambda:T -> T/D`. The quotient dimension is at
most four. The three small pieces have support union `S` of size at most
`8+12+12=32`. Call the eight remaining pieces `q_0,...,q_7`.

The small pieces and any `q_i` have union support at most `32+20=52<53`.
Their quotient images are independent. A dependence would be a nonzero
codeword supported on fewer than 53 coordinates; it cannot be zero because
the original eleven pieces are independent. Thus the quotient has dimension
exactly four. Modulo the three small images its dimension is one. Rescale the
`q_i` to have the same nonzero image in this one-dimensional quotient. Subtract
suitable small-piece combinations `s_i` to obtain

```
c_0=0,    c_i=q_i-q_0-s_i in D,    i=1,...,7.
```

These seven codewords are independent by their distinct coefficients on
`q_1,...,q_7`. They correspond to eight affinely independent vertices in `K^8`.
Every edge codeword is supported on at most `32+20+20=72` coordinates.
Outside `S`, the eight endpoint values differ from the vertex evaluations by
one common coordinate-dependent shift. The eight pieces have combined support
at most `8*20=160`. We prove a larger lower bound.

For eight scalar evaluations at a coordinate, every common shift leaves at
least `8 - maximum equality multiplicity` nonzero entries. This bound is
attained by cancelling a largest equality class. All finite costs below are
these integers, so the bound allows arbitrary shifts, not merely codeword shifts.

## Mixed edges

Here we replay the support-72 alphabet argument from Nick Petalas's PR3176
at `1111a074414c4d2be8b4e230133d873432780814` for seven instead of eight
independent directions. A support-72 codeword has at least 40 orthogonal live
roots. The 36-line rank-six cap forces their rational span to have rank seven.
Their rational annihilator is one-dimensional; hence even over `K` the
direction is a scalar multiple of a rational vector. The chamber-face counts
leave only a root direction or a Weyl transform of the D7 normal.

There are 1,080 projective D7 normals in the finite inventory. Their P112
supports have exact distribution `70:128, 73:896, 76:56`. Thus the allowed
alphabet is 120 root lines and 128 non-root lines. The latter are primitive
vectors with one entry `+1` or `-1` in each coordinate pair, up to common sign.
Even signed permutations preserving the actual deleted frame normalize any
non-root edge to `a=(1,0,1,0,1,0,1,0)`. All 128 transformations are checked.

Translate an endpoint to zero and rescale the selected non-root edge to `a`.
Any other vertex `x` must satisfy `a=s*u+t*v`, `x=s*u` for two distinct allowed
rays and nonzero coefficients. Exact two-ray intersections give 58 possible
vertices. The equation has a unique rational solution whenever its two rays
are independent, also if the original coefficients lie in `K`. The candidate
graph has 595 compatibility edges.

We need six further vertices, so enumerate six-cliques. Complete results are:

| Rank with the anchor | Six-cliques |
|---|---:|
| 4 | 105 |
| 5 | 2,520 |
| 6 | 5,096 |
| 7 | 2,016 |

Among the 2,016 independent cases, delete the 32 largest live costs, a relaxation
of the actual small support. The surviving support-sum histogram is
`162:784, 163:112, 170:784, 175:336`. Thus the mixed branch has support at
least 162, greater than 160. A separate Gram-intersection, three-plus-three
clique join and integer-elimination replay reproduces these exact counts.

## Root-only branches

If all edges are root directions, the retained root-plane argument identifies
an affine root A7 simplex up to a common nonzero scale. Extend each root-star
prefix by every root having the required inner products. Quotient by the
reflections perpendicular to that prefix, which fix it pointwise. Taking every
orbit of even this possibly smaller stabilizer is complete.

The successive orbit sizes are `240;56;27;16;10;6;(2,1)`. There are two
rank-seven representatives. Their full120 cost spectra are

```
ordinary       1:8, 2:56, 3:56
exceptional    0:1, 2:84, 4:35.
```

Allowing arbitrary removal of the eight frame lines and 32 small-support lines
leaves at least 168 in the ordinary branch, but only 158 in the exceptional
branch. The latter is a losing control, not a contradiction. The new weighted
flat-pair lemma addresses exactly this gap.

## Exceptional weighted flat-pair lemma

Let `c` denote the exceptional full120 costs. Their sum is 308. Let `F` be any
orthogonal eight-line frame, and let `U,V` be any two binary label five-flats.
Let `A` be any eight root coordinates. Then

```
sum_{r outside F union U union V union A} c(r) >= 162.
```

This relaxes the rank-four support to eight arbitrary coordinates, but retains
the two actual rank-five flats. It is therefore enough for the application.

Every cost is even. Suppose the union removed cost at least 148. The set `A`
removes at most 32. Each five-flat removes at most `12*4=48`. The orthogonal
frame has cost 16, 20, 24 or 28. A cost-16 frame is immediately impossible,
since `16+48+48+32=144<148`.

For any remaining frame of cost `f`, each five-flat outside that frame must
have cost at least `148-f-48-32=68-f`. If either falls below that threshold,
evenness bounds the complete removed cost by 146. In particular, each relevant
full five-flat has cost at least 40.

An exact reduced-row-echelon enumeration of all four-dimensional annihilators
in `F2^9` covers all 3,309,747 five-flats. It proves the full120 capacity twelve
and retains exactly 3,248 distinct root masks of cost at least 40.

The seven root reflections in the exceptional star preserve the evaluation
costs. On `(1,simple-root coordinates mod 2)` every Weyl transformation is an
invertible binary linear transformation: it acts integrally and invertibly
on the E8 root lattice. Canonical root signs do not matter modulo two. Thus
these reflections preserve label-flat dimensions as well as costs. They split
all 2,025 orthogonal frames into seven orbits. The finite pair check gives:

| Frame orbit size | Frame cost `f` | Required individual cost | Eligible live masks | Maximum pair-union cost |
|---:|---:|---:|---:|---:|
| 105 | 16 | not needed | 0 | not needed |
| 1,260 | 20 | 48 | 86 | 84 |
| 210 | 24 | 44 | 150 | 84 |
| 105 | 20 | 48 | 54 | 84 |
| 105 | 16 | not needed | 0 | not needed |
| 30 | 28 | 40 | 336 | 76 |
| 210 | 24 | 44 | 150 | 84 |

For the nontrivial rows, `f + maximum pair cost + 32` is at most 140,
strictly below 148. Every candidate pair, including identical masks, is tested.
Hence no removed cost reaches 148. Evenness gives removed cost at most 146,
and the surviving cost is at least `308-146=162`. This is a sufficient bound;
sharpness is not claimed.

The separate checker does not enumerate annihilators or use the frame-orbit
reduction. Given the proved five-flat capacity twelve, any cost-40 flat
contains at least eight of the 35 cost-four root labels. Those labels have
binary span of dimension four or five. Dimension at most three is impossible
because a three-flat has only four labels with leading bit one.

If their span is five-dimensional, five of those labels generate the flat;
enumerate all `binom(35,5)` subsets. If it is four-dimensional, it contains
exactly eight high-cost labels. Enumerate all `binom(35,4)` subsets to recover
all 105 such four-flats, and extend each by every binary vector. The union
gives 5,124 distinct five-dimensional candidate spaces. Filtering recovers
exactly the same 3,248 high-cost masks, byte-for-byte after canonical encoding.
The independent checker tests all 2,025 frames directly and obtains the same
pair maxima. It also verifies 840 binary-label reflection relations.

## Finish and scope

A Weyl transformation taking a root-only simplex to one retained representative
moves the original puncture to an orthogonal frame and the two small rank-five
supports to five-flats. The rank-four support still has size at most eight.
Thus the exceptional lemma applies even when the original puncture does not
stay fixed. In the mixed branch the chosen normalizing symmetry does preserve
the puncture. These are different reductions and are not interchanged.

All branches now need at least 162 endpoint incidences outside `S`, whereas the
eight weight-six endpoints permit at most 160. This proves the stated profile
exclusion over every characteristic-zero field. The unmodified original filter
and a separate transcription reproduce the 154 original `(7,4)` survivors and
retain this eleven-piece profile.

The result is author-checked with two finite algorithms, not independent human
review or proof-kernel verification. Shared premises are the reconstructed E8
geometry, chamber/root-plane arguments, original decoder reduction and the
full120 five-flat capacity proved by the primary complete census. No actual
physical caller, dirty restoration, precision or supplier invoice is constructed.
Such costs are outside this mathematical exclusion, not assumed to be zero.
