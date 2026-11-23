# K7 ordinary factor without the positive summation reserve

#8042's [TRANSFER.md](https://github.com/aliromman/integer-mult-bounds/blob/dfd25d553a843a946ca0b94130a5ff8943e98fdd/research/retimed-native-multiplier/TRANSFER.md#price-of-the-complete-integer-plan) gives one outward bound for `(256/255)F/N^t` that serves both suppliers. Only the numerical supplier uses the factor 256/255: there, the geometric sum is at most 256. The ordinary supplier needs only `(47/20)F < N^t`. Its same-rank child ratio `(75/32)/(47/20) = 375/376` is summed by the separate factor 376 in the ordinary clock ([ORDINARY-CLOCK.md](https://github.com/aliromman/integer-mult-bounds/blob/dfd25d553a843a946ca0b94130a5ff8943e98fdd/research/retimed-native-multiplier/ORDINARY-CLOCK.md), "Its finite geometric sum costs at most 376 at each stage"). #8057's FINITE-LOSS.md already drops 256/255 from the Gaussian supplier for the same reason. This package removes it from the ordinary K7 factor, which takes the floor-4474 ordinary debit from `1430037/2^20` (#8080) to `1424116/2^20`. It also books the Gaussian debit on a `2^-23` grid, at `1039017/2^23` instead of `64939/2^19`, using the unchanged directed Gaussian factor.

Under the unchanged #8072 clock cap 318292011, the Gaussian height reaches the top of the model domain, `G = 524288`. The ordinary heights are `(8192,101729,524288)`, and the conditional κ is **0.003898230327195**. That is `1173379/200000000000000` (+5.867e-9) above #8080 and +1.057e-8 above #8073. The Gaussian booking now binds, and the ordinary side keeps 8.7e-10 of slack. The complete recurring log₂ C is 318291971 and the entry conversion uses 520 bits. The same five all-size premises apply. [Exact signed invoice](RESULT.json)

From a clean checkout with Git and CPython 3.12, run:

```sh
python3.12 -IB scripts/research_package.py --package research/p104-k7-ordinary-reserve
```

The negative controls are:
- the ordinary factor with 256/255 kept fails the new allowance at both floors (4474 and 18960);
- the next finer ordinary point `1424115/2^20` and the Gaussian point `1039016/2^23` fail;
- the new profile is underfunded under #8080's debit, and under the old Gaussian booking `64939/2^19`;
- `G−1` fails Gaussian.

## Open next questions

With G at the 2^19 domain edge, the next charged step is either a proof that the native height domain extends to the 20-bit descriptor limit, which the setup scope already admits, or a legal rewrite of the Gaussian word that removes paid mass at fixed target ranks. Both need the full signed invoice.
