# QBRANCH QB (Nov 20, Sonnet; exact LP + proof). Code qb1 (float CG LP, Q0 control = HP), qb2/qb3 (#7113 role extraction, RC2 pair-form test), qb5/qb6 (single-l / cutting-plane dual search), qb7 (chart + dual cert, mpmath-60, exhaustive partition DP), qb8 (+DEG1<=Q row), qb9 (full enumeration k<=9), qb10-12 (debug/support). 1-2 procs, threads=1. No Lean/advisor/push.
Why this differs: KASYM covers Q=0 (n=2k-2, D>=2, L<=k-2). Here Q>=1: n=2k-2+Q roles, each extra role costs 1 (F = sum v - Q), D>=1, L<=k (cwlp.py Q>=1 branch).

## 0. Result
[C] Q>=1 reduced LP (count n>=2k-1 with -1/role, MAINS>=2k, RC2_l l=3..k) has optimum = CHART-Q: 2k mains carried by DEGREE-1 roles (v1 = 9^s-8^s, thin units) + x_h = 2k/rho all-2-piece full hubs (k, 2^{k/2}) (odd k: (k,(1,2^{(k-1)/2}))), rho = k(k-2)/(k-1) (even k).
 Even k: HP_Q(k) = (104/k)[2k-2 - 2k(1-v1) - x_h(1-v_hub)], v1 = 9^s-8^s, v_hub = (8k+1)^s - (k/2)16^s, x_h = 2(k-1)/(k-2).
 It is HIGHER than HP(k) everywhere (k=13: 151.69 vs 143.27; max HP_Q(16) = 152.081). Count row not binding, MAINS tight, wm = 1-v1 = .03096.
 [C qb7] dual certificates (float cutting-plane dual scaled by 1-1e-12, max Phi over ALL partitions of every D<=k < 0 in mpmath-60): chart = LP to 7e-11 at k = 7..16 (all), 20, 40, 72, 74, 128. [C qb9 full enumeration] k=3..6: LP slightly above chart (116.2866, 130.2193, 137.9822, 142.7276), k=7,8,9 = chart.
 Odd k: chart not always optimal. k=21 LP = chart (151.3032); k=73 LP 140.4758 > chart 140.4576 (support: 146 deg-1 roles, 2.024 x (72,2^36), .231 x (73,(2^5,63))). Dual search at 73, 75 infeasible for the chart, so odd-k values are the chart + small extras (0.018 at 73), no closed form.
 Values (chart): k=72 140.678, 73 140.458(LP 140.476), 74 140.350, 75 140.134, 128 133.357, 150 131.212, 170 129.49, 177 128.907, 178 128.8536, 179 128.751, 180 128.698, 200 127.22.
 CROSSING 128.891: even chart falls below at k=178 (177 is 128.9068, still above). All k>=178 chart < bar. Odd k>=179 LP = chart + extras (0.02 at 73): [CONJ] still below. k=177/178/179 full LP certificates NOT done (jobs starved/timed out): crossing is [C] for the chart, [CONJ] for the LP at odd k near it. Compare Q=0: crossing at 73. So Q>=1 reduced LP closes only for k >~ 178 and has no mid-k value below 144.

## 1. Why the bound is weak (structure)
Phi(D,P) = G(D) - sum_L g(L) + wm*m, G(D) = (8D+1)^s - 1 + [D(k-D)S(D)+D^2 T]/(k-1), g(L) = (8L)^s + [L(k-L)S(L)+L^2 T]/(k-1), S(D)=sum_{3<=l<=D} w_l, T=S(k) (RC2 dual written per piece). D=1 roles: v1-1+wm <= 0 forces wm=1-v1. A D=1 role is the best role by concavity (v1 > v2p = .9624), so mains cost only .031 each and the all-main hubs of KASYM are replaced by cheap 2-piece hubs. Dual weights w_l are NOT unique (many optimal duals; no chord closed form found) so no clean Lean dual; CallerHP.lean NOT extended.
With the conjectural row DEG1<=Q (#D>=2 roles >= 2k-2, R2 tier C) [CONJ, qb8 float]: k=8 142.37, 10 144.34, 13 145.17, 16 145.32, 24 143.71 (pure pairs fill the core). Still > Q=0 HP (143.27) and > 128.891.

## 2. Role count / branch model [P sketch]
n = space dim = rank of A (n x 2k) in prod V = I + A H B^T = -I, so n <= 2k + (#thin rank-1 events). With only k rank-2 hosts n<=2k; n=2k forces G = B^T A = -2I (A,B invertible, G_low=0) i.e. every K_tt = 0, eigenvalue lambda = -1 at every stage, contradicting the lambda != -1 hypothesis of SK 1 / BL 1 / RC2. So Q>=1 callers come only with thin units (QUERY / degree-1 roles): #7113 type A has 36 roles/port = 2k+2 (Q=4, 4 QUERY/port, 4 degree-1 roles). The SK 1 equivalence "prod=-I <=> rank K<=2, rank G<=n" was derived for n=2k-2.
## 3. Soundness of the rows in Q>=1
- MAINS (>= 2 singleton pieces per stage): holds on #7113 type A (4 or 6 per stage) [C qb3]. Not proved in the model for Q>=1 (cited from TB1/K4 as a general row).
- RC2 pair form: [C qb3] 0 violations over all (s,t,l), 17 stages x 36 roles, min LHS = 2 (tight) on #7113 type A with pieces = paid IDLE sets + leftover singletons (ids 1-based; a role's mask is exactly partitioned, checked). Type B (mixed roots, repeated/overlapping idle sets) is not a partition model, not tested.
- RC2 PROOF does not transfer as written: step (a) (Ghat_st = 1/4 eps alpha_s beta_t invertible) uses rank K = 2, derived at n = 2k-2; with thin units the blocks K_st are not shown invertible. So RC2 at Q>=1 is [C on one built frame], NOT [P].
- Role extraction check: #7113 roles/masks from MONOCALLER/7113_CALLER.json, type A = 2 full hubs (D=17, all main, unpaid) + two 8/9-stage nested chains.
## 4. Next
(i) prove the Q>=1 RC2 (and MAINS) from a frame model with thin units (rank-1 QUERY events) or find a violating thin-unit frame; (ii) law bounding degree-1 roles (DEG1<=Q or a per-stage cap): without it HP_Q > 140 for k<=100; (iii) certify k=177..179 (qb7 DP is O(k^3) mp ops: use mp.dps=30).
