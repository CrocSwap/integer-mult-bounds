# Executed validation

Validated on 2026-10-13, Linux x86-64, Python **3.12.3** and **3.14.4**,
against base `f567884aeb8851b6e794af1184119a3bfbe1e631` and the exact source
pins in [SOURCES.json](SOURCES.json). The selected #799 record remains
unchanged at κ = `1661634653669567/10^18`.

## Exact replay and separate arithmetic implementation

These commands passed from the repository root:

```sh
/usr/bin/python3.12 -B -I -S research/dyadic-fractional-grid/verify.py
/usr/bin/python3.14 -B -I -O research/dyadic-fractional-grid/verify.py
/usr/bin/python3.12 -B -I -S research/dyadic-fractional-grid/crosscheck.py
/usr/bin/python3.14 -B -I -O research/dyadic-fractional-grid/crosscheck.py
/usr/bin/python3.12 -B -I -S research/dyadic-fractional-grid/test_grid.py
/usr/bin/python3.14 -B -I -O research/dyadic-fractional-grid/test_grid.py
make selected-record-check
```

The primary verifier recomputed [EXPECTED.json](EXPECTED.json) exactly:

```text
PASS_DYADIC_FRACTIONAL_GRID programs=6 coefficients=962 extra_grid_coefficients=18 kappa=unchanged
```

The sparse `Fraction` interpreter, which does not use the integer-row engine,
agreed on every target-row denominator depth, their complete stream digests,
maxima, primitive counts and endpoints:

```text
PASS_FRACTION_GRID_CROSSCHECK complete_traces=12 scalar_primitives=1016110
```

Coverage includes:

- All six scalar programs, both forward-only and bidirectional lowering.
- All 716+9 CK/JP8 or 728+9 SW4 arbitrary native/private input columns.
- All 962 coefficients and 3,842 candidate circuits, including non-winners.
- Twelve sharpness witnesses, each checked separately using one-column
  `Fraction` evaluation at its recorded primitive address.
- Eighteen local counterexamples, with 24 insufficient-guard executions,
  their exact original controls and their sufficient-guard repairs.
- The complete CK forward integer-grid witness at three and four bits,
  the exact forward-only control at three bits, and the repaired circuit
  at five bits. This confirms actual endpoint errors, beyond the separate
  theorem about intermediate representability.
- Original event inventory and paid profiles, every macro boundary,
  final native maps, and complete erasure of arbitrary private inputs.

Nine tests passed on each Python version. They cover the `31/8` example,
negative directed rounding, zero/cancellation normalization, signed and
unreduced raw denominators, source preservation, missing copy/halving/clear
operations, every recorded witness at one bit below its bound, and a wrong
witness address. Production checks use explicit exceptions, so `-O` does
not disable them.

## Minimal package and adverse controls

The primary verifier also passed under Python 3.12.3 with `-B -I -S -O`
from a separate checkout whose path contains spaces. It contained only
this package, the files listed in `SOURCES.json`, and the source archive;
there was no Git metadata or third-party Python dependency.

The following six packaging controls were run against that disposable copy:

| Change | Observed result |
|---|---|
| Append a comment to the vendored #837 lowering | Rejected: source pin mismatch |
| Change CK forward's recorded guard from 5 to 3 | Rejected: certificate mismatch |
| Alter the recorded odd numerator of its sharpness witness | Rejected: certificate mismatch |
| Change a consumed program payload while keeping valid JSON | Rejected: source pin mismatch |
| Request `--write` to an existing receipt | Rejected before replay; existing bytes preserved |
| Recompress all four direct gzip inputs and both consumed archive members, reorder the members, alter tar/gzip metadata and retain only consumed members | Accepted with identical full mathematical receipt |

Each changed input was restored after its control. The last check establishes
that container bytes are provenance, not a substitute for comparison of the
consumed proof payloads. The verifier separately rejects ambiguous duplicate
archive members.

## Limits

These checks establish the finite **scalar projection** claim described in
[README.md](README.md). Frame changes, phases and recursive calls are not
evaluated as physical numerical operators. The fixed-grid model has an
unbounded integer part, and this result does not certify an overflow budget,
floating-point stability, coefficient preparation, all-size precision or
tape costs. Fractional guard bits are not total register width.

The two arithmetic implementations share source bindings and the frozen
#837 circuits as proof objects. Both were written by the same AI assistant;
different representations do not constitute independent human review.
No compiler, selected construction, κ or `upstream/` content was changed.
