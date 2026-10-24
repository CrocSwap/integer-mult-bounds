# Production envelope ratio

**Scoped comparison. No new κ.** The selected conditional exponent stays
60403/20000000. This does not accept PR #4100.

## Result

The ratio carried into the printed room is

```text
R = 3 r_max ((p+2) / 2^{ceil(log2(p+2))})^{64}.
```

On the #4174 production plan, `p = 9240576`, `ell = 24`, `L = 1540096`,
`G = 3072`, and `r_max = 5`. Then `ceil(log2(9240578)) = 24`, because
`2^{23} < 9240578 < 2^{24}`. The ratio is

```text
R = 15 (9240578 / 2^{24})^{64}.
```

The numerator `15 · 9240578^{64}` has bit length 1485, and the
denominator is `2^{1536}`, so

```text
2^{-52} ≤ R < 2^{-51}.
```

In particular `R < 1/6400`. The integer quotient of `1/6400` by `R` is
393602022308, with a positive remainder, so

```text
393602022308 < (1/6400) / R < 393602022309.
```

The bare room is larger still: its quotient by `R` is
2519052942774845, again with a positive remainder. `C_E` multiplies both
sides and is not evaluated. The 104,864-plan schedule is not replayed.

`L ≤ p` does not force this. The constructor accepts `p = 2^{24} - 2`,
`ell = 24`, and 65,536 widths of 23. There `L = 1507328 ≤ p`,
`G = 3072`, `r_max = 4`, and `p+2` is a power of two, so `R = 12`. That
exceeds both `1/6400` and the bare room. The production bound uses the
gap between 9240578 and `2^{24}`.

## Scope

Card `formal-interface-lemma`, scope **refined**. This is the open
question of the equality-case envelope product. Two layouts are
checked. No census, no real `E` polynomial, and no multiplication
theorem are claimed.

Canonical main fetched 2026-10-23T00:04:29Z at
`624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B research/crt-reservoir-production-ratio/verify.py
python3.12 -B scripts/research_package.py --package research/crt-reservoir-production-ratio
```

The direct command prints `PASS_CRT_RESERVOIR_PRODUCTION_RATIO`.

## Open next questions

1. On the edge layout `p = 2^{24} - 2`, `ell = 24`, `r_max = 4`, the
   envelope ratio equals 12. Is 12 still at most `p/6400`, the
   coefficient in the printed room line? The ratio exceeds `1/6400`
   and the bare room, while `L ≤ p`. First step: compare `12 · 6400`
   with `16777214`. Blocker: that comparison is not made here.

## Credit

Hiroki KUMAZAKI, PR #4174, for the production layout and the constructor.
PR #4646 for the printed envelope. PR #4924 for the ratio on the
equality case and on `p = 2`. Cinna Davis, PR #4100, for the CRT
parameters.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance.
Apache-2.0. No independent human review and no formal-kernel acceptance
are claimed.
