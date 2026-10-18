# Scoped tool-assisted review

Prepared for woklerx with substantial OpenAI Codex assistance, October 13,
2026. Apache-2.0. This is a second-agent review within the same AI-assisted
session, not independent human peer review or a formal proof certificate.

The review covered the archived common-subset family, its exact certificate,
the assembly-domain note, the balanced interfaces, and this package's
`verify.py`, `SOURCES.json`, `RESULT.json` and `README.md`. It did not review
unrelated constructions or replay the selected multiplication witness.

## Mathematical checks

Before inspecting the new verifier, the reviewing agent independently
reconstructed all 626 finite cases, including 301 positive deficits, with a
separate standard-library calculation. Prime powers were recognized by
factorization; no historical arithmetic module was imported. Logarithms
used the positive expansion `log(x)=sum((1-1/x)^j/j)` after binary range
reduction, with 80 terms and an exact geometric remainder. This differs
from the historical atanh expansion. The new verifier subsequently uses
the same positive-series idea with 96 terms, so these should not be counted
as two unrelated numerical algorithms.

Exact interval comparison identified the unique maximum of the optimistic
envelope at `(q,h)=(3,29)`, with `eta=237/599335286`. Approximate values are:

| Quantity | Value |
| --- | ---: |
| Bit envelope `A` | `3.91449860718828694e-8` |
| Historical `A/5` | `7.82899721437657388e-9` |
| Balanced `A/(1+A)` | `3.91449845395529948e-8` |
| Runner-up bit envelope, `(3,30)` | `3.89325964606213694e-8` |
| Family tail upper bound at `h=65` | `2.07691161587764289e-8` |

Thus the old conversion excludes `2^-26`; the balanced transferred ceiling
excludes `2^-24`, but does not exclude `2^-25` or `2^-26`. An upper envelope
above a target does not establish an attainable saving.

The Lucas support identity, full-rank incidence argument, implication
`Delta>0 => h>=3q`, and reconstruction of the partial-output pair from its
support are sound within the fixed family and cancellation-free compiler.
For the infinite tail, `M>=3` implies `eta<1/(14h^3)`, hence
`A(q,h)<1/((14h^3-1)log(h^3))`. Both positive denominator factors increase
for `h>=65`, and the bound at 65 lies below the finite maximum's lower
enclosure. Every `q>=33` has `h>=65`, so no prime powers or sizes are omitted.

The older factor-4 tail genuinely exceeds `2^-24`, even after the balanced
conversion. The tests prove this using its lower enclosure, avoiding any
inference merely from a loose upper bound. The factor-14 family tail closes
this gap.

## Scope and implementation review

The transfer remains conditional on an admitted balanced assembly receiving
an effective bit saving `a<=A` from this family. The paid shared interface
checks an actual uniform supplier and bridge. Its separately completed
supplier is not supplied by this package. The two-margin rational diagnostic
does not validate all assembly constraints or establish bridge admission.
The README states these limitations and makes no new-kappa claim.

The verifier reconstructs every archived finite row, preserves type-sensitive
receipt comparison, rejects duplicate JSON keys, checks a complete source
inventory with SHA-256 and Git-blob hashes, and uses explicit exceptions
rather than assertions for its acceptance conditions. The source files are
read but not executed. The exact receipt matched the recalculation.

Two review suggestions were incorporated: clarifying the archived `c+q`
scope-string typo as the `c+u` role ledger, and checking the factor-4 tail gap
with a lower as well as an upper logarithm enclosure. No unresolved
mathematical or implementation defect was found within this scope.

## Focused failure controls

`test_verify.py` checks logarithm anchors and input domains; prime-power
coverage and receipt equality; both conversions and the reduced diagnostic;
the old tail gap and sufficient new tail; omitted, reordered and corrupted
archived cases; source inventory omission and extension; missing and drifted
source bytes; Git-blob disagreement; historical dependency omission;
duplicate JSON keys; Boolean/integer receipt corruption; and output-file
preservation on rejection. It also exercises both a successful verifier run
and rejection of a corrupt receipt in a fresh `python -O` process.

Run from the repository root:

```sh
python -I -S -B research/prime-subset-assembly-scope/test_verify.py -v
```

Review run: all **14 tests passed** in 1.767 seconds on Python 3.14. The
default verifier also passed with 626 cases and eight built-in controls.

The tests create temporary directories inside this package and remove them
after checking that their resolved paths remain inside the package. This
avoids relying on a writable global temporary directory. The suite is a
focused verifier regression, not a supplier, circuit, bridge or theorem test.
