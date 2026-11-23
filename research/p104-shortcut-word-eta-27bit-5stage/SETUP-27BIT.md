# Fixed installer bound at 27-bit ordinary heights and nine recipes

This note extends the 25-bit fixed-installer lemma of [#8081](https://github.com/CrocSwap/integer-mult-bounds/pull/8081) (`research/p104-expanded-budget-25bit/SETUP-PROOF.md`). The argument there is reused step for step. Only the numbers below change. As in #8081, this is an encoding and action-count bound, not a rate-admission condition, and it does not certify a new supplier price, native opening, product, activation, precision or portable execution trace.

**Scope.** The supplied profiles have two entry ordinary recipes, **5** terminal ordinary recipes and two Gaussian recipes, so 9 height records in all. Every ordinary height satisfies `8192 ≤ H < 2^27`. Both Gaussian heights stay below `2^25` (entry 1024, terminal 208653). The 127-bit scalar-encoding guard on κ, η and the stop denominator is unchanged and still enforced.

**Height-dependent paths.** As #8081 shows, the fixed constructor records `H` and `92H` for each ordinary recipe and creates the native value/calendar only when an active caller requests it. The one materialised height-dependent integer is the positive (Gaussian) carrier `1 << G`.

- For `H < 2^27`, `92H < 92·2^27 < 2^35`. So a lazily materialised `2^(92H)` would have fewer than `2^34 + 1` bits. That is below the source's individual datum bound `w = 2^38`, which is the same premise #8081 uses.
- The native control exponent `1024H + 3` is below `2^38`. It is a fixed-size scalar, never materialised by the constructor.
- Each positive carrier still has at most `2^25` bits, since `G < 2^25`.
- Each scalar compared or assigned by a recipe constructor (`H`, `92H` and the bounded metadata) has at most 34 bits. The per-recipe allowance of `2^24` elementary transitions stays conservative.

**Count.** #8081 charges two maximal carriers plus `2^24` transitions per recipe construction. With 9 recipes this gives

```
2·2048·(2^25+1) + 9·2^24 = 137589952512 < 2^40.
```

The added work therefore still fits in #8081's separate `2^40` allowance. With `n = 2^68 + 2^40` and the same `w`, `h`, `S`, `L` and `E`, the transition bound `(n+1)(L+E+2^120)2^32 < 2^228` is unchanged. `prepare.py` asserts each of these inequalities in the installed receipt.

**Cuts and entrance logs.** The stage cuts `(32000, 534986, 8486957, 134217724, 268435515)` exceed `2^27`, and the last one exceeds `2^28`. They are exponents that `entrance_logs` and `activation` compute and use as unbounded Python integers. Like #8081's, this lemma bounds only the height records that the fixed constructor stores. The same was already true at 25 bits: #8090's last cut, 67108923, exceeds `2^26`. No fixed-width descriptor in the installed source stores a cut. The old `bit_length() ≤ 20` assertion examined heights only, and this package replaces it with the height check above.

**What is not covered.** This note does not re-run #8081's `verify_setup.py` finite falsification at these exact bytes. A height of 2^27 or more needs a fresh bound.
