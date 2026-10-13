# Validation receipt

Validated 2026-10-14 Australia/Melbourne (2026-10-13 UTC), macOS 26.5.2,
arm64, Python 3.14.6. Original experimental base:
`91a2094f2e022930069e8cfdc810a3ea1b81cd09`. Refreshed submission base:
`47481c89fd30a43f8f882eb4b391e89c29273fd0`.

```
python3 -I -B research/signed-connector-obstruction/verify.py
python3 -I -O -B research/signed-connector-obstruction/verify.py
python3 -I -O -B research/signed-connector-obstruction/test_package.py
make selected-record-check
python3 -B -m unittest discover -s tests -p 'test_selected_result.py' -v
```

Normal and optimized verifier stdout is byte-identical. The two timed replays
took 1.264 and 1.096 seconds respectively; these are environment observations,
not a before/after performance claim. The exact reproducible receipt is
[EXPECTED.json](EXPECTED.json).

- All 720 support-minimum source paths are independently reconstructed. All
  19,683 signed matrices have complete free-operator and inverse checks.
- Exactly 19,395 attain the support bound; the other 288 are the full signed
  permutation orbit of the canonical matrix and have 14-query witnesses.
  All 512 unsigned matrices attain their support bound over characteristic zero.
- The literal 308-leaf program and both star comparators (388/676) have complete
  free noncommutative product, source, dirty-workspace and inverse checks.
- 330 dense cases cover basis columns and arbitrary dirty values, exact
  integers, rationals and arithmetic modulo 3 and 5. Modular cases check the
  word identity, not the characteristic-zero minimum theorem.
- 22 mathematical controls exercise omitted calls, wrong signs, invalid or
  underpriced words, a wrong recursive factor, aliasing, changing sources, and
  the distinct nonlinear readout failure. All have the expected outcome.
- 15 dense tape trace/formula comparisons cover L=1..5 on identical factor and
  role layouts for all three schedules. Coefficient/source/target accesses,
  arithmetic, accumulator resets, head returns, storage and instructions are
  retained in the exact receipt. Scalar/control and bit-width costs are stated
  separately in the note.
- The standalone package passes in a temporary path containing spaces, outside
  the checkout. Default verification leaves every byte unchanged. Generator
  replay produces a byte-identical certificate. Nine package corruptions
  reject, including missing coverage, unpaid leaves/scratch, source drift and
  receipt drift: `PASS_SIGNED_CONNECTOR_PACKAGE relocation=1 regeneration=1
  corruptions=9`.
- Each of the four retained source files agrees with its SHA256 and locally
  reconstructed Git blob. GitHub's pinned contents API independently returned
  the same four blob identities. The predecessor heads remained unchanged at
  the prepublication refresh.
- `make selected-record-check` and all five selected-result unit tests pass.
  They passed first on the original #799 record, and again on the refreshed
  #890 record `1661957774647029/1000000000000000000`. Existing tracked files,
  selected certificates and upstream are unchanged relative to refreshed main.

Only this standalone research package is added. The global `make verify`
regeneration and selected-supplier cold replay are not rerun; no changed
supplier, assembly or existing generator depends on this package. No full
repository suite, Linux execution, hosted CI, proof-assistant verification or
independent human/delegated-agent review is claimed. The mathematical scope is
the explicitly restricted query alphabet, not the full multiplication theorem.
