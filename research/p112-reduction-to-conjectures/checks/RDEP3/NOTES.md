# RDEP3 — R-dep s>=2 + N2 at s=1; tight m s+t<=7 (Oct 16)
## STATE
- RDEP3: started; read PLAN, RDEP2, TWOSIDE, AUDIT-TS, BX README, BUDGET-X, K1-T2.
- RDEP3: ~60k. Plan: (b) exact-slack refinement of P2 (per-term slack vs P2) -> necessary shape of a tight cost<=63 decoder; (1,t) P2 closure when Lambda_P <= t-1; (a) s=1 case (i) with 8.3 + catalogue. Checks: two impls + witness control (wstat).
- RDEP3: DONE ~90k. (b): Theorem S (exact-slack P2) PROVEN mod P0 + cost_k >= wR+wA-9 (G2-BUDGET); table CHECKED x2 (slack1.py, slack2.py); control: weight floor = cost = 64 on 6/6 exact witnesses (slack2.py ctl). (1,t) P1 closure + exact residue. (a): not closed; residue restated with S ledger. No cell of (b) fully closed beyond (1,t) Lambda_P <= t-1.

Labels PROVEN (mod named imports) / CHECKED (2 impls) / OPEN. python = W/venv/bin/python; scripts here: slack1.py (impl 1), slack2.py (impl 2 + `ctl` positive control, ~1 min, 1 proc).

## §1 Theorem S (exact-slack form of G2-BUDGET P2) — PROVEN mod G2-BUDGET P0 (cost-0 terms deletable) and cost_k >= w(R_k)+w(A_k)-9
lam(w) := min(6,(8-w)^+) (so Lambda_P = Σ_k lam(wR_k), Lambda_Q = Σ_k lam(wA_k)); slack(a,b) := max(1,a+b-9) - (7 - lam(a) - lam(b)) >= 0 (all 81 cells).
**cost(D) >= Σ_k max(1, wR_k+wA_k-9) = 7m - Lambda_P - Lambda_Q + Σ_k slack(wR_k,wA_k).**  (P2 is the case "drop the slack".)
slack table (rows wR, cols wA = 1..9; CHECKED slack1 = slack2):
  1|6 6 5 4 3 2 1 0 0   2|6 6 5 4 3 2 1 0 1   3|5 5 4 3 2 1 0 0 1   4|4 4 3 2 1 0 0 0 1   5|3 3 2 1 0 0 0 0 1
  6|2 2 1 0 0 0 0 0 1   7|1 1 0 0 0 0 0 0 1   8|0 0 0 0 0 0 0 0 1   9|0 1 1 1 1 1 1 1 2
 i.e. slack = [wR=9][wA>=2] + [wA=9][wR>=2] + (10-max(wR,2)-max(wA,2))^+ for wR,wA <= 8 (doubly-light terms), and 0 exactly on wR+wA >= 10 (both <= 8), (1,8),(2,8),(1,9) and transposes.
**Positive control / sharpness (CHECKED slack2.py ctl):** on all 6 exact cost-64 witnesses (witness16 disjoint/shared m=10, MS3a m=11, swap(1,1) m=10, swap(2,2) m=12,
 swap(1,3) m=12 — all TIGHT m with s+t <= 4) the weight floor Σ max(1,wR+wA-9) equals the cost, 64. So the weight floor is exact on every known optimum; a proof of (b)
 at weight level must be sharp (no spare unit), and 64 is attained in cells (1,1),(2,1),(2,2),(1,3) at tight m.
**Corollary S1 (tight m, the (b) hypotheses Lambda_P <= 6s, Lambda_Q <= 6t; def_P := 6s-Lambda_P, def_Q := 6t-Lambda_Q).**
  cost >= 56 + s + t + def_P + def_Q + Σ slack.  Hence a cost <= 63 tight decoder must satisfy **def_P + def_Q + Σ_k slack_k <= 7 - s - t**; in particular
  N9 := #{terms with a weight-9 side opposite a side of weight >= 2} (a (9,9) term counted twice) <= 7-s-t, and every doubly-light term (wR,wA <= 8, max(wR,2)+max(wA,2) <= 9) costs
  (10-max(wR,2)-max(wA,2)) units of that budget. At s+t = 7: no slack at all — every term is one of the zero-slack types above and Lambda_P = 6s, Lambda_Q = 6t exactly.

## §2 (1,t), tight m = 9+t, Lambda_Q <= 6t — PROVEN mod G2-BUDGET P1 (WALL 8.2/8.3 imports)
P1: rows with wR <= 7 are ONE low row (weight w) or TWO weight-7 rows; inside rows have w >= 8 (L3.1). So Lambda_P = lam(w) or 2, and by §1
 cost >= 63 + t - Lambda_P + def_Q + Σ slack. **Closed (cost >= 64) whenever Lambda_P <= t-1.** Exact residue per cell (needs lam >= t):
 t=2: a low row of weight w <= 6, or two weight-7 rows | t=3: w <= 5 | t=4: w <= 4 | t=5: w <= 3 | t=6: w <= 2 — and then Σ slack + def_Q <= Lambda_P - t.
 For w <= 4 the low row has |R| <= g(4) = 8 <= 11: it can be taken as the (small) row pivot (Pi-gauge, p_pi = that row); for w = 1 (single entry) Theorem L applies:
 cost >= 64 unless rho_0 > Delta (#2816 R4 residue; Conjecture G in the self-paired case) — i.e. the w = 1 sub-residue of every (1,t) cell is exactly K1-T2's open residue.
 (1,1): BUD-A / LOWD (already closed). s >= 2: no P1 analogue (cross-class rows unconstrained, O4-2 §7(ii)); only Corollary S1 applies — OPEN.

## §3 (a) R-dep: status (NOT closed)
s = 1 at tight m: dep_Q = 1 exactly (dep_Q <= s + r); with BX, Lambda_Q <= 6(t+1) - BXsurplus, so the S-ledger gives cost >= 63 + t - Lambda_P - 6 + Σ slack (+BX surplus):
 case (i) (no row of weight <= 6, Lambda_P <= 2): cost >= 55 + t + Σ slack; J-terms contribute slack 1 per weight-9 row with w(A) >= 2 (these have eps = 0), so the
 needed eps (Σ_J eps >= w_max+1, TWOSIDE §2) must come from <= 2 weight-7 rows (WALL 8.3) and corrected weight-8 rows, while those rows give slack 0 — consistent, not contradictory.
 Under SU (|S_lambda| <= 11) a corrected weight-8 J row is, by the catalogue, a swap row x ∝ c_v (v ∈ S_lambda, <= 1 per line by Lemma D / M2) or a frame row x ∝ f_i with
 z_i ∈ U_{A_k} and S_lambda ∩ O_{z_i} = ∅; so case (i) needs n_frame^corr + n_swap^corr >= w_max - 3. Not closed: no bound on frame-corrected J rows was found.
 s >= 2: unchanged (only the boxed condition Σ_J eps^row >= max_J w(A)+1 per J_P-circuit). The N2 pattern at s = 1 with case (ii) unchanged.
## Exact residue after RDEP3
(b) tight m, s+t <= 7: s = 1: the §2 per-cell low-row list (w=1 part = Theorem L's rho_0 > Delta); s >= 2: every configuration meeting Corollary S1's budget
 def_P + def_Q + Σ slack <= 7-s-t (sharp: met with equality at 64 by the four witness cells). (a) as TWOSIDE §2 / §3 here.
