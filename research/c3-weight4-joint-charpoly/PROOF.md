# Characteristic polynomial of one weight-4 c=3 summand

This note computes the characteristic polynomial of one 16-dimensional
invariant subspace of the weight-4 sign character in sector `c=3`. The
selected conditional kappa stays `781451/250000000`. Nothing here is a new
minimal polynomial of the full one-slot operator, a replay of the degree-881
certificate, or a second classification of the signed-permutation stabilizer.

Two claim types are used, and they are not interchangeable.

- A **proof** exhibits one basis, the matrix of the operator in that basis,
  the characteristic polynomial, and an eigenbasis. The identities are exact
  integer equalities.
- An **exhaustive finite evaluation** computes the same polynomial on every
  element of a named list of 96 involutions. The list is the list described
  by `research/c3-centre-sign-split`. This note checks every element of that
  list. It does not repeat the proof that no other signed permutation splits
  every c=3 character.

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

## The weight-4 character

`H` is the order-16 group of diagonal sign patterns that are positive on the
even coordinates `{0,2,4,6}` and arbitrary on the odd coordinates
`{1,3,5,7}`. Every element fixes sector 3. The weight-4 character is the
unique character of weight 4,

```text
chi(h) = product of the signs of h on coordinates 1, 3, 5 and 7.
```

The trace formula gives dimension 32. An explicit basis of the equations
`h v = chi(h) v` also has dimension 32.

## One 16-dimensional summand, and the 8-dimensional joint spaces

Let `u` be the explicit involution `(0 2)(4 6)` with minus signs on
coordinates 0 and 2, and let `v` be `(0 4)(2 6)` with minus signs on
coordinates 0 and 4. Both fix sector 3, both square to the identity, and
they commute. Their product is `(0 6)(2 4)` with minus signs on coordinates
0 and 6. The predecessor records that the character trace of every splitting
involution on this character is 0, so each one-involution eigenspace has
dimension `(32+0)/2 = 16`. The explicit bases have those dimensions.

The four joint eigenspaces of `u` and `v` inside the character each have
dimension 8. The sentence in the predecessor that the trace formula gives
dimension 8 is this finer count. The 16-dimensional summand named in the
question is one eigenspace of a single involution. It is the sum of two of
the 8-dimensional joint spaces.

The basis of the `u = +1` space is canonical. The equations partition the
coordinates that are not forced to zero. In each component the representative
is the least index, its coefficient is `+1`, and every other coefficient is
the sign forced by the equations. Components are ordered by increasing
representative. Every vector has support 16. The basis is stored in
`evidence/basis.json`.

In that basis, write `e_0, ..., e_15` for the ordered vectors. The joint
`(+1,+1)` vectors are the differences `e_i - e_{i+8}`, and the joint
`(+1,-1)` vectors are the sums `e_i + e_{i+8}`, for `i = 0, ..., 7`. Each of
those sums has support 32. The same count and the same polynomial hold for
the two joint spaces inside `u = -1`.

## The matrix

`B` preserves the `u = +1` space: the two expansions of `B`, one by the
stored columns and one by the 112 ports, agree on every basis vector and
land in the space. In this basis the matrix `M` of `B` is the orthogonal
sum of two copies of one 8-by-8 block `C`. The off-diagonal blocks are zero.
`C` is itself the orthogonal sum of four 2-by-2 blocks,

```text
[[-4, 4], [4, -4]]   on pairs (0, 5) and (1, 4),
[[ 4, 4], [4,  4]]   on pairs (2, 7) and (3, 6).
```

The second copy of `C` repeats those pairs shifted by 8. Every other entry
is 0. The pinned matrix is `evidence/matrix.json`. The matrix of `A_3` is
`M/4`, so the blocks become `[[-1,1],[1,-1]]` and `[[1,1],[1,1]]`.

The first 2-by-2 block of `B` has characteristic polynomial `x(x+8)`. The
second has `x(x-8)`. Therefore, on the 16-dimensional space,

```text
chi_B(x)   = x^8 (x-8)^4 (x+8)^4,
chi_{A_3}(x) = x^8 (x-2)^4 (x+2)^4,
```

and `chi_{A_3}(x) = 4^{-16} chi_B(4x)`. Both polynomials are monic of degree
16 in `Z[x]`. The SHA256 hex digests of the JSON arrays of ascending
coefficients are

```text
chi_A  4207a8e80e73e3fcd16abc6cba001f8e9881023742eeb587cbd8fbadd9f24350
chi_B  5030313ecab6822bd390a9e6847a3b6a9c9d701d2e7e247d7892ce5f55bfe717
```

Each joint space inherits one copy of `C`. Its characteristic polynomials are

```text
chi_B(x)     = x^4 (x-8)^2 (x+8)^2,
chi_{A_3}(x) = x^4 (x-2)^2 (x+2)^2.
```

The degree-16 polynomial is the square of this degree-8 polynomial. All four
joint sign pairs of the explicit `(u,v)` have this same degree-8 polynomial.
Ascending-coefficient SHA256 values are

```text
chi_A  4078d16db1834dcd427c4f1094b96838a2c425c116c7cd1b60d46aa1f472f632
chi_B  04375398447c3b08683582cc785814e9955ed62fcaa6725dc3467484c8a41457
```

## Eigenbasis of the pinned space

On a block `[[-1,1],[1,-1]]` of `A_3`, the vector `(1,1)` has eigenvalue 0
and `(1,-1)` has eigenvalue `-2`. On a block `[[1,1],[1,1]]`, the vector
`(1,-1)` has eigenvalue 0 and `(1,1)` has eigenvalue 2. These 16 vectors use
disjoint coordinate pairs. Each pair contributes a 2-by-2 change-of-basis
matrix of determinant `-2` or `2`, so the 16 vectors are linearly
independent. Thus `A_3` is diagonalizable over `Q` on this space. Geometric
multiplicities equal the algebraic multiplicities: 8 for eigenvalue 0, 4 for
eigenvalue 2, and 4 for eigenvalue `-2`.

The same block reading gives multiplicities 4, 2 and 2 on each 8-dimensional
joint space of the explicit pair.

## The described list of 96 involutions

The predecessor describes 96 involutions: the three permutations

```text
(0 2)(4 6),   (0 4)(2 6),   (0 6)(2 4),
```

each 2-cycle uniformly signed, the two cycles carrying opposite signs, and
the four odd signs arbitrary. That is `3 · 2 · 16 = 96` elements. This note
rebuilds all 96 from that description. Each is a symmetry of the query, fixes
sector 3, and squares to the identity. On the weight-4 character, both
eigenspaces are 16-dimensional, `B` preserves each, and the characteristic
polynomial of `A_3` on each is `x^8 (x-2)^4 (x+2)^4`.

Each corresponding matrix of `B` is killed by `x(x-8)(x+8)`. The minimal
polynomial therefore divides a square-free polynomial, so every one of these
192 spaces is diagonalizable over `Q`. Combined with the characteristic
polynomial, the geometric multiplicities are again 8, 4 and 4 for eigenvalues
0, 2 and `-2` of `A_3`.

This is an evaluation of every element of the described list, both
eigenvalues. Completeness of the list, as the set of all residual signed
permutations that split every c=3 character, is the census in
`research/c3-centre-sign-split`. It is not repeated here. In particular, a
pattern that puts the same sign on both even cycles is not in the list. The
all-even-minus pattern on `(0 2)(4 6)` is still a symmetry and sends sector 3
to 48.

## Sector comparison

The irreducible factors `x`, `x-8` and `x+8` of `chi_B` each divide all four
published minimal polynomials of the `c=3` Bell sectors `(t,s)` in
`research/exact-one-slot-gram/CERTIFICATE.json`. Those four polynomials are
part of the degree-881 minimal polynomial of the full integer one-slot
operator. The comparison evaluates the published coefficient lists at
`0`, `8` and `-8`. It does not rerun the degree-881 certificate, and it does
not recompute the least common multiple.

## What is not claimed

The characteristic polynomial of `A_3` on the whole 32-dimensional character
is the square

```text
x^{16} (x-2)^8 (x+2)^8,
```

because the character is the direct sum of the two 16-dimensional eigenspaces
of `u` and those two spaces have the same polynomial. That is a corollary for
this character and this operator. It does not bound the minimal polynomial of
any other character, and it does not replace the degree-881 certificate.

The degree-8 polynomial is proved for the four joint spaces of the explicit
pair `(u,v)` only. It is not proved for every cross-coset pair among the 96.
The selected conditional kappa stays `781451/250000000`. Payload involutions
are outside this signed-permutation calculation. No κ change is claimed.

A failed search was not used. The 16-dimensional polynomial is the product of
the eight 2-by-2 characteristic polynomials, checked against the Newton
identities and against the Hessenberg characteristic polynomial modulo
`1000003`. The 96-element statement is the complete evaluation of the
described list.
