# A smaller finite-cap inverse bound

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract and credited premise

Let N be a positive integer, gamma>0, q=exp(-gamma), and |s|<=1/2.
Use the normalized real Gaussian section

    T_N(s)[i,j] = q^((j-i)^2-2s(j-i)),  0<=i,j<N,
    P_(N-1) = product_(r=1)^(N-1) (1-q^(2r)).

The empty product is one. Jose Manuel / PR4193, Section 3a of
`research/shifted-gaussian-conditioning/PROOF.md`, proves invertibility and

    |T_N(s)^(-1)[i,j]| <= q^(|i-j|+2s(i-j)) / P_(N-1)^3.       (1)

It then bounds the spectral norm by N/P_(N-1)^3. That entry theorem and
its finite q-LDU derivation are cited premises. This contribution neither
audits them nor claims their factorization as new. The norm below is the
Euclidean induced norm. The Frobenius norm is the square root of the sum
of squared entries.

## The new bound

Put x=q^4 and define

    D_N(x) = N(N+1)/2 + sum_(d=1)^(N-1) (N-d)x^d
           = N(N+1)/2 + ((N-1)x-Nx^2+x^(N+1))/(1-x)^2.        (2)

For every N>=1, gamma>0 and |s|<=1/2,

    ||T_N(s)^(-1)||_2 <= sqrt(D_N(q^4)) / P_(N-1)^3.           (3)

For every N>=2 this is strictly smaller than N/P_(N-1)^3.
There is equality between the two displayed bounds at N=1. We do not
claim equality between the inverse norm and the new bound.

To prove (3), square (1) and sum all N^2 entries. The diagonal contributes
N. For distance d>=1, each orientation occurs N-d times. Therefore

    P_(N-1)^6 ||T_N(s)^(-1)||_F^2
      <= N + sum_(d=1)^(N-1) (N-d)
               [q^(2d+4sd)+q^(2d-4sd)].                    (4)

The function t -> q^(2d+2dt)+q^(2d-2dt) is even and convex on [-1,1].
Indeed its second derivative is (2d log q)^2 times itself, which is
positive. Convexity bounds it by its equal endpoint values. Taking t=2s
thus bounds the bracket in (4) by 1+q^(4d). Summing gives D_N(q^4).
The elementary inequality ||A||_2<=||A||_F proves (3). This argument also
covers either half-shift endpoint without a positive infinite-symbol gap.
For N>=2 the bracket is strictly smaller at every interior shift.

For the closed form in (2), multiplying
A=sum_(d=1)^(N-1)(N-d)x^d by 1-x gives

    (1-x)A = (N-1)x - sum_(d=2)^N x^d.

Multiplying again by 1-x gives (N-1)x-Nx^2+x^(N+1).
This identity includes N=1.

Since 0<x<1, for N>=2,

    D_N(x) < N(N+1)/2 + sum_(d=1)^(N-1)(N-d) = N^2.          (5)

At least the distance-one term is strictly smaller, so this proves the
strict improvement for every nontrivial size, rather than only samples.

## Size dependence and an exact example

For fixed q in (0,1),

    N(N+1)/2 <= D_N(q^4)
             < N(N+1)/2 + N q^4/(1-q^4).

After division by N^2 both ends tend to 1/2. Consequently the ratio of
the new upper bound to the credited old upper bound tends to 1/sqrt(2).
This is a limit of two upper bounds, not an asymptotic formula for the
actual inverse norm. The statement keeps q fixed. It does not justify a
uniform growing-gamma or vanishing-gamma caller substitution.

For N=2 and q=1/2, x=1/16, P_1=3/4 and D_2=49/16. Thus the old bound is
128/27 and the new bound is 112/27, exactly one eighth smaller. These are
analytic upper bounds, not measured inverse norms or runtime numbers.

## Scope and remaining obligations

The universal quantifiers follow from this written proof and premise (1).
The finite exact checks corroborate the new norm inequality by independent
rational inversion. They do not certify a complete multiplication theorem
or provide independent human or proof-kernel acceptance.

The result sharpens the same finite-cap constant-shift contract. It does
not establish an optimal constant, a better asymptotic exponent, a physical
inverse algorithm, intermediate rounding stability, coefficient generation,
diagonal-gauge bounds, native implementation, restoration, physical stock,
tape costs or supplier admission. The source caller must keep those costs.
JoyboyBrian / PR5103 and PR5183 address a different varying-phase full-cell
kernel and its boundary-layer limit. No claim about that limit is changed.

Frobenius domination, convexity and finite geometric sums are classical.
Credit Jose Manuel / jmbarrancoml PR4193 for the entry estimate and explicit
finite-cap sharpness question; Vlado Vojdanovski / PR1673 for the retained
q-LDU framework; Jeremy Kothe and PR1758 contributors for the shifted-kernel
lineage; and Cinna Davis for the later broad Gaussian caller. Their frozen
sources and credit remain unchanged. The new result is the explicit
all-size improvement (2)-(5), including its exact bound-ratio consequence.
