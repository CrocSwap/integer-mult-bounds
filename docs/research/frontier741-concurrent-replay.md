# Concurrent bit/complex replay of the #589 + #741 ancestry

Status: **tooling improvement**. It changes no construction, bound, certificate or
selected record, and claims no new kappa.

## What changed

`scripts/verify_frontier741.py` (the cold ancestry replay that `verify_frontier799.py`
runs, and hence the selected `make frontier1042-verify` chain) runs `bit589` to
completion and then `complex741`. Neither reads anything the
other writes: `bit589` writes only under `<work>/bit`, `complex741` only under
`<work>/complex`, and the binding step needs both. The new
`scripts/verify_frontier741_concurrent.py` runs the same two commands at the same
time, then the same binding script.

`verify_frontier741.py` is untouched because its sha256 is pinned in
`certificates/selected-result.json` and the checkpoint certificates. The new driver
is a sibling that writes the same layout (`bit/`, `complex/`, `bit589.log`,
`complex741.log`, `STEPS.json`, `RESULT.json`) plus a `CONCURRENCY.json` with wall and
summed job times. If either supplier fails, the other is stopped (process group
SIGTERM, then SIGKILL after 20 s), the failing log is named, and nothing is bound.
`--complex-jobs N` (N>1) swaps in the existing dependency-scheduled complex replay
(`verify_complex741_parallel.py`, #853); the default of 1 runs `verify.py` unchanged so
that this change is measured on its own.

## Reproduce

```sh
python3 -B scripts/verify_frontier741_concurrent.py --work /absolute/fresh/dir
python3 -B scripts/verify_replay_coverage.py --frontier 741 --work /absolute/fresh/dir
python3 -m unittest tests.test_frontier741_concurrent
```

Expected: the first prints `PASS selected finite composition; inherited hypotheses
remain`, and `RESULT.json` has status `PASS_REBUILT_PR589_PR741_COMPOSITION`, kappa
`1661202643272239/1000000000000000000`. The second prints
`PASS_COMPLETE_PR741_REPLAY_COVERAGE`. The tests (8) take about 3 s.

Developed and measured at base commit `2921874911956718fcaaaf9396fe8267b3cfa9f0`.
The branch is rebased onto `ba82555c` (main when submitted); `verify_frontier741.py`,
its pinned hash, the bindings script and both supplier packages are unchanged between
the two, and the tests were re-run on the rebased tree. Benchmark environment (not the
CI image): WSL2 Ubuntu 24.04, 28 logical CPUs, 7 GB RAM; Python 3.12.15, numpy 2.5.4,
scipy 1.18.1, sympy 1.14.0; the C++17 checkers built with `zig c++` (ziglang 0.17.0,
clang 22.1.8) against Boost 1.86.0 headers. No system compiler was available.

## Measurement

Same checkout, same fresh output path each time, one run at a time on an otherwise idle
machine. The first row used different checkout/output paths and is timing only.

| Driver | Wall seconds | bit589 | complex741 |
| --- | --- | --- | --- |
| original, sequential | 608 | 138 | 469 |
| original, sequential | 599 | – | – |
| original, sequential | 562 | – | – |
| concurrent | 495 | 141 | 495 |
| concurrent | 479 | – | – |
| concurrent, `--complex-jobs 3` | 293 | 150 | 293 |

Sequential mean 590 s, concurrent mean 487 s: about 17% less wall time, 100 to 120 s
saved. The concurrent run is bounded below by `complex741` (critical path 469 to 495 s),
so the bit supplier is hidden but nothing else is. With `--complex-jobs 3` the complex
chain shortens to the dependency chain of #853 and the bit supplier is again fully
hidden: 293 s, about 50% less than sequential (one sample). That is 3 sequential, 2
concurrent and 1 combined samples on one machine; treat the ratios as indicative, not
as precise speedups. #853 alone would leave `bit589` (about 140 s) in series with the
complex replay; that exact configuration was not run here.

## Coverage is unchanged

* `tests/test_frontier741_concurrent.py` parses `verify_frontier741.py` and requires the
  concurrent driver's `bit589`, `complex741` and `bindings` commands, stage order and
  environment scrub (`PYTHONOPTIMIZE`, `WITNESS_DISCOVER`, `WITNESS_RECORD`, `SW4_PIN`)
  to equal the original's. If the original changes, the test fails.
* Output trees of the original and concurrent drivers (same path) were compared file by
  file: 385 common files, 101 differ. A second original run differs from the first in
  exactly the same 101 files, so the concurrent schedule adds no new difference. After
  removing `seconds`/`elapsed` fields and SHA-256 values (digests of files that embed
  timings), every differing JSON file is identical in both comparisons. The remaining
  differing files are logs.
* The concurrent output passes `verify_replay_coverage.py --frontier 741` and the
  original bindings check.
* Negative controls on a copy of the concurrent output: a changed `bit_lower_decimal`
  fails the bindings check (`Rebuilt bit differs`); one extra byte appended to
  `complex/global-replay/ASSEMBLY.json` fails coverage (`Required ancestry artifact hash
  differs`); a deleted `bit/xcheck.json` fails.
* Mutation controls on the tests: replacing the bit verifier, adding `-O` to the complex
  command, removing `SW4_PIN` from the scrub, not stopping the sibling after a failure,
  and waiting for each job right after launching it are each caught. (The `SW4_PIN`
  mutation first survived; the test now sets the variable before checking the scrub.)

## Scope and open items

* Finite replay tooling only. It is not a formal proof, and every inherited assumption
  listed in `certificates/selected-result.json` remains.
* The output is accepted as an ancestor by the coverage and bindings checks, so it can
  be passed as `--ancestor` to `verify_frontier799.py`. That was run once (WSL, default
  concurrent mode, base `2921874`; the 799 scripts are unchanged on later main):
  `verify_frontier799.py --work W --ancestor <output>` passed in 203 s with
  `PASS_REBUILT_PR589_PR799_COMPOSITION`, kappa `1661634653669567/10^18`, and
  `verify_replay_coverage.py --frontier 799 --ancestor <output>` printed
  `PASS_COMPLETE_PR799_REPLAY_COVERAGE`. It records the ancestor as reused
  (`reused_ancestry: true`), as for any externally produced ancestor. Nothing here
  changes what `make frontier1042-verify` (or `frontier942-verify`) runs.
* End to end, cold `frontier1042` on the rebased PR tree (WSL, same checkout, one run
  each, one after the other): the original `verify_frontier1042.py` took **1560 s**
  (`baseline799-cold` 788 s, its own stages 772 s). The new path (concurrent driver 467 s,
  then `verify_frontier799.py --ancestor` 189 s, then
  `verify_frontier1042.py --baseline799` 756 s, with the ancestor moved to
  `<baseline799>/ancestor` as that script expects) took **1412 s**, 148 s or 9.5% less.
  Both ended in `PASS_COMPLETE_PR1042_COMPOSITION` with kappa
  `0.001672188119205421`; the new path records `reused_completed_baseline: true`. About
  132 s of the saving is the 741 part (788 s to 656 s); the rest is run-to-run noise in
  1042's own stages (chain 479 s vs 464 s). Single runs, so about +/-2% should be
  assumed. The #942 replay was not run with it.
* Overlap check at submission: #853 (merged) schedules stages inside `complex741` only and
  does not overlap the bit supplier; no open or merged PR found by search touches
  `verify_frontier741.py` or overlaps `bit589` with `complex741`. The two are
  complementary: with `--complex-jobs 3` the complex chain hides `bit589` entirely (table
  above).
* `--complex-jobs 3` was run cold once (293 s). Its output has the same 385 files as the
  sequential tree and passes `verify_replay_coverage.py --frontier 741`. Against the
  sequential tree it differs in the 101 noise files plus `complex741.log`, whose 45
  lines differ only in the order of `RUN`/`PASS` progress messages; every differing JSON
  file is identical after masking `seconds` and SHA-256 values.
* The `u8-native` stage (about 254 s) and the cold #799 `native` stage (about 393 s)
  dominate the remaining serial time and were not examined.
* Peak memory with both suppliers running was not measured; the 7 GB benchmark machine
  completed it.
* Linux CI was not run; the benchmark used the environment above.

## Credit and disclosure

Builds on the pinned `verify_frontier741.py` driver, `verify_frontier741_bindings.py`
(Douglas Colkitt, with OpenAI Codex assistance), the
dependency-scheduled complex replay of #853 (Aaron / navinor), and the `--jobs` pattern
of `verify_frontier596.py`. Track: verification engineering, assignment seed 90, base
commit above. Substantial AI assistance (Claude, in Cursor) in analysis, code, tests
and this note. Contributor: James Reed (@rcfc-jreed).
