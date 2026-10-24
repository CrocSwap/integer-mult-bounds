# Independent check of #4599: four binary full-guard events lie below the product of their marginals

**Task:** independent-moment (independent check). **Base:** canonical main `f626db5c`. **No κ is claimed.**

## The claim

petalas's #4599 (head `19ca650c`) concerns four pairwise orthogonal rank-one requests on F₂ᵐ and a uniform header in GL_m(F₂). It claims Pr(E₁∩E₂∩E₃∩E₄) < s_m⁴ for every m ≥ 4, where s_m = 3ⁿ/((2ᵐ−1)2ⁿ) and n = m−1. The proof has two parts:

- **m ≥ 85:** a spectral tail bound built from a signed character spectrum, printed in its §2;
- **4 ≤ m ≤ 84:** exact comparisons.

## Independent route

This route uses no #4275 character law and no #4227 marginal formula. Nothing is imported from #4599.

1. **Minor formula.** G P_t G⁻¹ = I − g_t h_tᵀ, so the order-j minor is 1 − Σ_{i≤j} h_t[i] g_t[i].
2. **Headers as pairs.** For k requests, passing headers are counted through X, the first k columns of G, and Y, the first k rows of G⁻¹. The count runs over pairs with YX = I_k whose first m−1 prefix sums have a zero diagonal. Each such pair extends to exactly |GL_{m−k}| headers, because the remaining columns are an ordered basis of ker Y.
3. **Exact count.** A dynamic programme over zero-diagonal k×k matrices computes these counts exactly. Each step is weighted by the number of factor pairs with disjoint supports. All arithmetic uses Python integers and fractions.

## Results (every m from 4 to 85)

- **Marginal law.** Pr(E₁) = s_m exactly, which independently confirms the marginal law.
- **Product inequality.** Pr(E₁∩…∩E₄) < Pr(E₁)⁴ strictly at every m. At m = 4 the joint probability is 0. At m = 5 it is 1/208,320, against a marginal of 81/496.
- **Spectrum table.** The direct joint count equals #4599's formula (N_n/81ⁿ)·H(X)·s_m⁴, built from its printed signed spectrum, at all 82 dimensions. **Failure control:** changing one multiplicity by one unit is detected.
- **§3 constants.** These are re-checked from the table:
  - the tail sum is 4,083 with largest base 57;
  - 4083·57⁸⁴ < 63⁸⁴, 9·9⁸⁴ < 14⁸⁴, 11·7⁸⁴ < 9⁸⁴ and 11·512 < 18·315;
  - H's numerator minus denominator is 11X² − 53X + 63.
- **Leading deficit.** (1−ρ_m)/(7/9)ⁿ is 9.33 at m = 20, 11.56 at m = 40 and 11.9947 at m = 85. This is consistent with the claimed limit of 12.
- **Brute-force anchor.** A brute force from the leading-minor definition over all of GL₃ and GL₄, for k = 1, 3 and 4, matches the dynamic programme.

## Verify

```text
python3 -B research/pr4599-four-event-check/verify.py
```

The check takes about 7 s and uses the standard library only.

## Limitations

- **Analytic range.** The m ≥ 86 range still rests on #4599's §3 argument applied to its spectrum. This package checks the spectrum's agreement with an independent direct count at 82 consecutive dimensions, and checks the §3 integer constants. It does not prove that the spectrum is the exact transfer spectrum.
- **Scope.** Only the stated setting is covered: four requests, orthogonal kernels, F₂, and complete equally weighted headers.

## Open next questions

- **The five-request inequality,** which is k = 5 of #4275's Open question 2. First step: run the same prefix dynamic programme with k = 5 over 2²⁰ zero-diagonal states. A vectorised or modular transform is likely needed for speed.

Credit: petalas (Nick Petalas) for #4599, #4275 and #4227. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
