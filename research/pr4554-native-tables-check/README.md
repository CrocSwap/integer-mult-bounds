# Independent check of #4554: paid native phase and exp tables

**Task:** independent-moment (independent source-bound coverage). **Base:** canonical main `f626db5c`. **No new κ.**

Dugongue's #4554 (head `4f46c6a9`) prepares two kinds of table:
- root powers `z^e`, with query error `16(E+d)/Q` and O(d) cost per query, in `PHASE-TABLES.md` §1;
- negative Gaussian weights `exp(−x)`, with error `< 2^−p`, O(1) cost per query and `O(n^η log n)` setup, in `NATIVE-EXP-TABLE.md`.

This package checks both, after my #4556, #4557 and #4558 on the same PR. The texts are vendored as `PR4554-PHASE-TABLES.md` (blob `2dab8f3e`) and `PR4554-NATIVE-EXP-TABLE.md` (blob `ee6e734c`), with their SHA256 pinned. Nothing is imported from #4554's `phase_tables.py` or `exp_table.py`.

## Results

All checked claims are confirmed.

**1. Root-power tables (§1).** The construction follows the spec: `t` rounded squarings per level, `T_j[a] = round(T_j[a−1]·z_j)`, and queries that multiply the d digit-selected entries starting from exact 1, with nearest rounding to `1/Q`.
- **Coverage.** Six `(D, t)` pairs from `(12, 1)` to `(2^20, 4)`. Each uses all four floor/ceil grid seeds around `exp(2πi/D)`, so every coordinate error is `< 1/Q`, and `Q` is the smallest power of two with `Q ≥ 64(E+d)`.
- **Query error.** Over 20,852 queries, every error is at most `16(E+d)/Q` against a decimal reference with AGM π. The worst is 0.076 of the bound.
- **Magnitudes.** Coordinates stay `≤ 2Q`, products `≤ 4Q²` and sums `≤ 8Q²`, all within `2p+8` signed bits.
- **Error-factor count.** A literal unfolding of the computation tree confirms at most `2E+d` error factors. `(2E+d)η ≤ 1/16`, so `(1+η)^(2E+d) − 1 ≤ 16(E+d)/Q`, checked exactly.

**2. Exp table.** Concrete constants are `(c, C, η) = (1, 2, 1/4)` and odd `d = 13`, which gives `η(d+1) = 3.5 > c+η+2 = 3.25`, with `c0 = 6`. The test sizes are `n = 2^16`, `2^20` and `2^24`, with up to 3,073 table entries.
- **Taylor base.** The exact rational Taylor polynomial, rounded down to S bits, satisfies `0 ≤ q̂ ≤ e^(−h)`, with `C_d ≤ 0.96`. Then `(C_d+1)J·2^(−S) ≤ 2^(−p−4)`.
- **Table entries.** Every entry satisfies `0 ≤ e^(−jh) − Ê_j ≤ j(C_d+1)2^(−S)`; the worst is 0.70 of the bound.
- **Queries.** 204 queries per size, at the edges, at multiples of `h` and at random points, all have error `< 2^−p`. The worst is 1.8·10⁻⁴ of `2^−p`.
- **Cutoff.** For these constants, the tail condition `h^(d+1)/(d+1)! ≤ 2^(−S)` holds for every `n = 2^m − 2` with `2 ≤ m ≤ 4096`. The "fixed finite cutoff" is empty here.
- **Signed corollary.** `exp(+x) = 1/exp(−x)` with the stated budget `ε ≤ 2^(−p−3)e^(−2C log₂(n+2))` and a `2^(−p−2)` reciprocal rounding gives error `< 2^−p` (worst 0.12).

**3. Binding.** 10 statements are bound verbatim to the vendored texts.

## Verify

```text
python3 -B research/pr4554-native-tables-check/verify.py
```

This runs in a few seconds with the standard library only.

## Limitations

- **Out of scope:** §2 of `PHASE-TABLES.md` (finite-precision lowering of linear programs) and the Gaussian caller's argument bounds.
- **Exp table constants.** The exp table is checked for one concrete `(c, C, η, d, c0)` and three sizes. The universal statement rests on the written recurrence, which these checks corroborate.
- **Reference.** References are decimal, at well above the needed precision; they are not interval-certified.

## Open next questions

- An independent check of `PHASE-TABLES.md` §2, the finite-precision lowering of linear straight-line programs, on an actual transform DAG. First step: instantiate it on a radix-2 FFT DAG and compare the `ε·N^A` bound with the exact error chain in my #4557.

Credit: Dugongue (#4554). Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
