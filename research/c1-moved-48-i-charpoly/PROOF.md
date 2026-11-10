# Characteristic polynomial over Q(i) of one eigenvalue-i eigenspace

This is a finite exact computation for one invariant subspace of the `c=1`
block of the historical one-slot doubled centre operator. It is not a new
minimal polynomial of the full operator and not a change of the selected
conditional kappa.

Evidence class: a proof, by exact linear algebra over `Q(i)`, of the
characteristic polynomial of one explicitly presented matrix. The basis is
the full solution of a finite monomial equation system. The polynomial is
recovered by exact interpolation of `49` determinants. This is not a modular
image and not an incomplete search.

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
coordinate `i` and address `a`. Extend scalars to `Q(i)`.

## The subspace

The sign stabilizer `H` is the order-16 group of coordinate sign patterns
with positive sign on coordinate 0 whose label map fixes sector 1. The
character

```text
chi_12(eps) = eps[1] * eps[2]
```

has dimension 192. The element

```text
s = (0 4 3 7)(5 6), all signs +1,
```

lies in the `c=1` stabilizer, has order 4, fixes sector 1, and preserves
`chi_12`. On this character the power traces of `1, s, s^2, s^3` are
`192, 0, 0, 0`, so the complex eigenvalue multiplicities of `1, i, -1, -i`
are `48, 48, 48, 48`. The involution `g = (1 2)(5 6)`, with signs on
coordinates 4 and 7, preserves the character. The involution
`t = (1 5)(2 6)`, with signs on coordinates 3 and 7, moves it.

Let `W` be the set of vectors in the `chi_12` character space, over `Q(i)`,
with `s v = i v`. The equations are monomial. For a signed permutation `rho`
and a scalar `lambda` in `{±1, ±i}`,

```text
(rho v)[dest[src]] = sign[src] * v[src],
```

so `rho v = lambda v` is the family of equations

```text
v[dest[src]] = sign[src] * (1/lambda) * v[src].
```

For `lambda = i`, the reciprocal is `-i`. For each character value `±1`, the
reciprocal equals the value. A union-find on these equations, with relative
coefficients in the unit group `{±1, ±i}`, closes every consequence. A
component whose relations disagree is set to zero. Every solution is the
`Q(i)`-span of one vector per live component. In that vector the least index
has coefficient `+1` and every other coefficient is the forced unit. The
supports are disjoint, so the vectors are linearly independent. This is an
exhaustive solution of a finite linear system.

The resulting basis of `W` has dimension 48, matching the multiplicity of
eigenvalue `i`. Direct application checks that every basis vector is fixed by
`H` through `chi_12` and sent by `s` to `i` times itself. Support sizes are
8 (eight vectors), 16 (thirty-two vectors), and 32 (eight vectors). The same
count with reciprocal `i` gives the eigenvalue-`-i` space, also of dimension
48. Using reciprocal `i` while testing eigenvalue `i` produces no eigenvector.

## The matrix

`B` commutes with every element of `H` and with `s`, checked on all 4096
basis vectors. Therefore `B` preserves `W`. Two expansions of `B`, one by
columns and one by the 112 ports, agree on every basis vector. In the ordered
basis, the matrix `M` of `B` has entries in `Z[i]`. The real parts lie in
`-16..16` and the imaginary parts lie in `-4..4`, and both endpoints occur.
Because the basis vectors are Hermitian-orthogonal with squared norms equal
to their support sizes,

```text
size_r * conjugate(M_rs) = size_s * M_sr.
```

The matrix of `A_1` on `W` is `M/4`. The basis and the matrix are pinned in
`evidence/basis.json` and `evidence/matrix.json`.

## Characteristic polynomial

Let `chi_B(x) = det(x I - M)`. For each integer `t` from 0 through 48,
`chi_B(t)` is the determinant of `t I - M`, computed by fraction-free
elimination over `Z[i]` with the exactness of every division checked. The
monic polynomial of degree 48 is the unique polynomial of degree at most 48
taking those 49 values, converted from the Newton form over `Q(i)`. All 49
coefficients lie in `Z[i]`, the leading coefficient is 1, and the coefficient
of `x^47` equals minus the trace. Reducing that polynomial modulo the inert
prime `1000003` agrees with an independent Hessenberg recurrence over the
field `F_{1000003}[i]`. The Hessenberg image is a cross-check. The polynomial
itself is the exact interpolant.

Every coefficient of `chi_B` is a rational integer divisible by
`4^{48-k}` in degree `k`, and the imaginary part is 0. Therefore

```text
chi_{A_1}(x) = 4^{-48} chi_B(4x)
```

lies in `Z[x]` and is monic of degree 48. The SHA256 hex digests of the JSON
arrays of ascending coefficients are

```text
chi_A  248dde5357601a63a3e5b548e370f6025e6cc457204723a43413d2eaa79833e3
chi_B  d2d03090e33a628beb31eb51a8f332ec5ccbb18800a56f25186815bde4d81ffd
```

The same computation on the eigenvalue-`-i` space returns the conjugate
coefficient list. The two lists are equal, so the two eigenspaces are
isospectral.

The monic irreducible factorization over `Q(i)` is

```text
chi_{A_1}(x) =
    x^10
  * (x - 2)^5
  * (x + 2)^5
  * (x^3 - 8x^2 + 4x + 32)
  * (x^3 - 12x - 8)
  * (x^3 - 12x + 8)
  * (x^3 + 8x^2 + 4x - 32)
  * (x^8 - 6x^7 - 56x^6 + 296x^5 + 704x^4 - 3264x^3 - 1728x^2 + 7296x - 3072)
  * (x^8 + 6x^7 - 56x^6 - 296x^5 + 704x^4 + 3264x^3 - 1728x^2 - 7296x - 3072).
```

The factors multiply back to `chi_{A_1}`. Each factor of positive degree is
irreducible over `Q(i)`:

- A degree-1 factor is irreducible.
- Each cubic is monic in `Z[x]` and has no integer root, so it is irreducible
  over `Q`. A root in `Q(i)` outside `Q` would force a distinct conjugate
  root and a quadratic factor over `Q`. An irreducible cubic has no quadratic
  factor. So each cubic stays irreducible over `Q(i)`.
- Each octic is irreducible modulo `1019`, by the Rabin test, so it is
  irreducible over `Q`. A proper monic factor over `Q(i)` is, by Gauss's
  lemma for the UFD `Z[i]`, a monic factor in `Z[i][x]`. Conjugation preserves
  the octic. An orbit of size 1 would be a proper factor over `Q`. An orbit
  of size 2 has equal degrees and multiplies to a proper factor over `Q`
  unless both degrees are 4, in which case the octic is a product of a monic
  quartic and its conjugate. That product has constant term equal to a norm
  from `Z[i]` to `Z`, hence a nonnegative integer. Both octics have constant
  term `-3072`. So neither octic factors over `Q(i)`.

The polynomial is not square-free. Algebraic multiplicity of eigenvalue 0 is
10, and algebraic multiplicity of each of `±2` is 5. It is not the minimal
polynomial of `A_1` on `W`.

Every irreducible factor of `chi_B` divides at least one published minimal
polynomial of the `c=1` Bell sectors `(t,s)` in
`research/exact-one-slot-gram/CERTIFICATE.json`. The linear factors divide
all four. The comparison reads those coefficients. It does not replay the
degree-881 certificate.

The same explicit polynomial, including the same ascending-coefficient
digest, is the polynomial recorded by open PR #7036 for the eigenvalue-`±1`
spaces of the other `s`-preserved character `eps[5] * eps[6]`. The two
statements concern different subspaces. This package recomputes the
polynomial on `W` and does not rebuild that eigenvalue-`±1` matrix.

## Verification

`verify.py` uses CPython 3.12 and the standard library. Rejection controls
refuse a coordinate transposition, a swapped port label, a character-sign
flip that still claims dimension 48, the reciprocal `i` in place of `-i`, a
one-entry change of `M`, a missing factor, a one-coordinate sign error, and
conjugation of a basis vector that still claims eigenvalue `i`. On the
eigenvalue-`+1` equations, the Gaussian lattice reproduces the integer
orbit basis. Dropping `s` leaves the 192-dimensional character space.

Not run: Lean, Docker, the degree-881 replay, the selected cold replay, and
the exact nullity of `M`.

## What this does not say

A 48-dimensional invariant subspace does not replace the degree-881 minimal
polynomial. The selected conditional kappa stays `781451/250000000`. The
polynomial is not the characteristic polynomial of the eigenvalue-`±1` space
computed in PR #7036, even though the two explicit polynomials coincide with
the polynomial of a different character. Sector `c=3` is not treated. The
216-dimensional joint eigenspace of `g` and `t` is a different subspace.
Geometric multiplicity of eigenvalue 0 on `M` is not computed. The
eigenvalue-`i` polynomial on `eps[5] * eps[6]` is not computed.
