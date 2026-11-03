# Proof: one tail-sum sign change gives one positive crossing

## Lemma (Laguerre's rule of signs, tail-sum form)

Let `F(t) = sum_{k=0..n} c_k r_k^t` with real `c_k` and ranks
`0 < r_0 < ... < r_n`. Put `B_k = c_k + ... + c_n`. Then the number of distinct
zeros of `F` on `t > 0` is at most the number `S` of sign changes in
`B_0, ..., B_n` (zeros ignored).

This is classical: Pólya and Szegő, *Problems and Theorems in Analysis II*,
Part V, Chapter 1; Karlin, *Total Positivity*, Chapter 5. For the reader, the
reduction is as follows.

*Proof.* Put `m_k = ln r_k` and `B_{n+1} = 0`. Since `c_k = B_k - B_{k+1}`,

```text
F(t) = B_0 e^{m_0 t} + sum_{k=1..n} B_k (e^{m_k t} - e^{m_{k-1} t}).
```

For `t > 0`, `e^{m_k t} - e^{m_{k-1} t} = t * integral_{m_{k-1}}^{m_k} e^{u t} du`
and `e^{m_0 t} = t * integral_{-inf}^{m_0} e^{u t} du`. Hence

```text
F(t) = t * integral_{-inf}^{m_n} beta(u) e^{u t} du,
```

where `beta = B_0` on `(-inf, m_0]` and `beta = B_k` on `(m_{k-1}, m_k]`. The
step function `beta` has `S` sign changes. The kernel `e^{ut}` is strictly
totally positive, so its transform has at most `S` zeros on `t > 0`
(variation-diminishing property; Karlin, Chapter 5). Dividing by `t > 0`
does not change zeros. ∎

`B_0 = F(0)`. If `S = 0`, `F` has no zero on `t > 0`.

## Application to the binary query-tree bill

[PR6348](https://github.com/CrocSwap/integer-mult-bounds/pull/6348)
(`research/balanced-query-tree`, Ali Romman) has 19 full calls with the local
profiles, 16 thin queries of 104 rank-one calls, the main targets
`{17:1872, 25:208, 33:832, 57:208, 65:208, 153:208}` and the paired whole idle
jobs `{16:1872, 24:208, 32:832, 56:208, 64:208}`. The checker rebuilds this bill
from the source `RESULT.json` and checks its totals, 14214 fields and 70523
paid calls.

Let `F(t) = sum_r (T_r - P_r) r^t`. Its nonzero coefficients, in rank order,
are

```text
1:-43502  2:-8512  3:-9348  4:171  5:-2869  6:-114  8:342  9:7315
16:-1872  17:1872  24:-208  25:208  32:-832  33:832  56:-208  57:208
64:-208  65:208  153:208
```

The coefficients change sign 13 times, so a Descartes count allows up to 13
real roots. The tail sums, in the same order, are

```text
-56309 -12807 -4295 5053 4882 7751 7865 7523 208 2080 208 416 208 1040
208 416 208 416 208
```

They change sign exactly once. By the lemma, `F` has at most one zero on
`t > 0`. Since `F(0) = -56309 < 0` and `F(1) = 808 > 0` (the rank-mass
surplus), `F` has exactly one zero `t*` on `t > 0`. It lies in `(0,1)`, and
`F < 0` on `(0, t*)` and `F > 0` on `(t*, inf)`.

**Consequence.** With `t = 1 - C`, the complete raw target moment of this bill
strictly exceeds its paid moment exactly when `C < 1 - t*`, for every
`C < 1`. The source check proves uniqueness only for `C <= 0.0034` through a
derivative bound; this certificate excludes a second favourable window on
the rest of the range. The location of `1 - t*` is the source's enclosure
`(0.00314934401301, 0.00314934401302)`. This package does not recompute it.
A 60-digit decimal sign check at `t = 0.99685` and `t = 0.99686` is a
consistency control only; the root location is not part of the claim.

## Scope

This is a statement about one invoice's arithmetic. It does not touch the
construction, native maps, compiler, outer ledger or any of the five retained
framework assumptions, and claims no new κ.
