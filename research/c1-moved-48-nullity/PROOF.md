# Geometric multiplicity of eigenvalue 0

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Statement

Let `M` be the integer matrix of `B = 4 A_1` in the pinned eigenvalue-`+1`
basis of `s = (0 4 3 7)(5 6)` on the moved character `eps[1] * eps[2]`. The
matrix of `A_1` on that space is `M/4`. Eigenvalue 0 of `A_1` and eigenvalue
0 of `M` have the same kernel, and

```text
dim_Q ker(M) = 10.
```

The rational rank of `M` is 38. The algebraic multiplicity of eigenvalue 0 is
also 10, for `M` and for `A_1`. Both counts agree with the factor `x^10`
recorded by the characteristic polynomial in
`research/c1-moved-48-charpoly/`.

The selected conditional kappa stays `781451/250000000`.

## Pinned objects

The predecessor package is open PR #7036, commit
`0a670e4db89c79e6536dd4f448da0664d3f73890`. That commit is not on main, so
this package vendors byte copies of the two evidence files. Their SHA256
values are the predecessor blobs:

```text
basis   research/c1-moved-48-nullity/evidence/basis.json
        sha256 c18744f28d41c76a9b4299539a8c56e197a16850dd7ccc32aa7d227a48ef6764
        predecessor blob 34390858604205ef0e79cfc94199fe6d932ccff9
matrix  research/c1-moved-48-nullity/evidence/matrix.json
        sha256 32b45cef4c1461f81b7b04b07ad388058cd872159a3f29107c6fe47ada6c4eae
        predecessor blob 8ac74c0dd67ecac52309c4008cf06f924e203512
```

The basis is the least-index signed-orbit basis of the character
`eps[1] * eps[2]` and of `s v = v`. Every coefficient is `±1`. Support sizes
are eight vectors of size 8, thirty-two of size 16, and eight of size 32.
Write `D` for the diagonal matrix of those sizes. The identity

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
nonzero entry at or below the current row, produces rank 38. The pivot
columns and the original indices of the pivot rows are stored in
`evidence/kernel.json`. The determinant of that `38-by-38` minor is
`198928` modulo `1000003` and `736091` modulo `1000033`. Both residues are
nonzero, so the integer minor is nonzero. Therefore

```text
rank_Q(M) >= 38.
```

The same reduction modulo `1000003` produces 10 kernel vectors. Each free
coordinate is normalized to `1` over the field, reconstructed as a rational
of height at most 2, and cleared to an integer vector. The free columns are

```text
17, 19, 21, 23, 34, 35, 40, 41, 44, 45.
```

On those columns the 10 vectors form the identity matrix. The product of the
diagonal is `1`, so the vectors are linearly independent over `Q`. Every
entry lies in

```text
{-2, -1, 0, 1, 2},
```

and 34 of the 480 entries are nonzero. Exact integer matrix-vector products
give `M v = 0` for each vector. Therefore

```text
rank_Q(M) <= 38.
```

The two bounds agree, and the rational rank is 38. The geometric
multiplicity of eigenvalue 0 is 10.

A modular rank is a lower bound on the rational rank. The rank modulo
`1000003` and the rank modulo `1000033` are both 38. Those computations
become equalities only together with the integer kernel. The verifier
refuses a one-by-one matrix `(1000003)`, whose modular rank is 0 and whose
reconstructed modular kernel vector is not an exact integer kernel vector.

The reconstruction modulus is larger than `2 * 2^2`. Every kernel entry that
appears is the unique rational of numerator and denominator at most
`floor(sqrt(1000003 / 2))` in its residue class, and the exact product
`M v = 0` is the proof that the lift is a kernel vector.

## Algebraic multiplicity

The form `<x, y>_D = x^T D y` is symmetric and positive definite, because
every support size is positive. Since `D M` is symmetric, `M` is
self-adjoint for this form.

The left kernel of `M` is `D` applied to the right kernel. Indeed,
`M^T u = 0` rearranges, through `M^T = D M D^{-1}`, to `M D^{-1} u = 0`.

Let `K = ker M`. A vector `v in K` lies in the image of `M` exactly when
`u^T v = 0` for every left-kernel vector `u`. Every such `u` is `D w` for
some `w in K`, and `u^T v = w^T D v`. The Gram matrix of the 10 kernel
vectors under `< , >_D` has determinant `433223` modulo `1000003` and
`646636` modulo `1000033`. Both residues are nonzero, so the Gram
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
chi_M(x) = x^10 det(x I - B),
```

and `det(-B)` is nonzero, so the algebraic multiplicity is 10.

For any 48-by-48 matrix, `det(x I - M/4) = 4^{-48} det(4x I - M)`. The
power of `x` is unchanged by the substitution `x |-> 4x`. Eigenvalue 0 of
`A_1 = M/4` therefore has the same algebraic multiplicity, 10.

The predecessor records this exponent as the first factor `(10, (0, 1))` in
`research/c1-moved-48-charpoly/verify.py`, whose SHA256 is
`c44474de799a8b3d461b604aeac01c5f372838e4bbea484b99f55535060c54ca`. When
that commit is present in the clone, the verifier reads the factor and
checks that the ascent count equals it. The ascent argument does not
recompute the degree-48 polynomial. A clone without that commit still has
the vendored matrix, the kernel, and this ascent count.

## Evidence class

This is a proof for one pinned matrix. The domain is that matrix. The
kernel, the minor residues, the Gram residues, and the scaling identity are
exact integer or modular checks with the completeness argument above. It is
not an exhaustive census of invariant subspaces, and the modular ranks are
not by themselves the rational geometric multiplicity.

## What this computation leaves open

The same method applies to `M - 8 I` and to `M + 8 I`. Those kernels are the
eigenspaces of eigenvalues `2` and `-2` of `A_1`. The predecessor records
algebraic multiplicity 6 for each. This package does not run those shifted
eliminations.

The predecessor records the same characteristic polynomial on the
eigenvalue `-1` space of this character. That matrix is not pinned here, so
this rank is stated for the eigenvalue-`+1` matrix only.

The eigenvalue-`i` polynomial over `Q(i)` is a different computation, and
this kernel is not the 24-dimensional kernel of the 216-by-216 matrix. The
10-dimensional kernel is one `A_1`-invariant subspace. This package does not
split it further and does not identify it with the 12-dimensional minus
space cut by a different stabilizer element.
