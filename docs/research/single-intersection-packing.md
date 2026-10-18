# Exact packed Gram replay

This verification tooling contribution targets `minor_rows` in
`scripts/experiments/single_intersection.py`. It changes neither the historical
single-intersection search domain nor the selected multiplication bound.

The matrix entry is `C[S,T] = [S == T or popcount(S & T) == j]` over F2.
Distinct labels make every diagonal entry one. The intersection relation is
symmetric, so one exact popcount determines both off-diagonal entries.
Byte buffers store bit `b` at byte `b // 8`, bit `b % 8`; little-endian integer
conversion preserves the packed-row convention consumed by binary elimination.
The final partial byte has zero padding. Every matrix entry is retained.

The baseline at commit `66849e1475c930fd7732b1a0067ffee7e1e95f60` builds each
row by summing shifted arbitrary-precision integers. Profiling all 5,257 cases
and four committed orbit witnesses took 39.151 seconds, with 30.878 seconds
inside `minor_rows` (profiling overhead included). This motivated switching
from the initial feature-construction hypothesis to matrix packing. No rank,
feature-basis independence, transposition-closure, or input rejection check
is removed. No persistent cache is introduced.

The contribution is by merramil with substantial OpenAI Codex assistance,
under Apache-2.0. It builds on Douglas R. Colkitt's preserved historical
single-intersection audit (`d55bcd62ceb8f322bcf311a5a66e94c3ac7724f0`) and
retains that audit's mathematical scope and attribution. Assignment seed 86
selected verification engineering; the three candidates were gather schedules,
coded-carry controls, and single-intersection replay (86 modulo 3 selects the
last). The initial open-PR snapshot had 582 entries and no title claiming this
engine. The only open issue was #650, so the scope was claimed locally.

## Verification contract

Tests compare complete packed rows with the predecessor's directed formula,
including permutations, negative controls, and byte-boundary sizes. The bounded
benchmark compares every entry of all four committed orbit Gram matrices
and the complete audit output. Only the changed implementation's source hash
may differ from the committed certificate. Existing malformed orbit witnesses
still fail, including with Python optimization enabled.

The full matrices remain quadratic in space and time. This is an implementation
speedup for finite verification, not a new construction, rank theorem, expanded
search, or proof of the conditional multiplication theorem.

## Reproduce and measured result

From the repository root, using standard-library Python 3.11 or newer on
macOS or Linux:

```sh
python3 -B research/single-intersection-packing/benchmark.py --rounds 3 --output /tmp/single-intersection-packing.json
```

Use a fresh output path. Expected final status:
`PASS_IDENTICAL_GRAM_ROWS_AND_COMPLETE_CERTIFICATES`. Timing is descriptive,
not a pass threshold. The benchmark imports the preserved, hash-pinned complete
predecessor module, compares all 100,203,737 Gram entries, then runs three
alternating baseline/packed pairs in fresh, sequential interpreters. Each
worker recomputes the complete 5,257-case certificate, including feature-basis
independence, every adjacent-image closure check, exact Gram ranks, and all
other controls. Its full serialized output must have the original certificate
SHA256 after restoring exactly the implementation-source binding. The matrix
comparison happens outside the timing workers; it does not warm their caches.

[RESULT.json](../../research/single-intersection-packing/RESULT.json) records
every sample and source pin. On CPython 3.13.1 / macOS arm64, median full-audit
time was **13.766 to 6.597 seconds (2.087x faster)**. This trades memory for
speed: median process peak RSS increased from **49,266,688 to 68,845,568 bytes**
(about 40%). In-place buffer conversion avoids explicitly retaining two full
matrix lists, but Python allocator behavior still raises observed peak RSS.
These timings cover this historical finite audit, not supplier cold replay
or integer multiplication runtime.

Run the focused tests with:

```sh
python3 -B -m unittest discover -s tests -p 'test_single_intersection*.py' -v
python3 -B -O -m unittest discover -s tests -p 'test_single_intersection*.py' -v
```

The 16 tests include changed-source, changed-rank, changed-screen-row,
changed-other-source-binding, and wrong-matrix-entry rejection controls.
Only two generated certificate bindings change: `single-intersection.json`
and `affine-vector-screens.json`. Tests reconstruct and hash each complete
predecessor certificate after restoring that one binding. No selected-frontier
artifact or `upstream/` source changes.

The complete `make verify-tests` run passed **557 tests in 86 isolated
interpreters and 20 patch-application checks**. Both affected certificate
producers, selected-record integrity, and `git diff --check` passed.
[VALIDATION.json](../../research/single-intersection-packing/VALIDATION.json)
records the exact commands and scope. The broad `make verify-research` target
would regenerate unrelated certificates, so only its two affected producers
were rerun. Full `make verify`, selected-supplier cold replay, Lean builds, and
remote Linux CI are outside this local validation.

The final pre-submission overlap refresh covered 594 open PRs through #775;
none claimed this single-intersection packing change.
