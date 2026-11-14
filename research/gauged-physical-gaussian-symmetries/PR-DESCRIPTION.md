# Proposed title

Prove diagonal-gauge and inverse-error bounds for symmetry cycles of physical fine-prime Gaussian blocks

# Proposed description

## What changed and why

The preceding [heterogeneous Gaussian symmetry package](https://github.com/CubeJerry/integer-mult-bounds/tree/be76d6ae53fc887f977a04ceaa6ef56bb9e98fb7/research/heterogeneous-gaussian-symmetries)
handles normalized ideal square kernels. Its explicit remaining interfaces
include diagonal gauges, the actual physical capped blocks and inverse-error
transfer. This package proves those scoped implications and keeps the
conditioning, grid correspondence and coefficient-storage costs visible.

For any two-sided invertible diagonal gauges G=LHR, the exact normalized
pair product recovers the unshifted weighted Gaussian metric. The complete
monomial centralizer is `c A P A^-1`, where P preserves both that metric and
the actual diagonal products. Distinct widths force P to be a product of
coordinate reflections. A weighted monomial can still have infinite order;
the proof bounds the underlying vertex cycles, not the weighted order.

Across all gauges, the minimum cycle count is exactly `ceil(T/2)`. Thus the
existing specified dense cycle-boundary format requires at least
`2T ceil(T/2)` scalar slots. This is a format count, not a lower bound on
minimal displacement rank, implicit representations or multiplication time.

## Actual source and precision result

The retained same-cell narrow physical block has unit diagonal and every
entry at most one, including its chirp. The matching centered broad block
has maximum entry `alpha^-g` and diagonal floor
`alpha^-g exp[-(b/4)sum_i(1+theta_i B_i)^2]`; its scalar normalizer is paid.
These direct physical bounds close the source scope left open by the
normalized predecessor.

The normalized ratio error is at most `24M epsilon/delta^2`. Exact symmetry
containment follows when twice that bound is below the source edge/color
separation. For an entrywise approximation to the finite inverse, the proof
first pays the dimension factor and transfers to a forward error at most
`2T^3 M^2 epsilon`, with all invertibility and margin conditions stated.
The retained fine-prime regime makes the diagonal floor, tile dimension and
width gap compatible with Cp-bit errors eventually. Inverse coefficient
magnitudes separately use the retained chirp guard and symbol bound.

## Exact dependencies and novelty

- Canonical main: `e54523517d0f03e58352e647c403a5af3e525a57`.
- Immediate predecessor: CubeJerry commit
  `be76d6ae53fc887f977a04ceaa6ef56bb9e98fb7`; its proof is retained exactly
  and was compared in full with the published contents.
- Canonical fractional-shift and fine-prime notes are retained with exact
  byte, SHA256 and Git blob pins in `DEPENDENCIES.json`.
- The diagonal invariant, finite box geometry and Neumann identity are
  classical. The contribution is this monomial/physical-source/error and
  complete dense-format boundary, not general literature priority.
- Bounded overlap reads distinguish CrocSwap/integer-mult-bounds#6099,
  CrocSwap/integer-mult-bounds#5216, CrocSwap/integer-mult-bounds#6533,
  CrocSwap/integer-mult-bounds#6613, CrocSwap/integer-mult-bounds#4035 and
  CrocSwap/integer-mult-bounds#2066. Their production, inverse, capacity,
  tariff and Pauli results retain their separate claims and credit.

## Reproduction and checks

```sh
python3.12 -I -W error -B research/gauged-physical-gaussian-symmetries/verify.py
python3.12 -I -O -W error -B research/gauged-physical-gaussian-symmetries/verify.py
python3.12 -B scripts/research_package.py --package research/gauged-physical-gaussian-symmetries
```

The first two read-only commands pass with identical receipts. They
authenticate three exact inputs, check all 81,464 vertex permutations for
each of forward/inverse targets across nine fixtures, verify 922 exact
physical-source exponent pairs, and exercise rational forward/inverse
perturbation bounds. Eleven controls catch tiny-gauge coarse rounding,
weighted-order confusion, missing diagonal-product constraints, inverse
metric misuse, section/inverse interchange and invalid source phase/band
premises. The universal proof is written separately; enumeration is finite
corroboration. Independent review and publication gates are recorded in
their own files rather than attributed to the primary replay.

## Limitations and open obligations

**No new kappa.** The accepted complete bound remains conditional at
kappa `0.00363005817`; all five foundational assumptions remain.

The physical rounded specialization is an all-broad or all-narrow tensor
of matching square grids with the stated phase conditions. Mixed families,
rectangular or independently indexed blocks, periodic wraps, cross-cell
coefficients, identity holes, Schur pivots, repeated copies and a current
global caller need separate identification. An entrywise error tolerance
does not produce a coefficient table or inverse algorithm. Initial source
acquisition, setup, diagonal application, precision, transport and actual
access all remain charged.

The next constructive question is an actual implicit or non-cycle
generator application with a complete paid budget. This package does not
rule out that route or change the selected certificate.

## Credit

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Credit the preceding orbit/heterogeneous-width packages, Vlado Vojdanovski's
capped phase-cell work, the fractional-shift and fine-prime lineage, and
all retained source attributions. The lead orchestrator proposed the
invariant/error objective; the worker independently derived and checked the
centralizer, physical bounds, inverse transfer and controls. Separate
AI-agent cross-review is not human or formal-kernel certification.

## Independent review

`review/REVIEW.md` records a separate rational-complex checker and direct weighted commutator solution, with no imports from the author mathematical implementation. It checks 822 complete permutations for each forward/inverse target across six fixtures, 1,252 physical-source exponent identities, the precision inequalities and ten negative controls. Normal and optimized receipts agree. The physical entry-error tolerance does not establish that the actual global source pipeline supplies that error; that obligation remains explicit.

```sh
python3.12 -I -W error -B research/gauged-physical-gaussian-symmetries/review/independent_check.py --package research/gauged-physical-gaussian-symmetries
python3.12 -I -O -W error -B research/gauged-physical-gaussian-symmetries/review/independent_check.py --package research/gauged-physical-gaussian-symmetries
```
