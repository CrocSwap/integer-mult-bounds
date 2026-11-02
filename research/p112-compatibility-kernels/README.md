# Faster exact P112 plane compatibility

This contribution was produced by Nick Petalas. Apache-2.0.

The complete PR1325 scientific replay takes a local median **0.326 seconds**
with the restriction-kernel evaluator, versus **1.365 seconds** with the
retained source command, a **76.09% reduction** across five alternating runs
per side. All runs succeed with identical scientific stdout. This is a scoped
implementation-preservation proof, finite conformance evidence and a local
performance observation. No new kappa is claimed.

Philipp / mightyOil's [PR1325](https://github.com/CrocSwap/integer-mult-bounds/pull/1325)
supplies the census, equality theorem, witnesses and source implementation.
Its mathematics is a cited premise. The new step restricts bit-string basis
rows, preserving the complete 32,385-plane and
765-vector domains, canonical digest, witnesses and six rejection controls.
The predecessor package stays unchanged.

For a binary space with independent basis g_i, the exact replacement is

```text
log2(number of vectors v with v & mask = 0)
    = dimension(V) - binary_rank(g_i & mask).
```

[PROOF.md](PROOF.md) proves preservation of the complete scientific object.
The query stage masks 816,510 basis rows instead of 33,553,920 space vectors.
It also performs binary elimination and prepares four bases. This is not a
claim that the whole command has only 816,510 operations.

## Reproduce

Run from the repository root with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/p112-compatibility-kernels/fast.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/p112-compatibility-kernels/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p112-compatibility-kernels
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p112-compatibility-kernels --check-source-history
```

A reviewer can substitute their CPython 3.12 executable. The fast CLI prints
the same `PASS_SPARSE_REDUNDANT_DECODER` line as the source. The conformance
checker prints `PASS_P112_COMPATIBILITY_KERNELS` in a generated JSON stdout
receipt bound to all eight package files. It checks 1,072 exhaustive small
subspace/mask cases, 320 wide cases, five boundaries, the complete scientific
object and counted query work. Both registered commands include that complete
replay, with and without `-O`; each has a 120-second limit.

To reproduce the comparison, choose a fresh output path outside the checkout:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -B research/p112-compatibility-kernels/benchmark.py --write /tmp/p112-kernel-benchmark.json
```

The harness runs each entire command five times in alternating order, with
identical `-I -O -W error -B` flags. It checks exit status, exact stdout and
empty stderr for every sample. Source hashes, interpreter startup, census,
decoder checks, controls and certificate comparison all occur inside the
timed subprocess. It refuses to overwrite its output.

## Local timing evidence

CPython 3.12.15, macOS 27.0.1 arm64, 18 logical CPUs. The machine was shared;
the observed load averages were 9.46, 7.27 and 4.49. Other research and Git
processes were active. Alternation limits drift but does not establish a
portable performance guarantee. All ten commands returned success, with zero
stderr bytes and equal stdout hashes.

| Command | Five wall times, seconds | Median | Range |
|---|---|---|---|
| Source | 1.433095, 1.656254, 1.364952, 1.351939, 1.306152 | 1.364952 | 1.306152 to 1.656254 |
| Kernel | 0.317710, 0.338164, 0.326321, 0.331216, 0.293263 | 0.326321 | 0.293263 to 0.338164 |

CPU times are close to wall times on both sides. A separate, untimed cProfile
run attributes most source time to `run`, which contains the compatibility
comprehensions; all-pairs identity checks are the next substantial component.
The reduced scans explain the gain. The complete command still executes those
identity checks, source preparation, canonical JSON and hashing. The timing
comparison excludes the additional conformance verifier and does not claim
to accelerate the predecessor's independent implementation or package tests.

## Scope and credit

Sources are pinned to canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8. The card
`census-pruning-audit` changes scope to exact census acceleration, as recorded
in [TASK.json](TASK.json). The selected binding positive control passed.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19361674)
names this exact evaluation target.

PR1325's independent implementation already uses coefficient-space equations
and rank-nullity. This contribution claims the faster primary-receipt evaluator,
not priority for kernel dimensions or another mathematical verification.
The source retains Philipp / mightyOil's attribution and the PR845,
coordinate-reader, nine-term representation and deficiency-plane lineage.
Classical binary elimination and rank-nullity are used here. No predecessor
proof is audited or independently certified. Actual native delivery, dirty
restoration in a physical caller, complete recursive charges, stock, precision
and supplier admission remain outside this result. No selected cold replay,
Lean, Docker or independent human/formal-kernel review is claimed.

## Open next questions

Can the same kernel evaluator accelerate a different complete decoder census?
First profile its full command and identify its exact subspace-restriction
contract. Each source's ordering, receipt and rejection controls must survive;
this package proves no automatic compatibility. This is the sole Open next
questions item; research stops at the first verified improvement.

## Verifier bounds and deviations

The new code has no recursion. Kernel elimination uses at most nine passes
per row. Plane loops have three anchors and at most 255 by 254 candidate
pairs per anchor. Spaces have at most 512 vectors, masks have at most 112
bits and scientific fixtures have 112 rows. Source reads in the adapter are
bounded at one MiB per file before hash validation. The small-space generator has
four rounds, at most 67 spaces and sixteen vectors; wide enumeration has ten
dimensions, 32 masks and at most 512 vectors. Benchmarking has ten subprocesses,
each with a 60-second timeout. All new functions are below 60 physical lines.
Explicit exceptions remain active under optimized Python.

Power of Ten rules 3, 8 and 9 require managed-runtime deviations. Python
integers, JSON and containers allocate; fixed domains bound live collections.
One module with the exact source path is compiled from authenticated bytes,
and the verifier similarly loads the local evaluator. No generated expression
or user-supplied module name is executed, and bytecode caches are not read.
The retained source and six named control callbacks are the bounded indirect
targets. Their results are checked or intentionally discarded only where the
source also discards unused witness arrays. A future generic external-input
interface would require explicit capacity validation and a separate review.

Warning-strict normal and optimized execution and AST/function-size inspection
are the available diagnostics. Inherited source style is preserved through
the immutable adapter rather than changed in a frozen package. This is an
opt-in evaluator, not a shared verifier or CI-selection change.
