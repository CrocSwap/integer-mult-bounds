# NumCertK.lean + NumCertKData.lean + NumCertK22.lean: kernel-checked interval arithmetic; NumCert22 discharged
No sorry, no native_decide; axioms [propext, Classical.choice, Quot.sound] (all three files). Build order: NumCertK (13 s / 2.9 GB), NumCertKData (32 s / 3.4 GB), FloorK22, NumCertK22 (7 s / 2.9 GB); each with `-o .lake/build/lib/lean/Nov15/<F>.olean`. NumCertK22 is a separate file only because importing FloorK22 + the checks in one run exceeds the 3.5 GB guard.

## Library (NumCertK.lean, Mathlib only)
- ln: chain ln(c+2) = ln(c+1) + 2 atanh(1/(2c+3)) from `Real.hasSum_log_one_add_inv`, 36 terms, explicit geometric tail (`atanh_bounds`), outward rounding to 1e-30 (`rdn`/`rup`). `lnLo r <= ln r <= lnHi r`, r >= 1; accuracy ~1e-28 for r <= 145.
- exp: (Taylor_24(x/8))^8 with `Real.exp_bound'` remainder, outward rounding (`eLo_le`: 0 <= x; `le_eHi`: 0 <= x <= 8).
- **`pow_lo`**: 1 <= r, 0 <= a <= s => pLo r a <= r^s.  **`pow_hi`**: 1 <= r <= 145, s <= b <= 1 => r^s <= pHi r b.  (s-form: s = 1 - t, so r^(1-t) in [pLo r (1-t_hi), pHi r (1-t_lo)].) Rational, checked by `decide +kernel`.
- F(s) = sum c_r r^s (`Fc`): `Fc_le` (upper enclosure `Fup` on [a,b]), `dFc_ge` (lower enclosure `dLo` of F'), `Fc_hasDerivAt`, `Fc_mono` (dLo > 0 on [a,b] => F(s) <= F(b)).

## Crossing for K(S22) (NumCertKData.lean, NumCertK22.lean)
- `cfK`: the 17-call invoice caller(6|7) + 17 x nK22, merged by rank: 24 ranks, c_1 = -42272, c_2 = 6494, ..., c_137 = 208 (`invoice_eq_Fc`, simp + ring: identical to the Finv of FloorK22).
- `cfK_neg`: F(s) < 0 for every s in [0, 9939802595/10^10 = 1 - .0060197405]. Proof: six `Fup` boxes cover [0, .9] (grid 0, .45, .6, .7, .8, .85, .9; F <= -3.3e3 at worst); on [.9, s0] one box gives dLo >= 2.5e4 > 0, so F(s) <= F(s0), and the point enclosure gives Fup(s0, s0) < 0 (true F(s0) = -4.83e-6, relative margin 1e-10 of the 2.8e4-sized terms, so the 1e-28 enclosure is ample).
- **`numCert22 : NumCert22 tbar22`** and **`ceiling22_unconditional`**: kappa <= .0060197405 on class K(S22) with NumCert22 discharged; other hypotheses of `ceiling22` unchanged (ClassK22 rank input, cost-model link `hF`).
- The crossing is TRUE: F(1 - .0060197405) = -4.83e-6 (root .00601974047925), F' = 2.33e5 there.

## Not done
- JointCeiling's `NumCert th0 tbar`: it quantifies over ALL a, b >= 1 (R1 tail Jensen/MVT step, ~1,800 pairs, unaudited per its docstring); the library applies per (a,b) but the infinite tail is not an interval check. WholeFloor's (kappa <= .0204) was not available.
