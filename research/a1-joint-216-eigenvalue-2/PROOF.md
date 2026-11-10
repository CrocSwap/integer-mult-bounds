# Geometric multiplicity of eigenvalue 2

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Statement

Let `M` be the integer matrix of `B = 4 A_1` in the pinned joint `(+1,+1)`
basis of dimension 216. The matrix of `A_1` on that space is `M/4`.
Eigenvalue 2 of `A_1` is eigenvalue 8 of `M`, and

```text
dim_Q ker(M - 8 I) = 12.
```

The rational rank of `M - 8 I` is 204. The algebraic multiplicity of this
eigenvalue is also 12, for `M` and for `A_1`. Both counts agree with the
factor `(x - 2)^12` recorded by the characteristic polynomial in
`research/a1-joint-216-charpoly/`.

The selected conditional kappa stays `781451/250000000`.

## Pinned objects

The basis and the matrix are inputs, unchanged from the characteristic
polynomial package:

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

holds for every pair of indices. Equivalently, `D M` is symmetric. The same
identity holds for `T = M - 8 I`, because the subtracted term is a scalar
matrix and `D` is diagonal. This package checks both identities on the pinned
integers.

## Rank

Work modulo `1000003`. Greedy row reduction of `T`, always pivoting at the
first nonzero entry at or below the current row, produces rank 204. The pivot
columns and the original indices of the pivot rows are stored in
`evidence/kernel.json`. The determinant of that `204-by-204` minor is
`257823` modulo `1000003` and `857057` modulo `1000033`. Both residues are
nonzero, so the integer minor is nonzero. Therefore

```text
rank_Q(M - 8 I) >= 204.
```

The same reduction modulo `1000003` produces 12 kernel vectors. Each free
coordinate is normalized to `1` over the field, reconstructed as a rational
of height at most `120`, and cleared to an integer vector. The free columns
are

```text
79, 81, 85, 87, 89, 93, 135, 161, 185, 189, 209, 213.
```

On those columns the 12 vectors form a diagonal matrix with diagonal

```text
8, 8, 8, 8, 8, 8, 1, 1, 1, 34, 1, 34.
```

The product of the diagonal is `8^6 * 34^2 = 303038464 = 2^20 * 17^2`, so
the vectors are linearly independent over `Q`. Every entry lies in
`-120..120`, and 242 of the 2592 entries are nonzero. Exact integer
matrix-vector products give `T v = 0` for each vector. Therefore

```text
rank_Q(M - 8 I) <= 204.
```

The two bounds agree, and the rational rank is 204. The geometric
multiplicity of eigenvalue 8 of `M`, and of eigenvalue 2 of `A_1`, is 12.

A modular rank is a lower bound on the rational rank. The rank modulo
`1000003` and the rank modulo `1000033` are both 204. Those computations
become equalities only together with the integer kernel.

The reconstruction modulus is larger than `2 * 120^2 = 28800`. Every kernel
coordinate that appears is the unique rational of numerator and denominator
at most `floor(sqrt(1000003 / 2)) = 707` in its residue class, and the exact
product `T v = 0` is the proof that the lift is a kernel vector.

## Algebraic multiplicity

The form `<x, y>_D = x^T D y` is symmetric and positive definite, because
every support size is positive. Since `D T` is symmetric,

```text
T^T = D T D^{-1}.
```

The left kernel of `T` is `D` applied to the right kernel. Indeed,
`T^T u = 0` rearranges to `T D^{-1} u = 0`.

Let `K = ker T`. A vector `v` lies in the image of `T` exactly when
`u^T v = 0` for every left-kernel vector `u`. The standard pairing identifies
the orthogonal of a `k`-dimensional left kernel with a subspace of dimension
`216 - k`, which is the rank, so that orthogonal equals the image. Every such
`u` is `D w` for some `w in K`, and `u^T v = w^T D v`. The Gram matrix of the
12 kernel vectors under `< , >_D` has determinant `686998` modulo `1000003`
and `166386` modulo `1000033`. Both residues are nonzero, so the Gram
determinant is a nonzero integer and the form is nondegenerate on `K`.
Hence `w^T D v = 0` for every `w in K` forces `v = 0`, and

```text
ker(T) ∩ im(T) = {0}.
```

If `T^2 x = 0`, then `T x` lies in that intersection, so `T x = 0`. The
ascent of eigenvalue 8 is 1.

Choose a complement `W` of `K`. The restriction of `T` to `W` is injective,
and its image meets `K` only at 0, so that image is another complement of
`K`. In a basis of `K` followed by a basis of `W`, the matrix of `T` has the
block shape

```text
[ 0  A ]
[ 0  B ]
```

with `B` invertible: `B w = 0` puts `T w` in `K ∩ im(T)`, hence `T w = 0`,
hence `w = 0`. The characteristic polynomial is

```text
chi_T(x) = x^12 det(x I - B),
```

and `det(-B)` is nonzero, so eigenvalue 0 of `T` has algebraic multiplicity
12. That eigenvalue is eigenvalue 8 of `M`.

For any 216-by-216 matrix,
`det(x I - M/4) = 4^{-216} det(4x I - M)`. Substituting the factorization

```text
chi_M(y) = (y - 8)^12 det((y - 8) I - B)
```

gives

```text
chi_{A_1}(x) = 4^{-204} (x - 2)^12 det(4(x - 2) I - B).
```

The second determinant at `x = 2` is `det(-B)`, which is nonzero, so
eigenvalue 2 of `A_1` has algebraic multiplicity 12.

The predecessor records this exponent as the factor `(12, (-2, 1))` in
`research/a1-joint-216-charpoly/verify.py`, the monic linear polynomial
`x - 2` with multiplicity 12. This package reads that factor and checks that
the ascent count equals it. The ascent argument does not recompute the
degree-216 polynomial. The paired factor `(12, (2, 1))`, for eigenvalue
`-2`, is a different token and is not the count used here.

## Evidence class

This is a proof for one pinned matrix. The domain is `M - 8 I` for that
matrix. The kernel, the minor residues, the Gram residues, and the scaling
identity are exact integer or modular checks, and the rank bounds above are
the completeness argument for the nullity. A modular rank by itself is only
the lower bound `rank_Q(M - 8 I) >= 204`.

This is not a heuristic search, and it is not a census of the other
eigenvalues or of the other three joint sign spaces.

## What this computation leaves open

The same method applies to `M + 8 I`, whose kernel is the eigenspace of
eigenvalue `-2` of `A_1`. The predecessor records algebraic multiplicity 12
for that eigenvalue. This package does not run that shifted elimination.

The predecessor proves that the other three joint sign spaces have the same
characteristic polynomial. Their matrices are not pinned here, so this rank
is stated for the `(+1,+1)` matrix only. Eigenvalue 0 on those three spaces
remains the separate open question of the eigenvalue-0 package.

The kernel is an `A_1`-invariant subspace of dimension 12. This package does
not intersect it with the normalizer isotypics.
