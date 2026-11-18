# All irreducible seven-image pools at pattern dimension five

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.

## 1. Classification

Work over F2 in a fixed coordinate space. Let H be a five-dimensional
off-diagonal pattern space that contains no matrix unit. Its complete pool
consists of all rank-one idempotents with nonzero pattern in H. Suppose
that its joint image V has dimension seven and the pool acts irreducibly
on V.

**Theorem.** After a coordinate permutation, the complete pool consists of
two normal-form triples on coordinates 0..2 and 3..5, together with exactly
one link:

```text
First block:  image/covector pairs (6,5), (5,6), (7,7).
Second block: the same pairs shifted by three coordinates.
h = e_2 + e_5.
Link = (h+a)(h+b)^T,
    a,b supported outside the two blocks,   a dot b = 1.
```

The integers encode binary coordinate supports. Every such family has a
complete unit-free pattern space of dimension five and irreducible image
dimension seven. Thus the displayed form is necessary and sufficient at
every ambient width. In particular, **every attaining irreducible complete
pool has exactly seven projectors**. No larger pool supplies another
attaining geometry.

All these actions on V are isomorphic: in a suitable basis they consist of
the first six coordinate projectors and the all-one seven-by-seven matrix.
The parameterization permits arbitrary fresh supports a,b with pairing one.
It is not a count of coordinate-permutation orbits or a unique orbit
representative.

This answers question 2 of
[PR #7281](https://github.com/CrocSwap/integer-mult-bounds/pull/7281),
[exact source](https://github.com/unpaidmoon/integer-mult-bounds/blob/0cd5324c41490b856d0e94daa8b011683fc153f6/research/no-edge-dim5-fresh-link/PROOF.md).
The two-block construction and its links are prior work. The new step
forces that geometry for an arbitrary complete pool, without assuming an
irreducible image-basis subcollection.

## 2. Two possible image-basis structures

Choose any seven pool projectors with independent images. The total-image
and disjoint-circuit theorem in
[PR #7690](https://github.com/CrocSwap/integer-mult-bounds/pull/7690),
[exact proof](https://github.com/aliromman/integer-mult-bounds/blob/b725be51349cce4e0a262c76233838992042dd62/research/no-edge-total-image-bound/PROOF.md),
gives pattern rank at least `ceil(14/3)=5`. Thus these seven projectors span
H, and their space of diagonal relations has dimension two. Its two circuit
supports are disjoint, and each has at least three members. The possibilities
are a triple and a quad, or two triples and one member in no relation.

For each relation group, let U_j be its image span and S_j the coordinate
support of its diagonal sum. The source theorem proves that the S_j are
disjoint, every group covector is supported on S_j, and the coordinate space
on S_j lies in U_j. Also

```text
1 <= |S_j| <= dim U_j,
|S_j| = dim U_j modulo 2.
```

The U_j have zero intersection because the selected images are independent.
These statements concern the chosen basis. The remainder of the proof
checks every projector in the complete pool.

## 3. A column-support invariant

Suppose a pattern space has zero columns outside a coordinate set S. Let V
be the joint image of any collection of its rank-one idempotent lifts.
Then

```text
K = {v in V : v is zero on S}
```

is invariant under the whole collection. To see this, a projector whose
covector is supported on S kills K. If its covector has an outside bit j,
the zero off-diagonal column j forces its image to be e_j. This image lies
in V and is zero on S, so the projector maps K into K again.

If V contains the coordinate space on S and `0<|S|<dim V`, K is a proper
nonzero invariant subspace. This argument allows extra pool members with
outside covector bits; it does not assume that every covector stays on S.

## 4. A triple and a quad cannot be irreducible

In this case all seven selected projectors lie in the two relation groups.
Their patterns span H, so every pattern has zero columns outside
`S=S_1 union S_2`. This coordinate space lies in V.

If `|S|<7`, Section 3 gives a proper invariant subspace. If `|S|=7`, each
group's active-set size equals its image dimension. Its image space is
therefore that coordinate block. Both its factors are supported on the
block, and H is block diagonal on disjoint blocks of sizes three and four.
A rank-one idempotent lift with nonzero pattern cannot cross those blocks:
idempotence gives a coordinate at which both factors are one, and the
forbidden cross entries force both factors into its block. Each block is
then invariant under the complete pool. The action is reducible in both
cases.

Consequently every chosen seven-image basis has two relation triples and
one further projector L. Let H0 be the four-dimensional pattern space of
the six triple members. Then `H=H0+span(off(L))`.

## 5. A column triple cannot occur

A relation triple has active rank one or three. At rank one, its covectors
all equal e_c, its images are `e_c+t_i`, and the three t_i are the nonzero
vectors of a two-dimensional space T with no weight-one vector. At rank
three, both factors lie in its coordinate three-space and form dual bases.
These are the column and orthogonal triple cases of the source support
argument.

Let S be the union of the two active supports. If either triple is a column
triple, then `|S|<=4`. Every pattern in H0 has zero columns outside S.
Moreover **every lift of a nonzero H0 pattern has its covector supported
on S**. If a covector had an outside bit j, the zero off-column would force
image e_j and a pattern consisting of one row outside S. The columns of
an orthogonal triple are supported inside its active block, so they give
zero on that row. At a column-triple coordinate c, the column would have
to be zero or e_j, and T contains no weight-one vector. The entire pattern
would be zero, which is excluded.

All patterns in the other coset `off(L)+H0` have identical columns outside
S. If these columns are all zero, the full space H has zero columns
outside S, and Section 3 proves reducibility. Assume that at least one
outside column is nonzero.

If exactly one outside column j is nonzero, any odd-coset lift has y_j=1.
That column pins every image bit except x_j, so at most two different
images occur among all odd-coset projectors. If at least two outside
columns are nonzero, they pin each other's missing diagonal bits. There
is at most one image.

For each fixed image x, every covector bit outside S is determined by those
fixed columns. If `x!=e_j`, some image bit off j is one, and the corresponding
column entry determines y_j. If `x=e_j`, idempotence forces y_j=1. Thus
the restrictions of the odd covectors to the outside coordinates have at
most two possible values. Their span has dimension at most two.

The even covectors are supported on S. The span of all complete-pool
covectors has dimension at most `|S|+2<=6`. On a seven-dimensional image
they therefore have a nonzero common kernel. It is proper and invariant,
contrary to irreducibility. This excludes every column-triple case, including
cases with more than seven complete-pool projectors or overlapping row
supports.

Both relation triples must have active rank three. The two active
three-coordinate blocks are disjoint.

## 6. The two blocks have the normal form

The normal-form lemma in unpaidmoon's
[PR #6921](https://github.com/CrocSwap/integer-mult-bounds/pull/6921),
[exact proof](https://github.com/unpaidmoon/integer-mult-bounds/blob/6020400853abc110134804fad04b695adc360bcd/research/no-edge-irreducible-image/PROOF.md),
classifies an orthogonal rank-one triple on three coordinates whose pattern
space contains no matrix unit. It is the normal triple of Section 1, up to
coordinate permutation.

The verifier repeats the complete finite step: all 168 ordered bases of
F2^3 and their dual covectors. Exactly 18 bases survive, in three unordered
coordinate versions. Their image weights are two, two and three; the two
weight-two vectors are dual to each other and the weight-three vector is
self-dual. This proves the stated normal form. Unlike the total-image proof
in PR #7690, this classification uses that finite three-coordinate lemma.

Let C be the six-coordinate core. Write the remaining link as
`L=(u+a)(v+b)^T`, with u,v on C and a,b outside C. Independence of its image
from the six old images gives `a!=0`. If b were zero, every pattern in H
would have zero columns outside C. Section 3 would make the fresh image
line `V intersect {vectors zero on C}` invariant. Thus `b!=0` as well.

## 7. Complete fresh-factor classification

The remaining statement is the fixed-block theorem from
[PR #7676](https://github.com/CrocSwap/integer-mult-bounds/pull/7676),
[exact proof](https://github.com/aliromman/integer-mult-bounds/blob/943c355c233649f77f018e6247e5456584ef715e/research/two-block-fresh-link-classification/PROOF.md).
Its argument is repeated here to show where completeness enters.

The complete pool of H0 is exactly the six normal-block projectors. Every
nonzero pattern is confined to one of the blocks, and its three nonzero
patterns have the unique lifts `(6,5),(5,6),(7,7)`.

If v is zero, the fresh-row/core-column rectangle is zero in every pattern
of H. Each pool projector therefore either has its image in C or kills C.
The core C is a proper invariant subspace. If u is zero and v is nonzero,
the nonzero rectangle `a v^T` forces every odd-coset lift to have fresh
image a and core covector v. The opposite rectangle is zero, so that lift
either has image exactly a or has zero fresh covector and kills a. The old
projectors also kill a. The line spanned by a is invariant. These arguments
include every possible extra coset lift.

Now u and v are both nonzero. The two cross rectangles `a v^T` and `u b^T`
are nonzero and unchanged across the odd coset. A nonzero binary rank-one
rectangle has unique nonzero factors. The two rectangles therefore fix
u,v,a,b for every odd lift. L is the only odd-coset projector, so the
complete pool has seven members.

Let the old pairs be `(u_i,v_i)`. They are dual bases of C. Irreducibility
forces both `v_i dot (u+a)=1` and `(v+b) dot u_i=1` for each i. If the
second pairing were zero, the old image line would be invariant. If the
first were zero, the span of the link image and the other five old images
would be an invariant hyperplane. The twelve equations force u and v to
be the sums of the old image and covector bases. Both sums equal
`h=e_2+e_5`. Since `h dot h=0`, idempotence gives `a dot b=1`.

Conversely, these pairings give irreducibility. Any nonzero invariant
subspace hit by a pool covector contains a projector image. The link sends
every old image to its image, and the old projectors send the link image
to every old image. Such a subspace is all of V. The common covector kernel
is zero: the old covectors force the core part to vanish, and the link
covector pairs to one with a.

The two hub entries in any fresh row where a is one remain present in
every odd pattern, so no odd pattern is a matrix unit. The old patterns
have weight at least three. The fresh cross rectangle gives pattern
dimension five. The images have dimension seven, and the preceding
rectangle argument proves completeness. In the basis of the six old images
followed by a, the old projectors are the first six coordinate projectors
and the link has image and covector both equal to the all-one vector.
This proves the classification and the action-isomorphism statement.

## 8. Exact checks and limits

The verifier enumerates every rank-one idempotent at widths seven and eight:
8128 and 32640 matrices. It checks three distinct link domains: a normal
triple plus a column triple at width seven, two column triples at width
eight, and two normal triples at width seven with zero fresh covector.
Each candidate has image outside the old six-dimensional image. Zero
patterns and spaces containing a matrix unit are excluded as specified.

Across these domains there are 30679 candidate links and 30376 distinct
unit-free spaces, where distinctness is measured within each domain. Every
complete pool is obtained in two ways: a raw index over all idempotents and
a separate four-trial lift of each literal pattern. The pools agree. Every
excluded space has a checked invariant coordinate kernel or a nonzero
common covector kernel. The largest complete pools have ten members; the
check does not truncate them to a proposed basis.

Four triple-plus-quad controls cover active quad ranks two and four and
both triple types. Their complete pools have seven or eight members and
pass direct invariant-subspace and orbit checks. Six prior positive links
at widths seven through ten have exactly seven pool members and all 127
nonzero vector orbits span the image. The known extra-pool example generated
by link `(64,69)` includes `(70,5)` as an eighth member, and its fresh line
is checked against all eight projectors.

These finite scans cover the named coordinate geometries and every candidate
link in those domains. They do not enumerate all ambient embeddings. The
written support argument supplies the all-width reduction. The full prior
nonzero-fresh fixed-block census was not rerun; its proof is reused and the
listed positive and extra-pool controls are rechecked.

No paid BIT word, native operation, complete invoice, selected-assumption
discharge or new kappa is supplied. The selected frontier and all five
assumptions remain unchanged. Independent human and formal-kernel review
are unclaimed.

## Open next questions

Can the classified seven-projector action occur in a legal paid BIT word
with a valid relation, cube-span and coordinate-call reduction? The geometry
now has a complete description, but the word-level reduction and full
producer/consumer invoice are not supplied. Repeating a link search within
these two blocks does not address that missing interface.
