# Independent check of #4554: native FFT multiplier error chain and parameters

**Task:** independent-moment (independent source-bound coverage). **Base:** canonical main `f626db5c`. **No new κ.**

Dugongue's #4554 (head `4f46c6a9`) gives a native bounded-word FFT multiplier. `PROOF.md` sets its parameters, and `FFT-ERROR.md` proves a recovery error of at most `216N⁶β²/S < 2^(−10ℓ−6) < 1/4`. This package checks both. They are vendored as `PR4554-PROOF.md` (blob `c7b4777b`) and `PR4554-FFT-ERROR.md` (blob `53691b10`), with their SHA256 pinned. Nothing is imported from #4554's `native_fft.py`, `root_seed.py` or `recover.py`. It follows my #4556 on the same PR.

## Results

All checked claims are confirmed.

**A. Error chain, in exact rational arithmetic.** The recurrences are run with equality, as the worst case, for `N = 2^h` (`h ≤ 20`) and `β = 2^b` (`b ≤ 8`), at `S = 2^F` with `δ = 32N/S` and `η = 4/S`. That is 80 cases.
- **Forward amplitudes.** They stay below `4^j(β+η/3) ≤ 2·4^jβ`.
- **Forward errors.** They stay below `δβN(N−1) + η(N−1) ≤ 36N³β/S`, which is (1).
- **Pointwise products.** The error is at most `112N⁵β²/S` (2), and the computed modulus is at most `5N⁴β²` (3).
- **Inverse transform.** Amplitudes stay at most `6·4^jN⁴β²`, and the final error before normalization is at most `212N⁷β²/S`.
- **Normalized output.** The error is at most `216N⁶β²/S` (4), which is at most the envelope (5). The worst recurrence value is 0.196 of (4), as expected for a bound proved with loose amplitudes.
- **Twiddles.** The recurrence `a_(j+1) = (1+2δ)a_j + 4δ` stays at most `8jδ` (3,000 steps). Analytically, `2((1+x)^j − 1) ≤ 2(e^(jx) − 1) ≤ 4jx` when `jx ≤ 1`.
- **Parameters, exact integers, at the largest `n` for each `ℓ = 2…200`.**
  - `N < 4L ≤ 4n < 2^(ℓ+2)` and `F+1 ≤ 2^(ℓ+7)`;
  - `2^28 N^8 (F+1)^2 β^4 · 2^(10ℓ+6) < S`;
  - `δ, η < 1`;
  - the raw-product budget is within `2F + 6⌈log₂N⌉ + 2b + 8 ≤ 16(F+16)+20`.

**B. A separately written fixed-grid multiplier** following the `PROOF.md` construction. Its steps are:
- **Root.** π by Machin, cos and sin by Taylor at `F+64` bits, then floored to the `2^−F` grid.
- **Transforms.** Twiddles come from successive floor-rounded complex products, and forward twiddles are conjugated. Two forward FFTs are followed by rounded pointwise products, an unnormalized inverse and floor division by `N`.
- **Recovery.** Each coefficient is rounded to the nearest integer, and carries propagate in radix `β`.

It ran 367 products: all pairs for `n ≤ 4`, plus random and all-ones operands up to `n = 12,000` bits. All are exact, checked against Python's multiplication, which is used as the oracle only.
- **Observed error.** The worst observed coefficient error is **5.7·10⁻⁷ of (4)**, always `< 1/4`.
- **Magnitudes.** Inverse magnitudes stay below `6N⁶β²·S`. Carries stay at most `L(β−1)`, and the final carry is zero.
- **Word width.** Every stored magnitude is below `2^w` with `w = 16(F+16)+20`. The FFT itself uses at most 12% of that width, since the width is set by the root routine, as the PR says.

**C. Binding and replay.** 12 statements are bound verbatim to the vendored texts. #4554's registered package replays at its head (`outcome=completed`, 16.6 s; see #4556).

## Verify

```text
python3 -B research/pr4554-native-fft-check/verify.py
```

This runs in about 16 s with the standard library only.

## Limitations

- **Root precision.** `ROOTS-RECOVERY.md`'s universal root-precision proof is not re-derived here. My root is computed independently and is only required to meet the same `< 2/S` seed premise.
- **Operation ledger.** The operation-count ledger and `O(n)` cost are not re-counted.
- **Other components.** The Gaussian adapters, phase tables and outer assembly are out of scope; #4556 covers the banded inverse.
- **Finite checks.** Part B is a finite family. The universal bound rests on the written recurrences that part A checks.

## Open next questions

- An independent check of `ROOTS-RECOVERY.md`, covering root-seed precision with the Machin and Taylor truncation and the `O(F)` cost. First step: certified truncation bounds for both series at precision `8(F+16)`.

Credit: Dugongue (#4554); Fürer (2014) for linear Word RAM FFT multiplication. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
