# Exact row tables for the seven-owner Fano census

**Verification tooling; no new bound, supplier or κ.** An opt-in adapter
accelerates Sudarsh Chaturvedi's PR3168 independent seven-owner verifier. It
replaces repeated binary matrix multiplication by exact per-invocation row
actions. Every one of the 1,379,952 reduced triples remains enumerated, with
full 289-bit product keys and the same complete canonical receipt.

On this Linux host, three alternating fresh-process pairs under CPython
3.12.14 measured a median **21.44 → 8.00 seconds (2.68×)** for the complete
check. The scope includes input/source hashing, chart-swap route derivation,
the entire census, Fano incidence and labelling searches, and original
positive/negative controls. CPython 3.13.5 measured **20.72 → 7.48 seconds (2.77×)** in three further
alternating pairs. Raw samples and process memory are retained in
[BENCHMARK-python312.json](BENCHMARK-python312.json) and
[BENCHMARK-python313.json](BENCHMARK-python313.json). Timing is descriptive,
with no pass threshold. Filesystem caches were warm; the host was shared.

## Reproduce

From the repository root, Python 3.12+ and standard library only:

```sh
python3 -I -B research/fano-census-row-tables/verify.py
```

Expected: `PASS_ALL_EXACT_TRIPLE_KEYS 1379952 rows 18388`, then
`PASS_FANO_ROW_TABLES e33a4809ad6ec2025aa46ecb5b2f9d790295379d4794bd911e0b67cf7e6aa652`.
This command compares **every actual product key** against the original
exact multiply/pack functions, then runs the complete table-backed check.
It checks the full committed PR3168 receipt byte for byte.

```sh
python3 -I -B -m unittest discover -s research/fano-census-row-tables -p 'test_*.py' -v
python3 -I -B research/fano-census-row-tables/benchmark.py --pairs 3 --out /tmp/new-fano-benchmark.json
python3 scripts/research_package.py --package research/fano-census-row-tables
```

Expected: seven test groups; `PASS_IDENTICAL_COMPLETE_FANO_BENCHMARK`; and
successful registered replay. Use a fresh benchmark/output path. The benchmark
runs both complete engines in separate processes, alternating their order,
and checks every receipt. `adapter.py --engine reference` selects the original
engine; the default is `tables`. No existing command is changed.

## Exactness, controls and limits

[PROOF.md](PROOF.md) gives the row-action and injective packing argument.
The 12,432 ordered pairs reach 18,388 distinct rows. Tables store the exact
right action of each of the 112 routes on those rows. No intermediate row,
triple, equality class or relation is sampled or omitted. No successful
validation is cached across invocations. The existing pair uniqueness,
spectator block, involution, symmetry and relation-identity checks all remain.

The complete result retains histogram `{1: 1379852, 2: 50}`, all 100 relation
words (50 braid edges), 30 labelled Fano planes, all 28 six-cycle constraints,
zero valid Fano labellings and the original planted/missing-relation controls.
Additional tests use a separate parity-of-dot-products oracle, exhaustive
small row domains, seed-91 dense 17-coordinate matrices, noncommuting factors,
duplicate/zero matrices and classes larger than two. Four corrupted kernels
are detected: lost high bit, reversed row order, wrong packing stride and a
wrong table entry. Same-size/same-mtime source mutation is rejected after
prior success; restoration works; missing sources and output reuse fail.
Tests also run with optimized Python.

This is an implementation-equivalence contribution, not another independent
mathematical verification of the support-seven theorem. It inherits the
original observation model, faithful cover-group representation and earlier
support bound. It does not add support-eight or length-eight coverage,
physical acquisition/restoration accounting, supplier admission or a new κ.
The full selected cold replay, `make verify`, Lean and hosted CI were not run
for this isolated opt-in stage. All-size/compiler, realization, hosting,
precision/tape and analytic assumptions remain.

## Sources and coordination

Exact base: `463113d675af7410ac91d53a4fed51ec6494eb9a`.
[SOURCES.json](SOURCES.json) records live input SHA-256 and Git blob pins.
The source archive remains immutable and its member hashes are still checked
by the original chart-swap derivation. The selected context at this base is
PR1094, conditional κ = `836330098538459/500000000000000000`, with PR589/555
bit ancestry; the selected-source inventory is unchanged.

OS assignment seed **91** selected verification engineering. Three narrow
candidates, method, stopping rule and the local claim are in [CLAIM.json](CLAIM.json).
No pinned sprint coordination issue existed. Overlap checks covered 253 open
PRs and 2,017 Discussion records with complete pagination, plus local package
notes. PR3147's larger-block question is distinct and is not investigated here.
The ledger classifies #3097 and #3168 as partially reviewed archival intake;
this tool does not promote their theorem status. PR3168 source head is
`b8844f08d8832eb87f8a5725f50d9c5eaac953d8`; PR3097 source head is
`ef7a52f4b0acf7cc8c51f9d81274d106abeffa24`. A finite replay is not a formal
proof of the multiplication theorem.

## Open next questions

Should this become the PR3168 default after review? A feasible next step is
to review the exact row/packing argument and reproduce the all-product
comparison and complete benchmark on another host. Maintainer review is the
remaining adoption step. No extension of the research family is proposed.

## Credit and license

Sudarsh Chaturvedi (`Sudarsh3301`), with Claude assistance, supplied PR3168's
independent census, Fano searches and controls. Gonzalo Mier (`Gonzalo-Mier`) supplied PR3097's support-seven claim and first
census, prepared with OpenAI Codex assistance. The chart-swap derivation
and earlier block-repair result retain Ross Richardson and Aaron Wang/navinor
(PR2391) credit; ywz65 supplied the selected centre observation interface.
Rohan Arun, Jeremy Kothe, Hao Yan and the cumulative PR1094/589/555 supplier
lineage retain their original attribution. Douglas Colkitt supplied the
source-bound review and research-package infrastructure.

This adapter, table engine, differential tests and benchmark were prepared by
**Charan**, with substantial **OpenAI Codex assistance** in design, code,
explanation, tests and handoff. No delegated or independent human review was
used. Apache-2.0. Frozen predecessor sources and notices remain unchanged.
