# Proof map

| Claim | Status | Proof / check |
|---|---|---|
| (1) Padding: one-sided P112 decoder of cost c gives one-sided P120 decoder of cost exactly c+8 | proved; checked | Exactness: rows of P112 unchanged, row f_i = (2/mu)(mu e_i) = 2e_i for i in I, row f_j = 2e_j for j not in I, so P_E Y_E^T = C_E and q_k = C_E y_k (one-sided). Cost (rank B[R_k,A_k] = dim U_k - dim(U_k cap l(A_k)^perp)): non-corrected term unchanged (A_k grows, perp shrinks, U_k cap perp = 0 already); corrected term +1 (A_k gains f_i, l(A_k) = W_i + z_i = F_2^9, beta(z_i,z_i)=1); unit term exactly 1. Total c + |I| + (8-|I|) = c+8. Merging corrected terms with the same i is required first (an unmerged second term would also lose its epsilon, +1) and never raises cost (#2816 section 3.1). Check: `checks/pad.py` (5 decoders), `checks/pad_audit.py` (12 decoders incl. a split-correction decoder that exercises merging); both assert exactness over Q and equality of two cost computations. |
| (2) Lift form cost_w(S+) <= cost_w(S) + 8 - |I| | proved | Minimal basis of S extended by 0 keeps supports and weights; p_h^{E8} - ext(p_h^{X_I}) lies in span of delta_{f_j} (j not in I), each of weight 1. |
| (3) L120 suffices for the one-sided P112 floor 64+|I| for all I, i.e. Delta >= n_nf for all Delta | proved (sufficiency only) | (2) with the #2816 section 7 identity; no P120 decoder cost model is used on this route. Reading the corollary as "one-sided P120 decoders cost >= 72" additionally uses the dense-beta P120 cost model (imported, not covered by the P112-only theorem). Chain: Delta >= n_nf <= L120 <= [Delta + D <= 7 implies rho_0 <= Delta]; converse not claimed. |
| (4) delta delta^T padding is two-sided | proved | delta_{f_i} not in C(E8): codewords have |Off| >= 53. q = C_E 2e_j stays in col C_E. |
| L120 | OPEN | Residue: 38 OPEN rows of the #3049 ledger; 7 prior-only rows; 7 E6-slack rows; d=0 sliver Z = ker rho cap S nonzero with D >= 1, kappa <= 6. |

Checks cover the 12+ decoders: coordinate; root swaps k=1..4; basis changes; overcomplete m=11; shift decoders; split swap.
Related: #2816, #2826, #2862, #2985, #3049, #3029 (conditional only on L120 via this lemma).
