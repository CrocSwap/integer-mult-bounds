# Unequal scalar pivots and a prescribed product

This proof was produced by Nick Petalas. Apache-2.0.

Let K be any field and prescribe distinct nonzero p,q in K and h in K.
For commuting idempotents P,Q with P11=p, Q11=q and (PQ)11=h, the least
ambient dimension for Schur-commutator rank two is

```text
N(p,q,h) = 3 + [h in {0,p,q}] + [1-p-q+h != 0].              (1)
```

Brackets denote indicators of field equalities or inequalities. Every minimum
is attained. The hypothesis p!=q is essential. This answers Open next question
1 of Nick Petalas's #4771, whose equal-pivot theorem is a predecessor, not
part of the new claim. The sector construction follows ssafwann's #4671 and
Nick Petalas's #4746/#4771; the scalar factorization follows #4278.

## Four sectors

Let i:K -> V be coordinate inclusion and pi:V -> K coordinate projection.
Write E00=(I-P)(I-Q), E10=P(I-Q), E01=(I-P)Q and E11=PQ.
Their images Vj form a direct sum. Put Yj=Ej i and Xj=pi restricted to Vj.
The four scalar products are

```text
t00=1-p-q+h,    t10=p-h,    t01=q-h,    t11=h.              (2)
```

Conversely, any four pairs of maps Xj,Yj with these products give pi i=1,
since the products sum to 1. On their direct sum, take the diagonal
projectors with sector eigenvalues 00,10,01,11. Choosing the first basis
vector to be i(1) and the remaining vectors in ker pi realizes the prescribed
coordinate entries. Thus sector constructions give actual full matrices.

## Exact independence criterion

The cited scalar factorization, valid for arbitrary nonzero p,q, uses

```text
A = [PQ i - (h/q)Q i, P i/p - Q i/q],
B = [pi P/p - pi Q/q; -pi PQ + (h/q)pi Q].
```

Here pi A=0 and Bi=0. In coordinates V=i(K) direct-sum ker pi, AB induces
the Schur commutator on ker pi. Its rank is two exactly when A and B both
have rank two. A rank-two A is injective and a rank-two B is surjective;
Bi=0 means B restricted to ker pi remains surjective.

On each sector, A equals Yj times a row aj, and B equals a column bj times
Xj, as follows:

```text
sector   aj                                      bj
00       (0,0)                                   (0,0)^T
10       (0,1/p)                                 (1/p,0)^T
01       (-h/q,-1/q)                             (-1/q,h/q)^T
11       ((q-h)/q,(q-p)/(pq))                    ((q-p)/(pq),-(q-h)/q)^T
```

Each bj is the same invertible rotation of aj, namely (a2,-a1)^T.
Therefore the independence relations for A and B are identical, with Yj
and Xj respectively deciding whether a direction occurs. The determinants
of the pairs of rows are

```text
det(a10,a01)=h/(pq),
det(a10,a11)=-(q-h)/(pq),
det(a01,a11)=(p-h)/(pq).                              (3)
```

All three rows are nonzero because p,q are nonzero and distinct.

If h is outside {0,p,q}, all three active products t10,t01,t11 are nonzero.
Both maps in each sector are nonzero, and (3) guarantees independent
directions. These three sectors each require one dimension.

If h=0, sectors 10 and 01 have nonzero products but parallel directions.
Sector 11 has zero product and its direction is independent of both.
Consequently rank two for both factors is equivalent to X11 and Y11 both
being nonzero. This sector requires two dimensions, in addition to the
one-dimensional sectors 10 and 01.

If h=p, sectors 01 and 11 have nonzero products but parallel directions.
The independent direction is sector 10, whose product vanishes. Both
X10 and Y10 must be nonzero. The required dimensions are again 1+1+2.

If h=q, the same argument uses nonzero-product sectors 10 and 11 and
zero-product sector 01. Both X01 and Y01 must be nonzero. These cases
are disjoint because p and q are nonzero and distinct.

Sector 00 has no effect on either rank. Its product t00 requires exactly
one dimension when nonzero and can be omitted otherwise. Adding its
contribution gives the lower bound (1).

## Attainment

A nonzero scalar product t is realized in dimension one by Y=(1), X=(t).
A zero product for which both maps must be nonzero is realized in dimension
two by Y=(1,0)^T, X=(0,1). Omit every other zero-product sector.
These choices attain every sector lower bound above. Their products sum to
1, so the coordinate construction following (2) applies. The independence
conditions hold, hence the Schur commutator has rank two. This proves (1)
over every field.

For example, over F3, p=1,q=2 gives dimensions five, five and four at
h=0,1,2 respectively. Over F5, p=2,q=3,h=4 gives dimension three.
The equal-pivot rule cannot be reused: at h=p with p!=q it is just one
zero-product sector, rather than the two required when p=q=h.

This is a scoped algebraic theorem about one-coordinate Schur complements.
It gives neither a header frequency nor a paid physical implementation.
