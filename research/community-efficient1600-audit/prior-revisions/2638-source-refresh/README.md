# Opt-in gate tables for the packed selected-record checker

The independent PR1781 packed-integer checker rebuilds a 512-entry permutation
or phase table inside every gate application. This package integrates Charles
Bethin's existing PR662 table recurrences at that boundary, preserving the full
checker and its exact legacy result and receipt bytes. The frozen checker and
selected inputs are never edited. This is an opt-in replay tool, not a new table
algorithm, certificate, selected exponent or multiplication theorem.

The full audit passed all 2,896 child records and 224 endpoint adapters on all
512 columns, including global phase, source bindings, calibration and the
predecessor's 12 semantic control groups. It additionally compared every entry
of all 5,140 distinct permutation tables and 3,721 distinct phase tables used
by that complete run against the original scalar formulas: **4,536,832 exact
comparisons**. Both caches retain at most 64 immutable tables and cache no
state, operator result or acceptance decision.

## Measured effect

Four serial fresh CPython 3.12.7 processes ran the same source-authenticated
fixture in baseline/candidate/candidate/baseline order. Each starts empty
caches, creates the same private source snapshot, and executes the complete
unchanged `verify.py.main`. The baseline executes the original kernel bytes;
the candidate applies exactly the three edits in `adapter.EDITS`.

| Run | Mode | Whole process wall seconds | Checker CPU seconds |
|---|---|---:|---:|
| 0 | baseline | 68.905 | 67.156 |
| 1 | candidate | 31.266 | 29.891 |
| 2 | candidate | 31.677 | 30.313 |
| 3 | baseline | 84.857 | 78.891 |

The median wall times are 76.881 and 31.471 seconds: a **2.44x descriptive
ratio on this shared Windows host**. These four observations are not a
statistical estimate or a platform-independent guarantee. No correctness test
requires a speed ratio. `BENCHMARK.json` retains each run, source hashes, full
stdout, timing fields and runtime identity; `benchmark.py` reproduces the
serial comparison. Profiling identified repeated scalar P/D evaluation as the
bottleneck, but profiler timings are not used in this ratio.

All four runs reproduce legacy receipt SHA-256
`aaf7b41d99e9e5d4123f230ca5d22478a396f8a5c822e51d35e527d750084f34`.
The full legacy result SHA-256 remains
`bcf51c3fa67e29c64b74d2e9944c727d33b1d60518ec55de4f77f5cc6dc8cf25`.

## Exact integration and source boundary

`SOURCES.json` pins 14 runtime inputs at canonical main
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. Before compiling any predecessor
source, the adapter captures and authenticates all 14 byte strings. It writes
those captured bytes to a private temporary repository-shaped snapshot and
executes from that snapshot. No `.pyc` is read, no Git checkout is required at
runtime, and the source snapshot is checked unchanged after the replay.

The adapter compiles only the two function definitions `permutation_table`
and `phase_table` from the authenticated PR662 source through Python's AST.
It does not execute or import that file's `zero_state` implementation. The
packed checker's original scalar formulas remain intact for independent
entry-by-entry audit. There is now deliberately shared table arithmetic with
PR662; the original checker author's wholly separate kernel implementation
claim should not be attributed to this adapter. Its calibration and
no-producer-module guard still execute, and no producer lowering/evaluator or
producer acceptance result is used.

The source transformation has exactly three uniquely checked anchors:

1. Replace P's scalar table comprehension with a call using the gate's row
   tuple and dimension.
2. Compute D's phase table once before its 512-element loop.
3. Read D's phase from that table; PH retains its original expression.

The changed kernel SHA-256 is
`68f1f2305772c4be946351d4a20a90845d9a61b7c01f86531383113441f7aa67`.
All packed arithmetic, C/X/PH behavior, radix guards, P bijection checks,
comparisons, coverage loops and calibration code are otherwise unchanged.
`PROOF.md` explains the finite gate equivalence and complete-cache keys.

**Receipt interpretation:** the unchanged predecessor receipt header hashes
its original on-disk kernel source. It is retained for exact legacy comparison,
not presented as the identity of the transformed executed kernel. Every new
adapter run emits a companion record with `executed_kernel_sha256`, adapter
hash, source inventory and an explicit header limitation. Consumers identifying
the optimized execution must keep that companion record; the legacy receipt
alone does not identify this adapter.

## Reproduce

From the repository root, with standard-library Python 3.12 or later:

```sh
python -I -O -B research/packed-clifford-gate-tables/verify.py
python -I -O -B -m unittest discover -s research/packed-clifford-gate-tables -p test_package.py
python -I -O -B research/packed-clifford-gate-tables/test_export.py
python -B scripts/research_package.py --package research/packed-clifford-gate-tables
```

The primary command runs the full checker plus exhaustive actual-table audit.
For an ordinary optimized replay without that extra audit:

```sh
python -I -B research/packed-clifford-gate-tables/adapter.py --out NEW-companion.json --receipts NEW-receipts.jsonl
python -I -B research/packed-clifford-gate-tables/benchmark.py --out-dir NEW-benchmark-directory
```

Outputs must be new paths. `--write` and subset execution are not exposed.
The benchmark is an optional measurement command, not part of the registered
correctness hook. On this Windows sandbox the author set process-local
`TEMP` and `TMP` to a writable workspace directory; ordinary Python temporary
directory behavior is otherwise unchanged.

Eight control groups cover all 14 source corruptions before compilation,
loading only the two credited functions, mutable gate contents and fresh
outputs, bounded eviction/recomputation, a false permutation and false phase
rejected by the unchanged calibration, original gate rejection boundaries,
and reversibility/uniqueness of the exact source edits. A separate export test
runs the full package without Git, checks unchanged input bytes and rejects
an existing output path. Explicit failures remain active under `-O`.

## Scope and attribution

Sagar Thakrar (`thakrarsagar`) authored the independent packed checker in
[PR1781](https://github.com/CrocSwap/integer-mult-bounds/pull/1781), retained
from head `dafbaadeb423b3bc80fbf6fcd6f415400dc0ffbf`. Its original source,
semantics, controls and all predecessor credits remain in that package.
Charles Bethin (`cbethin`) supplied the table recurrences in
[PR662](https://github.com/CrocSwap/integer-mult-bounds/pull/662), head
`458744109003e0958798f27c1f04be78f03663ce`. The later
[PR2329](https://github.com/CrocSwap/integer-mult-bounds/pull/2329), head
`68a7161a610f175dc8e7b22f95acd033191450d9`, already integrates them into the
production `clifford_exact.zero_state` path. This contribution adapts them to
the independent packed all-column kernel with a source snapshot and explicit
executed-kernel receipt, rather than claiming either predecessor's algorithm.

This adapter accepts the valid nine-axis integer gate domain used by the pinned
checker; it deliberately refuses malformed rows and Z4 coefficients before
calling the table builders. It is not a general replacement for arbitrary
historical kernels. It does not close the executor bridge, residual wrapper,
recursive supplier or all-size multiplication obligations. No frozen source,
selected record, production interpreter or default command is changed.

## Open next questions

1. Should the maintained checker expose an explicit table-backend interface?
   That would remove the exact-source adapter's three text anchors. First
   review this narrow adapter and then design the interface with the original
   author; a changed source needs fresh binding and replay.
2. Does the improvement persist on another interpreter/platform? Re-run the
   same alternating full-checker benchmark with all source/receipt hashes
   preserved. The current four shared-host observations do not answer that.

Prepared by ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
