# Sharper bit bad-class charge

PR 458 makes the balanced assembly bind on the bit moment: its complex root
sits strictly above its bit root. The bit histogram, live width, complex root
and six-level outer assembly are unchanged. Only the bad-class term inside the
bit moment is replaced by the source theorem's own bound.

## Inherited charge

`notes/three-stage-cover-bit.tex` proves two comparisons, then uses the larger
round numbers in the moment.

For the fallback count, with `N = 2m`, Gaussian elimination of one bad residual
costs at most

```
6 N (N - 1) + 3 N + 6 (N - 1)
```

children, each of width at most one part in `m`. At `m = 78` this count is
146478, and `32 m^2 = 194688`.

For the bad fraction, every eligible cover prime `q > 2^80` gives fraction at
most `2 m^3 / q`, hence at most `2 m^3 / 2^80`. At `m = 78`,

```
2 * 78^3 * 10^16 < 2^80,
```

so the inherited round fraction `10^-16` is a valid but strictly larger
allowance. The two improvements multiply: the sharp charge per edge is strictly
smaller than `10^-16 * 32 m^2`.

## Result

The cited bit profile is PR 458's hosted histogram at `m = 78`, `W = 9600`,
deficit 3264. Replaying it with the inherited envelope reproduces

```
bit lower = 10205262550350024303 / 8000000000000000000000
kappa     = 1274032589159993 / 10^18
```

which is PR 458's published pair. With the sharp charge the same engines give

```
bit lower = 127565782172928582023 / 10^23
kappa     = 25480651841761 / 20000000000000000
          = 0.001274032592088050
```

The gain over PR 458 is `2928057 / 10^18`. The complex root cited from PR 458,

```
1297203880559577927527 / 10^24,
```

remains strictly above `(1 - 10^-18)` times the new bit root, so the assembly
stays bit-bound. Both interval engines put the moment strictly below 1 at the
new bit root and strictly above 1 at the next `10^-24` point. All 47 outer
inequalities hold, and the next `10^-18` grid point does not.

This does not divide a residual across families. The complex kernel, the bit
histogram and the compiler contracts are those of PR 458.

Run `python research/sharp-bit-bad-fraction/prove.py`.
