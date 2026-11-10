# Total and irreducible joint image at pattern dimension 4

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
Predecessor arguments are cited in place and are not reproved, except for the
GL(3,2) census and the six-point census, which `verify.py` repeats.

This is a scoped proof, plus one exhaustive census of a 16-element vector
space and one exhaustive census of GL(3,2). It is not a new κ. The selected
frontier stays `781451/250000000`.

## 1. Statement

Work over F2. For a width W, write off(N) for the matrix N with its diagonal
deleted. Let P be a 4-dimensional space of zero-diagonal W×W matrices
containing no matrix unit. The complete no-edge pool is

```text
C(P) = {xy^T : y·x = 1, off(xy^T) is a nonzero element of P}.
```

Every element is a rank-one idempotent. Coordinate projectors have zero
pattern, so they are not in C(P). Write V(P) for the span of the images of
C(P). The action is reducible when some subspace 0 < W < V(P) is invariant
under every pool projector.

**Theorem.** dim V(P) ≤ 6. Whenever dim V(P) = 6, the action is reducible.
In particular, no such pool acts irreducibly on a joint image of dimension
6 or more.

Section 9 records three pools of total dimension 6, each reducible, and
rechecks the irreducible dimension-5 pool of #7094. Both bounds are therefore
sharp. The argument is for every ambient width. It uses that the pool is
complete, that P contains no matrix unit, and that dim P = 4. It does not
apply to a larger pattern space, to a pool that contains a matrix unit, or
to an incomplete subset of projectors.

## 2. Inherited ingredients

**Fiber lemma (#5921).** A realizable nonzero off-diagonal pattern has one
rank-one idempotent lift, except a matrix unit, which has two. In a no-edge
pool the lifts are unique, so distinct pool projectors have distinct patterns.

**Lemma 3 (#6838).** Let N_i = x_i y_i^T for 1 ≤ i ≤ 5 have linearly
independent images. If N_1+N_2+N_3 and N_1+N_4+N_5 are both diagonal, then
N_1 is a coordinate projector. The proof does not use idempotence. A
coordinate projector has pattern 0, so this configuration cannot occur among
five pool patterns.

**Support lemma for a diagonal sum.** Let N_i = x_i y_i^T, 1 ≤ i ≤ k, have
independent images, and let D = N_1+...+N_k be diagonal. Write U for the
span of the images and X for the isomorphism F2^k → U sending the standard
basis vector ε_i to x_i. For each ambient coordinate b, let m(b) in F2^k
have components m(b)_i = y_i(b). Column b of D is X m(b), hence is 0 or e_b.
Thus m(b) = 0 whenever e_b is not in U, and whenever e_b is in U the vector
m(b) is 0 or X^{-1}e_b. The coordinates with m(b) ≠ 0 form the active set A.
The corresponding e_b are independent and lie in U, so |A| ≤ k. Each
covector is

```text
y_i = sum_{b in A} μ(b)_i e_b,        μ(b) = X^{-1}e_b.
```

Pairing against the images gives sum_i y_i·x_i = |A| mod 2. This identity is
the same one used for triples in #6921.

**Triples (#6921, recomputed below).** An independent-image zero-sum triple
in a no-edge pool has odd active-set size, so |A| is 1 or 3.

If |A| = 1, every covector equals the same e_c, every image has bit c, and
the three patterns are u e_c^T for the three nonzero vectors u of a
2-dimensional space T supported off coordinate c. Every nonzero vector of T
has weight at least 2. This is a **column triple**. Its images span
span(e_c)+T, which is 3-dimensional, and its patterns are exactly the three
nonzero elements of Q = {u e_c^T : u in T}.

If |A| = 3, the three active basis vectors lie in U, so after renaming
coordinates U is the coordinate space on a 3-set A. The images are a basis
of U and the covectors are the dual basis. The verifier enumerates all 168
elements of GL(3,2). Exactly 18 have all three pattern weights at least 2.
Each of those 18 has column weights 2, 2, 3, the weight-3 column is
self-dual, and the two weight-2 columns are dual to each other. F2^3 has a
unique weight-3 vector and three weight-2 vectors, and those three sum to
zero, so an invertible matrix cannot have three weight-2 columns. Thus every
survivor is a coordinate permutation of

```text
u = e_1+e_2,   v = e_0+e_2,   o = e_0+e_1+e_2,
N_u = u v^T,   N_v = v u^T,   N_o = o o^T.
```

This is a **normal-form triple**. Its three patterns are the nonzero
elements of a 2-dimensional space supported on the off-diagonal positions of
the coordinate block, and its covectors are a basis of the dual of that
block. There are 3 choices for the weight-3 column and 3·2 ordered choices
for the two weight-2 columns, hence exactly these 18 matrices.

## 3. Six patterns in a four-dimensional space

The nonzero vectors of P form a copy of F2^4 minus the origin, a set of 15
points. Any six pool projectors with independent images contribute six
distinct points. A three-term zero sum in this set is a **triple**. A
four-term zero sum is a **quad**. The verifier classifies all C(15,6) = 5005
six-point subsets:

| type | count | shape |
| --- | ---: | --- |
| meet-1 | 2625 | two triples meeting in one point |
| cap | 420 | no triple, and exactly three quads |
| one triple | 1680 | exactly one triple and exactly one quad |
| two triples | 280 | exactly two triples, they are disjoint, and there is no quad |

Nothing else occurs. A zero sum of patterns makes the corresponding sum of
projectors diagonal, because the off-diagonal parts cancel.

A meet-1 six-set contains five patterns to which Lemma 3 applies: the five
images are independent, and the two triples give the two diagonal sums in
that lemma. The shared projector would be coordinate, so its pattern would
be zero, but the shared point is nonzero. A meet-1 set of pool patterns is
therefore impossible.

## 4. Active sets of a diagonal quadruple

Let four pool projectors have independent images and a diagonal sum. Section
2 gives an active set A of even size: four idempotent pairings sum to 0, and
A is nonempty because the covectors are nonzero. Also |A| ≤ 4. Thus |A| is
2 or 4.

The four patterns are distinct, nonzero, and sum to zero, so they span a
space Q of dimension exactly 3. A 2-dimensional space has only three nonzero
vectors. Since dim P = 4, Q is a hyperplane of P. Call patterns in Q even
and the other coset odd.

## 5. Active set 4 forces total dimension at most 5

Let |A| = 4, and rename A = {0,1,2,3}. The four basis vectors e_b lie in the
image span U, so U is that coordinate 4-space. The diagonal sum is the
coordinate projection onto U, and it acts as the identity on U. Expanding
each image in the projector basis shows that the Gram matrix is the
identity: the covectors are the dual basis, supported on U. Every pattern is
supported in the off-diagonal U-block, and both columns of every matrix in Q
lie in U.

**Even images lie in U.** An even pattern has no entry outside the block. If
its lift xy^T had an outside image bit, the outside row would force the
inside covector to vanish; an outside covector bit would force the inside
image to vanish. Either alternative kills the inside pattern. The pattern
also has no outside entries, so it would be zero. Thus every even image lies
in U.

**Odd images add at most one dimension.** Every odd pattern has the same
entries outside the block. Write γ_t for the inside part of outside column
t, and write R_t for the inside part of outside row t.

*Some inside-facing outside column is nonzero.* Then every odd lift has
y_t = 1 and the same inside image ξ, the common nonzero column. For every
outside coordinate u, the inside part of column u is y_u ξ. That part is
fixed, and ξ ≠ 0, so every outside covector bit is fixed: y_u = 1 exactly
on the nonzero outside columns, and those columns all equal ξ. At least one
such bit s is 1. Entries of an outside row against outside columns other
than its own diagonal pin every outside image bit except possibly bit s.

If a second outside covector bit is 1, bit s is pinned as well and there is
one odd image. If y_s is the only outside covector bit and some other
outside image bit is already 1, the shared outside row at that bit fixes
the inside covector, and idempotence y_U·ξ + x_s = 1 selects exactly one
value of the remaining bit. If instead every pinned outside image bit is 0,
the two candidates are ξ and ξ+e_s: the value x_s = 1 forces the inside
covector to equal the shared row at s, and x_s = 0 keeps the image inside
U. In every branch the odd images lie in U+span(e_s). The joint image has
dimension at most 5.

*Some outside row is nonzero and every outside column is zero.* A nonzero
row R_t forces x_t = 1 and forces every odd lift to share the inside
covector R_t. Because that covector is nonzero, every outside image bit is
pinned by the shared rows. The inside image still lies in U, so every odd
image lies in one coset of U. The joint image has dimension at most 5.

*Every inside-facing outside row and column is zero, but some
outside-outside entry is 1.* A lift then has x_t = y_s = 1 for two outside
coordinates, which forces both the inside image and the inside covector to
vanish. The inside pattern is zero. At most one odd pattern has inside part
zero, and the fiber lemma gives it one lift. One extra image keeps the
joint dimension at most 5. If no odd pattern has inside part zero, there is
no odd lift at all.

*No outside entries.* The odd coset is supported in the block, and the same
argument used for even patterns puts every odd image in U.

## 6. Active set 2 forces total dimension at most 5

Let |A| = {0,1} after renaming. Every one of the four covectors is supported
on {0,1}, and e_0 and e_1 both lie in the image span U. The four patterns
and therefore all of Q are supported on columns {0,1}. As in Section 5, both
columns of every matrix in Q lie in U: column 0 of projector i is the
corresponding scalar times x_i with bit 0 cleared, and e_0 is in U.

**Even images lie in U.** Let xy^T be an even lift. For c ≥ 2, column c of
the pattern is zero, so either y_c = 0 or x = e_c. If x = e_c, idempotence
forces y_c = 1, and the pattern is the off-diagonal part of row c. That row
meets only columns {0,1}, and its weight is at least 2, so the pattern is
E_{c0}+E_{c1}. Its column-0 vector is e_c, which lies in U, so the image
e_c lies in U. Otherwise y is supported on {0,1}. Then y_0 = 1 or y_1 = 1,
and the corresponding column equals the image with one diagonal bit cleared.
That column lies in U and the cleared basis vector lies in U, so the image
lies in U.

**Odd images.** Outside columns of every odd pattern agree. If two outside
columns are nonzero, both covector bits are 1 and the two columns pin every
coordinate of the image, including each other's diagonal bits. There is at
most one odd image, and the joint dimension is at most 5.

Suppose exactly one outside column, γ at coordinate c ≥ 2, is nonzero.
Every odd lift has y_c = 1 and its image on the affine line γ+span(e_c).
An affine line over F2 has two points. One odd image adds at most one
dimension. If both points x and x+e_c occur, their patterns differ by an
element of Q, so the difference of each of columns 0 and 1 lies in U.

- If both lifts have y_0 = 1, that column difference is e_c, hence e_c is in
  U. Both images then lie in U+span(x).
- If both have y_0 = 0 and both have y_1 = 1, the same holds for column 1.
- If both have y_0 = y_1 = 0, every extra covector bit d ≠ c sees a zero
  column, so the image is a coordinate vector. Combined with y_c = 1 this
  makes γ a coordinate vector, and the pattern is a matrix unit. That is
  excluded. The only remaining covector is e_c. Idempotence holds for exactly
  one of the two points on the line, so both points cannot occur.
- If the two lifts differ on bit 0 of the covector, the lift with y_0 = 1
  has its column-0 vector in U, so its image is in U. Both images then lie
  in U+span(e_c).

The symmetric bit-1 subcases are the same. Thus the joint dimension is at
most 5.

Finally suppose no outside column is nonzero, so every pattern in P is
supported on columns {0,1}. Write σ_0 and σ_1 for the two columns of one odd
representative.

- A lift with outside covector bit c has image e_c and pattern E_{c0}+E_{c1}.
  If that pattern is even, e_c is in U as above. If it is odd, e_c lies in
  σ_0+U. Every such image therefore lies in U+span(σ_0).
- A lift supported on {0,1} with both covector bits 1 has the two columns
  equal to the same image with one bit cleared, so σ_0+σ_1 is in U. The
  image itself lies in σ_0+U. Any other odd lift with y_0 = 1 has the same
  shape. A lift with y_0 = 0 and y_1 = 1 has zero column 0, which forces
  σ_0 into U, and its image lies in σ_1+U = U.
- If every odd lift has y_1 = 0, column 1 of that lift is zero, so σ_1 is in
  U, and the images with y_0 = 1 lie in σ_0+U.
- If some odd lift has y_0 = 0 and y_1 = 1, the same reading puts σ_0 in U
  and every image in σ_1+U.

In every branch the odd images lie in a single coset of U. The joint
dimension is at most 5.

## 7. Two triples

Now suppose six independent images have patterns forming two disjoint
triples, and dim P = 4. Section 2 says each triple is a column triple or a
normal-form triple. Each pattern space is 2-dimensional. Two distinct
2-dimensional spaces of patterns with six distinct nonzero vectors intersect
trivially and span a 4-dimensional space: a nontrivial intersection would
leave at most five nonzero patterns. Thus P is the direct sum of the two
pattern spaces.

**Both column triples, different columns c and d.** The summands occupy
different columns, so every pattern in P has the form u e_c^T + v e_d^T
with u in the first T-space and v in the second. If a lift had a covector
bit b outside {c,d}, column b would be zero, so the image would be e_b.
Column c would then be a scalar times e_b. The first T-space contains no
weight-1 vector, so that scalar is zero, and the same holds for column d.
The pattern would be zero. Every covector is therefore supported on {c,d}.

The two image spaces are 3-dimensional. Six independent images force their
sum to be 6-dimensional and their intersection to be zero, so dim V(P) ≥ 6.
A lift with covector e_c has image in the first image space, and likewise
for e_d. A lift with covector e_c+e_d is pinned by both columns, so its
image lies in each image space. No image leaves the 6-dimensional sum.
The two covectors that appear span a space of dimension at most 2, so their
common kernel meets V(P) in dimension at least 4. That kernel is nonzero,
proper, and invariant. The action is reducible, and dim V(P) = 6.

**Both column triples, the same column.** All six patterns lie in one
column. Six distinct patterns force the two T-spaces to span a
4-dimensional space, so P consists entirely of column-c matrices. Every
lift has covector e_c, and every image lies in span(e_c) plus that
4-dimensional space, which has dimension 5. This cannot contain six
independent images. The same-column subcase does not occur under the
dimension hypothesis of this section. The same estimate shows that a
single-column no-edge pattern space of dimension 4 has total image at most
5, which is used only as a consistency check.

**Both normal-form triples.** Each image space is a coordinate 3-space. Six
independent images force the two 3-sets of coordinates to be disjoint, and
the image span to be their 6-dimensional coordinate sum. The pattern supports
are the off-diagonal positions of the two blocks, which are disjoint.

A sum of one nonzero pattern from each block is not realizable. Such a sum
has an entry inside each block and no cross entry. A rank-one off-diagonal
pattern is a combinatorial rectangle with the diagonal removed. If the
rectangle meets both blocks internally, its row support and column support
both meet both blocks, so it has a cross entry. The displayed sum does not.
Thus the complete pool is exactly the six projectors.

Each block's covectors are supported on that block, so they kill the other
image space. Each 3-dimensional image space is invariant. The action is
reducible, and dim V(P) = 6.

**One column triple and one normal-form triple.** Let the column be c and
the normal-form coordinates be A. The column image space contains e_c. If
c were in A, the two image spaces would meet nontrivially and could not
contain six independent images. Thus c is outside A, the pattern supports
are disjoint, and P is their direct sum.

Every pattern has nonzero columns only in {c}∪A. An outside covector bit
would force a coordinate image and then, as in the two-column argument, a
zero pattern: the column-c part would have weight at most 1, and the
normal-form part would be a single row outside A, while every nonzero
normal-form pattern has two or three rows inside A. Covectors are supported
on the four coordinates A∪{c}.

A lift with covector e_c has image in the column image space. A lift whose
covector is supported on A has no column-c pattern, so it realizes a
normal-form pattern and its image is in the coordinate space A. A mixed
covector has column c equal to some u in the T-space, which pins the image
into span(e_c)+T. Every image lies in a sum of two 3-dimensional spaces.
Six independent images make that sum exactly 6-dimensional, so
dim V(P) = 6. The covectors span a space of dimension at most 4, and the
common kernel in V(P) has dimension at least 2. The action is reducible.

## 8. Assembly

If dim V(P) ≤ 5 there is nothing to prove for the upper bound. Suppose
dim V(P) ≥ 6, and choose six pool projectors with independent images.
Section 3 says their patterns are not a meet-1 set. If they formed a cap or
a one-triple set, they would contain a quad. Sections 4 through 6 would
give dim V(P) ≤ 5, a contradiction. The only remaining type is two disjoint
triples.

Section 7 shows that every such pool has dimension exactly 6 and is
reducible. Dimension greater than 6 is therefore also impossible. This is
the theorem.

The same chain shows a little more about dimension 6: every six independent
images come from two disjoint triples, and the pool is one of the three
realizable geometries in Section 7. The package does not classify those
geometries up to coordinate permutation.

## 9. Sharpness

The bounds are attained. None of these examples moves κ.

**Total dimension 6, reducible.** On coordinates {0,1,2} and {3,4,5}, the
two normal-form triples have pattern dimension 4, no matrix unit, and
complete pool equal to the six projectors at every width at least 6. The
joint image is the coordinate 6-space. Each block is invariant, while the
six covectors span the dual, so the common kernel is trivial. Reducibility
here is the block decomposition, not a common kernel.

Two column triples also attain dimension 6. Take column 0 with
T = span(e_1+e_2, e_1+e_3) and column 4 with T = span(e_5+e_6, e_5+e_7).
The pattern space is 4-dimensional and unit-free, the pool has six
projectors, the image has dimension 6, and every covector is e_0 or e_4.
The common kernel has dimension 4.

A mixed pair attains dimension 6 as well: the normal form on {0,1,2} and
the column triple at column 3 with T = span(e_4+e_5, e_4+e_6). The pool has
six projectors, the image has dimension 6, and the covectors span a
4-dimensional coordinate space. The common kernel has dimension 2.

`verify.py` rebuilds each pool at the widths named in its checks, including
one width with a spare coordinate, and checks the invariant subspaces. The
normal-form pair is also checked by enumerating the subspace lattice of its
64-element image. These scans certify the three witnesses. They are not a
search over all 4-dimensional pattern spaces; Section 7 is what bounds
every pool.

**Irreducible dimension 5.** #7094 gives five projectors on coordinates
{0,1,2,3,4}:

```text
(e_0+e_2)(e_1+e_2)^T,
(e_1+e_2)(e_0+e_2)^T,
(e_0+e_1+e_2)(e_0+e_1+e_2)^T,
(e_2+e_3)(e_0+e_1+e_3)^T,
(e_0+e_2+e_3+e_4)(e_1+e_4)^T.
```

The verifier recomputes that pattern space: dimension 4, no matrix unit,
complete pool equal to these five projectors at widths 5 through 8, joint
image of dimension 5, and no proper invariant subspace in the 32-element
image. Deleting the last projector leaves a proper invariant subspace, so
the lattice scan is not hard-wired to one answer. The dimension-5
irreducibility is #7094's theorem; this package only rechecks the witness
that shows 5 cannot be replaced by a smaller universal number. The new
statement is the matching upper bound.

## 10. What this does not claim

The selected κ and its framework assumptions are unchanged. No rational
address, native word, supplier admission, or multiplication identity is
produced. The result does not bound pattern dimension 5 or more, and it
does not say that a pool containing a matrix unit has total image at most
6. An incomplete subset of a pool can fail to be invariant on a subspace
that the complete pool preserves; the theorem uses completeness.

The census in Section 3 is exhaustive because its domain is the 15 nonzero
vectors of F2^4. The GL(3,2) count is exhaustive because every ordered basis
of F2^3 appears once. A search that found no further example would not have
been a proof. The width scans certify the four explicit pools only.

Question 1 of #6921, paid-rank accounting after a relation split, is not
answered here. The original card still asks for a new register alphabet;
that gate is unmet.

## Open next questions

1. **Pattern dimension 5.** Does a complete no-edge pool of pattern
   dimension 5 still have total joint image at most 6, and can its
   irreducible image exceed 5? The parity construction one dimension higher
   has total image 6, and the edge-quotient bound only gives 31. The first
   step is one explicit unit-free pattern space of dimension 5 whose
   complete pool has image rank 7, or a support argument that still caps
   the image at 6. The four-dimensional census does not carry over: F2^5
   has more than six nonzero vectors, and the quad lemmas use a
   3-dimensional hyperplane.

2. **Coordinate classification at dimension 6.** Is every dimension-6 pool
   a coordinate permutation of one of the three Section 9 witnesses? The
   dimension bound does not need that list. The first step is to match the
   two T-spaces, or the two normal-form blocks, to a fixed pair of
   coordinate sets. Nothing in the case split is blocked; the missing piece
   is the bookkeeping.

3. **Paid rank.** After a valid relation, cube-span, and coordinate-call
   split, does irreducible dimension at most 5 change a three-relation
   paid-rank obstruction? This is still question 1 of #6921. The scalar
   bound does not by itself price a word. The split hypotheses are not
   proved in this package.
