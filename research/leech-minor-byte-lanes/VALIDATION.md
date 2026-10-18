# Validation receipt

2026-10-13, Linux x86_64, CPython 3.12.14. Base:
`f567884aeb8851b6e794af1184119a3bfbe1e631`. All consumed predecessor files
are pinned in `PINS.json`; all benchmarked implementation hashes are recorded
in `BENCHMARK.json`.

## Exact comparison and controls

- Full differential replay: **5,927 rows / 7,531,037 entries**, all five Leech
  fixtures, all equal. Both complete nine-screen certificates are byte-identical
  to `certificates/affine-vector-screens.json`; `EXPECTED.json` retains the
  per-case row hashes and geometry source hashes.
- `python3 -I -B research/leech-minor-byte-lanes/test_lanes.py -v`:
  **11 test groups pass**, including the **three unchanged predecessor tests
  in each of the two modes**. The retained run took 9.884 seconds; this test
  runtime is not an accelerator benchmark.
- Literal integer oracles compare every entry for 81 small vectors at 65
  shifts (426,465 comparisons), and 192 signed Leech vectors at seven shifts
  (258,048 comparisons). They include all three vector families, mandatory
  diagonals, extremal byte values and assignment seed 86.
- Controls detect sign/shift errors, missing diagonals, column permutation
  despite equal rank, dependent rows, zero-output kernels, malformed lane
  domains, changed source/fixture/certificate/rank-helper bytes, missing input,
  missing case or changed count in the expected receipt, disabled assertions
  and reused output paths. They do not authenticate arbitrary hostile runtime
  modifications or prove the full multiplication theorem.
- Selected-record integrity passes with kappa
  `1661634653669567/1000000000000000000`; all **five** tests in
  `tests/test_selected_result.py` pass.

## Timing

The final command was:

```sh
python3 -I -B research/leech-minor-byte-lanes/benchmark.py --rounds 3 --output /tmp/seed86-benchmark-final.json
```

The resulting file is retained as `BENCHMARK.json`. The process order was
baseline/lanes, lanes/baseline, baseline/lanes. No other test or benchmark from
this task ran concurrently during this final comparison. System-wide resource
contention on the shared runner was not controlled.

| Pair | Baseline seconds | Byte-lane seconds |
| ---: | ---: | ---: |
| 1 | 17.051406 | 8.988220 |
| 2 | 18.946560 | 7.536546 |
| 3 | 22.677771 | 14.988176 |
| Median | **18.946560** | **8.988220** |

Ratio of medians: **2.107932×**. Each process replays the same full nine-screen
audit, including the unchanged four polynomial-code screens, source admission,
all original checks, complete certificate comparison and writing the result.
The parent compares each file again. All six certificates are identical.
This is not a whole-repository or selected-supplier runtime claim. The sample
variation is retained; timing is never an acceptance threshold.

An earlier profile and exploratory three-pair run are excluded. The profile
added instrumentation overhead; the exploratory run overlapped supplemental
tests. No favorable subset of the final samples was selected.

## Portability and limits

The minimal dependency closure (41 pinned predecessor files plus this package
and repository license/notices) was copied to a fresh directory whose path
contains spaces. The complete differential verifier was invoked with `-I -B`
from `/tmp`, outside the checkout. It passed, and every copied input byte and
the file inventory remained unchanged. The relocation log is retained in
`validation/relocation.log`.

Original sources, default entry points, the selected frontier and `upstream/`
are unchanged. This optional adapter has no Makefile or CI activation. Full
`make verify`, cold selected-supplier replay, Lean and hosted CI were not run
or claimed. The relevant local checks above cover the new package; they do
not establish inherited all-size or analytic hypotheses.
