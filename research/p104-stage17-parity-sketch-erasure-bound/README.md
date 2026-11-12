# Bound parity-sketch erasure of two stage-17 body lanes

**Outcome.** Scoped exclusion. The complete bound is unchanged.

Fix the two Type B stage-17 returns at clocks 4646 and 4660 on the exact #7334/#7113 construction. At width two, allow an arbitrary 2×2 erased matrix in each common Walsh-address cell selected by at most five linear parity probes. Even with free linear routing and erasure, the two dirty lanes require displacement rank at least seven eighths of one old lane volume. A single normalized rank-16 core requires volume at least 7/6 under this bound. The directed tariff funds less than 1.003 volumes. Its eight-port optimistic gross upper is below −20.798 raw. [Proof](PROOF.md)

## Replay

Use CPython 3.12 with assertions on POSIX. From the checkout root:

```sh
python3.12 -I -B research/p104-stage17-parity-sketch-erasure-bound/replay.py
```

Both exact engines use the standard library. The replay authenticates bundled source and receipts, reconstructs one exact extremal sketch over all 65,536 addresses, verifies the directed price, and rejects a changed literal caller. Expected output is `PASS_P104_STAGE17_PARITY_SKETCH_ERASURE_BOUND`. [Verification](VERIFICATION.md)

## Open next questions

The five-probe bound leaves erasures with more linear probes, nonlinear dependence, or cross-address mixing open. Before a build, specify one actual erased matrix family and its routing, reconstruct the exact residual capacity, then charge all field, setup, restoration, precision and tape costs. For a six-probe follow-up at the same width, start with the strengthened polar rank bound and test one concrete extremal sketch only if its full tariff can still improve.

## Predecessors

- #7334 and #7113 supply the exact native comparator, literal signed caller and binary Gaussian tensor factor. [Comparator](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) · [Caller](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
- #7406 supplies the two complementary return lanes. #7416 constructs a single parity shell and prices one affine extraction. This package uses arbitrary lane mixing within each cell of a bounded linear Walsh sketch. [Two-return volume](https://github.com/CrocSwap/integer-mult-bounds/pull/7406) · [Parity shell](https://github.com/CrocSwap/integer-mult-bounds/pull/7416)
- #7397 supplies the conditional volume tariff. #7362 and #7298 supply directed accounting and its implementation. [Tariff](https://github.com/CrocSwap/integer-mult-bounds/pull/7397) · [Directed stock](https://github.com/CrocSwap/integer-mult-bounds/pull/7362) · [Arithmetic](https://github.com/CrocSwap/integer-mult-bounds/pull/7298)

OpenAI Codex and subagents materially assisted proof, implementation, independent replay and packaging.
