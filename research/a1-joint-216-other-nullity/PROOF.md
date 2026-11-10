# Geometric multiplicity of eigenvalue 0 on the other three joint sign spaces

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Statement

Let `H` be the order-16 `c=1` sign stabilizer, and let `g` and `t` be the commuting involutions from the sign-stabilizer split. On the trivial character space of `H`, each pair

```text
(λ_g, λ_t) in {(1, -1), (-1, 1), (-1, -1)}
```

determines a joint sign space of dimension 216. Let `M` be the integer matrix of `B = 4 A_1` in the least-index signed-orbit basis of that space. The matrix of `A_1` is `M/4`. Eigenvalue 0 of `A_1` and eigenvalue 0 of `M` have the same kernel, and

```text
dim_Q ker(M) = 24
```

for each of the three matrices. The rational rank is 192. The algebraic multiplicity of eigenvalue 0 is also 24, for `M` and for `A_1`.

The same geometric multiplicity, 24, is the multiplicity PR #7018 records for the remaining pair `(+1,+1)`. This package does not recompute that rank. The three matrices are not equal to that pinned matrix, nor to each other.

The selected conditional kappa stays `781451/250000000`.

## The three spaces

`g` and `t` are commuting involutions, and both commute with `B`. An involution has only the eigenvalues `±1`, so a joint sign pair for `(g, t)` is one of the four pairs `(±1, ±1)`. There is no fifth pair. The pair `(+1,+1)` is the basis and matrix pinned by `research/a1-joint-216-charpoly/`. Rebuilding that pair with the same restriction recovers those pinned bytes. The three pairs above are the rest of the list.

Each basis is the least-index signed-orbit basis of the equations `v = h v` for every `h in H`, `g v = λ_g v`, and `t v = λ_t v`. Every coefficient is `±1`, the least index in each vector has coefficient `+1`, and the support sizes are only `1, 4, 8, 16`. The trace formula gives trivial-character dimension 864 and joint `(+1,+1)` dimension 216. Each of the four explicit bases has dimension 216.

`B` preserves each space: the two expansions of `B`, by columns and by the 112 ports, agree on every basis vector, and the image meets every coordinate of a component with the same quotient. In that ordered basis, `M_rs` is the value of `B v_s` at the representative of component `r`. Every entry lies in `-28..28`. Each matrix has trace 0 and 3972 nonzero entries. The six pairwise entry-disagreement counts are

| pair | disagreeing entries |
|---|---|
| `(+1,+1)` against `(+1,-1)` | 7042 |
| `(+1,+1)` against `(-1,+1)` | 7006 |
| `(+1,+1)` against `(-1,-1)` | 6960 |
| `(+1,-1)` against `(-1,+1)` | 6462 |
| `(+1,-1)` against `(-1,-1)` | 6462 |
| `(-1,+1)` against `(-1,-1)` | 6304 |

Write `D` for the diagonal matrix of support sizes. The identity

```text
size_r M_rs = size_s M_sr
```

holds for every pair of indices of every one of the four matrices. Equivalently, `D M` is symmetric, so `M` is self-adjoint for the positive definite form `<x, y>_D = x^T D y`.

## Pinned certificates

The predecessor bytes are unchanged:

```text
basis   research/a1-joint-216-charpoly/evidence/basis.json
        sha256 e198cd71f4100d2629ecc25fb40b135a8c18c7756be8bc80bf24d7b349af418a
matrix  research/a1-joint-216-charpoly/evidence/matrix.json
        sha256 44f40ad5a12daf7c8493b42e1e9ddc4ef338b317ee5fdfc6de1b413642ca97aa
code    research/a1-joint-216-charpoly/verify.py
        sha256 4ab1cf663cd1d7eb2698f70c7601709ef78415d9dce47746a65f95671d9ee26a
```

Each other sign space is one JSON object: eigenvalues, basis, matrix, and rank certificate.

```text
(+1,-1)  evidence/g-plus-t-minus.json
         sha256 f3077453f9009ee4dd6cc4879cbd7ce6fdb8858f6083ce43d0e8c586473a44a8
(-1,+1)  evidence/g-minus-t-plus.json
         sha256 b9e60ba3fc977503ef489ddd9b377ff02f8b9f70b580c539422f49d88533301d
(-1,-1)  evidence/g-minus-t-minus.json
         sha256 58a4b4c053e1496e8824938b574e7773aaa9ad9da6edf1a031d5ff3a0e0282ed
```

## Rank

The same elimination is run on each of the three matrices. Work modulo `1000003`. Greedy row reduction, always pivoting at the first nonzero entry at or below the current row, produces rank 192. The same pivot minor is nonzero modulo `1000003` and modulo `1000033`, so the integer minor is nonzero and

```text
rank_Q(M) >= 192.
```

The rank modulo `1000033` is also 192. A modular rank is a lower bound on the rational rank. It becomes an equality only together with the integer kernel below.

The reduction modulo `1000003` produces 24 kernel vectors. Each free coordinate is normalized to `1` over the field, reconstructed as a rational of numerator and denominator at most `floor(sqrt(1000003 / 2))`, and cleared to an integer vector. Exact integer products give `M v = 0`. On the free columns the 24 vectors form a positive diagonal matrix, so they are linearly independent over `Q` and

```text
rank_Q(M) <= 192.
```

The two bounds agree. The rational rank is 192, and the geometric multiplicity of eigenvalue 0 is 24, on each matrix.

| sign `(g, t)` | entry bound | nonzero kernel entries | minor mod `1000003` | minor mod `1000033` |
|---|---|---|---|---|
| `(+1,-1)` | 14 | 384 | 666869 | 923642 |
| `(-1,+1)` | 18 | 426 | 488877 | 871788 |
| `(-1,-1)` | 42 | 454 | 119363 | 839553 |

The positive free diagonals are

```text
(+1,-1)   1, 1, 2, 2, 6, 3, 6, 1, 1, 3, 2, 8, 8, 2, 8, 8, 8, 8, 8, 8, 1, 6, 1, 6
(-1,+1)   1, 1, 2, 1, 1, 2, 4, 2, 4, 1, 1, 1, 2, 8, 8, 2, 8, 8, 8, 8, 8, 8, 1, 4
(-1,-1)   1, 1, 7, 2, 1, 7, 2, 2, 7, 1, 2, 1, 1, 7, 14, 8, 8, 2, 8, 8, 8, 8, 8, 8
```

Every kernel entry is at most 42 in absolute value, and `2 * 42^2 = 3528 < 1000003`. Each such integer is the unique rational of numerator and denominator at most `floor(sqrt(1000003 / 2))` in its residue class. The exact product `M v = 0` is the proof that the lift is a kernel vector. The kernel of one sign matrix is not an exact kernel of either other sign matrix.

The free columns and the full vectors are stored in the corresponding certificate. This argument is the one used for the single `(+1,+1)` matrix in PR #7018, applied here to the three matrices that PR does not pin.

## Algebraic multiplicity

The form `< , >_D` is symmetric and positive definite, because every support size is positive. Since `D M` is symmetric, `M` is self-adjoint for this form.

The left kernel of `M` is `D` applied to the right kernel. Indeed, `M^T u = 0` rearranges, through `M^T = D M D^{-1}`, to `M D^{-1} u = 0`.

Let `K = ker M`. A vector `v in K` lies in the image of `M` exactly when `u^T v = 0` for every left-kernel vector `u`. Every such `u` is `D w` for some `w in K`, and `u^T v = w^T D v`. The Gram matrix of the 24 kernel vectors under `< , >_D` has nonzero determinant modulo both working primes:

| sign `(g, t)` | Gram mod `1000003` | Gram mod `1000033` |
|---|---|---|
| `(+1,-1)` | 632885 | 70761 |
| `(-1,+1)` | 140621 | 995029 |
| `(-1,-1)` | 666400 | 467011 |

Both residues are nonzero, so the Gram determinant is a nonzero integer and the form is nondegenerate on `K`. Hence `w^T D v = 0` for every `w in K` forces `v = 0`, and

```text
ker(M) ∩ im(M) = {0}.
```

If `M^2 x = 0`, then `M x` lies in that intersection, so `M x = 0`. The ascent of eigenvalue 0 is 1.

Choose a complement `W` of `K`. The restriction of `M` to `W` is injective, and its image meets `K` only at 0, so that image is another complement of `K`. In a basis of `K` followed by a basis of `W`, the matrix of `M` has the block shape

```text
[ 0  A ]
[ 0  B ]
```

with `B` invertible: `B w = 0` puts `M w` in `K ∩ im(M)`, hence `M w = 0`, hence `w = 0`. The characteristic polynomial is

```text
chi_M(x) = x^24 det(x I - B),
```

and `det(-B)` is nonzero, so the algebraic multiplicity is 24.

For any 216-by-216 matrix, `det(x I - M/4) = 4^{-216} det(4x I - M)`. The power of `x` is unchanged by the substitution `x |-> 4x`. Eigenvalue 0 of `A_1 = M/4` therefore has the same algebraic multiplicity, 24.

The predecessor records this exponent as the first factor `(24, (0, 1))` in `research/a1-joint-216-charpoly/verify.py`, and proves that the four joint sign spaces have that same characteristic polynomial. This package reads that factor and checks that the ascent count equals it. The ascent argument does not recompute the degree-216 polynomial. A shared characteristic polynomial is not used as a substitute for the rational nullity: the nullity is the corank of the pinned integer kernel.

## Evidence class

This is a proof for each of the three pinned matrices. The domain of joint sign pairs of these two involutions is the four pairs `(±1, ±1)`. The enumeration of the three pairs other than `(+1,+1)` is complete. It is not a heuristic search, and it is not a modular rank standing alone.

## What this computation leaves open

The same method applies to `M - 8 I` on each of these three matrices. The predecessor records algebraic multiplicity 12 for eigenvalue 2 of `A_1`. Those three shifted eliminations were not run. The same question on the already pinned `(+1,+1)` matrix is open question 1 of PR #7018 and is not recomputed here.

The kernels are `A_1`-invariant subspaces of dimension 24. This package does not intersect them with a normalizer isotypic, and it does not recompute the degree-881 minimal polynomial.
