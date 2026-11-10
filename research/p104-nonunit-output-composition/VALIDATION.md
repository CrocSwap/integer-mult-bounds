# Validation record

Direct local CPython 3.12.14 runs:

- `python3.12 -B -u research/p104-nonunit-output-composition/verify_early.py`: passed; every frozen early receipt field matched.
- `python3.12 -B -u research/p104-nonunit-output-composition/verify_native.py --out research/p104-nonunit-output-composition/NATIVE-RESULT.json`: passed. Exact source/candidate reconstruction, forward/adjoint, eleven 512-column chart checks, phase, eight corruption controls, rational/integer grid agreement, separate ingredient invoice/ordinary/precision and finite native/signed routes passed.
- `python3.12 -B -u research/p104-nonunit-output-composition/verify.py --out research/p104-nonunit-output-composition/RESULT.json`: passed the complete application, including all 3,038 catalogue checks, 104 main boundaries and the increased precision context 2362.
- `python3.12 -B scripts/research_package.py --package research/p104-nonunit-output-composition`: exit code 0, `PASS_REGISTERED_RESEARCH_PACKAGE research/p104-nonunit-output-composition outcome=completed`. All three stages reran under isolated Python and matched every frozen early/native/application receipt field. Full stdout is REPLAY.txt.

The source-pinned fractional height is 25. The independent rational derivation
and integer forward replay agree on height and scaled maximum mass. Exact
one-occurrence adapters carry this height into the integer forward scale and
trailing-bit measurement, the ingredient precision and the complete caller
precision path. The insufficient-height control rejects F24. No divisibility
check is disabled; frozen sources are unchanged. The integration follows and
credits dillona/OpenAI Codex's PR7130 precision adapters.

The initial draft was published after the narrower exact price/native checks;
EARLY-RESULT.json preserves that historical boundary. Complete receipts are
recorded separately when those checks finish.

The current-CI-navigation test passes with the existing #7113/#7122/#7124
correction to docs/ci-verification.md, replacing obsolete selected #6030 with
#7000. No hosted scientific result for this new package is inferred from prior
passing packages. Five inherited assumptions and independent review remain.

The initial hosted run 42912441613 failed the known guide6030/selected7000
current-CI-navigation test (760 tests, one failure, 24 skips); scientific replay
was skipped. The existing documentation correction fixes that targeted test.
Hosted status after the final push remains separate from these local receipts.
