# Exact parameter refinement of PR21

The unchanged translated partial-swap construction supports the conditional bound

**T(n) = O(n (log n)^(1 − κ)), κ = 57114918/10^13 = 5.7114918 × 10^-6.**

This increases the final exponent saving by about 3.86419% over
[PR21](https://github.com/CrocSwap/integer-mult-bounds/pull/21), pinned at
`5ba6cf0bfb68f2be8d15610e7972207c50254d6a`. The finite construction and all
conditional hypotheses are unchanged. This is an arithmetic refinement, not a
new network or a formal verification of the multiplication theorem.

## Bit moment and its sufficient-envelope ceiling

Retain PR21's complete multiset of 35 child widths and multiplicities `c_t`,
with `m = 32775`, `W = 5820554077800` and deficit `Wm − Σ c_t t = 82076640800`.
All widths satisfy `0 < t < m`. Set

```
a_b = 2284609773/200000000000000 = 0.000011423048865
```

For each width, let `L_t` be the exact rational upper enclosure of `log(m/t)`
from `scripts/partial_swap_network.py`. With `u_t = a_b L_t`, all `0 ≤ u_t < 1`.
The retained Taylor enclosure gives

```
Σ c_t t^(1-a_b) / (W m^(1-a_b))
  ≤ U(a_b) = Σ [c_t t/(Wm)] [1 + u_t + u_t²/(2(1-u_t/3))]
  < 1 − 10^-17.
```

The exact gap is approximately `1.0744802171 × 10^-17`; the certificate stores
the full rational value. Thus PR21's arbitrary integer-width row construction,
padding, spectator handling and cleanup apply with the stronger bit exponent.

At `a_b + 10^-15`, the same rational envelope exceeds one by approximately
`2.6920999423 × 10^-17`. Each summand is strictly increasing in `a` in its
valid domain. Consequently this is the largest feasible multiple of `10^-15`
for this sufficient envelope. This brackets that envelope's ceiling only;
failure of an upper bound to contract does not show that the exact moment
fails, nor exclude other constructions or better enclosures.

## Dependency argument and exact final assembly

Use PR21's complex saving `a_c = 18/10^6`, translated complex phase network,
and its precision guard `rho = 2`, `C1 = 19991/10000`. Its moment gap remains
greater than `666/10^11`. The bit and complex dimensions may differ under
the retained arbitrary-width interface. No circuit, basis, endpoint, path
budget, coefficient allowance or precision constant changes.

Choose the following exact parameters:

```
tau     = 1 − a_b
sigma   = 1 − 18/10^6
epsilon = 1/(2+a_b) = 200000000000000/400002284609773
c       = 1
beta    = 1/1000
delta   = 1/10^16
lambda  = tau + 1/10^20
lambda' = tau + 2/10^20
C1      = 19991/10000
kappa   = 57114918/10^13
```

Because `sigma < tau` and `(1-beta)a_c = 17982/10^9 > a_b`, the
compact-control internal exponent is `tau`, and its leaf and preprocessing
exponents are below `lambda'`. The strict gaps absorb fixed logarithmic
factors. The precision constraint `1 − epsilon C1 > 0` remains strict.

The seven final margins are

```
g1 = 1 − 2 epsilon                  g2 = epsilon a_b
g3 = epsilon (a_b − 2/10^20)         g4 = (1−epsilon) a_b
g5 = 1 − delta − 2 epsilon           g6 = 1 − delta − epsilon
g7 = epsilon
```

Their minimum is `g5 = a_b/(2+a_b) − delta`. Exact subtraction gives

```
min(g_i) − kappa
 = 2284609773/400002284609773 − 1/10^16 − 57114918/10^13
 > 1/10^14 > 0.
```

The certificate checks all 29 strict interface constraints and seven strict
absorption margins using the unchanged PR21 assembly functions. The positive
Gaussian and spacing exponents give the eventual conditions, with the retained
corrected chirp enclosure and precision `P = 34p`. Under the same upstream
analytic, ordered-affine, common-basis, compact-control, Gaussian-map and
fixed finite-alphabet multitape hypotheses, the multiplication theorem then
gives the displayed bound. Every dependency stated in PR21 remains required.

## Reproduction and pinned proof patch

```
make translated-partial-refinement
git apply --check patches/translated-partial-refinement.patch
make verify
```

The generator first recomputes and compares the complete retained PR21
certificate, including source hashes, the stored producer reconstruction,
the complex phase evidence and old arithmetic. It then certifies the stronger
parameters and rejects both the next bit grid point and a final saving above
the assembly minimum. The existing `make verify` producer target independently
reconstructs the unchanged scalar circuits.

The generated [proof patch](../../patches/translated-partial-refinement.patch)
targets `notes/translated-partial-assembly.tex` at the pinned PR21 commit above.
It is an incremental patch against that proof, not a replacement for the
inherited original-manuscript patch. Apply it to a copy of PR21 to substitute
the stronger exact witness in its theorem and proof. The historical PR21
sources and certificate remain unchanged here so their hashes can be checked.
No PDF is generated or updated for this refinement.

## Attribution

Dominik Scholz contributed this parameter refinement with substantial OpenAI
Codex assistance. The translated bit endpoints, compatible corners, complex
phase construction and revised guard are Zhihao Chen (jacklightChen)'s PR21
contributions. They build on icekylinx's PR18 scalar producers, partial-swap
network and basis; eumemic's PR13 source-frame idea; Zhihao Chen's PR7/PR16
finite networks and nested bases; icekylinx's PR10 batching; and Douglas
Colkitt's framework and the other contributors recorded in NOTICE.
All preceding attribution and Apache-2.0 notices are retained.
