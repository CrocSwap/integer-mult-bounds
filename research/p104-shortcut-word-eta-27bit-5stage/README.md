# K7 ordinary floor retuned for the charged suffix

The ordinary K7 floor was set to `L=18960` in #8067. That is the optimum of the complete ordinary factor for the old `64/L` suffix allowance, since the minimiser of `c·log L + (s+10)/L` is `L ≈ (s+10)/c`. #8073 proved the sharper suffix `10Σk/(tΨ) < 7.43958 < 8`, which does not depend on `L`, but it kept `L=18960`. This package books the suffix at `186/25` and moves the floor to the new optimum, `L=4474`. The directed complete ordinary factor falls below `2.573602304817903473`, which supports the ordinary debit `1430037/2^20` (#8073 used `11204/8192 = 1434112/2^20`).

Under the unchanged #8072 clock cap 318292011, the literal profile has ordinary heights `(8192,110461,524288)`, Gaussian height `511587` and conditional κ **0.003898224460300**. That is `2353397/500000000000000` (+4.707e-9) above [#8073](https://github.com/CrocSwap/integer-mult-bounds/pull/8073), and strictly above #8073's exact fixed-booking ceiling. The same five all-size premises apply. [Full proof and scope](PROOF.md) · [Exact signed invoice](RESULT.json)

The complete recurring log₂ C bound is `318291991`. The entry conversion uses `518` bits, the maximum native height stays `524288`, and the binary cuts are `(8290,118815,643167)`.

From a clean checkout with Git and CPython 3.12, run:

```sh
python3.12 -IB scripts/research_package.py --package research/p104-k7-floor-retune
```

The seven scopes are the same as #8073's: price, calendar, raw, exterior, nested, product and setup. The calendar scope re-runs the literal K7 opening at the new floor through the installed `Recipe.open` seam, and replays a full two-port fixture on the occupied K7 grade (49,64): 76380 opens, 456 returned paid prefixes and 38003660528 paid singletons. The negative controls are:
- #8073's 8/L booking at 18960 fails the new allowance;
- the next finer grid point `1430036/2^20` fails;
- the new profile is underfunded under #8073's debit;
- both adjacent Gaussian heights fail.

## Open next questions

The ordinary side now has its debit near the directed optimum of this factor, so the Gaussian finite factor and the clock cap bound the allocation. A larger step needs a charged change to the Gaussian word itself. For example: a legal rewrite that removes paid mass at fixed target ranks, with the full signed invoice and a literal witness.
