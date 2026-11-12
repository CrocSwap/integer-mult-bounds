# Bound historical-bank support for same-role MOVE fusions

**Outcome** — Scoped exclusions. The complete bound is unchanged.

The exact #7334 word has 967 same-role MOVE pairs with one intervening ADD into the moved role. A proposed fusion replaces the two paid MOVEs with one and retimes the ADD into the literal endpoint chart immediately after the second MOVE. Exact normalized source support excludes 724 cases. Exact rational separating covectors exclude the six highest-priced support survivors. The other 237 remain unresolved, with combined optimistic gross below 28.041 raw across 17 invocations even when overlapping savings are counted.

The reproduced single-case control uses role 1034 and clocks 48765–48767. The old ADD source has normalized row `−e831+e1497`. All 760 rows in the exact chart-127 endpoint bank have coordinate 831 zero. [Proof](PROOF.md)

## Replay

From a clean checkout on a POSIX host, use CPython 3.12 with assertions and its standard library.

```sh
python3.12 -I -B research/p104-historical-bank-move-fusion-bound/replay.py
```

The command verifies the exact native gzip blob and decompressed payload, reproduces four deterministic receipts and verifies their recorded digests. It rechecks every source-support case and all six rational duals with a separate forward mask engine. Use `--out DIRECTORY` to retain the full generated JSON receipts. Expected final line is `PASS_P104_HISTORICAL_BANK_MOVE_FUSION_BOUND`. [Verification](VERIFICATION.md)

## Open next questions

- Can another literal endpoint bank supply a lower-priced survivor? The next frozen price order starts at clocks 40255/40256/43362, role 147, peer 85, chart 908 and a five-role bank. Reconstruct these exact normalized rows and test rational span before spending on a physical build.
- Can an alternative transport or different cut preserve the same arbitrary-input action with a positive whole invoice? Pin its exact chronology and charge every added operation, ownership and restoration boundary, precision step and tape change. Every tested one-pair quote is smaller than one new paid rank-one child.

## Predecessors

- Clear1nsight’s #7334 `aaeec8c0acf01e99a5f331ef363a698d9c084ace` supplies the complete comparator, κ = 0.00364665195644, and the exact native word. Rohan Arun’s #7113 `07a76c5e2738882c0cb322278e56f6cae3c9885d` supplies its signed caller. [Comparator](https://github.com/CrocSwap/integer-mult-bounds/pull/7334), [signed caller](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
- #7171 develops normalized temporal support on #7161 with the read kept at its original clock. Exact #7414 `9a9e39d8a91ef27d36ef1fa20a478625fd04eba2` uses the retained #7334 word for adjacent pairs on different public roles. The present scope changes the ADD clock on one role. [Temporal support precedent](https://github.com/CrocSwap/integer-mult-bounds/pull/7171), [adjacent-pair precedent](https://github.com/CrocSwap/integer-mult-bounds/pull/7414)
- The exact reverse source-span implementation comes from `403e0d388c35e83b15eab5bba67be563b33d5a8a`. #7362 and #7298 supply the directed price receipt and tariff lineage. [Reverse engine](https://github.com/CrocSwap/integer-mult-bounds/blob/403e0d388c35e83b15eab5bba67be563b33d5a8a/research/p104-owned-add-source-span-bound/engines/reverse.py), [price receipt](https://github.com/CrocSwap/integer-mult-bounds/pull/7362), [tariff precedent](https://github.com/CrocSwap/integer-mult-bounds/pull/7298)

OpenAI Codex and subagents materially assisted the proof, implementation and independent replay.
