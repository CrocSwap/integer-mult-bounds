# Independent proof check of #4532 §1.1, §2.2–2.3 and §3: the funded critical-root majorant

**Task:** independent-moment (independent source-bound coverage). **Base:** canonical main `f626db5c`. **No new κ.**

hexapode's #4535 (conditional κ = 0.003020165) rests on Dillon's #4532 theorem. Under the critical-root hypotheses, the finite compiler's normalised leaf count satisfies

```text
L(n) ≤ A n^(t*) (c + log n)^p,   A = n0^(1−t*)/(c + log n0)^p,   n0 = m·M^ℓ0.
```

My #4537 checked #4532's finite figures, and #4565 retuned the witness. This package checks the **written proof** of §2.2–2.3, step by step, in the form each step is used. The text is vendored as `PR4532-PROOF.md` (blob `bdf142f2`, SHA256-pinned), from #4535 head `a6d7237f`.

## Results

Every checked step holds. I found no gap.

| Step | What is checked | How |
|---|---|---|
| S0 | §1.1: `∫(S−E)dz/z = PT' − TP'` and `∫(S−E)z^(t−2)dz = (P(t)T(1) − T(t)P(1))/(1−t)`; strict slack gives a positive mean gap | exact finite sums over the actual p16 windows at seven exponents, 50-digit decimals |
| S1 | `(ln f)' = τ/x` and `f''/f = x^−2[τ(τ−1) − p/(c+log x)²]` | identity of rational functions in `(t, p, y = c+log x)` with `dy/dx = 1/x`, exact at 2,000 random rational points |
| S2 | `τ ≤ 1 ⟸ c ≥ p/(1−t*)`; `(f/x)' = f(τ−1)/x² ≤ 0`; `f(n0) = n0`, hence `L(n) = n ≤ f(n)` on the base range | 60-digit decimals on log-spaced grids `1…n0` |
| S3 | (11): `f(e)/f(n) ≤ (e/n)^τ(n)` for `1 ≤ e ≤ n` (from `log(1+y) ≤ y`) | grids above `n0` |
| S4 | (12): `f(n) − f(n−s) ≥ τ f(n) s/n ≥ η(τ) f(n)(s/n)^τ` for `n/m < s ≤ n`, including `s = n` | grids above `n0` |
| S5 | the recurrence closure: (10) bounds the exit charge by inner-source capacity | algebraic chain on 5,000 random potentials |
| S6 | `K_ℓ`'s derivative numerator `a(c + log m + log 2) + (a−1) log M`, and `n < m·M^(ℓ+1)` for `C_n = ⌊n/m⌋`, `ℓ = ⌊log_M C_n⌋` | exact rational identity; 17,118 exhaustive integer cases |
| S7 | monotonicity directions behind the endpoint evaluation in `critical_guards`: forward ratios, tilted means, every mirror cell sum and `η` nondecreasing; the root-tail and moment-ratio endpoint bounds; (6) `log q(t) ≥ d(t − t*)` from the crossing | the actual p16 profile on 121-point grids over each witness's cover interval |

| S8 | §3 lemma: the convexity bound `H(λ) ≤ μ_T − log q/λ`; (13) at the crossing; the sufficiency construction (`g = 2`, `j = 9`, so `a = b = 1`, `M = 512`) passing all three gates; necessity on 149 random passing gate samples | p16 profile, floats |

S2–S4 and S7 are run for **both** witnesses:
- #4532's p16 witness: `M = 1024`, `a = b = 1`, `ℓ0 = 650`, `p = 2/5`, `c = 133`, cover `.997067`;
- my #4565 retuned witness: `M = 2^24`, `a = 3`, `b = 2`, `ℓ0 = 64`, `p = 3/10`, `c = 101`, cover `.99725`.

**One remark, not a defect.** The proof bounds `log n < log m + (ℓ+1) log M + log 2`. The sharper `n < m·M^(ℓ+1)` (S6) shows the `log 2` is slack. Removing it would only enlarge `K_ℓ` slightly.

## Verify

```text
python3 -B research/pr4532-proof-check/verify.py
```

This runs in about 70 s with the standard library only.

## Limitations

- **Not re-proved.** The predecessor identities that #4532 imports from #4483 are not re-proved: the exact cancellation (2), the Chernoff bounds (7)–(9) and the mirror identity. My #4529 and #4551 check parts of them.
- **Not established.** Native, physical and outer premises are out of scope.
- **Finite checks.** The analytic inequalities are checked on finite grids, and S1 by exact evaluation at random rational points. Each is also a one-line calculus fact, given in the proof.

## Open next questions

- #4532 is now covered: §1.1, §2.2–2.3 and §3 here, plus §4's counterexample in my #4537. What remains open is #4532's own question, replacing pointwise mirror slack by a bound against the capped measure.

Credit: Dillon (#4532), hexapode (#4535), zxv and Jacob Alan Sussman (#4483 compiler and majorant lineage). Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
