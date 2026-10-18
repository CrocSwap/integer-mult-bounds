# Validation

Completed locally on 2026-10-13, Linux x86_64
(`Linux-7.0.0-38-generic-x86_64-with-glibc2.43`). Base and refreshed upstream
main: `dadfea6e8a78ff6ba901705f87532a71c6f5bbb8`.

| Command | Environment | Result |
| --- | --- | --- |
| `python3 -B scripts/research_baseline.py` | CPython 3.14.4 | PASS_RESEARCH_BASELINE_BINDINGS_ONLY; orientation, not supplier replay |
| `/usr/bin/python3.12 scripts/research_package.py --package research/complex-signed-prefix-audit` | CPython 3.12.3 | All four registered commands pass; six package tests pass |
| `python3 -I -O -B research/complex-signed-prefix-audit/verify.py` | CPython 3.14.4 | PASS_COMPLEX_SIGNED_PREFIX_AUDIT; identical receipt |
| `python3 -I -O -B research/complex-signed-prefix-audit/controls.py` | CPython 3.14.4 | PASS_SIGNED_PREFIX_CONTROLS; identical receipt |
| `python3 -I -B research/complex-signed-prefix-audit/source_check.py` | CPython 3.14.4 | Original driver passes both orientations and all 25 controls; entire receipt identical |
| `make selected-record-check` | CPython 3.14.4 | Selected record/source inventory/κ guard passes |

The registered Python 3.12 command runs `verify.py`, `controls.py`,
`source_check.py`, and `test_package.py`. The last command runs six tests,
including minimal read-only relocation with spaces in its path, isolated
optimized Python, exact dyadic cancellation, strict-power boundaries,
source mutation, a removed mandatory input pin, and a one-unit understatement
of the backward peak. No repository checkout or network is needed for that
relocated verifier; registration's historical metadata validation uses Git.
The source driver runs with `-I` and without `-O` even when its caller uses
optimized mode, so every original assertion remains enabled.

Portable SHA256 receipts, over sorted compact JSON:

- Signed prefix: `17c82644f920abd7b9a776481efec1740f0ae75b99c53bf331e3e1442d328300`.
- Controls: `415845cdd798be4ee121c3d7f873b1c6e30c73c1e424bb07bd655d0aac728c65`.
- Complete original local receipt: `510c6ec28beb87ee4c854a6bd492c7de8155b815d306e770245b49a074ac4774`.

All 39,386 scalar prefixes agree between sparse rational and dense integer
engines. Separate reverse functional checks and numerical primitive replays
attain each maximum. The numerical primitive counts equal the archived
198766/198814 real-component counts. Frame examples check 57,024 exact
matrix entries at 2,376 cuts; eight selected-word/bound controls reject the
specified weakened checks. Four mathematical boundary examples are recorded.

During development, the phase report was corrected to include unchanged
live rows at each phase entry, and the partial-store projection bound was
made explicit before the final receipts were generated. The initial package
metadata check rejected a structured `evidence` field; it was corrected to
the schema's text field before the successful registered replay. Neither
issue changes a predecessor artifact or the selected construction.

[OVERLAP.json](OVERLAP.json) records the refreshed complete remote pagination:
868 open PRs and 30 Discussions at 21:39 UTC, including bodies/comments. The
nearest five earlier heads remain unchanged. PR1263 changes scalar gauges;
PR1277 audits ancestry binding; PR1278 bounds a different dirty recursive
word. No duplicate signed-prefix result was found in the inspected scope.
This is coordination evidence, not a novelty certificate.

Not run: full native/Clifford/provider cold replay, whole global controller
or owner replay, physical compiler realization, roundoff/tape/exact-recovery
proofs, analytic assembly, Lean, or repository-wide historical suites. The
original local checker is run fully; its source assumptions do not become a
complete multiplication proof. Hosted PR CI is a separate status and is
reported at publication rather than inferred from these local passes.

Published as [PR1282](https://github.com/CrocSwap/integer-mult-bounds/pull/1282).
The mathematical package commit is `a7e3e61cd709ccbc22b3e938853e01f838048e72`;
the follow-up changes publication metadata only. Staged whitespace and local
documentation-link checks pass.
