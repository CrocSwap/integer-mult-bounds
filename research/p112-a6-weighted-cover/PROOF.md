# The P112 `3,4,6^8` profile is impossible

## Statement

Use the pinned 112 live E8 root lines `r_t` and their nine-bit labels `ell(t)`.
For any characteristic-zero field `K`, define

```
C = {c_h : c_h(t)=<r_t,h>, h in K^8},
w(q) = rank_F2 {ell(t) : q(t) != 0}.
```

There do not exist ten independent pieces spanning `T`, with
`dim(T intersect C)>=6`, whose respective weight upper bounds are

```
3,4,6,6,6,6,6,6,6,6.
```

This is one actual TWOSIDE `(b,t)=(6,4)` profile from DreamingOfClouds's
PR3154 at `708f0ad8928c383de8294aea3c126e9461d2066d`. It is not the whole
cell, C5, the P112 decoder floor or a supplier theorem.

## Retained geometry and exact coverage

The source-bound [root-simplex proof](vendor/ROOT-SIMPLEX-PROOF.md) and
Nick Petalas's PR3176 supply these geometric arguments:

- Weight-three and weight-four supports have at most four and eight lines.
  Every label has leading bit one, so a binary `d`-flat contains at most
  `2^(d-1)` labels. A weight-six support has at most twenty live lines.
  The replay enumerates all 788,035 three-dimensional annihilators in
  `F2^9` to check this last bound.
- `h -> c_h` is injective and every nonzero codeword has at least 53 live
  coordinates.
- A real subspace of dimension at most six contains at most 36 E8 root lines.
  The eight seven-node chamber faces contain respectively
  `42,28,22,14,16,23,37,63` root lines. The 42-line face has a D7 normal;
  the 63-line face has a root normal.
- Independent scalar-root directions whose pair differences are scalar
  roots have one common scale and orientations making a root star, with
  squared norm two and distinct inner products one.

The standard Weyl-chamber theorem remains an explicit dependency, not a
formalized consequence of a finite test. The replay checks simple-system
positivity, 960 simple reflections and all 7,140 root planes. It reconstructs
root and label bytes independently of the predecessor's binary data tables,
then checks their equality to the declared input.

A nonzero direction with support at most 72 has at least forty perpendicular
live roots. Their rational span cannot have rank at most six by the 36-line
bound. It therefore has rank seven and a one-dimensional rational kernel.
This also proves that a field-valued direction is a scalar multiple of a
rational vector, over any `K` of characteristic zero. The chamber-face counts
leave only a root direction or a Weyl transform of the D7 normal.

The retained program constructs a reflection-closed inventory of 1,080 D7
normal lines containing that chamber normal. Their live support histogram is
`70:128, 73:896, 76:56`. Thus the complete support-72 alphabet is contained in
120 root lines plus 128 eligible non-root lines. Those 128 normals have one
entry `+1` or `-1` in each coordinate pair, up to common sign. Explicit even
signed permutations preserving the deleted frame normalize each to
`a=(1,0,1,0,1,0,1,0)`. All 128 normalizations are checked.

## Seven affine endpoints

Choose small pieces of weights `3,4,6`, with support union `S` of size at most
`4+8+20=32`. Call the seven remaining weight-six pieces `q_0,...,q_6`.
Let `D=T intersect C`. The quotient `T/D` has dimension at most four.

The small pieces and any one `q_i` have support union at most `32+20=52<53`.
Their quotient images are independent: a dependence would be a nonzero
codeword supported on fewer than 53 lines, since the original pieces are
independent. The quotient therefore has dimension exactly four. Modulo the
three small images, the seven remaining images are nonzero in a
one-dimensional quotient. Rescale the `q_i` to give them equal images there.
Subtract suitable small-piece combinations `s_i` and write

```
c_0=0,    c_i=q_i-q_0-s_i in D,    i=1,...,6.
```

The six codewords are independent by their distinct coefficients on
`q_1,...,q_6`. They give seven affinely independent vertices in `K^8`.
Every edge is supported on at most `32+20+20=72` lines, so its direction is
in the complete root/D7 alphabet.

At any coordinate outside `S`, the endpoint evaluations differ from the
vertex evaluations by one common shift. For seven scalar values, every
common shift leaves at least

```
7 - maximum equality multiplicity
```

nonzero entries. Cancelling a largest equality class attains this minimum.
The seven endpoints permit at most `7*20=140` support incidences. Both
branches below require more.

## Mixed root/D7 branch

Translate and rescale a non-root edge to the segment `0,a`. Any other vertex
`x` has `x=s*u`, `a-x=t*v` for distinct allowed rays `u,v` and nonzero
coefficients. Solving `a=s*u+t*v` gives exactly 58 possible vertices.
The solution is rational even when initially sought over `K`, by an
invertible rational two-by-two coordinate minor. The compatibility graph
has 595 edges, testing whether each difference is an allowed ray.

Five further vertices form a five-clique. The complete exact census gives

| Rank with the anchor | Five-cliques |
|---|---:|
| 4 | 630 |
| 5 | 3,360 |
| 6 | 3,360 |

Only rank six is admissible. For each of these 3,360 cases, sum the minimum
nonzero costs after removing the 32 largest live costs. This relaxes the
actual `S` and allows arbitrary coordinate shifts. The surviving-cost
histogram is

```
142:1344, 145:336, 146:336, 147:112, 148:448, 149:560, 150:224.
```

Thus the mixed branch requires at least 142 incidences. A separate program
uses Gram intersections, a two-plus-three clique join, fraction-free integer
elimination and frequency-based deletion. It obtains the same graph, ranks
and costs, without calling those primary algorithms.

## Root-only A6 branch and its losing relaxation

The root-plane lemma identifies the vertices with one scaled affine root
A6 simplex. Extend each star prefix by every root having the prescribed
inner products. Reflections perpendicular to the prefix fix it pointwise.
Retaining every orbit of this subgroup is complete, even if the subgroup
is smaller than the full stabilizer. The extension orbit sizes are
`240;56;27;16;10;6`, leaving one rank-six star.

Evaluate its seven vertices on all 120 root lines. The minimum nonzero-cost
spectrum is

```
0:1, 1:21, 2:63, 3:35,    total cost 252.
```

Arbitrary removal of eight frame lines and 32 small-support lines leaves
only 137, below the allowance 140. This is a losing control. A proof cannot
replace the small supports by forty arbitrary deletions.

A Weyl transformation taking the star to its representative moves the
puncture to an orthogonal eight-line frame. It maps binary label flats to
flats of the same dimension. Indeed, a root reflection is an invertible
integral automorphism of the simple-root lattice; reduce its coordinates
modulo two and leave the leading one fixed. Canonical root signs do not
matter modulo two. The replay checks all 960 simple-reflection label
relations. We must retain the actual rank-six and rank-four support flats.

## New weighted cover lemma

Let `c` be the full120 A6 cost function above. For any orthogonal eight-line
frame `F`, binary six-flat `V`, binary four-flat `U`, and set `A` of at most
four root coordinates,

```
sum_{r outside F union Lambda(V) union Lambda(U) union A} c(r) >= 141.
```

This relaxes the weight-three support to four arbitrary coordinates. The
following finite argument proves the lemma.

All 2,025 orthogonal frames are enumerated. Their cost histogram is
`14:210,16:735,17:630,19:420,21:30`, so a frame costs at most 21.
A four-flat contains at most eight odd labels, costing at most 24; `A` costs
at most twelve. Suppose the union removed cost at least 112. Then `V` must
have full cost at least `112-21-24-12=55`.

The complete six-flat enumeration has maximum cost 60. Exactly 63 distinct
masks have cost at least 55: 35 cost 57, and 28 cost 60. For every one of
these masks and every frame, the prefix `B=F union Lambda(V)` has cost at
most 77. A prefix costing at most 75 is impossible, since adding `U` and
`A` removes at most another 36. The remaining prefixes are exactly

```
B cost 76: 4,620 pairs;    B cost 77: 2,520 pairs.
```

For these prefixes, `U` outside `B` would need cost at least
`112-c(B)-12`, hence 24 or 23. A four-flat containing at most six cost-three
labels has cost at most `6*3+2*2=22`. Any relevant four-flat must therefore
contain at least seven of the 35 cost-three labels. Those seven labels span
four dimensions: a three-flat contains at most four odd labels. Four of
them are a basis, so enumerating all four-element subsets of the 35 labels
covers every possible relevant four-flat.

This construction gives exactly 135 masks: thirty contain seven cost-three
labels and 105 contain eight. Every one is checked against every relevant
prefix, a total of 963,900 tests. Their maximum residual cost is twelve for
both prefix costs, strictly below the necessary 23 or 24. All other
four-flats cost at most 22 even before subtracting `B`. Thus no removed
cost reaches 112. Integrality gives removed cost at most 111 and surviving
cost at least `252-111=141`.

The separate checker enumerates all 788,035 six-flats and all 3,309,747
four-flats using forward-echelon annihilators, instead of the primary
reverse-echelon/high-label construction. It recovers the exact same 63
and 135 masks and the complete six-flat weight histogram. Its frames are
the 2,025-element simple-reflection orbit of the fixed frame, not the
primary orthogonality-clique traversal. It checks every relevant pair and
reproduces both residual maxima. The shared root reconstruction and
Weyl-chamber dependency remain explicit.

## Finish, overlap and limits

The actual root-only supports lie inside the sets of the weighted lemma,
so at least 141 endpoint incidences remain outside the small support. The
mixed branch requires 142. Both exceed 140. This proves the statement over
all characteristic-zero fields.

The original unmodified TWOSIDE program and a separate transcription
retain this profile among the original 69 `(6,4)` survivors. Every
weight-certified four-piece quotient basis has weights `3,4,6,6`. Its
best two-six-flat packing leaves twelve certified cuts and six rank-six
nonbasis pieces. PR3162's ten-cut theorem and PR3167's twelve-cut theorem
with a rank-four nonbasis anchor do not supply this exclusion by that
route. This is an applicability check, not a universal novelty proof.

The first session candidate `2,4,6^8` was discarded as already covered by
PR3162 through basis `2,4,6,6`. The present result changes that candidate
and repairs two losing relaxations: forty arbitrary cuts give 137; retaining
only the frame and six-flat but allowing twelve arbitrary small coordinates
gives 139. Neither alone proves the exclusion.

This is an author-checked mathematical exclusion with separately implemented
finite checks, not independent human or proof-kernel review. The standard
Weyl-chamber theorem, inherited root-plane argument and original decoder
reduction remain dependencies. Full C5, other profiles, `C(P112)>=64`,
physical realization and any improved multiplication exponent remain open
or unchanged. No physical costs are assumed to be zero.
