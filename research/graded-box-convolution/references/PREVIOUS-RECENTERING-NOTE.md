# Recentered weighted Gaussian tensor tiles

This is a bounded research result, not a new multiplication bound. The finite
implementation executes a joint packed convolution and verifies its local
precision behavior. A global fast transform, efficient table setup, routing,
phase-cell boundary composition, and an outer exponent saving remain unproved.

The source model is PR #489, commit
`8922e3b3f0fd7772b0fb42028eb2532984c3ab42`, specifically
`research/branchfree-gaussian-inverse/PROOF.md`. Its weighted factors, retained
dyadic q and weights, source approximation bounds, and old global H are kept.
No new inverse identity is asserted for the independently rounded old H.

## Exact local identity

On one phase cell, write theta=rho-1, beta_i=beta_c+theta(i-c),
lambda=pi*u*theta, and

    a_i = exp[-pi*u*(1/4-beta_i^2)/theta],
    a_hat_i = e_i*a_i,  1/2 <= e_i <= 1,
    f_k = product_{j=1}^k (1-q^(2j)),
    h_k = (-q)^k/f_k.

Here q is precisely the old downward approximation to exp(-pi*u*rho), and
14/15 <= f_k <= 1. Choose an integer centre c in the same phase cell. Set

    E_i = e_i*exp[lambda*(i-c)^2],
    q_lower = q*exp[+2*pi*u*beta_c],
    q_upper = q*exp[-2*pi*u*beta_c].

Expanding the square gives

    a_i = a_c*exp[2*pi*u*beta_c*(i-c)]*exp[lambda*(i-c)^2].

Consequently, the old weighted lower or upper triangular matrix, restricted
to any input/output coordinates in this cell, is exactly

    D_E T(h_effective) D_E^-1,
    h_effective(k) = (-q_orientation)^k/f_k,

with the same triangular orientation. The f_k denominators are NOT rebuilt
from q_orientation. The scalar a_c cancels; e_i remains in E_i. Because
beta_c lies in [-1/2,1/2), both effective q values lie in
(0, exp(-pi*u*theta)]. Tensoring this identity introduces no branch sum.

## Local magnitude and rounding bounds

For a tensor tile of D axes, let R_l bound the absolute distance to its
chosen centre on axis l. Assume

    D <= p, N <= 2^p, sum_l lambda_l*R_l^2 <= p,

where N bounds the number of input coordinates and kernel terms per output.
Then the tensor weights E and tensor kernel K satisfy

    2^-p <= E <= exp(p) <= 2^(2p),
    E^-1 <= 2^p,
    |K| <= (15/14)^D <= 2^p.

These bounds concern normalized E, never the product of the original a^-1.
For input norm at most B>=1, every exact diagonal/convolution intermediate
has magnitude at most 2^(5p)*B.

A simple conditional numerical lemma is enough here: suppose each E, 1/E
and K table entry has absolute approximation error at most eta=2^-P. Use
one completed-coordinate rounding of error <=eta after each of the three
stages. The predivision error is <=2*eta*B. The convolution error is at
most 2^(3p+4)*eta*B (sum N coefficient and input errors, including the
cross term); its exact output magnitude is at most 2^(3p)*B. Final
multiplication then has error at most 2^(5p+6)*eta*B. Thus the source
P=32768p has ample margin on such a tile. This is conditional on the
table error bound. The current code builds exact rational analogue tables;
it does not implement a certified transcendental table generator for all
source axes. In particular this note is not a complete setup-cost proof.

The finite evaluator uses exact E for completed predivision and final
multiplication, with their results rounded to P bits. It rounds the tensor
kernel once, uses four nonnegative integer products for signs, and rounds
the completed convolution output. Its sharper measured-case bound is

    Emax * [N*(H*eta + eta/Emin + eta^2) + eta] + eta,
    H=(15/14)^D, |input|<=1.

The checker compares this bound with both the exact observed error and the
12-bit target. Packed slot width strictly exceeds the maximum possible
coefficient magnitude, so no unaccounted integer carry is permitted.

## The previous legal counterfamily fits a tile

For the source family a>=26,

    p=2^(10a), d=u=2^(4a), D=d-1,
    X=2^(3a), w=4X+2, k=X/2048,

use centre c=w on every axis and the tile [w,w+k]^D. Both endpoints remain
inside the old cell interior. Source axes have u*theta<2. Since
pi/log(2)<8, the maximum residual magnitude exponent satisfies

    log2(Emax) < 16*D*k^2 < p/262144.

Also D<p/128. The source proof's weighted upper entry is >2^(-p/8).
For this selected displacement, E_source/E_destination>=2^-D; hence its
recentered kernel magnitude exceeds 2^(-p/8-D)>2^(-p/4). Unlike the
original unweighted tensor coefficient, it cannot round to zero at
P=32768p. This is a uniform argument for the same source family, not an
extrapolation from finite tests. Its table still contains exponentially
many entries; no enormous tensor has been constructed by the checker.

The elementary universal comparisons reduce to powers of two:
16*D*k^2/p < 16/2048^2=1/262144, D/p<2^(-6a), and
(3a-9)*D<p, the last bounding the padded coefficient count by 2^p.
The last inequality holds at a=26 and its right-hand ratio grows with a.
`check_family.py` verifies exact rational rows a=26,27,32,64.

## The current layout still has a prohibitive overhead

The executable packs axis l in radix 2*n_l-1, so integer operands have
O(P*product_l(2*n_l-1)) bits. For the counterfamily tile n_l=k+1,
the ratio of padded slots to actual entries is

    [(2k+1)/(k+1)]^D >= (3/2)^D > 2^(D/2).

Since D=2^(4a)-1 and log2(p)=10a, this exceeds every fixed power of p
eventually. Merely repeating this packing on all local tiles cannot be
charged as a polynomial-in-p overhead per tensor entry. This is an
obstruction for this implementation, not for different circular layouts,
implicit kernels, recurrence schemes, adaptive representations, or all
weighted transforms. No global time bound or improved kappa follows.

## Executed finite evidence

Run from this directory:

    python3 -B recenter_fixture.py
    python3 -B check_family.py

The rational analogue uses a_j=2^(-20j+j^2), q=2^-21, and nonconstant
dyadic e_j in [1/2,1]. It is not claimed to satisfy every asymptotic
source hypothesis. Shapes (3,3,3,3) and (3,2,4), both orientations, verify
14,274 exact matrix entries against the unrecentered definition. Every
basis column plus two signed dense vectors is checked at 32 and 64 bits.
The eight cases use 1,744 actual integer products; each convolution uses
four products. Worst error is below 7.265e-9, below the explicit per-case
rounding bounds and the target 2^-12. This is numerical error, not runtime.

The unweighted 64-bit grid erases a coefficient whose weighted entry is
about 0.0016 (>2^-12). Recentered evaluation passes. Four controls fail:
omitted slope, omitted residual weights, omitted multidimensional padding,
and omitted signed cross terms. All comparisons and pass/fail decisions
use exact rational arithmetic; decimal JSON fields are display values.
