# Local validation receipt — 2026-10-14

Base: `2de86c77b4127d2f01f504e0c7c5e4db737caa3c`. Assignment seed: 93.
All changes are confined to `research/bit-frame-closure-basis/`.
`upstream/`, the selected record, frozen words and predecessor code are unchanged.

## Exact execution and controls

- Python 3.12.12: complete paired reference/basis replay passes for PR589,
  PR555 and degraded PR589. Every one of the 6,477 returned closure entries and
  all three complete reports agree. The unchanged enumeration visits 1,156
  assignments; the degraded fixture recovers the tuned word's paid profile.
- The registered package runner and exact Git/SHA source metadata check pass.
  The ninth control group binds the benchmark to its code, case coverage,
  receipts and summary arithmetic. No mathematical kernel changed after timing.
- All nine current control groups pass under an optimized Python 3.12 parent.
  The adapter rejects optimized direct execution and compiles the inherited
  checker with assertions enabled; its ordinary child runs use `-I -B`.
- A minimal source export containing only this package and the five consumed
  inputs passes the complete paired replay and all nine groups under Python
  3.14.6. Every exported file was mode 0444 and every directory mode 0555. The
  command ran from `/private/tmp`, outside the export, with `-I -O -B` on the
  parent verifier and inherited `PYTHONOPTIMIZE=2`. Its children still had
  assertions enabled. No Git metadata or precomputed cache was required for
  this direct `verify.py` replay; the registered metadata command separately
  needs the pinned Git history.
- `make selected-record-check` passes for the unchanged conditional
  `836330098538459/500000000000000000` record. This is a source-binding check,
  not the selected construction's cold replay.

The exact rational oracle checks 1,100 bounded cases. Controls detect wrong
membership and rank, unsafe modular aliasing, malformed inputs, cross-word
cache misuse, five changed input files, missing/duplicate inventory entries,
missing/duplicate adapter anchors, optimized inherited execution, and stale or
incomplete benchmark evidence. The new code uses explicit failure checks.

## Same-input benchmark

Five alternating pairs, each engine running the identical three-case suite in
fresh interpreters. macOS 26.5.2 arm64, CPython 3.12.12; normal OS caching.

| Workload | Reference median seconds | Basis median seconds |
| --- | ---: | ---: |
| PR589 | 10.70300 | 2.03097 |
| PR555 | 10.76556 | 1.84596 |
| Degraded PR589 | 11.14466 | 2.03038 |
| Complete three-case suite | **32.61348** | **5.90754** |

Ratio of suite medians: **5.52066x**. The suite median is computed from complete
pair totals, not by summing per-case medians. Reference totals range from
30.93507 to 50.12656 seconds; basis totals range from 5.70348 to 9.40149 seconds.
All samples, including the slower fourth and fifth pairs on the shared host,
are retained in `BENCHMARK.json`. No samples were discarded. Each timed result
matches the same full receipt and closure inventory hash. Its code, source
manifest and expected-result hashes are checked by the package verifier.
There is no timing-based acceptance test.

## Coordination and handoff boundary

The final overlap snapshot at 05:45 UTC paginated 536 open PRs and 310
Discussion records, with no warnings. Exact checker-path and closure-related
searches found no duplicate PR886 adapter in the inspected records. PR933 and
PR1345 remain distinct transport-search work; PR1459/1461 concern different
rational-frame containment checkers. These searches do not inspect every code
diff and are not a novelty proof.

Current-main compatibility was checked at
`a18b4b0136d647529971e9fcb99fa83f5b9a0b81`: all five consumed Git blobs and the
selected-record blob are identical to the pinned base. The package retains its
original base and historical provenance instead of moving those pins.

The contribution is ready for independent review as verification tooling.
No selected-frontier cold replay, native/physical supplier admission, Lean
build, full historical suite or multiplication theorem is claimed. Hosted CI
and publication are external handoff state, not established by this receipt.
