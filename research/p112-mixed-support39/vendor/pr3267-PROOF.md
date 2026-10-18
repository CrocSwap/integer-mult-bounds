# Mixed-rank shortening through common support 38

Let K be any characteristic-zero field. On the fixed 112 nonframe E8 root
lines, let C be the root-evaluation code, using doubled roots r_t:

```
C = {(r_t dot h)_t : h in K^8}.
```

Binary support rank is the rank over F2 of the pinned nine-bit labels in a
vector's support. Let pi_S delete ONE common coordinate set S.

**Theorem.** If |S| <= 38, and three residual pieces q_1,q_2,q_3 have binary
support ranks at most 5,5,6, then

```
dim_K(pi_S(C) intersect span_K(q_1,q_2,q_3)) <= 1.
```

The pieces can be dependent and have arbitrary coefficients. Rank constraints
apply only outside S. The theorem is sufficient; sharpness is not claimed.
PR3260 proves support 37 and leaves the 30-root D6 classification branch
open. This proof closes that branch at 38. It supplies no new historical
profile exclusion, full C5, decoder-floor theorem, supplier or kappa.

## Dependencies and exact finite coverage

The source-pinned root-simplex proof and receipt supply global P112 capacities
12 and 20 for binary ranks five and six. Their complete historical flat
censuses are inherited, not rerun here. The standard real Weyl-chamber theorem
and the rational-nullspace transfer below are written dependencies.

The new replay checks the 28 six-node parabolics. Only D6 and E6 have at
least 30 root lines, with counts 30 and 36. All 56 five-node parabolics have
at most 20 root lines. The normal planes of the two qualifying six-node
parabolics contain respectively two orthogonal root lines and an A2 triple.
Thus their Weyl images are covered by orthogonal root pairs and A2 planes.
The source module also checks all 960 simple reflections.

The replay checks all 1,120 A2 planes, their live union spectrum 78/80,
and transitivity under eight simple reflections. Each reflection induces
an invertible linear map of the nine-bit labels. The three representative
27-line projective fibers each span a binary seven-space. Their 2,667
five-spaces have fiber capacity ten. Their 127 hyperplanes have the following
complete full-E8 support / fiber-support counts:

```
(0,0):1, (12,11):27, (12,12):36, (16,15):36, (16,16):27.
```

These joint counts follow PR3262's support-plus-singleton argument; they are
rechecked here. The independent D6 check does not independently re-prove
these A2 premises or the global 12/20 capacities.

## Classify a two-dimensional intersection

Suppose the displayed intersection has dimension at least two. Choose two
independent restricted codewords and lifts c_h,c_k. Their full support union U
lies in S together with the three piece supports. Extend each residual piece
by zero on S. The global capacities give

```
|U| <= |S| + 12 + 12 + 20 <= 82.
```

The lifts are independent, since their restrictions are independent. Therefore
the rational span Z of all full E8 roots perpendicular to h and k has rank
at most six. At least 112-82=30 live roots belong to Z.

Every root in the rational span of Z is also perpendicular to h,k. A generic
real vector perpendicular to Z therefore has exactly those full E8 roots as
its perpendicular root set. Indeed, finitely many additional hyperplanes can
be avoided. Move this real vector into a closed Weyl chamber. Its perpendicular
root system is a parabolic subsystem of rank at most six. The checked counts
force rank six and type D6 or E6. Its two-dimensional normal plane equals the
K-span of h,k, since rational matrix rank is unchanged by characteristic-zero
extension. In particular it has a rational basis.

This argument uses the full perpendicular root system, even though the count
30 comes from live roots. It does not assume any individual piece is a
restricted codeword or any quotient-basis normalization.

## Exclude E6 using joint incidence capacity

In this branch the normal plane is an A2 root plane. Replace h,k by a rational
basis of that plane. Their live support union has at least 78 coordinates.
On the complement of S there is a fixed two-by-three matrix A with

```
(c_h(t), c_k(t))^T = A (q_1(t), q_2(t), q_3(t))^T.
```

At a coordinate in U outside S where exactly one piece q_i is nonzero,
the nonzero evaluation pair is proportional to column i of A. Such singleton
sites for q_i lie in ONE projective fiber. A zero column has no such sites. Besides three large
27-line fibers, the A2 plane has three one-line fibers.

Let M_i be total residual support of piece i and let J_i count its singleton
sites in U outside S.
For i=1,2, the global capacity 12 and fiber capacity ten give M_i+J_i<=22.
For the rank-six piece, M_3+J_3<=32. To see the latter, a one-line fiber gives
the stronger bound 21. For a large fiber in a seven-space W, let V be the
actual binary support span of q_3. If dim(V intersect W)<=5, then J_3<=10
and M_3<=20, giving at most 30. Otherwise V is a six-space contained in W.
The complete hyperplane inventory above gives M_3+J_3<=32. Supports can be
proper subsets of their binary closures; this only lowers these quantities.

Let N=|U minus S|. Each union coordinate has at least one piece incidence;
a nonsingleton has at least two. Thus

```
2N <= sum_i(M_i+J_i) <= 22+22+32 = 76.
2N >= 2*(78-38) = 80.
```

This contradiction permits cancellations, arbitrary columns of A, and piece
support outside U. Extra support only increases M_i. No common shift is
assumed modal.

## Exclude the D6 equality case with the actual puncture

Every D6 normal plane is spanned by two orthogonal E8 roots a,b. The full E8
nonzero evaluation union has 90 lines. Its four projective fibers have sizes
33,33,12,12. The two large fibers are the two coordinate axes. The exact live
union histogram over all 3,780 orthogonal root pairs is

```
82:448, 84:2688, 85:448, 86:168, 88:28.
```

Since |U|<=82, only the 448 minimum planes can occur. Then |U|=82 and |S|=38
are forced. Their residual union has at least 44 coordinates, while the
three pieces have at most 12+12+20=44 incidences in total. Equality follows
throughout. The pieces have disjoint supports of sizes 12,12,20, every support
coordinate lies in U outside S, and every coordinate is a singleton.

Consequently the rank-six piece's entire support of size 20 lies in ONE
projective fiber. A small fiber has only twelve full E8 coordinates. Each
large fiber in a minimum plane has 29 live labels of binary rank eight.
For each of the 448 planes and both large fibers, the primary replay checks
all 10,795 six-spaces in that eight-space via unique two-dimensional dual
spaces. Their maximum live intersection is always 18. A binary space of rank
at most six meets the fiber in a subset of one such six-space. This contradicts
support size 20 and proves the theorem.

The puncture is essential to this finite premise. A full 33-line axis has
six-space capacity 20, with sixteen maximizing supports. A separate checker
enumerates all 788,035 ambient six-spaces, rather than using the primary
fiber coordinates, and reconstructs those sixteen sets. It checks all 120
orthogonal four-root subsets inside the axis. Each support 20 meets each such
four-frame in two or four roots, with multiplicities 1,440 and 480. All 896
actual minimum-plane axis punctures are such four-frames. A separate orbit
check covers all 3,780 orthogonal pairs under the simple reflections.

This alternate check excludes a surviving support 20. It does not by itself
establish the stronger punctured capacity 18 for subsets of smaller full
intersections; the primary complete census supplies that stronger value.

## Credit and limits

Nick Petalas's PR3260 supplies the mixed 5,5,6 question and support 37 proof.
PR3262 supplies the joint A2 support/singleton argument. The source-pinned
root-simplex work, PR3249 and PR3255 supply the capacity and geometry lineage.
DreamingOfClouds/PR3154 supplies the TWOSIDE motivation; the retained E8/P112
lineage includes joaqcoo. Worker1's simultaneous uniform 5,5,5 support 46 audit
identified the same D6 prerequisite and has a distinct equality obligation.
The present theorem uses no unpublished sibling result.

The finite certificate and written characteristic-zero proof do not constitute
proof-kernel or independent human verification. Support39, global sharpness,
a fresh caller, the original C5 reductions, physical/recursive realization,
restoration, the complete consumer bill and multiplication transfer remain
separate obligations. No selected result is changed.
