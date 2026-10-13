# Provenance, authorship, and AI assistance

Author and human developer: **Alejandro Zarzuelo Urdiales**.

This contribution originates in an earlier **Archivara** exploration of
parity-aware integer multiplication. Alejandro subsequently developed the
line of research personally with assistance from multiple AI tools, most
recently **GPT-6.1**, as recorded in his account of the development history.
The present paper, Lean development, exact arithmetic controls, and submission
preparation were produced with substantial assistance from **OpenAI Codex**.
AI assistance is disclosed as assistance, not as independent peer review.

The earlier exploration provides the motivation to retain and certify parity
information. This contribution's proofs stand independently of that draft's
broader circuit-separation, carry-saving, and benchmark claims. Those claims
are not imported as hypotheses or asserted by this submission.

## What this submission adds

The actual multiplication framework uses the Gaussian phase kernel
`C = (i I + X)/(1+i)`. For integer numerators at a common denominator exponent,
its exact division predicate is equality of the inputs' residues
`(real + imaginary) mod 2`. One retained defect bit reconstructs all four
local half-integer coordinates. The formalized lattice conversion provides
the sharp `ceil(D/2)` completed-child binary denominator bound, while the
paper distinguishes the final normalized Hadamard tensor's `D`-bit bound.

The useful deliverable is a local arithmetic and child-boundary audit
interface: check legal divisions, preserve denominator tags, and detect
incorrect parity or normalization shortcuts. It does not change a network,
assembly parameter, multiplication exponent, or existing upstream manuscript.

## Dependencies and credits

- OpenAI's pinned manuscript supplies the target `C`/`H0` interface.
- Douglas Colkitt's `CrocSwap/integer-mult-bounds` supplies the community
  framework and review workflow.
- Zhihao Chen's PR23 and the attributed RaD/hipotures semantic-child work
  supply the proposed integration site; their existing semantic precision
  argument is credited, not claimed as new here.
- Swapnil Jain's work supplies current research context and an intended
  consumer of the precision certificate.
- The independent formal checks in PR26 are a complementary precedent.
- Amy, Glaudell, and Ross (Quantum 4, 252, 2020), section 5.4, explicitly
  develop Gaussian denominator exponents and parity-based reduction. This
  submission claims a checked specialization, not priority for that arithmetic.

Exact source commits and links are in the paper and `manifest.json`.
The 69 Lean theorem declarations were freshly kernel-checked on Lean 4.31.0.
The complete axiom audit contains only Lean's standard foundational axioms;
there are no omitted proofs or project axioms. The tensor coefficient
derivation is written mathematics plus independent finite controls; full
tensor-network execution, tape costs, analytic premises, and the asymptotic
multiplication theorem are not formalized by this package.

This contribution is submitted under the destination repository's
**Apache-2.0** license. Copyright 2026 Alejandro Zarzuelo Urdiales.
