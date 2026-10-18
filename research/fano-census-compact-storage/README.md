# Compact storage for the exact Fano census

An opt-in representation change reduces memory in the complete retained
seven-owner Fano replay. A singleton equivalence class stores one base-`n`
word code; a member list is allocated only when another word reaches the
same exact matrix key. Every triple, full key, class member and ordered
relator pair is retained. No mathematical result or selected bound changes.

The fixed fixture has 1,379,952 reduced triples and 1,379,902 distinct product
keys. Of those classes, 1,379,852 are singletons and only 50 have two members.
The new representation therefore retains 50 member lists plus one index list,
instead of a member list for every key. It also handles larger classes;
the observed maximum of two is never used as an assumption.

## Measurements

Four alternating repetitions on this shared Linux host measured **43.0% less
mean peak RSS** with canonical multiplication and **44.4% less** with row
tables. Each of the 16 samples is a fresh process running the complete same
fixture. All complete receipts and census digests agree.

| Mode | Mean wall seconds [range] | Mean peak MiB [range] |
| --- | --- | --- |
| Canonical multiplication | 29.12 [28.42, 29.70] | 392.4 [392.34, 392.45] |
| Canonical + compact storage | 27.97 [27.55, 28.42] | 223.8 [223.71, 223.90] |
| PR3219 row tables | 11.65 [11.14, 12.14] | 380.3 [380.20, 380.41] |
| Row tables + compact storage | 10.32 [9.70, 11.23] | 211.4 [211.38, 211.50] |

The respective mean wall-time reductions are 4.0% and 11.4%. Timing ranges
for the row-table pair overlap. These are descriptive measurements, not a
significance claim or a portable speed/memory guarantee. Filesystem caches
were not cleared; mode order reverses on alternate repetitions. The exact
object-count reduction is independent of these environment-specific timings.

[BENCHMARK-python312.json](BENCHMARK-python312.json) retains all samples,
commands, receipts and 13 code/input hashes, checked unchanged before and
after measurement. Environment: CPython 3.12.15, Linux x86_64, AMD EPYC-Genoa,
four logical CPUs; GNU `time` from Ubuntu package `time` version `1.9-0.4`.
The parent measures wall time around the complete fresh process. GNU `time`
reports peak RSS in KiB; the table divides by 1024 for MiB.

The four modes distinguish canonical multiplication from Charan's separately
pinned PR3219 row-table engine, and apply compact storage to each. The source
file is retained verbatim for the optional comparison, with exact head, hash,
Git blob and attribution in [PREDECESSOR.json](PREDECESSOR.json). PR3219 is
pending work, not an adopted production dependency. The `baseline` and
`compact` workers never read that optional source.

## Coverage and exactness

The canonical/compact pair changes only the storage in `relation_census`.
The original `mul` and `pack` functions remain unchanged. The optional
composition likewise keeps PR3219's `prepare` and `product_key` functions
unchanged and feeds their full keys to the same compact storage object.

Every mode authenticates its inputs and executes the original complete
`build`: route extraction, involution and ordered-product checks, all
1,379,952 triples, relation identities and symmetry, the Fano incidence and
flag-label searches, and the original positive/missing-relation controls.
Each result must match the original committed receipt **byte for byte**.
We also compare a digest of the complete census total, histogram and sorted
relation set, beyond the aggregate counts in that receipt.

[PROOF.md](PROOF.md) gives the injective word encoding and class invariant.
Singletons cannot contribute a pair of distinct words. Collision lists retain
their first member and all later members, then enumerate exactly the original
ordered pairs and cyclic filter. Python dictionary keys remain full integers;
ordinary internal hash collisions do not equate distinct matrices.

Independent controls use a dense parity-of-dot-products oracle and cover
empty/single-matrix domains, duplicate and noncommuting matrices, classes
larger than two, leading-zero word codes and full keys with colliding Python
hashes. Semantic mutants lose the first class member or alias codes. Further
controls check authentication before execution, receipt mismatch, restoration
of the original callable, optional-source corruption, malformed benchmark
receipts, process timeout cleanup and output overwrite refusal. There is no
persistent acceptance cache.

## Reproduce

From the repository root, using standard-library CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/fano-census-compact-storage
python3.12 -I -B research/fano-census-compact-storage/worker.py --mode compact
python3.12 -I -B research/fano-census-compact-storage/benchmark.py --repetitions 4 --output /tmp/fano-compact-benchmark.json
```

Use a fresh output path. The benchmark requires Linux and GNU `time` at
`/usr/bin/time`; the full replay itself has no third-party Python dependency.
[VERIFY.json](VERIFY.json) registers complete four-mode equivalence and the
controls. Benchmark timings have no pass threshold and are not regenerated
by the registered checks.

The complete registered replay passes on CPython 3.12.15. All four full
replays reproduce the original 806-byte receipt and identical complete census
digest; all 17 controls pass in isolated optimized mode with warnings treated
as errors. The controls also pass in normal isolated mode. The benchmark's
13 measured code/input hashes still match the retained files.

This is an implementation-equivalence contribution. It inherits the original
observation model and proof obligations; it does not provide a new independent
mathematical verification, a larger support bound, supplier/native admission
or a kappa improvement. The selected cold replay, all-width implementation,
physical acquisition/restoration and formal proof are outside scope.

## Open next questions

Should compact storage be adopted together with the exact row-table engine?
First review the encoding/class invariant and reproduce complete receipts
and fresh-process measurements on another host. That would test portability
of the measured benefit; production adoption and the pending predecessor
still require maintainer review. No canonical verifier is changed here.

## Attribution and coordination

Canonical investigation:
[Discussion3062 comment19004550](https://github.com/CrocSwap/integer-mult-bounds/discussions/3062#discussioncomment-19004550).
Base canonical main and synchronized fork:
`463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
[TASK.json](TASK.json) records the original replay-runtime card and the
memory-focused scope refinement; [SOURCES.json](SOURCES.json) pins the
unchanged canonical executable, manifest, receipts and input closure.

Sudarsh Chaturvedi (`Sudarsh3301`), with Claude assistance, supplied PR3168's
independent census, Fano searches and controls. Gonzalo Mier supplied
PR3097's support-seven claim and first census. The chart-swap derivation and
earlier block-repair work retain Ross Richardson and Aaron Wang/navinor
(PR2391) credit; ywz65 supplied the selected centre observation interface.
Retain Rohan Arun, Jeremy Kothe, Hao Yan and the cumulative PR1094/589/555
supplier lineage, and Douglas Colkitt's review/package infrastructure.

Charan, with substantial OpenAI Codex assistance, supplied the distinct
row-table optimization in [PR3219](https://github.com/CrocSwap/integer-mult-bounds/pull/3219),
head `209d20d9da025c90110465f9a1f18186a6160147`. Its source header and
Apache-2.0 notice remain unchanged. The new contribution is compact class
storage, its equivalence proof and controls, and the measured composition.

Copyright 2026 thakrarsagar. Apache-2.0. Substantial OpenAI Codex assistance
in design, implementation, independent controls, benchmarking and writing.
Separate AI executions are not independent human review.

## Engineering constraints

Build the Lever is the compact class invariant, shared by the two actual
key engines. Prove It Works is full-receipt equivalence, independent small
oracles and deliberate failure controls. New functions are at most 60 lines;
checks remain active under `-O` and subprocess deadlines are explicit.
Managed-runtime allocation and execution of authenticated source are scoped
deviations from Power-of-Ten rules 3, 8 and 9. Exact pins and finite fixtures
bound them. Frozen predecessor loops and archives remain unchanged.
