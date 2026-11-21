# DEN4 (Nov 20, Opus, theory + exact checks). Own code in this dir. venv python, 1 proc, threads=1. No Lean, no SAT, no advisor.
Why this is not a retread: HC, ORBITLP §3, D56, TAU and NG all assume 2-adic valuation >= -1. TAU §4 only named the mod-8 problem.
This lane proves the carry identity and the rank bound for every 2^e at once, then measures them on quarter decoders (HS64, E7, P104, P120).

## 0. Verdict
- [P] CARRY-POLYNOMIAL IDENTITY, any e, any rows (mixed valuations allowed), any label set. It is uniform in e.
- [P] RANK BOUND: C >= rank_F2(x) P(x). From the forced coefficients alone: C >= rank T_{e+1} - rank T_e (block Toeplitz).
  - e = 1 gives exactly C >= rank(I+X), the doubling lemma.
  - e = 2 gives C >= rk X0 + rk((I+K2) restricted to leftker X0 x rightker X0).
- [P] DEEP-PORT LEMMA, any e. It generalises the O-form and split decoders (C >= n).
- [P] Graded Smith floor for 2^e. This is the first general-model quarter floor, and it is weak: HS64 6, E7 7, P104 8.
- [C] Half-spin quarter decoder (C = 48): the forced bounds give 38 in the canonical gauge and 42 at the gauge maximum.
  - Every identity-forced law plateaus at 42 there.
  - PORTWALL(8) needs 38, so on the optimal decoder there is slack (42 vs 38). The complementary-slackness filter does NOT forbid slack laws here, unlike Wall56.
- NOT proved: any decoder-independent quarter floor above 8. The obstruction is the same as for halves: control of the carries K_l (tau_{2^l}-forms).

## 1. Setting (port-general)
- Q is the 0/1 odd-cell matrix (diagonal included). Rows are (w_k, u_k), with M o Q = I. The price is r_k = rank_F2 Q[D_k,S_k].
- Rescale each row by powers of 2, so that w_k and v_k are 2-integral and sum_k D(w_k) Q D(v_k) = 2^e I on Q-cells. Odd denominators are units.
- Digits: a_k^i and b_k^j are the binary digit vectors of the residues of w_k and v_k mod 2^(e+1).
- Ĝ_ij = sum_k (a_k^i b_k^jT) o Q is an integer count matrix. G_ij is Ĝ_ij mod 2.

## 2. Theorem 1, the carry identity [P]
- Let P_l = sum_{i+j=l} G_ij and K_l = floor( sum_{i+j<l} 2^(i+j) Ĝ_ij / 2^l ) mod 2.
- Then P_l + K_l = [l = e] I for 0 <= l <= e, on Q-cells. Also K_0 = 0, so P_0 = 0 (the cancellation law).
- Proof: let S_l = sum_{i+j<l} 2^(i+j) Ĝ_ij. Then S_{l+1} = S_l + 2^l Ĝ_l, and S_{e+1} ≡ 2^e I mod 2^(e+1).
  Bit l of S_{l+1} is (floor(S_l/2^l) + Ĝ_l) mod 2 = K_l + P_l, and later terms do not touch bit l. ∎
- e = 1: K_1 = X, so P_1 = Y + Z = I + X. This is HC.
- e = 2:
  - level 1: G01 + G10 = K1 = X0 (= Ĝ00/2 mod 2). No I appears here.
  - level 2: G20 + G11 + G02 = I + K2, with K2 = floor((Ĝ00 + 2Ĝ01 + 2Ĝ10)/4) mod 2.
- Sign rows (entries ±1, the case of HS64, P104 and E8): -1 = ...111, so a^2 = a^1 = s (the minus pattern).
  - The quarter identity reads G[s,b] + G[a,s'] = X0 and G[s,b] + G[s,s'] + G[a,s'] = I + K2.
  - Equivalently, in counts: delta = bit2(c) + bit1(c_-). Here c is the cover count and c_- the negative-cover count, so the I lives in second-order carries.
- [C] The identity was checked exactly at every level l <= e on 30+ decoders with e = 1..4 (asserts in carrypoly.analyse).
  Negative control: 20/20 one-entry perturbations of the HS decoder fail it.

## 3. Theorem 2, the rank bound [P]
- Let P(x) = sum_k D(a_k(x)) Q D(b_k(x)) over F2[x], with a_k(x) = sum_i x^i a_k^i.
  Each term factors through Q[D_k,S_k], so its F2(x)-rank is <= r_k. Hence C >= rank_F2(x) P(x) = sum_l x^l P_l.
- Forced part: Smith form over F2[[x]] gives rank T_s = sum_i max(0, s - nu_i). So rank T_{e+1} - rank T_e = #{nu_i <= e} <= rank P <= C.
  T_s uses only P_0..P_{s-1}, and all of these are forced by Theorem 1. ∎
  - e = 1: T_2 - T_1 = rank(I+X), the ORBITLP doubling.
  - e = 2: rank [[X0, I+K2],[0,X0]] - rk X0 = rk X0 + rk( (I+K2) | leftker X0 x rightker X0 ) (Marsaglia–Styan).
  - So if the half-carry X0 vanishes, C >= rank(I + K2). In general C >= rank(I+K2) - rk X0.
- Consistency [C]: E8-56 gives 56 = C at e = 1. It also gives 56 when re-normalised at e = 2 (v -> 2v), and 56 at e = 2 with mixed per-row scalings.
  The bound is invariant under row 2-power rescaling (w(x) -> x w(x), v(x) -> v(x)/x).
- Gauges: w_k(t) -> lam_k mu_t w_k(t) and v_k(t) -> (lam_k mu_t)^-1 v_k(t), with 2-adic units, leave the decoder unchanged but change P(x). The max over gauges is valid.
- Quarter master form [P]: C >= rank [[G[a1,b], G[a1,b1]],[0, G[a,b1]]]. This is a 2-stack, so the lower-left block G00 = 0.
  - For sign-like rows (residues {0,±1,-2} mod 8), block ops turn the top-right block into I + K2. So C >= rank[[Y, I+K2],[0,Z]] with Y + Z = X0.
  - For general rows there are extra terms: ε-digit form T = I + K' + Δ4, where Δ4 = G[c,b] + G[a,d] counts only residues ≡ 4,5 mod 8 (checked exactly).
  - Neither the master form nor Toeplitz dominates the other (table below).

## 4. Lemma 3, deep ports [P] (any e)
- Let mu(t) = min_k v2 w_k(t) and nu(t) = min_k v2 v_k(t). Then mu + nu <= e (diagonal).
- Call t DEEP if mu(t) + nu(t) = e. Then C >= #deep.
- Proof: divide row t of P(x) by x^mu(t) and column s by x^nu(s) to get P''(x).
  - At x = 0 on deep x deep: an entry with mu(t) + nu(s) <= e is the bit at level mu(t) + nu(s) with no lower terms possible, so it equals delta_ts.
  - An entry is unforced only if mu(t) > mu(s). So the matrix is unitriangular in mu-order, and rank P'' >= #deep. ∎
- e = 1: this is the ORBITLP O-form (non-O ports) and the split-decoder theorem.
- [C run6/deep.py]: 12 decoders with e = 3..5, 0 forced-entry violations. Deep ports are rare in practice (0-3).

## 5. Graded Smith floor for 2^e [P] (general model, no rank hypothesis beyond the price)
- bit0(c) = sum_{S≠∅} (-1)^(|S|+1) 2^(|S|-1) prod_{rho∈S} x_rho. So Q_k ≡ (a sum of sum_{j<=e+1} C(r,j) rank-1 integer matrices) mod 2^(e+1).
- ADICWALL step 2 therefore gives n <= sum_k sum_{j=1}^{e_k+1} C(r_k, j).
- The worst ratio is at r = h. So C >= n h / (h + C(h,2) + C(h,3)) for quarters:
  - HS64 (h=8): >= 6 (halves: 15)
  - E7 (h=7): >= 7
  - P104 (h=9): >= 8 (halves: 21)
- General e: denominator sum_{j<=e+1} C(h,j). As e -> ∞ this tends to the Hadamard bound 2^h - 1.

## 6. Numbers [C exact; C = true cost; "gauge" = hill-climbed max of Toeplitz over unit gauges]
| decoder | n | e | C | Toeplitz canon. | Toeplitz gauge | master2 | need (PORTWALL) |
|---|---|---|---|---|---|---|---|
| HS64 D8-frame (optimal) | 64 | 2 | 48 | **38** | **42** (3 seeds × 150 steps; master also 42) | 42 | 38 |
| HS64 random Gram | 64 | 2/3/4 | 60/61/64 | 46/43/35 | 46/49/44 | 56 (e=2) | 38 |
| E7 basis decoder (optimal 49) | 63 | 1 | 49 | 45 (= rank(I+X)) | 45 | – | 41 |
| E7 basis decoder | 63 | 2 | 49 | 44 | **48** | 34 | 41 |
| E7 random Gram | 63 | 2/3/4 | 56 | 44/44/47 | 44/51/50 | 45 | 41 |
| P104 Gram, quarters | 104 | 2 | 71-72 | 59-69 | same (30 steps) | 43-50 | 56 |
| P104 E8-56 (halves) | 104 | 1 (and as 2) | 56 | 56 | – | – | 56 |
| P120 random Gram | 120 | 2/3 | 72 | 70/63/71 | 70/70/71 | 68 | – |
- Plain stack rank with FREE y,z reaches C = 48 on HS even with a 1-stack (stack.py), so a free stack bound alone says nothing.
  Only digit-derived (gauge-covariant) choices are identity-forced.

## 7. What it means / general 2^k
- Uniformity: every denominator 2^e has the same law. A decoder is a polynomial matrix P(x) whose first e+1 coefficients are (0, K_1, ..., K_{e-1}, I+K_e), and C >= its F2(x)-rank.
  There is no new mechanism per level. The only unknowns are the carries K_l.
- The carries are the tau-forms: K_1 = tau (entry sum/2) and K_2 = tau_4-type (bit 2 of the signed cover count).
  The D56 isotropic-pair lemma bounds K_1. A K_2 analogue must work on leftker X0 x rightker X0 (Theorem 2, e = 2), i.e. three-level Rado spaces exactly as TAU §4 guessed.
- For PORTWALL(8) (HS64) and PORTWALL(7) (E7) the needed thresholds (38, 41) sit BELOW the forced bound on the optimal decoders (42, 48).
  So a proof may use slack laws. The task is "forced bound >= 38 for all decoders", which is a tau_4-isotropic statement [CONJ, unexplored].
- Next: (i) the quarter isotropic-pair lemma (bound rank of (I+K2) on ker X0 via tau_4 on even-even blocks); (ii) Lean the e-uniform identity + Toeplitz bound (short: carry recursion + Smith over F2[[x]]); (iii) gauge-min search of the forced bound over Gibbs-type quarter walks on HS64 (exact moves exist mod 8 as in TAU gibbs.py).
FILES: qlib.py, quarter.py (ε-form identity, master2), carrypoly.py (Thm 1, Toeplitz, F2(x) rank via gf.py), gauge.py, stack.py, deep.py, run1-6.py, verify.sh.
