# Four-factor reuse of signed Type A phase legs

**NO VERIFIED GAIN.** This package extends [#7420's pair and triple tests](https://github.com/CrocSwap/integer-mult-bounds/pull/7420) to four factors on the exact 38-factor Type A relative word from [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113). The independently reproduced complete comparator is [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) with #7113, κ = 0.00364665195644.

The [#7419 proper-window ranks](https://github.com/CrocSwap/integer-mult-bounds/pull/7419) rule out every four-set contained in a proper anchored window. Both exact methods check the 2,381 other four-sets, which meet J1 and J17. Every selected product has displacement rank four after transport past the unchanged intervening factors. Three rank-one changes cannot supply that displacement. All cases are resolved. Realized saving and Δκ are zero. [Proof](PROOF.md).

From a clean POSIX checkout with CPython 3.12 and assertions:

```sh
python3.12 -I -B research/p104-signed-phase-leg-four-factor-bound/replay.py
```

The replay authenticates the literal caller and exact predecessors, regenerates the denominator-safe modular certificates and independent integer minors, and rejects a corrupted caller. [Verification and sources](VERIFICATION.md).

## Open next questions

Can a changed factor group or a different signed provider lower the exact displacement and whole paid invoice? Pin one such change and price every new field and adapter before checking its signed action. Larger groups and edits to the unselected factors remain open.
