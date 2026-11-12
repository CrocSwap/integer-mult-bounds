# Exclude the remaining delayed chart-127 corrections

At the exact [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) word and [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) signed caller, two distinct fixed late banks left open by [#7438](https://github.com/CrocSwap/integer-mult-bounds/pull/7438) cannot recover their omitted old source.

| Old key | Latest cut | Available chart-127 donors | Source value | Nonzero input coordinates |
|---|---:|---:|---:|---:|
| `[40430,40432,46222]` | 46224 | 298 | 1 | 8 |
| `[43091,43093,46566]` | 46568 | 417 | 1 | 157 |

Every donor evaluates to zero on its corresponding exact probe. The verified saving is zero and the conditional exponent is unchanged.

From a clean POSIX checkout with CPython 3.12:

```sh
python3.12 -I -B research/p104-chart127-delayed-bank-separators/replay.py
```

The [proof](PROOF.md) and [verification](VERIFICATION.md) describe the exact local exclusions and price. [#7438](https://github.com/CrocSwap/integer-mult-bounds/pull/7438) supplied the latest-cut model, [#7436](https://github.com/CrocSwap/integer-mult-bounds/pull/7436) the separating-input method, [#7434](https://github.com/CrocSwap/integer-mult-bounds/pull/7434) the original bank inventory, [#7362](https://github.com/CrocSwap/integer-mult-bounds/pull/7362) the directed rank arithmetic and [#7444](https://github.com/CrocSwap/integer-mult-bounds/pull/7444) the prior scalar replay structure for a different chart.

## Open next questions

No additional chart-127 key from the changed #7438 latest-cut inventory was left in this package's scope. A changed source, later observer, alternative donor frame or altered paid itinerary is a new experiment. Any future case needs fresh literal clocks and a positive fully charged price before a build.
