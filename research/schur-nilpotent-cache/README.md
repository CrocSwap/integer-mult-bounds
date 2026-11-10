# Bounded product reuse makes the complete nilpotent-Schur replay 9.15% faster

This contribution was produced by Nick Petalas. Apache-2.0.

The unchanged complete PR5267 replay takes a local median of 2.063804 seconds
with a 512-entry exact-product cache, compared with 2.271722 seconds through
its original entry point. That is a 9.15% reduction across ten alternating
fresh-process pairs. Every pair improves and every process succeeds with
byte-identical scientific output. This is a scoped implementation-preservation
proof, exact finite conformance and local performance evidence. It supplies
no new mathematical theorem, kappa or supplier admission.

The mathematical results, fixture selection, original implementation and
rejection controls remain ssafwann's PR5267 contribution. This package adds
one source-bound reuse boundary and its performance/conformance evidence.
It does not independently audit the predecessor's mathematical claims.

## Change and proof of preservation

The profiled complete original replay spends 4.969 of 6.236 cumulative
profiled seconds in `mul`, across 274,422 calls. These instrumented times
identify the bottleneck; they are not the timing comparison. The optimization
uses `functools.lru_cache(maxsize=512)` around this one original function.
The key consists of both ordered tuple matrices and the coefficient modulus.
No matrix algorithm, arithmetic, source fixture, expected value or original
check changes. The cache is empty at entry and cleared in a `finally` block.

The pinned `mul` reads its arguments, validates shapes and returns a tuple of
integer tuples. It has no writes or external effects. For the immutable tuple
arguments reached by the complete replay, identical keys therefore give
identical values or the same validation failure. A cache miss runs that exact
function. A hit returns the same immutable value computed for the identical
ordered matrices and modulus. Failed calls are not cached. Eviction only
replaces a later hit by another exact computation. These facts prove result
preservation at this boundary. Python's standard cache implementation is a
trusted runtime dependency, not a separately formalized theorem here.

`cached.py` authenticates the source SHA256 and compiles exactly those checked
bytes, avoiding a second source-file read between authentication and execution.
It changes only that source namespace's `mul` binding, then invokes the original
complete `main`. It neither copies nor edits a frozen predecessor file.
Different source bytes reject before execution. The callable is private to
one invocation; no cross-run, file-backed or global cache is supplied.

## Evidence and measurement

The conformance replay compares every one of the 274,422 reached products with
an uncached original evaluation, including all cache hits. It finds 128,609
hits and 145,813 misses. The maximum reached matrix extent is 22. The complete
scientific stdout SHA256 is unchanged:
`ba358675b3031aef57895701547380f864223c83ef89a9f44f039714f1a97fa0`.
Eleven controls cover modulus and factor-order keys, immutable reuse, empty
and malformed operands, capacity/eviction, retirement, changed source and
oversized source. All remain active under optimized Python.

[BENCHMARK.json](BENCHMARK.json) is the generated ten-pair confirmation record.
It binds the original, optimized entry point and measurement harness by SHA256.
Each timed region includes fresh process launch, complete computation and
process completion. Return status, stderr and the complete scientific output
are checked after timing. The benchmark includes no conformance instrumentation.
The original entry point and the cached entry point use identical interpreter
and warning/isolation flags. There is no tunable original cache configuration.

| Complete replay | Median seconds | Range, seconds | Successful processes |
|---|---:|---:|---:|
| Original | 2.271722 | 2.193223 to 2.318187 | 10 |
| Bounded reuse | 2.063804 | 2.031170 to 2.248516 | 10 |

The host is shared macOS arm64, CPython 3.12.15, with 18 logical cores.
Observed load averages were 4.20/2.89/2.36 before profiling and
4.31/3.57/2.80 during measurement. Other research processes were active and
were left alone. Ranges overlap, so the evidence is the repeated full-workload
comparison, not disjoint worst-case bounds or a cross-machine guarantee.
An initial five-pair pilot had a 7.10% lower median with overlapping ranges;
that unresolved variation prompted the unchanged ten-pair confirmation.
[PILOT.json](PILOT.json) retains those earlier observations. No later algorithm
or cache-capacity tuning was used. The remaining work includes the 145,813
misses, tuple hashing, matrix ranks and the rest of the unchanged replay.

The mathematical workload inherited from PR5267 includes all its 834 nilpotent
inputs, 45 padded fixtures, five scalar split inventories, six sector-factor
censuses and nine original rejection controls. These are cited predecessor
coverage, not new mathematical counts claimed by this contribution.

## Reproduce

From the repository root, use CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/schur-nilpotent-cache/cached.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/schur-nilpotent-cache/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/schur-nilpotent-cache/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/schur-nilpotent-cache
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/schur-nilpotent-cache --check-source-history
```

`cached.py` prints the original `PASS_SCHUR_NILPOTENT_EXTENSION` marker;
`verify.py` prints `PASS_SCHUR_NILPOTENT_CACHE calls=274422 hits=128609 controls=11`.
The other expected markers are `PASS_REGISTERED_RESEARCH_PACKAGE` and
`PASS_RESEARCH_COMMIT_BYTES`. `cached.py --uncached` runs the same authenticated
source without reuse for diagnostic comparisons.

To repeat the performance experiment, choose a new output path outside the
checkout. Substitute any CPython 3.12 interpreter for the displayed local path.

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/schur-nilpotent-cache/benchmark.py --rounds 10 --output /absolute/external/new-measurement.json
```

The registered checks authenticate the recorded implementation/source bindings
and rerun complete conformance. They do not rerun the timing experiment or
require a speedup on a different CI host. Source and benchmark records are
observations and declared inputs, not proof-kernel receipts. The verifier
prints a generated file-hash receipt to stdout and writes no publication file.
Temporary rejection-control files are retired on exit.

## Limits and code constraints

The reuse proof covers this exact immutable-input replay. Raw mutable matrix
inputs, other source revisions, cache sizes or callers require a separate
contract. No selected native/caller/cold replay, Lean, Docker, physical cost,
new compiler theorem or outer bound is supplied. Independent human and formal
proof-kernel review are unclaimed. No registered check is intentionally unrun.

The new functions are all below 60 lines, with no recursion. The cache has at
most 512 entries, each containing two keys and one result; the fixed source
reaches matrices of at most 22 by 22. The conformance observer enforces a
32-coordinate and 300,000-call ceiling. Source reads are capped at 64 KiB,
receipt reads at 64 KiB and benchmark samples at 15 pairs, with a 120-second
child timeout. Original fixture loops and their capacities remain inherited.
Every new invariant uses explicit exceptions and warning-strict replay.

Power of Ten deviations are limited to this offline Python implementation.
Rule 3: Python and the cache allocate dynamically. The fixed source domain,
512-entry cap and final retirement bound retained data, at most
3*512*22^2 scalar references plus row/key/cache metadata. A changed domain must
restate and check that bound. Rule 8: loading the original executable requires
one `compile`/`exec` boundary, constrained to the authenticated 64-KiB source
and its two checked entry points. Rule 9: the only replaced dynamic call target
is that pinned `mul`; the benchmark invokes only two explicit local scripts.
Rules 7 and 10: the child return status, stderr and full stdout are checked;
warning-strict compilation and registered normal/optimized checks are the
available standard-library diagnostics. Optional external Python analyzers
were unavailable. The inherited source is retained rather than refactored
under these rules. No real-time or fixed-allocation claim is made.

## Sources and overlap

Base: canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8,
selected PR6030. The originating PR5267 head is
`8ab280c8a3ef0544f13ff23a1c69df4757cd4900`.
[SOURCES.json](SOURCES.json) pins the exact main-based input bytes.
The original selected-source orientation passed its metadata-only binding
check; it was not a selected operator replay. The `replay-runtime` card is
refined to this complete source-bound fixture.

The fresh overlap helper covered 406 open PRs and 6,353 Discussion records with
complete remote pagination. Sparse local notes were incomplete; distinctive
searches of main and targeted merged-PR searches supplemented them. The later
Schur central-class and gluing packages answer mathematical follow-ups, so
those questions were excluded. No competing acceleration of this source was
found within that coverage. Arbitrary diffs and unpublished work remain
outside it. The advance claim is linked in TASK.json.

## Open next questions

Can the same bounded reuse contract help one separately named active replay?
Start with its profile, immutable inputs and measured repeated products, then
compare its complete end-to-end workload. No other source, cache capacity or
consumer is covered here. This package stops at the first verified improvement.

## Credit

This contribution was produced by Nick Petalas. ssafwann / Malik Safwan's
PR5267 supplies the original executable, mathematical normal form, complete
finite inventory and rejection controls. The original source and its credit
line remain unchanged. Its cited lineage includes Nick Petalas's sharp-sector
and stabilizer work, MatShep and codyw912's factor transport, Ryanson Jonathan,
lee-phys, Cinna Davis and the retained Schur/header contributors. Python's
standard bounded LRU cache and memoization are prior techniques; the new work
is this source-bound adaptation, preservation argument, complete conformance
and measured full-replay improvement. No literature-priority claim is made.
