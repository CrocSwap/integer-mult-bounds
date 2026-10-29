# BUDA11 — the AUDIT-IMP open cell of BUD-A (m = 11, (s,t) = (1,1), n01 = 2) (Oct 16)
Labels PROVEN / CHECKED (two implementations: chk1.py = TWINSWAP lib coords; chk2.py = AUDIT-IMP ind_e8.py independent E8 rebuild, own elimination) / OPEN.
python = W/venv/bin/python. Logs chk1.log, chk2.log. Imports: WALL 8.2/8.3 (AUDIT-IMP PROVEN), WALL §2 structure, the sound P2 form (AUDIT-IMP).

## STATE
- BUDA11: read PLAN, G2-BUDGET, AUDIT-IMP, LOWD, WALL §0-2. Found a short exact kill of the cell (no catalogue/LOWD tables needed). 
- BUDA11: DONE. chk1 (100 s) and chk2 (285 s) agree: A ok; B only ('w8',tau'=tau,y∝c_tau):112 and (w=1):5824; C kinds 0/frame/root = 56224/896/112, 0 violations; D min frame/frame cost 8, control 896 cost-7 (frame,root) pairs; E true. THEOREM BUDA11 PROVEN.

## THEOREM BUDA11 (PROVEN; finite inputs (A)-(E) CHECKED twice). The open cell is EMPTY. Hence corrected BUD-A:
## every exact (1,1) decoder of N0 with m >= 11 has cost >= 64 (m = 11), >= 70 (m >= 12).
Setting: exact decoder P Q^T = N0, s = t = 1: p_k = C'x_k + x2_k E, q_k = C'y_k + y2_k F, Xhat^T Yhat = diag(I8, 0) (WALL §2).
Sound P2 gives cost >= 77 - 12 - n01; cost <= 63 forces n01 = 2: a term a with p_a = e_tau (w=1, labels distinct (A): R = {tau}),
w(A_a) = 8, cost 0, a term b with q_b = e_tau', w(R_b) = 8, cost 0 (two (8,1) terms would be two D=8 row lows: WALL 8.2), and the other
nine terms S have d^R, d^A <= 1 (WALL 8.2/8.3: the D=8 lows are unique) and cost_k >= 9 - d^R - d^A >= 7, so all are (1,1) with cost 7.
Step 1 (normal form). e_tau is not in col C' (CHECKED A), so take E = e_tau: xhat_a = (0,1). Likewise F = e_tau', yhat_b = (0,1).
Step 2 (tau' = tau). cost_a = 0 means q_a vanishes on Z_tau := {s : Bd[tau,s] = 1} = {tau} ∪ tau^perp (60 lines).
 CHECKED (B): rank C[Z_tau] = 8, rank C[Z_tau \ s] = 8 for s in Z_tau\tau, rank C[Z_tau \ tau] = 7 (for every tau). So for tau' != tau
 y_a = 0 and q_a = y2_a e_tau' (w = 1 != 8, or q_a = 0); hence tau' = tau and y_a ∝ c_tau, q_a ∝ N0[:,tau] - e_tau (w = 8). E = F = e_tau.
Step 3 (row/column directions). For k in S, w(R_k) <= 8 and R_k \ tau = Off(x_k) \ tau. If H is a hyperplane of F2^9 containing the labels of R_k,
 x_k is orthogonal to c_s for every s != tau with label outside H. CHECKED (C), all tau and all 511 hyperplanes: that kernel is 0, span(c_tau)
 or span(f_i). So x_k ∝ c_tau or x_k ∝ f_i (x_k != 0: x_k = 0 would be a second weight-1 row). Same for y_k (Bd symmetric, F = e_tau).
Step 4 (frame/frame is lossy). If x_k ∝ f_i and y_k ∝ f_j then R_k ∈ {Off f_i \ tau, Off f_i ∪ tau} (all cases: Off f_i has no coloop, ind_coloop.py; w=9 options are outside the cell), A_k likewise; CHECKED (D): every such
 pair with both weights 8 has Bd-rank >= 8 (min = 8). So each k in S has x_k ∝ c_tau or y_k ∝ c_tau.
Step 5 (contradiction). x_a = 0 and y_b = 0, so Σ_{k in S} x_k y_k^T = I8 (top-left block of Xhat^T Yhat). c_tau has 4 zero frame
 coordinates (CHECKED E); for such i, x_k[i] y_k[i] = 0 for every k in S by Step 4, but the (i,i) entry is 1. ∎
Control: (D) also counts (frame row, root column Off(c_tau)\tau) pairs of cost 7 (lossless pairs exist, so Step 4's checker can see 7).
Remark: Steps 2-5 use only cost_a = cost_b = 0, w(A_a) = w(R_b) = 8, and w <= 8 + cost 7 on S; the tightness of P2 is not otherwise used.

## Corrected bounds wherever P2 was used (sound P2: cost >= 7m - Λ_P - Λ_Q - n01)
n01 := #{k : cost_k = 0, (d^R,d^A) ∈ {(8,1),(1,8)}}. PROVEN: n01 <= n8_P + n8_Q <= s + t, n8_X := #single-line lows on side X
 (single-line lows sit at distinct lines after Lemma-D merging; s+1 of them e_t1..e_t(s+1) in span(C', E) (dim 8+s) would give a nonzero C'x of support <= s+1 < 53 = min|Off|). Weaker uniform form: Λ'_X := Σ min(7,(d-1)^+) (subtracts every d=8 low, cost-0 or not).
- BUD-A ((1,1), m >= 11): 77 - 12 - 2 = 63 at m = 11, closed to >= 64 by THEOREM BUDA11; m >= 12: >= 84 - 14 = 70. K1 (1,1) m >= 11 RESTORED.
- O4-2 line 85 (s,t >= 2): cost >= 7m - 6(s+t) - n01 >= 56 + 7r at m = 8+s+t+r (was 56 + s + t + 7r). Tight-m survival range is no longer
  "s+t <= 7" from this bound alone: with n01 <= s+t every tight m survives; with n01 = 0 (no cost-0 single-line terms) the old statement holds.
- BUDGET-X §1/§4 ("with BX both sides and P2") and #3029 C2 (CONDITIONAL on P2): cost >= 56 + s + t + 7r - 6(dep_P + dep_Q) - def(b_P,s) - def(b_Q,t) - n01.
  #3029 already marks C2 CONDITIONAL; the correction is the extra -n01 (<= s+t). AUDIT-BX items 1 and 4 "mod P2": statements unchanged
  (they are identities/bounds on |Lo|, not P2 consequences); any numeric conclusion drawn from P2 there gets -n01.
- G2-BUDGET P3 (s = 1 ledger): cost >= 7m - 3 - Λ_Q - n01 (under G2 no row has d^R = 8, so n01 = #(1,8) cost-0 terms <= n8_Q <= t).
OPEN (not attempted): extending the BUDA11 kill to s or t >= 2 (Step 2 fails: q_a = C'y + F y2 with t >= 2 need not vanish trivially on Z_tau).
