# Geometric multiplicity of eigenvalue 0

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Statement

Let `M` be the integer matrix of `B = 4 A_1` in the pinned joint `(+1,+1)`
basis of dimension 216. The matrix of `A_1` on that space is `M/4`. Eigenvalue
0 of `A_1` and eigenvalue 0 of `M` have the same kernel, and

```text
dim_Q ker(M) = 24.
```

The rational rank of `M` is 192. The algebraic multiplicity of eigenvalue 0 is
also 24, for `M` and for `A_1`. Both counts agree with the factor `x^24`
recorded by the characteristic polynomial in
`research/a1-joint-216-charpoly/`.

The selected conditional kappa stays `781451/250000000`.

## Pinned objects

The basis and the matrix are inputs, unchanged from the predecessor package:

```text
basis   research/a1-joint-216-charpoly/evidence/basis.json
        sha256 e198cd71f4100d2629ecc25fb40b135a8c18c7756be8bc80bf24d7b349af418a
matrix  research/a1-joint-216-charpoly/evidence/matrix.json
        sha256 44f40ad5a12daf7c8493b42e1e9ddc4ef338b317ee5fdfc6de1b413642ca97aa
```

The basis is the least-index signed-orbit basis of the joint `+1` equations
for the `c=1` sign stabilizer and the involutions `g` and `t`. Every
coefficient is `±1`. Support sizes are only `1, 4, 8, 16`. Write `D` for the
diagonal matrix of those sizes. The identity

```text
size_r M_rs = size_s M_sr
```

holds for every pair of indices. Equivalently, `D M` is symmetric, so

```text
M^T = D M D^{-1}.
```

The predecessor derived this identity from symmetry of `B` and orthogonality
of the basis. This package checks the identity on the pinned integers.

## Rank

Work modulo `1000003`. Greedy row reduction, always pivoting at the first
nonzero entry at or below the current row, produces rank 192. The pivot
columns and the original indices of the pivot rows are stored in
`evidence/kernel.json`. The determinant of that `192-by-192` minor is
`977754` modulo `1000003` and `743543` modulo `1000033`. Both residues are
nonzero, so the integer minor is nonzero. Therefore

```text
rank_Q(M) >= 192.
```

The same reduction modulo `1000003` produces 24 kernel vectors. Each free
coordinate is normalized to `1` over the field, reconstructed as a rational
of height at most 10, and cleared to an integer vector. The free columns are

```text
57, 59, 65, 67, 71, 75, 77, 79, 81, 83, 85, 87, 89, 91,
93, 95, 134, 135, 161, 165, 185, 189, 209, 213.
```

On those columns the 24 vectors form a diagonal matrix with diagonal

```text
2, 2, 1, 2, 1, 1, 2, 8, 8, 2, 8, 8, 8, 8, 8, 8, 1, 1, 1, 2, 1, 2, 1, 2.
```

The product of the diagonal is `2^32`, so the vectors are linearly
independent over `Q`. Every entry lies in

```text
{-10, -8, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 8, 10},
```

and 298 of the 5184 entries are nonzero. Exact integer matrix-vector
products give `M v = 0` for each vector. Therefore

```text
rank_Q(M) <= 192.
```

The two bounds agree, and the rational rank is 192. The geometric
multiplicity of eigenvalue 0 is 24.

A modular rank is a lower bound on the rational rank. The rank modulo
`1000003` and the rank modulo `1000033` are both 192. Those computations
become equalities only together with the integer kernel.

The reconstruction modulus is larger than `2 * 10^2`. Every kernel entry
that appears is the unique rational of numerator and denominator at most
`floor(sqrt(1000003 / 2))` in its residue class, and the exact product
`M v = 0` is the proof that the lift is a kernel vector.

## Algebraic multiplicity

The form `<x, y>_D = x^T D y` is symmetric and positive definite, because
every support size is positive. Since `D M` is symmetric, `M` is self-adjoint
for this form.

The left kernel of `M` is `D` applied to the right kernel. Indeed,
`M^T u = 0` rearranges, through `M^T = D M D^{-1}`, to `M D^{-1} u = 0`.

Let `K = ker M`. A vector `v in K` lies in the image of `M` exactly when
`u^T v = 0` for every left-kernel vector `u`. Every such `u` is `D w` for
some `w in K`, and `u^T v = w^T D v`. The Gram matrix of the 24 kernel
vectors under `< , >_D` has determinant `267823` modulo `1000003` and
`187428` modulo `1000033`. Both residues are nonzero, so the Gram
determinant is a nonzero integer and the form is nondegenerate on `K`.
Hence `w^T D v = 0` for every `w in K` forces `v = 0`, and

```text
ker(M) ∩ im(M) = {0}.
```

If `M^2 x = 0`, then `M x` lies in that intersection, so `M x = 0`. The
ascent of eigenvalue 0 is 1.

Choose a complement `W` of `K`. The restriction of `M` to `W` is injective,
and its image meets `K` only at 0, so that image is another complement of
`K`. In a basis of `K` followed by a basis of `W`, the matrix of `M` has the
block shape

```text
[ 0  A ]
[ 0  B ]
```

with `B` invertible: `B w = 0` puts `M w` in `K ∩ im(M)`, hence `M w = 0`,
hence `w = 0`. The characteristic polynomial is

```text
chi_M(x) = x^24 det(x I - B),
```

and `det(-B)` is nonzero, so the algebraic multiplicity is 24.

For any 216-by-216 matrix, `det(x I - M/4) = 4^{-216} det(4x I - M)`. The
power of `x` is unchanged by the substitution `x |-> 4x`. Eigenvalue 0 of
`A_1 = M/4` therefore has the same algebraic multiplicity, 24.

The predecessor records this exponent as the first factor `(24, (0, 1))` in
`research/a1-joint-216-charpoly/verify.py`. This package reads that factor
and checks that the ascent count equals it. The ascent argument does not
recompute the degree-216 polynomial.

## Evidence class

This is a proof for one pinned matrix. The domain is that matrix. The
kernel, the minor residues, the Gram residues, and the scaling identity are
exact integer or modular checks with a completeness argument written above.
A modular rank by itself is only the lower bound `rank_Q(M) >= 192`.

## What this computation leaves open

The same method applies to `M - 8 I`, whose kernel is the eigenspace of
eigenvalue 2 of `A_1`. The predecessor records algebraic multiplicity 12 for
that eigenvalue. This package does not run that shifted elimination.

The predecessor proves that the other three joint sign spaces have the same
characteristic polynomial. Their matrices are not pinned here, so this rank
is stated for the `(+1,+1)` matrix only.

The kernel is an `A_1`-invariant subspace of dimension 24. This package does
not intersect it with the normalizer isotypics of dimensions 8, 80, and 128.
