# Validation record

Local environment: macOS arm64, CPython 3.12.14. Source-specific retained
engines and receipts are distinct from independent human/formal acceptance.

- `python3.12 -B -u research/p104-global-output-rechart/verify_early.py`: passed; every frozen early receipt field matched.
- `python3.12 -B -u research/p104-global-output-rechart/verify_native.py --out research/p104-global-output-rechart/NATIVE-RESULT.json`: passed. Exact forward/adjoint, eleven 512-column chart checks (eight new chart pairs), phase controls, integer grid, ingredient caller/price/ordinary/precision, eight corruption controls, native finite physical replay and signed routes all passed.
- `python3.12 -B -u research/p104-global-output-rechart/verify.py --out research/p104-global-output-rechart/RESULT.json`: passed the complete application, including all 3,038 catalogue checks and 104 main boundaries.
- `python3.12 -B scripts/research_package.py --package research/p104-global-output-rechart`: exit code 0, `PASS_REGISTERED_RESEARCH_PACKAGE research/p104-global-output-rechart outcome=completed`. All three stages reran under isolated Python; every frozen early/native/application field matched. Full stdout is REPLAY.txt.

The initial draft was deliberately submitted after exact κ verification and
before full application verification. EARLY-RESULT.json retains that historical
scope. NATIVE-RESULT.json and RESULT.json retain the subsequent complete receipts.

The canonical documentation says #6030 while the selected result is #7000.
This submission carries the existing #7113/#7122 correction to
`docs/ci-verification.md`; the targeted current-CI-navigation test passes.
On #7122 this correction enabled the scientific package's hosted replay to pass,
while an unrelated historical package failed. No hosted result for this new
package or independent scientific admission is inferred from that prior run.

The initial exact-head hosted run 42905094314 failed only the current-CI-navigation
test (760 tests, one failure, 24 skips); scientific replay was skipped. The
documentation correction described above fixes that targeted test. Hosted
status after the final push is separate from this local registered receipt.
