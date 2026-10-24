# The reciprocal family and its sharp blockwise restrictions

Let n be an integer with n>=5. Put m=n-4 and k=n-2. Over the real
numbers, or over a characteristic-zero subfield, define

```text
u=(1^k,m,0)^T,       ell=(-1^k,1,0),
R=I+u ell,           P=diag(I_k, swap),
E=P R.
```

Then R^2=I, E^-1=R P, and both E and E^-1 have zero diagonal.
The displacement E-P has rank 1. The displacement E-I has rank 2.
These facts follow directly from ell u=-2 and the displayed coordinate
formulas in `MODEL.md`.

This family gives one centre per block relative to the simple map P.
It gives two displacement directions per block relative to identity.
The distinction is needed in a controller: P must still be implemented
or carried.

## Classification of diagonal metrics

Every diagonal real matrix D with E^T D E=D is a scalar multiple of

```text
J=diag(1^k,-1/m,-1/m).
```

To prove this, write D=diag(d_0,...,d_(k-1),e,f). The last column of E
has its only nonzero entry, equal to 1, in row b. Its norm equation gives
e=f. The norm equation for column a_i is

```text
sum_j d_j + m^2 f = 2 d_i.
```

Thus all d_i have the same value d. Since k=m+2, this equation reduces
to m(d+m f)=0. The field has characteristic zero and m is nonzero, so
f=e=-d/m. These are necessary equations. The identity in `MODEL.md`
proves that they are sufficient.

Consequently, a nonsingular diagonal metric exists, but it is
indefinite. It has inertia (n-2,2) or (2,n-2), according to the sign
of its nonzero scale. No positive diagonal metric is possible.

Over the dyadic ring Z[1/2], a diagonal metric whose entries are all
units exists if and only if m is a power of 2. Indeed, the units are
the signed powers of 2. If d and -d/m are units, their ratio m is a
unit. Conversely, if m is a power of 2, J and J^-1 are diagonal
matrices of dyadic units.

Thus the permitted block sizes in this family are

```text
n=4+2^h,    h>=0.
```

The actual native geometry supplies sizes 6 and 8. The larger abstract
family does not assert that the repository has a native geometry for
every listed size.

## A unit centre norm

Let K=J^-1. Then

```text
K ell^T=-u,          ell K ell^T=2,
R=I-K ell^T ell.
```

The centre has signed norm 2 for every n. This removes the odd norm
factor n-1 that occurs with the unsigned all-ones centre. In the actual
physical pair basis, the large-block centre norm is 4 and the small-block
norm is 2. Both are dyadic units. This permits a metric-compatible
one-centre completion in principle. A complete code still needs its
physical basis, native access, and paid implementation.

## Minimum displacement in the reciprocal zero-diagonal grammar

Let A be an invertible n-by-n matrix over a characteristic-zero field,
where n>=3. Suppose that both A and A^-1 have zero diagonal. Then

```text
rank(A-I) >= 2.
```

Rank 0 is impossible. If rank(A-I)=1, write A=I+v w^T.
Zero diagonal gives v_i w_i=-1 for every i, and hence w^T v=-n.
The rank-one inverse formula is

```text
A^-1 = I + v w^T/(n-1).
```

Every diagonal entry of A^-1 is then (n-2)/(n-1), which is nonzero.
This contradicts the hypothesis.

The family E attains the lower bound 2 in every block. Therefore the
actual rank 32 is minimum among direct sums of sixteen independent
blocks of sizes 6 and 8 for which both the response and its reciprocal
must have zero diagonal. This is not a rank 32 lower bound for arbitrary
112-by112 responses, coupled blocks, a changed native grammar, or a
different baseline P.

The assumptions have concrete boundary cases. At n=2, a coordinate
swap has zero diagonal in both directions and rank(A-I)=1. At n=3,
this family becomes a coordinate 3-cycle and has a positive diagonal
metric. At n=4, every diagonal invariant metric in this family is
singular: it has zero ordinary weights and equal final two weights.
The diagonal-metric classification above is therefore stated for n>=5.

## Checks and provenance

The formal arguments above apply to all stated n. The companion checker
also verifies the exact matrices, ranks, metric equations, and the
dimension of the diagonal-metric solution space for n=5,...,24. It
checks the boundary cases and the rank-one inverse counterexample
directly. These finite checks support the proof; they do not replace
its quantified argument.

The actual 112 matrices and native words remain pinned in the model
and native freezes. This theorem adds the metric classification and the
sharp blockwise displacement bound. It does not close the global
caller or terminal.

The coordinating agent supplied the E=P R family and its candidate
metric. This lane supplied the classification, boundary cases, and
blockwise lower bound. AI assistance was used.

No PR, push, commit, or publication is authorized. Before any future PR
description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
