# Local validation

Research base: `680967accfd4311f3241dc154e1f434869747b43` (current main when
the session started). New work is confined to this package. The selected
record, upstream inputs and frozen predecessor packages are unchanged.

On Windows, CPython **3.12.14** (bundled runtime), these final-scope commands passed:

```sh
python3.12 -I -B scripts/research_package.py --package research/ut3-two-targets-any-registers
```

The registered hook runs the isolated optimized verifier, then all four tests.
It reports `PASS_UT3_ANY_REGISTERS ... minimum=4w ... controls=48`, four passing
tests, and `PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=negative-result`.
The counts in `EXPECTED.json` include the expanded nilpotent alphabet.

An additional **CPython 3.14.6** isolated optimized replay passed:

```sh
python3.14 -I -O -B research/ut3-two-targets-any-registers/verify.py
```

Tests make a temporary minimal source export in a path containing spaces.
The export's optimized replay leaves every source/receipt byte unchanged.
Three actual receipt corruptions (boolean replacing integer schema, omitted
fixture and an underpriced fixture) and actual source drift all reject,
without overwriting the evidence. The tests also check 324 two-factor words
over the expanded paid alphabet, including noncommuting scalar couplings.

The first test attempt failed because this Windows execution sandbox denied
its default temporary directory. Setting `TEMP` and `TMP` to an existing
directory inside the authorized workspace resolved that environment problem.
No verifier or proof change was made to bypass it. The final registered replay
used that environment; the temporary exports were cleaned up by the tests.

Independent predecessor check: PR1573 at
`0b8c5a69297c794f2de22c04494c83e41300ae36` was exported into a separate directory
with its `README.md`, `verify.py`, `independent.py` and `CERTIFICATE.json`.
Its command `python3.12 -I -O -B verify.py` passed as
`PASS_UT3_ALL_REGISTERS`. Exact canonical source Git blobs and SHA256 hashes are
in `SOURCES.json`; this package imports none of that code. The shared theorem
is credited as corroboration, and the submission removes scalar idempotence.

The prescribed source-bound `scripts/research_baseline.py` orientation passed.
`scripts/verify_selected_result.py` passed for the full selected source
inventory, exact kappa and proof supplements. `git diff --cached --check`
passed. The metadata/provenance checks run as part of the registered replay.

Not run or established: selected-supplier cold circuit replay, hosted CI,
physical/compiler/common-label admission, ownership/hosting, precision/tape,
outer analytic transfer, Lean formalization or independent human proof review.
The arbitrary-register theorem is the written rank proof, not an extrapolation
from these finite checks. No new kappa is claimed.
