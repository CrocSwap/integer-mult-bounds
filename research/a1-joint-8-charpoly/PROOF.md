# Characteristic polynomial of one 8-dimensional c=1 joint eigenspace

This is an exhaustive finite certificate for one invariant subspace of the
`c=1` block of the historical one-slot doubled centre operator. It is not a
new minimal polynomial of the full operator, not a change of the selected
conditional kappa, and not a statement about the 216-dimensional
trivial-character space.

## Operator

The input is the 8-by-112 query in `INTERFACE.json`, SHA256
`5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.
Its columns lie in `{-1,0,1}^8`, each has weight 4, the 112 port labels are
distinct odd-weight vectors in `F_2^9`, and `R R^T = 56 I_8`.

On `Q^8 ⊗ Q[F_2^9]`, of dimension 4096, the `c=1` block and its integer form are

```text
A_1 = (1/4) sum_q r_q r_q^T ⊗ P_q(1),
B   = 4 A_1 = sum_q r_q r_q^T ⊗ P_q(1).
```

`P_q(1)` sends `e_a` to `e_{a+q}` when the `F_2` dot product `q·1` equals 1,
and to `(-1)^{q·a} e_a` otherwise. Basis index `i*512+a` means query
coordinate `i` and address `a`.

The published `c=1` sector minimal polynomials in
`research/exact-one-slot-gram/CERTIFICATE.json` are used only for the
divisibility comparison below. This note does not replay that degree-881
certificate.

## The character

A signed coordinate permutation acts by `(S v)_k = eps[k] v[inv[k]]` and by
the orthogonal label map `U e_a = e_{T a}`. The sign stabilizer `H` is the
set of coordinate sign patterns with positive sign on coordinate 0 whose
label map fixes sector 1. The verifier enumerates all 128 such patterns.
Exactly 16 survive, and they are exactly the patterns whose negative signs
lie in coordinates `{1,2,5,6}`. Every element is an involution and fixes the
eight coordinates as a permutation. Thus `H` is `(Z/2)^4`.

`H` has 16 linear characters. The trace formula

```text
dim chi = |H|^{-1} sum_{h in H} chi(h) tr(h),
tr(S) = (sum of eps[k] over coordinates fixed by the permutation) * 2^{nullity(T-I)},
```

recomputes the dimension histogram `{864: 1, 432: 4, 192: 6, 80: 4, 32: 1}`.
Exactly one character has dimension 32. On a sign pattern `eps` it is

```text
chi(eps) = eps[1] * eps[2] * eps[5] * eps[6].
```

The values on all 16 elements are pinned in
[evidence/character.json](evidence/character.json). This is the sign list the
trace formula, by itself, does not provide.

The involutions from the sign-stabilizer split are

| name | `inv` | output signs `-1` |
|---|---|---|
| `g` | `(0, 2, 1, 3, 4, 6, 5, 7)` | coordinates 4 and 7 |
| `t` | `(0, 5, 6, 3, 4, 1, 2, 7)` | coordinates 3 and 7 |

Both square to the identity, they commute, both preserve sector 1, and `g`
sends sector 3 to 343. Conjugation by `g` swaps the sign pairs `(1 2)` and
`(5 6)`, and conjugation by `t` swaps `(1 5)` and `(2 6)`. Either operation
preserves the product `eps[1] eps[2] eps[5] eps[6]`. The verifier checks
`chi(ghg) = chi(h)` and `chi(tht) = chi(h)` for every `h` in `H`, and checks
that both conjugates remain inside `H`. So `g` and `t` preserve the
`chi`-isotypic component.

The same trace formula, twisted by `chi`, gives joint `(±1, ±1)` dimensions
`8, 8, 8, 8` for `(g, t)`.

## The subspace

The `chi`-isotypic component is the simultaneous eigenspace
`rho(h) v = chi(h) v` for every `h` in `H`. These are two-term equations on
`Q^4096`. Signed union-find computes the full rational solution space. It has
dimension 32, matching the trace formula, and every basis vector is supported
on the coordinates `{0,3,4,7}`.

Let `V` be the further joint `(+1,+1)` eigenspace of `g` and `t` inside that
component. The same equations, with those two eigenvalues, have an explicit
solution space of dimension 8. The trace formula gives the same dimension, so
the basis is the whole eigenspace, not a proper subspace. The basis is
canonical: in each connected component the representative is the least index,
its coefficient is `+1`, and every other coefficient is the sign forced by
the equations. Components are ordered by increasing representative. Every
vector has support size 8, and every coefficient is `±1`. Every vector is
supported on query coordinate 0.

Coordinate 0 is the unique coordinate fixed by both permutations and carrying
output sign `+1` under both `g` and `t`. The other three joint spaces are
supported in the same way:

| `(g, t)` | support coordinate | sign of `g`, sign of `t` |
|---|---:|---|
| `(+1,+1)` | 0 | `+`, `+` |
| `(+1,-1)` | 3 | `+`, `-` |
| `(-1,+1)` | 4 | `-`, `+` |
| `(-1,-1)` | 7 | `-`, `-` |

The four bases together consist of 32 vectors. Their supports are pairwise
disjoint, and each vector has coefficient `+1` at its own least index, so the
32 vectors are linearly independent. They lie in the 32-dimensional character
space, so they are a basis of that space. The four joint spaces are therefore
a direct-sum decomposition of the character space. The pinned `(+1,+1)` basis
is [evidence/basis.json](evidence/basis.json). Its representatives are the
addresses `128, 129, 134, 135, 170, 171, 172, 173` on coordinate 0.

`chi` is not the trivial character: the sign flip of coordinate 1 has
`chi = -1`. A vector fixed by every element of `H` and transforming by `chi`
is zero. This 8-dimensional space meets the trivial-character 216-dimensional
space only at zero.

## The matrix

`B` commutes with every element of `H` and with `g` and `t`, checked on all
4096 basis vectors by comparing the two actions of each signed permutation on
the columns of `B`. Two independent expansions of `B`, one by columns and one
by the 112 ports, agree on every basis vector of all four joint spaces.

In the ordered basis of `V`, the matrix `M` of `B` is

```text
  4  -4   0   0   0   0   0   0
 -4   4   0   0   0   0   0   0
  0   0  -4  -4   0   0   0   0
  0   0  -4  -4   0   0   0   0
  0   0   0   0   4  -4   0   0
  0   0   0   0  -4   4   0   0
  0   0   0   0   0   0  -4  -4
  0   0   0   0   0   0  -4  -4
```

Every entry lies in `{-4,0,4}`. The same matrix is pinned in
[evidence/matrix.json](evidence/matrix.json). If `size_r` is the support of
the `r`-th basis vector, then `size_r M_{r s} = size_s M_{s r}`. Here every
support has size 8, and `M` is symmetric. The matrix of `A_1` on `V` is
`M/4`.

## Characteristic polynomial

The matrix is four 2-by-2 blocks. For `[[4,-4],[-4,4]]`,

```text
det(x I - block) = (x-4)^2 - 16 = x(x-8).
```

For `[[-4,-4],[-4,-4]]`,

```text
det(x I - block) = (x+4)^2 - 16 = x(x+8).
```

Two blocks of each kind give

```text
chi_B(x) = x^4 (x-8)^2 (x+8)^2 = x^8 - 128 x^6 + 4096 x^4.
```

The Faddeev–Leverrier recurrence on the recomputed matrix produces the same
coefficients. Determinants of `t I - M` at `t = 0,1,2,3,5,8,-2,4` agree with
this polynomial, both over `Z` and modulo `1000003`. Since
`chi_{A_1}(x) = det(x I - M/4) = 4^{-8} chi_B(4x)`,

```text
chi_{A_1}(x) = x^4 (x-2)^2 (x+2)^2 = x^8 - 8 x^6 + 16 x^4.
```

Both polynomials are monic of degree 8 in `Z[x]`. Ascending-coefficient
SHA256 values are

```text
chi_A  4078d16db1834dcd427c4f1094b96838a2c425c116c7cd1b60d46aa1f472f632
chi_B  04375398447c3b08683582cc785814e9955ed62fcaa6725dc3467484c8a41457
```

The same polynomial is the characteristic polynomial of `A_1` on each of the
four joint spaces. On each of those four matrices, `M(M^2 - 64 I) = 0` and
the rational nullities at `0`, `8` and `-8` are `4`, `2` and `2`, so
each joint space is diagonalizable with the same minimal polynomial. Explicit
eigenvectors are pinned only for the `(+1,+1)` space. Those spaces are
`A_1`-invariant and direct-sum to the 32-dimensional character space, so the
characteristic polynomial of `A_1` on that whole character space is

```text
x^{16} (x-2)^8 (x+2)^8.
```

## Minimal polynomial and rational nullities

Matrix multiplication gives `M (M^2 - 64 I) = 0`, so the minimal polynomial
of `B` on `V` divides `x(x-8)(x+8)`. In the ordered basis, the following
vectors are linearly independent eigenvectors:

| eigenvalue of `B` | eigenvalue of `A_1` | basis vectors |
|---|---:|---|
| 0 | 0 | `(1,1,0,0,0,0,0,0)`, `(0,0,-1,1,0,0,0,0)`, `(0,0,0,0,1,1,0,0)`, `(0,0,0,0,0,0,-1,1)` |
| 8 | 2 | `(-1,1,0,0,0,0,0,0)`, `(0,0,0,0,-1,1,0,0)` |
| -8 | -2 | `(0,0,1,1,0,0,0,0)`, `(0,0,0,0,0,0,1,1)` |

They are pinned in [evidence/kernels.json](evidence/kernels.json). Each is
checked by multiplication against `M`. Exact rational row reduction of
`M`, `M-8I` and `M+8I` gives ranks `4`, `6` and `6`, hence nullities `4`,
`2` and `2`. The nullities equal the algebraic multiplicities, and each
linear factor occurs, so the minimal polynomial of `B` on `V` is exactly
`x(x-8)(x+8)`. Equivalently, `A_1` is diagonalizable on `V` with minimal
polynomial `x(x-2)(x+2)`.

These ranks are exact rational ranks. A modular rank is not used. The
geometric multiplicity of eigenvalue 0 on the separate 216-by-216 matrix is
not computed here.

An eigenvector in `Q^4096` is the same linear combination of the eight pinned
basis vectors. The kernels therefore exhibit proper nonzero
`A_1`-invariant subspaces of `V`.

## Divisibility

Each of `x`, `x-8` and `x+8` divides all four published minimal polynomials
of the `c=1` Bell sectors `(t,s)` in
`research/exact-one-slot-gram/CERTIFICATE.json`. Those polynomials are monic
of degrees 71 or 101, and the comparison evaluates them at `0`, `8` and `-8`.
It reads coefficients. It does not rerun the degree-881 certificate. This
places the eigenvalues of this 8-dimensional space among the eigenvalues
already present in that certificate. It does not identify this space with any
subspace of the 216-dimensional trivial-character block.

## Evidence class

This is a proof of one finite identity. The group `H` is obtained by
enumerating all 128 sign patterns with positive sign on coordinate 0. All 16
characters of that `(Z/2)^4` are evaluated by the trace formula, so the
identification of `chi` is an exhaustive census of a finite group. The joint
space is the full rational solution space of the stated eigenvalue equations,
and its dimension matches the trace formula. The characteristic polynomial is
the exact determinant of the resulting 8-by-8 integer matrix, cross-checked
by the block factorization, by Leverrier's recurrence, and by integer and
modular determinants. Nothing in that chain is a partial search. The result
is not an unrestricted nonexistence theorem and does not constrain operators
outside this pinned query and this subspace.

## What this does not say

The selected conditional kappa stays `781451/250000000`. A degree-8
polynomial on one invariant subspace does not replace the degree-881 minimal
polynomial of the full one-slot operator. The characteristic polynomial of
the 216-dimensional trivial-character joint space is a different computation,
already recorded by the predecessor package, and is not recomputed here. The
8-dimensional isotypic summand of the signed normalizer of that 216-space
lies in the trivial character; this space lies in `chi` and meets it only at
zero. Sector `c=3` is not preserved by `g`. Equality of the four joint
polynomials is not an intertwiner between those spaces.
