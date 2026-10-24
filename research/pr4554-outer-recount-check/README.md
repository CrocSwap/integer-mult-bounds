# Independent check of #4554: native outer assembly and Gaussian-map recount

**Task:** independent-moment (independent source-bound coverage). **Base:** canonical main `f626db5c`. **No new κ.**

This package checks two documents from Dugongue's #4554 (head `4f46c6a9`):
- `NATIVE-OUTER-ASSEMBLY.md`, the caller-tolerance theorem. A native cyclic transform with output error `δ = 1/(128L2^b)` gives exact multiplication in `O(F(L,n) + L)`.
- `NATIVE-RECOUNT.md`, the recount of the Gaussian maps, with its lattice tail, cost exponents and metadata lemma.

The texts are vendored as `PR4554-NATIVE-OUTER-ASSEMBLY.md` (blob `b9c54968`) and `PR4554-NATIVE-RECOUNT.md` (blob `300188c8`), with their SHA256 pinned. Nothing is imported from #4554's code. With #4556–#4560, this covers every constructive component of #4554 except `NATIVE-STABILITY.md` and `PHASE-TABLES.md` §2.

## Results

All checked claims are confirmed.

**Outer assembly.**
- **Exact inequalities.** For `L = 2^k` (`k ≤ 64`) and `b ≤ 16`, with `δ = 1/(128L2^b)`, three facts hold exactly (1,024 cases):
  - the product error `2L2^bδ + δ² + δ < 1/16`;
  - inverse inputs stay inside the domain, `(L2^b+δ)² + δ ≤ L^4 2^(4b)`;
  - the final budget `1/16 + 1/16 = 1/8`.
- **Assembly runs.** My own assembly uses a transform that satisfies the contract with deliberate perturbations: every forward output, pointwise product and inverse output is moved by modulus `δ(1−10⁻⁶)`, in coherent or random directions. It ran 16 times, for `n` from 254 to 65,534 bits on all-ones and random operands.
  - Every product is exact, with `2B ≤ L < 4B` and carries `≤ B2^b`.
  - The worst final real error is 6.2·10⁻⁵. These perturbations do not reach the analytic worst case; the guarantee rests on the exact inequalities above.
- **Corollary.** The exponent bookkeeping `L(log L)^(1−κ) ≤ n/(log n)^κ` for `L = n/log n` holds.

**Recount.**
- **Lattice tail.** `Σ_{|j−z|>R} e^(−a(j−z)²) ≤ 4e^(−a(R−1)²)/(1 − e^(−a(2R−1)))` holds for 4,000 random real centres, `a` and `R`. It is checked in ratio form, and the worst ratio is 0.26. The periodic budget derived from it falls below `2^(−P−1)`.
- **Radius selection.** Selecting `R` by doubling with rational squared comparisons meets both stated conditions in 36 cases (`π > 333/106`, `ln 2 < 0.6932`). The result stays within a factor 2 of the least admissible radius.

  **Note.** The second condition, `a(2R−1) ≥ ln 2`, gives `R = Θ(α²)` and binds only when `α` exceeds about `√P`. That is outside the source regime `α < √p`, so `R = Θ(α√p)` stands as stated.
- **Cost exponents.** With `d = p^ε` and `α² = d√p`, exact exponent arithmetic gives:
  - `h ~ p^(1/4−ε/2)`;
  - `dh ~ p^(1/4+ε/2)`, the stated adapter term;
  - `dp/α² ~ p^(1/2)`;
  - direct forward `~ p^(3/4+3ε/2)`.
- **Metadata lemma.** `next = (current−M) & M` enumerates every submask in increasing order, checked for all `M < 2^11`. A mixed-radix odometer with radices `≥ 2` makes at most `2T + d` digit changes (200 random cases).
- **Binding.** 9 statements are bound verbatim to the vendored texts.

## Verify

```text
python3 -B research/pr4554-outer-recount-check/verify.py
```

This runs in about 5 s with the standard library only. The assembly simulation uses double-precision FFTs, whose rounding is far below `δ`.

## Limitations

- **Not established here:** the transform hypothesis itself, a native cyclic program with `F = O(L(log L)^(1−κ)…)`. #4554 states that it is not supplied, and this package does not supply it either.
- **Assembly runs.** The perturbations are contract-satisfying samples, not a proof of the worst case.
- **Out of scope:** `NATIVE-STABILITY.md` and `PHASE-TABLES.md` §2.

## Open next questions

- An independent check of `NATIVE-STABILITY.md`, the rational Gaussian kernel and safe shear divisions. That is the last unchecked constructive component of #4554. First step: replay its stated recurrence on the #956 rational kernel in exact rationals.

Credit: Dugongue (#4554); the Harvey–van der Hoeven sources and #956's rational kernel lineage. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
