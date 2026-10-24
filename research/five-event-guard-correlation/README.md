# Five binary full-guard events are strictly below independent marginals

**Task:** independent-moment (original successor result). **Base:** canonical main `f626db5c`. **No κ is claimed.**

**Claim type:** scoped counting proof with an exact finite component. [PROOF.md](PROOF.md) has the argument.

For five pairwise orthogonal rank-one requests on F₂ᵐ and a uniform header in GL_m(F₂), let E_t be the event that every leading-minor guard of G P_t G⁻¹ through order m−1 passes. Then, for every m ≥ 5,

```text
Pr(E_1 ∩ … ∩ E_5) < s_m^5,   s_m = 3^(m−1)/((2^m−1) 2^(m−1)),
1 − ρ_m = 20 (7/9)^(m−1) + O((19/21)^(m−1) (7/9)^(m−1)).
```

This answers k = 5 of Open next question 2 in #4275. #4599 settles k = 4.

## Evidence

- **Exact signed spectrum.** It is computed over all 2²⁰ characters of the zero-diagonal 5×5 binary matrices. There are 62 bases, all positive, led by 243ⁿ − 20·189ⁿ + 60·171ⁿ.
- **Independent cross-checks of the table.**
  - direct meet-in-the-middle counts at n = 4, 5, 6;
  - the 2,880 complete headers at m = 6, matching #4598 and #4605;
  - the marginal law at k = 1;
  - the pair reduction against a brute force over GL₃ and GL₄ (k = 1, 3, 4);
  - a positive control of k = 4 below the product (#4599);
  - a one-unit table mutation is detected.
- **Two ranges.** For 5 ≤ m ≤ 118 there are exact rational comparisons. For m ≥ 118 a uniform tail bound from exact integer inequalities applies, with no unchecked interval.
- **Values.**

  | m | 6 | 8 | 20 | 40 | 118 |
  |---|---|---|---|---|---|
  | ρ_m | 0.0056 | 0.078 | 0.881 | 0.99895 | 1 − 3×10⁻¹² |

  The deficit ratio (1−ρ)/(7/9)ⁿ reaches 19.9995 at m = 118.

## Verify

```text
python3 -B research/five-event-guard-correlation/verify.py
```

It takes about 5 s and uses the standard library only.

## Limitations

- **Scope.** Only k = 5 is covered, with orthogonal kernels, F₂ and complete equally weighted headers. No all-k statement is made.
- **Not claimed.** A producer, selection, emission, dispatch, dirty restoration, stock, precision, a supplier or a κ change. Independent human or proof-kernel review has not been done.

## Open next questions

- **All k ≥ 4.** Bound the remaining negative spectrum uniformly in k. The second base 7·3^{k−2} carries sign −1 and multiplicity k(k−1). The third base is 19·3^{k−3} with sign +, which is 57 at k = 4 and 171 at k = 5. First step: tabulate the spectrum at k = 6, which has 2³⁰ characters and needs a vectorised or symmetry-reduced transform.

Credit: petalas (Nick Petalas) for #4275's character law and threshold framing, #4599's k = 4 method and #4598's m = 6 count. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
