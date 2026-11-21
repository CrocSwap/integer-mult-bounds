# LEANSGRAM (Sonnet, Lean) -- lean/decoder-duality/Nov15/CallerSGram.lean (579 lines, compiles rc=0 via runlean.sh, no sorry; axioms propext, Classical.choice, Quot.sound only)
Setting: A,B : Matrix (Fin n) iota K, block fn beta : iota -> N, stage V_t = 1 + A Pi_t B^T, G = B^T A, roles = rows of A,B. Blocks are m wide (m=2 for SK).
[P, Lean] sgProd_eq     : P_k = 1 + A H B^T, H=(1-Glow)^-1 (unit det proved via BlockTriangular). Any field, any block width.
[P, Lean] sgForward     : P_k=-1, char/=2  =>  rank K + n <= |iota| (rank K <= 2 for n=|iota|-2) and rank G = n.  K := 2+Gdiag+Gup-Glow as in SK.
[P, Lean] sgConverse    : n+2=|iota|, rank K<=2, char/=2  =>  P_k=-1.  (rank G<=n is AUTOMATIC: G=B^T A factors through n.) So SK's "<=>" is fully proved; the
          idempotent step is done as range(E) cap range(D)=0 + commutation, rank A=rank B=n falls out of rank G>=n.
[P, Lean] blk_unit      : rank M<=m, M_ss, M_tt invertible => M_st invertible (Schur: M_tt = M_ts M_ss^-1 M_st).
[P, Lean] sgPairCoverage: P_k=-1 frame, n+m=k*m, char/=2, K_tt invertible all t  =>  any s/=t are met by >= m common roles (m=2: >=2). This is CROSS for c=1
          (and for any disjoint nonempty X,Y by monotonicity: pick s in X, t in Y).
[P, Lean] non-vacuity   : k=3,m=2,n=4 over Q (CallerSignInst design, reversed list order): prod_A3B3, diag_unit_A3B3, inst_pair_coverage, inst_forward, inst_converse.
NOT formalised: gauge form (Etil), rank G_XY = 2 rank E_XY and c>1 CROSS, staircase det 2^{c-1}, DYADIC_J, PIECE-CROSS.
SK gaps found: (1) char /= 2 is needed for item 1 (forward and converse), SK states it only for the staircase det. (2) "rank G <= n" in the iff is redundant given sizes.
(3) lambda /= -1 enters as K_tt invertible (hypothesis hdiag); that is exactly SK's use. (4) role-meets is stated with M_r = support of A or B; the proof only needs the directional
condition B_r(s) /= 0 and A_r(t) /= 0, so coverage can be sharpened to that. (5) c>1 and DYADIC rest on [C] rank E = min(runs) and are unproved.
