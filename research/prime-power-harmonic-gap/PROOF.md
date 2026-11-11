# Primitive-unit harmonic cancellation

This scoped written proof was produced by Nick Petalas. The finite verifier
corroborates the new inequalities; it is not a proof-kernel verification.
Independent human and formal proof-kernel review are unclaimed.

## New primitive-unit envelope

Let q = p^a, where p is prime and a >= 1. Set N = floor(q/2),
m = floor(N/p), and H_j = sum_{i=1}^j 1/i, with H_0 = 0.
For every integer p >= 2, p <= 2^(p-1). The integral bounds
H_N <= 1 + log N and H_m >= log(m+1) therefore give

```text
R_q = q/phi(q) sum_{1 <= j <= N, gcd(j,q)=1} 1/j
    = (p H_N - H_m)/(p-1)
   <= log N + p/(p-1) + log(N/(m+1))/(p-1)
   <= log q - log 2 + 2 + log 2
    = log q + 2.                                            (1)
```

The penultimate line uses N <= q/2, N < p(m+1),
p/(p-1) <= 2 and log p/(p-1) <= log 2. This includes m = 0
and q = 2. The subtracted term H_m must be retained.

For 1 <= j <= q/2, the sine chord bound is
sin(pi j/q) >= 2j/q. Pair j and q-j in the unit group. At q = 2,
counting the single midpoint twice only enlarges the upper bound. Thus

```text
1/phi(q) sum_{j unit mod q} 1/sin(pi j/q) <= R_q <= log q + 2. (2)
```

Now let r be a prime power and 0 < h < r. Put q = r/gcd(h,r).
Reduction of units modulo r onto units modulo q has uniform fibers,
and multiplication by h/gcd(h,r) permutes those units. For any interval I
of consecutive integers and zeta = exp(2 pi i/r), the geometric-sum bound
and (2) imply

```text
average_{k unit mod r} 2/|1-zeta^(hk)| <= log q + 2 <= log r + 2,
|sum_{s in I} zeta^(hks)| <= 2/|1-zeta^(hk)|.                (3)
```

The right side is independent of I. This replaces the bound
2(1+log r) used in Chafik Boukhalfa's #1025. The new step is the
primitive harmonic cancellation in (1), rather than a new unit-group
surjectivity theorem or sine inequality. These elementary tools are classical.

## Substitution into the credited height argument

Use #1025's polynomial, normalization and embedding-specific heights:

```text
n = r-1, D = phi(r), ell = ceil(log2 r), t = log r,
a_(k,j) = product_{s=j+1}^{r-1} (1-zeta^(ks)),
f_k(z) = sum_{j=0}^{r-1} a_(k,j) z^j = r P_k(z),
H_k = sum_{j=0}^{r-1} |a_(k,j)|.
```

Here r >= 3 is a prime power, k is a unit modulo r, and log is natural.
The empty suffix has coefficient one. Nick Petalas's older #5930 proves
the following Fourier identity for the auxiliary sampled logarithm F:

```text
F(0) = -log r, F(s) = log|1-zeta^s| for s != 0,
Fhat(0) = 0, sum_{h != 0} |Fhat(h)| = log r.
```

This is a cited premise. Its proof and scientific verifier are not replayed
here. The residue-zero value never enters a suffix product. Fourier inversion
and (3) give a bound valid simultaneously for every suffix, including the
empty suffix:

```text
M_k = max_j log|a_(k,j)|
    <= sum_{h != 0} |Fhat(h)| 2/|1-zeta^(hk)|,
average_k M_k <= t(t+2).
```

Since H_k <= r exp(M_k), the new averaged-height inequality is

```text
sum_{k unit mod r} log H_k <= D [t^2 + 3t].                 (4)
```

The older #5930 inequality is D[2t^2+3t]. This bounds an average
of pointwise upper envelopes of maxima. It does not commute a maximum
with an average and does not claim a bound on one chosen H_k.

## Uniform circle gap and an integer exponent

Ali Romman's #621 supplies prime-power resultant nonvanishing. The
embedding-specific norm/cofactor implication in #1025 gives

```text
|P_k(z)| >= 1/[2rn product_{u unit mod r} H_u^n], |z| = 1.
```

Both are cited inputs, not new resultant or inverse theorems. Substitution
of (4) gives the sufficient analytic gap

```text
|P_k(z)| >= exp(-nD[t^2+3t])/(2rn).                        (5)
```

Put B_ell = ceil(3ell^2/4 + 3ell). With c = log 2 < 3/4 and
t <= ell c,

```text
(t^2+3t)/c <= c ell^2 + 3ell <= B_ell.
```

The inherited coarse height bound gives the alternative exponent nDr,
and 2rn <= 2^(1+2ell). Hence, uniformly in the primitive embedding and
circle point,

```text
|P_k(z)| >= 2^(-d_new),
d_new = 1+2ell+nD min(r, B_ell).                           (6)
```

For ell >= 2, the difference between 3ell^2 and 3ell^2/4+3ell is
3ell(3ell-4)/4 >= 3. Since 3ell^2 is an integer, B_ell <= 3ell^2.
Thus (6) never worsens the cited #5930 exponent.
At r = 4096, B_ell = 144, and the sufficient exponent decreases
from 3,622,993,945 to 1,207,664,665. These are conservative analytic
exponents, not executed precision, actual inverse norms or runtime measurements.

## Finite evidence and limits

The checker evaluates the exact R_q expression for prime powers through
4096, comparing with rational lower enclosures of log q. It independently
enumerates the coprime harmonic sum through 512. Through 128 it encloses
the actual primitive cosecant average using rational Machin/alternating-series
bounds, checks the sine chord and covers every primitive residue by pairing.
The midpoint q = 2 is explicit. These checks exercise the new envelope,
without replaying a predecessor result or computing the predecessor heights.

Large dyadic and ternary exponent cases check only integer budget arithmetic.
The generated stdout receipt enumerates the finite domains and binds all
six package files by SHA256. Controls include deleting the divisible harmonic
terms at q = 64 and replacing a needed exponent ceiling by a floor.

This is a scoped analytic proof, not a complete multiplication theorem.
It stays within prime-power radices. The concurrent #7195 mixed-radix extension
of #1428 uses the existing general-radix envelope; no composite result is claimed
here. Actual reduced-precision inverse execution, coefficient preparation,
rounding, scratch restoration, physical tapes, common-label compilation,
hosting, full cost, supplier admission and all five selected framework
assumptions remain outside this result. No new kappa or selected-frontier
change is claimed. No Lean, Docker, historical or selected scientific replay
was run.
