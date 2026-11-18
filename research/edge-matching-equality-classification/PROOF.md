# Equality in the binary edge-matching image bound

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
This is an all-dimension classification with two explicit finite proof steps.
It does not supply a paid BIT word or a new kappa.

## 1. Statement

Work over F2 at any finite ambient width. Let C be a collection of rank-one
idempotents with nonzero off-diagonal patterns. Let H be its actual pattern
span, k its dimension, V its joint image, and n the dimension of V. Let nu
be the maximum matching size in the undirected graph whose edges are the
coordinate pairs of matrix units contained in H. Assume n is positive and
C acts irreducibly on V. Coordinate projectors are excluded throughout.

The source theorem gives `2n <= 3k+nu-1`. Equality is possible **if and
only if** `0 <= nu <= k-1` and `k-nu = 1 modulo 4`.

More precisely, apart from the one-projector case `(k,nu,n)=(1,0,1)`,
every equality collection is already the complete pool of H. After a
coordinate permutation, it consists of t disjoint matrix-unit pairs,
r disjoint normal triples, and one fresh link, where

```text
t = nu,        r = (k-nu-1)/2 is even,
k = t+2r+1,   n = 2t+3r+1.
```

The image/covector pairs on each coordinate pair are
`(e_a, e_a+e_b)` and `(e_a+e_b, e_b)`. A normal triple, in binary masks
on its own three coordinates, is `(6,5), (5,6), (7,7)`. Let h_x and h_y
be the sums of all old image and covector vectors. The link is

```text
L = (h_x+a)(h_y+b)^T,
```

where a,b are supported outside all old blocks and `b dot a = 1`.
Every such nonempty-core family is an equality pool. All its n projectors
have independent images. Its action is isomorphic to the first n-1
coordinate projectors together with the all-one n-by-n matrix. In
particular, **equality always has odd n**.

At `(1,0,1)`, take any rank-one idempotent whose off-pattern is nonzero
and not a matrix unit; its unique lift is the whole pool. The simple pair
`(x,y)=(1,7)` is a positive control.

If `k-nu = 3 modulo 4`, equality is impossible. Since `3k+nu` is odd,
the sharp bound improves to `2n <= 3k+nu-3`. Thus, for every odd
positive k-nu, the exact maximum image dimension is the largest odd
integer at most `(3k+nu-1)/2`. The proof below supplies attainment in
both residue classes. Even k-nu and classification of the lower attaining
pools remain open. Even irreducible image dimensions remain possible
away from the first equality.

## 2. Reduction to a complete pool and three basis cases

Use the disjoint diagonal-relation theorem and matching bound of
[PR #7692](https://github.com/CrocSwap/integer-mult-bounds/pull/7692),
[pinned proof](https://github.com/aliromman/integer-mult-bounds/blob/c2870a38841f515db7203a0761cd77f014f7fb7a/research/edge-matching-image-bound/PROOF.md).
That theorem is a consumed premise, not re-proved here.

At equality, `3k+nu=2n+1`. The total-image bound therefore also limits
the complete pool to n dimensions. Its image contains V, so it is V.
Adding operators to an irreducible collection preserves irreducibility.
It suffices to classify this complete pool.

Choose n pool projectors with independent images. Let k0 be their pattern
rank, d=n-k0 their diagonal-relation dimension, and t the number of
size-two relation groups. The groups are disjoint. All other groups have
size at least three. If f is the number of members in no relation, put

```text
delta = f + sum(m-3 over groups of size m at least three).
```

The source identities give

```text
2n = 3k0+t-delta,
t <= nu,   k0 <= k,
3(k-k0)+(nu-t)+delta = 1.
```

Thus k0=k. There are only these cases:

1. t=nu-1, delta=0: only size-two and size-three groups.
2. t=nu, delta=1: one size-four group, all other groups of size two or three.
3. t=nu, delta=1: one free member, all groups of size two or three.

For a group of size m, let S_j be the coordinate support of its diagonal
sum and U_j its image space. The source support theorem gives disjoint S_j,
all group covectors supported on S_j, the coordinate space on S_j inside
U_j, and `1 <= |S_j| <= m` with `|S_j| = m modulo 2`.

## 3. Excluding cases with no free member

Let S be the union of the active sets S_j. If all chosen projectors belong
to relation groups, H has zero columns outside S. The coordinate kernel
`K = {v in V : v is zero on S}` is invariant under every pool member.
A covector supported on S kills K. A covector with an outside bit j has
image e_j, because its off-column j is zero; that image is in K.
If `|S|<n`, K is proper and nonzero.

If `|S|=n`, every group is a full coordinate block. H is block diagonal.
A noncoordinate rank-one idempotent cannot cross these blocks: choose a
coordinate present in both factors, which exists by idempotence. The
forbidden cross entries confine both factors to its block. More than one
block therefore gives reducibility.

A single size-two block has matching number one, so it cannot realize
case 1, which would require nu=2. The remaining single-block cases are:

- a full orthogonal triple at `(n,k,nu)=(3,2,1)`;
- a full orthogonal quadruple at `(n,k,nu)=(4,3,0)`.

These are finite coordinate problems. The checker enumerates all 28
unordered bases of F2^3 and all 840 unordered bases of F2^4, with their
unique duals. The independent cardinality formula is
`product(2^w-2^i, i=0..w-1) / w!`. Respectively 18 and 339 bases have
all selected patterns nonzero and the required k,nu.

For every surviving space, all rank-one idempotents are found both by a
raw x,y scan and by separate literal-pattern lifting. The complete pools
have sizes four or five. Every pool has a checked proper invariant
subspace, recorded with its basis and full pool in EXCEPTIONS.json. A
separate orbit-closure check over every nonzero vector also rejects
irreducibility. This finite exhaustion excludes both remaining cases.
It is part of the proof, not an extrapolation to untested widths: the
preceding argument reduces each exceptional case to exactly width three
or four.

## 4. Every triple in the free-member case has full active rank

Now let H0 be the pattern span of all relation groups, and let L be the
free projector. Then `H = H0 + span(off(L))`. A size-two group has full
active rank two. A size-three group has active rank one or three.

Suppose c triples have rank one. Then, for the union S of active sets,
`|S| = n-1-2c`. A rank-one-active triple has covectors e_j and images
`e_j+v_i`, where the v_i are the three nonzero vectors of a two-dimensional
space T. T contains no coordinate vector. Such a vector would be outside
all other active blocks, by independence of the group image spaces. Its
matrix unit would add an edge disjoint from the t selected edge pairs,
contrary to `t=nu`.

Every lift of a nonzero H0 pattern has its covector supported on S. If
there were an outside covector bit a, its zero off-column would force
image e_a. A full-rank group has no row outside its block. A rank-one-active
triple would need the forbidden coordinate vector e_a in T. Thus no
nonzero H0 pattern can be that outside row.

All patterns in the other coset have the same columns outside S. If these
columns are zero, the invariant K from Section 3 proves reducibility.
Otherwise, one nonzero outside column pins every image bit except its own
diagonal bit, so at most two images occur in that coset. Two or more
nonzero outside columns pin those missing bits as well, leaving at most
one image. For each image, all outside covector bits are determined by
the fixed columns and idempotence. Therefore the outside restrictions
of the odd-coset covectors span at most two dimensions.

The span of all pool covectors has dimension at most `|S|+2`. If c is
positive, this is at most n-1. There is a nonzero common kernel on V,
contrary to irreducibility. Thus c=0.

This extends the complete-coset support argument of
[PR #7691](https://github.com/CrocSwap/integer-mult-bounds/pull/7691),
[pinned proof](https://github.com/aliromman/integer-mult-bounds/blob/69e70b1426c32b19da8334930815800a2c95ffca/research/no-edge-dim5-extremal-classification/PROOF.md),
to any number of edge pairs and triples. It includes all additional pool
members; it does not assume that a selected image basis is irreducible.

## 5. The full blocks and unique link force even r

A matrix unit in a full triple block would again give an edge disjoint
from all t selected pairs. Thus every triple is unit-free. The finite
three-coordinate normal-form lemma cited in PR #7691 gives the displayed
normal triples. The checker also repeats this step: the 28 unordered
bases give exactly three unit-free versions, all coordinate permutations
of the displayed triple. The old complete pool is exactly the pair and triple
members: block support forbids cross-block lifts, each pair has its two
unit lifts, and each nonzero triple pattern has its unique lift.

Let C0 be the old coordinate core, of dimension m=n-1. Write
`L=(u+a)(v+b)^T`, with u,v on C0 and a,b outside. Independence of the
link image gives a nonzero a. A zero b would leave all columns in C0
and make the fresh image line invariant. Hence b is nonzero.

If v=0, every pool projector either maps C0 into C0 or kills C0, so C0
is invariant. If u=0 and v is nonzero, the fixed fresh/core rectangle
forces every odd-coset projector either to have image a or to kill a;
the old pool also kills a. Its line is invariant. Hence u,v are nonzero.

The two nonzero cross rectangles `a v^T` and `u b^T` are fixed across
the odd coset. Nonzero binary rank-one rectangles have unique factors.
Thus u,v,a,b are fixed, and L is its only lift. The complete pool has n
members.

Let `(x_i,y_i)` be the m dual old pairs. Irreducibility forces both
`y_i dot (u+a)=1` and `(v+b) dot x_i=1` for every i. Otherwise an old
image line or the span of the other old images and the link is invariant.
The pairings force `u=sum x_i=h_x` and `v=sum y_i=h_y`.
The old covectors kill a. To avoid a common kernel, `b dot a=1`.
Idempotence of L now gives

```text
1 = (h_y+b) dot (h_x+a) = m modulo 2 + 1.
```

Therefore m is even. Since `m=2t+3r`, r is even. Pattern dimension is
`t+2r+1`; matching number is t. This proves the necessity of
`k-nu = 1 modulo 4` and the stated normal form. Every original equality
collection contains an n-element image basis and lies in this n-member
complete pool, so it is the complete pool itself.

## 6. Attainment at the first bound

Take t arbitrary nonnegative and r arbitrary nonnegative even, with a
nonempty core. Use the displayed old blocks and any fresh a,b with pairing
one. The link is idempotent. Its cross rectangles make its pattern
independent of H0 and fix its unique odd-coset lift. Both rectangles are
nonzero, so that coset contains no matrix unit. The old blocks give exactly
t disjoint unit edges. The dimensions are the stated k and n.

The old projector covectors detect the core, and the link covector detects
the fresh image line. The common kernel on V is zero. The link maps every
old image to its image, and every old projector maps the link image to
its own image. Any nonzero invariant subspace therefore contains all
projector images and is V. This proves irreducibility and attainment.
In the basis of the old images followed by a, the operators are the first
m coordinate projectors and the all-one matrix of odd size m+1.

## 7. Sharp attainment when k-nu is three modulo four

Write `t=nu` and `r=(k-nu-1)/2`, now odd. Take t old edge pairs and r
old normal triples, with no fresh coordinates. Put `m=2t+3r` and add
`L=h_x h_y^T`. Since m is odd, L is idempotent. On the m-dimensional
old image, this gives all m coordinate projectors and the all-one matrix.
Their action is irreducible: the coordinate projectors detect every
nonzero vector, and the all-one operator connects every coordinate image.

If there are at least two old blocks, the cross-block entries make the new
pattern independent of H0. The odd coset has at least two cross-block
entries, so it contains no matrix unit. The old matching number is t.
Two distinct block rectangles pin every image and covector component of
an odd-coset lift; with more blocks the other rectangles pin the rest.
Thus L is the only new lift. The complete pool has m+1 projectors, with
joint image m, and

```text
k=t+2r+1,  nu=t,  n=m=(3k+nu-3)/2.
```

The only one-block case is `(t,r)=(0,1)`, hence `(k,nu,n)=(3,0,3)`.
Use the three image/covector pairs `(7,63), (56,504), (448,511)` at
width nine. These are the three-copy embeddings of the three-coordinate
projectors with images e_0,e_1,e_2 and covectors
`e_0+e_1`, `e_1+e_2`, `e_0+e_1+e_2`. The covectors are independent,
and their action graph is strongly connected, so the image is irreducible.
Their matrix span has exactly those three rank-one idempotents: a sum
with two nonzero rows has two distinct nonzero row vectors and rank at
least two. The exact three-copy pool lemma of
[PR #7688](https://github.com/CrocSwap/integer-mult-bounds/pull/7688),
[pinned proof](https://github.com/aliromman/integer-mult-bounds/blob/d9aba79eaed566640353efcb0a27b0d5649f705a/research/no-edge-basis-extraction-failure/PROOF.md),
retains that complete pool, injects the matrix span into off-patterns
and excludes matrix units. The checker also lifts all seven nonzero
patterns directly. This proves the remaining attainment case.

Together with Sections 1–6, this gives the exact maximum for every odd
positive k-nu. It does not classify all pools at the improved bound.

## 8. Finite evidence and limits

The checker lifts every nonzero pattern for 27 attaining families, with
18927 patterns in total. It varies edge count, even triple count and fresh
supports. Direct all-vector orbit checks run when n is at most nine; the
larger finite cases check the exact star pairings and common-kernel rank.
Ten families attain the improved bound; all 4206 of their nonzero
patterns are lifted. The checks include the exceptional width-nine pool.
It also checks 1050 links in two column-triple domains, including every
extra pool member, and finds a common kernel in each.

Three odd-triple controls with `b dot a=0` are idempotent equality pools
but have a common kernel. Forcing pairing one instead makes the link have
trace zero. A separate complete irreducible pool with `(k,nu,n)=(3,0,2)`
shows that even n is possible away from equality. The theorem does not
exclude those alphabets.

The equality classification concerns operator geometry. It does not prove
a legal paid relation lattice, native realization, dirty-state restoration,
complete BIT invoice, selected-assumption discharge or new kappa. All five
selected assumptions remain. Independent human and formal-kernel review
are not claimed.

## Open next questions

What is the exact maximum when k-nu is even, and which complete pools
attain the improved bound in the odd case? For the classified first-equality
pools, can any legal word
beat paid rank after the relation lattice and full endpoint are charged?
The existing orthogonal-basis single-bridge word obstruction must be used
before a new word search.
