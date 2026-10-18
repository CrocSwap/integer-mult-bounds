# Concurrent scheduling for the isolated test runner (verification engineering)

Track 85–94 (verification engineering), assignment seed 88. Base commit
`f567884aeb8851b6e794af1184119a3bfbe1e631`. Prepared with help from opencode.
No new kappa claim; this is a tooling improvement only.

## What changed

`scripts/run_isolated_tests.py` (run by `make verify-tests`, hence by
`make verify`) ran each test module in a fresh interpreter, sequentially. A
timing survey of the `make verify` checks on the base commit found this
runner to be by far the most expensive single check: it exceeded a 250 s
sweep budget and measured 298.5 s end to end, while every other individual
check surveyed was at most 144 s (`scripts/audit_quadratic_affine.py`),
most below 10 s.

The runner now schedules the same per-module commands concurrently, one
isolated interpreter per module, and replays each module's captured
stdout/stderr bytes in sorted module order. The point of the original
design — one fresh interpreter per test module, so research packages with
colliding module names (`verify`, `skip_graph`, `data_recovery`, ...) cannot
bind each other's imports — is unchanged: process isolation is exactly what
makes the modules independent and safely concurrent. A test-module audit
found no writes outside `tempfile.TemporaryDirectory()` blocks (see
"Exactness" below), so concurrent modules share no mutable state.

A `--workers N` flag pins the concurrency width (default: CPU count). With
no arguments the command line, the per-module commands, the summary lines
and the exit behavior are those of the pre-change runner.

## Measured result (same host, same input)

| Run | Modules | Wall time |
|---|---|---|
| Pre-change runner, base commit, end to end | 87 (its test file not yet added) | 298.5 s |
| Benchmark sequential pass (pre-change schedule, captured) | 88 | 250.6 s |
| Benchmark concurrent pass (`run_modules`, 16 workers) | 88 | 75.9 s (3.30x) |
| Post-change runner end to end | 88 | 76.7 s (3.9x vs. the base run) |

The sequential baseline differs from the shipped old script only in pipe
capture; commands and ordering are identical. The end-to-end comparison
covers 87 vs. 88 modules because `tests/test_isolated_test_runner.py` is
part of this change; the extra module accounts for roughly a second on
either side. Host: 16 logical CPUs, CPython 3.13.15 on Windows; the
speedup is bounded by the slowest single module (tail effect), so it scales
with core count up to that floor.

## Exactness

The change alters scheduling only. Per module, the command is
byte-identical to the pre-change one:

    python -m unittest discover -s <tests> -p <module> -v

with the same interpreter, working directory and environment. The runner
replays each module's captured bytes in sorted module order, so the
combined stdout and stderr streams equal a sequential run module for
module.

Equivalence is machine-checked by `benchmark.py`: it runs every module with
the pre-change sequential schedule and again with the concurrent scheduler,
then compares per-module exit codes and stdout/stderr SHA-256. Measured on
88 modules:

- exit codes: identical for all 88; the failing-module sets of the two
  schedules are equal (the same 15 modules fail in both);
- stdout: byte-identical for all 88;
- stderr: byte-identical for 87 after normalizing the wall-clock field
  `unittest -v` embeds in its `Ran N tests in T.TTTs` line (raw stderr
  differs in every module for exactly that field);
- `test_frontier799_bindings.py` is inherently nondeterministic across any
  two runs: its failing traceback embeds a machine-random temporary
  directory path (`...\Temp\tmpXXXX\ancestor\bit`). The benchmark proves
  this automatically by re-running any mismatched module twice under the
  same schedule; `scheduling_driven_mismatches` is empty.

Coverage is unchanged: the same glob (`tests/test*.py`), the same command
per module, and every module's exit code still contributes to the shared
`Failed modules: ...` failure summary and the
`PASS all N test modules in isolated interpreters` success line.

## Negative controls

`tests/test_isolated_test_runner.py` runs the real runner end to end in a
sandbox (a copied runner plus a tiny `tests/` directory):

1. Two passing and one deliberately failing module: every module runs and
   the failure is reported in the shared summary (failure detection intact).
2. A barrier test: three modules each write a marker and then wait (8 s)
   for three markers to exist. They only all pass if at least three module
   processes run concurrently. Against the pre-change runner this test
   fails with "barrier timeout: test modules did not run concurrently"; it
   passes with `--workers 3` after the change.
3. Default-invocation compatibility: unchanged summary lines and exit
   code 1 on failure.

The benchmark itself is a negative control on exactness: any exit-code or
scheduling-driven receipt change makes it fail.

## Reproduce

    python3 -B research/agent-07-verifeng-seed88/benchmark.py --workers 4 --output /tmp/fresh-test-benchmark.json

Expected final line (numbers above it may vary with core count):

    PASS identical exit codes (88 modules); receipts identical for 87 modules modulo the unittest timing field; 1 module(s) inherently nondeterministic across same-mode runs: ['test_frontier799_bindings.py']

    python3 -B scripts/run_isolated_tests.py

Expected on a host with the full Unix test surface: per-module
`Checking ...` lines and `PASS all 88 test modules in isolated interpreters`.
Measured on this Windows host: exit 1 with the pre-existing 15-module
failing set (`Failed modules: ...`), 88 `Checking` lines, 76.7 s; the same
set fails at the base commit.

## Scope and inherited obligations

- The 15 failing test modules on this Windows host are environmental and
  present identically before and after this change (for example
  `ModuleNotFoundError: No module named 'resource'`, a Unix-only
  standard-library module, in the `copied_*` tests). This package does not
  fix Windows portability of the test suite; the claim is that the
  concurrent runner reproduces the sequential runner's per-module receipts,
  exit codes and failing set exactly.
- This changes no mathematical content: no certificate, patch, generator,
  proof supplement or pinned source file is touched.
  `run_isolated_tests.py` is not hash-pinned by
  `certificates/selected-result.json`,
  `research/community-frontier799-audit/SELECTED-SOURCE.json` or any
  checkpoint record.
- Unresolved: live interleaved output during a run is replaced by
  per-module replay when each module finishes (still in sorted order). A
  hung module stalls the printed stream where a sequential run would, but
  earlier finished modules wait for their turn to print.

## Attribution

Written with help from opencode. The runner's original design and the
test-suite content are repository predecessors; this package only changes
scheduling and adds evidence. Related concurrent work on other targets
includes PR #853 (concurrent pinned stages for the #741 replay); this
result does not touch or depend on it.

## Maintainer integration correction

The submitted benchmark compared same-mode reruns using raw timing hashes, so
elapsed-time differences could misclassify a real receipt mismatch as inherent
nondeterminism. The integrated benchmark uses timing-normalized same-mode checks
and rejects every remaining cross-schedule mismatch, including nondeterministic
ones. It requires a fresh `--output` path and supports `--workers`; the submitted
Windows evidence remains a historical measurement, not fresh validation. The
runner buffers all module results before printing them in order. Thus no live
per-module progress is promised during the run.
