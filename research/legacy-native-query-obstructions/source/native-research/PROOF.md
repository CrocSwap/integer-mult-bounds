# Subgroup filters for native ADDRESS words

Use the native model from PR521 at
`a190fdb39f31647fc6f651625353710624627348`.
Let G be the group of rational invertible ADDRESS maps. Work in
`Mat_4(F_2[G])`. A query is `H_N(g)=I-N+N g`, where N is a nonzero
binary rank-one idempotent. Its inverse is `H_N(g^-1)`.
The all-size ADDRESS contract gives this group-algebra identity. A
test at one modulus does not give it.

## One map outside a subgroup

Let H be any subgroup that contains the endpoint. Suppose exactly one
query uses a map g outside H. Write the word as

    A (I-N+N g) B,

where A and B are invertible matrices over `F_2[H]`. The first term
`A(I-N)B` has support in H. The second term `A N g B` has support in
the double coset `H g H`, which is disjoint from H. That second term
cannot be zero: multiplication by `A^-1` and `B^-1` would give `N g=0`.
Thus the endpoint cannot have support in H.

This proof permits all binary scalar projectors. It does not use a
map from `F_2` to the rational numbers.

## Two maps outside a subgroup

Suppose the only maps outside H, in chronological order, are g1 and
g2. Remove the first and last words over H. The remaining matrix is

    F = H_M(g2) B H_N(g1),

where B is invertible over `F_2[H]`. If the full endpoint is over H,
then F is over H. Since `H_N(g1) N = N g1`,

    F N = (I-M) B N g1 + M g2 B N g1.

This matrix is nonzero because every factor before N is invertible.
The two terms have support in `H g1 H` and `H g2 H g1 H`. The first
set is disjoint from H. The second set can meet H only if

    g2 belongs to H g1^-1 H.

Therefore that double-coset membership is necessary. It is not
sufficient. The scalar coefficients and all other word terms still
have to cancel.

For B3 signed permutation maps and coordinate shears
`U_ij(a)=I+a E_ij`, with nonzero rational a and i different from j,
the condition is `abs(a2)=abs(a1)`. Signed permutation multiplication
preserves the multiset of absolute matrix entries. It also changes
the position and sign of a by conjugation. These two facts prove both
directions. For positive coordinate scalings with factors d1 and d2
different from 1, the condition is `d1*d2=1`.

## One positive query and a common Gram matrix

Suppose ten maps preserve one nondegenerate symmetric rational matrix
Q. Every nonidentity rank-one update that preserves Q has determinant
-1. Here is a proof that also permits indefinite Q.

Write `g=I+u v^T`, with nonzero u and v. Set `w=Q u` and
`a=u^T Q u`. The equation `g^T Q g=Q` gives

    v w^T + w v^T + a v v^T = 0.

Choose a nonzero entry of v. The entries in its row imply that w is
`k v` for a scalar k. Nondegenerate Q and nonzero u imply `k!=0`.
The equation then gives `2k+a=0`. Hence

    det(g) = 1+v^T u = 1+a/k = -1.

A positive-determinant rank-one query is therefore outside the group
that preserves Q. The one-map lemma excludes an eleven-call word
with ten common-Gram reflections and one positive query. This is
stronger than the B3-only instance. It does not exclude three or more
positive queries, or negative queries without one common Gram matrix.

## Three nonunit determinant magnitudes

Apply the group homomorphism `g -> abs(det(g))` to the word. Its image
is the torsion-free abelian group of positive rational numbers. If
exactly three queries have nonunit determinant magnitudes x,y,z,
the projected endpoint is the identity. The determinants of the
scalar controlled matrices give `xyz=1`. Thus

    H_M(y) H_N(x) = H_P(xy).

If x differs from y, the group terms `1,x,y,xy` are distinct. Their
coefficients imply `MN=N=M=P`. If x equals y, torsion-freeness makes
`1,x,x^2` distinct. The coefficient of x implies `M=N`, and then
the coefficient of x squared implies `P=N`. Thus all three scalar
projectors must be equal. With exactly two nonunit magnitudes, their
magnitudes must be reciprocal and their projectors must be equal.
Unit-determinant unipotents do not appear in this test.

## The three-shear quarter turn has one scalar projector

Set `U=I-E_12` and `V=I+E_21`. The product `R=U V U` is a B3
quarter turn. Suppose the three consecutive positive queries are

    H_C(U) H_B(V) H_A(U).

The distinct ADDRESS terms are `1,U,V,VU,UV,U^2,R`. Among these,
only 1 and R belong to B3. If the three-query block has all support
in B3, its five other coefficients must vanish. The coefficients of
VU and UV first give

    BA=CBA=CB.

The coefficient of V is `B+CB+BA+CBA`, so `BA=CB=CBA=B`.
The coefficient of U squared gives `CA=CBA=B`. The coefficient
of U is `A+C+BA+CB`, so `A=C`. Idempotence then gives
`B=CA=A^2=A=C`. Thus the three scalar projectors must be equal.

The block is therefore `H_A(R)`. The quarter turn R is the product
of one coordinate reflection and one signed swap reflection. It can
use two B3 queries with projector A. A full word in which the other
maps are in B3 and this three-shear block is consecutive can always
replace that block by two queries. This result does not apply to
three positive queries that have other ADDRESS queries between them.
It also does not prove that a ten-call B3 word is impossible.

The checker uses all `120^3=1728000` ordered projector triples and
tests the five off-B3 coefficients. Exactly 120 triples pass, one
for each equal-projector choice. A separate full group-algebra
replay checks all 120 passing blocks and the two-query replacement.
It also checks every one of the 14400 triples whose first projector
is E00 by full operator replay, without the five-coefficient formula.
A common scalar conjugation takes any first rank-one idempotent to
E00. The pool and the condition of support in B3 are unchanged by
that conjugation. This second calculation is therefore complete.

## Scope

These are exact necessary conditions. They give no shorter native
word, no new supplier exponent, and no integer-multiplication kappa.
The finite checker verifies the B3 double-coset calculations and
full rational group-algebra controls. The written proofs establish
the general subgroup and Gram statements.
