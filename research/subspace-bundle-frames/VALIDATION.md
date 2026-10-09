# PR readiness validation

Local audit date: 2026-10-10. Base repository commit:
`3b6b66891c0ac888521cf591fe306c6286601d4f`.
PR195 seed commit: `d3e6b83af33c3aad940e737776937706e25b0b19`.

## Completed witness checks

- Independently replayed PR195's full verifier before using its frozen seed.
- Replayed this package's default verifier in a clean base checkout containing
  only this added package, under Python 3.13. No `local-investigation` directory
  was present. The saved certificate matched exactly without `--write`.
- Verified changed physical frames, 46 terminal sinks, all formal columns under
  both signs, exact interval moments, 47 assembly inequalities and seven margins.
- Rebuilt all eight candidate gzip files byte-for-byte in the clean checkout.
  Independently rebuilt the pinned PR195 seed candidate byte-for-byte as well.
- Passed `check_moves.py` under Python 3.13 and 3.14: 300 exhaustive tiny
  closure comparisons, 2536 feasible edge states and 1056 source restrictions.
- Passed `check_report.py`: exact exponent comparisons, all 468 frame changes,
  seed hash and frozen candidate agreement.
- Confirmed optimized Python rejects verification rather than skipping asserts.
- Passed `make entrance-bank-verify`, including the selected-result pins,
  immutable parent source closure and the bank scheduling supplement.
- Completed an independent review of the final package. No blockers remained;
  predecessor attribution, retained assumptions and AI assistance are explicit.

## Repository regression and patch checks

All targets in the sequential `make verify` recipe passed. The initial run
stopped at `skip-suffix-producer` because Apple's default C++ compiler rejects
`-fopenmp`. The suffix target and every remaining group were then completed
sequentially with Homebrew GCC 15:

    CXX=/opt/homebrew/bin/g++-15 make skip-suffix-verify verify-clones verify-positive verify-joint verify-pair verify-tests

This covers all 16 top-level verification groups, including 538 isolated tests
across 82 modules and all 20 historical patch application checks. No test or
certificate failure remained. All 2183 tracked baseline files were compared
after regeneration; none changed.

The historical positive-frame C++ check required Boost multiprecision headers.
Official Boost 1.86.0 headers were extracted into the audit directory and exposed
through an untracked include symlink in the isolated checkout. The release
archive's SHA256 matched the official metadata:
`1bed88e40401b2cb7a1f76d4bab499e352fa4d0c5f31c0dbae64e24d34d7513b`.
No compiler adjustment or Boost file belongs to this submission.

The final patch contains 26 new files: this package and its CI workflow.
Git applicability and strict whitespace checks passed. Applying the patch in
an isolated directory reproduced all included files byte-for-byte. The original
selected result, `upstream/`, and all tracked baseline sources remain unchanged.

## Limits

Local runs used macOS and Python 3.13/3.14. The supplied Ubuntu CI matrix uses
Python 3.11/3.14; hosted CI has not run because no PR has been published.
The optional floating-point discovery search is not a certification step.
These finite checks retain the parent's conditional all-size assumptions;
they do not formally verify the complete integer-multiplication theorem.
