# Faster exact partial-swap merge construction with identical receipts

**Tooling improvement; no new kappa.** Stacked on open
[CrocSwap/integer-mult-bounds#2039](https://github.com/CrocSwap/integer-mult-bounds/pull/2039)
tip `3b29a00f972bd15871baac0acf5ac204740a9863` (verify digests already applied),
`partial_swap.shared.SharedPointCircuit.__init__` builds the common-point merge
DAG by, for each of `h` commons, sorting the local active set, unpacking child
mappings through a per-node generator, and looking up merge keys with repeated
attribute access. Profiling on the historical full-size circuit (`h=46`) shows
construction wall time dominated by that merge/lookup loop. Open
[CrocSwap/integer-mult-bounds#2054](https://github.com/CrocSwap/integer-mult-bounds/pull/2054)
applied the same construction rewrite to the canonical
`scripts/shared_point_circuit.py`; this package ports it to the distinct
partial-swap producer copy named in #2039's open question.

This change pre-sorts `local.active` and `local.outputs` once, unpacks children
directly, binds hot lists/dicts locally, and keeps the historical node-allocation
order (including the producer-specific `point_order` / sorted `pair_ids`
contracts). Every structural field (`args`, `core`, `union`, `provenance`,
`outputs`, `active`, `merged_additions`, `additions`) and every verify receipt
(`circuit_sha256`, roles, flags) stays identical. Production `verify` keeps
#2039's hand-rolled digests. `certificates/partial-swap-network.json` updates
only the `scripts/partial_swap/shared.py` `source_sha256` pin relative to the
#2039 tip.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/partial-swap-init/verify.py
python3.12 -I -O -B research/partial-swap-init/verify.py
python3.12 -B scripts/research_package.py --package research/partial-swap-init
python3.12 -I -B research/partial-swap-init/benchmark.py --rounds 5
```

Expected:

```text
PASS_PARTIAL_SWAP_INIT verify_cases=5 mutant=rejected certs=1 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/partial-swap-init outcome=completed
PASS_IDENTICAL_PARTIAL_SWAP_INIT_RECEIPTS
```

Default verify is read-only aside from the already-committed pin-only certificate
refresh. Full `make verify`, selected cold replay, Lean, and
multiplication-theorem obligations were not rerun for this isolated
historical-checker change.

## Result

On Linux / CPython 3.12.3 (Linux-6.12.94+-x86_64-with-glibc2.39), five
alternating fresh-process pairs timing only
`partial_swap.shared.SharedPointCircuit(46)` construction (verify excluded from
the timer; nested `ExclusionCircuit(45)` construction included) gave median wall
time **0.771 → 0.523 seconds (1.47×)**. Timing is host-descriptive and is not a
correctness gate; all samples and environment pins are in
[RESULT.json](RESULT.json). Every verify receipt matches the baseline checker
fieldwise (`roles`, `additions`, `merged_additions`, `circuit_sha256`, flags),
and the constructed DAG matches fieldwise.

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
controls. The #2039 tip `circuit_sha256` for `h=46` remains
`b0402f9eaaf138129939521c2a2ef1c3e8230b730de0a7bdea3596eb415dd173`.

## Open next questions

1. **Question:** Should research packages that pin live
   `scripts/partial_swap/shared.py` bytes refresh that one SHA-256 entry after
   this equivalence-preserving constructor rewrite?
   **Why it matters:** Those provenance packages bind working-tree bytes; leaving
   the old pin keeps this tooling PR focused.
   **First step:** Dedicated provenance follow-up that only rewrites that one
   entry after confirming `circuit_sha256` identity.
   **Blocked by:** Pin repair outside `certificates/partial-swap-network.json`
   is outside this tooling change.

2. **Question:** Once open #2039 and #2054 land, should the partial_swap and
   canonical constructors share a single tested helper for the merge/lookup loop?
   **Why it matters:** The producers diverge on `point_order` / `pair_ids`
   sorting and inlined local support checks; a shared helper risks coupling
   those contracts, but duplicated micro-opts drift.
   **First step:** Diff the two optimized `__init__` bodies after both land.
   **Blocked by:** Depends on merge order of #2039 / #2054 / this follow-up.

## Overlap and credit

Closest priors (different objects):
[CrocSwap/integer-mult-bounds#756](https://github.com/CrocSwap/integer-mult-bounds/pull/756),
[CrocSwap/integer-mult-bounds#1793](https://github.com/CrocSwap/integer-mult-bounds/pull/1793),
[CrocSwap/integer-mult-bounds#1861](https://github.com/CrocSwap/integer-mult-bounds/pull/1861),
[CrocSwap/integer-mult-bounds#1922](https://github.com/CrocSwap/integer-mult-bounds/pull/1922),
[CrocSwap/integer-mult-bounds#1984](https://github.com/CrocSwap/integer-mult-bounds/pull/1984),
[CrocSwap/integer-mult-bounds#1994](https://github.com/CrocSwap/integer-mult-bounds/pull/1994),
[CrocSwap/integer-mult-bounds#2039](https://github.com/CrocSwap/integer-mult-bounds/pull/2039)
(partial-swap verify digests; this stacks on that tip and only rewrites
`__init__`),
[CrocSwap/integer-mult-bounds#2054](https://github.com/CrocSwap/integer-mult-bounds/pull/2054)
(canonical `__init__` rewrite; this ports the same object to the partial-swap
fork),
[CrocSwap/integer-mult-bounds#1874](https://github.com/CrocSwap/integer-mult-bounds/pull/1874),
[CrocSwap/integer-mult-bounds#2001](https://github.com/CrocSwap/integer-mult-bounds/pull/2001)
(ExclusionCircuit / DisjointTensor support masks — not touched).
No competing open PR on the `partial_swap.shared` `__init__` merge object at
refresh.

Douglas R. Colkitt authored the shared-point / exclusion circuits. icekylinx
adapted the partial-swap producer copy. Prepared by Wentao Li
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0.
