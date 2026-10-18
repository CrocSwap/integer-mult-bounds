# Exact sparse U8 phase compilation

This optional compiler propagates only nonzero Gaussian amplitudes. It
reuses PR662's exact gate tables. It preserves the complete phase recipes
for the U8 word used by the selected PR942 construction.

The full input has 1,005 frames, 2,949 directed edges, and 224 endpoint
adapters. The benchmark compares every recipe byte and every review field
except elapsed seconds. The accepted recipe SHA256 is
`4629507dcbdd516457c001ff8f9dbe750d1a0cbfa5cfa3c6be003d45804ba0c5`.

No accepted source or certificate changes. The default cold replay is
unchanged. This is an optional verification speed improvement, not a new
construction, new kappa, or measured multiplication speedup.

## Reproduce

Use Python 3.11 or later. There are no third-party Python dependencies.
From the repository root, use a new output file:

```sh
python3 -B research/selected-replay-fastpath/benchmark.py --pairs 3 --out /tmp/u8-phase-benchmark.json
```

Expected: `PASS_COMPLETE_U8_PHASE_RECIPES_IDENTICAL`.
The command extracts the complete canonical word from the pinned PR942
archive. It runs the original `phases_full.py`, the PR662 dense evaluator,
and the sparse evaluator in separate processes. It alternates the order
between rounds. It checks the committed recipe bytes after every run.
Timing has no pass threshold. The memory measurement uses POSIX `wait4` on
macOS or Linux. The temporary files belong to the command and are removed
when it exits.

Run the exact state and negative controls with:

```sh
python3 -B research/selected-replay-fastpath/test_package.py
```

For a fresh canonical word from a separate native replay:

```sh
python3 -B research/selected-replay-fastpath/run.py \
  --word /path/to/native/local/CANONICAL-WORD.json.gz \
  --out /tmp/new-u8-phases
```

Use a new output directory. `--engine dense` selects the unchanged PR662
state evaluator. `--engine reference` selects the retained original lowering
routine. The default is `sparse`. Source pins are checked in all three modes.
This command compiles the local word. It does not check its parent supplier
or install its output into a selected replay.

## Method

The dense evaluator visits all `2^n` amplitudes for every gate. Many states
in phase lowering have much smaller support. The sparse evaluator stores
only nonzero amplitudes. A `C` gate visits each XOR pair once and removes
exact cancellations. It keeps the same power-of-two normalization and
returns the complete dense vector for the compiler's equality checks.

The compiler still checks all frame spans, ranks, tableaux, denominators and
global phases. `lowering.py` passes its evaluator through normal function
arguments. It does not patch a retained method or rebind retained globals.
See [PROOF.md](PROOF.md) for the gate induction and work/storage bounds.

## Evidence and limits

Base: `8bddbee377e2f3ce1f1247196c4b290d55767d20`.
The selected bound at that base is `1661960547713947/10^18`.
[SOURCES.json](SOURCES.json) pins the four consumed source/input files.
The full input comes from the completed PR942 replay archive, not a newly
rebuilt supplier. Its compressed canonical-word SHA256 is
`387a2266ffe006d20042221d967f67a4b18d9bb8de1cd1e01d4031b539fa74a5`.

The initial profile assigns 516.468 of 533.973 profiled seconds to 33,111
exact state evaluations. Profiling adds overhead. These values locate the
cost; the unprofiled benchmark measures the improvement.

Three alternating rounds on Python 3.14.7, macOS 26.6.1, arm64 gave:

| Complete command | Median wall time (s) | Median user + system time (s) | Maximum process RSS (MiB) |
| --- | ---: | ---: | ---: |
| Retained original driver | 185.265 | 167.202 | 33.17 |
| PR662 dense evaluator | 24.786 | 23.911 | 49.59 |
| Sparse evaluator | 11.266 | 10.275 | 54.69 |

The ratios of median wall times are **16.44** against the original command
and **2.20** against PR662. All nine runs passed the full recipe and review
comparison. The source files were fixed before, during and after the runs.
See [the full measurement receipt](evidence/benchmark-python314.json),
[the command output](evidence/benchmark-python314.txt), and
[the profile](evidence/profile.txt).

Other research jobs used the same host. It was not isolated, and OS caches
were not flushed. Each child was a fresh Python process with empty gate
caches. The wall-time ranges were 167.076--204.528 s, 23.768--32.390 s,
and 8.124--11.465 s, respectively. These measurements describe this input
and host; they are not performance guarantees. The sparse command used
21.52 MiB more peak memory than the original and 5.09 MiB more than dense.
The optional commands include source admission, the gate tables and output
writing. Their memory measurements do not isolate the state representation.

The tests protect exact gate semantics, cancellation, compiler phase
equality and public input refusal. They compare 5,934 exhaustive small-gate
states and 540 mixed-circuit states with the retained scalar evaluator.
They cover all gate kinds, both `C` signs, `q = 0`, dimension zero, full
states, and inverse circuits that return to one nonzero amplitude.
Phase mutations preserve the tableau but must change the exact state.

Four corrupted words contain a dependent frame, a nonnested edge, a wrong
source frame, or a wrong target frame. The actual original driver, dense
entry point and sparse entry point each reject all four. Other controls
reject an unknown opcode, optimized Python, altered pinned source bytes,
and reuse of an output directory. A relocated source tree also passes.

All five test groups passed locally on Python 3.14.7; see
[the test output](evidence/tests-python314.txt). A separate coordinating
Codex agent repeated these tests and reviewed the source and proof; see
[its test output](evidence/parent-tests-python314.txt). This is separate AI
review, not independent human review. The selected-result verifier and its
five regression tests also passed with the selected record unchanged.

The focused workflow specifies Python 3.11 and 3.14 on Linux. It runs the
controls and a complete three-engine recipe comparison. Hosted CI is
separate from local verification. The repository-wide suite and complete
selected cold replay are outside this package's scoped validation.

The live overlap check on 2026-10-13 found PR662 to be the applicable dense
baseline. PR1006 changes T37 occupancy checks. PR900 changes historical
spectator-orbit rank checks. Neither changes this phase-state update or is
used by this package. New local-word proposals are outside the benchmark;
the measurements here apply to the pinned U8 input only.

See [NOTICE.md](NOTICE.md) for predecessor credit and AI-assistance disclosure.
