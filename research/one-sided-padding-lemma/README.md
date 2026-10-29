# One-sided padding lemma: P112 to P120 (no kappa claim)

Statement and a two-implementation check; nothing here claims a kappa improvement.

**Lemma (padding).** Every one-sided P112 decoder (case (b)) of cost c becomes a one-sided P120 (E8) decoder of cost exactly c + 8: after merging corrected terms with proportional y, for each frame line f_j with j not in the corrected set I add the term (delta_{f_j}, y = 2e_j); for i in I the corrected term gets p_k(f_i) = 2/mu. The new q = C_E * 2e_j is the E8 frame codeword, so the decoder stays one-sided.

**Lift form.** S containing the code of X_I gives S+ (extend by 0 on f_j, j not in I, plus the unit vectors delta_{f_j}) containing C(E8), with cost_w(S+) <= cost_w(S) + 8 - |I|.

**Consequence (sufficiency only).** L120 (every lift S containing C(E8) has cost_w >= 72) suffices for the one-sided P112 floor 64 + |I| for every I, i.e. Delta >= n_nf for all Delta, using only the #2816 section 7 identity (corrected cost = cost(X_I) - |I|). The converse is not claimed. This makes the conditional in #3029 conditional on L120 alone.

**Remark.** Padding with delta delta^T is two-sided: delta is not a codeword (codewords have |Off| >= 53), so it enlarges col Q. The earlier remark that the reduction "does not transfer" referred to that two-sided padding.

**OPEN (L120).** Not proved. Residue: the 38 OPEN rows of the #3049 ledger (one d=4 [7^5,4]; one d=6 [7^7,6]; four d=7; 32 d=8), the 7 prior-only rows (killed only by prior arguments), the 7 E6-slack rows (E6-cover rows, conditional), and the d=0 sliver Z = ker(rho) intersect S nonzero with D >= 1, kappa <= 6.

Cites: #2816, #2826, #2862, #2985, #3049, #3029.

Run `bash verify.sh` (needs `sympy`; `PYTHON=/path/to/python`). Runtime about 2 s. `PROOF_MAP.md` maps each claim to its proof and check.
