# Sharper bit bad-class charge on the eleven-stage cross-copy word

PR 450's balanced assembly binds on the bit moment. Its bit root
`674781707224226878971 / 5 * 10^23` sits strictly below `(1 - 10^-18)` times
its complex root `718766148669433 / 5 * 10^17`. The bit histogram, live width,
deficit, complex root, bootstrap and six-level outer assembly are unchanged
here. Only the bad-class term inside the bit moment is replaced by the bound
the source theorem proves.

## Inherited charge

`notes/three-stage-cover-bit.tex` proves two comparisons and then uses the
larger round numbers in the moment.

For the fallback count, with `N = 2 m`, Gaussian elimination of one bad
residual costs at most

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

so the inherited round fraction `10^-16` is valid but strictly larger. The two
improvements multiply: the sharp charge per edge is strictly smaller than
`10^-16 * 32 m^2`. PR 461 applied this sharp charge to PR 458's word; this
package applies it to PR 450's.

## Result

The cited bit profile is PR 450's hosted histogram at `m = 78`, `W = 1200`,
deficit 408, from `eleven/stacked_mixed/RESULT.json` at head `e36181b4`:

```
{1: 27060, 2: 11132, 3: 3036, 4: 3465, 5: 1188, 6: 462, 7: 154, 8: 99, 14: 1, 56: 184}
```

Replaying it with the inherited envelope through the engines in
`research/five-stage-gen4-banks`, whose `moment`, `certify`, `base_two_moment`
and `outer` are byte-identical to the engines PR 450 pins, reproduces

```
bit lower = 674781707224226878971 / 5 * 10^23
kappa     = 269548909542967 / 2 * 10^17
```

which is PR 450's published pair. With the sharp charge the same engines give

```
bit lower = 1349563417453477963841 / 10^24
kappa     = 269548910142353 / 2 * 10^17
          = 0.001347744550711765
```

The gain over PR 450 is `299693 / 10^17`. The complex root cited from PR 450
remains strictly above `(1 - 10^-18)` times the new bit root, with 6.5183
percent of slack, so the assembly stays bit-bound. Both interval engines put
the moment strictly below 1 at the new bit root and strictly above 1 at the
next `10^-24` point. All 47 outer inequalities hold at the new kappa, the next
`10^-18` grid point is rejected, and the zero-eta, zero-beta and unit-beta
controls are rejected. Adding one rank-56 child to the histogram lowers the
root, so the pair is tied to the cited histogram.

## Scope

PR 450's engine marks the `10^-16` and `32 m^2` envelope as an inherited
assumption whose portability to the eleven-stage cover is conditional. This
package keeps that conditionality unchanged: it replaces the round envelope by
the exact expressions the same theorem proves under the same hypotheses, and
makes no new admission. The complex side still uses the inherited envelope.
Sharpening it there would only widen slack that does not bind.

Run from the repository root:

```
python3 -B research/e8-eleven-stage-sharp-charge/prove.py
```
