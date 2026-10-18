# Audit of PR1786's fine-prime transfer (no new kappa)

**No gap found in the audited scope. No new bound is claimed, and the selected record is unchanged.**

This is an independent check of the written transfer lemmas in
[PR1786](https://github.com/CrocSwap/integer-mult-bounds/pull/1786) (chafreaky,
"Conditional κ = 0.001679754788150048 from fine source-prime padding"). It answers
that package's Open next questions 1 and 2 for the explicit inequalities only.

| Audited text | Commit | SHA256 |
|---|---|---|
| `research/fine-prime-padding/FINE-PRIME-PADDING.md` | PR1786 head `c52345caa318fc6b1b6e2659c57d746317a72823` | `47d1b1b4df28aadda3cd6bdeb1fbc47290595e9208cd09c1a1f338520d33fdce` |
| `research/fine-prime-padding/vendor/pr1758/outer/GAUGEFREE-INTERIORS.md` (PR1758, byte-preserved) | same | `d1423ac0ea0003521797209f4396e6981a66994bbee4f8b48026e5b95f8c5116` |
| `research/capped-phase-fusion/LOG-A-PHASE-SCHUR-AUDIT.md` (PR1673) | PR1673 head `2569871ff906d2a2abfc86e97126ab9afe2e4a5a` | `e05d6b8596c80b6e8676569a0ff464a29fa704c3304143f58914f47cdf38b272` |
| `research/capped-phase-fusion/FORWARD-SMALL-A-AUDIT.md` (PR1673) | same | `e37aaa30b15671a1dff00676b14572213efaaac99df202dbba5e09f57af487c0` |

`verify.py` is written from the prose. It neither imports nor reads PR1786's
checkers, `LEDGER.json` or `CLAIM.json`. Exact rationals decide every PASS. Thresholds
marked INFORMATIONAL use floating point and are reported, not certified.

## Findings

1. **Section 1 (prime interval).** For `s` in `((1-2η)t, (1-η)t]` with `η = 1/(4p²)`,
   `θ = t/s - 1` lies in `(1/(4p²), 1/(2p²-1)]`, and `S/T > 1/2` whenever `d ≤ p`.
   Checked exactly for p = 2..2000. The Trudgian step is sound:
   - the main term is at least `ηx/log x`;
   - both endpoint errors are at most `2f(x)`, since `f` increases once `log y ≥ 2`;
   - at least `x/(8p² log x)` primes survive once `4.472 p² u^{1/4} e^{-√(u/6.455)} ≤ 1`, where `u = log x`.

   If `log x = c·p^(1-ε)` at ε = 0.9999999, that condition needs `ln p ≈ 4.3·10⁸`
   (3.8·10⁸ to 4.8·10⁸ for c from 100 down to 0.01). This is consistent with the PR's
   disclaimer that it claims no practical cutoff, and it quantifies the cutoff.
2. **Section 2 (conditioning).** The cited bounds do state the θ-dependence the transfer
   substitutes:
   - PR1673 LOG-A §1: `‖N-I‖∞ ≤ e^{-2aθ} + 5e^{-2a}` holds for every θ > 0. Only its
     numeric margin `1/(8p)` assumed `θ ≥ 1/(4p)`.
   - FORWARD-SMALL-A §1–2: explicit in θ for 0 < θ ≤ 1.
   - PR1758 §3: the accretive gap is `≥ θ/2` (narrow) and `≥ θ` (broad).

   The new margin `1/(8p²)` holds for every p ≥ 1, checked exactly to 5000; the argument
   is uniform in p.

   **Column analogue.** LOG-A does not write it out; §5's spectral norms need it. For
   column j and `G = q_j - q_i`, the exponent is `G(G + 2β_j)`. The two in-cell
   neighbours have `1 ± 2β_j ≥ 2θ` and these sum to 2, so
   `‖N-I‖₁ ≤ e^{-2aθ} + e^{-2a(1-θ)} + 4e^{-2a}`, the same polynomial gap. A Decimal
   fixture (p = 8, 3000 points, 12 cell cuts) gives a maximum row sum and column sum of
   0.7995, against the bound 0.8018. A control shows that the old `1/(8p)` margin really fails at the new θ,
   so the PR is right not to reuse it. The "eventually" steps start at p ≥ 1.05·10⁶
   (`e^{aρ/3} ≤ p²`) and p ≥ 1.9·10²³ (`a ≤ 5 log 16p`).
3. **Section 3 (setup vs online precision).** The bound `a ≤ 16⌈log₂ p⌉` holds for every
   p ≥ 3 (exact α to 4096; a continuous bound beyond). Then
   `2^{-P_setup} e^{a/(4θ)} < 2^{-Cp}` with slack factor 64 ln 2/16 ≈ 2.77 in the p² L_p
   term. Control: with C = 128, the old Cp-bit absolute weight precision rounds some
   weight to zero at every p in 32..4096, not only at the PR's p = 32 witness.
4. **Section 5 (locality).** The stated error `p^10 e^{-p²}` is sharp for the exact
   identity `H⁻¹ - σΣ_{j<J} Qʲ Hᵀ = Q^J H⁻¹`. A cruder geometric-series bound would give
   `p^30`, which is harmless anyway. The identity and the bandwidth `2W(J-1)+W` are checked
   exactly on a banded fixture. The exponents 40/42/43 sit below halo 48, which sits below
   core 128, and `128-48-β > 0`.
5. **Section 7 (ledger).** All nine rows were re-derived from the prose table:
   - the minimum is `εq`, and the boundary row equals main + 10⁻⁶⁴;
   - the Gaussian row exceeds main by exactly `δ(1-2q)`;
   - every side condition is positive, including the chirp guard `0.1841409904237`;
   - the headline is below `εq` and exceeds PR1758 by 9.279348·10⁻⁹.

   Controls that must fail, and do: the old `θ ~ 1/d` guard, a `θ ~ 1/p` guard,
   `β = 1-δ/2`, and `ε = 1`.
6. **Saturation of this outer on this supplier.** Along the whole family
   `ε = 1-δ, β = 1-3δ, ξ = ε(1+q) - 3/32 + s` (checked for δ = 10⁻⁴..10⁻³⁷), the binding row
   stays `εq < q`, where `q` is PR1699's certified complex endpoint
   `b_cert = 0.001679754956125544521335` minus 2·10⁻⁶⁴. No reparametrization of this
   nine-row ledger can reach `b_cert`. The remaining outer-only headroom is
   `(1-ε)q ≈ 1.68·10⁻¹⁰`. Larger gains on this line need a better certified complex
   supplier, which is the PR's own Open question 3.

## Not checked

- SHALLOW-TOEPLITZ and the accretive circuit theorem (PR1758 §4). Its proof is cited, not
  re-derived here.
- The derivation of each cost row's exponent.
- The union schedule and microbox layout.
- §4's normalization accounting, beyond the `O(d log p) = o(p)` arithmetic.
- The supplier admission (no native replay).
- The all-size compiler and every other inherited hypothesis that PR1786 lists.

## Reproduce

```sh
python3 scripts/research_package.py --package research/pr1786-fine-prime-transfer-audit --check-only
python3.12 scripts/research_package.py --package research/pr1786-fine-prime-transfer-audit
# or directly: python3 -B research/pr1786-fine-prime-transfer-audit/verify.py
```

The verifier is stdlib-only, runs in under one second, and passes on Python 3.10, 3.12 and 3.14.

## Open next questions

1. **Can the accretive Toeplitz theorem (PR1758 §4) be independently re-derived?** It is
   the largest cited input left unchecked. First step: check §4(a)'s quotient identity
   `(T_b/T_a)/(T_m/T_a) = T_b/T_m` and §4(d)'s recursion. Blocked only by reviewer time.
2. **Can the supplier endpoint be raised?** Finding 6 shows that is the only remaining
   lever on this outer line. First step: price candidate suppliers with the same paid
   moment. That requires a complete native word and admission.

## Credit

The audited mathematics is by Chafik Boukhalfa (PR1786, with OpenAI Codex assistance),
Vlado Vojdanovski (PR1673), and IdeaOuter and the PR1758 contributors. Tim Trudgian proved
the cited prime theorem. The supplier lineage is retained by PR1699. This audit was
prepared in a Claude Code (Anthropic Claude Opus) session donated by JosieElliston.
It is new work under Apache-2.0.
