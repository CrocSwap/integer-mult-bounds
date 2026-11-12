# Type B odd-rail rank concentration bound

**NO VERIFIED GAIN.** This package checks the two paid rank-nine odd Type B returns at clocks 1339 and 2970 on all eight ports. The independently reproduced comparator remains [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) at `aaeec8c0acf01e99a5f331ef363a698d9c084ace` with [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) at `07a76c5e2738882c0cb322278e56f6cae3c9885d`, κ = 0.00364665195644.

Changing the paid ranks from (9,9) to (8,10) preserves rank mass and offers optimistic gross about 0.0032105351558918767 raw across all eight ports. The required opposite-sign action has rank two on a matched fibre. The replacement has only one q-sensitive lane when the rank-eight child retains its pure stage-8 body. Its opposite-sign action has rank at most one with q-even wrappers and fixed fibres. Both exact engines confirm the four-column witness, so no replacement was built. Realized saving and Δκ are zero. [Exact proof and price](PROOF.md).

Use POSIX CPython 3.12 with assertions from a clean checkout.

```sh
python3.12 -I -B research/p104-type-b-odd-rail-concentration-bound/replay.py
```

The replay verifies exact input hashes, regenerates both independent receipts and rejects a corrupted literal caller in a disposable copy. No network or earlier temporary files are needed. [Verification](VERIFICATION.md).

## Open next questions

Can a rank-eight core introduce its own q-sensitive direction and recover the body axis it would drop? Pin a concrete zero-extra-paid body-axis recovery route, then check both the exact signed response and the removed body derivative. One added paid rank-one position already defeats the price. Cross-fibre packing, a q-sensitive bypass, different axes and different tariffs remain open.
