# Prime supply with subexponential dimension

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement and inherited reduction

Let ell and d be integers satisfying

```text
ell >= 2^18,       2 <= d <= 2^floor(sqrt(ell)/4),       D=d-1.
```

For either t=2^ell or t=2^(ell-1), the half-open interval

```text
I(t,d) = (t*(1-1/(3d)), t*(1-1/(4d))]
```

contains at least D primes. Thus the same two-scale caller can select D
distinct odd prime lengths in original axis order. Retain the separate
premise target_halo+2w <= 2^(ell-3) to obtain its period guard. The band
also retains the source-ratio guards and T/S<3/2 from ToikY's
[PR4029](https://github.com/CrocSwap/integer-mult-bounds/pull/4029).

The new result is the displayed parameter domain. Source guards, ordering,
product accounting and the prime-selection algorithm retain their
predecessors' credit. No producer implementation or multiplication theorem
is proved here.

All logarithms below are natural. Put y=log(t). We use the following
interval estimate from PR4029's PROOF.md, section "Imported analytic input
and effective cutoff", as a cited premise:

```text
pi(b)-pi(a) >= t/(12*d*y) - 20*t*sqrt(y)*exp(-sqrt(y)/2).       (1)
```

Its derivation requires only d>=2 and t>=4, before imposing the old
polynomial dimension restriction. Its analytic input is Fiori, Kadiri and
Swidinsky, [Corollary 22, arXiv:2206.12557v2](https://arxiv.org/pdf/2206.12557v2):

```text
|pi(x)-Li(x)| <= 9.2211*x*sqrt(log(x))*exp(-.8476*sqrt(log(x))), x>=2.
```

Neither predecessor theorem is reverified by the finite checker. To make
the right side of (1) strictly larger than D, it suffices to prove

```text
480*d*y^(3/2)*exp(-sqrt(y)/2) < 1,                             (2)
t > 24*d*D*y.                                                (3)
```

Indeed, (2) makes the error strictly smaller than t/(24*d*y), leaving
strictly more than t/(24*d*y), which exceeds D by (3).

## A dimension bound independent of a polynomial degree

The elementary estimates 1/2<log(2)<7/10 give

```text
ell/4 <= y <= ell,       log(d) <= (sqrt(ell)/4)*log(2)
                                     < 7*sqrt(ell)/40.
```

For the first lower bound, ell>=2 implies
(ell-1)*log(2) > (ell-1)/2 >= ell/4. Set z=sqrt(ell), so z>=512.
The left side of (2) is at most

```text
480*z^3*exp(-3*z/40).
```

Let f(z)=log(480)+3*log(z)-3*z/40. At z=512,

```text
f(512) < 7 + 3*9*(7/10) - 3*512/40 = -25/2 < 0.
f'(z) = 3/z - 3/40 <= f'(512) = -177/2560 < 0.
```

Here log(480)<7. These inequalities establish (2) on the entire domain,
without an enumeration over ell or d.

For (3), D<d and y<=z^2 give

```text
log(24*d*D*y) < 5 + 7*z/20 + 2*log(z),
log(t) >= z^2/4.
```

Use log(24)<5 and define g(z)=z^2/4-5-7*z/20-2*log(z). At z=512,

```text
g(512) > 512^2/4 - 5 - 7*512/20 - 2*9*(7/10)
       = 326696/5 > 0.
g'(512) = 512/2 - 7/20 - 2/512 = 327227/1280 > 0.
g''(z) = 1/2 + 2/z^2 > 0.
```

Therefore g stays positive for all z>=512, proving (3) and the theorem.

The logarithm estimates use classical elementary inequalities. Integrating
1/t>1/2 on [1,2] proves log(2)>1/2. Positive exponential partial sums
of degrees three, six and three at 7/10, 7 and 5 exceed 2, 480 and 24,
respectively. The verifier checks these strict rational comparisons.

## Strict enlargement of the original dimension region

For every ell>=2^32, the new cap contains d<=ell^334 from PR4029.
It suffices to prove

```text
334*log(ell) < (sqrt(ell)/4-1)*log(2),                        (4)
```

because floor(u)>u-1. With z=sqrt(ell)>=65536, the right side minus
the left side of (4) is strictly greater than

```text
h(z) = z/8 - 7/10 - 668*log(z).
```

At z=65536, h(z)>8192-7/10-668*16*(7/10)=7097/10>0.
Its derivative 1/8-668/z is positive there and increases afterward.
This proves (4) for all ell>=2^32.

The enlargement is strict. At ell=2^32, d=2^12000 exceeds
ell^334=2^10688 and is below the new cap 2^16384. Only exponent
comparisons are needed to certify this witness. The old improved
polynomial cutoff in PR5149 is a different domain comparison; no least
cutoff or optimal dimension constant is claimed.

## Evidence boundary

The standalone verifier computes the displayed rational endpoints and
derivative signs. It also checks the first error endpoint by the separate
integer inequality

```text
8^38 > 480*512^3*3^38,
```

using e>8/3 and 3*512/40>38. A separate quota calculation compares
the exact exponents ell-1=262143 and 5+256+18=279, since
24*d*D*y < 2^5*2^256*2^18 at the first endpoint. These corroborate
the endpoint arithmetic; the derivatives above prove the unbounded range.

The proof does not execute a giant prime search, materialize D lengths,
prove a practical cutoff, or implement an encoded caller. The imported
prime-counting theorem is mathematical input, not a finite certificate.
Native operations, physical costs, complete numerical recovery, compiler
closure, precision/tape and selected-supplier admission remain separate.
Independent human and formal proof-kernel review are unclaimed.
