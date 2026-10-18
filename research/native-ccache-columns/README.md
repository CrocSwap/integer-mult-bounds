# Reuse native compilation while rerunning every column check

On this Linux/GCC fixture, a warm private compiler cache reduces the measured
build-and-replay median from **2.753 s to 0.240 s (11.46×)**. A fresh cache fill
takes **2.942 s**. These are local wall times for one native nine-stage checker
and two exact words; they are not whole selected-replay timings.

This uses the existing **ccache** implementation. The contribution is the
source-bound experiment, full native receipt comparison, toolchain binding and
actual invalidation controls. No production entry point, frozen source or
selected certificate is changed. Mathematical success receipts are never reused.

## Measured boundary

The unchanged `columns_k.cpp` comes from the merged
`research/e8-bit-carrier-skeleton` at canonical base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. Its lineage is DaysSky's PR #381,
Dylan Crow's PR #370 and the original cohort checkers; upstream attribution and
the nlohmann/json header are authenticated by `SOURCES.json`.

The two RAW6 fixtures are exact outputs of the complete native replay in
[our PR #2373](https://github.com/CrocSwap/integer-mult-bounds/pull/2373),
head `b52f87f5355ad9f02ca4ac4395117655ac1b19c7`: the PR #1188 baseline and
Sagar Thakrar's PR #2115 deferred-target-undo word. `FIXTURES.json` pins each
committed gzip container and its full uncompressed payload. The fixtures have
13,421 / 12,991 raw records and 10,492 / 10,062 scalar ADDs. The third fixture
removes one required undo from the latter word and must fail.

Every normal native execution retains all **1,327 formal columns**, **439 dirty
helper rows**, **nine stages**, **81 fresh copies**, **36 reverse fresh copies**,
**1,998 bridge additions**, exact signed-prefix bounds and **18 omitted-bridge
controls**. Both words have local rank mass 5,129 and the same paid histogram;
the existing source checker, not this optimization, establishes its native
column conclusions. The source's phase-label, geometric, hosting, owner and
physical admission limits remain; this package does not rerun the complete
legality/exporter/5-stage/11-stage pipeline from PR #2373.

Three uncached and three warm-cache samples were interleaved. Each sample
includes source and fixture authentication, fresh toolchain fingerprinting,
compilation or cache lookup, fresh linking, execution of both words and complete
receipt comparison. Each gets a new object/output directory. The fresh fill is
reported separately. `BENCHMARK.json` contains all individual times, command
arguments, object hashes, cache counters and execution receipts.

| Mode | Local median / time | Native execution |
| --- | ---: | --- |
| Uncached, three samples | 2.752770 s | Both complete words every sample |
| Warm cache, three samples | 0.240295 s | Both complete words every sample |
| Initial cache fill | 2.941703 s | Both complete words |

The warm improvement is 11.4558× on this host; first use is slower. The experiment
used GCC 15.2, ccache 4.12.3, Boost 1.90 and Python 3.12. Timing varies with host,
compiler, headers and cache state. `VALIDATION.json` records the separate
Python 3.14 read-only export replay. Hosted CI success is not implied.

## Cache and comparison contract

Ccache's [preprocessor mode](https://ccache.dev/manual/4.12.3.html#_the_preprocessor_mode)
keys the expanded translation unit and relevant compiler options. This experiment
turns direct/depend modes off, uses `compiler_check=content`, no sloppiness and
no remote storage. A dedicated config overrides system settings; all inherited
`CCACHE_*` variables are removed. A file named through `extra_files_to_hash`
adds fresh content hashes for the GCC driver, cc1plus, assembler, collect2,
linker and their shared libraries, plus target, compiler specs and a digest of
the effective environment. Compiler tools and the private cache remain trusted
build infrastructure, not an execution-authentication system. Those settings
follow the [ccache manual](https://ccache.dev/manual/4.12.3.html).

The linker runs every time. Every resulting executable runs on both positive
fixtures during timing. Reference and cached object SHA-256 values must match
within each experiment. Every native JSON field participates in strict canonical
comparison, with exactly two declared treatments: elapsed `seconds` must be a
finite nonnegative number and is removed; `local_scalar_stream` must equal the
actual input path and is replaced by the SHA-256 of the complete consumed raw
bytes. No role, stage, histogram, bill, control or scope field is dropped.

Seven actual controls run through the compiler/cache/executable chain:

1. Change a transitive header's COPY count from 9 to 8, preserving size and
   nanosecond mtime: cache miss, then the native COPY-count guard rejects it.
2. Change the source parity predicate, also preserving size and mtime: cache
   miss, then the full-column identity fails.
3. Change KPAIRS from 4 to 5: cache miss, and the actual eleven-stage executable
   checks 1,549 columns and 24 omitted bridges. This is a flag control, not a
   full eleven-stage supplier admission.
4. Change the extra toolchain profile: cache miss, with the same native result.
   This simulates a fingerprint change; no second GCC version was installed.
5. Restore the original inputs: a preprocessor-mode hit and both words pass.
6. Run the missing-undo word after that hit: the native defining column check
   fails, demonstrating that compilation reuse cannot reuse a mathematical pass.
7. Damage this experiment's private cached object result: ccache rebuilds it;
   both words then pass with complete receipts unchanged.

The full benchmark performs **13 builds and 24 native executions**: 21 positive
executions and three expected mathematical rejections. Twenty positive executions
use nine stages; the flag control uses eleven. In total the successful runs
execute 384 of the source's omitted-bridge controls. No timing sample substitutes
an old proof receipt for a command.

## Replay

The registered replay is standard-library Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/native-ccache-columns
```

It authenticates source/fixture bytes and independently checks every dirty
column with Python integer bitsets, every local signed-prefix bound and the
missing-undo failure. Nine package control groups check pin drift, payload
binding, strict comparison, location binding, invalid JSON, inherited cache
policy, actual-entry-point receipt corruption and output preservation. Its
marker explicitly says `PYTHON_COLUMNS_ONLY`: it does not compile C++ or measure
native performance.

For the actual native benchmark, install GCC, Boost headers and ccache, then:

```sh
python3.12 -I -O -B research/native-ccache-columns/benchmark.py \
  --work /tmp/native-cache-new-run --cxx /usr/bin/g++ \
  --ccache /usr/bin/ccache --boost-include /usr/include --repeats 3
```

The work directory must be new and outside the checkout. This harness currently
supports dynamically linked GCC tools on little-endian Linux. It uses a private
cache under that directory and changes no system cache. Each build, native run
and rejection retains its stdout/stderr there. The scoped workflow executes the
same benchmark. The locally downloaded ccache/Boost tools are not vendored in
this contribution.

## Selection and next scope

One fresh draw `2f939a000f93b5f7feca53d415dcfc3b` selected verifier-engineering,
first card `replay-runtime`, method source-bound reuse. No reroll or scope change.
The required selected baseline passed. Priority revision 4; selected κ unchanged.
Canonical claim: [Discussion #2408](https://github.com/CrocSwap/integer-mult-bounds/discussions/2408).

## Open next questions

Can the measured compilation boundary be integrated into a named production
native harness while retaining its exact pins and every required execution?
Start with PR #2373's native harness, keep its legality and 5/9/11-stage commands
and controls, and measure the entire before/after pipeline. This experiment
establishes one reusable compilation boundary; production adoption, persistent
CI caching and end-to-end speed remain separate work.

Gareth Davidson (@bitplane), with substantial OpenAI Codex assistance. No
subagents or independent human review. See `NOTICE.md` for the unchanged native
checker, fixture lineage and ccache attribution.
