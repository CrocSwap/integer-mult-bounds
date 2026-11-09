# Signed-permutation splitting of the doubled centre block

This is a finite exact certificate for three Bell sectors of the historical
one-slot doubled centre operator. It is not an annihilating polynomial, not a
minimal-polynomial degree, and not a multiplication bound.

## Operator

The live input is the actual 8-by-112 query retained by
`research/centre-polynomial-cache-limits/`. Its columns lie in `{-1,0,1}^8`,
each has weight 4, and `R R^T = 56 I_8`. The 112 port labels are distinct
odd-parity vectors in `F_2^9` and span that space.

For a Bell label `c` in `F_2^9`, the one-slot block is the operator

    A_c = (1/4) sum_q r_q r_q^T ⊗ P_q(c)

on `C^8 ⊗ C[F_2^9]`, of dimension 4096. Here `P_q(c)` sends `e_a` to `e_{a+q}`
when `q·c = 1`, and to `(-1)^{q·a} e_a` otherwise. The factor `1/4` is not
needed for the symmetry argument below.

Krzysztof Wojt's package `research/exact-one-slot-gram/` already gives the
scalar minimal polynomial of the full one-slot operator, of degree 881, by a
different reduction: payload involutions `X_c` and `Z_{c+e}` split each
nonzero representative into four 1024-dimensional sectors. This note does not
replay that certificate. The symmetries used here are signed permutations of
the eight query coordinates, not those payload involutions.

## Two explicit involutions

A signed coordinate permutation acts by

    (S v)_k = eps[k] v[sigma^{-1}(k)],

and by the orthogonal linear label map `T` that carries each port to the port
of its image column. The two operators certified here are involutions:

| name | `sigma = sigma^{-1}` | output signs `-1` |
|---|---|---|
| `g` | `(1 2)(5 6)` | coordinates 4 and 7 |
| `t` | `(1 5)(2 6)` | coordinates 3 and 7 |

Coordinates are numbered `0..7`. Both squares are the identity operator,
including the identity label map, and `g` commutes with `t`. The induced label
maps satisfy

    T_g(1) = T_t(1) = 1,
    T_g(128) = T_t(128) = 128,
    T_t(3) = 3,
    T_g(3) = 343.

So `g` and `t` both preserve sectors `c=1` and `c=128`. Sector `c=3` is
preserved by `t` and is sent to `343` by `g`. The same conjugation identity
used by the predecessor notes then gives

    (S ⊗ U_T) A_c (S ⊗ U_T)^{-1} = A_{T c}.

Whenever `T c = c`, the signed permutation commutes with `A_c`.

## Sign stabilizer and its characters

For a fixed sector, `H(c)` is the group of coordinate sign patterns with
positive sign on coordinate 0 whose induced label map fixes `c`. It is an
elementary abelian 2-group. The trace of a signed permutation on the
4096-dimensional block is

    tr(S) · 2^{nullity(T - I)},

where `tr(S)` sums `eps[k]` over coordinates fixed by `sigma`. The dimension
of the `chi`-isotypic component is

    |H|^{-1} sum_{h in H} chi(h) tr(h).

The verifier recomputes these dimensions from the query. They are nonnegative
integers summing to 4096, with histograms

| sector | `|H|` | dimension histogram |
|---|---:|---|
| `c=1` | 16 | `{864: 1, 432: 4, 192: 6, 80: 4, 32: 1}` |
| `c=3` | 16 | the same histogram |
| `c=128` | 8 | `{512: 8}` |

The unique largest `c=1` character is the trivial character, of dimension
864. The four characters of dimension 432 are different character spaces.
JoyboyBrian's handoff on Discussion #1166, comment 19144258, found two
connected 432-coordinate components inside a quotient of the largest space.
That connectivity was reported there as basis-dependent and is not
reconstructed or certified here. The dimension-864 space is the largest
sign-character space that handoff asked to decompose.

## Joint eigenspaces

Because `g` and `t` are commuting involutions, the whole block they preserve
splits into joint `(±1, ±1)` eigenspaces. A character space is invariant
under both involutions precisely when both conjugations preserve that
character. On each such space the joint dimensions are

    (tr I + e_g tr g + e_t tr t + e_g e_t tr(gt)) / 4.

For `c=1`, exactly two characters are preserved by both involutions: the
trivial character and the unique character of dimension 32. Their joint
dimensions are

| character | joint dimensions |
|---|---|
| trivial, dimension 864 | `216, 216, 216, 216` |
| unique dimension-32 character | `8, 8, 8, 8` |

Each of these eight spaces is invariant under `A_1`, because each involution
commutes with `A_1` and the joint spectral projection is a polynomial in the
two involutions.

For `c=128`, exactly four of the eight characters are preserved by both
involutions, including the trivial character. Each of those four
512-dimensional spaces splits as `224 + 96 + 96 + 96`. The trivial
character's `(+1, +1)` summand has dimension 224. Those four decompositions
are invariant under `A_128`.

The other characters of these two sectors are moved by at least one of the
involutions, so this pair does not split them. Sector `c=3` is not preserved
by `g`, so this pair does not split its character spaces either. The `c=3`
histogram above is only a dimension certificate.

## What this does not say

A 216-dimensional invariant subspace has restricted minimal-polynomial degree
at most 216. The minimal polynomial of the full one-slot operator is the lcm
of the polynomials on a complete set of invariant pieces, so this split does
not upper-bound that degree by 216 and does not replace the degree-881
certificate. No characteristic polynomial of a 216-dimensional block is
computed. No basis of those blocks is listed; the certificate gives the
dimensions through the trace formula and the explicit intertwining operators.

The selected conditional kappa stays `781451/250000000`. This package does
not touch the selected supplier.
