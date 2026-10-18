# A support-shortening lemma for the P112 code

Let K be a field of characteristic zero. Let P be the 112 nonframe E8 root
lines, with doubled representatives r_t of squared norm eight and binary
labels ell(t) in F2^9. Define

```
C = {c_h : c_h(t)=<r_t,h>, h in K^8},
w(q) = rank_F2 {ell(t) : q(t) != 0}.
```

All pieces below are vectors in K^112. A support is a set of live coordinates.
Weights and supports do not change when multiplying a piece by a nonzero scalar.

**Shortening lemma.** Suppose a_1,...,a_k,q_0,...,q_5 are collectively linearly
independent. Let S be the union of the supports of the a_j. If |S|<=29 and
each q_i has support at most twenty, then their span T satisfies
`dim(T intersect C)<=4`.

**Actual-profile corollary.** Ten independent pieces with weights bounded by
`2,5,5,6,6,6,6,6,6,7` cannot have code-intersection dimension at least six.
The last piece's weight is in fact unrestricted in this corollary.

The full A5 spectrum and the deletion method are inherited from Nick
Petalas/PR3188 and PR3195. The new result separates that spectrum from the
weaker coordinate inequality, proves the general support 29 contract, and applies
it at support 26 to this actual TWOSIDE profile. It does not settle full C5,
the complete decoder floor, supplier admission or kappa.

## Finite geometric premises and their scope

The retained geometry reconstructs P, its frame and binary labels from the
E8 simple-root system. It compares all 112 points and labels with the pinned
data file. The live Gram sum is `112 I`, so evaluation h -> c_h is injective.
All 3,309,747 five-flats and 788,035 six-flats are enumerated through their
reduced-echelon annihilators. Their maximum live capacities are twelve and
twenty. A two-flat has at most two odd labels because a nonzero parity
functional takes value one on half its four vectors. Thus weights two, five
and six imply support caps two, twelve and twenty.

Every nonzero codeword has support at least 53. Every nonzero direction with
live support below seventy is an E8 root direction. Here is the retained
Weyl-chamber argument, including the field-extension step. In a real closed
Weyl chamber, the perpendicular roots form the subsystem on the simple nodes
with zero pairing. The replay checks simple-system positivity, all 960 simple
reflections, the maximum 36 root lines on six nodes and the seven-node counts

```
42,28,22,14,16,23,37,63.
```

Live support at most 69 means at least 43 perpendicular root lines. Only the
63-line E7 face qualifies; its normal is a root. The 120 root normals have live
support 53 or 56. This proves the assertions over the reals, using the standard
Weyl-chamber theorem as an explicit mathematical dependency.

For a K-valued direction, the rational perpendicular roots have rank at most
seven. If their rank were at most six, a generic real vector in their rational
annihilator would have exactly the same perpendicular root set. Such a vector
cannot have 43 perpendicular root lines: after moving to a chamber it lies
on a face of at most six zero nodes, whose cap is 36. Thus the perpendicular
roots have rank seven. Their kernel is one rational line, and the K-valued
normal is a scalar multiple of that rational root direction. A hypothetical
nonzero codeword of support below 53 would also qualify and contradict the
root support minimum. The same assertions therefore hold over every K of
characteristic zero. These arguments do not use a real inner product on K.

All 7,140 root planes are checked. A plane on two root lines has either two
root lines or the three lines of A2, whose dependence coefficients have ratios
plus or minus one. This is the retained root-simplex implication. Five
independent directions whose every pairwise difference is also a root
direction have a common scalar after absorbing root signs: in each A2 plane
the two endpoint coefficients have equal magnitude. Their doubled-root Gram
matrix has diagonal eight and off-diagonal four. They give an affine A5 simplex
with the zero vertex. The coefficient argument is valid over K.

## Quotient normalization uses the complete independence hypothesis

Assume for contradiction that D=T intersect C has dimension at least five.
Write Q=T/D. Then `dim Q<=k+1`. The images in Q of all k small pieces and any
one endpoint q_i are independent. Otherwise a nonzero combination of those
original independent pieces would be a nonzero codeword supported on

```
S union supp(q_i), of size at most 29+20=49<53.
```

This contradicts the distance. Consequently `dim Q=k+1`, `dim D=5`, and
every endpoint has nonzero image in the one-dimensional quotient by the
span of the small images. Rescale the q_i so these last images are equal.
Choose s_i in span(a_1,...,a_k) with

```
c_0=0,    c_i=q_i-q_0-s_i in D,    i=1,...,5.
```

These five codewords are independent: their coefficients on q_1,...,q_5 in
the original piece basis form the identity matrix. Injective evaluation gives
five independent directions h_i, with h_0=0. Every nonzero edge has support
at most `|S|+20+20<=69`, so all fifteen edges are root directions. The A2
argument above puts the six vertices into one common scalar multiple of an
affine A5 root simplex.

Outside S, the six q_i values are the six vertex evaluations plus one common
coordinate shift. For a full-root coordinate r, define

```
k(r)=6-max_z #{i in {0,...,5}: <r,h_i>=z}.
```

At least k(r) of the six endpoints are nonzero at that coordinate, regardless
of the common shift. The full 120 A5 spectrum is

```
k=0:4, k=1:36, k=2:60, k=3:20; total cost 216.
```

The orbit replay keeps every extension orbit under reflections perpendicular
to the fixed prefix, with sizes `240,56,27,16,10`. These reflections fix the
prefix pointwise; using this possibly smaller stabilizer cannot omit any
extension orbit. Exactly one A5 star remains. Its Gram matrix and spectrum
are checked. A separate explicit-star calculation and the retained root-class
formula agree. For the star `0,e0+e1,...,e0+e5`, the 56 integer-pair rays give
`0:2,1:24,2:30`. Fixing the first half-root sign positive, if j of the next
five signs are positive, the two multiplicities are j and 6-j; the last
two signs have two parity-compatible choices. Thus the 64 half-root rays
have costs `min(j,6-j)` with multiplicity `2*binomial(5,j)`.

A Weyl normalization may move the eight puncture lines. It still removes
only eight full-root coordinates. Relax them and S to any 37 coordinates.
At most `20*3+17*2=94` cost is removed. The six endpoints must therefore have
at least `216-94=122` support incidences, against their allowance `6*20=120`.
This contradiction proves the lemma. No binary-label transport under the
Weyl normalization is assumed.

At |S|=26 there are at most 34 cuts and the stronger count is

```
216-(20*3+14*2)=128>120.
```

The inherited coordinate inequality gives only `795<=112+8*26+4*120=800`.
It cannot prove this application. At support 25 it still contradicts, since
the upper side is 792; support 26 is the first integer cap beyond its range.
At support 30 the arbitrary-cut A5 count is exactly 120, and the edge cap
is seventy. Both strict arguments fail there. This is a boundary of this
proof, not a counterexample or a claim that 29 is optimal for the code.

## Delete one piece and bind the actual caller

Let T10 be the span of the ten independent pieces in the corollary. Delete
the last piece and let T9 be the remaining span. The quotient T10/T9 has
dimension one, so restriction to T10 intersect C gives

```
dim(T9 intersect C) >= dim(T10 intersect C)-1 >=5.
```

The three small supports have union at most `2+12+12=26`; the other six
pieces each have support at most twenty. The shortening lemma contradicts
this retained code dimension, proving the corollary. Independence is required
before deletion and in the lemma; a displayed list with dependent pieces
does not meet the hypothesis.

DreamingOfClouds/PR3154's unchanged `bk2b.py` and a separate transcription
both retain this profile among the historical 69 `(b,t)=(6,4)` survivors.
Its excess is `35<36`. This binds the historical caller; the 69 are not a
claim about the current unresolved count.

The only four-piece quotient basis certified by weight-only support bounds
has weights `2,5,5,6`, support cap 46<53, and nonbasis weights `6^5,7`.
Enumerating the bin assignments and separately enumerating disjoint subsets
give minimum certified cut allowances 14 for two six-flats and 12 for two
seven-flats. These are upper bounds on cuts supplied by those weight-only
recipes, not lower bounds on actual geometric deletions. They do not certify
the earlier eight-/ten-cut rank-six or two-cut rank-seven rules. The
fourteen-common-cut span-five result leaves five rank-six nonbasis directions,
so alone does not contradict; the twelfth-cut rank-four-anchor route has no
rank-four nonbasis piece. This is a scoped audit of named sufficient routes,
not a claim that no other published argument could apply.

PR3195's `5,5,6^6,7` and PR3197's `4^3,6^6,7` are predecessors and overlap
controls. Their retained small support is 24; the new profile has another
independent weight-two piece and small support 26. Neither the inherited
coordinate inequality nor those earlier dimension statements directly close
this caller. Exact source records are in SOURCES.json. The complete decoder
reduction and all other conjectures remain outside this package.
