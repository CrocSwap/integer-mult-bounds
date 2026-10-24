# Executed checks and limits

Executed on macOS arm64 with standard-library CPython 3.12.8
(`/opt/local/bin/python3.12`) and CPython 3.14.5 (`python3`). No third-party
dependencies, Lean, Docker or hosted workflows were launched.

* Ten shared-CLI tests pass in normal and optimized modes on both versions.
  The tests include 625 exact signed histogram comparisons against a separate
  discrete-slope tariff enumeration and the changed-contract/input controls.
* Direct source-bound package replay passes normal and optimized modes on both
  versions, with identical committed RESULT.json. The registered Python 3.12
  runner passes both commands and all metadata/source pins.
* Two additional Codex agents critically reviewed the signed-order proof,
  interval formulas/global cover, source reconstruction and scope. They found
  no blocking defect. This is AI review, not independent human/kernel acceptance.
* Committed-byte checks pass, including the unchanged CRLF invoice export.
  The official 21-file export at `ff9137e2a103654d9fa8f3f950c7a0f8afa4a79b`
  passes transport integrity and optimized scientific replay with an empty PATH
  in a read-only extracted directory. Later edits only add/clarify documentation;
  the final publication export is checked separately.
* Direct ancestry from canonical base
  `1ec1119972c9aefe42525172d07b332fcff81cb4` to the contribution passes.
  The optional `--check-source-history` preflight was attempted but cannot run
  because this checkout is shallow. Full-history verification is not claimed.
  All consumed scientific exports, including the pending witness, are committed
  package-local; no foreign Git object is needed for scientific replay.

The exact reusable commands are in VERIFY.json and README.md. The full selected
cold replay, physical/native phase lowering, complete compiler execution, tape/
precision implementation, BIT supplier and inherited analytic foundations are
outside this contribution. No source profile or selected record is changed.
