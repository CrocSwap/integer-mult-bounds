# Fixed installer bound at individual datum width w = 2^41

This note restates the serial fixed-installer bound of [#8055/#8057 `SERIAL-SETUP.md`](https://github.com/CrocSwap/integer-mult-bounds/commit/cbe847a953b971f9c6c5a0a6661e2008acd29086) and its height extensions in [#8081 `SETUP-PROOF.md`](https://github.com/CrocSwap/integer-mult-bounds/pull/8081), [#8094 `SETUP-27BIT.md`](https://github.com/CrocSwap/integer-mult-bounds/pull/8094) and [#8097 `SETUP-28BIT.md`](https://github.com/CrocSwap/integer-mult-bounds/pull/8097) with the individual datum width raised from `w = 2^40` to `w = 2^41`. **This changes one stated hypothesis of the inherited setup bound.** The arithmetic implementation, the encoding argument and the action census stay the same. Only the explicit width parameter and the resulting constant change. The change affects a fixed setup constant, not a rate-admission condition.

## Why 30 bits was sharp, and what 31 bits needs

#8098 observed that `1024·(2^30 − 1) + 3 < 2^40 < 1024·2^30 + 3`. Under `w = 2^40`, the fixed native control exponent `1024H + (m+1).bit_length()` of a 30-bit height therefore fits an individual datum, and the exponent of a 31-bit height does not. For every ordinary height `H < 2^31` and `m ≤ 7` stages:

- `92H ≤ 92·(2^31 − 1) < 2^40 < 2^41`, so a lazily materialized `2^(92H)` stays below the datum width.
- `1024H + (m+1).bit_length() ≤ 1024·(2^31 − 1) + 3 = 2199023254531 < 2^41 = 2199023255552 < 1024·2^31 + 3`.

So 31 bits is the sharp height limit for `w = 2^41`, exactly as 30 bits was for `w = 2^40`. The two Gaussian carriers stay tiny (`G = 1024` and `G = 52367`, each below `2^16`). As in #8081, `Recipe.__init__` and `WeightedRecipe.__init__` record `H` and `92H` and defer every calendar to an active caller. The census in `source/wide/check_installed.py` makes both `open()` and `width` raise if the fixed constructor touches them.

## The width-dependent terms

The serial argument in `SERIAL-SETUP.md` is stated for an arbitrary width parameter: both operands of each rational operation may have the full width `w`, unreduced magnitudes have at most `h = 2w + 2` bits, and a Euclid/Bézout reduction costs at most `2^16(h+4)(7h+9)`. Products, signed sums, exact divisions, normalization and erasure add `8·2^16(h+4)^2`. With `w = 2^41`:

```
h       = 2^42 + 2
scalar  = 2^16(h+4)(7h+9) + 8·2^16(h+4)^2  < 2^110        (unchanged exponent)
store   = 4w · 2^68 = 2^110 cells
lookup  = 8 · store · 512 · 128 = 2^130
total   = (2^68 + 1)(2^130 + scalar + 2^120) 2^32 < 2^231
```

With the #8081 allowance of `2^40` additional actions (`n = 2^68 + 2^40`) the expanded setup bound `(n+1)(8(4wn)·512·128 + E + 2^120)2^32` is also below `2^231`. The previous bound was `2^230`. The carrier and recipe allowance `2·2048·(2^25+1) + 10·2^24 = 137606729728 < 2^40` is unchanged, because the number of recipes (ten) and the Gaussian carrier bound are unchanged.

`check_wide_setup.py` evaluates the same formula at `w = 2^38`, reproduces the inherited `check_serial_setup.clock()` total exactly, and then evaluates it at `w = 2^41`. It also reruns the inherited 4,071 quotient/Bézout and 7,396 rational-operation tests. Those finite tests do not depend on `w`.

## What is not covered

- The `2^68` indexed-action census is inherited unchanged. This note does not rederive it.
- The historical portable WASI fuel trace and its `2^113` certificate are not claimed. That is the same position as #8081.
- Heights `H ≥ 2^31` violate `1024H + 3 < 2^41` and are excluded. Larger widths follow the same formula, but they are not checked by the literal stage-seam replay here (see `PROOF.md`, "Why 31 bits").
