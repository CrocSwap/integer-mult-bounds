# Reciprocal signed centre responses

This packet gives a complete coefficient classification for the signed
48-port centre family. It gives a reciprocal pair with dyadic entries,
and it preserves the eight-port data interface. The first useful pair is

```text
E = G - K^T Lambda K/4,
E^-1 = G - K^T Lambda K/8.                              (1)
```

The eight centre queries are the same in both responses. Only their
scatter coefficients change. A native word must supply the ordinary
response G and those queries in one compatible schedule. This packet
does not substitute a matrix identity for that implementation obligation.
It also does not identify responses in different routed stage charts.

## The actual response family

Use the pinned K, G, and selected set from
`../bipartite-eight-20261018/BIPARTITE-EIGHT-PROGRAM.json.gz`. The
decompressed SHA256 is
`0c832994c1d06562a8db0b9b3d940f6f6143c37beed983f874a69f2bf6ecfdee`.
There are eight mutually orthogonal six-dimensional component spaces.
Let P_v be the projector onto component v, and k_v its centre row. Then

```text
sum_v P_v = I_48,
k_v k_w^T = 12 delta(v,w),
P_v k_w^T = delta(v,w) k_w^T.
```

The signs are `alpha=(1,-1,1,-1,1,-1,1,-1)`, and
`Lambda=diag(alpha)`. Put

```text
G = sum_v alpha_v P_v,
E_beta = G - sum_v alpha_v beta_v k_v^T k_v,
s_v = 1-12 beta_v.                                     (2)
```

On the five-dimensional part of component v orthogonal to k_v,
E_beta acts by alpha_v. On its centre line, it acts by alpha_v s_v.
Thus

```text
det(E_beta) = product_v s_v,
E_beta^-1 = G + sum_v alpha_v beta_v/s_v k_v^T k_v.      (3)
```

For a dyadic beta_v, s_v cannot be zero: that would require
`beta_v=1/12`. The inverse is again in the same family, with

```text
beta'_v = -beta_v/(1-12 beta_v),
s'_v = 1/s_v.                                          (4)
```

Equations (3) and (4) are ordered local matrix identities. K and G have
their actual routed meanings when a stage is fixed. No commutation
between a Q phase and a graph entry is used.

## All dyadic full-unit parameters

Let `R=Z[1/2]`. Its units are `+/-2^n`, for integer n. Suppose every
beta_v is in R. Then E_beta is a unit over R if and only if every s_v
is a unit over R.

For necessity, the determinant in (3) is a product of elements of R.
If their product is a unit, each factor is a unit. Sufficiency follows
from (3), or from the explicit inverse.

The equation `s=1-12 beta` with beta in R has `s=1 mod3`. A unit
`s=+/-2^n` has this residue if and only if

```text
s = (-2)^n,
beta = (1-(-2)^n)/12,              n in Z.               (5)
```

Conversely, the coefficient in (5) is dyadic for every integer n. For
negative n, multiply the numerator and denominator by the required
power of two before reducing modulo3. Inversion takes n to -n. The
eight exponents can be chosen independently.

This is a full classification within (2). The checker also checks a
finite exponent range as a control, but the classification does not
depend on that range.

## Exactly four choices preserve both principal units

Use `S=[0,7,15,36,42,46,79,89]`, and let U contain the other 40 centre
ports. The actual source has `G_SS=0` and `det(K_S)=-4`. Therefore

```text
L = E_beta[S,S] = -K_S^T diag(alpha_v beta_v) K_S,
det(L) = 16 product_v beta_v.                            (6)
```

Let H be the ordinary principal block E_beta[U,U]. By (3), the selected
block of the full inverse is

```text
(E_beta^-1)[S,S]
    = K_S^T diag(alpha_v beta_v/s_v) K_S.
```

Jacobi's complementary principal-minor identity and (3) now give

```text
det(H) = det(L) = 16 product_v beta_v.                    (7)
```

Thus L and H are both dyadic units if and only if every beta_v is a
dyadic unit. Combine this with (5). For n>0, `1-(-2)^n` is odd and
divisible by3. The coefficient beta is a unit if and only if the absolute
value of this numerator is3. This occurs only at n=1 or n=2. For
`n=-m<0`, the same test is `abs(2^m-(-1)^m)=3`, so m=1 or m=2. At n=0,
beta is zero and L is singular.

The four possible coefficients and their inverses are:

| n | beta | s | reciprocal beta |
| ---: | ---: | ---: | ---: |
| 1 | 1/4 | -2 | 1/8 |
| -1 | 1/8 | -1/2 | 1/4 |
| 2 | -1/4 | 4 | 1/16 |
| -2 | 1/16 | 1/4 | -1/4 |

Each of the eight components can use any of these four choices. There
are exactly `4^8=65,536` full-unit responses with both principal units
in this parameter family. The family is closed under inversion.

For uniform beta, the determinants in (7) are `16 beta^8`. They are
`2^-12` for beta=1/4 or -1/4, `2^-20` for beta=1/8, and `2^-28` for
beta=1/16. These values must not be conflated with each other.

## Existing data fields can carry the inverse gauge

The ordinary factor does not need a separate centre bank. Let `T=G(S)`
and let R contain the other 32 centre ports. In the following word, t
and r are arbitrary data. Put `B=diag(alpha_v beta_v)`.

```text
t <- K_T t
t <- t + K_R r
t <- -B t
r <- G_R r
r <- r + K_R^T t
t <- K_T^T t.                                           (8)
```

Expansion gives H exactly. Every factor is a dyadic unit when every
beta_v is a dyadic unit. Reverse the word and invert each factor to
obtain H^-1. This is the same factor order as the frozen eight-port
ordinary gauge. Its central eight scalings have different coefficients.
No owned centre field is required. A native emitter must still price
the concrete coefficient choices and the other boundary factors.

For `E_beta=[[L,B_s],[D_s,H]]`, the usual diagonal borrowed interface has

```text
A = [[-L+B_s H^-1 D_s, -B_s H^-1],
     [-H^-1 D_s,       H^-1]],
A^-1 = [[-L^-1,       -L^-1 B_s],
        [-D_s L^-1,    H-D_s L^-1 B_s]].
```

Equations (6) and (7) give `det(A)=1`. This preserves the local data-unit
interface for all 65,536 choices. It does not make an old Y query legal
at a later cut.

## Reciprocity is more general than orthogonality

The real symmetric response (2) is orthogonal if and only if every
`s_v` is +1 or -1. With dyadic beta_v, (5) permits only +1 among those
two values. Hence a dyadic orthogonal response in this family must have
every beta_v=0 and equal G. The nontrivial orthogonal choice beta=1/6
is not dyadic. It is not needed for the reciprocal pair (1).

The separate 64-port response in the frozen source has square `4I`.
Its reciprocal is therefore one quarter of itself. Combining that
reciprocal with (3) gives an exact full 112-port inverse. The checker
checks both full inverse orders for all four uniform choices and two
mixed choices. It also checks the selected and ordinary determinants
directly from the 48-port matrices.

## Verification and use

Run from the workspace root:

```text
python3 work/centre-encoding-campaign-20261014/lanes/controller-followthrough-20261017/reciprocal-centres-20261018/check_reciprocal_centres.py
python3 -O work/centre-encoding-campaign-20261014/lanes/controller-followthrough-20261017/reciprocal-centres-20261018/check_reciprocal_centres.py
```

Both commands must print `PASS_RECIPROCAL_SIGNED_CENTRE_FAMILY` and
produce an identical receipt. The checker imports no producer code. It
reads the pinned matrices, verifies K K^T, G K^T, G^2, the selected
minor, both full inverse orders, direct determinants, and all 65,536
component combinations through the proved determinant formulas.

The next native target is the uniform reciprocal pair beta=1/4 and
beta=1/8. A compatible source schedule can reuse all eight centre
queries and change only their scalar scatter coefficients. Full native
replay, recursive cost, routed stage composition, and the terminal
endpoint remain separate checks. No kappa claim is made here.

This is AI-assisted research. It builds on the controller lane's signed
centre geometry, the bridge-review and budget-geometry principal-minor
proofs, and the oblique-native productive pair-code source schedule.
The coordinating agent supplied the complete exponent parameterization
in (5); this packet adds the principal-unit classification and the
independent component family.
