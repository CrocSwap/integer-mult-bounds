# Batch source pins when creating a research draft

`new_research_package.py` previously started two Git processes per source,
in addition to resolving the base and reading its catalogue. The generator
now reuses the existing `research_package.git_blobs` reader. It still compares
every live file with the pinned bytes, records exact blob IDs and SHA256s,
and completes all source checks before creating the draft directory. The
reader is closed on failure and exhausted on success, including its final
process-exit check. No persistent cache is introduced.

The earlier optimizations by woklerx ([#1452](https://github.com/CrocSwap/integer-mult-bounds/pull/1452))
and Arham-Tahir64 ([#1595](https://github.com/CrocSwap/integer-mult-bounds/pull/1595))
covered validation of existing packages. This change applies the retained
reader to draft generation; it does not claim a new batching method.

From a full-history checkout, with Python 3.12 and Git:

```sh
python3.12 -m unittest discover -s tests -p 'test_research_scaffold_batch.py' -v
python3.12 tests/benchmark_research_scaffold.py --pairs 3
```

The benchmark loads the original generator from canonical main
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, creates temporary shared clones,
and uses the 175 paths listed in `research/u8-e4-gap-fill/SOURCES.json` at
that same commit. With the selected record and catalogue, each draft has
177 source pins. Clone setup and fixture preparation are outside the timing.
Execution order alternates; all five generated files must match byte for byte
within each pair. Timings have no pass threshold.

Measured on Windows, CPython 3.12.14, Git 2.53.0.windows.3:

| Pair | Order | Before (seconds) | After (seconds) |
| --- | --- | ---: | ---: |
| 0 | before, after | 17.315766 | 0.825035 |
| 1 | after, before | 16.323979 | 0.301599 |
| 2 | before, after | 14.558922 | 0.278119 |

Every pair used 356 Git processes before and 3 after, with identical draft
bytes. The medians were 16.323979 and 0.301599 seconds. These are measurements
on one busy host (the first pair overlapped the tooling suite), not a promise
of cross-platform speedup or whole-replay improvement. The benchmark prints
all samples, runtime versions, and source hashes for independent repetition.

The focused tests additionally check independently computed blob/SHA pins,
binary/empty/Unicode/spaced filenames, input deduplication, first/last live
input drift and restoration, untracked sources, and a reader failure after
the final row. Failures leave no draft and reap the reader. POSIX newline
filenames are covered when that platform runs the tests; they were not run
on this Windows host. The required research tooling suite passed 68 tests
with three existing Linux-only skips. No mathematical replay was performed.

Task selection: bit-mechanisms seed `93ced3f5e7c1825e5b6ca72a228fc968`, scope
changed to a measured contributor-tooling delay after source-bound orientation
and overlap review. Prepared by ywz65 with substantial OpenAI Codex assistance.
Credit Douglas Colkitt and the retained generator/reader contributors. Apache-2.0.
