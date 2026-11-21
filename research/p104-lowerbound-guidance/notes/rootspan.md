# ROOTSPAN RS (Nov 20, Sonnet, exact compute). Code: rootspan.py (CP-SAT, 1 worker, integer-exact), osexact.py, l8.py, abl.py; log rootspan.log
VERDICT: NOT LOUD. One-sided class (rank_Q F = 8): D >= 28 (root-span law added), vs OS 24 as quoted (true exact OS min over the full profile domain is 22; osip.py's search grid was restricted). No 56. E8 profile (c2..c8 = 8, D = 56) satisfies every constraint [C control passes].
How this differs: NT gave level cuts x cliques only. Here: reader roots must lie in span of depositor contents (alpha_k in Q^8), giving Hall/rank constraints that couple root subspaces (E8 root caps R(s)) with label flats (readers per flat N(9-b)).
## Model [P unless noted]
- D = sum_l c_l, c_l = |X_l| (nodes with b<l<=a), n_beta (non-free depositors, dim b = beta) <= c_{beta+1}; wlog n_beta = c_{beta+1} (extra depositors only weaken nothing: Hall rows below are implied by the n-row for n+1 since R is monotone). Cuts exist only for l <= 8 (gatherers have a >= 8). [BUG FOUND+FIXED: an earlier run used l = 9 and charged c_9; E8 control caught it.]
- One-sided: every content r_k = <alpha_k, Ah_.>, reader t needs Ah_t in span{alpha_k : k deposits to t}; k deposits only to its flat L_k = labels in b_k^perp, |L_k| <= N(9-beta).
- Rank: V_l = span{alpha_k : beta_k < l} has dim <= c_l (Menger). Readers whose depositors are all in Low_l u T (T any m high depositors) have roots in a (c_l+m)-dim space, so number <= R(c_l+m) (R = max E8 root lines in a subspace: 1,3,6,12,20,36,63; P104 heuristic 1,3,6,12,20,32,55 gives the same optimum). Readers not touched by High\T number >= 104 - (sum of the smallest h-m weights N(9-beta)).
- Hall rows: x_j = #readers with j depositors; sum x = 104; sum j x_j <= sum N(9-beta) n_beta; for s<=7 sum_j x_j C(D-j,s-j) <= R(s) C(D,s) (n = D).
- Forced crossing: any depositor with b < l <= 8 forces c_l >= 1. OS clique rows kept.
## Result [C, CP-SAT OPTIMAL/INFEASIBLE for every D < 28, integers only]
- min D = 28, profile c = (c1..c9) = (0,0,0,2,3,7,8,8,0): depositors b=3:2, b=4:3, b=5:7, b=6:8, b=7:8 (flat sizes 20,12,8,4,2).
- Ablation: OS alone 22; + level/Hall-chain family 27; + x-Hall rows 28; without generalized (T) family 26.
## What still allows 28 (not 56)
1. Depositors on one path/fan-out share alpha (parallel contents); Hall rows treat depositors as independent directions. The true law is dim span(alpha_S) <= min cut(S), used only for the prefix sets Low_l.
2. Flat coverage uses sum of N, not exact unions of label flats (e.g. 9 flats of dim 4 cannot all be size 8 and disjoint?). Exact max-coverage not computed (CP-SAT set cover over 1.26M dim-4 flats timed out).
3. R(s) caps are root-subsystem sizes, not the root/label coupling (q_t.v pattern of the E8 kernel normals).
4. Direct-sum subclass (8 disjoint trees, alpha = basis beta): support LP gives total support >= 328 over 104 roots (mean 3.2 per root); chain unions F(c)=sum N(j+1) are convex so it still allows ~30.
NEXT: add law 1 (min-cut on arbitrary depositor subsets, via tree/chain structure) and exact flat unions (law 2); that is the remaining one-sided lever.
