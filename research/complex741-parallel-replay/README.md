# Concurrent replay of the selected #741 complex supplier

Tooling only. No κ, construction, predicate or pinned file changes. `make frontier741-verify`
is unchanged and remains the reference replay.

The complex half of `make frontier741-verify` runs the 22 stages of
`research/complex-sw4-frame8/verify.py` one after another (874 s of the 1158 s cold replay in
the c290b7b receipt). Many stages are independent: the fresh PR558 ancestor replay (the
slowest stage) shares nothing with the gauge44 → p6n → SW4 → frames construction chain, and
three of the control stages read only the final word. This package runs them concurrently.

```sh
make complex741-parallel-verify
# or
python3 -B scripts/verify_complex741_parallel.py --work /fresh/dir/outside/repo [--jobs N]
```

Expected result: the same stage log lines as `verify.py` (in completion order), then
`PASS 0.001661202643272239`, and `RESULT.json`/`RECEIPT.json` in the work directory.

## What the driver does

`scripts/verify_complex741_parallel.py` executes the pinned `verify.py` itself, statement by
statement, after checking its SHA-256 (`7706065e…`, the value in the package `MANIFEST.json`):

- The prelude runs unchanged: package manifest check, vendored source pins, work-directory
  checks and environment.
- Each `run(...)` call is recorded. A worker thread later calls `verify.py`'s own `run`
  function with the same arguments once the stage's prerequisites in `STAGE_DEPS` have
  passed, so the command line, environment, `run_portable.py` wrapper, log file and failure
  handling are the original code. Only its progress write of `STAGES.json` is redirected, so
  that the file stays in `verify.py`'s stage order.
- Assignments that only combine paths (`W=…`, `L=…`) run immediately. Every statement that
  reads stage output runs unchanged and in its original order after all stages pass: the
  ancestral linkage loop, all count assertions, `RESULT.json` and `RECEIPT.json`.
- The first failing stage stops new launches; running stages finish and the error from
  `verify.py`'s `run` (with its log tail) is raised.

The driver refuses a changed `verify.py` and a stage list that differs from `STAGE_DEPS`.

## Why the order change is safe

`STAGE_DEPS` makes each stage wait for every stage whose output path appears in its command
line. The five stages that share the `local/` directory, and the stages after them, stay in
program order. The table was then checked against a recorded trace.

`record_access.py --record DIR` runs the unchanged sequential `verify.py` in a throwaway venv
whose interpreter installs a Python audit hook (through a `.pth` file, so it also loads in
the `-I` child processes). The hook logs every file open (read or write), directory listing,
rename, delete and mkdir. The reducer assigns each process to the stage whose top-level
command most recently started (stages run one at a time) and writes
[`ACCESS.json`](ACCESS.json): per-stage paths relative to the work directory. It was
recorded twice on the same machine (once with a development copy of the hook, once with
`record_access.py --record`); the per-stage access sets and temp-write counts were identical.
From the recorded run (83 processes):

- No stage writes outside the work directory except into fresh `tempfile` directories in the
  system temp directory (unique names created exclusively; 555 such writes in six stages).
- `conflicts()` finds no pair of stages, unordered in `STAGE_DEPS`, where one writes a path
  the other reads, writes or lists, or creates a directory the other lists.
- Deferring the ancestral linkage loop is checked the same way: its reads under
  `work/ancestral558/` and its write of `ANCESTRAL-LINK.json` conflict with no later stage.
- The trace would allow more overlap (for example, `all-native-phase-edges` reads only the
  output of `all728-columns-native`). The table keeps the argument-derived edges because
  audit hooks do not see `os.stat`/existence checks; the saving would be about 10 s.

`tests/test_complex741_parallel.py` checks the scheduler (ordering, overlap, failure
propagation), the stage table and commands against `verify.py`, the SHA-256 refusal, the
conflict rule on `ACCESS.json`, and a negative control: dropping the
`inherited-cold-controls` edge produces a reported conflict.

## Equivalence and benchmark

Three full replays on one machine, base `7ee02b7`, each started in the same absolute work
directory after the previous one was renamed away, so that embedded paths agree
([`EVIDENCE.json`](EVIDENCE.json) has per-stage seconds):

| Replay | Result | Total (RESULT.json `seconds`) |
|---|---|---:|
| sequential `verify.py` | PASS κ = 1661202643272239/10^18 | 594.7 s |
| this driver, `--jobs 8` (default) | PASS, same κ | 386.4 s (1.54×) |
| this driver, `--jobs 3` | PASS, same κ | 347.7 s (1.71×) |

One run each on a host that was not isolated; the timings are descriptive. The parallel time
is the length of the dependency chain gauge44 → notri56 → layered66 → p6n → promotions →
SW4 → frames → `local/` stages → `all-native-phase-edges` → global admission, which makes up
386 s of stage time in the `--jobs 8` run. More workers cannot shorten it; only faster stage
code could. Applying the same chain to the Linux stage times in the c290b7b receipt gives
457 s of the 874 s complex replay. That is an estimate, not a measurement.

`compare_replays.py A B` compares every file of two work trees (304 here):

| Comparison | Byte-identical | JSON: timing or such digests only | Logs: elapsed time or such digests only | Other |
|---|---:|---:|---:|---:|
| sequential vs `--jobs 8` | 233 | 50 | 21 | 0 |
| sequential vs `--jobs 3` | 235 | 49 | 20 | 0 |
| `--jobs 8` vs `--jobs 3` | 233 | 50 | 21 | 0 |

The rules are strict. A JSON difference is accepted only under a `seconds`/`elapsed_seconds`
key, or when both values are SHA-256 digests of the same relative file in the two trees and
that file is itself accepted (iterated to a fixed point; this covers `log_sha256`,
`template_sha256`, receipts and the `CLIFFORD-REVIEW.json` chain). Logs must have the same
number of lines; text and integers must agree, decimal floats (elapsed times) may differ,
and 64-hex tokens only as digests of accepted files. Masking floats in logs is a real
relaxation: a float printed only in a log would not be compared. The JSON outputs, which
hold κ, counts, rejected-control lists and words, are compared without masking, and all
generated words (`*.json.gz`) are byte-identical.

Negative control: in a copy of the `--jobs 8` tree, changing the last digit of κ in
`global-replay/ASSEMBLY.json` and one integer in `notri56/cold44.log`
(`FULL_INVERSE 14826` → `14827`) gives exactly those two rejections.

For reproduction on another machine, run `make complex741-parallel-verify`, then compare its
work directory with a `verify.py` replay made at the same path.

## Scope and limits

- Measured on one Windows 11 machine (16 logical CPUs, 31 GB, CPython 3.12.14). Linux CI
  was not run for this change. The traced and untraced sequential replays also passed on
  this machine, which is itself a portability data point for the package.
- The trace covers file access made through Python, which is all of this package (standard
  library only, no compiled helpers). It does not record `stat`-style queries; the
  argument-derived edges and the output comparison cover that gap.
- A trace and a comparison are evidence for this pinned `verify.py`, not a proof for future
  versions. The SHA-256 pin forces the table to be re-derived (`record_access.py`) when the
  package changes.
- The bit supplier replay (`research/e8-bit-p111-tuned/tune/verify.sh`, 284 s, needs a
  C++17 compiler and Boost) is not covered and could not be run here. Running it beside this
  driver would hide most of its time; that is left to someone who can test it.
- Finite replay does not prove the multiplication theorem; the selected record's inherited
  assumptions are unchanged.

## Attribution

The replayed package is chafreaky's #741 (`research/complex-sw4-frame8`) with the
contributors credited in its `PROVENANCE.md`. eumemic's #154 proposed concurrent execution
for the `make verify` groups; this applies the idea inside the selected complex replay, with
a recorded access trace in place of a manual audit. Prepared by navinor (Aaron Wang) with
substantial AI assistance (Claude) in design, code, measurement and prose.
