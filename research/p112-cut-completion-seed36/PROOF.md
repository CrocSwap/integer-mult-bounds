# A sharp completion bill for one P112 binary copy-channel interface

The fixed pairing matrix M is defined from the pinned P112 model in
`inputs/MODEL.json`. Root coordinates are doubled E8 roots. For live root
indices i,j its binary pairing is `1+(root_i dot root_j)/4 modulo 2`.
The parent row support is the co-star of root3 (tag7); the column support is
the full star of root0 (tag0). Thus M has 52 rows, 56 columns and rank7 over F2.

This proof concerns a named standalone binary interface, not a complex decoder
or an accepted supplier cost theorem. The incoming source bits are arbitrary.
The interpretation of these maps as actual complex copy records needs a
separate interface argument. No real/complex rank is inferred from F2 rank.

## Contract and quantities

For row/column subsets S,T, let `K=D_S M D_T`, with zero outside the selected
rectangle, and `E=M+K`. The sum of the two packets is the entire original
parent map. Two independent input families x,z request

```
(Kx, Ex),                 (K^T z, E^T z).
```

The receiver has no other source-dependent side information. Arbitrarily
shared preprocessing/encoding is allowed. All source-dependent information
must enter through the counted copy-channel cut; later direct source access
would be an additional operation. Initial outputs/helpers are independent
arbitrary dirt, so they supply no information about x,z.

Define the minimum information ranks

```
j_col = rank([K; E]) = rank([K; M]),
j_row = rank([K^T; E^T]) = rank([K^T; M^T]),
B(K) = j_col+j_row.
```

The equalities follow from an invertible output-row operation replacing E by
E+K=M. With no split, the two original packets Mx,M^Tz have total rank14.
Since x,z are independent, even joint encoding across both source families
has the block-diagonal rank B(K). For L independent bit lanes the image has
`2^(L B(K))` possibilities, so at least L B(K) bits are needed. Rank
factorization attains this information dimension. This is an information
minimum, not a zero-price claim for source reads, arithmetic or helper work.

**Theorem.** For every arbitrary rectangular restriction of exact rank
`r=1,...,6`, `B(K) >= 14+r`, and each bound is attained. Also `rank(E)>=7`, so
separately copying the cut and remainder costs at least `r+7` on one source
orientation. If both restricted factor spans lose rank, then

```
rank(E)=7+r,  j_col=j_row=7+r,  B(K)=14+2r.
```

## Corollary for two separately required bilinear kernels

The same dimensions are necessary for linear operand encoders that preserve
both bilinear values `x^T K z` and `x^T E z`, even when the receiving helper
uses an arbitrary decoder instead of reconstructing the full packets. If an
encoder A identifies x and x+u, correctness for every z forces
`u^T K=u^T E=0`. Thus `ker(A)` lies in the common left kernel and its rank is
at least j_row. The other operand requires at least j_col dimensions.

A joint linear encoder of (x,z) has the same lower bound. Its kernel must lie
in the common polarization radical of the two quadratic functions
`x^T K z` and `x^T E z`. This radical is exactly the direct sum of their common
left and right kernels, of codimension j_row+j_col; the functions also vanish
on it. The rank bound is therefore B(K), attained by separate rank encoders.
This corollary requires linear source compression. A joint nonlinear encoder
that already evaluates the two kernels is a different computation and cannot
be granted as free copy preprocessing. Requiring only their sum changes the
contract back to M and needs no extra information.

## Finite premise and its independent certificate

For every nonzero w in the seven-dimensional column space of M, the original
rows indexed by supp(w) have full rank7. There are exactly127 such codewords;
the primary replay checks each support directly. The transposed statement
holds for the seven-dimensional row space as well.

The independent replay verifies an equivalent premise: every pair of nonzero
codewords intersects. Minimum intersections are six roots for the column
space and eight for the row space. Indeed a support supp(w) would fail to
span the full rank if and only if another nonzero codeword vanished on that
support. All `2*127^2=32258` pairs are checked. These are complete finite
premises for this one input model, not statistical samples or a theorem for
other punctures or parents.

## Complement and intersection lemmas

If `rank(M[S,:])<7`, there exists a nonzero column-space word w vanishing on S.
Its support lies in the complement of S and, by the finite premise, the
original rows on that support span rank7. Hence `rank(M[complement S,:])=7`.
The transposed argument applies to a rank-lowering column restriction.

Suppose the row restriction loses rank. Any vector in both col(M) and col(K)
vanishes outside S, because K does. But M restricted to those complementary
rows has rank7, the same as M, so its kernel equals ker(M). The vector must
therefore be zero. Consequently

```
col(M) intersect col(K) = {0},   j_row = 7+r.
```

A rank-lowering column restriction similarly gives disjoint row spaces and
`j_col=7+r`. Both j quantities are always at least7 because their stacks
include M or M^T.

Write a rank factorization `M=XY`, with inner dimension7. If both X[S,:] and
Y[:,T] retained full rank7, K would retain rank7. Thus r<7 forces at least one
rank-lowering restriction. One j is 7+r, the other is at least7, proving
`B(K)>=14+r`. The untouched complementary original rows or columns appear
verbatim in E, giving `rank(E)>=7`.

If both factor spans lose rank, both row and column spaces of M,K are
disjoint. Factor M and K separately. Their concatenated left factors have
full column rank7+r, and their stacked right factors have full row rank7+r.
Their product is M+K, so E has rank7+r as claimed.

For sharpness, select r independent original rows, with all columns retained.
Then K has rank r; row(K) is contained in row(M), so j_col=7. The row restriction
loses rank, giving j_row=7+r. Explicit row sets for every r=1,...,6 are recorded
in EXPECTED.json. Their remainders have rank7.

The geometry premise is essential: for M=I7 and K=diag(I5,0), E has rank2
and both j quantities equal7. A generic rank-seven argument alone would not
establish this theorem.

## The high-coverage rank-five step

For any rank-at-most-five cut, let x,y be the restricted factor-span dimensions.
Sylvester's inequality gives `rank(K)>=x+y−7`. If x<=5, expand the rows to a
full codimension-two kernel slice and restore all columns. This dominates
frame coverage and remains rank at most five. The transposed case is analogous.
If x,y>=6, they must both equal6. Expand both sets to their full hyperplane
slices; their factor spans are unchanged, so rank remains at most five.

This is the completeness argument credited to woklerx's PR1445 and the
rank-six predecessor PR1347. Our independent census rebuilds all of its
candidate supports and geometry: 2,667 row planes, 2,667 column planes and
127*127 joint hyperplanes, 21,463 candidates in all. Of these, 13,335 have
rank at most five. One-sided maximum coverage is1020 rows /990 columns;
the joint maximum is1060 of the1260 orthogonal frames.

If an arbitrary rank-at-most-five cut covers more than1020 frames, neither
factor span can have dimension at most five. Therefore x=y=6. Its rank is
exactly five, both restrictions lose rank, and the previous lemmas force

```
rank(E)=12, j_col=j_row=12, B(K)=24.
```

This statement applies to arbitrary support subsets, not only canonical cuts.
The dominating-candidate argument is used for coverage only; it does not
assume completion cost is monotone under support expansion.

A row-only cut attaining1020 frames has B=19. The joint1060-frame cuts attain
B=24. Therefore the exact maximum coverage among rank-at-most-five cuts is
1020 when `19<=B_budget<24`, and1060 when `B_budget>=24`. No complete frontier
below19 is asserted. All384 canonical maximum-coverage cuts have the same
rank tuple `(K,E,j_col,j_row)=(5,12,12,12)`; separately copying K,E costs17
on one orientation.

## Literal dirty implementation and boundaries

For either split fork F=[K;E], factor `F=UV` over F2, with d=rank(F). Use d
arbitrarily dirty helper scalars h and arbitrarily dirty output y. The literal
word is

```
y += U h; h += V x; y += U h; h += V x.
```

It implements `y += F x`, preserves x and returns h exactly. Every nonzero
entry in U,V is one source-to-target XOR; no clean scratch, overwrite or
free coefficient multiplication is used. Reverse the entire gate list to
undo it. The same identity holds componentwise for every bit-lane length L.
Its exact arithmetic recurrence is

```
G_F(L) = (2 nnz(U)+2 nnz(V)) L.
```

GATES.json.gz records the explicit rank-optimal encoding/decoding matrices,
all gates, source labels and target labels for the seed-selected maximum cut.
The two orientations use12 dirty helpers each and have1200/1196 scalar XORs.
Both replay all348 independent source/helper/output columns. Exact source
access, writes, helper restoration, instruction access and data-head motion
are separately counted in the declared L=1 fixed-cell cost model. Arbitrary-L
tape layout, allocation, loop control, complex native adapters and recursive
supplier charges have not been instantiated.

This completed information audit cannot be promoted to a supplier moment or
an exponent result. Changing other parent terms, sharing data with other
parents, or requiring fewer packets changes the contract and is outside its
scope. The written proof and exact finite premises await human review; no
Lean multiplication theorem is claimed.
