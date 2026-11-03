# Sparse products for the complete frame-incidence replay

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped implementation-equivalence proof, exact operation-count
certificate and local performance evidence. The new adapter removes
**15,732,800 zero products** and **1,408,228 unit multiplications** from the
complete pinned PR1668 replay. It retains every scientific check and produces
identical scientific stdout. No mathematical result of PR1668 is claimed as
new, audited or independently accepted here. No new kappa is claimed.

The complete workload reaches 148 kernel calls and 353,069 dot products.
The original contracts 17,141,028 coordinate pairs. The replacement sums
1,408,228 selected coordinates and performs no scalar multiplication inside
those dot products. Selection, validation, geometry, ranks and all other work
remain paid by the measured process.

## The replacement and its proof

Let r be a binary incidence row and v an integer vector of equal width. Then

```text
sum_j r[j] v[j] = sum_(j with r[j]=1) v[j].
```

For each row, build its support once, then reuse it for the supplied kernel
vectors in their original order. Both implementations return false at the
first nonzero dot product, and true after the same final dot product. This
proves equivalence for every valid call, including zero rows and empty vector
lists. A zero coordinate contributes exactly zero; no rounding, modular
reduction, approximate rank or altered mathematical premise is involved.

The adapter validates its bounded binary-row/integer-vector domain. The pinned
source supplies only this domain. This is a scoped replacement contract, not
an equivalence for arbitrary iterators, side-effecting numeric objects,
nonbinary rows or malformed inputs that the original zip might truncate.

Only the fresh reference module's `kernel_ok` binding changes. Its main routine,
fixtures, graph conditions, Fraction ranks, modular restore tests, certificate
mutations and output formatting are unchanged. There is no persistent cache,
reused result or skipped check. The SHA256 of the reference is checked before
its bytes are compiled. Compilation explicitly uses `optimize=0`, including
when the adapter runs under `-O`, so the retained assertions remain enabled.

The scientific source remains byte-identical at
`research/full-family-g-without-d/verify.py`, SHA256
`2e45790da2cc2b2eea2e47900a94cadf7aa4a7d42a3d38390729cd9b409d73fb`.

## Evidence

`verify.py` compares the original, sparse and separately counted predicate at
every reached call of the complete workload. Both full runs must finish and
their entire stdout must agree. The scientific stdout SHA256 is
`5ece3cdbfec55235c3d95cfcf7bae6448b31cc6b7d4504676c06a7200ec9ce4b`.
The hash of the exact reached arguments and predicate results is
`3df326c08d6f4b7eb7e811e6f3f67202c12b7836d42a75724b53128b674650e8`.
These are implementation-conformance checks, not independent review of the
scientific theorem or a new census of its objects.

The operation counter follows the original row/vector short-circuit order.
It enumerates 51,419 reached row scans and two false kernel calls, including
the predecessor's damaged-certificate controls. Thus the claimed counts do
not charge dots after a failure. No receipt is handwritten or trusted as an
input; the verifier generates a report bound to every package file.

All 55,987 combinations of a binary row and a ternary vector at widths zero
through six also agree with literal dense arithmetic. Fourteen controls cover
nonbinary values, ragged rows, vector dimensions/types, all three capacity
bounds, empty predicates, a nonzero dot, altered/oversized source bytes and
retained reference assertions under optimized execution.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/frame-kernel-sparse-products/replay.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/frame-kernel-sparse-products/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/frame-kernel-sparse-products/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/frame-kernel-sparse-products
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/frame-kernel-sparse-products --check-source-history
```

Other machines may substitute their absolute CPython 3.12 path. A sparse
checkout must materialize both this package and `research/full-family-g-without-d`.
`VERIFY.json` declares the sole scientific runtime input. The original README,
catalogue and selected record are historical provenance pins in `SOURCES.json`.
The direct conformance marker is `PASS_FRAME_KERNEL_SPARSE_PRODUCTS`.

For a fresh-process end-to-end measurement:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/frame-kernel-sparse-products/benchmark.py --pairs 15
```

The benchmark times complete process creation, source authentication, reference
compilation/initialization and the full main routine. It alternates the original
kernel and sparse kernel with identical flags and no reused scientific state.
Every process must exit zero with empty stderr and identical complete stdout.
Timing is observational and is never a CI pass condition.

## Local runtime

Fifteen alternating fresh-process pairs on CPython 3.12.15, macOS arm64, give a **10.94%** median wall-time reduction. All fifteen pairs improve; all thirty complete outputs agree, with zero failures.

| Version | Median seconds | Range seconds |
| --- | ---: | ---: |
| Original kernel | 1.801392 | 1.787448 to 1.983607 |
| Sparse kernel | 1.604257 | 1.573416 to 1.769150 |

The process runs on a shared 18-logical-CPU host. Its final load average was 2.96 / 3.06 / 2.45. Profiling was separate from reported timings. An initial seven-pair diagnostic overlapped one conformance run and was discarded; a later seven-pair observation had wider noise. The fifteen-pair serial run below is the published measurement, with no concurrent task-local replay or profiler. Other users and processes remained outside this task's control.

| Pair | Original seconds | Sparse seconds |
| ---: | ---: | ---: |
| 1 | 1.797559208 | 1.574686667 |
| 2 | 1.800518500 | 1.578095333 |
| 3 | 1.787448333 | 1.584051208 |
| 4 | 1.792102667 | 1.587584125 |
| 5 | 1.800453875 | 1.604909792 |
| 6 | 1.801391875 | 1.573415958 |
| 7 | 1.792766666 | 1.585695583 |
| 8 | 1.844230083 | 1.608174916 |
| 9 | 1.821983042 | 1.649498250 |
| 10 | 1.820826333 | 1.604256709 |
| 11 | 1.804861750 | 1.769150084 |
| 12 | 1.814463125 | 1.612519375 |
| 13 | 1.791639083 | 1.668824833 |
| 14 | 1.983606875 | 1.584959708 |
| 15 | 1.833430208 | 1.744815625 |

A separate baseline profile attributes 1.066 of 4.368 instrumented main-routine seconds to kernel products, about 24.4%. The observed wall-time reduction is below that ceiling. The separate candidate profile still spends 2.102 of 3.670 instrumented main-routine seconds in Fraction elimination. Fraction elimination remains the dominant unchanged cost; this optimization makes no rank arithmetic change. Profiles are diagnostics and their instrumented seconds are excluded from the wall-time comparison. The benchmark measures the whole direct replay, not CI setup, environment installation or the extra conformance runner. The time percentage is local evidence, not a portable speed guarantee or a claim that multiplication itself is faster.

## Scope and credit

Credit Josie Elliston / PR1668 for the full scientific replay, fixtures and
mathematical result; PR1650 for its retained geometry and criterion execution;
Andrey Mas / PR1560 for the incidence criterion; Aaron Wang / PR1649 for the
selected-family boundary; and the retained Brett Halligan / PR1212,
themilkman216 / PR968 and DreamingOfClouds / PR717 decoder lineage. Their files
and notices remain unchanged. Sparse dot products are classical. The new
contribution is this exact source-bound implementation and its complete-workload
operation saving and runtime evidence.

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priorities
revision eight, selected PR6030. The selected binding-only orientation passed.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19370283)
and `TASK.json` record the scope. Live overlap covered 506 open PR records and
6,503 Discussion records. The helper searched 130 of 8,917 main-tree note
records; distinctive Git-object and merged-PR searches supplemented that sparse
coverage. Arbitrary historical diffs and unpublished work remain limits.

No larger P105 timing, independent theorem audit, native supplier, physical
caller, recursive invoice, selected-frontier improvement, proof-kernel review
or complete multiplication theorem is supplied. All five selected framework
assumptions remain. Selected cold replay, Lean and Docker are unrun.
Independent human and formal proof-kernel review are unclaimed.

## Implementation constraints

New loops are bounded by 2,025 rows, 120 columns, eight kernel vectors,
55,987 small fixtures, fourteen controls and at most twenty benchmark pairs.
Each child process has a 120-second bound. Every new function is below sixty
physical lines. Source reads stop after 65,537 bytes; package reads stop after
one MiB plus a guard byte, with at most twelve files. Explicit exceptions remain
enabled under `-O`; the scientific reference is deliberately unoptimized.

Python managed allocation is a Power of Ten rule 3 deviation. The finite
domains bound live matrices and support tuples; the authenticated scientific
workload uses bounded integer coefficients. No fixed-allocation or arbitrary
large-integer service claim is made. Rule 8's constrained dynamic-code deviation
is the single fixed-hash reference program, compiled without edits. Its inherited
frame enumeration has recursion bounded by eight levels; that frozen code is
outside the new implementation. New call paths are acyclic. The verifier's
one bounded comparison callback and stdlib dispatch are managed-runtime
indirections. Warning-strict normal and optimized checks provide diagnostics.
Build the Lever supplied the rerunnable adapter and counter; Prove It Works
required full stdout and call equality; Explain the Number required complete
alternating processes rather than a dot-product microbenchmark.

## Open next questions

Can a separately budgeted larger incidence replay benefit from this binary-row
contraction? First profile one complete command and prove its replaced rows are
binary. No larger workload, speed estimate or integration is supplied here.
Stop after this first verified improvement; no rank or geometry optimization
is included. Native and physical costs remain separate from verifier runtime.
