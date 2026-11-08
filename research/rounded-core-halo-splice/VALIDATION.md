# Validation and review boundary

Environment: CPython 3.12.14, Linux managed research checkout, canonical base
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Acceptance uses standard-library
integer/Fraction arithmetic. No float, transcendental approximation, network
lookup or predecessor import occurs inside the mathematical verifier.

Package metadata and source pins passed. The registered normal and optimized
commands passed with the same mandatory exact RESULT.json. The four fixtures
contain 1,408 complete outputs, 792 uniquely returned halo outputs, 2,024
copied records and 378 coefficients actually changed by inward rounding.
Three reference matrices are checked on all rows for inverse identities,
Neumann tails and kept-row comparison. These counts are finite coverage,
not the proof of the quantified result.

The test core is a dense rational section inverse followed by rounding. It
checks composition for a nonlinear implementation satisfying the assumed
contract. The actual #4205 source program, production Gaussian coefficients,
native supplier and full multiplier were not run. Python containers provide
no physical tape, space or speed theorem.

A separate Codex agent read the proof and verifier without editing them and
ran the optimized verifier. Its findings led to two corrections:

- Recovery now transfers the real-stage component-l1 error to
  complex-modulus supremum norm before using Fourier contraction. A rational
  unit-phase control shows why those norms cannot be conflated.
- Initial dyadic/J=2 fixtures did not exercise coefficient rounding or
  longer paths. Non-dyadic weights, J=3, unequal axes and a positive
  changed-coefficient count now cover both.

The reviewer independently checked a directional cycle
`H=I-(1/2)S`, N=32, L=16, A=3, J=3, a=2: all 20 kept rows satisfy the
bound, with maximum normalized row defect 1/16 below 1/4. This separate
scratch check is reported review evidence, not a retained executable
certificate. It also checked a biased-core domain example in which a
bounded nonlinear defect pushes the next input above the ideal radius.
The verifier retains its own exact 1/16-error version and rejects funding
the second call only at the ideal radius.

Parent source review requested explicit accumulated normalization bits,
restoration amplification, scan-cost limits, interval containment and
per-neighborhood coefficient-generation scope. All are now stated in
PROOF.md. Both reviews found no remaining blocker to the scoped theorem.
They are AI-assisted author-process checks, not independent human or
formal-kernel acceptance.

The live overlap refresh identified #4517 (restricted row lift), #5081
(actual nonlinear compression suffix under a local-defect premise),
#5159 (whole-period service), and #5986 (Chebyshev locality witness).
Their methods and scope are credited. The package does not claim invention
of these covered implications. Its change is the explicit row-gap
polynomial correction plus rounded common-reference core/halo error
contract and recovery-budget substitution.

Remaining obligations: independent admission of the core theorem,
production shared-reference and global approximation bounds, physical
pre-copy/return schedule and cost, actual suffix amplification, full source
transform identity and final recovery policy. No selected assumption is
marked fully discharged and no frontier is changed.
