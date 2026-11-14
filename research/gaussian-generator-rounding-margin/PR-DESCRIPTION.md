## What changed and why it matters

Exact displacement rank alone does not exclude a shorter representation
after rounding. This package proves explicit approximation margins for a
Gaussian tensor's Stein boundary minor and its inverse target. Approximations
inside those margins require at least `2T/n_fast` ordinary lower-times-upper
Toeplitz generator terms.

The boundary minor has inverse norm at most
`K=V(m/b_-1+m/b_1)+2UV^2m^2/(b_-1 b_1)`. The forward error threshold is
`1/(2K)`. Two Schur factorizations and persymmetry give the inverse threshold
using `Kinv=max(K,U0)(1+U0)^2(1+V0)^2`.

With the source-compatible logarithmic Gaussian parameters, polynomial local
dimensions, phase gap at least a constant times p^-2, and `g<=p^beta` for
fixed beta<1, both logarithmic margin costs are `O(g log p)=o(p)`. Explicit
inequalities protect Cp-bit direct entry rounding and per-factor table
rounding, including the tensor of exact rounded-factor inverses.

## Provenance and predecessor credit

Base: `e54523517d0f03e58352e647c403a5af3e525a57`. SOURCES.json contains eight
exact Git-blob/SHA256 provenance pins. The verifier is standalone with no
external runtime inputs or third-party dependencies.

This extends the
[boundary-minor package at 326844a](https://github.com/CubeJerry/integer-mult-bounds/tree/326844a3e0c570fdafa4f3737095cd37154743a6/research/tensor-gaussian-displacement-rank)
with quantitative conditioning, inverse-target transfer and the Cp-bit
rounding bridge. It restates the required algebra and does not require the
unmerged predecessor object for replay. Preserve Vlado Vojdanovski's
capped-phase-fusion credit, the fractional-shift source and Chafik Boukhalfa's
fine-prime work (#1786). The accretive symbol lemma is attributed retained
work, with NIST DLMF 20.5.9 as primary product-identity background.

## Reproduction and checks

```sh
python3 -I -W error -B research/gaussian-generator-rounding-margin/verify.py
python3 -I -O -W error -B research/gaussian-generator-rounding-margin/verify.py
python3 scripts/research_package.py --package research/gaussian-generator-rounding-margin --check-only
python3 scripts/research_package.py --package research/gaussian-generator-rounding-margin
```

Both standalone runs passed in Python 3.12.14 with identical output: 27
arbitrary-A fixtures, six Gaussian tensors, 39 exact rational PSD singular-gap
certificates, 39 protected perturbations, 39 direct roundings, and six
factor-table roundings across twelve targets. Six controls cover a false
shifted two-point bound, actual low-precision rank loss, forged gap and
indefinite-matrix certificates, beta=1, and zero half-shift gap. Checks remain
active under optimization. The all-size proof is in PROOF.md.

## Limitations, open questions and kappa status

This is a linear-matrix representation lower bound, not a runtime lower bound
for separable circuits, arbitrary permutations or nonlinear rounded
arithmetic. Unstructured errors may increase rank. Shifted two-point factors
are excluded from the geometric shortcut. Paid gauges, actual periodic
Reference matrices, holes, source conversion and the complete recovery bill
remain open; concrete next questions identify those obligations.

**No new kappa.** The selected #7000 value remains
`363005817/100000000000`, conditional on all five inherited assumptions.
No practical cutoff is asserted for its tiny exponent slacks.

Prepared for @CubeJerry with substantial OpenAI ChatGPT assistance. The
worker derived and packaged the theorem; the orchestrator independently
checked the inverse Schur and uniform precision arguments. Predecessor
attribution is retained. New files are Apache-2.0.

## Independent publication review

REVIEW.md independently checks the boundary norm, indexed inverse Schur argument, source accretivity, explicit constants and precision inequalities. Registered normal/optimized replay, eight exact source pins, committed bytes/modes, direct base ancestry and export checks pass. VALIDATION.json records the scope. No full-history gate success is claimed for the intentionally shallow checkout.
