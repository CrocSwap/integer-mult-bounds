# A bounded matrix-vector cache for the full P104 native replay

The retained exact P104 checker repeats binary matrix-vector products while
interpreting native Gaussian states. This opt-in wrapper memoizes that pure
operation with a **32,768-entry process-local cache**, keyed by the entire
immutable matrix tuple and address. It runs the original checker unchanged
and compares its complete receipt to the frozen expected receipt.

On this Windows machine with CPython 3.12.14, three alternating fresh-process
pairs reduced median complete-replay wall time from **25.366922 to 21.910709
seconds**: **1.158x**, or approximately **13.6% less time**. All six runs return
the same complete mathematical receipt. This is one-machine evidence, not a
performance guarantee. Frozen source files and the selected frontier are unchanged.

## Measurement and mechanism

[PROFILE.json](PROFILE.json) records an initial cProfile run of the unmodified
`research/p104-native-channel/verify.py`. The pure binary `mul` function is
called 4,481,452 times and accounts for 34.636 seconds cumulative in the
instrumented run. Profiling overhead disproportionately affects tiny functions;
those instrumented timings are not the before/after wall benchmark.

The wrapper imports a fresh source checker only after authenticating all nine
declared source inputs. It temporarily replaces `module.N.mul` by
`lru_cache(maxsize=32768)(original_mul)`. It does not change the interpreter,
skip Gaussian columns, cache acceptance decisions or reuse a prepared receipt.
The function still runs on every miss. Its result is an immutable integer and
its dependencies are the pinned pure parity/product code. The full matrix value
and vector address form the key; no rank, filename, mutable object identity or
partial summary substitutes for those inputs. The wrapper restores the original
function and clears its cache in a `finally` block, including on failure.

The full fixture records 3,896,401 cache hits and 585,051 misses, with occupancy
capped at 32,768 entries. This entry bound is not a measured process-memory
bound. The wrapper is deliberately scoped to the pinned interpreter's immutable
tuple calls, not advertised as a replacement API accepting arbitrary mutable
matrix containers.

[BENCHMARK.json](BENCHMARK.json) retains all six wall times, interpreter/platform,
order, cache statistics and complete-receipt hashes. Each measurement includes
process startup, source hashing and receipt comparison; every run starts with
an empty cache. The host was not reserved exclusively; no system-load isolation
is claimed. Alternating order limits but does not remove contention. There is
no persistent benchmark cache or timing pass/fail gate.

| Pair | Order | Reference seconds | Cached seconds |
| --- | --- | ---: | ---: |
| 0 | reference, cached | 24.044590 | 22.873248 |
| 1 | cached, reference | 25.961044 | 21.910709 |
| 2 | reference, cached | 25.366922 | 20.900126 |

## Retained coverage and controls

The source checker still evaluates 740 distinct native transport recipes, all
1,410 paid occurrences, 208 intrinsic endpoint adapters, all 280 arbitrary
logical input columns, all 14,400 root pairings, and all **4,096** private-drop
Gaussian basis columns. It retains every original rejecting control: global
phase, missing transport, altered physical label, missing initial query
compensation and missing final cleanup. The entire structured source receipt,
including its exact hashes, histogram and scope, is compared; no subset digest
is used for acceptance.

An independent bit-by-bit multiplication loop checks the identity, all 72
elementary binary shears and all 36 row swaps on every one of 512 addresses:
**109 matrices and 55,808 products**. The check exercises bounded eviction,
equal-value immutable keys and explicit cache clearing. Actual counterexamples
show that omitting either the address or matrix from the key gives wrong
answers. These key controls complement, rather than replace, the five original
full semantic fault checks.

`test_boundary.py` runs the cached complete checker in a Git-free source export
and checks every exported file remains byte-identical. It then changes the
source checker, native interpreter, logical word and native recipe archive in
turn: all four fail at the hash boundary before any changed source executes.
No changed source file is silently admitted under an old cache entry.

## Reproduce

Python 3.12, standard library. Default replay writes no artifact:

```sh
python3.12 -I -O -B research/p104-native-matvec-cache/accelerated.py
python3.12 -I -O -B research/p104-native-matvec-cache/accelerated.py --reference
python3.12 scripts/research_package.py --package research/p104-native-matvec-cache
python3.12 -I -O -B research/p104-native-matvec-cache/benchmark.py --out /tmp/new-benchmark.json
```

The benchmark and optional `--out` replay receipt refuse to overwrite an existing
file. Windows may require TEMP/TMP pointed at a writable workspace. The registered
check runs complete cached replay, independent products/key tests, source-drift
tests and the Git-free export. It does not repeat the six timing measurements.

This contribution adds no new native identity, construction, supplier or kappa.
It inherits the original finite replay's scope and open side-correction/global
hosting/precision/all-size obligations. No selected cold replay, independent
human review or hosted-CI pass is claimed. Source pins are in
[SOURCES.json](SOURCES.json); selection and overlap limits are in [TASK.json](TASK.json).

## Open next questions

Does the same bounded cache help another named native replay, or does a larger
matrix alphabet erase the benefit? Profile that exact fixture first, then repeat
the complete receipt comparison and memory/runtime measurement. This result
establishes neither a universal speedup nor an optimal cache size.

## Credit

Prepared for **ywz65** with substantial OpenAI Codex assistance in profiling,
implementation, checking and writing. Apache-2.0. The original native interpreter
and its exact checks are credited to Ali Romman / PR1862, retained through PR1931;
the P104 native realization and complete checker are Chafik Boukhalfa / PR1991;
the original scalar/frame word is Rohan Arun / PR1972. Credit Adam Gall / PR1940,
Josie Elliston / PR1071, Ali Romman / PR1125, icekylinx's compiler lineage and
the retained E8/dirty-helper contributors. Frozen packages and notices remain
unchanged. The cache wrapper does not claim those prior mathematical results.
