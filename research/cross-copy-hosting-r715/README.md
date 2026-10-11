# Cross-copy hosting on #472's R715 eleven-stage word: conditional κ ≈ 1.3725502·10⁻³

#448's cross-copy slot applied to #472's suppliers: chafreaky's R715 word with shared kernel, target mixing and
retimings in eleven compressed stages (bit), and #448's cross-copy hosted #433 word (complex). Neither local word nor
any schedule, isometry or bridge changes; only the owners of the helper residuals do.

**Result:** κ = 1372550159367980/10¹⁸ ≈ 1.372550159367980·10⁻³, bit-bound, **+6.23 % over #472** (1.2920996·10⁻³)
and +1.63 % over #469 (1.3505809·10⁻³).

| supplier | parent saving | this saving | hosted residuals (split) | max child |
| --- | --- | --- | --- | --- |
| bit, m = 78, R = 715, eleven stages, 8 replicas | 1.293771·10⁻³ | **1.374423·10⁻³** | 62,920 (14,612) | 56 |
| complex, m = 73, R = 560 (#448) | 1.437532·10⁻³ | 1.437532·10⁻³ | 40,320 (13,720) | 48 |

[PROOF.md](PROOF.md) gives the construction, the accounting and the scope.

## Verify

```sh
python3 -B research/cross-copy-hosting-r715/verify.py /absolute/new/output          # full
python3 -B research/cross-copy-hosting-r715/verify.py /absolute/new/output --quick  # skips only #443's inherited exhaustive controls
```

- The output directory must not exist. #472's parents need numpy, mpmath, sympy, a C++17 compiler and Boost
  headers (`BOOST_INCLUDE`); the new steps use the standard library (scipy only for `--discover`).
- It runs #472's complete `verify.py` (which rebuilds #458's complex supplier and the R715 composition), then both
  generators, the independent audit (fifteen mutation controls) and the exact assembly, and compares every value,
  the emitted-program digest and the complex template hash with `EXPECTED.json`.

## Scope and credits

Conditional, like its parents; the review point is #448's cross-copy slot. Builds on and runs unchanged: #472, #467,
#463 (R715 word: DreamingOfClouds), #458, #454, #451, #443–#445 (chafreaky), #442 (DaysSky), #450 (target mixing),
#441/#440/#436 (eumemic), #434 (Rohan Arun), #433 (icekylinx), #425/#386 (Zhihao Chen), #370 (Dylan Crow), Jacob
Sussman's E8 unit and interfaces. The cross-copy generators, audit and assembly were prepared by higherbeing with
Claude (Anthropic) assistance.
