# Exact optimization of the dyadic cut family

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

## Mathematical input and claim boundary

CubeJerry's [PR #6784](https://github.com/CrocSwap/integer-mult-bounds/pull/6784),
head `c134aa6edc8ed6444bbf7bfcabbed8124ff26c39`, section 6, supplies the
following exact mass for a chronological cut of the balanced dirty word.
For integers `h >= 2`, `0 <= k <= h-2`, and `m=h-k-1`, it reads scratch
`z_(m+1)` after `4^h-(4^k+2)/3` completed leaves and has total channel mass

```text
6 K_h(k) = (48*4^m-4)*4^k
           +(-36*4^m-24*2^m+12*3^m+3)*3^k
           +24*2^(m+k)-5.                         (1)
```

The same source proves that the global formal peak `E_h=E_infinity(2^h)`,
over all cuts, registers and both orientations, satisfies

```text
max_k K_h(k) <= E_h <= 2*4^h-3^h.                 (2)
```

We cite (1) and (2), without rechecking their free-algebra transport proofs.
The unchanged source proof is retained as [predecessor-proof.md](predecessor-proof.md),
with its original attribution. [PREDECESSOR.json](PREDECESSOR.json) binds its
exact bytes and source URL. The new proof below optimizes (1) and quantifies
its convergence. It does not determine the global finite-height peak.

## The unique optimum at every height

Let `D_h(k)=2*4^h-K_h(k)`. Substituting `m=h-k-1` in (1) gives

```text
6 D_h(k) = 4*4^k + 9*4^h*(3/4)^k + 12*2^h*(3/2)^k
           -4*3^h -3*3^k -12*2^h +5.             (3)
```

Subtract (3) at adjacent indices. For `0 <= k <= h-3`,

```text
8 [D_h(k+1)-D_h(k)] = T_h(k),
T_h(k) = 16*4^k -3^k [3*4^(h-k)-8*2^(h-k)+8].   (4)
```

The normalized quantity

```text
T_h(k)/3^k = 16*(4/3)^k - f(2^(h-k)),
f(t)=3t^2-8t+8,                                  (5)
```

is strictly increasing in `k`. Its first term increases. Its subtracted
term decreases, because `f` is strictly increasing for `t >= 4`, and the
arguments under consideration are at least eight. Thus the sign in (4)
changes at most once, from negative to positive.

There are no ties. For `k >= 1`, `T_h(k)` is one modulo three. For `k=0`
and `h>=3`, `2^h>=8`, so `f(2^h)>=f(8)=136>16` and `T_h(0)<0`.
For `h=2` there is only one candidate.

Consequently the following rule gives the unique maximizer of (1):

```text
k_h = the first k in [0,h-3] for which T_h(k)>0;
      use h-2 if that set is empty.
m_h = h-k_h-1.                                   (6)
```

This is an exact integer criterion. Bisection uses at most
`ceil(log2(h-1))` sign comparisons. The count is a comparison bound,
not a bit-complexity or physical tape-cost claim.

For example `h=11` gives `k_h=8`, `m_h=2`, cut `4^11-21846`, and readout
`z_3`. Its mass is `7,735,559`. The `m=1` member has mass `7,716,024`.
These values evaluate the cited formula, rather than replaying its native
realization. The improvement inside this explicit family is `19,535`.

## A sharp exponent for the family's deficit

Define real constants

```text
alpha = log(4)/log(16/3),
lambda = 4^alpha,
beta = log_2(lambda) = 4*log(2)/log(16/3).
```

Here `beta` is about `1.656289`. For every integer `h>=2`, the optimized
family deficit `D_h=min_k D_h(k)` satisfies

```text
lambda^h/6 <= D_h <= 6*lambda^h.                  (7)
```

Thus `D_h=Theta(lambda^h)=Theta(n^beta)` for dyadic `n=2^h`. The exponent
is sharp within the family (1). This does not assert that the global peak
has a deficit of this order.

To prove the lower bound, put `Q=4^h*(3/4)^k`. Since `h-k>=2`,

```text
9Q >= 16*3^h,
4*4^k-3*3^k >= 4^k,
12*2^h*((3/2)^k-1) >= 0.
```

Equation (3) therefore implies `6D_h(k) >= 4^k+Q`.
The two expressions `4^k` and `Q` are equal at the real index
`k=alpha*h`, with common value `lambda^h`. One increases in `k` and
the other decreases. Hence their maximum is always at least `lambda^h`,
proving the lower bound in (7).

For the upper bound take `k=floor(alpha*h)`. For `h>=12` this is a legal
family index: `alpha<5/6` follows from `3^5<4^4`. Then

```text
4^k <= lambda^h,
Q <= (4/3)*lambda^h,
2^h*(3/2)^k <= lambda^h.
```

For the third inequality it suffices that `2*(3/2)^alpha < 4^alpha`.
Indeed

```text
alpha*log(8/3)-log(2)
    = log(2)*log(4/3)/log(16/3) > 0.
```

Dropping the negative terms in (3) now gives
`6D_h(k) <= 28*lambda^h+5 <= 33*lambda^h < 36*lambda^h`.
For the ten remaining heights `h=2,...,11`, exact evaluation of (1),(6)
gives deficits

```text
19, 64, 209, 668, 2109, 6624, 20809, 65668, 208949, 653049.
```

Each is at most `6*3^h`. Finally `lambda>3`, since
`log(4)^2-log(3)*log(16/3)=(log(4)-log(3))^2>0`.
This establishes the upper bound of (7) at every height.

## Quantitative consequence for the global peak

Combining the cited envelope (2) with the new constructive bound (7) gives

```text
3^h <= 2*4^h-E_h <= 6*lambda^h,
n^(log_2(3)) <= 2*n^2-E_infinity(n) <= 6*n^beta,
0 <= 2-E_infinity(n)/n^2 <= 6*n^(-(2-beta)).        (8)
```

The last two lines apply to dyadic `n>=4`. This gives an explicit
power-saving convergence rate where the predecessor supplied a limit.
The lower and upper exponents for the global deficit still differ.
No arbitrary-`n`, exact global optimum, error-budget profile, physical
rounding realization, new multiplier or new kappa follows.

## Executable evidence and remaining obligations

The verifier checks the new integer optimization, adjacent identity and
rational enclosures used for (7). It takes (1) as input and does not
execute any predecessor verifier or reconstruct its channel polynomials.
Its finite arithmetic checks corroborate the written proof; they do not
replace the all-height argument. The same explicit checks run under `-O`.

Python allocates integers dynamically. This is the bounded managed-runtime
deviation to Power of Ten rule 3: height is restricted to `2..4096`, the
exhaustive range to `2..256`, and no word of length `4^h` is materialized.
All loops have bounds, functions are at most 60 lines, failure checks use
explicit exceptions, and there is no recursion, dynamic code or network
access. Warning-strict normal and optimized replay provide interpreted-code
diagnostics; no external static analyzer is a dependency. Expanding the
height bound requires revisiting integer resource bounds.

All five selected framework assumptions remain. Independent human review,
formal proof-kernel review, native rounding, internal leaf errors, inverse
precision, physical storage/access and a complete selected caller are unrun.
