# Odd-sign cross-coset pairs do not split the weight-4 degree-16 polynomial

The selected conditional kappa stays `781451/250000000`. Nothing here changes
that frontier, replaces the degree-881 one-slot certificate, or reclassifies
the signed-permutation stabilizer.

Two claim types are used, and they are not interchangeable.

- A **proof for one named pair** exhibits the joint spaces, the integer
  matrices of `B = 4 A_3`, their characteristic polynomials, a spanning
  determinant, and the identity `B(B^2 - 64 I) = 0`.
- An **exhaustive finite census** checks every element of the described list
  of 96 splitting involutions, and every one of the 32 diagonal signs with
  equal even coordinates. The passage from those 96 operator identities to
  all `3072` unordered cross-coset pairs is the reduction below. It is not a
  sample. Completeness of the list of 96, as the set of all residual signed
  permutations that split every `c=3` character, is the census in
  `research/c3-centre-sign-split`. It is not repeated here.

## Operator and the weight-4 character

The input is the pinned 8-by-112 query, SHA256
`5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.
On `Q^8 ⊗ Q[F_2^9]`,

```text
A_3 = (1/4) sum_q r_q r_q^T ⊗ P_q(3),
B   = 4 A_3.
```

`P_q(3)` is the same sector-3 action used for the degree-16 polynomial in
upstream PR #7021. `H` is the order-16 group of diagonal signs that are
positive on the even coordinates `{0,2,4,6}` and arbitrary on the odd
coordinates `{1,3,5,7}`. The weight-4 character is

```text
chi(h) = product of the signs of h on coordinates 1, 3, 5 and 7.
```

The canonical signed-orbit basis of the equations `h v = chi(h) v` has
dimension 32. Call this space `W`.

## The named pair

Let `u0`, `v0` and `w0` be the explicit no-odd-minus involutions recorded by
#6965 and used again by #7021:

| name | permutation | minus signs |
|---|---|---|
| `u0` | `(0 2)(4 6)` | coordinates 0 and 2 |
| `v0` | `(0 4)(2 6)` | coordinates 0 and 4 |
| `w0` | `(0 6)(2 4)` | coordinates 0 and 6 |

The named pair keeps those even signs and puts a minus on odd coordinate 1
only:

| name | permutation | minus signs |
|---|---|---|
| `u` | `(0 2)(4 6)` | coordinates 0, 1 and 2 |
| `v` | `(0 4)(2 6)` | coordinates 0, 1 and 4 |

Both are in the described list of 96. Both fix sector 3, both square to the
identity, and they commute. Their product is exactly `w0`, whose odd signs
are all positive. The odd-sign pattern of the pair is nontrivial: coordinate
1 is negative and coordinates 3, 5 and 7 are positive.

The same odd signs with both even cycles left positive send sector 3 to 48.
So do equal minus signs on the two even cycles. Those patterns are symmetries
of the query, but they are not splitting involutions of sector 3 and they are
not the pair under test.

Let `d` be the diagonal sign with a minus on coordinate 1 only. The composite
that applies `u0` first and `d` second equals `u`, including the port map, and
the same composite with `v0` equals `v`. On `W`, `d` acts as `-I`.

## Direct factorisation of the named pair

Inside `W`, each of the four joint spaces of `(u, v)` has dimension 8. In the
canonical basis of each space the matrix of `B` has characteristic polynomial

```text
x^4 (x - 8)^2 (x + 8)^2,
```

so the characteristic polynomial of `A_3` is

```text
x^4 (x - 2)^2 (x + 2)^2.
```

Ascending-coefficient SHA256, matching the degree-8 fingerprint recorded by
#7021:

```text
4078d16db1834dcd427c4f1094b96838a2c425c116c7cd1b60d46aa1f472f632
```

Each matrix of `B` is killed by `x(x - 8)(x + 8)`. The minimal polynomial
therefore divides a square-free polynomial, so `A_3` is diagonalizable over
`Q` on each joint space. Algebraic and geometric multiplicities agree:
eigenvalue `0` has multiplicity 4, and eigenvalues `2` and `-2` each have
multiplicity 2.

The `u = +1` space and the `u = -1` space each have dimension 16. Each is the
direct sum of its two joint spaces: the sixteen joint basis vectors are
linearly independent modulo `1000003` when written in the canonical basis of
that 16-dimensional space. `B` preserves each joint space, so the
characteristic polynomial of the 16-dimensional space is the product of the
two degree-8 polynomials. Both factors are the same polynomial, and the
product is

```text
x^8 (x - 2)^4 (x + 2)^4,
```

SHA256

```text
4207a8e80e73e3fcd16abc6cba001f8e9881023742eeb587cbd8fbadd9f24350
```

which is the degree-16 polynomial recorded by #7021. The named pair therefore
does not split that polynomial into two different degree-8 factors.

The same canonical bases, with both eigenvalues flipped, are the four joint
bases of the explicit pair `(u0, v0)`. That identifies the spaces. It is not
a second factorisation of the no-odd-minus pair; #7021 already recorded that
pair.

## The other odd-sign patterns

A diagonal sign whose four even coordinates carry one common sign, and whose
odd signs are arbitrary, is one of 32 signs. All 32 fix sector 3. On `W`,
each acts by the scalar

```text
(product of its four odd signs) * (its common even sign).
```

In particular every element of `H` acts by `chi`, and the all-even-minus
diagonal acts by `-1`. This is checked on every vector of the 32-dimensional
basis, for every one of the 32 signs. A diagonal with unequal even signs need
not act by a scalar; the control with a minus on coordinate 0 only does not.

Every described splitting involution has the same coordinate permutation as
exactly one of `u0`, `v0` and `w0`. It equals the composite that applies that representative first and one of
the 32 diagonals second. The equality includes the port map. Therefore, on
`W`, the involution acts as that diagonal's scalar times the representative. Both scalars occur, 16 times in each of the three permutation
cosets.

The three representatives form one Klein group: `w0 = u0 v0`, and `u0` and
`v0` commute. Any cross-coset pair is an unordered pair of described
involutions from two different nontrivial cosets. There are
`3 · 32 · 32 = 3072` such pairs. On `W`, the pair acts as a pair of scalars
times two of `u0`, `v0` and `w0`. The four joint eigenspaces are the four
joint spaces of `(u0, v0)`, up to swapping eigenvalue labels. All four have
the degree-8 polynomial computed above. No described cross-coset pair splits
the degree-16 polynomial into two different degree-8 factors.

Same-coset pairs are not cross-coset pairs. The named `u` and the explicit
`u0` have the same permutation; on `W` they differ by the scalar `-1`, so
they do not give a four-way split.

## What is not claimed

The argument uses the weight-4 character in an essential way. On a weight-3
character the same explicit pair has joint dimensions `44 + 12 + 12 + 12`,
and the predecessor records that the slot of the large piece moves with the
trace signs. The scalar reduction above does not determine the characteristic
polynomial of one of those 12-dimensional spaces.

The list of 96 is an input description, not a new classification. Payload
involutions are outside that list. An involution that is not one of the 96
is not covered, so this is not an unrestricted nonexistence statement. No
κ change is claimed.

The characteristic polynomials were recomputed from the query by the Newton
identities and compared with the block products `x(x ± 8)`. A failed test of
one pair was not used as a universal negative. The 96-element statement is
the complete check of the described list.
