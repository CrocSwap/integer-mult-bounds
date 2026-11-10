# Characteristic polynomial on the 128-dimensional isotypic component

This is an exact computation in linear algebra over `Q`. It determines one
monic characteristic polynomial on one invariant subspace of the historical
`c=1` centre block. The selected conditional kappa stays
`781451/250000000`. The degree-881 minimal polynomial of the full one-slot
operator is not replayed.

## Operator and group

The input is the 8-by-112 query in `INTERFACE.json`, SHA256
`5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.
Its columns lie in `{-1,0,1}^8`, each has weight 4, the 112 port labels are
distinct odd-weight vectors in `F_2^9`, and `R R^T = 56 I_8`.

On `Q^8 ⊗ Q[F_2^9]`, of dimension 4096,

```text
A_1 = (1/4) sum_q r_q r_q^T ⊗ P_q(1),
B   = 4 A_1 = sum_q r_q r_q^T ⊗ P_q(1).
```

`P_q(1)` sends `e_a` to `e_{a+q}` when the least bit of `q` is 1, and to
`(-1)^{q·a} e_a` otherwise. The basis index `i*512+a` is query coordinate
`i` and address `a`.

`E` is the joint `(+1,+1)` space of the order-16 sign stabilizer of sector 1
and the involutions `g` and `t`. The trace formula gives dimension 216. The
recomputed signed-orbit basis equals the basis pinned by
`research/a1-joint-216-charpoly/evidence/basis.json`. On that basis, the
port formula for `B` reproduces `evidence/matrix.json`.

The dihedral image `G` has order 12. Its generators are the signed
permutations

| name | `inv` | output signs `-1` |
|---|---|---|
| `u` | `(0, 1, 2, 3, 7, 6, 5, 4)` | none |
| `r` | `(0, 1, 6, 7, 3, 2, 5, 4)` | coordinates 0 and 7 |

`u^2 = 1`, `r^6 = 1`, `r` has order 6, and `u r u = r^{-1}`. Both preserve
sector 1 and `E`. Each power of `r` acts on the pinned basis of `E` by a
signed permutation. `B` commutes with `r` and with `u` on the ambient
4096-dimensional space.

## The isotypic component

Let `ψ` be the rational character with values `2, 1, -1, -2, -1, 1` on
`r^k` for `k = 0..5` and value 0 on the reflections. These are the traces of
the rational representation whose rotation satisfies `x^2 - x + 1 = 0`. The
central idempotent is

```text
P = (1/6) sum_{k=0}^{5} ψ(r^k) ρ(r^k),
6P = 2 I + ρ(r) - ρ(r^2) - 2 ρ(r^3) - ρ(r^4) + ρ(r^5).
```

On the basis of `E`, `6P` has trace 768, rank 128, and `(6P)^2 = 6(6P)`.
The rational image `W` therefore has dimension 128, and the multiplicity of
`ψ` is `128/2 = 64`. The other two-dimensional rational character,
`2, -1, -1, 2, -1, -1` on `r^k`, has trace 0 on `E`.

`B` commutes with `r`, so `B` preserves the column lattice `L = (6P) Z^216`.
A unimodular Hermite process produces a `Z`-basis of `L`. Its 128 diagonals
lie in `{2, 6}`, so `L` is a finite-index sublattice of the saturated
lattice `{v in Z^216 : (6P)v = 6v}`. Every Hermite basis vector satisfies
`(6P)v = 6v`, and there are 128 of them, so they are a basis of `W` over
`Q`. The matrix `X` of `B` on this basis is an integer matrix: each image
`B v` reduces through the Hermite pivots with exact divisions.

## Polynomial

The monic characteristic polynomial is `chi_B(t) = det(t I - X)`. It lies in
`Z[t]`, every coefficient of `t^k` is divisible by `4^{128-k}`, and

```text
chi_{A_1, W}(x) = 4^{-128} chi_B(4x)
```

is monic in `Z[x]`. Both polynomials are even. Evaluations of `chi_B` at
`0, 1, 2, 3, 5` agree with `det(t I - X)` modulo the first three CRT primes.

Write

```text
f(x) = x^11 + 2x^10 - 108x^9 - 192x^8 + 3208x^7 + 2128x^6 - 33888x^5 + 19264x^4 + 115776x^3 - 196352x^2 + 102144x - 12288
g(x) = x^11 - 2x^10 - 108x^9 + 192x^8 + 3208x^7 - 2128x^6 - 33888x^5 - 19264x^4 + 115776x^3 + 196352x^2 + 102144x + 12288
h(x) = x^14 - 2x^13 - 112x^12 + 136x^11 + 4376x^10 - 3632x^9 - 76384x^8 + 44928x^7 + 621184x^6 - 260736x^5 - 2179840x^4 + 704000x^3 + 3049472x^2 - 702464x - 1167360
k(x) = x^14 + 2x^13 - 112x^12 - 136x^11 + 4376x^10 + 3632x^9 - 76384x^8 - 44928x^7 + 621184x^6 + 260736x^5 - 2179840x^4 - 704000x^3 + 3049472x^2 + 702464x - 1167360
```

Then `g(x) = -f(-x)`, `k(x) = h(-x)`, and each of `f, g, h, k` is irreducible
over `Z` by the Rabin test modulo one prime. The factorization on `W` is

```text
chi_{A_1, W}(x) = q(x)^2,
q(x) = x^6 (x-2)^4 (x+2)^4 f(x) g(x) h(x) k(x).
```

Equivalently, `q(x) = x^6 r(x^2)` where `r` is the monic degree-29 polynomial
with ascending coefficients

```text
-52675902681576269414400
2303306134076870941999104
-18827961748477891024257024
73124429304073607471693824
-171456969792808134744473600
271456076002980399446753280
-309537536542443194852311040
264951255789256454094979072
-175106550821218960407527424
91149737035716567039475712
-37905952006491036612296704
12722870692816032484032512
-3471386398306750712250368
773676955090062483128320
-141267596592764868886528
21162534505722224312320
-2601171087886668267520
262024005207787307008
-21579308813538295808
1447508150155345920
-78661706621779968
3437815337254912
-119644063870976
3271915571200
-69036760064
1095226368
-12571072
98112
-464
1
```

The product of these factors is the expanded polynomial. Ascending-coefficient
SHA256 values, as canonical JSON, are

```text
chi_A    bf10fad08aa427ff461bc3a7a7377f5b90ab7a810a1004d81e550a2a328bbb65
chi_B    33f15f1bcc5d9a57fec18f40653e2362792a77b2c82bdbcf4bbd469694dd03a2
q        d895a734501995193ce1a820dfe8d7cf9121fdf12a1abd1620a344e3315f5762
```

Each factor above occurs in the published degree-216 factorization from
`research/a1-joint-216-charpoly/`, and the multiplicity on `W` does not exceed
the multiplicity on that 216-dimensional space. The factors which occur there
with multiplicity one do not divide `chi_{A_1, W}`. That comparison reads the
published coefficient lists. It does not rebuild the degree-216 matrix
characteristic polynomial.

The square is proved by exhibiting `q` in `Z[x]`. It is the polynomial
predicted by Schur's lemma for this character: the representation is
absolutely irreducible, so an operator commuting with `G` acts as `I_2 ⊗ T`
on a 64-dimensional multiplicity space, and `q` is the characteristic
polynomial of `T`. This package does not construct a basis in which that
tensor form is visible.

## Evidence class

Finite exact linear algebra over `Q`. The verifier rebuilds the query, the
group, the basis of `E`, the operator `6P`, a `Z`-basis of its column
lattice, and the characteristic polynomial, then checks the factorization,
the square, the determinant samples, and the rejection controls. A one-entry
change of `X`, a dropped character coefficient, a dropped splitting
involution, and several nearby permutations fail those controls.
