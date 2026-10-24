# Certified assembly of the R715 bit profile

PR 463 records a whole-residual eleven-stage bit histogram for its R715 word
and an exact bit root, and leaves the outer assembly uncertified. This note
checks that root and runs the six-level balanced assembly against PR 458's
complex root. The bad-class term is then replaced by the source bound. No
residual is placed on two families.

## Histogram

PR 463's tape audit recomputes the paid-children profile

```
{1: 26914, 2: 11799, 3: 2642, 4: 3569, 5: 1254, 6: 906, 7: 630, 8: 99, 42: 1, 56: 63}
```

at `m = 78`, `W = 1200`, rank mass 93192, deficit 408, largest child 56.
Replaying it through the inherited envelope `10^-16 * 32 m^2` reproduces

```
bit lower = 642564369945714399381 / (5 * 10^23)
```

which is the value in that audit.

## Assembly and sharp charge

PR 458's complex root `1297203880559577927527 / 10^24` stays strictly above
the bit root, so the assembly binds on the bit side. With the inherited
envelope the exponent is

```
641739651875561 / (5 * 10^17) = 0.001283479303751122
```

`notes/three-stage-cover-bit.tex` charges each bad edge at most
`(2 m^3 / 2^80) * (6 N (N - 1) + 3 N + 6 (N - 1))` rank-one children,
`N = 2 m`. At `m = 78` that is strictly below `10^-16 * 32 m^2`, since the
fallback count is 146478 rather than 194688 and `2 * 78^3 * 10^16 < 2^80`.
The sharp charge gives

```
bit lower = 642564371409803769573 / (5 * 10^23)
kappa     = 1283479306671789 / 10^18
          = 0.001283479306671789
```

The gain over PR 462 is `8984335486213 / 10^18`. Both interval engines put
the sharp moment strictly below 1 at this bit root and strictly above 1 one
`10^-24` step later. All 47 outer inequalities hold, and the next `10^-18`
grid point does not. Every bootstrap gap is positive, so the finite cutoff
exists for a 1664-bit coefficient charge and for a 10^6-bit charge.

The column audit of the R715 word remains PR 463's. This file certifies the
moment and the assembly of the histogram that audit published.

Run `python research/r715-certified-assembly/prove.py`.
