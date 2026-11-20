## What this PR establishes

This PR groups three sequential, independently reviewed source lemmas rather than opening three overlapping PRs. It upgrades the selected *three-axis* physical Gaussian source from exact nonvanishing to explicit, error-tolerant Stein displacement bounds. The physical chirp/phase coefficients are retained throughout. **No multiplication exponent or foundational-assumption status changes.**

### Exact rank on the actual distinct-prime source

For three extremal two-point fine-prime factors, every one of the **40,320 simultaneous vertex orders** of the 8×8 tensor has ordinary Stein displacement rank eight, as does the exact tensor inverse. This strengthens the general source rank-six floor of CrocSwap/integer-mult-bounds#7598. A crucial counterexample prevents overgeneralization: three *repeated* factors can have rank six even strictly inside the older positive-decay parameter box. Distinct-prime source structure, not a generic box argument, supplies the positive theorem.

### Quantitative margins and errors

- **Two specified orders:** with common dyadic target and pairwise prime spacing at least t/(32p²), the singular-box order (0,1,2,4,6,5,3,7) and its reverse satisfy |det E(C)| ≥ a³ exp(-4a)/(2¹⁶p⁶). Forward and inverse singular-value, periodic-alias and factor-rounding errors are explicitly billed. At p≥4096, ceil(233+42 log₂ p) additional bits suffice.
- **All orders under narrower prime placement:** for p≥2²⁰, common t≥p⁷² and one source prime in each of the three specified target-ratio intervals centered at (33,47,62)/64, all 40,320 orders retain a common determinant margin D=2⁻¹⁸ exp(-8a). The rounded forward displacement has σ_min≥2⁻²²D and the exact rounded tensor inverse has σ_min≥2⁻⁵⁰D. ceil(379+72 log₂ p) fractional bits suffice. This is *not* a claim for arbitrary separated triples.

Prime existence is established only with the explicit finite fixtures and qualified eventual argument based on Trudgian's prime-count theorem. No production routine for the actual rounded coefficients is silently admitted.

### Independent checks

```sh
python3 -B scripts/research_package.py --package research/three-axis-extremal-source-rank
python3 -B scripts/research_package.py --package research/separated-three-axis-source-margin
python3 -B scripts/research_package.py --package research/narrow-three-axis-all-order-margin
```

The first package uses modular and independent integer/Bareiss enumeration of all 40,320 orders. The second reconstructs both 7,529-term determinant polynomials via subset recursion and separate Leibniz expansion, with rational Gram, inverse and alias controls. The third checks 3,360 order classes, 20,160 mixed coefficients and a separate Kronecker/Berkowitz reconstruction plus analytic review. Negative controls catch repeated-factor singularities, lost phases and undercharged errors. All original package bytes and tested branches are preserved.

### Limitations, novelty and credit

These are selected *small-tensor* theorems, not a full high-dimensional Gaussian decomposition, coefficient-table producer, transport bill, exact integer-recovery theorem or new κ. All five selected assumptions remain in the canonical certificate. Credit CrocSwap/integer-mult-bounds#7598, #7599 and #7600, their retained source authors, Tim Trudgian, and the separate model-assisted reviewers. Prepared for @CubeJerry with substantial OpenAI assistance; no human peer review or proof-kernel acceptance is claimed.