# Recorded validation

2026-10-13, Linux x86-64. CPython 3.14.4 normal and a separately relocated,
read-only source closure under `/usr/bin/python3.12` 3.12.3 with `-I -O -B`.
Both complete runs rebuild the metric and unchanged native checks using GCC
15.2.0 and Boost 1.83 headers. Original exporters run with assertions enabled
even when the parent verifier uses `-O`.

The complete canonical receipts agree:

```text
651157b0fecd64d805ef3b871435b2891ebce14a1118af55d35cd42a41b987f0
```

The committed [EXPECTED.json](EXPECTED.json) is compared in full on every
ordinary replay. The complete decoded candidate hash is
`b381d9bc18820b89f92485826ff9f8449d0f72f7599772d52c14e07d6b89b7f2`.
The raw metric hashes are in CERTIFICATE.json. Paths, compiler commands,
scratch files and timings are outside the deterministic receipt.

Coverage: 9,999,360 metric vertices, 199,987,200 directed edges, 1,203 complete
windows, 38,496 Boolean input cases, 59 full positive admission trials, two
661-column full words in both directions, and two native words at 5/9/11 stages
on 883/1,327/1,549 columns. All 96 omitted-bridge controls reject. The 20 local
controls include missing A and D preparation/restoration, missing replacement
operations, stale but F2-valid cleanup, omitted copy/erase, invalid frames,
strict precision equalities, overlapping intervals, missing census entries,
false shortest lengths, corrupt/truncated full tables, and a deliberately
non-shortest predecessor tree whose edge inequalities must fail.

Ten package tests pass under optimized Python, including recompressed candidate
and census acceptance, corrupted candidates, duplicate windows/JSON keys,
nonfinite JSON, exaggerated interval savings, omitted admission trials and a
corrupted executable source rejected before import. Fourteen repository
selected-record/finite-bit-contract tests also pass. Every vendored Git blob
and all 15 base source hashes are checked; there are 21 source pins total.

The first standalone metric run took 0.59 seconds / 108,348 KiB peak RSS for BFS
and 0.29 seconds / 69,180 KiB for the independent check on this host. These are
single-run engineering observations, not benchmarks or multiplication speedups.

The read-only run uses only pinned base inputs and this package. Scratch tables,
compiled binaries, native records, and receipts are outside that closure. No
historical global `make verify` or selected hosted cold replay was run: neither
the selected construction nor its sources are modified. Hosted PR CI status is
reported separately at submission; local success does not assert hosted success.

All general compiler/algorithmic, hosting, analytic and precision/tape
obligations remain, including the inherited semantic-D H2/K exception. The
bounded optimality statement is restricted exactly as in PROOF.md.
