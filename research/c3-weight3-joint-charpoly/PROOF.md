# Characteristic polynomial of one weight-3 c=3 joint space

This note computes the characteristic polynomial of one 12-dimensional joint
eigenspace of a weight-3 sign character in sector `c=3`. The selected
conditional kappa stays `781451/250000000`. Nothing here is a new minimal
polynomial of the full one-slot operator, a replay of the degree-881
certificate, a recomputation of the weight-4 polynomial, or a second
classification of the signed-permutation stabilizer.

Three claim types are used, and they are not interchangeable.

- A **proof** exhibits one basis, the matrix of the operator in that basis,
  the characteristic polynomial, and an eigenbasis. The identities are exact
  integer equalities.
- An **exhaustive finite census** evaluates that polynomial on every
  12-dimensional joint space of one named pair inside every weight-3
  character. The set, the enumeration, and the reason the list is complete
  are stated below.
- A **single witness** evaluates one other named pair. It is not a census of
  the cross-coset pairs.

## Operator

The input is the pinned 8-by-112 query, SHA256
`5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.
Its columns lie in `{-1,0,1}^8`, each has weight 4, and `R R^T = 56 I_8`.
The 112 port labels are distinct odd-parity vectors in `F_2^9`.

On `Q^8 ⊗ Q[F_2^9]`, of dimension 4096,

```text
A_3 = (1/4) sum_q r_q r_q^T ⊗ P_q(3),
B   = 4 A_3.
```

`P_q(3)` sends `e_a` to `e_{a+q}` when the `F_2` dot product `q·3` equals 1,
and to `(-1)^{q·a} e_a` otherwise. The dot product `q·3` is the parity of the
two low bits of `q`. Basis index `i*512+a` means query coordinate `i` and
address `a`.

Krzysztof Wojt's `research/exact-one-slot-gram/` gives the minimal polynomial
of the full one-slot operator, of degree 881, by a different reduction. This
note does not replay that certificate. It uses the published `c=3` sector
coefficient lists only for the divisibility comparison below.

## The weight-3 characters

`H` is the order-16 group of diagonal sign patterns that are positive on the
even coordinates `{0,2,4,6}` and arbitrary on the odd coordinates
`{1,3,5,7}`. Every element fixes sector 3. Characters of `H` are indexed by
`F_2^4` through those four odd coordinates. The weight of a character is the
Hamming weight of that index. Exactly four indices have weight 3, namely
`7, 11, 13, 14`. There is no fifth: the verifier enumerates all 16 indices.

Character 7, the least of the four, is

```text
chi(h) = product of the signs of h on coordinates 1, 3 and 5.
```

The trace formula gives dimension 80 on each of the four characters. An
explicit basis of the equations `h v = chi(h) v` also has dimension 80.

## Which joint space has dimension 12

Let `u` be the explicit involution `(0 2)(4 6)` with minus signs on
coordinates 0 and 2, and let `v` be `(0 4)(2 6)` with minus signs on
coordinates 0 and 4. Both fix sector 3, both square to the identity, and
they commute. Their product is `(0 6)(2 4)` with minus signs on coordinates
0 and 6. On every weight-3 character, the character traces of `u`, `v` and
`uv` are `+32`. The joint-dimension formula therefore gives

| `(u, v)` | dimension |
|---:|---:|
| `(+1, +1)` | 44 |
| `(+1, -1)` | 12 |
| `(-1, +1)` | 12 |
| `(-1, -1)` | 12 |

The explicit bases have those dimensions, so the lattice agrees with the
trace formula.

The source first step names the `(+1, +1)` space of character 7. That space
is 44-dimensional, so it is not a 12-dimensional joint space. The space
computed here is character 7 with eigenvalues `(u, v) = (+1, -1)`, the first
12-dimensional slot in the table above.

## The pinned basis

The basis is canonical. The equations partition the coordinates that are not
forced to zero. In each component the representative is the least index, its
coefficient is `+1`, and every other coefficient is the sign forced by the
equations. Components are ordered by increasing representative. Every vector
has support 8, and every coefficient is `±1`. The basis is stored in
`evidence/basis.json`.

Each of the twelve vectors satisfies the character equations and the
eigenvalue equations of `u` and `v` on all 4096 coordinates. The check is not
restricted to the support.

## The matrix

`B` preserves the space: the two expansions of `B`, one by the stored columns
and one by the 112 ports, agree on every basis vector and land in the space.
In this basis the matrix `M` of `B` is

```text
0  0  0  0  0  0  0  0  4  4  0  0
0  0  0  0  0  0  0  0  4  4  0  0
0  0  0  0  0  0  0  0  0  0  4  4
0  0  0  0  0  0  0  0  0  0  4  4
0  0  0  0  8  0  0  0  0  0  0  0
0  0  0  0  0 -8  0  0  0  0  0  0
0  0  0  0  0  0 -8  0  0  0  0  0
0  0  0  0  0  0  0  8  0  0  0  0
4  4  0  0  0  0  0  0  0  0  0  0
4  4  0  0  0  0  0  0  0  0  0  0
0  0  4  4  0  0  0  0  0  0  0  0
0  0  4  4  0  0  0  0  0  0  0  0
```

Every omitted entry in that display is zero. The pinned matrix is
`evidence/matrix.json`. It is the orthogonal sum, up to the displayed order,
of two 4-by-4 blocks and four 1-by-1 blocks.

On coordinates `(0, 1, 8, 9)` and again on `(2, 3, 10, 11)`, the block is

```text
[[0, 0, 4, 4],
 [0, 0, 4, 4],
 [4, 4, 0, 0],
 [4, 4, 0, 0]].
```

Its characteristic polynomial is `x^2 (x - 8)(x + 8)`. Direct multiplication
gives the eigenvectors below; the eigenvalues of this block of `B` are
`8, -8, 0, 0`. The four scalar entries are `8, -8, -8, 8` on coordinates
`4, 5, 6, 7`. Therefore

```text
chi_B(x)   = x^4 (x - 8)^4 (x + 8)^4,
chi_{A_3}(x) = x^4 (x - 2)^4 (x + 2)^4,
```

and `chi_{A_3}(x) = 4^{-12} chi_B(4x)`. Both polynomials are monic of degree
12 in `Z[x]`. The SHA256 hex digests of the JSON arrays of ascending
coefficients are

```text
chi_A  589ce5d010f0e4c5cf6d78719150e69afee3650ddf71dd273b58de10a5082e45
chi_B  bf3564eac70bdbb2ff2e0041ca84c8f69f1f215e9ba5678f5a10d8b90804106a
```

The weight-4 calculation does not determine these polynomials. On the
weight-4 character the recorded polynomials are `x^8 (x - 2)^4 (x + 2)^4`
for one 16-dimensional summand and `x^4 (x - 2)^2 (x + 2)^2` for one
8-dimensional joint space. The degree-16 ascending coefficient list is the
degree-12 list above preceded by four zeros. That comparison was made after
this matrix had been computed from the weight-3 equations. The weight-4
matrix was not an input, and this note does not rebuild it.

## Eigenbasis of the pinned space

On a scalar entry `8` of `B`, the corresponding axis vector has eigenvalue
`2` for `A_3`. On a scalar entry `-8`, it has eigenvalue `-2`. The two
4-by-4 blocks use the same four patterns. In coordinates `(a, b, c, d)` of
either block,

| vector | eigenvalue of `A_3` |
|---|---:|
| `(1, 1, 1, 1)` | 2 |
| `(1, 1, -1, -1)` | -2 |
| `(1, -1, 1, -1)` | 0 |
| `(1, -1, -1, 1)` | 0 |

Each identity is four integer multiplications. The four pattern vectors, as
columns, have determinant `-16`, so they are linearly independent. They use
different coordinates from the four axis vectors and from the other block.
The twelve vectors are therefore a basis of eigenvectors over `Q`. Geometric
multiplicities equal the algebraic multiplicities: 4 for eigenvalue 0, 4 for
eigenvalue 2, and 4 for eigenvalue `-2`. Thus `A_3` is diagonalizable over
`Q` on this space.

The Newton characteristic polynomial of `M` equals the block product. The
Hessenberg characteristic polynomial modulo `1000003` agrees, as do the
determinants of `xI - M` at `x = 0, 1, 2, 3, 5, 8, -8`.

## The twelve spaces of the explicit pair

The four weight-3 characters are exactly the Hamming-weight-3 elements of
`F_2^4`, enumerated above. For the explicit pair `(u, v)`, each character has
joint dimensions `44, 12, 12, 12` in the sign order of the table, by the
trace formula and by the lattice. The twelve 12-dimensional spaces are
exactly the three sign slots other than `(+1, +1)` on each of those four
characters. There are no further weight-3 characters and, for this pair, no
further 12-dimensional joint slots.

On each of the twelve spaces, every basis vector has support 8 and satisfies
the character equations and the two eigenvalue equations. `B` preserves the
space, the characteristic polynomial of `A_3` is
`x^4 (x - 2)^4 (x + 2)^4`, and `x(x - 8)(x + 8)` kills the matrix of `B`.
The minimal polynomial therefore divides a square-free polynomial, so each
space is diagonalizable over `Q`. Combined with the characteristic
polynomial, the geometric multiplicities are again 4, 4 and 4 for eigenvalues
`0`, `2` and `-2` of `A_3`.

The twelve matrices are not claimed to equal the pinned matrix. The census
evaluates the characteristic polynomial and the annihilating polynomial.

## One odd-sign witness

Let `u'` be `(0 2)(4 6)` with minus signs on coordinates 0, 2 and 1, and let
`v'` be `(0 4)(2 6)` with minus signs on coordinates 0, 4 and 1. Both fix
sector 3, both square to the identity, and they commute. The odd minus is
coordinate 1 only. On character 7, the character traces of `u'`, `v'` and
`u'v'` are `-32`, `-32` and `+32`. The joint dimensions are `12, 12, 12, 44`
for `(+1, +1)`, `(+1, -1)`, `(-1, +1)` and `(-1, -1)`. The 44-dimensional
slot has moved. Each of the three 12-dimensional spaces has the same
characteristic polynomial, and `x(x - 8)(x + 8)` kills each matrix of `B`.

This is one pair on one character. It is not an enumeration of the 3072
cross-coset pairs, and it does not ask whether an odd-sign pattern splits the
weight-4 degree-16 polynomial into two different degree-8 factors.

## Sector comparison

The irreducible factors `x`, `x - 8` and `x + 8` of `chi_B` each divide all
four published minimal polynomials of the `c=3` Bell sectors `(t, s)` in
`research/exact-one-slot-gram/CERTIFICATE.json`. Those four polynomials are
part of the degree-881 minimal polynomial of the full integer one-slot
operator. The comparison evaluates the published coefficient lists at
`0`, `8` and `-8`. It does not rerun the degree-881 certificate, and it does
not recompute the least common multiple.

## What is not claimed

The characteristic polynomial of the 44-dimensional `(+1, +1)` space is not
computed. The same polynomial on every cross-coset pair is not proved; one
odd-sign pair was evaluated and the rest were not. These subspaces do not
replace the degree-881 certificate. The selected conditional kappa stays
`781451/250000000`. No κ change is claimed.

A failed search was not used. The pinned polynomial is the product of the
block characteristic polynomials, checked against the Newton identities and
against the Hessenberg characteristic polynomial modulo `1000003`. The
twelve-space statement is the complete evaluation of the named list. The
odd-sign statement is one pair.
