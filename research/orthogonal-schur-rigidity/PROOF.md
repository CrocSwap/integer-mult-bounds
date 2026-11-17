# Orthogonal Schur dilation rigidity

This contribution was produced by Nick Petalas. Apache-2.0.

The claim is a scoped finite-dimensional theorem over R or C. The positive
Gram-isometry argument is the classical uniqueness argument for a minimal
positive-operator dilation. The contribution is its explicit application to
the prescribed-pivot Schur interface, including the entire residual pair.
No literature-wide priority claim is made.

## Statement

Fix d >= 1 and Hermitian d-by-d matrices A,B,H, with A and B invertible.
Define

```text
T00 = I-A-B+H,  T10 = A-H,  T01 = B-H,  T11 = H.
n0 = sum_j rank(Tj).
```

There exist commuting orthogonal projections P,Q on K^n with
P11=A, Q11=B and (PQ)11=H if and only if all four Tj are positive
semidefinite and n >= n0. Here K is R or C and the first d coordinates
carry the usual positive definite inner product. In particular A and B
are positive definite whenever these conditions hold.

For every such realization form the usual Schur complements

```text
S = P22-P21 A^-1 P12,  Z = Q22-Q21 B^-1 Q12.
```

There is an ordered pair (S0,Z0) on dimension n0-d, determined up to
simultaneous unitary equivalence by A,B,H alone, such that

```text
(S,Z) is unitarily equivalent to
(S0,Z0) plus k00 copies of (0,0), k10 copies of (1,0),
             k01 copies of (0,1), k11 copies of (1,1),
kj = rank(Ej) - rank(Tj).
```

The Ej are the projections onto the four original joint sectors. Consequently the
commutator [S,Z], its rank, every nonzero singular value, and every
nonzero eigenvalue are independent of all four padding dimensions.
At each n >= n0 there is exactly one possible commutator rank for these
fixed compressed matrices in the orthogonal class. This is a restriction
of the oblique problem, not a competing formula for its rank frontier.

## Proof

Let i:K^d -> K^n be the coordinate isometry. For commuting orthogonal
projections the four mutually orthogonal projections are

```text
E00=(I-P)(I-Q), E10=P(I-Q), E01=(I-P)Q, E11=PQ.
Yj=Ej i,       Yj*Yj=Tj.
```

This gives positivity and rank(Ej) >= rank(Tj). Their sum gives n >= n0.
For sufficiency use the Hilbert space Vj=range(Tj), and regard Tj^(1/2)
as a map from K^d into Vj. Stack these four maps into i0. Since sum Tj=I,
i0*i0=I. On the direct sum of the Vj define the diagonal projections

```text
P0=diag(0,I,0,I), Q0=diag(0,0,I,I).
```

Their three compressions are A,B,H. Complete i0 to an orthonormal basis
to put it in the first d coordinate positions. This realizes n0. Add
00-sector dimensions to realize every larger n. Square roots and this
basis completion are existence operations over R or C; a rational
orthonormal realization at n0 is not asserted.

For any realization set Cj=range(Yj) and C=orthogonal direct sum Cj.
Then dim C=n0 and i(K^d) is contained in C, because i=sum Yj. Each
original sector splits orthogonally as Cj plus an inactive subspace Kj.
Both C and its orthogonal complement reduce P and Q. On Kj the ordered
pair is the corresponding scalar pair j.

If Yj and Yj' come from two realizations with the same Tj, the rule

```text
Uj(Yj x)=Yj' x
```

is well-defined: both squared norms equal x*Tj x, so their kernels
agree. Polarization shows that Uj preserves the inner product. It is
onto Cj' by definition. Their orthogonal direct sum U:C -> C' is unitary,
intertwines both P and Q, and satisfies Ui=i'. This proves uniqueness
of the core as a dilation fixing the observed coordinates pointwise.

It remains to show that the same decomposition survives Schur deletion.
On the whole ambient space put

```text
Phat=P-Pi A^-1 i*P, Qhat=Q-Qi B^-1 i*Q.
```

Pi A^-1 i*P is the orthogonal projection onto range(Pi): it is
self-adjoint, its square equals itself using i*Pi=A, and it is the
identity on range(Pi). This range lies inside range(P). Thus Phat is
also an orthogonal projection, and it kills i(K^d). The same holds for
Qhat. In the original coordinates they are diag(0,S), diag(0,Z).

Both correction terms have range in C and vanish on C-perp. Therefore
on C-perp the lifted pair remains the original commuting scalar pair.
On C, U intertwines the correction terms because it intertwines P,Q
and fixes i. Restricting to C intersect i(K^d)-perp gives the unique
pair (S0,Z0). Each Kj already lies in i(K^d)-perp. These orthogonal
subspaces exhaust the residual space and prove the displayed decomposition.
Its commutator is [S0,Z0] plus a zero matrix, proving all consequences.

## Scalar specialization

For d=1 write A=a>0, B=b>0, H=h. Feasibility says

```text
max(0,a+b-1) <= h <= min(a,b).
c = (a-h)(b-h)/(ab).
```

The forced Schur-commutator norm is sqrt(c(1-c)). Its rank is two when
0<h<min(a,b), and zero otherwise. These statements hold in every
admitted ambient dimension.

For the strict interior case the core has one line in each active
sector. In sector coordinates, the residual P line and Q line are
spanned by the unit vectors

```text
u=(sqrt(h)e10-sqrt(a-h)e11)/sqrt(a),
v=(sqrt(h)e01-sqrt(b-h)e11)/sqrt(b).
```

Their squared inner product is c. Two unit-vector projections with
squared overlap c have commutator eigenvalues +i sqrt(c(1-c)) and
-i sqrt(c(1-c)) on their joint span. This follows by using u and the
normalized component of v perpendicular to u as a basis. The remaining
coordinates contribute zero. At h=0 the two original active sectors
are disjoint and both core Schur projections vanish. At h=a or h=b
one of the core Schur projections vanishes. This proves the boundary
cases without dividing by a vanished sector vector.

For example a=1/2, b=2/3, h=1/6 gives c=1/2, n0=3 and norm exactly 1/2.
The exact rational fixture realizes these effects in dimension eight;
its core has dimension three. Padding cannot change its two nonzero
commutator singular values. With a=b=h=1 the core has dimension one
and every orthogonal Schur pair commutes, regardless of padding. The
unrestricted maximal-rank formula of #5128 permits rank two at n=5
for those same compressed scalars. Self-adjointness is therefore a
material restriction on that interface.

## Dependencies and limits

Krzysztof Wojt's #5128 supplies the prescribed A,B,H interface, the four
sector compression products and the unrestricted maximal-rank result.
Nick Petalas #6031 and apoursh #6053 already settle the unrestricted
rank/dimension trade-off; it is not an open claim here. The wider ordered
Schur and sector lineage is retained in those packages. This proof uses
the classical positive Gram uniqueness argument rather than their
oblique subspace enumeration or extremal constructions.

The result does not cover indefinite inner products, merely symmetric
projections without conjugation over C, arbitrary idempotents, singular
pivots, approximate compressions, or rational minimum-dimension
orthonormal realizations. No actual selected header is proved to have
this self-adjoint contract. Producer/consumer costs, restoration, native
realization, precision, stock, compiler and outer transfer remain separate.
This is not a new kappa or a complete multiplication theorem.
