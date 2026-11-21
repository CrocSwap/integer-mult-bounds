# BILINEAR BL (Nov 20, Opus; theory + LP). Own code: bl0.py (float) / bl0x.py (EXACT Fractions) kernel-gauge checks; bl1.py (sk2-equivalent LP + f(D,#singletons) rows, sizing); bl2.py (WALT rows); bl3.py (CHAIN rows); bl4.py (2-branch effective LP, superseded); bl5.py (COVER LP, exact DP pricing over (d, e, hasone)); bl6.py (coarse cells, superseded); bl7.py (valid branch & bound over cover profiles); bl8.py (float SCOUT, Delta-zero walks). Logs: sz1.log, tri.log, bb32.log. 1 process, threads=1. No Lean, advisor, kill or push.
Why this differs: SCHERK, MAINSCAN and CYCLELP give rank or support laws on MASKS. This lane uses (a) a new gauge in which every role vector has zero block sum, so values (not ranks) of G enter, and (b) the shared rescue vector y_q across a piece, collectively (closed sets), not one piece at a time (PINCH, NO-FIX).
VERDICT: NOT LOUD. Three new [P] laws, all sound on the built frames (they are vacuous there, since those frames have no multi pieces). They do not move the witness LP materially. The best valid bounds are k16 <= 148.648 (was 148.859) and k32 <= 150.866 (was 151.971; the branch & bound is not closed). Every law here is QUALITATIVE per stage: one relay role per stage rescues any number of big-piece roles. What is missing is a quantitative rescue law.

1 [P] KERNEL (ZERO-SUM) GAUGE. Start from SCHERK's gauge, scaled on the right by Lam_t^{-1}: G' = E(x)I2 - 2 diag(M_t), M_t = (A_t+I)^{-1}. Rank G' = 2k-2.
  Right kernel: blocks kap_t = 1/2 Lam_t S_t, with S_1 = I and S_{t+1} = -A_t S_t. Here S_{k+1} = -I is exactly the product law.
  Left kernel: lam_t^T = 1/2 T_t Lam_t, with T_k = I and T_{t-1} = -T_t A_t.
  All these blocks are invertible (A_t invertible, lambda != -1).
  Put a^_r[t] = kap_t^T a_r[t] and b^_r[s] = lam_s^T b_r[s]. Then Ghat = sum_r b^_r a^_r^T. Every a^_r and b^_r has ZERO BLOCK SUM, because the row space of G' is ker^perp. Conversely, any zero-sum support factorisation of Ghat through n = 2k-2 roles is a frame: rank 2k-2 forces row space = Z, the space of zero-sum vectors.
  Closed form: Ghat_st = 1/4 eps_st alpha_s beta_t for s != t, with alpha_s = Q_s^{-1} - Q_{s-1}^{-1}, beta_t = Q_t - Q_{t-1}, Q_t = (-1)^t A_t...A_1 (Q_0 = I, Q_k = -I). The diagonal blocks are fixed by the zero sums.
  [C exact, bl0x] k = 3..7, random rational walks: all identities hold.
2 [P] PAIR-SYMMETRY (value law). A degree-2 role {s,t} contributes the Laplacian edge (e_s-e_t)(e_s-e_t)^T (x) v u^T. This term is invariant under sigma (swap blocks (s,t) and (t,s)). So Ghat - Ghat^sigma = sum_{D_r>=3} (b^_r a^_r^T - (b^_r a^_r^T)^sigma).
  If a pair is served only by degree-2 roles, then Ghat_st = Ghat_ts, i.e. g C_s D_t g = -C_t D_s, where g = Q_{t-1}Q_{s-1}^{-1}, C = I + A^{-1}, D = I + A.
  [P] For commuting (scalar or SO(2)) walks the Delta-zero graph is bipartite (p_s = -p_t, p_t = q_t q_{t-1}). So it has no triangle, and k^2/4 Delta-zero pairs are attainable.
  [C float, bl8, tri.log] For noncommuting walks, k=4: a walk with ALL 6 pairs Delta-zero (min sv A .26, min sv Lam .32); at k5, triple 024 is Delta-zero (other pairs not). So the triangle and Turan route is DEAD.
  The rank form, rank(Ghat - Ghat^sigma) <= 5 #{D>=3}, is a deep-role count, which SK sizing already shows is insufficient. No LP row.
3 [P] CLOSURE / INERT. At a stage t, call C ⊆ E_t CLOSED if every r in C has a multi piece q at t with E(P_q) ⊆ C. Then the rows of C in A_t and B_t vanish.
  Proof: the |C| vectors y_q (q ∋ t) are biorthogonal to the x_q, hence independent, and supported in C. So they span R^C and kill A_t on C (x_q likewise for B_t).
  EFFECTIVE MASKS. Let eff_r = {t : r not in the greatest closed set at t}. CROSS, DYADIC, WALT and pair coverage all hold with eff in place of M (inert rows contribute nothing to G_XY).
  [P] COVER: a role whose piece at t has size L is effective at t only if the intervals [L_r(t)+1, D_r] over r in E_t cover [2, L]. Proof: follow the chain to a singleton holder; for each level l <= L, the first link with a piece < l has degree >= l.
  The typed argmax {hubs (k/2|k/2), pure halves, singletons only on chords and triples} is closed at every stage, so hubs and pure halves are inert. That is DEAD as typed.
  [P] CHAIN_l row (#roles with all pieces >= l <= 2 * small-piece incidences on roles of degree >= l): k16 148.769 only.
4 [C] LP (base = SCHERK sk2: ms9 coord,pfix,shal + DYADIC_J; reproduced 134.050 / 142.837 / 148.859).
  COVER, everything-effective branch (S_l >= k for all l in 3..k-2): k8 142.687, k16 147.299, k32 146.932, k64 144.224.
  VALID bound = max over monotone profiles tau_l = |T_l| (bl7 branch & bound): k8 142.837 (closed); k16 in [148.141, 148.648] (400 LPs); k32 <= 150.866 (700 LPs, not closed; was 151.971).
  Escape: profiles in which deep big-piece roles are effective on only part of the stages, paid for by a few roles with pieces just below each level, e.g. (1,7) on D8 and (15,17) on D32.
  WALT_w rows (piece-aware CROSS averaged over uniform alternating w-subsets): no change at k8, k16, k32.
5 [C sizing, bl1, sz1.log; rows NOT proved] k64: total singletons sum_t sigma_t >= 4k: 150.1; 4.5k: 142.7; 5k: 135.1; 5.5k: 127.6 (k16 125.2, k32 124.5). Singletons on D>=3 roles >= 5.5k: 127.5 (= CY). sum_{D>=3} C(j,2) >= C(k,2): 142.4.
  Built frames are all-coordinate, with sum sigma/k = 2, 3.33, 4, 5.33 at k = 2, 3, 4, 6.
  The naive parameter count sum sigma >= (k-1)^2 + (6k-3)/4 FAILS on c33 (32 < 33.25). So frames sit in special position, and no singleton count follows from dimension counting.
  Coordinate case (no rescue): DYADIC on singleton supports already forces sum sigma >= R_J + n, about 8k (k64: LP 84). The WHOLE gap is rescue.
WHAT IS MISSING: a QUANTITATIVE rescue law. With relays O_t (deep roles with a small piece at t), the big-piece rows satisfy a_Big[t] = M_cell(t) a_O[t], so their contribution to Ghat_st is b_O[s]^T Phi(cell s, cell t) a_O[t]. It factors through the few relay roles. Next: bound the rank or values of {Phi} against Ghat_st = 1/4 eps alpha_s beta_t over many cells (a value law on the relay coupling). Any such law must force about 5.5k singletons in total, or on D>=3 roles.
