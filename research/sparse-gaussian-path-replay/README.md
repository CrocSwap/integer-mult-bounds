# Faster complete weighted-path Gaussian replay

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped implementation-preservation proof, exact finite conformance
and local performance evidence. No new kappa or selected-frontier change.

An opt-in row-sparse Gaussian evaluator reduces the complete retained
[PR800](https://github.com/CrocSwap/integer-mult-bounds/pull/800) replay's median
wall time by **8.94%** in five alternating fresh-process pairs, from
0.574331250 s to 0.522962709 s. Every complete scientific output is identical.
The exact work reduction is **1,237,016 zero Gaussian products** on cache
misses, from 2,275,392 to 1,038,376 evaluations. These are Gaussian numerator
product evaluations, not real multiplications or processor instructions.

The new evaluator lists the nonzero entries in each right-hand row and visits
only those entries for every nonzero left-hand coefficient. It preserves the
source normalization, central-phase convention and 40,000-entry LRU capacity.
It adds no row or result cache. [PROOF.md](PROOF.md) proves equality over all
integer components in the fixed 8-by-8 representation and explains complete
consumer preservation. Sparse multiplication is classical; the contribution
is this source-bound evaluator and complete-consumer evidence.

## Evidence

The complete source replay remains intact. Its actual output retains the
73-word source screen, nine unresolved cases, 2,187 dense full paths, 919
certificates, 1,152 frame choices, 104 Laurent determinant controls and three
valid nine-call controls, together with every original rejection check.
These are retained workload counts, not new mathematical exclusions. Later
[PR955](https://github.com/CrocSwap/integer-mult-bounds/pull/955) closes the
remaining words; neither its conclusions nor PR800's conclusions are audited
or extended here.

The new verifier checks all **30,343 reached multiplication requests**, including
22,179 cache hits and 8,164 misses, against the original exact evaluator.
The ordered input/flag/result transcript has SHA256
`d1e74f64ea043c5cd5e7028cdf729488401ff111bf58392bb21e9ed137c1819d`.
The complete scientific stdout has SHA256
`5c63fd080111bc2848c9995866905f1bc3041cd1f357cc636602dc5a15225964`.
Both original and replacement cache inventories agree exactly.

A separate unpruned dot-product oracle checks 6,625 Gaussian numerator
products: all 6,561 ordered pairs of the 81 embedded 2-by-2 matrices with
entries in {0,1,i}, and 64 full signed large-integer fixtures. The controls
reject individual corruption of each of the seventeen source inputs, an
actual wrong-sign evaluator mutation, and optimized execution of both the
retained source and the adapter. This gives twenty rejected executions.
A fresh Git-free export with empty PATH reproduces the complete output.

The checker writes no package files. Its stdout is a generated receipt bound
to every package-file hash. There is no handwritten or committed result
receipt. Temporary exports, bytecode namespaces and logs belong outside the
checkout. The seventeen immutable source inputs are declared in VERIFY.json
and authenticated before source execution; source modules are compiled from
those bytes without loading their bytecode caches.

## Measurement

The final evaluator was measured with CPython 3.12.15 on macOS 27.0.1 arm64,
18 logical CPUs. Both commands use isolated, warning-strict, no-site execution
and a fresh bytecode namespace. The timed region includes process startup,
imports, source checks, the entire scientific replay, expected-result comparison
and output. Adapter authentication is included. No comparison-mode checks run
inside either timed arm. Every output agrees, with zero command errors.

Raw times in seconds, in actual reference-then-sparse order:

| Pair | Original complete command | Sparse complete command |
| --- | ---: | ---: |
| 1 | 0.573577583 | 0.518634458 |
| 2 | 0.572040000 | 0.519956750 |
| 3 | 0.574331250 | 0.525366416 |
| 4 | 0.576835583 | 0.522962709 |
| 5 | 0.578966791 | 0.527706291 |
| Median | 0.574331250 | 0.522962709 |
| Range | 0.572040000 to 0.578966791 | 0.518634458 to 0.527706291 |

The one-minute load average was 3.735 before and 3.394 after. Other application
and research processes were present, so the arms alternate on the same host.
Separate untimed profiles locate the original multiplication cost and the
remaining normalization and certificate-traversal costs. Omitting zero products
does not remove those costs. Profiling times are not the reported samples.
The timing claim concerns this complete fixed command on this host; CI does
not certify a universal speedup.

`benchmark.py` emits the raw samples, order, environment, output hash and hashes
of its four executing/manifest files and seventeen source inputs to a fresh
external path. Measurements are not a CI acceptance threshold. The preliminary
scratch prototype showed a larger gain with different invocation overhead;
only the final complete-command measurements above support the reported 8.94%.

## Reproduce

From the repository root, with the local interpreter and a scratch directory
outside the checkout:

```sh
TMPDIR=/absolute/scratch /Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/sparse-gaussian-path-replay
TMPDIR=/absolute/scratch /Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/sparse-gaussian-path-replay/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -S -W error -B research/sparse-gaussian-path-replay/adapter.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/sparse-gaussian-path-replay --check-source-history
```

Replace `/absolute/scratch` with an existing directory. Another CPython 3.12
path can replace the displayed interpreter; only the standard library is used.
The adapter's stdout is exactly the original scientific stdout. The verifier
prints `PASS_SPARSE_GAUSSIAN_PATH_REPLAY` in JSON, and registered replay prints
`PASS_REGISTERED_RESEARCH_PACKAGE`. The full registered command has a
120-second limit. Assertions remain enabled in every scientific source run.
Optimized scientific execution is deliberately rejected, as in the predecessor.

Optional measurement, using a previously nonexistent external output path:

```sh
TMPDIR=/absolute/scratch /Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/sparse-gaussian-path-replay/benchmark.py --output /absolute/scratch/measurement.json
```

## Scope, credit and overlap

Credit Jeremy Diviney / jeremydiviney for PR800's weighted-path theorem,
certificates, complete replay and controls; Ivan / littleBro for PR705's
corpus and screen and PR680's exact dense/symbolic model; eumemic PR288,
Swapnil Jain and the retained upstream Clifford lineage for the framework.
All predecessor bytes and credit lines remain unchanged. No predecessor
scientific result is claimed as original here.

Base canonical main is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority
revision 8. This refines the replay-runtime card to one complete consumer.
The selected-baseline binding command passed; the selected scientific cold
replay is unrelated and unrun. The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19362386)
precedes the evaluator and new conformance work.

Live open/account PRs, recent handoffs, local reservations, main README terms,
merged object/algorithm searches and the card cache were checked. The cache
covered 388 open PRs and 6,329 Discussion records with complete remote pagination,
but its local sparse scan omitted 8,801 of 8,917 HEAD note paths. Direct main
object searches supplement that scan. Search absence is not a novelty proof;
unpublished work and arbitrary historical diffs remain outside coverage.
Recent PR6207 changes a quadratic Gauss-sum evaluator for a different consumer;
this package neither reuses that algorithm nor answers its follow-up questions.

No new native operation, physical caller, dirty-restoration schedule, recursive
bill, supplier admission or complete multiplication theorem is supplied.
Stock, compiler, physical precision/tape and all inherited selected assumptions
retain their status. No Lean, Docker, native suite, PR955 replay or selected cold
replay was run. Independent human and formal proof-kernel review are unclaimed.

## Open next questions

Can this evaluator help the distinct complete PR955 consumer? First profile
its whole command and derive its exact input, output and failure contract;
then compare all reached calls and alternate complete runs. PR955 adds Boolean
and polynomial work, so the same dense module does not establish an end-to-end
gain there. No PR955 adapter, conformance transcript or measurement is supplied.
The structured question is in TASK.json. No continuation is reserved.

## Implementation constraints

The new arithmetic loops have fixed dimension eight, with at most 64 temporary
row entries and 64 real/imaginary result entries. Kernel tests use fixed domains;
source execution uses exactly the pinned finite corpus. Each new function is
below 60 physical lines. There is no recursion or arbitrary evaluator input.
All subprocesses have 30-second timeouts. Exports are at most 32 files, and
source input reads are limited to one MiB each. Scoped temporary directories
are removed on normal and exceptional exits.

Power of Ten deviations: CPython allocates managed integers and containers;
live growth is bounded by these domains and the retained 40,000-matrix result
cache. Fixed static allocation is not claimed. The source loader executes five
specific authenticated Python modules, and the evaluator calls one fixed source
normalizer through a bounded LRU wrapper. This indirect loading/dispatch is
required to preserve the original consumer. It accepts no executable source
from command-line input. Original assertions remain active; warning-strict
normal execution and explicit optimized-mode rejection are the diagnostics.
