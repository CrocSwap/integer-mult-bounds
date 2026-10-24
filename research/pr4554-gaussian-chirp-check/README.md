# Independent check of #4554: stable Gaussian block maps by one paid convolution

**Task:** independent-moment (independent source-bound coverage). **Base:** canonical main `f626db5c`. **No new κ.**

Dugongue's #4554 (head `4f46c6a9`) evaluates Gaussian resampling blocks `W[x,y] = exp(−a(ux − vy + c)²)` with a diagonal–Hankel–diagonal factorisation, so each block costs one linear convolution. The supporting results are:
- conditioning after centring each block (A);
- a precision rule (C) that implies the block error bound (B);
- a blocking geometry (Theorem 3).

This package checks `GAUSSIAN-CHIRP.md`, vendored as `PR4554-GAUSSIAN-CHIRP.md` (blob `4e31f302`, SHA256-pinned). Nothing is imported from #4554's `chirp_check.py`, `gaussian_block.py` or `native_convolution.py`. It follows my #4556–#4559 on the same PR.

## Results

All checked claims are confirmed.

1. **Theorem 1.**
   - `log D[x] + log E[y] + log H[x+y] = −a(ux − vy + c)²` holds as a polynomial identity in ℚ[a,u,v,c,x,y].
   - `Σ_y W[x,y]Z[y] = D[x]·(H ∗ reverse(E·Z))[x+l−1]` holds, with an explicit **linear** convolution, at 60 digits on 40 random rectangles (`m, l ≤ 7`).
2. **Conditioning (§2).** With `Cp := a(|u|q+|v|q+|c0|)²`, every exponent of D, E and H is at most `Cp` in absolute value. This is checked exactly in rationals on 300 random parameter sets, with signed `u`, `v`, `c0` and `q ≤ 24`.
3. **Blocking geometry (§4).** Brute force over 120 random rational geometries (3,522 retained blocks):
   - each row block keeps at most `K = ⌈(u(q−1)+2R)/(vq)⌉ + 3` column blocks;
   - every retained block has `|c0| ≤ R+(u+v)(q−1)`;
   - (D) implies (A).

   The tail rule `aR² ≥ (p0+⌈log₂(sX+1)⌉+2)ln 2` keeps the omitted row mass below `2^−p0/2` (116 cases).
4. **Precision rule.** (C) implies `(B) ≤ 2^(−p0−4)` in all 576 parameter cases, using only `log₂e < 2`.
5. **End-to-end block.** I wrote my own fixed-point evaluator at the `P` that (C) prescribes:
   - chirps and twiddles on the `2^−P` grid;
   - nearest-rounded complex products;
   - linear convolution through a radix-2 FFT of size `N0 = 4q`, then division by `N0`;
   - selection at `x+l−1` and multiplication by `D`.

   Against a direct 120-digit sum, all 6 runs (`q ∈ {8, 16}`, with the conditioning scale `p` up to 52) have error far below `2^−p0` and within (B). Observed errors are about `2^−331` at `P = 512` and `2^−219` at `P = 234`.

   **Observation.** (C) is valid but conservative. The observed precision loss is about 180 bits at `p = 52`, against the roughly 484 bits that (C) reserves above `p0`. The `8⌈C⌉p` term, sized for `M⁴`, dominates the rule.
6. **Binding.** 7 statements are bound verbatim to the vendored text.

## Verify

```text
python3 -B research/pr4554-gaussian-chirp-check/verify.py
```

This runs in a few seconds with the standard library only.

## Limitations

- **Exp table.** The exp table that generates `D`, `E` and `H` is checked separately in #4559. Here the chirps come from a decimal reference rounded to the grid, which matches the `2^−P` interface of (B).
- **Cost.** Theorem 3's operation count is not re-counted. Only its geometric inputs, `K`, `|c0|` and (D), are checked.
- **Finite checks.** These are finite and random checks of universal statements whose proofs are written.

## Open next questions

- A sharper precision rule than (C). The observed loss suggests that something like `2Cp·log₂e + O(log q)` guard bits suffice. First step: redo the (B) derivation, tracking `M` powers separately for the forward and inverse transforms.

Credit: Dugongue (#4554); the Harvey–van der Hoeven Gaussian resampling sources; classical chirp/Bluestein convolution. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
