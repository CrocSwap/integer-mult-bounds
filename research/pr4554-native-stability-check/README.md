# Independent check of #4554: native lowering of the closed rational Gaussian kernel

**Task:** independent-moment (independent source-bound coverage). **Base:** canonical main `f626db5c`. **No new κ.**

This is the last constructive component of Dugongue's #4554 (head `4f46c6a9`) that I had not yet checked, after #4556–#4561. `NATIVE-STABILITY.md` makes four claims:
- a fixed rational ADD/SCALE provider template has derived prefix norms;
- its fixed-point lowering has the stated roundoff and precision formulas;
- it instantiates to #956's closed Gaussian/Walsh provider (`m = 73`, `W = 58,899`, `θ = 1023/1024`);
- the two shear divisions of the cyclic compiler are quantitatively safe.

The text is vendored as `PR4554-NATIVE-STABILITY.md` (blob `86f98436`). #956's `PROFILE.json` at #956 head `fa4df77c` is vendored as `PR956-PROFILE.json` (blob `3bb4409c`). Both have their SHA256 pinned. Nothing is imported from either PR's code.

## Results

All checked claims are confirmed.

1. **Gate norms, exactly.** With `ā = |Re a| + |Im a| ≥ |a|`, over 3,000 rational complex `a` with denominators from {1,2,3,4,6,9}:
   - the 2×2 block of `x ← x + a·y` has largest squared singular value `≤ (1+ā)²`, decided by a rational eigenvalue test;
   - scaling is `≤ max(1, ā)`;
   - COPY has norm `√2`, and CLEAR `≤ 1`.
2. **Roundoff.**
   - **Programs.** 40 random rational ADD/SCALE programs (up to 40 gates, denominators 2 and 3), lowered with truncation toward zero at `P ∈ {12, 20, 30}` bits. Every one has error within the sum of local errors `√2·2^−P` transported through the product of suffix gate bounds; the worst ratio is 0.035.
   - **Formulas.** In 3,321 parameter cases, the precision formula `P` gives `√2A2^e(e+1)^θK^(D+1)2^−P ≤ 2^(−B−2)`, and the integral width `I` covers `K^(D+1)√(Z2^e)2^b` with three bits to spare.
   - **Walsh rescaling.** `|(1−i)^e|² = 2^e` exactly for `e < 200`, and the rescaling keeps the error `≤ 2^−B`.
3. **#956 instantiation.**
   - `m = 73`, `W = 58,899` and largest child rank 48 match #956's `PROFILE.json` as stated.
   - The integer-root certificate `r·u_r^1024 ≥ m·2^32768 > r·(u_r−1)^1024` holds at all 12 ranks.
   - The moment `μ = Σh_r·r·u_r/(W·m·2^32)` is `< 1` (gap 5.7·10⁻⁵), so `θ = 1023/1024` is funded.
   - The depth bound `D(e) ≤ 1 + ⌈log(e+1)/log(73/48)⌉` holds for the worst-case contraction `e → 48e/73` for all `e < 2000` and at `10^4…10^6`, even counting the leaf call as a level.
4. **Shear divisions.** Over 3,001 rational `μ` (including the extremal `μ = 1/2`) and 9,003 perturbations:
   - `t1 = 1+|μ|² ≥ 1` and `Re t2 = −[(a−1/2)² + b² + 3/4] ≤ −3/4` hold exactly;
   - `|t1' − t1| ≤ (2U+1)δ` and `|t2' − t2| ≤ (2U+2)δ`;
   - whenever `|Δt2| ≤ 3/8`, `|Δ(1/t2)| ≤ (32/9)|Δt2|`.
5. **Polyloglog absorption.** `max_x x^C e^(−(κ−κ')x) = (C/(e(κ−κ')))^C` is finite.
6. **Binding.** 6 statements are bound verbatim to the vendored text.

## Verify

```text
python3 -B research/pr4554-native-stability-check/verify.py
```

This runs in about 1 s with the standard library only.

## Limitations

- **Template constant `K`.** `K` is not computed from #956's literal template bytes. #4554 says it is computable but does not print a value, so the formulas are checked for `K ∈ {2, 3, 17}`.
- **#956's own theorem.** It is not re-proved. Only the profile constants and the moment certificate are recomputed.
- **Newton/Toeplitz preparation.** #4554 states that the cyclic compiler's Newton/Toeplitz preparation is not covered, and it is not checked here.

## Open next questions

- Compute the explicit prefix-norm constant `K` for #956's literal provider template, from its coefficient bytes. First step: read its fixed nonchild pass list and multiply the elementary gate bounds.

Credit: Dugongue (#4554); the #956 provider and its #390/Sussman/P193 lineage; ram_cost for the completion-of-squares shear argument, as credited in #4554. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
