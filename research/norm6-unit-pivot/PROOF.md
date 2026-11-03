# An integral unit-edge pivot for norm-six features

Produced by Nick Petalas. Apache-2.0. Claim type: scoped algebraic proof.
The kernel and feature identity are credited to Cinna Davis / PR2222, with
the relation-column convention of Krzysztof Wojt / PR5143. Their results are
cited premises. The new step is the integral pivot and resulting denominator.

## Credited interface

Put d=48, q(x)=x^T G x, h_i=G_ii/2 and v=Gy. Before compression, use

| Key | Integral source phi_j(x) | Integral target psi_j(v) |
| --- | --- | --- |
| f_i | (x_i^3-x_i)/3 | v_i^3 |
| l_i | x_i | (v_i^3-4v_i)/3 |
| s_(i,j), i!=j | x_i^2 x_j | v_i^2 v_j |
| t_(i,j,k), i<j<k | x_i x_j x_k | 2v_i v_j v_k |

Integrality follows since u^3-u is divisible by three and
u^3-4u=(u^3-u)-3u. The credited multinomial identity is

```text
sum_j phi_j(x) psi_j(v) = ((x dot v)^3-4*x dot v)/3.
```

There are N0=2d+d(d-1)+binom(d,3)=19,648 features. The relation
r_i(x)=x_i(q(x)-6)/2 has feature coefficients R[i,j] given by

```text
R[i,f_i]       = 3h_i
R[i,l_i]       = h_i-3
R[i,s_(i,j)]   = G_ij
R[j,s_(i,j)]   = h_i
R[i,t_(i,j,k)] = G_jk, with the other two entries by permutation.
```

All unlisted entries vanish. Thus R phi=(q(x)-6)x/2 as a polynomial
identity, and R phi=0 on q(x)=6.

## New pivot

For the pinned Gram, H={i:G_ii=8} is

```text
2,3,8,10,11,12,13,15,16,19,21,22,24,25,27,29,30,33,34,35,36,38,39,40,42,47.
```

Every i outside H has a root parent p(i) with epsilon_i=G_i,p(i) in {-1,+1}.
Choosing the least possible root gives this complete certificate:

```text
i:       0  1  4  5  6  7  9 14 17 18 20 23 26 28 31 32 37 41 43 44 45 46
parent: 12  3  3  2 10  3  3  2  3  2  8 15  2  2  3  2  2  2  3  2  8 10
G_ip:   -1  1 -1  1  1  1  1 -1 -1  1  1  1 -1  1 -1  1  1  1  1 -1  1  1
```

The pivot set P consists of l_r for r in H and s_(i,p(i)) for i outside H.
Order root rows and root columns first, then other rows and their matching
columns. The pivot matrix is

```text
R_P = [ I  B ],
      [ 0  E ]
E_ii = epsilon_i,
B[p(i),i] = h_i, with other entries zero.
```

A root linear column has the single coefficient h_r-3=1. A chosen
square-linear column has coefficients epsilon_i in its own row and h_i
in its parent row. Therefore the determinant in this common ordering is
product epsilon_i, of absolute value one. R_P has an integral inverse.

The checker validates all 26 roots and 22 unit edges against the pinned
Gram, computes the determinant independently by rational elimination, and
checks every entry of the integral inverse through coordinate right-hand
sides. These are checks of the new pivot, not a replay of predecessor suites.

## Integral solve and exact substitution

The system R_P^T lambda(v)=psi_P(v) has the explicit integral solution

```text
lambda_r = (v_r^3-4v_r)/3                              for r in H,
lambda_i = epsilon_i*(v_i^2*v_p(i) - h_i*lambda_p(i))   for i outside H.
```

Define eta_j(v)=psi_j(v)-sum_i R[i,j]lambda_i(v). Every eta_j is integral
on integral v. The pivot equations make eta_j=0 identically for j in P.
Subtracting lambda^T R phi from the credited feature identity gives

```text
sum_(j not in P) phi_j(x)*eta_j(v)/64
 = ((x dot v)^3-4*x dot v)/192
     - (lambda(v) dot x)*(q(x)-6)/128.
```

This holds even off the shell. If q(x)=6, its defect term vanishes. Setting
v=Gy proves the claimed kernel identity for every integral norm-six source
and every integral target. The all-input statement rests on polynomial
substitution, rather than finite extrapolation.

Exactly N0-d=19,600 pairs remain. Source features are integral and targets
have integral numerators over 64. PR5143 and PR5132 supply denominator 256
for their different chosen feature sets. This improves the sufficient common
denominator by a factor of four while retaining their term bound. It does
not prove minimal denominator or that every numerator is odd.

## Limits

The new coordinate selection must be used on both sides of a factorization.
Old coefficient arrays cannot be substituted into the new source features.
The original stream's storage and operation bounds do not transfer merely
from the denominator calculation. Fewer coefficient fractional bits do not
by themselves imply fewer physical working bits or a favorable paid invoice.

The geometric interpretation and binary chart remain cited premises. There
is no full-shell rank calculation, full-shell enumeration, completed physical
caller, native realization, restored arbitrary workspace, new kappa or selected
frontier change. All five framework assumptions remain. Discovery stops at
this first improvement; the next useful obligation is a fully charged caller.
