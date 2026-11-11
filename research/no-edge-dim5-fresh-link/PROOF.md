# Odd fresh links on two normal-form blocks

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
The fiber lemma is cited and not reproved. Everything else is proved here.

This is not a new κ. The selected frontier stays
`363005817/100000000000`. The argument does not bound every
pattern-dimension-5 pool, and it does not list those pools. It classifies
one family of links and gives one coordinate counterexample to uniqueness.

## 1. Statement

Work over F2. For a matrix N, write off(N) for N with its diagonal deleted.
For ambient width W, let P be a linear space of zero-diagonal W×W matrices
containing no matrix unit. The complete no-edge pool is

```text
C(P) = {x y^T : y·x = 1, off(x y^T) is a nonzero element of P}.
```

Every element is a rank-one idempotent. Write V(P) for the span of the
images. The action is reducible when some subspace 0 < U < V(P) is invariant
under every pool projector.

Let A = {0,1,2} and B = {3,4,5}. The normal-form triple on A is

```text
u = e1+e2,  v = e0+e2,  o = e0+e1+e2,
```

with projectors u v^T, v u^T and o o^T. The hub is coordinate 2 and the
leaves are 0 and 1. The same formulas shifted by 3 give the triple on B,
with hub 5 and leaves 3 and 4. These six projectors are the block pool.
Their off-diagonal patterns span a 4-dimensional space H = Q_A ⊕ Q_B, the
sum of the two 2-dimensional block pattern spaces. This is the same pair of
blocks as in the seven-projector witness of #7237.

For an odd positive integer k, let F_k = {6, 7, ..., 5+k} and

```text
z_k = e2 + e5 + sum_{t in F_k} e_t.
```

**Theorem 1.** For every odd integer k ≥ 1 and every width W ≥ 6+k, let P
be the span of H and off(z_k z_k^T). Then dim P = 5, P contains no matrix
unit, C(P) is exactly the six block projectors and z_k z_k^T, dim V(P) = 7,
and the action on V(P) is irreducible.

**Theorem 2.** Let z be any vector with z·z = 1 and weight at least 3 whose
support meets A in at most one coordinate and B in at most one coordinate.
Let P be the span of H and off(z z^T), in any width large enough to contain
A ∪ B ∪ supp(z). Then dim P = 5, P contains no matrix unit, C(P) is the six
block projectors and z z^T, and dim V(P) = 7. The action is irreducible if
and only if supp(z) contains both hubs. In that case the fresh set
supp(z) \ (A ∪ B) is nonempty of odd cardinality, and the pool is Theorem 1
after renaming those fresh coordinates.

**Corollary.** The k = 3 pool is not a coordinate permutation of the k = 1
pool. The k = 1 pool is the seven-projector witness of #7237. Therefore an
irreducible complete no-edge pool of pattern dimension 5 and joint-image
dimension 7 need not be a coordinate permutation of that witness.

Sections 2–6 prove Theorem 1. Section 7 proves Theorem 2. Section 8 is the
corollary. Section 9 records an incidence matrix that does not see k.
Section 10 is a separate exhaustive finite census. It is not an all-width
classification of links that meet a block in two or more coordinates.

## 2. The pattern space

The three A-patterns are the ones written in #7237:

```text
p_u = E10 + E12 + E20,
p_v = E01 + E02 + E21,
p_o = E01 + E02 + E10 + E12 + E20 + E21.
```

They have weights 3, 3 and 6. The first two are disjoint and their sum is
the third, so they span Q_A. The translate by 3 spans Q_B. The blocks use
disjoint positions, so H is 4-dimensional.

The vector z_k has weight 2+k. That weight is odd, so z_k·z_k = 1 and
z_k z_k^T is a rank-one idempotent. Let S = {2,5} ∪ F_k, so |S| = 2+k.
The pattern p_* = off(z_k z_k^T) is 1 on every ordered pair of distinct
points of S, and 0 elsewhere. It has weight |S|(|S|-1) = (2+k)(1+k).

No position of p_* is internal to A or internal to B: S meets A only at the
hub 2 and B only at the hub 5. Coordinate 6 lies in F_k and in no block, so
column 6 of every matrix in H is zero, while column 6 of p_* is nonzero.
Thus p_* is outside H. Let P = H ⊕ span(p_*). Then dim P = 5.

A general element is q_A + q_B + λ p_*. If λ = 0 and the element is
nonzero, its weight is a sum of a weight in {0,3,6} from each block, not
both zero, hence at least 3. If λ = 1, every position of p_* survives,
because neither block meets those positions, and there are at least 3·2 = 6
of them. Every nonzero element has weight at least 3. In particular P
contains no matrix unit.

## 3. Support of the factors

Let x y^T be a pool element, and let T = A ∪ B ∪ F_k. Every matrix in P is
zero in every row and every column indexed by t not in T. If x_t = 1, then
y_j = 0 for all j ≠ t, so y = e_t. Then y·x = 1 forces the diagonal entry,
and the off-diagonal pattern is zero, which is not a pool pattern. If
y_t = 1 and x_t = 0 has already been proved, column t is zero, so x = 0,
which is impossible. Thus both factors are supported on T.

The same reading applies to a fresh coordinate f in F_k when the pattern is
even, meaning λ = 0. An even pattern has zero row f and zero column f, so
x_f = y_f = 0. An even pattern also has no entry between A and B: those
cross positions lie in p_*, not in H.

## 4. The odd coset

Every odd pattern contains every position of p_*. Fix the fresh coordinate
f = 6. Column f of H is zero, so column f of every odd pattern equals
column f of p_*: it is 1 on S \ {f} and 0 off S. The entries of column f,
off the diagonal, are x_i y_f. Therefore y_f = 1, x_i = 1 for every i in
S \ {f}, and x_i = 0 for every i outside S.

Row f of the same pattern is 1 on S \ {f}. Those entries are x_f y_j, so
x_f = 1 and y_j = 1 on S \ {f}. Off S the row is 0, so y_j = 0 outside S.
Thus x = y = z_k.

The projector is z_k z_k^T, whose pattern is exactly p_*. An odd pattern
with a nonzero block summand differs from p_* on an internal A or B
position, so it is not this pattern. The six entries of one fresh column
already forced the factors. The only odd pool element is z_k z_k^T.

## 5. The even coset

Let p = q_A + q_B be even and nonzero, and let x y^T realize it. Section 3
puts both factors on A ∪ B, with x_a y_b = 0 and x_b y_a = 0 for all a in A
and b in B.

The internal A-pattern is the restriction of x y^T. If it is nonzero, some
x_a and some y_a' equal 1. From x_a = 1 and the cross equations, every
B-bit of y is zero. From y_a' = 1, every B-bit of x is zero. The internal
B-pattern is then zero. The symmetric argument says that a nonzero
B-pattern forces the A-pattern to vanish. A pattern with both blocks
nonzero is unrealized.

So p lies in Q_A or in Q_B. The three nonzero elements of Q_A are p_u, p_v
and p_o. They are realized by u v^T, v u^T and o o^T, and none is a matrix
unit. By the fiber lemma of #5921, a realizable nonzero off-diagonal
pattern that is not a matrix unit has exactly one rank-one idempotent lift.
Those three lifts are the A-projectors, and the same holds for Q_B. There
is no further even pool element.

The odd-coset forcing in Section 4 does not use the fiber lemma. The
identification of the even pool at every width does. The verifier
enumerates the pool at the widths it checks and does not replace this
citation.

## 6. Image and irreducibility

Sections 4 and 5 give, for every W ≥ 6+k,

```text
C(P) = the six block projectors and z_k z_k^T.
```

The three A-images are u, v and o. On coordinates (e0,e1,e2) they are the
rows (0,1,1), (1,0,1) and (1,1,1). Adding the first two produces (1,1,0);
adding the third produces (0,0,1); back-substitution produces the identity.
They are a basis of L = span(e0,e1,e2). The three B-images are a basis of
R = span(e3,e4,e5). The vector z_k is not in L ⊕ R, because it has a fresh
coordinate. Therefore

```text
V(P) = L ⊕ R ⊕ span(z_k).
```

Since e2 lies in L and e5 lies in R,

```text
V(P) = L ⊕ R ⊕ span(sum_{t in F_k} e_t),    dim V(P) = 7.
```

Let ζ be the covector z_k, so ζ(w) = z_k·w. Every A-image contains the hub
e2, and every B-image contains the hub e5, so ζ equals 1 on all six block
images. The three A-covectors are v, u and o, each of which contains e2, so
each equals 1 on z_k. The three B-covectors likewise equal 1 on z_k. Also
ζ(z_k) = 1 because the weight 2+k is odd.

The same three-by-three matrix shows that the A-covectors are a basis of
L*. They vanish on R and on the fresh sum. The B-covectors are a basis of
R* and vanish on L and on the fresh sum.

Let U be a nonzero invariant subspace of V(P).

If some w in U has ζ(w) = 1, the linking projector sends w to z_k, so z_k
is in U. Every block covector is 1 on z_k, so every block image is in U.
Those images span L ⊕ R. Then

```text
sum_{t in F_k} e_t = z_k + e2 + e5
```

lies in U, and U = V(P).

If instead ζ vanishes on U, no block image lies in U, because ζ is 1 on
each of them. An invariant subspace that does not contain a block image
cannot be hit by that block's covector, so every block covector vanishes
on U. The A-covectors span L*, so the L-component of every vector in U is
zero. The same holds for R. A vector of V(P) with both components zero is
λ times the fresh sum, and ζ of that vector equals λ, because the fresh
set has odd size. Thus λ = 0 and U = 0, a contradiction.

Every nonzero invariant subspace equals V(P). The action is irreducible.

Deleting the linking projector leaves the six block projectors. Their
covectors vanish on the opposite block, and each block's projectors map
into that block, so L is a proper nonzero invariant subspace. The fresh
link is what makes the seven-projector action irreducible. The dots in
this section never use a fresh coordinate, so the same deletion leaves L
invariant for every k.

## 7. The other disjoint-support squares

Let z have z·z = 1 and weight at least 3, and suppose |supp(z) ∩ A| ≤ 1
and |supp(z) ∩ B| ≤ 1. Let S = supp(z) and let F = S \ (A ∪ B). Then
|S| ≥ 3 forces F to be nonempty: A ∪ B can contribute at most two points
under the intersection bounds. Let p = off(z z^T). Its positions are the
ordered pairs of distinct points of S. None is internal to A or to B.
A fresh coordinate has zero column in H and nonzero column in p, so
p is outside H and P = H ⊕ span(p) has dimension 5.

The weight argument of Section 2 still applies: p is disjoint from the
internal block positions, and |S|(|S|-1) ≥ 6. Thus P contains no matrix
unit. Sections 3 and 4 used only that some fresh column of H is zero and
that p is the complete off-diagonal of S. They give the same odd coset:
the only odd pool element is z z^T. Section 5 did not use which point of
A or B lies in S. The even pool is still the six block projectors, by the
same appeal to the fiber lemma. Hence C(P) is those six projectors and
z z^T, and V(P) = L ⊕ R ⊕ span(z) has dimension 7.

Write h_A = e2 and h_B = e5.

Suppose S contains both hubs. The intersection bounds then exclude both
leaves, and |F| = weight(z) - 2 is odd and at least 1. Renaming F to
F_k puts this pool under Theorem 1, which is irreducible.

Suppose S does not contain h_A. There are two cases.

If S misses A, the linking covector z vanishes on L. Every B-covector is
supported on B, so it vanishes on L. Every A-projector maps into L. Thus
L is invariant. It is nonzero and proper in the 7-dimensional image.

If S meets A in a leaf ℓ, let m be the other leaf and let u_ℓ = e_m + h_A.
This is the weight-2 A-image that omits ℓ. Its covector is e_ℓ + h_A, which
dots u_ℓ to 1, so that projector sends u_ℓ to itself. The other weight-2
covector is u_ℓ itself, and u_ℓ·u_ℓ = 0. The full covector o meets u_ℓ in
the two coordinates m and h_A, so the dot is 0. Every B-covector vanishes
on u_ℓ. The link meets A only at ℓ, which u_ℓ omits, so z·u_ℓ = 0. Thus
span(u_ℓ) is invariant. It is a proper nonzero subspace of V(P).

The symmetric argument applies when S does not contain h_B. Therefore the
action is reducible unless both hubs lie in S. Combined with the previous
paragraph, both hubs are necessary and sufficient.

## 8. Not a coordinate permutation

A coordinate permutation preserves the multiset of Hamming weights of the
pool images, and the multiset of Hamming weights of their off-diagonal
patterns. Padding by unused coordinates does not change either multiset.

For k = 1 the seven image weights are 2, 2, 2, 2, 3, 3, 3 and the seven
pattern weights are 3, 3, 3, 3, 6, 6, 6. The linking image is e2+e5+e6,
of weight 3, and the linking pattern has weight 6. This is the witness
written in #7237.

For k = 3 the linking image has weight 5 and the linking pattern has
weight 20. The image weights are 2, 2, 2, 2, 3, 3, 5 and the pattern
weights are 3, 3, 3, 3, 6, 6, 20.

These multisets differ. The k = 3 pool is not a coordinate permutation of
the k = 1 pool. Theorem 1 says the k = 3 pool is an irreducible complete
no-edge pool of pattern dimension 5 and joint-image dimension 7. That is
the corollary in Section 1.

The same weight comparison separates every two distinct odd fresh sizes.
The linking image weight is 2+k and the linking pattern weight is
(2+k)(1+k). Both strictly increase with k.

## 9. The incidence matrix does not see the fresh set

Order the seven projectors as the three A-projectors, the three
B-projectors, and the link. Let G_ij be the dot of covector i with image j.
Section 6 shows that the six block rows form the 6×6 identity in the first
six columns, that every block covector meets the linking image, and that
the linking covector meets every image. Thus

```text
G = [ I_6    1 ]
    [ 1^T    1 ]
```

for every odd k. The fresh coordinates never enter these dots. As operators
on the 7-dimensional joint image, the pools therefore have one and the same
incidence matrix. This package does not claim a new configuration of lines,
and it does not claim that the pools are inequivalent under GL(W). The
corollary is only coordinate inequivalence, which is what question 2 of
#7237 asks. The no-edge condition and the pattern dimension are statements
about the standard basis.

## 10. Exhaustive censuses at widths 7, 8 and 9

These censuses fix the two blocks on A and B. They do not range over other
5-dimensional pattern spaces. Each one has a finite domain, and the
verifier visits every element of that domain.

**Width 7, every idempotent link.** An idempotent is a pair (x, y) with
x ≠ 0 and y·x = 1. There are (2^7 − 1) 2^6 = 8128 such pairs. For each
pair the verifier forms p = off(x y^T). Pairs with p in H, or with p = 0,
are skipped. Each remaining pattern is adjoined to H. If the span contains
a matrix unit or has rank other than 5, it is discarded. Otherwise the
complete pool is enumerated by the same 8128-pair scan, the image rank is
computed, and, when that rank is 7, every nonzero vector of the image is
closed under the pool. The only pattern for which every closure has
dimension 7 is off((e2+e5+e6)(e2+e5+e6)^T).

This is an exhaustive census of one-idempotent extensions of these two
blocks at width 7. It is not, by itself, a census of every 5-dimensional
pattern space containing H. The reduction is as follows. If P contains H,
has dimension 5, and is unit-free, the quotient P/H is 1-dimensional, so
the patterns outside H are exactly one nonzero pattern p. The six block
images span the 6-dimensional space L ⊕ R. Joint image dimension 7
therefore requires a pool element whose image lies outside L ⊕ R, and that
element's pattern must be p. So p is realizable and is not a matrix unit.
The fiber lemma gives it one rank-one idempotent lift, which the census
has already tested. At width 7, with these two blocks fixed, the only
irreducible image of dimension 7 is the k = 1 witness. Squares that meet a
block in two or more coordinates are inside this census, because every
idempotent was visited, and none of them is irreducible of image dimension 7.

**Widths 8 and 9, every square.** A square link is z z^T with z·z = 1, so
z runs through the odd-weight vectors. There are 2^{W-1} of them: 128 at
width 8 and 256 at width 9. The same adjoining test is applied. The
irreducible image-7 hits are

```text
width 8:  e2+e5+e6,  e2+e5+e7
width 9:  e2+e5+e6,  e2+e5+e7,  e2+e5+e8,  e2+e5+e6+e7+e8.
```

These are exactly the Theorem 1 squares whose fresh coordinates are chosen
from the coordinates beyond B: one fresh coordinate, or, at width 9, all
three fresh coordinates. No square that meets a block in two or more
coordinates is an irreducible image-7 extension at these two widths. That
is a finite census, not a proof for every larger width, and it does not
include non-square idempotents x y^T with x ≠ y. The width-7 census does
include those non-squares, and finds none.

## 11. What this does not claim

The selected κ and its framework assumptions are unchanged. No rational
address, native word, supplier admission, or multiplication identity is
produced. The original card asks for a new register alphabet. That gate is
unmet. This is a scalar pattern-pool question, and the family expansion
gate is not a reason to start another construction round from this example.

The theorems do not say that every complete no-edge pool of pattern
dimension 5 has joint image at most 7. The zero-edge quotient bound of
#6782 still gives only dim V ≤ 2^5 − 1 = 31. Theorem 1 attains 7 and does
not exceed it. A search through links on two fixed blocks is not an upper
bound.

The theorems do not classify a pattern space that does not contain these
two blocks. They do not classify, at every width, a square whose support
meets A or B in two or more coordinates. Section 10 does that only for
squares at widths 8 and 9, and for every idempotent at width 7. They do
not classify non-square idempotent extensions at width 8 or more.

Question 1 of #7237, whether 7 is an upper bound, remains open. Question 2
of #7139, the coordinate classification at pattern dimension 4, is not this
result. The dimension-6 pools of #7221 are not these seven-projector pools.

## Open next questions

1. **Is 7 an upper bound at pattern dimension 5?** Does every complete
   no-edge pool of pattern dimension 5 have total joint image at most 7?
   The odd-fresh family shows that 7 is attained and that 6 is too small.
   The zero-edge quotient bound is still 31. The missing step is a
   one-dimensional extension of a pattern space of dimension 6, not another
   fresh set on these two blocks.

2. **Is there an irreducible image of dimension 7 whose pattern space
   contains no two disjoint normal-form blocks?** The width-7 census fixes
   the blocks. A pool that is not a coordinate permutation of any odd-fresh
   link would be a different coordinate class. The first step is to decide
   whether every irreducible image-7 pattern space of dimension 5 contains
   at least one normal-form triple. The Grassmannian of 5-planes in the
   42-dimensional space of 7×7 zero-diagonal matrices is not a feasible
   enumeration, so that decision needs a structural reduction.

3. **At width 8, does a non-square idempotent extension of these two blocks
   have irreducible image dimension 7?** The width-7 census says no
   non-square works at width 7. Width 8 has (2^8 − 1) 2^7 = 32640
   idempotents. This package did not enumerate them. The first step is the
   same complete-pool test used at width 7. A partial sample would not be
   that census.
