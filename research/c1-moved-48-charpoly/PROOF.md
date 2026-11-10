# Characteristic polynomial of one 48-dimensional eigenspace of s

This is a finite exact computation for one invariant subspace of the `c=1`
block of the historical one-slot doubled centre operator. It is not a new
minimal polynomial of the full operator, not a change of the selected
conditional kappa, and not a centralizer classification.

Evidence class: a proof, by exact linear algebra over `Q`, of the
characteristic polynomial of one explicitly presented matrix. The four real
eigenspaces below are an exhaustive list of the eigenvalue-`±1` spaces of
this one element `s` on the two 192-characters it preserves. That list is not
a census of every `A_1`-invariant subspace, and it does not include the
eigenvalue-`±i` spaces.

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

Krzysztof Wojt's `research/exact-one-slot-gram/` already gives the minimal
polynomial of the full one-slot operator, of degree 881, by a different
reduction. This note does not replay that certificate. It uses the published
`c=1` sector coefficient lists only for the divisibility comparison below.

## The subspace

The sign stabilizer `H` is the order-16 group of coordinate sign patterns
with positive sign on coordinate 0 whose label map fixes sector 1. Its
character dimensions are `{864: 1, 432: 4, 192: 6, 80: 4, 32: 1}`. A character
is the homomorphism sending a sign pattern `eps` to a value in `{±1}`.

The two dimension-192 characters preserved by

```text
s = (0 4 3 7)(5 6), all signs +1,
```

are exactly

```text
chi_12(eps) = eps[1] * eps[2],
chi_56(eps) = eps[5] * eps[6].
```

Coordinates are numbered `0..7`. In the lexicographic order of value tuples
on increasing sign masks, `chi_12` is the smaller character. Both have
dimension 192. The involution `g = (1 2)(5 6)`, with signs on coordinates 4
and 7, preserves both. The involution `t = (1 5)(2 6)`, with signs on
coordinates 3 and 7, moves both. So each is a moved character for the pair
`<g, t>` from the sign-stabilizer split, and neither is the trivial character
or the unique 32-dimensional character.

The element `s` lies in the `c=1` stabilizer, has order 4, and fixes sector
1. On each of these two characters the power traces are `192, 0, 0, 0`, so
the complex eigenvalue multiplicities of `1, i, -1, -i` are `48, 48, 48, 48`.

The canonical space `V` is the set of vectors in the `chi_12` character space
with `s v = v`. An explicit basis of those equations has dimension 48, and
direct application shows that every element of `H` acts by `chi_12` and that
`s` acts by `+1`. The eigenvalue-`-1` equations on the same character also
have dimension 48. The same two dimensions hold for `chi_56`.

The basis of `V` is canonical. The equations `v_{ρ(e_j)} = σ_j λ v_j`, as `ρ`
runs through `H` and through `s`, partition the coordinates that are not
forced to zero. In each component the representative is the least index, its
coefficient is `+1`, and every other coefficient is the unique sign forced by
the equations. Components are ordered by increasing representative. The basis
is stored in `evidence/basis.json`. Support sizes are 8 (eight vectors), 16
(thirty-two vectors), and 32 (eight vectors).

## The matrix

`B` commutes with every element of `H` and with `s`, checked on all 4096
basis vectors by comparing two actions of each signed permutation on the
columns of `B`. Therefore `B` preserves `V`. Two independent expansions of
`B`, one by columns and one by the 112 ports, agree on every basis vector of
all four real eigenspaces.

In the ordered basis above, the matrix `M` of `B` has integer entries in
`-16..16`, and both endpoints occur. `M_{r s}` is the value of `B v_s` at the
representative of component `r`. The pinned matrix is `evidence/matrix.json`.
If `size_r` is the support of the `r`-th basis vector, then
`size_r M_{r s} = size_s M_{s r}`, because `B` is symmetric and the basis
vectors are orthogonal with squared norms `size_r`.

The matrix of `A_1` on `V` is `M/4`.

## Characteristic polynomial

Let `chi_B(x) = det(x I - M)` and `chi_{A_1}(x) = det(x I - M/4)`. Then
`chi_{A_1}(x) = 4^{-48} chi_B(4x)`, and both polynomials are monic of degree
48 in `Z[x]`. Both are even: only even powers occur. The SHA256 hex digests
of the JSON arrays of ascending coefficients are

```text
chi_A  1230f7227b6cbd0ad1383273a601bb4f517462ca663235c673e6b6bb13f1b3af
chi_B  7505211cf6196c312dd5afce7307eb5ec8f63b89cfe0bd73463f9d5352535d7e
```

The irreducible factorization over `Z` is

```text
chi_{A_1}(x) =
    x^10
  * (x - 2)^6
  * (x + 2)^6
  * (x^5 - 4x^4 - 24x^3 + 80x^2 + 80x - 160)
  * (x^5 + 4x^4 - 24x^3 - 80x^2 + 80x + 160)
  * (x^8 - 4x^7 - 72x^6 + 240x^5 + 784x^4 - 2208x^3 + 1920x - 768)
  * (x^8 + 4x^7 - 72x^6 - 240x^5 + 784x^4 + 2208x^3 - 1920x - 768).
```

The eigenvalue-`-1` space of `chi_12` has this same characteristic polynomial.
The ascending coefficient lists and multiplicities are the constant `FACTORS`
in `verify.py`.

The other character `chi_56` is not isospectral to `chi_12`. On each of its
eigenvalue-`±1` spaces,

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
  * (x^8 + 6x^7 - 56x^6 - 296x^5 + 704x^4 + 3264x^3 - 1728x^2 - 7296x - 3072),
```

with ascending-coefficient SHA256

```text
chi_A  248dde5357601a63a3e5b548e370f6025e6cc457204723a43413d2eaa79833e3
chi_B  d2d03090e33a628beb31eb51a8f332ec5ccbb18800a56f25186815bde4d81ffd
```

Each irreducible factor of either `chi_B` divides at least one of the four
published minimal polynomials of the `c=1` Bell sectors `(t,s)` in
`research/exact-one-slot-gram/CERTIFICATE.json`. Those four polynomials are
part of the degree-881 minimal polynomial of the full integer operator. The
linear factors `x`, `x-8`, and `x+8` of `chi_B` divide all four sector
polynomials. The comparison reads that coefficient list. It does not rerun
the degree-881 certificate.

## Corollary

`x` and `x-2` both divide `chi_{A_1}` on `V`. Over `Q`, both are eigenvalues,
so `V` has a proper nonzero `A_1`-invariant subspace. Algebraic multiplicity
of eigenvalue 0 is 10, and algebraic multiplicity of each of `±2` is 6. The
polynomial is not square-free, so it is not the minimal polynomial of `A_1`
on `V`. This package does not construct the invariant subspace, does not
compute a geometric multiplicity, and does not search for an element of the
`c=1` stabilizer that preserves `chi_12`, fails to commute with `s`, and cuts
`V`.

## Verification

`verify.py` uses CPython 3.12 and the standard library. It rebuilds the
matrix from the query, computes `chi_B` by the Hessenberg recurrence modulo
primes whose product exceeds twice the Gershgorin binomial coefficient bound,
and lifts by the Chinese remainder theorem. Determinants of `tI-M` at
`t=0,1,2,3,5` agree with that polynomial modulo the first prime. The pinned
factors multiply back to `chi_{A_1}`. Each factor of degree 5 or 8 is
irreducible over `Z` because it is irreducible modulo one prime, by the Rabin
test. The linear factors are irreducible because they have degree 1.

Rejection controls refuse a coordinate transposition, a swapped port label, a
character-sign flip that still claims dimension 48, a one-entry change of `M`
that preserves the polynomial modulo `1000003`, a missing factor, and a
one-coordinate sign error in a linked basis vector. Dropping `s` leaves the
192-dimensional character space.

Not run: Lean, Docker, the degree-881 replay, and the selected cold replay.
Selected-baseline orientation returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`
for kappa `781451/250000000`.

## What this does not say

A 48-dimensional invariant subspace does not replace the degree-881 minimal
polynomial. The selected conditional kappa stays `781451/250000000`. The
eigenvalue-`i` and eigenvalue-`-i` spaces are 48-dimensional over `C`; their
characteristic polynomials are not computed. Sector `c=3` is not treated.
The 216-dimensional joint eigenspace of `g` and `t` is a different subspace,
and this polynomial is not that one. Transport of either polynomial onto a
192-character that this particular `s` does not preserve is not checked.
Existence of the eigenvalues `0` and `±2` does not exhibit a signed
permutation outside the centralizer of `s`.
