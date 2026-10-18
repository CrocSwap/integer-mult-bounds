# A six-flat equality obstruction excludes one ten-piece profile

Work over any characteristic-zero field K. The 120 E8 root lines use the
doubled integral representatives of squared norm eight in geometry.py. A
label is `(1,c_1 mod2,...,c_8 mod2)`, where c are simple-root coordinates.
Remove any orthogonal eight-root frame F to obtain P112. Let C be the
eight-dimensional root-evaluation code on its live coordinates.

**Theorem.** Let `a_1,...,a_k,q_0,...,q_3` be collectively independent
vectors on P112. Suppose the union S of the a supports is contained in
the live labels of one binary space U of dimension at most six, together
with at most four additional live coordinates. Suppose each q support
has binary rank at most six. Then their span T has `dim(T intersect C)<=2`.

**Corollary.** The actual TWOSIDE `(b,t)=(6,4)` profile
`2,2,6,6,6,6,6,7,7,7` in DreamingOfClouds/PR3154 is impossible. This is one
scoped profile exclusion, not full C5 or a decoder-floor theorem.

## Source and geometric dependencies

SOURCES.json pins canonical main `463113d675af7410ac91d53a4fed51ec6494eb9a`,
the unchanged geometry source, and PR3154's actual BK/BK7 filters at
`708f0ad8928c383de8294aea3c126e9461d2066d`. The checker reproduces the named
profile's survival of those filters. Its excess is `sum(w-2)=35<36`; deleting
the five largest weights successively meets the original generalized-support
tests. The four smallest weights `2,2,6,6` have support capacity 44<53,
but do not pack into two dimension-six bins and have weight sum 16>7.

The byte-identical original OS-CHARGE2/data.json is retained as
caller-data.json. All 112 original root lines match the fixed live roots.
The invertible binary label map from this package to the original LAB has
columns `1,116,320,90,136,458,350,38,440`. The replay checks every coordinate
and rank nine of that map. Thus the original caller's support-weight
convention is directly bound to the one used by this theorem. The original
root representatives differ only by scaling and coordinate signs. The
corresponding diagonal coordinate change preserves supports, binary ranks
and all code-intersection dimensions.

The retained geometry, following the earlier E8/P112 and joaqcoo decoder
lineage, supplies the following finite facts. The replay checks all 960
simple reflections, all 7,140 root planes, the six-node parabolic maximum 36
and seven-node counts `42,28,22,14,16,23,37,63`. With the standard real
Weyl-chamber theorem these imply minimum nonzero live support 53 and classify
every direction of support strictly below 70 as a scalar root direction.
This standard chamber theorem remains a written dependency.

For a K-valued direction, its perpendicular rational roots span a rational
space of rank at most seven. If its live support is below 70, at least 43
live roots are perpendicular. Rank at most six contradicts the parabolic
maximum 36 by choosing a generic real normal with the same perpendicular
roots. Its rational kernel therefore has dimension one. The real
classification of its generator extends to a K-scalar root direction.
The same rational-kernel argument transfers the minimum-support statement.

These facts hold uniformly after any orthogonal puncture. Full-root
evaluation has Gram matrix 120I, and any doubled-root orthogonal frame
has Gram matrix 8I. Thus every live evaluation has Gram matrix 112I and is
injective. A root direction has full-root support 57. If it belongs to F,
it loses only its own coordinate and has live support 56. Otherwise each
frame pairing is zero or plus/minus four. Parseval gives
`sum_F (r.f)^2=64`, so exactly four frame entries are nonzero and live
support is 53. Nonroot directions have full support at least 78 by the
parabolic calculation, so even eight arbitrary deletions leave at least 70.

The exact root-plane check says a plane containing three root lines is A2,
with coefficient ratio plus or minus one in equal-norm representatives.
Consequently four affinely independent vertices with all edge directions
root lines are a common nonzero K-scalar multiple of an A3 star
`0,h_1,h_2,h_3`, with `h_i.h_i=8`, `h_i.h_j=4` for i!=j. The argument is
the root-simplex normalization used in PR3211, with three directions.
An invertible rational minor transfers the plane relation to K.

Every ordered A3 star is Weyl-equivalent to
`h_j=2(e_0+e_j)`, j=1,2,3. The replay verifies successive extension orbits
of sizes 240,56,27 under reflections perpendicular to the chosen prefix.
These reflections fix that prefix pointwise, so the orbit argument covers
every extension. The full-root labels transform by an invertible binary
linear map under every simple reflection. Explicitly, reflection in simple
root j changes only coordinate c_j by the Cartan pairing modulo two and
fixes the constant coordinate. Thus binary support ranks and the six-flat
contract survive this normalization. The puncture moves to another
orthogonal frame, all of which are checked below.

## The new weighted flat and equality lemma

For a root line r define the four integer values and cost

```
v(r)=(0,r.h_1/4,r.h_2/4,r.h_3/4),
k(r)=4-max_z #{i:v_i(r)=z}.
```

The full-root spectrum is `0:20,1:64,2:36`, totaling 136 incidences.
At a live coordinate outside S, the four q values differ from these four
values by a common shift and nonzero scalar. They therefore have at least
k(r) nonzeros. A cost-one coordinate has a unique group of three equal
values. Achieving cost one forces precisely its exceptional endpoint
nonzero; any other shift has at least three nonzeros.

The two separate finite implementations establish these facts.

1. Every binary six-space contains at most 20 of the full 120 root labels.
   Its total k-cost is at most 36. Exactly 20 six-spaces attain 36; every other
   one has cost at most 32. The census covers all 788,035 six-spaces.
2. Among all 2,025 orthogonal frames, the cost histogram is
   `8:1005,10:960,12:60`. In particular the frame cost is at most 12.
3. For the 20 maximizing flats and all 2,025 frames, union cost is at most 48.
   Exactly 60 pairs attain 48. Nonmaximizing flats give union cost at most 44,
   so none can be an additional equality case.
4. For every equality pair, all 64 cost-one coordinates remain outside its
   union. Partition them by their exceptional endpoint. Each of the four
   sets has 16 labels, has binary rank six, and its entire live-label closure
   outside the frame is exactly that same set of 16.

The primary checker enumerates the RREF annihilator three-spaces in F2^9.
The separate checker enumerates all 97,155 linear five-spaces in F2^8 and
eight affine cosets each, plus the 10,795 six-spaces contained in the even
hyperplane. These are disjoint and exhaustive because a six-space meeting
the odd hyperplane has a five-dimensional even kernel. Separate root and
label reconstruction, frame traversal and binary-span methods agree on
every maximizing flat and equality pair, as well as the histograms.
RESULT.json and INDEPENDENT.json retain the complete equality evidence.

## Equality cannot satisfy the endpoint ranks

Extend U to dimension six if necessary. Let E be the at most four extra
coordinates. The total endpoint support is at least

```
sum_live_outside_S k >= 136-cost(F union Lambda(U))-sum_E k
                       >= 136-48-8 = 80.
```

Each q support is contained in a binary six-space and therefore has at
most 20 coordinates. The total allowance is 80. All inequalities must be
equalities. In particular the flat/frame union is one of the 60 equality
pairs, E consists of four cost-two coordinates, and each cost-one
coordinate uses its unique modal shift. This remains true when S is a
proper subset of the cover: equality also requires the omitted covered
coordinates to have zero additional cost.

Each endpoint must contain its 16 exceptional singleton coordinates. Their
rank is already six, so any rank-at-most-six support containing them has
exactly their binary span. Its live closure has only those 16 coordinates.
Thus every q has support at most 16. This gives total support at most 64,
contradicting the required 80. Extra endpoint entries on S cannot escape
this closure argument. No search over possible endpoint coefficients or
the four extra coordinates is required.

## Quotient normalization and the actual caller

Suppose D=`T intersect C` has dimension at least three. A six-flat has at
most 20 root labels, so `|S|<=24`, and each q has support at most 20. The
images of the k small pieces together with any one q are independent in
T/D: a nonzero relation would give a nonzero codeword supported on at most
44<53 coordinates. Collective independence excludes a zero combination.
Hence `dim(T/D)=k+1` and `dim D=3`.

Modulo the small images, all four q images are nonzero in one dimension.
Rescale them to agree, preserving supports. For small-piece combinations
s_i, the three codewords `c_i=q_i-q_0-s_i`, i=1,2,3, are independent,
by their coefficients on the independent q_i. Injective evaluation gives
three independent directions. Every edge has support at most
`24+20+20=64<70`, so the preceding geometric classification gives the A3
star. The weighted equality obstruction is a contradiction. This proves
the theorem for every characteristic-zero field.

For the original ten-piece profile, collective independence and code
intersection dimension at least six are the TWOSIDE hypotheses. Delete its
three weight-seven pieces. Restricting to the seven remaining basis pieces
loses at most three dimensions of the code intersection, leaving at least
three. Choose the two weight-two pieces and one weight-six piece as the
small pieces. Their support union is inside one six-flat and at most four
extra coordinates: an odd-label rank-two space contains at most two labels.
The remaining four weight-six pieces are exactly the theorem's endpoints.
Its conclusion contradicts the retained code dimension.

The earlier support-only relaxation gives just `136-12-2*24=76<=80`.
Keeping the six-flat improves this to equality 80; the binary endpoint
closure is the additional step that makes it an exclusion. The separately
claimed nine-piece profile `2,6^5,7^3` has a different common-support budget
and is credited as concurrent work, not claimed here.

## Scope and credit

Nick Petalas contributes this weighted A3 six-flat/frame lemma and its
application to `2^2,6^5,7^3`. DreamingOfClouds/PR3154 supplies the original
TWOSIDE formulation and filters. PR3211 supplies the piece-deletion and
root-simplex normalization precedent; PR3217 distinguishes sharp arbitrary
support bounds from the stronger binary-rank contract. Retained E8/P112
geometry attribution is unchanged, including joaqcoo's decoder model.

This is author-checked finite evidence and a written characteristic-zero
argument. Internal automated review, independent human review and formal
proof-kernel verification are separate. Full C5, `C(P112)>=64`, supplier
admission and kappa remain open or unchanged. New work is Apache-2.0 and
used substantial automated assistance. Frozen sources and the selected
frontier are untouched.
