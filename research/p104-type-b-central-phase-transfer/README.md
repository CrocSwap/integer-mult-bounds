# Fixed-clock Type B central-phase transfers

**NO VERIFIED GAIN. Exact conditional κ change 0%.** Every tested transfer of the negative central phase from a rank-nine Type B IDLE_ODD to a larger Type B IDLE_ONE fails on the exact [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) caller. The two jobs keep their original clocks, roles and body masks. The narrow signed job would become rank eight, and an even job of rank 8m would become signed at rank 8m+1. All other operations and productive fields stay fixed.

The census covers all 104 pairs of four signed idles and 26 larger even idles of mask sizes two through eight. Fifty-two pairs have disjoint body masks. The modular check and the independent exact rational replay exclude every pair, with zero survivors and zero unresolved cases.

## Exact price and obstruction

The price uses independently replayed [#7314](https://github.com/CrocSwap/integer-mult-bounds/pull/7314) at `9d0119eb12fbd9fa534b48cd37b68e7099757b91`, κ = 0.003646221436446, with 17 signed native calls, 110,536 paid positions and 22,461 productive fields. The peer gain over #7277 is exactly 0.000000551507748. The present transfer contributes zero.

For (H_r=r^{1-\kappa}), the price-only credit across eight Type B ports is `D(m)=8[H9+H_(8m)−H8−H_(8m+1)]` before added charges. The exact prices are directed at the independent crossing upper. At most four transfers can be disjoint, and the four largest distinct even partners give upper `2D(8)+2D(7)`, about 0.22538900255587932 raw units. This grants the original volume and free additional work for the upper. The bound after support is exactly zero for each individual two-job transfer with all other operators fixed. The four-transfer figure is a price relaxation. Simultaneous transfers could cancel defects even at disjoint clocks, and that family remains open.

The [proof](PROOF.md) cancels unchanged body factors and compares the two-sided transport of the phase projector at (q=-1), body variables one. A nonzero outside coordinate rules out the required identity. The independent rational replay verifies the old 36-role endpoint and every modular exclusion. It independently enumerates the full scope from the literal caller.

This is a fixed-clock necessary obstruction. Changed surrounding operations, altered roles, additional signed providers, multi-role phase transfer and alternate field-volume models are open. The retained signed binder checks singleton masks. Extending that binder to a multi-stage signed child would require separate uniform ownership, tape, precision and phase evidence even if a different support route survived.

## Replay

From a clean checkout with CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/p104-type-b-central-phase-transfer
```

The same check works in a Git-free export and can emit all four receipts plus controls:

```sh
python3.12 -I -B research/p104-type-b-central-phase-transfer/replay.py --out fresh-receipts
```

[PRICE](receipts/PRICE.json), [BODY1](receipts/BODY1.json), [EXACT](receipts/EXACT.json) and [COMPARE](receipts/COMPARE.json) are the four frozen deterministic artifacts. Replay compares each byte for byte and rejects a corrupted caller. [Local pins](LOCAL-PINS.json) bind the bundled closure. [Public provenance](PROVENANCE.json) identifies the source commits, Git blobs and SHA-256 hashes.

The [admission record](admission/ADMITTED.json) binds the four successful independent #7314 stages and their verified frozen receipts. Source-history validation binds exact base ancestry, committed bytes and modes, and recursive archives. The stock full-history wrapper recorded its shallow-checkout refusal separately. The exact hosted run was queued at this frozen admission checkpoint. This package replays the transfer census and authenticates those existing admission receipts. A fresh #7314 native/caller admission is outside its runtime.

## Credit

[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) supplies the signed caller and singleton signed idle binding. [#7314](https://github.com/CrocSwap/integer-mult-bounds/pull/7314) supplies the independently replayed comparator and [#7277](https://github.com/CrocSwap/integer-mult-bounds/pull/7277) its predecessor and earlier complete invoice. [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) supplies directed tariff arithmetic.

[#7309](https://github.com/CrocSwap/integer-mult-bounds/pull/7309) bounds signed idle demotion with the fixed J blocks, [#7296](https://github.com/CrocSwap/integer-mult-bounds/pull/7296) supplies a one-child volume obstruction, [#7295](https://github.com/CrocSwap/integer-mult-bounds/pull/7295) prices fixed-contact lane capacity, and [#1252](https://github.com/CrocSwap/integer-mult-bounds/pull/1252) is the older paid idle rank-repartition precedent. OpenAI Codex and subagents materially assisted the proof, implementations, verification and packaging.

## Open next questions

Can a changed literal interval support a central-phase transfer at a positive complete price? First pin one changed interval and its complete paid, ordinary and field-volume bill, then test the exact two-sided projector relation. A surviving route would still need a uniform signed multi-stage binding and full dirty-data restoration at the original volume.
