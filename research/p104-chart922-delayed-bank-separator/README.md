# Exclude delayed correction from the chart-922 bank

At the exact [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) word and [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) signed caller, one changed cut left open by [#7438](https://github.com/CrocSwap/integer-mult-bounds/pull/7438) is excluded. This uses the fixed chart-922 bank at cut 43421 for key `[41944,41946,43419]`. The old source evaluates to 1 while all five donors evaluate to zero. The verified saving is zero, and the conditional exponent is unchanged.

From a clean POSIX checkout with CPython 3.12:

```sh
python3.12 -I -B research/p104-chart922-delayed-bank-separator/replay.py
```

The [proof](PROOF.md) and [verification](VERIFICATION.md) describe the exact local claim, tariff, and rejection control. [#7438](https://github.com/CrocSwap/integer-mult-bounds/pull/7438) supplied the latest-cut model, [#7436](https://github.com/CrocSwap/integer-mult-bounds/pull/7436) the separating-input method, [#7434](https://github.com/CrocSwap/integer-mult-bounds/pull/7434) the original bank inventory, and [#7362](https://github.com/CrocSwap/integer-mult-bounds/pull/7362) the directed rank arithmetic. [#7444](https://github.com/CrocSwap/integer-mult-bounds/pull/7444) supplied a predecessor scalar-replay structure and closed a different cut.

## Open next questions

The two remaining changed-cut keys `[40430,40432,46222]` and `[43091,43093,46566]` were outside scope. If revisiting this mechanism, freeze one bank, solve its exact span, and independently replay all donors before any native build. Other donor frames, changes to the paid itinerary, and other correction alphabets are outside the exclusion.
