# Sharp joint-image bounds for three binary pattern dimensions

Prepared for **@CubeJerry** with substantial OpenAI assistance. New work is
Apache-2.0. This is a written, all-width linear-algebra proof, accompanied by
finite exact corroboration. **No new κ.**

## 1. Statement and relation to earlier work

Work over the binary field F2. For a matrix N, write off(N) for the matrix
obtained by deleting its diagonal. Let P be a linear subspace of the
zero-diagonal W-by-W matrices, and define the **complete noncoordinate pool**

    C(P) = {N = x y^T : y^T x = 1, off(N) in P, off(N) != 0}.

The condition y^T x=1 makes N a rank-one idempotent. Put

    V(P) = sum_{N in C(P)} im(N),

and let e(P) be the number of matrix units E_ab, a!=b, contained in P.
Coordinate projectors E_aa are excluded, even though their zero patterns
belong to every P.

**Theorem 1 (no-edge bound).** If dim P<=3 and e(P)=0, then

    dim V(P) <= 4.

For dim P=3 the bound is sharp, already at W=5. The transpose statement
also holds: the span of the covectors y has dimension at most four.
Neither statement assumes that the pool acts irreducibly on its joint image.

**Theorem 2 (sharp universal rank-three bound).** Among all three-dimensional
binary pattern spaces and all widths, the maximum of dim V(P) is exactly six.
More precisely, the following bounds hold:

| e(P) | Joint-image bound | Source of the bound |
| --- | ---: | --- |
| 0 | 4, sharp | Theorem 1 below |
| 1 | 5 | The edge-quotient argument in #6782 |
| 2 | 5, sharp | #6782, including an irreducible attaining example |
| 3 | 6, sharp | #6782; three disjoint directed edges attain six |

The new result is the sharp no-edge bound four, replacing the previous
seven-projector upper bound. Combining it with the inherited edge-containing
bounds establishes the sharp universal maximum six. We do not claim the
one-edge bound is sharp, or a new classification of irreducible pools.

The question originates in Nick Petalas's #5921,
`research/pattern-pool-cardinality/PROOF.md` and its README. That contribution
proved the fiber and cardinality theorem and explicitly left sharp joint-image
dimension as a follow-up. The later #6782,
`research/bit-three-relation-core/PROOF.md`, established the edge-quotient
bound and identified the zero-edge case as outside its sharp classification.
Its exact proof is retained in `sources/pr6782-PROOF.md`; this package's
argument is self-contained and does not import predecessor code.

## 2. The inherited fiber lemma

We recall and credit the following lemma to Nick Petalas, #5921.

**Fiber lemma.** A realized nonzero off-diagonal pattern has exactly one
binary rank-one-idempotent lift, except a matrix unit E_ab. That pattern has
exactly the two lifts

    e_a(e_a+e_b)^T,       (e_a+e_b)e_b^T.

Here is the short proof, to make the mathematical dependencies reviewable.
If distinct projectors N=xy^T and M=uv^T have the same pattern, their sum D
is nonzero and diagonal. Its rank is at most two and its trace is zero, since
both projectors have trace one. Over F2, D therefore has exactly two nonzero
diagonal entries, at a,b. Its image is contained in span(x,u), so this span
equals span(e_a,e_b). Applying the same argument to the transposes puts y,v
in that coordinate plane too. The six rank-one idempotents on F2^2 are

    [[1,0],[0,0]], [[0,0],[0,1]],
    [[1,1],[0,0]], [[0,1],[0,1]],
    [[0,1],[0,1]]^T, [[1,1],[0,0]]^T.

Their only repeated nonzero patterns are the two single directed edges.
This also excludes a third lift. In particular, when e(P)=0, different pool
projectors have different nonzero patterns.

## 3. Intersecting diagonal dependencies

The key new observation is about image independence; it does **not** require
the covectors to be independent.

**Lemma 3.** Let N_i=x_i y_i^T, 1<=i<=5, have linearly independent nonzero
image vectors x_1,...,x_5 over F2 and nonzero covectors y_i. Suppose

    D = N_1+N_2+N_3,       F = N_1+N_4+N_5

are diagonal. Then N_1 is a coordinate projector.

**Proof.** Take any coordinate j with (y_1)_j=1. The j-th column of D is

    x_1 + (y_2)_j x_2 + (y_3)_j x_3.

It is nonzero, since x_1,x_2,x_3 are independent. As D is diagonal, this
column must equal e_j. The same reasoning for F puts e_j in both
span(x_1,x_2,x_3) and span(x_1,x_4,x_5). Independence of all five image
vectors makes the intersection exactly span(x_1). Consequently x_1=e_j.
Every coordinate in the support of y_1 must satisfy this same equality,
so y_1=e_j too. Hence N_1=E_jj. This proof does not need the idempotence
hypothesis separately. ∎

The independence assumption is essential. In the sharp construction in
Section 5, five projectors can have both displayed diagonal sums while
their common projector is noncoordinate; their image rank is four. The
verifier retains this as a failure control.

**Lemma 4 (five points in the binary three-space).** Any five distinct
nonzero vectors of F2^3 contain two three-element zero-sum subsets meeting
in exactly one element.

**Proof.** Let a,b be the two omitted nonzero vectors and put p=a+b. The
vector p is present. Addition by p partitions the other six nonzero
vectors into three pairs. One pair is {a,b}; the two remaining pairs are
present, and each, together with p, is a zero-sum triple. These triples
meet exactly at p. ∎

There are 21 five-element subsets; the verifier checks every one. The
four-point set {001,010,100,111} has no zero-sum triple, so this particular
argument does not reduce the upper bound from four to three.

## 4. Proof of the no-edge theorem

Assume for contradiction dim V(P)>=5. Choose five pool projectors with
independent images. By the fiber lemma their patterns are five distinct
nonzero elements of P. Their existence forces dim P=3, since a space of
dimension at most two has at most three nonzero elements.

Lemma 4 supplies two zero-sum pattern triples with exactly one common
pattern. Uniqueness of each lift makes the triples share exactly one
projector. Relabeling the five projectors gives the two triples in
Lemma 3. A zero sum of patterns means that each corresponding sum of
projectors is diagonal. Lemma 3 then makes their shared projector
coordinate, contradicting its membership in C(P). Thus dim V(P)<=4.

Apply the same result to P^T to obtain the covector-span bound. This is an
all-width argument; no finite census is used to establish its quantifiers.

## 5. A complete no-edge pool attaining four

Use coordinates 0,1,2,3,4. Let U be the even-parity subspace on coordinates
1 through 4, viewed as a subspace of F2^5 with coordinate 0 equal to zero.
It has dimension three and no weight-one vector. Set

    P = {u e_0^T : u in U}.

This is a three-dimensional zero-diagonal pattern space with no matrix
unit. For each nonzero u in U, the matrix

    N_u = (e_0+u)e_0^T

is a rank-one idempotent with pattern u e_0^T. All seven nonzero patterns
are realized, and each has a unique lift by the fiber lemma. Thus these
seven projectors are the **complete** pool.

Their images lie in span(e_0) direct-sum U. For distinct nonzero u,v in U,
the three vectors e_0+u, e_0+v and e_0+u+v sum to e_0. Therefore e_0 is
in V(P), and then every u is too. Hence

    V(P) = span(e_0) direct-sum U,       dim V(P)=4.

For literal reproduction, use bit i for coordinate i. A basis of U has
masks 6,10,18, and its nonzero masks are 6,10,12,18,20,24,30. The seven
projector factors (x,y) are (1+u,1). This example is reducible: U is its
common kernel. Sharpness here is for **total joint image**, not irreducible
core dimension.

## 6. The inherited edge-quotient argument and the universal maximum

For clarity we give the argument from #6782 in full and claim no novelty
for it. Let e=e(P), let P_0 be the span of all e matrix units in P, and
let E be the coordinate span of their endpoints. Distinct matrix units
are independent, so dim P_0=e and e<=dim P. Both lifts of every edge
belong to the complete pool, and their images span its two endpoints.
Consequently E is contained in V(P).

A noncoordinate rank-one idempotent whose pattern is supported in the
E-by-E block has image in E. Indeed, an outside coordinate i with x_i=1
would force y=e_i from its off-diagonal row. The outside column i then
forces x=e_i, contradicting noncoordinate status. In particular, the
zero coset P_0 contributes no joint-image dimension modulo E.

Fix a nonzero coset of P/P_0 and two projectors N=xy^T and M=uv^T whose
patterns belong to it. Their off-diagonal difference is supported in
E-by-E. Suppose x and u have independent images modulo E. Their outside
rows and inside columns give

    (x mod E)(y|E)^T = (u mod E)(v|E)^T,

forcing y|E=v|E=0. Both inside blocks then vanish, so the full patterns
of N and M agree. They are distinct projectors, and the fiber lemma
makes this common pattern a single edge. Its two lifts have covectors
vanishing on E only if both edge endpoints lie outside E. This
contradicts the definition of E using **all** edges in P.

Thus the image classes in each nonzero coset are pairwise dependent;
over F2 their span has dimension at most one. Therefore

    dim V(P) <= dim E + 2^(dim P-e) - 1
             <= 2e + 2^(dim P-e) - 1.

For dim P=3 and e=1,2,3 this gives respectively 5,5,6. For e=0 use the
new upper bound four instead of seven. All cases have joint image at
most six.

The old attaining example consists of three disjoint directed edges:

    P = span(E_01,E_23,E_45) in M_6(F2).

Their six lifts have factor masks

    (1,3), (3,2), (4,12), (12,8), (16,48), (48,32).

They span all six coordinate directions. A sum of two or more disjoint
edges is not realizable: the two required entries force a forbidden
cross entry in a rank-one matrix. Hence the displayed pool is complete.
This proves the sharp universal maximum six, with attainment credited
to #6782.

## 7. Relevance, scope and remaining obligations

The all-width reduction cuts the largest previously unclassified
three-dimensional no-edge joint image from seven to four. This is a
structural restriction on the binary scalar pool. In the relation-based
word framework of #6777 and #6782 it can be used after their hypotheses
have legitimately reduced the occurring pattern span to at most three
and dealt with coordinate calls. We do not reprove those word-reduction
hypotheses or assert that an arbitrary three-relation word satisfies
the required split.

V(P) is invariant under every projector in C(P), since the image of
every such projector lies in V(P). The quotient action is zero for the
projectors and identity for factors I+(z^A-1)N. This elementary fact does
not license free physical basis changes, discard coordinate calls, or
prove a paid/target rank inequality. Coordinate projectors have zero
pattern and can enlarge the joint image without bound; excluding them
is essential. Four-dimensional pattern spaces also fall outside the
theorem: the same parity construction in width six has joint image
five, and is a retained scope control.

This package proves no rational-address realization, native primitive,
dirty-input compiler, recursive invoice, supplier admission, full
multiplication improvement, formal proof-kernel result, or human
acceptance. The selected frontier is unchanged.

## Open next questions

1. **Irreducible no-edge bound.** Can a complete three-dimensional no-edge
   pool act irreducibly on a four-dimensional joint image, or is the
   irreducible bound three? The sharp example above is reducible, so it
   does not decide this. Start by classifying four independent image
   projectors and their remaining patterns. A new all-width argument or
   explicit example is required; a failed finite search would not settle it.
2. **Word consequences after a valid split.** Does the reduced at-most-four
   scalar alphabet satisfy the required three-relation paid-rank
   obstruction, or admit a rank-saving word? First state and check the
   exact relation/cube-span and coordinate-call hypotheses from #6777
   and #6782, then derive the full endpoint and paid-rank accounting.
   This pool theorem alone supplies neither conclusion.

## Source and attribution record

Scientific base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
Retained #6782 proof: head `685457252b51b9c7932ece363365bdf0b12c9c31`,
with exact content hashes in `ORIGINS.json`. Credit Nick Petalas for
#5921's fiber/cardinality theorem; @CubeJerry and the credited researchers
in #6782 for its edge-quotient bound and attaining edge examples. The
relation-word context is inherited from #6777 and the sources it credits;
it is context, not a proof dependency of Theorems 1 or 2.
