# Faster Gaussian resampling: conditional kappa = 1479/10^12 > 2^-30

October 8, 2026. Contributed by eumemic, prepared with assistance from Claude
(Anthropic). Conditional on the pinned upstream interfaces, the compact-control
construction, the compressed complex network and the written arguments below.
Not independently reviewed or formally verified.

- [Proof note (PDF)](../../artifacts/fast-gaussian-note.pdf) and
  [source](../../notes/fast-gaussian-note.tex)
- [New resampling lemmas](../../notes/fast-gaussian-resampling.tex)
- [Independent upstream patch](../../patches/fast-gaussian-30.patch)
- [Exact certificate](../../certificates/fast-gaussian.json)

## What was binding

After the compressed complex network, the completed-layer margin is
`g3 = epsilon (1 - lambda') < epsilon a_b`, and the retained Gaussian
resampling row has power `3/4 + delta + 5 epsilon/4`, which must stay below 1.
So `epsilon < 1/5` and `kappa < a_b/5 < 2^-30`. The guard
(`epsilon C1 < 1` with `C1 = 5 - 4 beta + zeta`) also bound near `1/5`, but
only because `beta` was kept tiny; the compressed complex network makes larger
`beta` available.

The line cost `O(t p^(3/2+delta) alpha)` has two sources. The map `S'` sums a
window of `sqrt(p) alpha` terms per output. The Neumann series for
`N^{-1}` needs `p/(alpha^2 theta)` terms with `theta ~ 1/(4d)`, which the
original analysis balances against the window by taking
`alpha ~ (dp)^(1/4)`.

## Two changes

**Chirped correlations.** For `sigma = t/s = 1 + theta` and integers `a, b`,

    (sigma a - b)^2 = sigma theta a^2 + sigma (a - b)^2 - theta b^2.

Every Gaussian weight at the points `sigma a - b` therefore factors into a
decaying input chirp, a kernel depending only on `a - b`, and a growing output
chirp. A block of `m` outputs is one correlation of `O(m)` fixed-point
numbers, computed exactly by packing integers and calling the established
`O(N log N)` multiplier. Blocks are chosen so the growing chirp stays below
`2^(O(p))`; the working precision is then `O(p)` and the cost is
`O(p^(1+delta))` per output, independent of `alpha`. The same algorithm
computes `S'` and the correction `E = N - I`, with the same truncation windows
and error interfaces as the cited lemmas.

**Powers of the correction.** Along a path of steps `h_i` in the expansion
of `E^n`, put `Phi(j) = sigma (beta_j^2 + 1/4) / theta`. Each step satisfies

    c(j,h) - Phi(j+h) + Phi(j) = sigma h^2 + (sigma/theta) w (2y - w) >= sigma h^2,

where `w` is the nearest integer to `y = beta_j + h theta`. Summing over the
path gives

    ||E^n|| <= exp(pi alpha^2 (1/(4 theta) + 1/2)) (2.01 exp(-pi alpha^2 sigma))^n.

The original bound `||E||^n < 2^(-alpha^2 theta n)` gains `alpha^2 theta`
bits per term; this one gains about `4.5 alpha^2` bits per term after a
burn-in of order `alpha^2/theta` bits. The Neumann series needs at most
`ceil((p+1)/(4 alpha^2) + 1/theta)` terms. The certificate checks the step
identity exactly on several `(s,t)`, and the tests compare explicit `E^n`
against both bounds.

## New parameters

`alpha = floor(sqrt(b/(8d)))` keeps `gamma = 2 d alpha^2 <= b/4`, the bound
used by the retained rounding argument, and gives `alpha^2 theta_i >= 1` and
Neumann counts at most `30 d`. The Gaussian row becomes `O(d^2 p^delta)` per
bit, with power `2 epsilon + delta`.

    epsilon = 49999/100000, c = 9999/10000, beta = 19/25, zeta = 1/10000,
    delta = 1/10^6, C1 = 19601/10000,
    lambda = 1 - 29595/10^13, lambda' = 1 - 2959/10^12,
    kappa = 1479/10^12.

The minimum margin is `g3 = 147947041/10^17`. The guard needs `beta > 3/4`
at this epsilon and the leaf needs `(1 - beta) a_c > 1 - lambda'`; with the
original complex saving `418/10^12` no `beta` satisfies both.

## Ceiling and next targets

Now `g2, g3, g4 <= a_b min(epsilon, 1 - epsilon)`, so `kappa < a_b/2 < 2^-29`
for these networks. The witness is above 99.9% of that bound. Further progress
needs a stronger bit network. Two bit-network observations from this session,
not yet proved or certified:

- The center wires can gather through total nodes of the side circuit and
  scatter at the zero label, losing `h - 1` instead of `h` each. That raises
  the bit deficit numerator from `v - 6h^2` to `v - 6h(h-1)`, about 6.5% at
  `h = 50`.
- A globally consistent block structure for the paired exclusion circuits
  merges about 1.3% more side additions at `h = 50`.

A rank argument (the Hadamard product of the Gram and integer central counts)
bounds any center decomposition's loss below by about `h^2/6`, against the
present `h(h-1)`, but small exact searches found no family beating
`h(h-1)`.
