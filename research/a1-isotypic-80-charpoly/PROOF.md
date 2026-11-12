# Characteristic polynomial of the 80-dimensional isotypic summand

This is an exact proof over `Q` for one invariant subspace of the historical
`c=1` doubled centre block. It is not a new minimal polynomial of the full
one-slot operator, not the characteristic polynomial of the 128-dimensional
isotypic component, and not a multiplication bound.

## Operator and the joint space

The input is the 8-by-112 query in `INTERFACE.json`, SHA256
`5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.
On `Q^8 ⊗ Q[F_2^9]`,

```text
A_1 = (1/4) sum_q r_q r_q^T ⊗ P_q(1),
B   = 4 A_1.
```

`P_q(1)` sends `e_a` to `e_{a+q}` when the least bit of `q` is 1, and to
`(-1)^{q·a} e_a` otherwise. The canonical basis of the trivial-character
`(+1,+1)` joint space `E` is the one pinned by
`research/a1-joint-216-charpoly/evidence/basis.json`, SHA256
`e198cd71f4100d2629ecc25fb40b135a8c18c7756be8bc80bf24d7b349af418a`.
Its dimension is 216, both by that file and by the trace formula

```text
(tr_V I + tr_V g + tr_V t + tr_V(gt)) / 4 = 216
```

for the order-16 sign stabilizer `H` of sector 1 and the involutions `g` and
`t` from the sign-stabilizer split. This note recomputes that basis and
checks it against the file. It does not recompute the degree-216
characteristic polynomial; it uses the published irreducible factors only
for the comparison below.

## The character and its projector

The signed permutations are the ones recorded for this dihedral image:

| name | `inv` | output signs |
|---|---|---|
| `u` | `(0, 1, 2, 3, 7, 6, 5, 4)` | all plus |
| `r` | `(0, 1, 6, 7, 3, 2, 5, 4)` | minus on coordinates 0 and 7 |

They satisfy `u^2 = 1`, `r^6 = 1`, `r` has order 6, and `u r u^{-1} = r^{-1}`.
The twelve words `r^k` and `r^k u` are distinct and preserve sector 1. Each
preserves `E`, and on the canonical basis of `E` each acts by a monomial
matrix with entries `±1`.

Let `ψ` be the linear character

```text
ψ(r^k) = (-1)^k,    ψ(r^k u) = (-1)^k.
```

The reflections are involutions and `ψ(r^{-k}) = ψ(r^k)`, so

```text
P = (1/12) sum_{k=0}^{5} (-1)^k (ρ(r^k) + ρ(r^k u)).
```

On the basis of `E`, the integer operator `12P` satisfies
`(12P)^2 = 12 · (12P)`, its trace is 960, and its image has rank 80.
Thus `P = (12P)/12` is a projector of trace 80. The trace of a projector
equals the dimension of its image, so

```text
W = im P
```

is 80-dimensional. The opposite sign on `u`, the character used for the
8-dimensional summand, has trace 96 and rank 8 under the same words. That
comparison identifies the sign. It does not recompute the characteristic
polynomial of the 8-dimensional summand.

`B` commutes with every element of `H`, with `g`, with `t`, and with all
twelve dihedral words, by direct comparison of the two operator orders on
all 4096 ambient basis vectors. Therefore `B` commutes with `P` and
preserves `W`.

## Explicit basis

Index the canonical basis of `E` by `e_0, ..., e_215`. A vector lies in `W`
exactly when `ρ(r)` acts by `-1` and `ρ(u)` acts by `+1`. Solving those
monomial equations gives 80 vectors. In the order of increasing least
component, with representative coefficient `+1`, they are a basis of the
solution space. Their supports in the 216-basis are disjoint, of size 1 for
24 vectors and size 3 for 56 vectors, and every coefficient is `±1`.
Thirty-two of the vectors use a minus sign away from the representative.
Each is fixed by `12P`, `r` acts by `-I`, and `u` acts by `+I`. They are
independent and lie in an image of rank 80, so they are a basis of `W`.

The first four vectors are

```text
w0 = e_0
w1 = e_1
w2 = e_2 + e_8 + e_26
w3 = e_3 + e_9 + e_27.
```

One vector that uses a minus sign is `e_96 + e_108 - e_138`. The full list
is `evidence/basis.json`, SHA256
`3391aa2d4ccafa5869d28f4a92dfa719c6b391f5bfeb1a03af9c15bfa5ea9910`.

## The matrix

In this basis the matrix `M` of `B` is an integer matrix. Every entry lies
in `-48..48`, the trace is 0, and not every entry is divisible by 4. If
`size_r` is the ambient support of the `r`-th basis vector, then
`size_r M_{r s} = size_s M_{s r}`, because `B` is symmetric on the ambient
space and these basis vectors are orthogonal. The two expansions of `B`, by
the precomputed columns and by the 112 ports, agree on every basis vector,
and the image of each basis vector lies in `W`.

The nonzero pattern of `M` has two connected components, each of size 40.
Both are `A_1`-invariant. The component containing `w_0` uses basis indices

```text
0, 1, 6, 7, 8, 9, 10, 11, 16, 17, 22, 23, 26, 27, 32, 33, 34, 35,
36, 37, 38, 39, 46, 47, 50, 51, 52, 53, 56, 57, 58, 59, 60, 61,
72, 73, 74, 75, 76, 77.
```

The other component is the complementary set of 40 indices. The matrix is
`evidence/matrix.json`, SHA256
`6ebe1cee465be2aba4626bd5700e4eebf3dd25e02712fed6129725eedacb7f69`.

The matrix of `A_1` is `M/4`. It is not an integer matrix entrywise. Its
characteristic polynomial is nevertheless in `Z[x]`, because
`chi_{A_1}(x) = 4^{-80} chi_B(4x)` and every coefficient of `chi_B` is
divisible by the required power of 4.

## Characteristic polynomial

`chi_B` is computed by the Hessenberg recurrence modulo primes whose product
exceeds twice the Gershgorin binomial bound
`max_k C(80,k) R^k`, where `R` is the maximum absolute row sum of the
matrix under consideration. The same calculation is run on `M` and on each
40-by-40 block. The Chinese remainder theorem lifts each polynomial, and
every coefficient lies inside the bound. The trace equals the negative of
the degree `n-1` coefficient.

On the first prime, the Hessenberg polynomial agrees with the Newton
interpolation of `det(tI - M)` at `t = 0, ..., n`. On the next two primes it
agrees with those determinants at `t = 0, 1, 2, 3, 5`. The characteristic
polynomials of the two blocks multiply to `chi_B`.

The resulting polynomial of `A_1` is monic of degree 80, even, and has
SHA256

```text
bd72312859b05d7cd69c5cc94e4768998cd033869ab9f157fdf9d2042b6bc0d2
```

of its ascending JSON coefficient list. The coefficient file is
`evidence/charpoly.json`, SHA256
`0881414a57133c69e3ebc1d78f9b40781bc8780c98db55692aeae5f8e75aba06`.

Let `f14` and `f16` be the following monic polynomials, copied from the
published factorisation of the degree-216 characteristic polynomial in
`research/a1-joint-216-charpoly/`:

```text
f14(x) = x^14 - 14x^13 - 180x^12 + 2824x^11 + 10112x^10 - 202144x^9
         - 173568x^8 + 6293376x^7 - 97024x^6 - 86923264x^5 + 8403968x^4
         + 453709824x^3 + 132964352x^2 - 739049472x - 498401280
f16(x) = x^16 + 12x^15 - 180x^14 - 2344x^13 + 11488x^12 + 173824x^11
         - 277632x^10 - 6136576x^9 - 321280x^8 + 105269248x^7
         + 108563456x^6 - 773404672x^5 - 1259880448x^4 + 1656389632x^3
         + 3560341504x^2 - 112656384x - 1702232064.
```

Both have even degree, so `f14(-x)` and `f16(-x)` are monic. Exact division
gives

```text
chi_{A_1,W}(x) =
    x^10 (x-2)^3 (x+2)^3 (x-6)^2 (x+6)^2 f14(x) f14(-x) f16(x) f16(-x).
```

The two quadratics `x^2 - 2x - 4` and `x^2 + 2x - 4`, both degree-11
factors, and both squared degree-14 factors of the published degree-216
polynomial do not divide `chi_{A_1,W}`. The factors that do occur are
irreducible over `Z`: the linear factors have degree 1, and each of `f14`,
`f14(-x)`, `f16` and `f16(-x)` is irreducible modulo one prime by the Rabin
test. The product of the copied degree-216 factors has the published SHA256
`18114a297071c454cb935ef85cab42a745954fb065be2a6d7e4ff23ef26b771b`, and
`chi_{A_1,W}` divides that polynomial. The quotient has degree 136.

On the block containing `w_0`,

```text
chi = x^6 (x-2)^2 (x+2)^2 (x-6) (x+6) f14(x) f14(-x).
```

On the other block,

```text
chi = x^4 (x-2) (x+2) (x-6) (x+6) f16(x) f16(-x).
```

These two polynomials multiply to `chi_{A_1,W}`.

## Evidence class

This is a proof by exact finite linear algebra over `Q`. The joint space is
the full solution of a finite sign system. The projector identity is checked
on every vector of a basis of that space. The trace of `P` equals the rank
of its image, so the eighty vectors are a basis of the whole isotypic
component.
The matrix entries, the divisibility by powers of 4, the factor
multiplication, and the block multiplication are integer identities. The
modular characteristic polynomials are determined by a finite prime product
larger than twice an a priori coefficient bound. No enumeration was stopped
early, and no floating-point approximation was used.

It is not an exhaustive census of the `c=1` stabilizer. It is not a
heuristic or incomplete search.

## What this does not say

Algebraic multiplicity 10 for eigenvalue 0 is the exponent of `x` above.
The geometric multiplicity, the nullity of `M`, is not computed.

The degree-136 quotient is the characteristic polynomial of `A_1` on any
complementary invariant subspace of `E`. It is not factored further here.
The 128-dimensional isotypic component of the two-dimensional rational
representation is a proper subspace of that complement, because the
8-dimensional linear summand is disjoint from `W` and also sits in `E`.
This note does not compute that 128-dimensional polynomial.

The 8-dimensional summand is not given a new matrix or a new polynomial.
The unique 32-dimensional `c=1` sign character and its four joint spaces of
dimension 8 are a different subspace.

The degree-881 one-slot annihilator is untouched. The selected conditional
kappa stays `781451/250000000`.
