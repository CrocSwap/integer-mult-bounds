# Executed validation

2026-10-13, macOS arm64, Python 3.14.6, Apple clang 17.0.0, Boost 1.85.0.
Exact research base `f567884aeb8851b6e794af1184119a3bfbe1e631`.
Local execution and eventual GitHub workflow status are separate.

| command / check | executed result |
|---|---|
| `python3 -I -B research/r439-frame524-seed13/search.py --check` | Deterministic nomination matches; fixed-factor minima 12+15 |
| Same search under `-O` | Pass, explicit pin/acceptance checks retained |
| `python3 -I -B research/r439-frame524-seed13/verify.py` | Exact committed certificate matches fresh replay; block 41→27, full ADDs 24305→24277 |
| Verifier under `-O` | Same receipt; acceptance checks retained |
| `factor_check.py --controls` under `-O` | Nine distinct proof-relevant corruptions rejected |
| `BOOST_INCLUDE=../boost_1_85_0 python3 -I -B research/r439-frame524-seed13/native.py --write-certificate` | Unchanged C++ legality and 5/9/11-stage checkers pass on both words; 883/1327/1549 columns, all 96 bridge controls |
| `python3 -I -B research/r439-frame524-seed13/test_package.py` | All seven tests pass, including isolated minimal relocation with spaces, no Git/search module, normal/optimized receipts, corruptions and existing output preservation |
| `make selected-record-check` | Exact selected #799 κ, source inventory and proof supplements pass |
| All 16 `SOURCES.json` entries vs base Git objects | SHA-256 equality |
| Word, wlib, xcheck and nodeopt vs original #589 Git objects | Byte equality; original path `research/e8-bit-p111/` |
| Staged `git diff --check` | Pass; only the research package is added |

The two mathematical implementations agree on every finite-class coverage
field: 4096 subsets and 24576 transitions per factor, feasible transitions
23552/21120, feasible orders 239500800/43908480, optimal orders
39916800/992640. These order counts include empty identity writes.

Full-word evidence covers every dirty-input column, all 636 closed frames,
H1–H5 and the U/J/K/U-inverse conclusions, all 661 unchanged register frame
paths, the nine COPY/ERASE pairs, the full rank invoice and the actual positive
precision envelope. The independently interpreted exported record bytes agree
exactly with the owning exporter. `CERTIFICATE.json` contains the complete
deterministic receipt. `NATIVE-CERTIFICATE.json` retains all non-timing native
fields; `NATIVE-ENVIRONMENT.json` records the toolchain and downloaded header
archive hash. No local binaries or Boost headers are included in the PR.

Word controls reject an omitted forward gate, unchanged old cleanup, invalid
frame descent, substituted dirty-helper donor, omitted copied-total contribution,
and omitted ERASE. Factor controls reject false maps, false minima, false
coverage, premature completion, wrong search domain, destination revisits,
false donor coefficients/order and corrupted reverse matrices. Package tests
independently exercise corrupt source/certificate/metadata bytes and preserve
an existing output file. These are failed tests of deliberate mutations, not
counterexamples to the selected construction or failed mathematical searches.

Verification caught and corrected two integration defects before acceptance:
the factor-minimum field name initially differed between independently written
scripts; integer paid-profile keys initially differed from their JSON round
trip. Both were corrected and ordinary/optimized/minimal replay was rerun.
The arithmetic witness and its reported minima did not change.

No native endpoint checks are weakened, and no global artifact regeneration is
performed. The expensive repository-wide regenerating `make verify`, selected
supplier cold rebuild, hosted-owner/global invoice, outer assembly and Lean
theorem checks were not run for this standalone finite circuit package. Its
paid recursive profile and selected κ are unchanged. All-size/compiler,
common-label/mutable-source realization, whole-call hosting, precision/tape and
analytic obligations remain inherited. Hosted CI is reported after publication;
no independent human peer review is claimed.
