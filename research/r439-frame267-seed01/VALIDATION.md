# Executed validation

Executed 2026-10-13 UTC (2026-10-14 Melbourne) against base
`91a2094f2e022930069e8cfdc810a3ea1b81cd09`. See `VALIDATION.json` for the precise
Python/platform/compiler environment; Boost 1.87.0 headers were used.

- `python3 -I -B research/r439-frame267-seed01/verify.py`: PASS. Both complete
  search certificates, exact matrices, 64 local inputs, 661 arbitrary dirty
  columns, 636 closed frames, unchanged H1-H5, all record bills, the PR904
  overlap comparison, and eight controls pass.
- `BOOST_INCLUDE=/private/tmp/boost_1_87_0 python3 -I -B
  research/r439-frame267-seed01/native.py --output /private/tmp/math-seed01-final-native`:
  PASS. Fresh unchanged legality and 5/9/11-stage checkers on both words;
  883/1,327/1,549 formal columns and 96 omitted-bridge controls. Every saved
  proof-relevant native field agrees. The local candidate is freshly rebuilt.
- `python3 -I -B research/r439-frame267-seed01/test_package.py -v`: all seven
  tests pass, including optimized Python from an offline minimal closure in a
  path with spaces, source/certificate corruption and output preservation. The
  H4 test was then strengthened to call the owning checker on a scalar-valid
  stale cleanup and rerun separately; it passes and detects the H4 violation.
- `make selected-record-check`: PASS at the exact base. All 20 pinned source
  and context files also match their base Git objects; the three execution
  inputs match the actual selected source inventory. No selected source is edited.
- Python syntax checks and Git whitespace checks pass.

## Repository-wide check: incomplete

One `make verify` invocation ran in a disposable exact-base checkout containing
this package. It was stopped at the predeclared **240-second** budget during
`verify-producers -> endpoint-gauge-producer` (h=40). The process group was
terminated and the partial regeneration remains outside the contribution.
`MAKE-VERIFY.json` records the bounded outcome and full-log SHA256. The log is
retained locally at `/private/tmp/math-seed01-required-check/make-verify.log`.

This is **not a full-suite pass**, nor evidence of a mathematical failure.
The broad suite was not repeatedly relaunched. The package's focused local and
native checks above completed. No selected complex cold replay, full changed
hosted-parent invoice, outer assembly, Lean theorem or hosted CI pass is claimed.
The finite contribution is independently reviewable within that stated scope.
