# AUD-3 (Oct 16) — independent adversarial audit, P112-PUSH. 0 FALSE.
Own scripts here: buda_mine.py (+.out; own mod-p linear algebra and F2 ranks, 20 s), slack_mine.py, land_mine.py (+.out; own post-filters on dpX enum + symlp).
STATE: AUD-3: 1 PROVEN, 2 PROVEN, 3 PROVEN-WITH-FIXES (needs −n01), 4 PROVEN for x>=1 and d=0, list CHECKED-2 (35/280), 5 α PROVEN, β R6 PROVEN, β R7 p=2 CHECKED-1 + FINITE2 partial, β R7 p=4 GAP (never run).

1. BUDA11: PROVEN. buda_mine.py, a third implementation, reproduces (B) incl. ker C[Z_t \ t] = <c_t>; (C) 0/frame/c_t = 56224/896/112 with 0 violations; (D) min 8; (E).
   Logic re-read: Steps 1-5 are sound. Λ_P=Λ_Q=6 means every S term has d<=1 directly (no WALL needed). In Step 5, x_a = y_b = 0 gives Σ_S x y^T = I8.
   Sound P2 re-derived from Sylvester alone (cost_k >= wR+wA−9, cost_k >= 0). The only deficit cells are weights (1,8)/(8,1), at −1 each => −n01. n01 <= s+t: proof OK (mod min|Off| = 53).
   Corrected bounds are right: BUD-A >= 64 (m=11), >= 70 (m>=12); O4-2 56+s+t+7r−n01; P3 7m−3−Λ_Q−n01. BUDGET-X / #3029 C2 take an extra −n01 (accepted as additive; base formulas not re-audited).
2. RDEP2 DR': PROVEN (mod Lemma T, M2, Pay(b),(c)). Overlapping V_a are fine: each Pay(b) bound is on its own pivot. Hence Σ_a rank_l(T∩S_a) >= |T| suffices; a partition is not needed.
   Also checked: |T_D∩T_X| <= #XM; CL proof (L-values at w are c times those at v); colouring corollary (i)/(ii) and s=1 => δ=0; SH-move identity exact, cost <= c(π_a)+c(π_a') (ρ depends only on U), Δ <= def' (the ρ_b row increase is dim(U_A∩Z_R)). The re-gauging caveat stands as the card says.
3. RDEP3 Theorem S: PROVEN-WITH-FIXES. The max(1,·) floor uses P0. Sound form: cost >= 7m − Λ_P − Λ_Q + Σ_k slack_k − n_0, n_0 = #cost-0 terms.
   Every cell with wR+wA<=9 has slack >= 1 except (1,8)/(8,1) (slack_mine.py), so this is >= ... + Σ slack' − n01 with slack' >= 0. Table and closed form re-checked.
   S1 becomes def_P+def_Q+Σslack' <= 7−s−t+n01. (1,t) §2 becomes: closed iff Λ_P + n01 <= t−1. Since Λ_P <= 5, no wR=1 row exists, so n01 = #cost-0 terms with (wR,wA)=(8,1), <= t. Those terms join the residue (unkilled except at (1,1), BUDA11).
4. CONJG2: x>=1 empty PROVEN. I re-read the Pencil Lemma (SMALL2 §7): its statement and proof use only T, D, λ and Lemma N, with no x.
   land_mine.py shows the slack-0 rows: e=1 (t=2) dies at DP/LP alone; e=2 (t=3) has 2 LP survivors at d=8, killed by Basis(S66+t) and Pencil (both T-level).
   d=0 shape PROVEN (arithmetic re-done; nit: "(6,2)" for t=3 should read (6,1,1)/(5,2,1)…, bound 22 unchanged).
   d>=1 list: my independent filter chain reproduces e=2: 35 (by d 4,8,6,2,3,4,4,4) and e=3: 280 (3,7,13,24,45,56,65,67). DP+LP are shared imports (OS-CHARGE2), not re-implemented.
5. FINITE: (α) F7+P max span 4 <= 5: PROVEN (FINITE+FINITE2 agree, 52 reps, 12 dirs; the 4-flat superset is conservative; |Off| <= 80 list is complete).
   (β) R=6: span 1, PROVEN for p=2 (2 impls); p=4 single impl.
   (β) R=7 p=2: FINITE complete over 159 reps, max 4 (distribution 0:12 1:7 2:99 3:33 4:8).
   FINITE2 is PARTIAL: 97/160 reps done, max 4, no rank 5. Its chunks are killed at 1190 s, leaving holes (14, 41, 49-50, 58-59, 66-68, 78-81, 86-90, 99, 107-108, 116-117) plus 119+ still pending.
   FINITE vs FINITE2 rep numbering is NOT aligned (FINITE2 adds an empty rep and orders orbits differently), so "per-rep ranks match" is unsupported. Compare maxima only.
   (β) R=7 p=4 (needed for TWOSIDE's "<= 4 lines" case): GAP, never completed.
