# Prove exact finite Gaussian rounding thresholds with compact Hall witnesses and independently checked orbit-flow certificates

## Exact result and why it matters

For injective integer-output rounding of H4/2 with uniform Euclidean error
at most1, the complete radius-five lattice ball has exact optimal outward
slack `sqrt(21)-sqrt(19)`. The exact optima are `sqrt(31)-sqrt(28)` on
radii6 and7, and `sqrt(78)-sqrt(73)` on radii9 and11. Radius10 follows by
inclusion, without a separate computation. The explicit signed-permutation
identity `H4=L(2C+)R` transfers these results to the ideal Gaussian pair of
#6509 and its conjugate.

Thus any global injection under these error hypotheses needs outward slack
at least `sqrt(78)-sqrt(73)`. The available global interval is
`[sqrt(78)-sqrt(73),1]`; the upper endpoint is inherited from #6509.
Finite injections do not establish global attainment.

## What changed and novelty relative to predecessors

#6619 raises the rational norm-rounding question and credits #2589's
finite-sphere method; #6509 supplies the Gaussian map and a global error-one
construction. This package supplies exact finite optima and a necessary
global lower bound without period, conserved-sum or equivariance premises
on the unknown rounder. Classical Hall and symmetry facts are credited as
such; the explicit certificates and source-bound transfer are the new work.

The radius-five lower bound has a short two-exclusion proof. Remove the
signed coordinate orbits(0,0,3,3) and(0,1,3,3) from the squared-norm19 ball,
obtaining1,777 points. Add the32 positive-product permutations of(2,2,2,3),
obtaining1,809 inputs; every error-one neighbor below the strict threshold
lies in the1,777-point set. Only38 input-orbit representatives need checking.

The extension gives reusable positive flow and Hall-cut certificates on
paired W(D4) orbits. Biregularity, rather than complete bipartite adjacency,
lifts a saturated quotient flow to a fractional matching and then an actual
finite injection. At radii6/7 the strict Hall sizes are3,569/3,537; at9/11
they are23,561/23,497. Full orbit predicates and exact capacities are retained.
This extends the same mathematical package and does not create a separate
PR for each finite radius.

## Reproduction and independent checks

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
Original verified R5 package: `9c75d0b4b6e1cfe74694edf52f2f238a741bbaf5`.

```sh
python3 -I -W error -B research/sharp-finite-gaussian-outward-slack/verify.py
python3 -I -W error -B research/sharp-finite-gaussian-outward-slack/compact-hall/check.py
python3 -I -W error -B research/sharp-finite-gaussian-outward-slack/orbit-extension/verify.py
python3 -I -O -W error -B research/sharp-finite-gaussian-outward-slack/orbit-extension/verify.py
python3 -I -W error -B research/sharp-finite-gaussian-outward-slack/review/extension/check_full_certificates.py
python3 -I -W error -B research/sharp-finite-gaussian-outward-slack/review/extension/check_full_r9.py
```

These standard-library commands are read-only. Normal/optimized search and
verification receipts agree. The independent full-point checker reconstructs
all1,551,060 candidate edges over the four extension domains, checks actual
point-count orbit capacities, positive-flow conservation and complete Hall
neighborhoods, and imports no author generator or radical comparator. It
rejects changed flows, missing neighbor orbits and strict/inclusive boundary
confusion. A separate full-vertex radius-nine matching has32,633 inputs,
strict maximum32,569 and full saturation when equality edges are admitted.
Its different Hall set has23,057 inputs and22,993 outputs, agreeing on
maximum deficiency64. The original certificate, compact checker and source
transfer also retain their corruption and tie controls.

## Limitations, kappa and credit

This is a scoped rounding obstruction and exact finite verification package.
It supplies no global map at the lower endpoint, unrestricted forward1/2
bound, selected caller admission or physical rounding tariff. It does not
reject the selected exact-layer route. **No new kappa; all five multiplication
assumptions remain.** Selected conditional kappa is `0.00363005817`.

Prepared for @CubeJerry with substantial OpenAI Astra/Sol/Luna assistance in
candidate construction, proofs, code and independent checking. Credit Nick
Petalas (#6619), ywz65 (#2589), Ali Romman (#6509), and the retained source
authors in SOURCES.json and NOTICE.md. Independent AI implementations are
not human review or formal-kernel acceptance. No upstream PR is submitted.
