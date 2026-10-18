# Faster exact shared-point merge construction with identical receipts

**Tooling improvement; no new kappa.** At base
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`, `SharedPointCircuit.__init__`
builds the common-point merge DAG by, for each of `h` commons, sorting the
local active set, unpacking child mappings through a per-node generator, and
looking up merge keys with repeated attribute access. Profiling on the
historical full-size circuit (`h=46`) shows construction wall time dominated by
that merge/lookup loop. Open
[CrocSwap/integer-mult-bounds#2039](https://github.com/CrocSwap/integer-mult-bounds/pull/2039)
noted construction cost on the partial-swap producer fork; this package
rewrites the canonical `scripts/shared_point_circuit.py` constructor (the
partial-swap `__init__` copy remains a separate follow-up).

This change pre-sorts `local.active` and `local.outputs` once, unpacks children
directly, binds hot lists/dicts locally, and keeps the historical node-allocation
order. Every structural field (`args`, `core`, `union`, `provenance`, `outputs`,
`active`, `merged_additions`, `additions`) and every verify receipt
(`circuit_sha256`, roles, flags) stays identical. The bit-compression
certificate does not list `scripts/shared_point_circuit.py` in `source_sha256`.
Production `verify` keeps the merged hand-rolled digests from
[CrocSwap/integer-mult-bounds#1994](https://github.com/CrocSwap/integer-mult-bounds/pull/1994);
this package only rewrites `__init__` merge/lookup construction.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/shared-point-init/verify.py
python3.12 -I -O -B research/shared-point-init/verify.py
python3.12 -B scripts/research_package.py --package research/shared-point-init
python3.12 -I -B research/shared-point-init/benchmark.py --rounds 5
```

Expected:

```text
PASS_SHARED_POINT_INIT verify_cases=5 mutant=rejected certs=0 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/shared-point-init outcome=completed
PASS_IDENTICAL_SHARED_POINT_INIT_RECEIPTS
```

Default verify is read-only. Full `make verify`, selected cold replay, Lean, and
multiplication-theorem obligations were not rerun for this isolated
historical-checker change.

## Result

On Linux / CPython 3.12.3 (Linux-6.12.94+-x86_64-with-glibc2.39), five
alternating fresh-process pairs timing only `SharedPointCircuit(46)` construction
(verify excluded from the timer; nested `ExclusionCircuit(45)` construction
included) gave median wall time **0.649 → 0.438 seconds (1.48×)**. Timing is
host-descriptive and is not a correctness gate; all samples and environment pins
are in [RESULT.json](RESULT.json). Every verify receipt matches the baseline
checker fieldwise (`roles`, `additions`, `merged_additions`, `circuit_sha256`,
flags), and the constructed DAG matches fieldwise.

## Equivalence

The historical constructor walks `sorted(self.local.active)` and
`sorted(self.local.outputs.items())` inside each common-point group, allocates a
new node unless `(core, union)` already appears in the cross-common lookup when
`core.bit_count() >= 2`, and records `(common, local_node)` provenance in
allocation order. This rewrite:

- sorts those two collections once before the common-point loop;
- replaces `a,b=(mapping[x] for x in self.local.args[node])` with direct indexing;
- uses one `bit_count` and `lookup.get` per internal node;
- binds `args`/`core`/`union`/`provenance` append methods locally;

and does not change when a merge hits, which node id is allocated, or which
output key is written. A reverse-common-order mutant that walks commons
descending changes `args` / provenance numbering and is rejected by the package
controls.

## Open next questions

1. **Question:** Should `research/bit-compression-provenance` refresh its live
   `scripts/shared_point_circuit.py` SHA-256 pin after this equivalence-preserving
   constructor rewrite?
   **Why it matters:** That provenance package binds working-tree bytes; leaving
   the old pin keeps this tooling PR focused.
   **First step:** Dedicated provenance follow-up that only rewrites that one
   `SOURCES.json` entry after confirming `circuit_sha256` identity.
   **Blocked by:** Pin repair is outside this tooling change.

2. **Question:** Is the same merge/lookup construction rewrite worth applying to
   `scripts/partial_swap/shared.py:SharedPointCircuit.__init__`?
   **Why it matters:** #2039 named that fork; large skip-strip builds still spend
   substantial wall time on its constructor.
   **First step:** Port after #2039 lands (or in a follow-up that updates the three
   `partial_swap` `source_sha256` certificate pins) and remeasure.
   **Blocked by:** Avoid concurrent pin conflict with open #2039 on that file.

## Overlap and credit

Closest priors (different objects):
[CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756),
[CrocSwap/integer-mult-bounds#1793](https://github.com/CrocSwap/integer-mult-bounds/pull/1793),
[CrocSwap/integer-mult-bounds#1861](https://github.com/CrocSwap/integer-mult-bounds/pull/1861),
[CrocSwap/integer-mult-bounds#1922](https://github.com/CrocSwap/integer-mult-bounds/pull/1922),
[CrocSwap/integer-mult-bounds#1984](https://github.com/CrocSwap/integer-mult-bounds/pull/1984),
[CrocSwap/integer-mult-bounds#1994](https://github.com/CrocSwap/integer-mult-bounds/pull/1994)
(verify digests on this file; this package changes only `__init__`),
[CrocSwap/integer-mult-bounds#2039](https://github.com/CrocSwap/integer-mult-bounds/pull/2039)
(partial-swap verify digests; open question this package answers on the canonical
constructor),
[CrocSwap/integer-mult-bounds#1874](https://github.com/CrocSwap/integer-mult-bounds/pull/1874),
[CrocSwap/integer-mult-bounds#2001](https://github.com/CrocSwap/integer-mult-bounds/pull/2001)
(ExclusionCircuit / DisjointTensor support masks — not touched).
No competing open PR on the canonical `SharedPointCircuit.__init__` merge object
at refresh.

Douglas R. Colkitt authored the shared-point / exclusion circuits and
bit-compression screens. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.

Also folded here: `research/shared-point-frame-contains/` (dense `support_in` cache for `verify_frames`, same production file).
