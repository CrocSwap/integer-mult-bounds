# The five-dimensional two-edge core at three pattern dimensions

Prepared for **@CubeJerry** with substantial OpenAI assistance. New work is
Apache-2.0. This is a scoped written proof, with finite corroboration. It does
not settle the three-relation paid-rank question or improve kappa.

## 1. Exact statement

Work over F2. For an r-dimensional space P of zero-diagonal W-by-W matrices,
let C(P) be **all** noncoordinate rank-one idempotents N=xy^T with
`off(N) in P`. Thus x,y are nonzero, y^T x=1, and off(N)!=0. Let e(P) count
the matrix units E_ab (a!=b) in P. Let V be the joint image of C(P).

**Theorem (three-dimensional spaces containing two edges).** Suppose r=3.

1. If e(P)=2, let E be the coordinate span of the endpoints of those two
   directed edges. Then `dim V <= dim E + 1 <= 5`. If the edges share an
   endpoint, the bound is at most four.
2. If e(P)=2, dim V=5, and the restrictions of the complete pool C(P) to V
   act irreducibly, the edges have disjoint endpoints. There is a binary
   basis of V in which the **set of restricted projectors** is exactly
   `{E11,E22,E33,E44,J5}`, where J5 is the five-by-five all-ones matrix.
   This normal form is irreducible.
3. If e(P)=3, the pool is a direct sum over the connected components of
   the undirected graph of the three edges. Each nontrivial component
   uses at most four coordinates. In particular, every irreducible
   constituent has dimension at most four, although the total joint
   image can have dimension six.

Both the bound five in part 1 and the irreducible exception in part 2
are attained. Therefore a reduction of all rank-three noncoordinate
pattern pools to irreducible scalar cores of dimension at most four is
false. The theorem does **not** assert that a rank-saving diagonal word
exists on the five-dimensional exception.

There cannot be more than three matrix units in P: distinct matrix units
are linearly independent. The general corollary in Section 3 also bounds the one-edge case by five.
The irreducible classification is specific to two edges; the zero-edge
case and the one-edge irreducible classification remain outside it.

## 2. Inherited fiber lemma and a new quotient observation

We use Nick Petalas's #5921 fiber lemma: a realized nonzero binary pattern
has one rank-one-idempotent lift, except E_ab, whose two lifts are
`e_a(e_a+e_b)^T` and `(e_a+e_b)e_b^T`. The proof follows by subtracting two
lifts: their diagonal difference has rank at most two and even trace, so
is supported on two coordinates; the resulting binary 2-by-2 list gives
the stated pair. This lemma and its credit are inherited.

**Quotient observation.** Let U be a coordinate subspace, and let N=xy^T
and M=uv^T be noncoordinate binary rank-one idempotents such that
`off(N)+off(M)` is supported within the U-by-U block. If x and u have
linearly independent images modulo U, then N and M have the same
single-edge pattern, and both endpoints of this edge lie outside U.

Indeed, the outside-U rows and inside-U columns give
`(x mod U)(y|U)^T=(u mod U)(v|U)^T`. Independence forces y|U=v|U=0.
Consequently the entire inside-U block vanishes in both matrices, so
their full off-diagonal patterns are equal. The projectors differ, since
their image classes are independent. The fiber lemma makes that common
pattern a single edge. In its two lifts both covectors vanish on U only
when both endpoints lie outside U. This proves the observation.

Also, a noncoordinate rank-one idempotent with its entire off-diagonal
pattern supported inside U has its image in U. Otherwise choose an
outside coordinate i with x_i=1. Its off-diagonal row forces y=e_i; the
remaining outside-block entries then force x=e_i, making the projector
coordinate, a contradiction.

## 3. Sharp joint-image bound

Assume e(P)=2. Let p,q be the two edge patterns, let P0=span(p,q), and let
E be their endpoint space. Every pool projector whose pattern belongs
to P0 has image in E by the preceding observation. Moreover the two lifts
of each edge belong to the **complete** pool and their images span its
two endpoints. Thus E is contained in V.

There is just one nonzero coset P/P0. For any two projectors with patterns
in that coset, their off-diagonal difference is supported inside E.
If their image classes modulo E were independent, the quotient observation
would produce a third single-edge pattern in P, with endpoints outside E.
This contradicts e(P)=2. Hence their image classes are pairwise dependent.
Over F2 all nonzero such classes are equal; their span has dimension at
most one. Therefore V/E has dimension at most one. This proves part 1
at every ambient width, without a word-length or address-rank assumption.

**General edge-quotient bound.** More generally, let P have dimension r,
let e=e(P), and let E be the coordinate span of the endpoints of
**all** e edge patterns.
Let P0 be their span, of dimension e. The same proof gives

    dim V <= dim E + 2^(r-e) - 1.

The zero coset contributes only images inside E, while each of the
2^(r-e)-1 nonzero cosets contributes at most one quotient-image dimension.
Otherwise the quotient observation would produce an additional edge with
endpoints outside E, contrary to its definition. This also holds at e=0
with E=0. For r=3 and e=1 it gives dim V<=5. For e=0 it gives only the
seven-projector bound; no five-dimensional reduction is asserted there.
This resolves an edge-containing slice of #5921's explicit open question
about sharp joint-image dimension, whose general cardinality estimate
gives the coarser bound 2^r+r-1 (ten at r=3). The e=2 normal form is the
new sharp irreducible case.

Since dim E<=2e and the function 2e+2^(r-e)-1 is convex in e, its
maximum on 0<=e<=r occurs at an endpoint. Consequently every complete
noncoordinate pool satisfies

    dim V <= max(2^r-1, 2r).

In particular, all three-dimensional pattern pools have joint image at
most seven. This is an upper bound, not an attainment claim. The precise
r=3 conclusions supplied here are:

| Number e of edge patterns | Joint-image bound | Additional conclusion |
| --- | ---: | --- |
| 0 | 7 | No sharpness or irreducible classification proved |
| 1 | 5 | No sharpness or irreducible classification proved |
| 2 | 5 | Irreducibly sharp; unique five-dimensional restriction |
| 3 | 6 | Coordinate components have dimension at most four |

## 4. The unique irreducible five-dimensional restriction

Suppose dim V=5 and the restricted pool is irreducible. Part 1 makes
E four-dimensional, so the edges are disjoint. Order their endpoints
as (1,2),(3,4), with edge patterns E12 and E34. Choose w in V supported
outside E, so `V=E direct-sum F2*w`.

The two lifts of each edge restrict to their usual two-by-two block and
annihilate w. Conjugating by
`S=(I+E12)(I+E34)` makes those four lifts E11,E22,E33,E44. This change of
basis acts only on E.

The sum E12+E34 is unrealizable: its entries (1,2) and (3,4)
would force the unwanted cross entry (1,4) in a rank-one matrix. Thus
the four edge lifts exhaust the nonzero realized patterns in P0.
All remaining projectors have patterns in the single coset P/P0. Before
or after this shear, the E-to-w and w-to-E blocks of their restrictions
are identical: their differences have zero off-block entries in the
original coordinates. More explicitly, a difference has its off-diagonal
support inside E; on E its outside component is zero, and on w its E
component is zero because w has no E coordinates. Both projectors
preserve V, so the remaining outside component is a scalar multiple of w.

Write the common off-block column and row as a and b^T. If a=0, the line
F2*w is invariant under every restricted projector. If b=0, E is
invariant. Irreducibility therefore makes both a and b nonzero.

Write any remaining rank-one restriction as
`(alpha,epsilon)(beta^T,eta)` in the basis E,w. Its off-blocks give
`alpha*eta=a` and `epsilon*beta=b`. Over F2, nonzero a,b force
`epsilon=eta=1`, alpha=a and beta=b. Thus there is **one** remaining
restricted projector, namely `(a,1)(b^T,1)`.

With the four coordinate projectors present, irreducibility forces all
four entries of a and b to be one. If a_i=0, the hyperplane with coordinate
i zero is invariant; if b_i=0, the line F2*e_i is invariant. Conversely,
when a=b=(1,1,1,1), the remaining projector is J5 and the family is
irreducible: for a nonzero invariant subspace U, either some vector has
one of its first four coordinates nonzero, so Eii puts e_i in U and J5
puts the all-ones vector in U; or U initially contains e5, and J5 again
puts the all-ones vector in U. Applying E11,...,E44 then gives e1,...,e4,
and adding them to the all-ones vector gives e5. Thus U=F2^5.

This proves both uniqueness and irreducibility of the normal form.
It is an assertion about the set of restrictions; different original
projectors need not be distinguished if their restrictions coincide.

## 5. Explicit sharp pool

Use five coordinates numbered 0 through 4. An integer mask lists the
support of a binary vector, with bit i representing coordinate i. Take

| Projector | x mask | y mask |
| --- | ---: | ---: |
| P | 1 | 3 |
| Q | 3 | 2 |
| R | 4 | 12 |
| T | 12 | 8 |
| B | 26 | 21 |

Here B=(e1+e3+e4)(e0+e2+e4)^T. Each y^T x is one. Let
`P*=span(E01,E23,off(B))`. These three patterns are independent and the
only matrix units in P* are E01 and E23. The complete noncoordinate
pool C(P*) is exactly the five projectors in the table.

For the last completeness assertion, the outside coordinate 4 has
B_44=1. Every pattern in off(B)+span(E01,E23) has the same nonzero
row-4 and column-4 off-diagonal entries. Any rank-one idempotent lift
therefore has x4=y4=1, fixing all other x and y entries and hence fixing
B itself. Among span(E01,E23), only the individual edges are realized:
their sum has two disjoint edges and cannot be a rank-one off-diagonal
pattern. Its four lifts are P,Q,R,T.

The shear S=(I+E01)(I+E23), with S^-1=S, sends these five projectors to
E00,E11,E22,E33,J5. Section 4 proves irreducibility without enumeration.
The verifier independently checks all 496 binary rank-one idempotents
at width five, all 372 nonzero proper subspaces, and the conjugation.
This is a counterexample to a four-dimensional **pool** compression,
not to the two-relation rank theorem or to any paid-rank inequality.

## 6. The three-edge case

If e(P)=3, those three matrix units form a basis of P. Every realized
pattern is supported on their graph. The undirected support graph of a
noncoordinate rank-one idempotent is connected on its nonzero rows and
columns: the supports of x and y meet (their dot product is one), and
a common support coordinate connects all the others. Its support is
therefore contained in one connected component of the three-edge graph.
There are no extra isolated diagonal coordinates in a noncoordinate
rank-one lift. Thus every projector is supported in one component.
A connected component with at most three distinct edges has at most four
vertices. This proves part 3. Three disjoint edges attain total image
dimension six, showing why part 3 must discuss components instead of
claiming a total image bound five.

## 7. Exact word relevance and its limits

In the binary scalar-idempotent word model, let L be the saturated
integral lattice of exponent relations, with rank three. The first-order
augmentation argument from #720/#6777 puts the span of off-diagonal
coefficient vectors inside L/2L. Thus the occurring pattern span has
dimension at most three. The new theorem concerns the **dimension-three**
case whose complete pattern space contains at least two single edges.
It does not cover smaller pattern dimensions with three relations.
The one-edge case has the general joint-image bound five, but no unique
irreducible normal form is proved here. The zero-edge case has only the
general bound seven.

Coordinate calls cannot simply be discarded. Here is a sufficient exact
split, which also explains the relevance of the complete pool. Let L0 be
the saturated rational span of all cube relations (entries in {-1,0,1}).
If rank L0<=2, the cube-fiber lift preserves the full endpoint and the
inherited #6777 theorem already gives the disjoint-subset rank bound.
Otherwise L0=L. If the occurring pattern span has dimension three, its
first-order coefficient vectors span all of L/2L. At a coordinate-call
index every such coefficient is zero, so every lattice vector has an even
entry there. A cube relation must then have entry zero there. Since cube
relations rationally span L, **every** relation has zero entry at every
coordinate-call index. The exponent group consequently splits as the
noncoordinate group plus the independent coordinate-call generators.

Projecting away those free generators removes coordinate calls while
preserving a diagonal monomial endpoint. Apply the joint-image theorem
to the complete noncoordinate pool. Its joint image is invariant and its
quotient action is the identity. As in #6777, a diagonal monomial endpoint
preserving a binary subspace decomposes that subspace by equal monomial
labels: independence of the group-algebra monomials makes each coordinate
label projection preserve the subspace. An adapted binary basis therefore
keeps the endpoint diagonal. Nonidentity quotient labels cannot occur.

In the one-edge or two-edge case this reduces the noncoordinate word to
at most five active scalar dimensions. The following uniqueness conclusion
is restricted to the two-edge case. If the five-dimensional complete-pool
restriction is irreducible, Section 4 gives its unique alphabet. If it
is reducible, an invariant flag gives block-upper-triangular subquotient blocks of
dimensions at most four. Adapt the binary basis to the equal-monomial
label decomposition at every flag term to retain a diagonal endpoint.
Each rank-one idempotent has exactly one active diagonal block.
The three-edge case already has coordinate blocks of size at most four.

The shear to {E11,...,E44,J5} need **not** preserve a diagonal endpoint:
it can introduce the two edge positions. It is a proof normal form, not
a license to assume a diagonal endpoint in the sheared coordinates or to
insert free address transformations. The independent coordinate-call
generators removed above must also be restored to their original target
labels. No saving follows from
this scalar reduction. Exact rank-three diagonal identities, rational
rank-one address realizations and a complete paid/target invoice remain
unproved.

## 8. Provenance and scope

Scientific base: 7c49fe32c55de02c2c873655c804b16e4c3fef0a. The inherited
all-width two-relation theorem is #6777, exact head
 e62a9d0d4143e11c190fcb4d81d83dc1662da782. Credit Nick Petalas/#5921 for the
fiber and cardinality theorem; David Govea/#720 and Ali Romman/#468 for
the relation and augmentation framework; woklerx/#1456 and #1846 for
the common-pattern and historical two-plane reductions; and eumemic/#288
for the formal model. The new contribution is the quotient observation,
general edge-quotient bound, sharp two-edge bound, unique five-dimensional
irreducible normal form,
and its explicit obstruction to four-dimensional pool compression.

No physical supplier, native implementation, dirty-input compiler, recursive
invoice, admitted BIT improvement, selected-frontier change, new kappa,
independent human acceptance, or proof-assistant formalization is claimed.
