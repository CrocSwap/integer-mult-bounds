# Sharp rounding bounds for cyclic scans

**Mathematical refinement, no new kappa.** The clean two-pass periodic scan
from [PR628](https://github.com/CrocSwap/integer-mult-bounds/pull/628) has
length-independent error at most `4(B+1)u/beta^2`, under `u <= beta/2`.
The existing sufficient bound is `6(B+1)u/beta^3`, under `u <= beta^2/2`.
Here `u` is the working grid spacing, `B` bounds the input magnitude,
and all exact complex coefficients have modulus at most `1-beta`.

[PROOF.md](PROOF.md) proves the result for every cycle length, either
orientation, and arbitrary varying coefficients within the margin.
A one-entry dyadic family has error at least `u/(4*beta^2)` for the same
algorithm and rounding rule. Thus the inverse-square margin dependence is
necessary for a uniform bound on this algorithm.

The proof also lowers PR628's sufficient factor-cascade execution precision
by at least `g` bits when `beta=2^-g`. It preserves the coefficient and
phase-preparation assumptions. The asymptotic `O(p+r^4)` precision bound
stays the same. No runtime improvement, factorization implementation,
supplier admission, selected frontier change, or full multiplication proof
follows. This package proposes a guard refinement; it does not activate it
inside PR628 or modify that contribution's files.

## Reproduce

From any working directory, run with Python 3.11 or later:

```sh
python3 -B /path/to/repository/research/cyclic-scan-sharp-bound/verify.py
```

Expected status: `PASS_SHARP_CYCLIC_SCAN_BOUND`.
The command checks source hashes and compares its full result with
[EXPECTED.json](EXPECTED.json). It uses only the standard library.
To preserve a fresh receipt, use `--write /absolute/new/result.json`.
The output path must not exist. The default command never overwrites evidence.

## Evidence and independence

- 5,024 cases compare the rounded output with an independently evaluated
  finite geometric inverse. This oracle evaluates each matrix row directly.
- 24 longer cases, through length 2,048, use exact residual certificates.
  Dividing the residual norm by `beta` bounds the forward error.
- 3,362 cases match PR628's unchanged varying-coefficient scan exactly.
  Of these, 482 also match its unchanged constant-coefficient scan.
- 1,686 cases meet the new guard but lie outside the original admission.
  The new integer-grid implementation executes these cases.
- 64 exact members of the sharp family match the symbolic output and error
  formulas in the original scan and the integer-grid implementation.
- 384 exact cascade recurrences and 276 inherited-budget comparisons check
  the precision formulas. The written inequalities establish their scope.
- Seven controls reject missing closure, wrong denominator sign, substituted
  coefficients, wrong orientation, unstable coefficients, insufficient
  admitted precision, and a false inverse-linear margin bound.

The original-scan comparisons establish implementation agreement, not
independent validation of a shared traversal. The direct finite inverse,
residual certificates, and symbolic one-entry family provide separate
mathematical checks. None of these finite checks proves the all-length
theorem by enumeration. There is no independent human or formal review.

The exhaustive domain uses lengths 1–3, all real coefficient sequences over
`{-1/2,0,1/2}`, all inputs over `{-1,0,1}`, both orientations, and three grids.
Additional complex cases use the recorded seed 68 and exact rational unit
directions. Long cases use two margins, two grids, and both orientations.
These are fixed validation domains, not an optimization search.

## Sources and scope

[SOURCE.json](SOURCE.json) pins PR628 at
`0768f97d06c623b8211e651543c66135796b62bf`, with construction base
`66849e1475c930fd7732b1a0067ffee7e1e95f60`.
The vendored files match that Git source byte for byte.
`verify.py` executes the unchanged `scan` function AST from `weighted.py`
with its original arithmetic module. It does not execute the unrelated
kernel factorization imports or claim their validation.
The vendored weighted file is an archival source, not a standalone command
inside this reduced package.

PR663's nonlinear restoration audit and PR673's dirty-echo construction and
alias repair address separate questions. Their results are not dependencies
of this clean-array rounding theorem. Existing dirty restoration, arbitrary
stride routing, factor preparation, and full-transform obligations remain.

Joshua Snider's [PR692](https://github.com/CrocSwap/integer-mult-bounds/pull/692),
at `c5b53a5e80372a1fae9830d8dcf21aaabce3f729`, already uses the standard finite
geometric inverse to audit weighted stride cycles and their bilinear dual.
This package does not claim that oracle identity or method as new.
Its distinct result is the uniform sharp rounding bound and execution guard.
The oracle here was written independently; no PR692 code is consumed.

Chafik Boukhalfa's PR628 supplies the scan and its prior proof.
Its predecessor attribution is preserved in [vendor/NOTICE.md](vendor/NOTICE.md).
The shared-factor estimate, matching family, guard derivation, and new
validation code were prepared for Charles Bethin with substantial OpenAI
Codex assistance. No literature-priority claim is made.
New material is Apache-2.0, under the repository license.
