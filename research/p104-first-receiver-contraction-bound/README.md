# P104 first-receiver repair bound after a three-MOVE contraction

One earlier exact endpoint membership still fails the first intermediate receiver on the current word. Both same-clock repairs tested here are excluded. Conditional κ stays at the independently reproduced 0.00364665195644 on exact [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) `aaeec8c0acf01e99a5f331ef363a698d9c084ace` with the [#7113 signed caller](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) `07a76c5e2738882c0cb322278e56f6cae3c9885d`. The maintainer-selected record is separate.

Public role 930 follows charts 3→652→657→649 at paid ranks 2, 4 and 1. A direct rank-seven lift at clock 42650 removes access to the chart-652 source for the receiver-793 ADD at pre-event cut 42651. Receiver 793 leaves for chart 653 at clock 42653. This package checks the one exact chart-652 bank at the original ADD clock. Its two unchanged public donors are 165 and 586. There are no live owned donors on that chart.

- On input 930, the receiver's existing coefficient is +1/2, the old ADD contributes −1/2, and both distinct donors are zero. Any local invertible update to receiver 793 while leaving its donors fixed requires a nonzero receiver diagonal. Matching this input forces diagonal zero.
- Grant one fresh stationary owned scratch field and allow the receiver to be erased before reconstruction. The first input still forces zero total coefficient on the old receiver. On input 893, the required full receiver row is +1/2 and both distinct donors are zero. The exact rational donor rank is two and adding the target raises it to three.

A hypothetical contraction across all 17 copies gives paid delta `{1:−17,2:−17,4:−17,7:+17}` with productive ranks fixed. The complete directed margin at the old crossing upper is in `(0.4127144682830787, 0.4127144682830788)` raw units before unbuilt ancillary work. One extra paid rank-one position defeats this one-edit quote. See [proof and price](PROOF.md).

## Reproduce

From the package directory, using CPython 3.12 and assertions enabled:

```sh
python3.12 -I -B replay.py
```

The standard-library replay authenticates all relative inputs, reconstructs the full directed price and both exact signed row proofs, and checks the forward/adjoint agreement and mutation controls. `--out receipts-replayed` saves the deterministic receipts listed in [receipts/SHA256.json](receipts/SHA256.json).

## Open next questions

A different receiver deadline, a changed paid path or a temporally retained source could change the bank. Price one concrete changed mechanism before searching new clocks. Neither later receiver of this carrier, any other interval from the older endpoint search, nor an expanded ownership interface was evaluated. The five comparator assumptions remain in force.

[#7274](https://github.com/CrocSwap/integer-mult-bounds/pull/7274) and its retained R29 endpoint search supply the old exact role-930 geometry and endpoint membership. [#7312](https://github.com/CrocSwap/integer-mult-bounds/pull/7312) supplies the earlier common-lift contact restriction. [#7338](https://github.com/CrocSwap/integer-mult-bounds/pull/7338) and [#7383](https://github.com/CrocSwap/integer-mult-bounds/pull/7383) cover distinct compensated fusion and shared-midpoint scopes. [#7355](https://github.com/CrocSwap/integer-mult-bounds/pull/7355) supplies the reverse rational engine. [#7387](https://github.com/CrocSwap/integer-mult-bounds/pull/7387) and [#7389](https://github.com/CrocSwap/integer-mult-bounds/pull/7389) supply related owned MOVE reconstruction and zero-initialization evidence. [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334), [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113), [#7362](https://github.com/CrocSwap/integer-mult-bounds/pull/7362) and [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) supply the exact comparator, caller, complete invoice and directed tariff. OpenAI Codex and subagents materially assisted.
