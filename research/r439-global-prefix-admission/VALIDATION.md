# Executed validation

Completed on 2026-10-13. All mathematical and native checks below passed.
Hosted GitHub Actions status is separate from these local results.

- Ordinary isolated CPython **3.14.4**: complete strict-search comparison,
  relaxed search regeneration, independent local checks, all 42 literal
  trial replays, source H1-H5, native legality and 5/9/11-stage checks. The
  initial successful run produced EXPECTED.json through `verify.run`.
- Isolated optimized CPython **3.12.3**, `-I -O -B`: the documented verifier
  CLI repeated the whole computation from a relocated read-only closure
  with exactly the 18 pinned runtime inputs and package files, with output
  outside that tree. No repository checkout, network, Python package,
  unlisted source file or generated cache was needed. The complete resulting
  receipt is byte-identical to EXPECTED.json.
- Seven artifact tests pass under ordinary 3.14.4 and isolated optimized
  3.12.3. They cover complete decoded-payload equality after gzip
  recompression, modified candidates and parents, duplicate JSON keys,
  non-finite JSON, missing sources and source-byte corruption.
- All 18 runtime hashes agree with exact Git objects at research base
  `946293a3dcaa9121ef5f4be44db2e07adb7de085` and refreshed upstream
  `bbc600db2fc15007b7c914f4f2b2ed55fa909c87`.
- `make selected-record-check` passed with PR942's selected rational
  `1661960547713947 / 10^18`. The selected construction is not edited.

Full EXPECTED.json file SHA-256:
`af51d2ca596d09e5d77326b33cb213eb4b97c45a8888c5bc8e819d4e24a2b0ab`.
Reproduction compares every canonical receipt field, not that presentation
hash. Generated gzip container bytes are not equality criteria. Immutable
source inputs retain exact byte pins, as required by CONTRIBUTING.md.

The completed comparison uses 172,800 strict nominations and 172,800 relaxed
nominations. The strict result is zero replacements. The new result prices
42 whole candidate words and admits all 42, with 120 A ADDs saved. Independent
local coverage is 2,688 Boolean inputs and 504 positive column pairs. The
42 literal trial replays cover both orders and all 661 arbitrary-dirt input
columns, executing 1,979,296 literal instructions. Separate complete-word
checks of PR589, PR952 and the final candidate execute another 142,930.

Native tests compile the unmodified pinned sources with **GCC C++ 15.2.0**,
`-O2 -std=c++17`. Boost **1.83** came from Ubuntu
`libboost1.83-dev_1.83.0-5ubuntu5_amd64.deb`, SHA-256
`c17abc5a40a074c3d959655191ebec1561fa25f14f4948f6788be49417d4b234`,
extracted under `/tmp/math-pass09-boost/extracted/usr/include` and selected
by `BOOST_INCLUDE`. Native checks run all three words at 5/9/11 stages,
covering 883/1,327/1,549 formal columns per word and 144 omitted-bridge
controls. Full source and helper restoration, target behavior, literal
cleanup, MOVE paths, ranks, COPY/ERASE lifecycle and exact payload bounds
agree between the source, literal and native implementations.

All 16 local controls reject. In addition to malformed circuits and receipts,
the paired-ADD identity controls retain the Boolean endpoint while creating
precisely measured precision failures: 103/194 bits for local/nine-stage at
320 identity pairs, and 111/207 bits at 1,024 pairs. An initial test fixture
used rapidly growing four-gate identities and jumped over the nine-only
failure region; it was replaced by these two explicit slower-growing
fixtures. No candidate changed during this test-fixture correction.

This is the scoped finite replay described in README.md and PROOF.md. No
full `make verify`, cold selected complex replay or whole-hosted global
controller/invoice run is claimed. No independent human or subagent review
was performed.
