# The exhibited 12-dimensional minus space is reducible under A_1

This note is an exact computation over `Q`. It is a proof of one characteristic polynomial and of the invariant-subspace decomposition that polynomial determines. It is not a characteristic polynomial of the 48-dimensional eigenspace, not a census of every cutting involution, and not a multiplication bound. The selected conditional kappa stays `363005817/100000000000`.

Evidence class: a proof, by exact linear algebra over `Q`, for two explicitly presented matrices of one involution.

## Hypotheses

The live input is the 8-by-112 query pinned by `research/centre-polynomial-cache-limits/`, SHA256 `5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`. Its columns lie in `{-1,0,1}^8`, each has weight 4, the port labels are distinct and of odd weight, and `R R^T = 56 I_8`.

On `Q^8 ⊗ Q[F_2^9]`,

```text
A_1 = (1/4) sum_q r_q r_q^T ⊗ P_q(1),
B   = 4 A_1.
```

`P_q(1)` sends `e_a` to `e_{a+q}` when `q · 1 = 1`, and to `(-1)^{q · a} e_a` otherwise. The factor `1/4` is restored only when passing from the characteristic polynomial of `B` to the characteristic polynomial of `A_1`.

`H` is the order-16 group of pure sign changes with positive sign on coordinate `0` whose label map fixes sector `1`. Its character dimensions are `{864: 1, 432: 4, 192: 6, 80: 4, 32: 1}`. Write a sign pattern through the values `eps[0], ..., eps[7]`. The two dimension-192 characters preserved by

```text
s = (0 4 3 7)(5 6), all signs +1,
```

are

```text
chi(eps)  = eps[1] * eps[2],
chi'(eps) = eps[5] * eps[6].
```

In the lexicographic order of value tuples on increasing sign masks, `chi` is the smaller character. The flip of coordinate `1` and the flip of coordinate `2` are sent to `-1` by `chi` and to `+1` by `chi'`; the flips of coordinates `5` and `6` go the other way. This is the pair of characters in PR #7082. The involution `g = (1 2)(5 6)`, with output signs `-1` on coordinates `4` and `7`, preserves both. The involution `t = (1 5)(2 6)`, with output signs `-1` on coordinates `3` and `7`, swaps them. So both are moved by the pair `<g, t>`.

The involution

```text
u = (4 7)(5 6), all signs +1,
```

lies in the same stabilizer, fixes sector `1`, has order 2, and does not commute with `s`. Both `s` and `u` commute with `B`. The sign symmetries in `H` commute with `B` as well.

## The minus space

On each character, the equations `h v = chi(h) v` for `h` in `H`, together with `s v = v`, have a 48-dimensional solution space `E`. In the canonical lattice basis of that space, `u` acts by an integral matrix of trace `24`. The rank of `u + I` is `36` and the rank of `u - I` is `12`. The minus space

```text
W = {v in E : u v = -v}
```

therefore has dimension `12`, and the plus space has dimension `36`. The same ranks hold for `chi'`.

The lattice basis of `W` is the least-index basis of the joint equations `h v = chi(h) v`, `s v = v` and `u v = -v`, with pivot coefficient `+1` on each component. Every basis vector has coefficients in `{±1}` and support size `8` or `16` on `chi` (four vectors of support `8` and eight of support `16`) and support size `16` on `chi'`. Both implementations of `B`, the address-sum form and the coordinate form, agree on these vectors, and every image lies in the `Q`-span of the basis. The matrices are pinned in [evidence/minus-space.json](evidence/minus-space.json).

This `W` is the minus space exhibited by PR #7082. That note proves `B(W) ⊆ W` and stops before a characteristic polynomial.

## The canonical polynomial

On `W` for `chi`, the monic characteristic polynomials are

```text
chi_B(t) = t^4 (t - 8)^4 (t + 8)^4,
chi_A(x) = x^4 (x - 2)^4 (x + 2)^4,
```

with `chi_A(x) = 4^{-12} chi_B(4x)`. In ascending coefficients,

```text
chi_A = [0, 0, 0, 0, 256, 0, -256, 0, 96, 0, -16, 0, 1].
```

The SHA256 of that JSON list is `589ce5d010f0e4c5cf6d78719150e69afee3650ddf71dd273b58de10a5082e45`, and the SHA256 of `chi_B` is `bf3564eac70bdbb2ff2e0041ca84c8f69f1f215e9ba5678f5a10d8b90804106a`.

The characteristic polynomial is the monic characteristic polynomial of the pinned integer matrix, recovered by a Hessenberg recurrence modulo primes past one million and the Chinese remainder theorem. The first prime is checked against determinants at five points, the degree-`11` coefficient is checked against the trace, and every coefficient lies inside the binomial row-sum bound. The relation `chi_A(x) = 4^{-12} chi_B(4x)` is the divisibility of those coefficients by the matching power of `4`.

The polynomial `t(t - 8)(t + 8)` annihilates the matrix of `B`. Omitting any one of the three linear factors leaves a polynomial that does not annihilate. The minimal polynomial of `A_1` on `W` is therefore `x(x - 2)(x + 2)`.

The kernels of `B`, `B - 8I` and `B + 8I` each have dimension `4`, and their twelve basis vectors are linearly independent. They form a basis of `W`. On each kernel, `B` acts by the corresponding scalar `0`, `8` or `-8`. For an eigenvalue `λ` of `A_1` in `{0, 2, -2}`, the Lagrange polynomial

```text
e_λ(t) = product_{μ ≠ λ} (t - 4μ) / (4λ - 4μ)
```

evaluated at `B` is the projection onto the `λ`-eigenspace along the other two. Any subspace invariant under `B` is invariant under these three projections, so it is the sum of its intersections with the eigenspaces. A scalar operator leaves every subspace invariant, so the `A_1`-invariant subspaces of `W` are exactly `U_0 ⊕ U_2 ⊕ U_{-2}` with `U_λ` an arbitrary subspace of the `λ`-eigenspace of `A_1`.

In particular `W` is reducible under `A_1`. An explicit proper nonzero invariant subspace is `ker B`, of dimension `4`. An explicit invariant line is the span of

```text
(0, 0, 0, 0, 0, 0, 0, 1, 0, -1, 0, 0)
```

in the pinned basis of `W`. The matrix of `B` sends that vector to zero. The irreducible `A_1`-subspaces of this `W` are the lines inside the three eigenspaces.

## The twin copy

PR #7082 builds the same minus space on `chi'` for this same `u`. The trace and the ranks `36` and `12` agree with the canonical character. The characteristic polynomial does not. On that copy,

```text
chi_A(x) = x^2 (x - 2)^2 (x + 2)^2 (x^3 - 12x - 8)(x^3 - 12x + 8).
```

Both cubics are irreducible over `Q` by Rabin's test: each remains irreducible modulo at least one prime at or above `1009`. Ascending-coefficient SHA256 values are

```text
chi_A  c58d35de18567d24a9abeef5a3e536852d61ab429c03da1477f5792ad0cce841
chi_B  49655042b6738fa130d0297dc04113484e5b85bd2cbe61823f69a7f7bd1e696f
```

The square-free product of these five factors annihilates `B`, and omitting any one factor does not. The minimal polynomial therefore has degree `9`. The primary kernels have dimensions `2, 2, 2, 3, 3` and together form a basis. The three linear primaries are scalar. Each cubic primary has the corresponding cubic as the characteristic polynomial of `A_1` on that block, so each cubic block is irreducible under `A_1`. The kernel of `B` still has dimension `2`, so this copy is reducible under `A_1` as well.

## What the two calculations share, and where they stop

Both spaces belong to one involution, `u = (4 7)(5 6)`, and to the two 192-characters preserved by one element, `s`. The census in PR #7082 has 96 noncommuting involutions that cut `E` as `36 + 12` or `12 + 36`. This note does not compute their polynomials.

Each degree-12 polynomial divides the matching degree-48 coefficient list recorded by PR #7036 for the eigenvalue-`+1` space of `s` on the same character. The verifier multiplies those published factors and divides. It does not rebuild the 48-by-48 matrix, and a degree-12 factor is not that degree-48 polynomial.

The 36-dimensional plus space of this `u` is invariant under `B`, because `u` commutes with `B`, and its dimension is checked. Its characteristic polynomial is not computed. The exact dimension of `E ∩ h E`, for an element that preserves the character and does not preserve `E`, is not computed.

Sector `c = 3` is untouched. The degree-881 one-slot polynomial is untouched. Selected conditional kappa stays `363005817/100000000000`.
