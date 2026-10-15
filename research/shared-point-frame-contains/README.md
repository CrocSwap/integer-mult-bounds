# Faster exact shared-point frame nesting

**Folded into open [CrocSwap/integer-mult-bounds#2054](https://github.com/CrocSwap/integer-mult-bounds/pull/2054)** (same `scripts/shared_point_circuit.py` as `__init__`). Do not open a second upstream PR.

**Tooling improvement; no new kappa.** At base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` (after merged
[CrocSwap/integer-mult-bounds#1994](https://github.com/CrocSwap/integer-mult-bounds/pull/1994)
verify digests), `SharedPointCircuit.support_in` uses
`@lru_cache(maxsize=16384)`. Profiling
`SharedPointCircuit(46).verify_frames` with a precompiled program shows
`contained` / `support_in` dominate the timed window, with far more than
16384 distinct `(node, common)` pairs — the small LRU thrashes. Open
[#2054](https://github.com/CrocSwap/integer-mult-bounds/pull/2054) speeds
`__init__` merge construction on the same file; this package leaves that
surface alone.

This change memoizes `support_in` in a per-instance dense table indexed by
`node * h + common`, unpacks leaf and two-point pairs without a generator or
`sorted` call, and runs the `verify_frames` nesting walk through local
closures that share that table. Nesting predicates, `circuit_sha256`, and the
`verify_frames` receipt fields stay identical. The bit-compression certificate
does not list `scripts/shared_point_circuit.py` in `source_sha256`.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/shared-point-frame-contains/verify.py
python3.12 -I -O -B research/shared-point-frame-contains/verify.py
python3.12 -B scripts/research_package.py --package research/shared-point-frame-contains
python3.12 -I -B research/shared-point-frame-contains/benchmark.py --rounds 5
```

Expected:

```text
PASS_SHARED_POINT_FRAME_CONTAINS cases=5 json_files=… certs=0 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/shared-point-frame-contains outcome=completed
PASS_IDENTICAL_SHARED_POINT_FRAME_CONTAINS_RECEIPTS
```

On Linux / CPython 3.12.3 (Linux-6.12.94+-x86_64-with-glibc2.39), five
alternating fresh-process pairs timing only
`SharedPointCircuit(46).verify_frames(code)` (construction and compile
excluded) gave median wall time **2.888 → 1.729 seconds (1.67×)**. Timing is
host-descriptive and is not a correctness gate; see `RESULT.json`.

Default verify is read-only. Full `make verify`, selected cold replay, Lean, and
multiplication-theorem obligations were not rerun for this isolated
historical-checker change.

## Equivalence argument

- Dense-table hits return the same bitmask previously returned by the LRU path.
- Leaf triples still select the unique pair complementary to `common`; the
  branchless unpack yields the same ordered pair as
  `tuple(x for x in triple if x != common)`.
- Two-point stars still OR the same `pair_ids[common][pair]` bits over
  `union & ~core`.
- `verify_frames` still compiles (or accepts) the same program, walks the same
  forward and reverse role slots, and applies the same
  `contained(prev, node)` / `contained(node, prev)` predicates.
- `SharedPointCircuit.verify` digests from #1994 are untouched in structure;
  they continue to call `support_in` and receive identical masks.

## Coverage preserved

- `verify.py` compares baseline vs optimized `verify` and `verify_frames`
  receipts on `h ∈ {6,8,10,12,46}`, plus pointwise `support_in` on sampled
  active nodes.
- Corrupting a node's recorded core intersection still raises `AssertionError`
  in both engines (skipped under `-O` because historical checks use `assert`).
- Package JSON manifests are scanned for duplicate keys.
- Existing `tests/test_shared_point_network.py` and `tests/test_bit_compression.py`
  remain valid consumers; focused
  `tests/test_shared_point_frame_contains.py` covers the package controls.

## Open next questions

1. **Question:** Should `research/bit-compression-provenance` refresh its live
   `scripts/shared_point_circuit.py` SHA-256 pin after this rewrite?
   **Why it matters:** That package binds working-tree bytes; a later provenance
   replay would otherwise see a hash mismatch.
   **First step:** Dedicated pin-only follow-up after confirming receipt identity.

2. **Question:** After open #2054 merges, does folding its `__init__` rewrite
   onto this frame-contains cache keep `circuit_sha256` and frame receipts
   identical on one host?
   **Why it matters:** Both edit the same production file; a clean fold preserves
   combined review-throughput gain without dueling pins.
   **First step:** Rebase onto the merged #2054 tip and rerun verify + benchmark.

## Credit

Prepared by Wentao Li with substantial AI assistance. See `NOTICE.md`.
