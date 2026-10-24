# Independent check of #4554: root seeds and exact recovery (`ROOTS-RECOVERY.md`)

**Task:** independent-moment (independent source-bound coverage). **Base:** canonical main `f626db5c`. **No new κ.**

This completes my coverage of the native multiplier in Dugongue's #4554 (head `4f46c6a9`). #4557 checked the FFT error chain, assuming a root seed with coordinate error `< 2^−p`. This package checks that seed construction, and the CRT and carry recovery, against `ROOTS-RECOVERY.md`. The text is vendored as `PR4554-ROOTS-RECOVERY.md` (blob `5791526c`, SHA256-pinned). Nothing is imported from #4554's `root_seed.py` or `recover.py`.

## Results

All checked claims are confirmed.

**1. Root seed.** I implemented the construction from the spec text:
- `P = 8(p+16)`, `S = 2^P`, `K = 128(p+1)`;
- Machin π from floored alternating terms while `q^(2j+1) ≤ S` (at most `P+1` terms);
- `t = ⌊2A/D⌋`;
- `K` fixed-point complex Taylor steps with truncation toward zero;
- nearest rounding to `p` bits.

The checks:
- **Per-term rounding (12 runs, `p ≤ 4`).** Every term is compared with the exact rational Taylor term at `θ = t/S`. Each term's error stays within the recurrence `E_k ≤ (8/k)E_(k−1) + 1/S` and below `e^8/S`; the worst observed error is `6.9/S`. The summed error is at most `4096K/S`, with the worst run at 7.9·10⁻⁵ of that bound.
- **Machin and angle.** Against a separate AGM π, `|A/S − π| ≤ 20(P+2)/S` and `|t/S − 2π/D| ≤ [40(P+2)+1]/S` hold for `p ≤ 64` and `D` up to `2^40+87`.
- **Final error `< 2^−p`.**
  - 112 checks against exact algebraic values for `D ∈ {1, 2, 3, 4, 6, 8, 12}` and `p ≤ 128`. Values involving `√2/2` and `√3/2` are decided by integer square comparisons, so no transcendental code is involved.
  - 36 checks against a separate decimal reference for other `D` up to `2^40+87`.
- **Word budget.** Every intermediate stays below `2^(2P+20)`. The observed peak is about 283 bits for `p = 1`, inside the stated `2^(2P+17)` product bound of 289 bits.

**2. Lemmas, exactly.**
- The Machin tangent identity: `tan 2a = 5/12`, `tan 4a = 120/119` and `tan(4a − b) = 1`.
- `e < 11/4`, from the partial sum through `1/3!` and the `(1/24)Σ5^−j` tail, and `(11/4)^8 < 4096`.
- For every `p ≤ 4096`:
  - the tail ratio is `< 1/2`;
  - the last `K/2+1` factorial factors are all `≥ 128`;
  - `2^(−K/2−3) ≤ 32/S`;
  - `[40(P+2)+1+4096K+32]·2^(p+1) < S`.
- The factorial tail `2·8^(K+1)/(K+1)! ≤ 2^(−K/2−3)` itself is checked exactly at `K = 256`, 384 and 512.

**3. Recovery.**
- **CRT.** Garner CRT with Fermat inverses recovers all 23,800 coefficients exactly, both unsigned and signed. It runs on 300 random and extremal digit-array pairs with `β ≤ 2^16`, and the invariant `0 ≤ x < M` holds throughout.
- **Carries.** `t ≤ min(a,b)β(β−1)` and `carry ≤ min(a,b)(β−1)` hold. The carry invariant holds at every step, the final carry is zero, and every product is exact.

**4. Binding.** 7 statements are bound verbatim to the vendored text.

## Verify

```text
python3 -B research/pr4554-roots-recovery-check/verify.py
```

This runs in about 26 s with the standard library only.

## Limitations

- **Not checked:** the operation envelope `100(P+1)+40(K+1)` and the CRT setup costs. Only the structural facts behind them are checked: at most `P+1` Machin terms and `K` Taylor steps.
- **Finite checks.** The per-term error check uses exact rationals only for `p ≤ 4`; larger `p` are checked on the final error. The universal statement rests on the written recurrence, which these checks corroborate.
- **Out of scope:** the Gaussian adapters other than the banded inverse (#4556 covers that), the phase and exp tables, and the outer assembly.

## Open next questions

- An independent check of `PHASE-TABLES.md` and `NATIVE-EXP-TABLE.md`, the paid native phase and exp tables used by the Gaussian adapters. First step: replay their stated table precision against exact rational or algebraic references.

Credit: Dugongue (#4554). Machin (1706) and the standard Taylor and CRT methods; the method precedents the PR cites (#3877 and Mason Hale's interval backend). Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
