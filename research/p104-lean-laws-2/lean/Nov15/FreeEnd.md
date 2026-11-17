# FreeEnd: FLOOR3 collapse, kernel-checked
File: Nov15/FreeEnd.lean (imports V2Bridge). Axioms: propext, Classical.choice, Quot.sound; no sorry.
- `chD0_eq_sum_w0`: ascending chain a -> ... -> b: chD0 (D0, f = r ln r) = sum_moves w0 th (dim tail)(dim head) - w0 th (dim a)(dim b), every th.
- `chD0_nonneg`: D0 >= 0 on every ascending chain. `oneMove_D0`: born at L, one MOVE to U, dim L < dim U => D0 = 0.
- `floor3_collapse`: for any pair list with dim L < dim U, the one-move helpers realise each pair, total D0 = 0, and 0 lower-bounds every ascending-chain family: relaxation optimum = 0.
## PAPER SLIP (stated at once)
"Sum w0 - corr = 0" is FALSE as written: corr = w0 + rho(d0) - rho(e) includes the potential. Correct: sum w0 - w0(d0,e) = D0 (corr-free); with full corr, `sum_w0_sub_corr`: sum w0 - corr = D0 + rho(e) - rho(d0). Counterexample `slip_counterexample`: theta = 1, one move 1 -> 2: w0 - corr = -B1 < 0 (B1 > 0, `B1_pos`). FLOOR3.md itself uses the corr-free form (cost = sum w0 - w0(d0,e)), so its conclusion (relaxation value 0) stands; only the "- corr" phrasing is wrong. Consistent with chD0_bound: sum wcut <= D0 + corr.
