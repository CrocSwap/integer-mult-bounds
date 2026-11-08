# Rounded finite cores with a common-reference sparse halo

**Scoped composition theorem and exact finite controls; no new kappa.**
A finite-core inverse can be rounded and nonlinear. This package gives a
complete cyclic/tensor error bound when those cores are joined to rounded
local halo rows of the same reference, using input copies saved **before**
core mutation. The number of cores and global axis lengths do not enter the
maximum-norm error bound.

The halo polynomial here is `sum_{j<J}(I-H)^j`, using the already required
row gap `||I-H||_infinity<1`. It is an explicitly proposed replacement for
#4100's normal-equation polynomial, not an assertion about an unchanged
implementation. The result consumes the all-input finite-core contract of
[#4205](../rational-unitary-fft/CORE-PROOF.md), retained via #4253. It does
not independently certify that predecessor's circuits or the whole
`analytic_recovery` assumption.

[PROOF.md](PROOF.md) states the complete quantified argument. For each axis,
let `delta=1-rho`, `K=1/delta`, `tau=K rho^J` and choose a dyadic normalizer
`a>=K`. If the actual core inverse has uniform error `epsilon` on radius
`2R0`, and the rounded normalized halo axis has error `eta` on radius `R0`,
the completed g-axis splice has error at most

```
max(sum_i epsilon_i/a_i + 2R0 sum_i tau_i/a_i,
    sum_i eta_i         +  R0 sum_i tau_i/a_i).
```

This requires `sum_i epsilon_i/a_i<=R0`. The proof establishes that later
core calls see their actual rounded inputs inside the admitted radius.
It keeps all errors on discarded core rows until those rows are replaced;
it never assumes rounding is linear or that a discarded error vanishes.
Absolute-coordinate polynomial paths preserve holes, phase changes and
periodic wraps. A complete intermediate rectangle is retained through the
halo tensor evaluation.

The normalizers add fractional bits and their product amplifies any error
when restored. Both charges are explicit. The recovery substitution uses
complex-modulus supremum norm; normalized Fourier transforms need not
contract the component-l1 norm used by the real Gaussian stages. A complete
outer suffix bound and both source-size factors remain required.

## What changes downstream

Subject to the cited finite-core contract and the fixed reference's row
gap, this supplies the local-to-global numerical defect for the alternative
sparse correction. A bounded exact inverse alone would not have done that:
the core call's actual input domain, retained pre-core inputs, coefficient
rounding, data rounding, output masks and final scalars all enter the proof.

This is not a production physical splice or a faster multiplication theorem.
It does not supply the global Gaussian/reference error, arbitrary-size
parameter policy, actual page/tape delivery, supplier correctness, complete
CRT/Fourier identities or recovery scale. Extra normalization scans must be
paid unless the shifts are folded into existing writes. No selected file,
frozen source or upstream file is changed.

## Verification

From the repository root, CPython 3.12, standard library only:

```sh
python3 -B scripts/research_package.py --package research/rounded-core-halo-splice --check-only
python3 -B scripts/research_package.py --package research/rounded-core-halo-splice
```

The registered normal and optimized checks compare the exact typed
[RESULT.json](RESULT.json). They run in a few seconds, without regenerating
package files. `verify.py --write-receipt` is the explicit development mode.

Three synthetic rational references include nonconstant directional
coefficients, exact identity holes, cross-period couplings and powers through
`J=3`. Their inverse and kept-row defect checks use exact fractions. Four
rounded 1D/2D executions cover **1,408 outputs**, **2,024 saved-copy records**
and **378 nontrivially rounded coefficients**, including unequal 24-by-32
axes. Every sparse rectangle endpoint is compared to the full tensor
polynomial on its original input. Actual core errors and actual next-input
radii are checked separately.

The finite core test double performs a dense exact section inverse followed
by component rounding. It satisfies the declared nonlinear error contract;
**it is not an execution of #4205's fast core**. Dense matrices, dictionaries
and exact inverse oracles are verification machinery, not a tape algorithm.

Twelve controls distinguish changed references, deleted period paths,
insufficient strips, stale post-core input copies, nonlinear rounding,
half-unit ties, a missing source-size factor, product cross-error, premature
intermediate cropping, an ideal-only radius, unpaid normalizers and the
complex-norm seam. An additional biased-core example sends the next input
above its ideal radius and is rejected by an incorrectly funded caller.
Finite evidence corroborates the written theorem; it is not its universal
proof or independent human/proof-kernel acceptance.

## Sources, overlap and credit

Base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.
The selected conditional result remains `781451/250000000` from #6030.
[SOURCES.json](SOURCES.json) pins seven live mathematical texts and separate
provenance/overlap sources. [OVERLAP.json](OVERLAP.json) records the focused
live searches and exact PR heads. Coverage includes relevant retained
packages and the listed PR bodies; it excludes arbitrary diffs, unpublished
work and an exhaustive literature or Discussion search.

The initial circuit-prefix investigation was stopped after finding the
already-completed leading-section/full-gate theorem in
`rational-unitary-fft` and its `full-toeplitz-cut-audit`. The new task follows
the former's explicit core/halo boundary instead. Relevant prior results
are distinguished rather than claimed anew:

- #4217 proves the normal-equation polynomial locality and its two-tail
  factor of two; #4517 proves the restricted kept-row tensor lift.
- #4870 proves the first-boundary rectangle copy enumeration.
- #5081 proves the actual physical compression suffix recurrence given a
  uniform local defect, including computed inputs and all-halos-first
  ordering. This package supplies a different local defect from the
  #4205 finite-core contract and the proposed direct-Neumann halo.
- #5159 and later periodic/direct consumers compute whole-period inverse
  actions, rather than this core/sparse replacement.
- #5986 gives a Chebyshev locality-degree improvement under two-sided
  2-norm conditioning. No locality-degree priority claim is made here.

Credit Cinna Davis/#4100, Jose Manuel/jmbarrancoml/#4205, Nick
Petalas/#4217, Ryanson Jonathan/#4517, the halo-copy-enumeration authors,
JoyboyBrian/#5081/#5159, Ali Romman and the periodic direct-solver authors,
Mason Hale/#2313, Vlado Vojdanovski/#1673, Jeremy Kothe/IdeaOuter/#1758,
Chafik Boukhalfa/#1786, and the retained Harvey--van der Hoeven lineage.
The kept-row lift, nonlinear-error induction, classical Neumann series and
tensor telescoping are not claimed as new general methods.

Prepared for **@CubeJerry**, with substantial OpenAI Codex assistance in
source analysis, proof, implementation and adversarial AI review. That review
belongs to the author process, not independent human acceptance. Apache-2.0.
See [VALIDATION.md](VALIDATION.md) for the review corrections and actual checks.

## Open next questions

Bind this exact pre-copy/core-mutation/unique-return transaction to a
production physical tensor caller with one admitted reference. First inspect
saved payloads at a periodic corner and hole, then pay pages, retained
copies, shifts and cleanup. Production delivery and complete tape costs
remain blockers.

Independently admit the retained finite-core all-input proof and instantiate
the outer suffix and recovery scales, including every dyadic normalizer.
The existing core supplier, global Gaussian approximation and complete
recovery budget remain explicit premises. Structured details are in
[TASK.json](TASK.json).
