# Mixed 5,6,6 shortening at one common cut of 33

Let R be the fixed 112 nonframe E8 root lines, with the pinned leading-one
nine-bit labels. Over a characteristic-zero field K, let
`C = {(r dot h)_r : h in K^8}`. A vector's binary support rank is the F2
rank of the labels of its nonzero coordinates. Let pi_S delete ONE set S.

**Conditional theorem.** For arbitrary residual vectors q1,q2,q3 of binary
support ranks at most 5,6,6 and `|S|<=33`,

```text
dim_K(pi_S(C) intersect span_K(q1,q2,q3)) <= 1.
```

The pieces may be dependent, asymmetric and have arbitrary coefficients.
Their support ranks are constrained only outside S. This improves PR3299's
conditional sufficient32 by one. It makes no sharpness or caller claim.

## Inherited premises and exact sources

The verbatim proofs in vendor/ and SOURCES.json identify their exact commits,
source paths, Git blobs and SHA256 hashes. Retention is not mathematical
admission. The following premises remain inherited.

* PR3299/3295 give the global P112 rank-five/six capacities12/20, the E6
  fiber incidence bounds22/32, and the characteristic-zero parabolic
  normalization argument. Its standard Weyl-chamber theorem is unrun.
* PR3295 gives concentration when a rank-five/six piece has at least10/18
  labels in one full D6 axis. Its full-root support then lies in that axis.
  PR3299's inherited premise4 also supplies rank-five capacity8 in either
  small D6 fiber. Either small full fiber has at most12 roots in total.
* PR3292 proves that an arbitrary ambient binary rank-six space meets a
  D6 axis in at most18 live labels after FOUR orthogonal punctures.
  It also gives the structural decomposition used below.

These mathematical inputs are conditional premises here. Their original
heavy censuses, analytic proofs and full transport suites are not rerun.
The new bounded replay checks the axis-union lemma, the exact bulk-span
property, fixed-frame plane inventory and invertible label transport.

## A small concentration implication used only in the union82 case

For orthogonal root normals a,b, the full 33-root axis F has the form
`F={a} union T`. The bulk T has32 labels and spans a binary seven-space W.
The exceptional label a lies outside W. The actual root intersection of W
is exactly T. These PR3292 structural facts are checked again on the
canonical axis. All7560 ordered orthogonal pairs are in one checked orbit
of invertible linear root-label maps, so the facts transport to every axis.

Suppose an ambient binary space V of dimension at most six contains17 live
axis labels. If V is not contained in W, its intersection with W has
dimension at most five. The inherited P112 capacity12 bounds the live bulk
labels there by12, and the exceptional root adds at most one. Thus V has at
most13 live axis labels, a contradiction. Therefore V is contained in W.
Its full-root closure, and every piece supported in V, lies in F.

Only the implication at17 is used. Concurrent Batch7 work investigates the
sharp universal concentration threshold and its outside-axis equality
witnesses. That is a distinct result and is not presumed here.

## The new full-axis pair-union lemma

For any D6 full axis F and two arbitrary binary support spaces A,B of
dimensions at most five and six,

```text
|(F intersect A) union (F intersect B)| <= 28.
```

This is a finite exact lemma with complete coverage. The full axis spans
eight binary dimensions. Intersect any ambient support space with that
eight-space and extend the result to a five-space or six-space there.
This enlarges its root support, so it suffices to enumerate those spaces.

The primary checker enumerates each reverse-echelon annihilator once:
97,155 five-spaces and10,795 six-spaces. It obtains19,458 and5,336 distinct
root intersections. Every five-space has at most12 roots. Every six-space
has at most16 roots except exactly16 intersections of size20. For the
small cases the union has at most12+16=28. Comparing every five-space
intersection with those16 large intersections gives311,328 unions, all
of size at most28, with equality attained. The checked reflection orbit
transports the finite result to every ordered D6 axis.

The separate checker uses127 bulk hyperplanes and all237,336 five-root
subsets instead of reverse-echelon annihilators. A five-space support of
size at least nine spans dimension five, since a rank-four leading-one
section has at most eight labels. Thus a five-root basis appears in its
enumeration. Its critical large-section maximum is26. The other rank-five
supports have at most eight labels, so their union with20 has size at most28.
This corroborates union28. Complete outside-bulk coverage belongs to the
primary enumeration.

## Normalize a hypothetical two-dimensional intersection

Choose independent restricted codewords in the piece span and lift them to
the full code. Let U be their full live evaluation union, R'=U minus S,
and N=|R'|. Extend each piece by zero on S. The support capacities give

```text
|U| <= 33+12+20+20 = 85.
```

There are at least27 live roots perpendicular to both lifts. Their rational
span has rank at most six, including over K by characteristic-zero rank
invariance. PR3299's generic-real-vector/Weyl argument applies unchanged:
rank-at-most-five parabolics have at most20 root lines, and the only
qualifying rank-six types are D6 and E6. The replay explicitly checks the
new27-zero boundary: other rank-six parabolics have at most21 lines, while
the qualifying counts are30 and36. Thus the normal plane is rational
of one of these types. Replace its basis without changing U.

A fixed two-by-three coefficient matrix expresses the two restricted
codewords in the pieces. A site where only one piece is nonzero belongs
to one projective evaluation fiber for that coefficient column. A zero
column has no singleton sites. These statements allow cancellations,
coefficients outside Q, and support outside U.

For E6, the inherited union lower bound78 and joint incidence bounds give

```text
90 = 2*(78-33) <= 2*N <= 22+32+32 = 86,
```

which is impossible. For D6, the actual live union sizes are82,84,85,86,88.
The budget85 retains exactly82,84,85. The85 case is essential and was not
present in PR3299's budget84 proof.

## D6 union82

Let c=(12,20,20), let M_i count all support of piece i, and let J_i count
its singleton sites in R'. The exact capacity-deficit identity from PR3299
gives `c_i-J_i <= 52-N`. Since N>=82-33=49,

```text
J_1>=9, J_2>=17, J_3>=17.
```

The two small D6 fibers each have at most12 roots. Therefore both rank-six
pieces have their singleton fibers on large axes. The preceding17-label
implication confines their whole supports to those axes. Each axis has29
live roots, obtained from the full33 by FOUR orthogonal frame punctures.
PR3292 bounds either rank-six support by18. Consequently the three pieces
cover at most12+18+18=48 sites, contradicting N>=49. The rank-five piece
need not be confined to an axis.

## D6 unions84 and85

Now N>=51, so the same identity gives J_i>=c_i-1. In particular the
singleton thresholds are at least11,19,19. A rank-five piece has at most8
sites in a small fiber by the inherited small-fiber premise, while a
rank-six piece has at most12 there. All singleton fibers are therefore
large axes, and PR3295's10/18 concentration confines every piece to its axis.

If all pieces use one axis, they cover at most33 sites. Otherwise one axis
has one piece and the other has two. If the rank-five piece is alone, the
coverage is at most12+33=45. If a rank-six piece is alone, the new pair-union
lemma bounds the other rank-five/rank-six pair by28, for total20+28=48.
Thus the coverage is always at most48, below the required51 or52 sites.
This completes the conditional theorem.

## Limits and credit

No sharpness at34, literal caller, full C5, global decoder floor, native
access, frames, restoration, consumer, physical supplier, selected-frontier
change or kappa follows. No human or proof-kernel review is claimed.

Credit Nick Petalas/PR3299, PR3295 and PR3292, their retained
PR3278/3267/3260/3262/3269 and E8/P112/root-simplex lineage, David Arias's
quadratic model, joaqcoo, and DreamingOfClouds/PR3154. The related5/5/6
sharpness witness belongs to PR3286. Concurrent concentration work is
separate from this common-cut theorem. Apache-2.0.
