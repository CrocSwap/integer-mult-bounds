# Independent check of #4554: native banded inverse and periodic Gaussian Woodbury reduction

**Task:** independent-moment (independent source-bound coverage). **Base:** canonical main `f626db5c`. **No new κ.**

Dugongue's #4554 (head `4f46c6a9`) replaces the Gaussian adapter arithmetic with native Word RAM constructions. This package checks one component, `NATIVE-BANDED-INVERSE.md`, against its text, vendored as `PR4554-NATIVE-BANDED-INVERSE.md` (blob `8be8f992`, SHA256-pinned). The component has three parts:
- a pivot-free band elimination with an explicit rounding error bound `1000H⁴u(‖b‖+1)`;
- a proved Gaussian tail and bandwidth choice;
- a rank-2h Woodbury reduction for the periodic wraparound.

Nothing is imported from #4554's `band_solve.py`, `periodic_solve.py` or `gaussian_inverse.py`.

## Results

All checked claims are confirmed.

**A. Band theorem.** Matrix arithmetic is exact over the Gaussian rationals; norms use complex absolute values.

The test matrices are near-identity complex band matrices with `ρ = 1/2`: 15 random matrices plus 5 adversarial real ones with every entry of `E` negative. Shapes are `(s, h) ∈ {(12,0), (16,1), (20,2), (24,3), (18,4)}`.

- **Exact elimination without pivoting.** Pivots are ≥ 1/2, surviving row sums ≤ 3/2, and multipliers ≤ 3. The solve satisfies `‖x‖ ≤ 2‖b‖`.
- **Rounded elimination: 60 solves.** Every multiplier, Schur entry and solved coordinate is rounded once with complex error `< u`, and dot products are accumulated exactly. Three values of `u` are used: the limit `1/(1000H²)`, `2⁻¹⁴` and `2⁻³⁰`. In every solve:
  - row sums stay `< 2`, pivots `≥ 1/4` and multipliers `≤ 8`;
  - `‖L̂Û − A‖ ≤ 6H²u`, `‖L̂‖ ≤ 9H` and `‖Û‖ ≤ 2`;
  - `‖ŷ‖ ≤ 8(‖b‖+u)` and `‖x̂‖ ≤ 4(‖b‖+19Hu)`;
  - the final error is at most `1000H⁴u(‖b‖+1)`. The worst observed ratio of error to bound is 8.8·10⁻⁵, consistent with the stated deliberately loose constants.

**B. Periodic Gaussian inverse.**
- **Summand and tail.** The per-summand distance `|r(ℓ−i)+β_i| ≥ d − 1/2` holds for `r > 1` (2,000 random cases). The tail `2Σ_{d>h} exp(−πα²d(d−1)) ≤ 4exp(−πα²h(h+1))` holds, in log domain, for `α ∈ [2, 6]` and `h ≤ 8`.
- **Choice of `h`.** The stated `h` gives a tail `< 2^(−P)/4` for `P ≤ 4096`. Together these make 5,346 checks.
- **Actual instances.** On 7 instances of `N` with `‖N − I‖ ≤ 1/8` (as low as `r = 1.1875`, where `‖N−I‖ ≈ 9·10⁻³`), using `h = 2`:
  - the row tails meet the bound;
  - `‖A − I‖ ≤ 1/4`;
  - every wraparound entry lies in the first or last h columns, so `A = A0 + UV`;
  - `‖A0 − I‖ ≤ 1/4`, `‖U‖ ≤ 1/4` and `‖S − I‖ ≤ 1/3`;
  - the Woodbury solve `x = y − Xz` satisfies `A x = b` **exactly** in rational arithmetic.

**C. Binding and replay.** 8 statements are bound verbatim to the vendored text. I also replayed #4554's registered package at its head: `PASS_REGISTERED_RESEARCH_PACKAGE research/native-word-fft outcome=completed` in 16.6 s.

## Verify

```text
python3 -B research/pr4554-banded-inverse-check/verify.py
```

This runs in about 16 s with the standard library only.

## Limitations

- **Out of scope:** the rest of #4554 (roots and recovery, phase and exp tables, native stability, outer assembly), and the source estimate `‖N − I‖ ≤ 2^(−α²θ)`, which is a predecessor fact. This package only checks that its test instances lie in that regime.
- **Floating-point norms.** Instance entries of `N` and all norm comparisons use floats. Matrix arithmetic and the Woodbury identity are exact.
- **Finite checks.** The universal statements rest on #4554's written induction, which these finite checks corroborate.

## Open next questions

- An independent check of `NATIVE-STABILITY.md` or `ROOTS-RECOVERY.md`, the other precision-carrying components of #4554. First step: an exact-rational replay of their stated per-step error recurrences.

Credit: Dugongue (#4554); the Gaussian resampling construction and the Harvey–van der Hoeven sources it cites. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
