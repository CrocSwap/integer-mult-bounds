# Sharp prefix range for every active tensor repetition

For every positive integer m, the largest absolute real or imaginary
component of an ordered row prefix in the fixed role-1256 graph is

```text
M(m) = (12927/2)*2^(2m) + (36549/8)*2^(4m)
       + (51071533/256)*2^ceil(9m/2).
```

The same location attains it for every m: terminal row 156140, after its
eleventh donor 103886, in chart 127. Address zero of the real output
suffices. No claim of a unique attaining location or input is made.
This answers the active-tensor question in
[PR #7725](https://github.com/CrocSwap/integer-mult-bounds/pull/7725).
Its one-tile result is the case m=1, which is prior work.

## Contract

Use graph hash
`8e7b755bd2d2d387bc3d3adfe48100985adf74775ca5acbb143170a3d16b5ccf`
from [PR #7704](https://github.com/CrocSwap/integer-mult-bounds/pull/7704).
Keep each scalar factor, donor order, chart and paid route. Replace each
complete chart map T by its m-fold tensor power on 9m active binary axes.
Scalar coefficients still occur once. This is not the tensor power of
the complete scalar expression. Independent identity spectators repeat
the same map on each slice and do not change the bound.

Every real and imaginary component of every physical entrance field can
vary independently in [-1,1]. The inputs need not be separable tensors.
The result concerns exact row accumulators after each nonempty scalar
prefix. It does not cover multiplication numerators, paid-child interiors,
caller correlations, rounding or the complete recursive root format.
It changes no paid/productive invoice or kappa. The five framework
interfaces remain conditional.

## Repeated transition gain

At a prefix in chart A, all paths from entrance i telescope to the same
operator. Let B_i be its entrance chart and c_i its signed normalized
coefficient after the prefix. The physical prefix is

```text
sum_i c_i * (T_A T_B_i^(-1))^(tensor m) * x_i.
```

Contributions to one entrance add before an absolute value is taken.
Telescoping uses the exact ordered chart representatives, including
phase. Tensor powers preserve composition and inverse identities.

The source proof gives Fourier rank
`d_i = dim(A)+dim(B_i)-2*dim(A intersect B_i)` and a flat row with
`2^d_i` nonzero Gaussian-dyadic entries, each of squared modulus `2^(-d_i)`.
The exact frame construction and rank theorem are retained. For m
repetitions, a row has `2^(m*d_i)` nonzero entries of squared modulus
`2^(-m*d_i)`. Its Fourier rank is m*d_i.

For completeness, a Gaussian-dyadic number of squared modulus `2^(-r)`
has a constrained phase. Multiply by a sufficient power of two. Its
Gaussian-integer norm is a power of two, so unique factorization in
the Gaussian integers leaves only the prime `1+i` and a unit. For even
r, the entry lies on a real or imaginary axis with magnitude `2^(-r/2)`.
For odd r, both components have magnitude `2^(-(r+1)/2)`. Thus the sum
of the absolute real coefficients of one real output component is

```text
g_m(d) = 2^ceil(m*d/2).
```

The imaginary output has the same gain. This uses the exact
Gaussian-dyadic chart group, not an arbitrary unitary global phase.
In particular, `g_2(9)=512`, whereas `g_1(9)^2=1024`. Raising the one-tile
real-component gain to the repetition count gives the wrong sharp bound.

Independence of the entrance components now gives the exact prefix norm
`sum_i abs(c_i)*g_m(d_i)`. The triangle inequality proves the upper bound.
Choose the sign of each real and imaginary entrance component to match
its coefficient in one chosen output component. All choices can be made
at once, so the upper bound is attained for each prefix.

## A finite certificate for all repetition counts

Group the absolute normalized coefficients of each prefix by distance:
`a_d = sum_(i:d_i=d) abs(c_i)`, for d=0,...,9. The exact forward scan
checks 9044092 coefficient products and all 172414 prefixes in 7644 rows.
There are 86838 distinct rank-mass vectors. Duplicate vectors give the
same bound for every m, so one dominance check per distinct vector is enough.

For even m=2k, put t=2^k. The prefix norm is `E_a(t)=sum_d a_d*t^d`.
For odd m=2k+1, put t=2^k. It is
`O_a(t)=sum_d a_d*2^ceil(d/2)*t^d`. All required t are at least one.
For each parity and each vector a, the checker expands the proposed
maximum minus that polynomial in powers of s=t-1. The coefficient of
`s^j` is the exact sum of its degree-d coefficients times `binom(d,j)`
over d>=j. Every one of the 1736760 resulting coefficients is nonnegative.
Therefore every difference is nonnegative for all real t>=1. This proves
the envelope for every positive integer m; it is not a finite m sweep.

The winning vector has only three nonzero entries:

| Transition rank d | Absolute normalized mass a_d |
| --- | --- |
| 4 | 12927/2 |
| 8 | 36549/8 |
| 9 | 51071533/256 |

Substitution gives M(m). The checker hashes the complete ordered prefix
trace and both exact dominance tables. It regenerates every inequality
from the pinned graph; no floating-point comparison or numerical root
finding is used. A separate backward rational expansion of the eleven
winning donors agrees on all 448 nonzero entrance coefficients.

## Attaining physical fields

Let z_i(alpha) be the exact address-alpha entry of
`T_B_i T_A^(-1) e_0`, the adjoint output row at one tile. For address tuple
`(alpha_1,...,alpha_m)`, put `z=product_j z_i(alpha_j)`. Choose

```text
Re x_i = sign(c_i * Re z),
Im x_i = sign(c_i * Im z).
```

Use sign(0)=0. These components lie in [-1,1]. The corresponding real
output contribution is `abs(c_i)*(abs(Re z)+abs(Im z))`. Summing over
addresses and entrances gives M(m). The formula specifies an attaining
field for every m without requiring a separable field or a free runtime
input-construction service.

The exact native interpreter checks the actual adjoint column for each
entrance chart in the winning form. It checks support, magnitude and
phase parity. For m=1,2,3,4, Gaussian coefficient histograms are multiplied
exactly. They count tensor entries without materializing the exponential
address array. All gains and attained totals agree with the formula:

| m | M(m) |
| --- | --- |
| 1 | 51863149/8 |
| 2 | 103416050 |
| 3 | 3287704864 |
| 4 | 52598313856 |

These are finite corroboration of the physical input rule. The all-m
claim follows from the gain proof and polynomial dominance certificate.
Controls reject a bound below the actual winning coefficient in both
parities, the multiplicative one-tile gain and an odd-rank floor in place
of the required ceiling.

## Limits and credit

The source graph reader, backward coefficient expansion and native
interpreter are retained dependencies. The new forward rank-mass and
polynomial checks adapt the credited prefix method. This is source-aware
author checking, not blind or independent human or formal-kernel acceptance.
No claim is made that a correlated signed caller can realize the local
extremum. No physical stock, reset, compiler, tape or root budget is changed.
Full predecessor suites, selected cold replay, Lean and Docker were not run.
[CREDITS.md](CREDITS.md) gives the exact source attribution and pins.
