# Faster complete R2 verification through mutation-path isolation

The retained R2 audit spends most of its remaining time copying entire fixtures
for tests that modify a single event, recipe or gate. This opt-in adapter
reduces complete-audit median runtime from **32.643 to 6.084 seconds (5.37x)**
while running every original mutation and rejection predicate. Against
jackmgaller/#1939's existing checked-marshal copier on the same workload,
the improvement is **10.289 to 6.084 seconds (1.69x)**.

This is verification tooling. It does not improve kappa, change a native
operator, certify a supplier or implement recursive integer multiplication.
Path copying is an established technique; the contribution is its source-bound
integration, isolation argument and complete differential verification for this
current caller.

## Measured bottleneck and result

After PR3218's exact-comparator improvement, cProfile attributes 99.6 of 109.4
profiled seconds to deepcopy. Those figures include profiling overhead and are
used only to locate the bottleneck. [PROFILE.json](PROFILE.json) records that
diagnosis and the remaining source/event work.

The following measurements are unprofiled, with three fresh serial CPython
3.12.14 processes per mode, alternating order on the same Linux host:

| Copy mode | Mutation-copy median | Complete-audit median | Peak RSS median |
|---|---:|---:|---:|
| Original deepcopy | 25.603 s | 32.643 s | 138.57 MiB |
| Credited checked marshal | 2.908 s | 10.289 s | 142.12 MiB |
| Mutation paths | **0.061 s** | **6.084 s** | **135.16 MiB** |

Whole-audit runtime falls by about **81%** versus deepcopy and **41%** versus
checked marshal. The roughly 421x improvement in the copy interval is not a
whole-audit speedup. Memory differences are modest local observations.

[BENCHMARK.json](BENCHMARK.json) retains all nine raw samples, full-process
timings/RSS, exact source and adapter hashes, the complete original result's digest,
mutation footprints and circuit-decision digests. All modes include identical
snapshot authentication and original-fixture guards. OS caches were not
flushed; the host was shared; no timing threshold is imposed by CI.

All runs execute **32 semantic mutants** and the same **253 operator decisions
(244 accepted, 9 rejected)**. Native artifact generation is excluded. The
current PR3218 exact comparator and all original event/frame calculations are
unchanged. No acceptance result or predicate outcome is cached.

## What changes, and why the checks remain meaningful

For each literal mutation, the adapter copies the containers leading to the
affected event, recipe or gate, then deep-copies that small subtree. The two
mutations that only splice/pop an outer list copy just that list and its
ancestors. Other cells remain read-only and shared. This avoids repeatedly
walking millions of unrelated descendant objects.

The [proof](PROOF.md) lists all sixteen write footprints and derives the
tree-copy equivalence. This applies to the original strict-JSON fixtures and
pinned read-only predicates; it is not a generic deepcopy replacement for
arbitrary aliased graphs. Unknown mutation names and changed hook locations
fail explicitly. Every complete run compares the original fixture's full
serialized bytes before and after its audit and mutation tests.

The registered verifier additionally applies each original mutation to a
complete deepcopy and compares the **entire resulting word and data** with
the optimized mutant. It checks all 32 actual cases, not just changed fields
or rejection counts. The original mutation bodies, nonvacuity check, predicate
and exact rejection-message check remain executable. This differential check
deliberately pays for full copying and is slower than normal accelerated use.

The new controls also cover 100 generated tree/path equivalences (seed 21),
outer-list splicing, nested-write leakage, an unexpected write outside the
footprint, incorrect complete payloads, unknown mutations and malformed source
hooks. Three source-corruption controls and optimized Git-free replay check
the export/invalidation boundary. These are finite implementation checks,
not formal verification of the full multiplication theorem.

## Reproduce

From the repository root, with Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/r2-mutation-path-copy
```

Expected: `PASS_R2_PATH_COPY mutants=32 complete_deepcopy_equivalence=32 decisions=253`,
`PASS_R2_PATH_COPY_EXPORT`, and `PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=completed`.
The registered command includes the intentionally expensive differential check.

Normal accelerated complete audit, without regenerating any artifact:

```sh
python3 -I -B research/r2-mutation-path-copy/replay.py
```

Use `--mode deepcopy` or `--mode marshal` for the comparison modes;
`--differential` adds complete actual-mutant comparison. An optional
`--output FRESH.json` writes a full receipt. To repeat the benchmark:

```sh
python3.12 -I -B research/r2-mutation-path-copy/benchmark.py \
  --rounds 3 --output /tmp/r2-mutation-benchmark-fresh.json
```

Measured replay and RSS support Linux/macOS. Pickle protocol 5 is used only to
serialize trusted in-memory fixtures for exact within-process comparison; no
pickle data is loaded and no cross-version pickle certificate is required.

## Source boundary, related work and next steps

Base: `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
Pending PR3218: `a93c4f0bfcac21bf9c62c79728c8936e35ebbc3b`.
Its nested PR3202: `259043321323717b7e816d6be38ad5e1f0b69b4c`.
The entire predecessor package and checked-marshal source are retained verbatim.
[RETAINED.json](RETAINED.json) records all 27 original paths, commits, blobs and
hashes; [SOURCES.json](SOURCES.json) pins thirteen live inputs and historical
orientation records. All 40 retained/live files are authenticated before use.
Replay works without Git or pending foreign commit objects.

The private source transformations replace only mutation-copy construction and
add observation/immutability callbacks. Executed source hashes are recorded
separately from the historical kernel field in the unchanged nested result.
The generic package checker validates main-history pins; the package's own
capture validates retained pending sources. Frozen/default commands and the
selected frontier remain unchanged.

PR3208's separate R2 cleanup audit, PR3209's T16 reader cache and independent
host replication, and PR3219's Fano row-table work are complementary. This
package claims no coverage or timing result for those callers. Full native
prefix, physical ownership, precision/tape, efficient recursion and supplier/
outer admission remain inherited or unestablished here.

## Open next questions

Profile another named audit before reusing this
approach; derive its actual write footprints and compare every mutant against
full deepcopy. In this R2 caller, unchanged source/frame/event reconstruction
now dominates. Any future reuse must retain type/rank checks and explicit
invalidation. [TASK.json](TASK.json) gives first steps and blockers.

Credit 24kHandsome1201/#3202 for the audit, Tekalign/#3218 for the unchanged
comparator integration, jackmgaller/#1939 for the stronger copy baseline,
Sagar Thakrar/#1781, ywz65/#2638, Charles Bethin/#662 and the full retained
construction/native lineage in [NOTICE.md](NOTICE.md). New work by Tekalign
(@tekuuu), with substantial OpenAI Codex assistance. Apache-2.0; no independent
human or proof-kernel review is claimed.

[Canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-19002641).
