# A zero-mean mixed-radix height bound

This scoped written proof was produced by Nick Petalas. The new step combines
the all-radix Fourier identity of Nick Petalas's #5930 with the mixed-radix
unit-average estimate of Hanson Sun / bbMisk's #1428. Those results are cited
premises. Their proofs, programs and finite censuses are not rechecked here.
The averaged-height framework is Chafik Boukhalfa's #1025; the resultant and
cofactor implication is Ali Romman's #621, as specialized in #1428.

## Statement and hypotheses

Let r >= 3 be any integer, n = r-1, D = phi(r), ell = ceil(log2 r),
zeta = exp(2 pi i/r), and t = log r, where log is natural. For each unit k
modulo r define

    a_(k,j) = product_(s=j+1)^(r-1) (1-zeta^(ks)),  0 <= j <= n,
    f_k(z) = sum_(j=0)^n a_(k,j) z^j,
    P_k(z) = f_k(z)/r,
    H_k = sum_(j=0)^n |a_(k,j)|.

The empty product is one. The new unconditional averaged-height estimate is

    sum_(k unit mod r) log H_k <= r t(1+t) + D t.             (1)

For the circle-gap consequence, additionally assume that the resultant of
f_1 and f_1*(z) = z^n conjugate(f_1(1/conjugate(z))) is nonzero. Put

    B_new = n [3r ell^2/4 + (r+D)ell],
    d_new = 1 + 2ell + min(nDr, ceil(B_new)).                 (2)

Then for every primitive embedding k and every |z| = 1,

    |P_k(z)| >= 2^(-d_new).                                 (3)

The inherited cyclic-operator transfer of #1428 also gives, for every L >= 1,
integer w and |tau| = 1, with U = tau Z_L^w,

    ||P_k(U)^(-1)||_infinity <= 2^(2d_new+r+2).               (4)

Here Z_L is the cyclic shift on L coordinates. The nonzero-resultant
hypothesis is essential to the derivation of (3)-(4), and is not asserted
for every integer r. Jason Willems's #666, specialized and credited in
#1428, supplies it for r = 2p^a with p >= 5 prime and a >= 1. We cite that
family without replaying its lifting argument.

## Proof of the new averaged height

Use #5930's function F on Z/r:

    F(0) = -t,  F(s) = log|1-zeta^s| for s != 0,
    Fhat(h) = (1/r) sum_s F(s) zeta^(-hs).

Its all-integer-r identity says

    Fhat(0) = 0,  Fhat(h) < 0 for h != 0,
    sum_(h != 0) |Fhat(h)| = t.                            (5)

The Fourier identity in that source is stated for every integer r >= 3;
only its subsequent height application was restricted to prime powers.
No singular zero-residue value occurs in any a_(k,j), because k is a unit
and 1 <= s < r. Fourier inversion and the geometric-sum inequality imply

    log|a_(k,j)|
        <= sum_(h != 0) |Fhat(h)| 2/|1-zeta^(hk)|.

The same nonnegative bound includes the empty suffix. Therefore it bounds
M_k = max_j log|a_(k,j)|. The zero Fourier mean removes the old additive t
term at this step.

For each fixed h != 0, the mixed-radix estimate of #1428 gives

    (1/D) sum_(k unit mod r) 2/|1-zeta^(hk)|
        <= (r/D)(1+t).                                    (6)

That source proves (6) by equal fibers from units modulo r to units modulo
q = r/gcd(h,r), pairing reciprocal sines and using q/phi(q) <= r/D. It
does not require a prime-power radix. Apply (6) separately to each
nonnegative term in the bound on M_k, then (5), to obtain

    sum_k M_k <= r t(1+t).

There are r coefficients, so H_k <= r exp(M_k). Summing log H_k proves (1).
The maximum is bounded before averaging; no maximum is interchanged with
an average. This is the new mixed-radix estimate.

## Conditional gap and integer exponent

Under the nonzero-resultant hypothesis, #1428's retained norm/cofactor
argument gives

    |P_k(z)| >= 1 / [2rn product_(a unit mod r) H_a^n].      (7)

It applies at every primitive embedding. Substituting (1) into (7) gives
the stronger, non-dyadic statement

    |P_k(z)| >= exp(-n [r t(1+t)+D t])/(2rn).              (8)

Write c = log 2. Since t <= ell c and c < 3/4,

    [r t(1+t)+D t]/c
        <= r c ell^2 + (r+D)ell
        < 3r ell^2/4 + (r+D)ell.

The coarse alternative H_k <= 2^r-1 < 2^r gives nDr. Also
2rn <= 2^(1+2ell). Taking the smaller sufficient exponent and rounding
up proves (2)-(3). Equation (4) is precisely the cited gap-to-operator
implication with this improved d; it introduces no new operator claim.

## Comparison with the old mixed-radix exponent

The old analytic branch in #1428 is

    B_old = 3nr(ell+1)^2/2 + 2nD ell,
    d_old = 1+2ell+min(nDr, B_old).

B_old is an integer because nr is even. Direct subtraction gives

    B_old - B_new
        = n [3r ell^2/4 + 2r ell + 3r/2 + D ell] > 1.

Consequently ceil(B_new) < B_old and d_new <= d_old for every r >= 3.
The full exponent can remain equal when both bounds use the coarse branch.
For the certified mixed radix r = 8978 = 2*67^2, the exact new exponent is
13,531,624,611, compared with the cited formula's 28,312,479,536. The
standalone checker computes these integers; they are sufficient analytic
exponents, not measured or executed precision.

## Verification and limitations

The written proof supplies all-radix quantifiers, conditional on the cited
identities and implication. The new verifier independently encloses actual
coefficient-height sums at thirteen mixed radices using rational intervals,
Machin's identity, Taylor remainders, integer square roots and an atanh
logarithm series. It checks the new natural-to-binary inequality and exponent
arithmetic, including a half-integer ceiling boundary. It imports and runs
no predecessor code and makes no floating-point inference.

These finite checks corroborate the new estimate. They are not a proof kernel
and do not establish nonvanishing at other radices. No paid composite solver,
coefficient-preparation or rounding schedule, restored dirty workspace, native
word, physical tape/caller invoice, compiler closure, supplier admission,
new kappa or complete multiplication theorem is supplied. All five selected
framework assumptions remain. Independent human and formal proof-kernel
review are unclaimed.
