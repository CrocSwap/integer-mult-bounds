# A rank-nine obstruction after each hyperplane removal

Let R be the 120 E8 root lines. A binary fitting matrix F has F(r,r)=1.
For distinct roots r,s with r dot s nonzero, it has F(r,s)=0. Entries for
orthogonal roots are free. The matrix need not be symmetric.

For every linear hyperplane H through the origin, the fitting matrices
on R outside H have binary rank at least nine. The finite part of this
statement uses eight certificates in `../quick.json`. Each certificate
has thirteen root lines. `independent_check.py` checks each certificate
with integer arithmetic. It also checks the simple-root basis and the
root counts. `INDEPENDENT.json` records the result and the input hash.

## The thirteen-root certificate

The first eight roots are pairwise nonorthogonal anchors. Their fitting
block is the identity I8. Each of the five other roots is a witness for a
distinct pair of anchors. It is orthogonal to exactly those two anchors.
The five pairs use only four anchor indices. Witnesses for incident pairs
are nonorthogonal.

Suppose the fitting matrix on these thirteen roots has rank at most eight.
Write it in block form as [[I8,B],[C,D]]. The Schur complement gives D=CB.
For the witness for e={i,j}, its column in B and its row in C have support
contained in {i,j}. Its diagonal entry gives

    C[e,i] B[i,e] + C[e,j] B[j,e] = 1.

Over F2, exactly one product is one. Assign the pair to that endpoint.
If two incident pairs e,f are assigned to their common endpoint i, then

    (CB)[e,f] = C[e,i] B[i,f] = 1.

Their witnesses are nonorthogonal, so D[e,f] must be zero. This is a
contradiction. Each of the four endpoints can receive at most one pair.
There are five pairs. Thus the fitting rank is at least nine.

## The eight maximal parabolic subsystems

Use the simple roots in `../quick.json`. Their Dynkin edges are
1-3, 2-4, 3-4, 4-5, 5-6, 6-7, and 7-8. All roots are scaled by two.
Delete one simple root at a time. The types and root-line counts are:

| Deleted node | Type | Root lines |
| --- | --- | ---: |
| 1 | D7 | 42 |
| 2 | A7 | 28 |
| 3 | A6+A1 | 22 |
| 4 | A4+A2+A1 | 14 |
| 5 | A4+A3 | 16 |
| 6 | D5+A2 | 23 |
| 7 | E6+A1 | 37 |
| 8 | E7 | 63 |

For each row, its certificate has all thirteen roots outside the span of
the retained seven simple roots. The normal in the input is orthogonal
to those seven roots and has nonzero inner product with the deleted root.
Thus each of the eight complements has fitting rank at least nine.

## All hyperplanes

Write H=v-perp, where v is nonzero. A Weyl transformation puts v in the
closed dominant chamber. In that chamber each simple-root inner product
is nonnegative. A positive root is a sum of simple roots with nonnegative
integer coefficients. Its inner product with v is zero exactly when each
simple root in its support has zero inner product with v.

Thus the roots in H form a standard parabolic subsystem after that Weyl
transformation. Since v is nonzero and the simple roots span the ambient
space, at least one simple-root inner product is positive. Delete such a
node. The roots in H lie in the rank-seven subsystem for that deletion.
The complement of H therefore contains the complement of that subsystem.
Fitting rank cannot decrease when more vertices are present, since the
smaller fitting matrix is a principal submatrix. Weyl transformations
preserve orthogonality. The eight finite certificates now give the claim.
This argument also applies to real hyperplanes.

## Consequence for rank-nine fitting matrices

Let F be a fitting matrix on all 120 roots, with binary rank nine. For a
proper hyperplane H, let O be the indices outside H. The principal matrix
F[O,O] has rank at least nine, and hence exactly nine. The rows F[O,*]
therefore span the complete row space of F. The columns F[*,O] span the
complete column space.

If a column-space vector Fu has support in H, then F[O,*]u=0. Since those
rows span all rows, Fu=0. Apply the transpose argument to the row space.
Consequently, every nonzero vector in either space has support with
rational span dimension eight. In particular, a rank-nine factorization
cannot have a nonzero factor row or column with support rank at most seven.
This does not rule out factorizations with more than nine factors.
