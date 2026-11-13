# Bound common-plane helper growth with productive endpoints

The source is exact [#7481](https://github.com/CrocSwap/integer-mult-bounds/pull/7481) with the retained [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) signed caller. Any eligible productive-public helper component may grow by a common two-dimensional plane, with every productive edge kept positive and every incident paid or productive rank charged. The [proof](PROOF.md) gives the exact paid and productive cut model.

The two engines exclude all 256 tested planes at the top of the 1,014-plane saved population. All 4,608 shared-price vertex optimizations give upper saving zero. The scan covers 552 eligible helper groups, 2,565 incident paid edges and 193 productive target edges. The other 758 saved planes and 42,421 planes outside the saved population are untested. The conditional exponent is unchanged.

From a clean POSIX checkout with CPython 3.12:

```sh
python3.12 -I -B research/p104-endpoint-common-plane-growth-bound/replay.py
```

[#7458](https://github.com/CrocSwap/integer-mult-bounds/pull/7458) supplied the four-direction plane population under fixed endpoints. [#7456](https://github.com/CrocSwap/integer-mult-bounds/pull/7456) supplied the common-vector endpoint model and shared price enclosure, [#7454](https://github.com/CrocSwap/integer-mult-bounds/pull/7454) the reverse lifetime and direct-cut routines, and [#7362](https://github.com/CrocSwap/integer-mult-bounds/pull/7362) the directed tariff. [#7465](https://github.com/CrocSwap/integer-mult-bounds/pull/7465) is a related closure proof for dimension-linear signed prices.

## Open next questions

The exact tested scope is common-plane growth with fixed scalar order and fixed main and owned frames. Untested planes, mixed promotions and demotions, and independent plane choices per component require new scopes. Any physical build still needs a positive full-invoice price.
