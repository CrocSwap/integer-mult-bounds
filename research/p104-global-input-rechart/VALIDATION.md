# Validation record

Direct local runs on macOS arm64 with CPython 3.12.14:

- `python3.12 -B -u research/p104-global-input-rechart/verify_early.py`: PASS_EXACT_NATIVE_AND_PRICE_ONLY.
- `python3.12 -B -u research/p104-global-input-rechart/verify_native.py --out research/p104-global-input-rechart/NATIVE-RESULT.json`: PASS_GLOBAL_INPUT_RECHART_NATIVE.
- `python3.12 -B -u research/p104-global-input-rechart/verify.py --out research/p104-global-input-rechart/RESULT.json`: PASS_P104_GLOBAL_INPUT_RECHART.

The registered verifier reruns all three stages with isolated Python and
compares every frozen receipt field. It completed with exit code 0 and
`PASS_REGISTERED_RESEARCH_PACKAGE research/p104-global-input-rechart outcome=completed`.
The complete stdout is retained in `REPLAY.txt`. Command:

```sh
python3.12 -B scripts/research_package.py --package research/p104-global-input-rechart
```

The first native attempt stopped on a Python module-name collision when loading
the authenticated predecessor verifier. The loader now isolates the predecessor's
modules and restores our modules afterward. The complete subsequent native run
passed; no scientific condition was relaxed.

The initial draft CI plan failed a pre-existing documentation consistency test:
`docs/ci-verification.md` still identified #6030 while the selected result is
#7000. This PR carries the existing correction from #7113; the targeted
`CurrentCiNavigationTests.test_current_ci_section_matches_selected_record` passed.
Hosted CI acceptance and independent mathematical review are separate from the
local verification results above.
