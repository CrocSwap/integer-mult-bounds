# Characteristic polynomial of one 216-dimensional joint eigenspace

This is a finite exact computation for one invariant subspace of the `c=1`
block of the historical one-slot doubled centre operator. It is not a new
minimal polynomial of the full operator, not a change of the selected
conditional kappa, and not a centralizer classification.

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
and to `(-1)^{q·a} e_a` otherwise. The dot product `q·1` is the least bit of
`q`. Basis index `i*512+a` means query coordinate `i` and address `a`.

Krzysztof Wojt's `research/exact-one-slot-gram/` already gives the minimal
polynomial of the full one-slot operator, of degree 881, by a different
reduction. This note does not replay that certificate. It uses the published
`c=1` sector coefficient lists only for the divisibility comparison below.

## The subspace

A signed coordinate permutation acts by `(S v)_k = eps[k] v[inv[k]]` and by
the orthogonal label map `U e_a = e_{T a}` induced by the image of the root
lines. The tensor operator is `S ⊗ U`. The two involutions are the ones from
the sign-stabilizer split:

| name | `inv = sigma^{-1}` | output signs `-1` |
|---|---|---|
| `g` | `(0, 2, 1, 3, 4, 6, 5, 7)` | coordinates 4 and 7 |
| `t` | `(0, 5, 6, 3, 4, 1, 2, 7)` | coordinates 3 and 7 |

Both square to the identity, they commute, both preserve sector 1, and `g`
sends sector 3 to 343. The sign stabilizer `H` is the order-16 group of
coordinate sign patterns with positive sign on coordinate 0 whose label map
fixes sector 1.

Let `V` be the set of vectors fixed by every element of `H`, by `g`, and by
`t`. This is the joint `(+1,+1)` eigenspace of `g` and `t` inside the trivial
character space of `H`. The trace formula gives character dimension 864 and
joint dimension 216. An explicit basis of the same equations has those same
dimensions, and direct application shows that `g` and `t` preserve the
864-dimensional space. The three other joint sign pairs also have dimension
216. Omitting `g` leaves the 432-dimensional space fixed by `H` and by `t`.

The basis of `V` is canonical. The equations `v_{ρ(e_j)} = σ_j v_j`, as `ρ`
runs through `H`, `g`, and `t`, partition the coordinates that are not forced
to zero. In each component the representative is the least index, its
coefficient is `+1`, and every other coefficient is the unique sign forced by
the equations. Components are ordered by increasing representative. The basis
is stored in `evidence/basis.json`. Support sizes are only 1, 4, 8, and 16.

## The matrix

`B` commutes with every element of `H` and with `g` and `t`, checked on all
4096 basis vectors by comparing two actions of each signed permutation on the
columns of `B`. Therefore `B` preserves `V`. Two independent expansions of
`B`, one by columns and one by the 112 ports, agree on every basis vector of
all four joint spaces.

In the ordered basis above, the matrix `M` of `B` has integer entries, and
`M_{r s}` is the value of `B v_s` at the representative of component `r`.
The pinned matrix is `evidence/matrix.json`. Every entry lies in `-28..28`.
If `size_r` is the support of the `r`-th basis vector, then
`size_r M_{r s} = size_s M_{s r}`, because `B` is symmetric and the basis
vectors are orthogonal with squared norms `size_r`.

The matrix of `A_1` on `V` is `M/4`.

## Characteristic polynomial

Let `chi_B(x) = det(x I - M)` and `chi_{A_1}(x) = det(x I - M/4)`. Then
`chi_{A_1}(x) = 4^{-216} chi_B(4x)`, and both polynomials are monic of degree
216 in `Z[x]`. Both are even: only even powers occur. The SHA256 hex digests
of the JSON arrays of ascending coefficients are

```text
chi_A  18114a297071c454cb935ef85cab42a745954fb065be2a6d7e4ff23ef26b771b
chi_B  ec79276843b69dc6e064cdcb009a238e8231d0a8bf8f9c532c679c6a0cb6a81e
```

The irreducible factorization over `Z` is

```text
chi_{A_1}(x) =
    x^24
  * (x - 2)^12
  * (x + 2)^12
  * (x - 6)^2
  * (x + 6)^2
  * (x^2 - 2x - 4)
  * (x^2 + 2x - 4)
  * (x^11 + 2x^10 - 108x^9 - 192x^8 + 3208x^7 + 2128x^6 - 33888x^5
       + 19264x^4 + 115776x^3 - 196352x^2 + 102144x - 12288)^2
  * (x^11 - 2x^10 - 108x^9 + 192x^8 + 3208x^7 - 2128x^6 - 33888x^5
       - 19264x^4 + 115776x^3 + 196352x^2 + 102144x + 12288)^2
  * (x^14 - 14x^13 - 180x^12 + 2824x^11 + 10112x^10 - 202144x^9
       - 173568x^8 + 6293376x^7 - 97024x^6 - 86923264x^5 + 8403968x^4
       + 453709824x^3 + 132964352x^2 - 739049472x - 498401280)
  * (x^14 + 14x^13 - 180x^12 - 2824x^11 + 10112x^10 + 202144x^9
       - 173568x^8 - 6293376x^7 - 97024x^6 + 86923264x^5 + 8403968x^4
       - 453709824x^3 + 132964352x^2 + 739049472x - 498401280)
  * (x^14 - 2x^13 - 112x^12 + 136x^11 + 4376x^10 - 3632x^9 - 76384x^8
       + 44928x^7 + 621184x^6 - 260736x^5 - 2179840x^4 + 704000x^3
       + 3049472x^2 - 702464x - 1167360)^2
  * (x^14 + 2x^13 - 112x^12 - 136x^11 + 4376x^10 + 3632x^9 - 76384x^8
       - 44928x^7 + 621184x^6 + 260736x^5 - 2179840x^4 - 704000x^3
       + 3049472x^2 + 702464x - 1167360)^2
  * (x^16 + 12x^15 - 180x^14 - 2344x^13 + 11488x^12 + 173824x^11
       - 277632x^10 - 6136576x^9 - 321280x^8 + 105269248x^7
       + 108563456x^6 - 773404672x^5 - 1259880448x^4 + 1656389632x^3
       + 3560341504x^2 - 112656384x - 1702232064)
  * (x^16 - 12x^15 - 180x^14 + 2344x^13 + 11488x^12 - 173824x^11
       - 277632x^10 + 6136576x^9 - 321280x^8 - 105269248x^7
       + 108563456x^6 + 773404672x^5 - 1259880448x^4 - 1656389632x^3
       + 3560341504x^2 + 112656384x - 1702232064).
```

The same polynomial is the characteristic polynomial of `A_1` on each of the
four joint sign spaces. The ascending coefficient lists and multiplicities
are the constant `FACTORS` in `verify.py`.

Each irreducible factor of `chi_B` divides at least one of the four published
minimal polynomials of the `c=1` Bell sectors `(t,s)` in
`research/exact-one-slot-gram/CERTIFICATE.json`. Those four polynomials are
part of the degree-881 minimal polynomial of the full integer operator `B`.
The comparison reads that coefficient list. It does not rerun the degree-881
certificate.

## Corollary

`x` and `x-2` both divide `chi_{A_1}`. Over `Q`, both are eigenvalues, so `V`
has a proper nonzero `A_1`-invariant subspace. This package does not construct
that subspace, does not compute a geometric multiplicity above 1, and does not
search the centralizer.

## Verification

`verify.py` uses CPython 3.12 and the standard library. It rebuilds the
matrix from the query, computes `chi_B` by the Hessenberg recurrence modulo
primes whose product exceeds twice the Gershgorin binomial coefficient bound,
and lifts by the Chinese remainder theorem. Determinants of `tI-M` at
`t=0,1,2,3,5` agree with that polynomial modulo the first three primes. The
pinned factors multiply back to `chi_{A_1}`. Quadratics are irreducible
because their discriminants are not squares. Each higher factor is irreducible
over `Z` because it is irreducible modulo one prime, by the Rabin test.

Rejection controls refuse a coordinate transposition, a swapped port label, a
flipped stabilizer sign that still claims dimension 216, a one-entry change of
`M` that preserves the polynomial modulo `1000003`, a missing factor, and a
one-coordinate sign error in a linked basis vector.

Not run: Lean, Docker, the degree-881 replay, and the selected cold replay.
Selected-baseline orientation returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`
for kappa `781451/250000000`.

## What this does not say

A 216-dimensional invariant subspace does not replace the degree-881 minimal
polynomial. The selected conditional kappa stays `781451/250000000`. Sector
`c=3` is not preserved by `g`, and this polynomial says nothing about it.
Algebraic multiplicity 24 for eigenvalue 0 is not a computation of the
rational nullity beyond the existence of at least one kernel vector.
