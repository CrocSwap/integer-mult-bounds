# MAINPLACE MP (Nov 20, Opus; theory + small builds). Code: mp0 (pure-ban LP support), mp1 (k8 placement enum + rblaw + STAR + RELAY-HALL),
mp2 (numeric build, rbcore/rb15), mp3/mp4 (SIZING bans/rows, NOT laws), mp5 (cc1 + HALL_l rows [P]). 1 proc, threads=1. No Lean/push/advisor.
Why this differs: CC/BL/RB priced rows or mask laws. Here the LP argmax is taken literally and built. Its failure is traced to a VALUE law
(sign flatness through a 2-dim hub channel), not to a rank or count law.

## 1. [P] RELAY-HALL (mask level, any order). Stage t, any s != t. The roles of E_t \ E_s have a matching into the pieces q containing t
(multi pieces and idle singletons, never mains) with M_r ⊇ q.
Proof: K = span{x_q : q ∋ t} = leftker(B_t|E_t) has dim |E_t|-2 (x_q independent, rank B_t = 2). Ghat_ts invertible needs rank B_t|W = 2,
W = E_t ∩ E_s, so dim(K ∩ R^W) = |W|-2, so K projects ONTO R^{E_t \ W}. x_q is supported on E(q), so the support pattern needs Hall.
- Consequence: a main on a chord {t,u} needs, for every s not in {t,u}, a 2-piece {t,u} of another role, distinct for the 2 mains at t.
  The relayer of a hub piece h must have mask exactly h when it is a degree-|h| role.
- Averaged row HALL_l [P]: sum_r ( sum_{pieces q, L<l, q multi or idle singleton} L(k-L) - [D_r<l] D_r(k-D_r) ) >= 0.
  [C mp5] Inert: k5/8/13 = 133.804/141.321/143.273 (HUBPAIR satisfies it with equality per pure pair).

## 2. k8 nested-chain argmax (pure-ban LP: 2x(8,(4|4)), 4x(4,(2|2)), 8 main chords; 140.982)
- [P] RELAY-HALL forces the shape, in every call order: exactly 2 D4 roles per stage; chords = the pair pieces (as a multigraph);
  D4 masks = the 4 hub halves {X, X^c, Y, Y^c}. If Y in {X, X^c}, CELL-RANK kills it (order-free).
- [C mp1, one order per |X∩Y| class, 243 designs] Only one placement passes every rblaw law, STAR and HALL: X=0123, Y=0456, D4 (01|23), (45|67),
  (04|56), (12|37). The chords form the 8-cycle 0-1-2-3-7-6-5-4. Numeric build (mp2): fixed walks stall at 0.29 / 1.00 / 1.00 / 1.00,
  and the joint walk also stalls.
- [P] DEAD by TWO-HUB SIGN FLATNESS:
  (i) For each t, some s has E_t ∩ E_s = {H1,H2}. So H[t] = [b_H1[t] b_H2[t]] and K[t] are invertible.
  (ii) Hub piece h has E(h) = {H1,H2,R_h}, so x_h(R_h) != 0 and R_h is SLAVED: b_R = v_R^T H, a_R = v'_R^T K on M_R.
  (iii) For a non-chord pair, Ghat_st = H[s] M_st K[t]^T, where M_st = I + sum_{R ⊇ st} N_R and N_R = v_R v'_R^T has rank 1.
      With Ghat_st = 1/4 eps_st alpha_s beta_t, this gives M_st = eps_st U_s W_t.
      So every chord-free 4-cycle has M_st M_s't^-1 M_s't' M_st'^-1 = eps_box I, with eps_box = -1 iff {s,s'},{t,t'} interleave cyclically.
  (iv) Cycles (0,7;2,5), (0,1;7,5), (7,2;0,5), (0,1;5,3), (0,4;6,2) give BD = I, CA = -I and ABA^-1 = -B, where A,B,C,D = I+N_X, Y, X^c, Y^c.
      Then tr A = tr B = 0 and A^2 = B^2 = I. Also N_Y N_X = 0 (from M_13 = BA = I+N_X+N_Y^c) and (A+I) N_Y = 0 (from M_46 = -AB = I+N_X^c+N_Y).
      So v_Y = c v_X and v'_Y·v_X = 0, hence tr N_Y = 0, which contradicts tr N_Y = -2.
  Scope: this exact placement and every placement where the same five cycles exist chord-free with the same interleave pattern
  (the kill is invariant under the dihedral symmetries of the call order). An all-orders k8 sweep was not run (99k designs, ~8 h of rblaw).
- k13 chain: not built. The same mechanism applies wherever every non-hub role is slaved to 2 hubs.

## 3. Coordinator note (KASYM: the mid-k binding point is literally HUBPAIR)
- HUBPAIR (2 all-main hubs + pure pairs) is the same object: each pure pair p has E(p) = {H1,H2,p} (plus parallel pairs), so it is slaved.
  FLATNESS then says that uncovered interleaved 4-cycles give I = -I. That is the CROSS/HUBPAIR kill, seen as a value law.
  FLATNESS [P] holds for any design fully slaved to 2 hubs. It needs the placement and the order, so it is NOT a type row.
- SIZING [C, NOT laws]:
  - Main-chord ban: k8/k13 unchanged (141.32/143.27; HUBPAIR has no chords).
  - Pure ban + main-chord ban: 138.37/140.16.
  - "#{D>=l0} >= c" rows (the cheapest type proxy for a 2-hub cut), l0 = 0.3k..0.5k, c = 3..6: k13 143.07-143.22 (at most -0.2).
  So no deep-count / Hall / chord row reaches the bar. The two-hub family has to be cut by a law that prices interleaving,
  i.e. one that uses the call order (CROSS with slaved roles counted only on pairs they cover). That is open.
NEXT: (1) an all-orders k8 sweep (prefilter with the FLATNESS sign-labelling test, which is combinatorial: u_s w_t eps_st must depend only on the cell pair); (2) a
'slaved CROSS' row: in a 2-hub-slaved design a role adds rank to Ghat_XY only on pairs inside its mask. Type form = an averaged count over interleaved 4-cycles of D(D-1)-weighted cover. It has to be sized before it is proved.

## 4. Round 2 (coordinator: slaved CROSS, order-free flatness, all-orders k8)
- (1) [P] SLAVED CROSS = CROSS, so there is nothing to size.
  In a slaved design, Ghat_XY = H_X (Mbb_XY) K_Y^T with Mbb = J (x) I + sum_r chi_r^X chi_r^Y^T (x) N_r.
  Each role meeting both X and Y adds exactly one rank-1 term on (X ∩ M_r) x (Y ∩ M_r), so the rank count is #{r meeting X and Y} >= 2c. That is CROSS verbatim.
  Slaving changes VALUES, never ranks. No new type row.
- (2) [P] TRIPLE LAW (order-free, no slaving needed, lambda != -1). For any 3 stages s,t,r, at least 3 roles contain >= 2 of them.
  Proof: suppose only roles A,B do. Pair coverage forces E_st = E_tr = E_rs = {A,B}, so Ghat_xy = H[x] K[y]^T on all 6 ordered pairs,
  and U_x W_y = eps_xy I with U_x = 4 alpha_x^-1 H[x] and W_y = K[y]^T beta_y^-1.
  Computing U_s U_t^-1 via W_r and via W_t, then W_s, gives eps_rs eps_rt = -eps_rs eps_rt (antisymmetry of eps only). Contradiction.
  This is the order-free core of the HUBPAIR kill: an uncovered triangle is impossible, in ANY call order.
  - Generalisation: a set S of m stages whose pairs are all covered by the same c roles needs c >= CROSS bound (~m), +1 at m=3. So TRIPLE ≈ CROSS + parity.
  - [C mp7] Sound on C1, c33, c12, c22, C1json (min slack 1).
  - [C mp8] Averaged row sum_r C(D,3)+C(D,2)(k-D) >= 3C(k,3):
    - HUBPAIR violates it for k >= 11.
    - LP values: k5/8/10 unchanged; k11 143.104, k12 143.238, k13 **143.252** (was 143.273), k16 142.809, k20 141.818.
    - Escape: a fractional 3rd deep role (D ~ k-2) covers most triples. The per-triple law needs placement, and averaging loses it.
- (3) [P+C] All-orders k8 sweep (mp6). 3450 dihedral classes of the RELAY-HALL-forced shape (aligned hubs excluded, CELL-RANK).
  - Exact GF(2) FLATNESS prefilter: within a cell U_s = ±U_cell. This is proved here: s, s' in one cell share >= 2 common non-chord partners at k8.
    So eps_st u_s w_t must depend only on the cell pair.
  - **3425/3450 DEAD [P]**. 25 pass; the reduced matrix system on them is tested numerically (scout; see mp6.log).
  - Numeric scout (mp6b): the 8-cycle placement already FAILS the GF2 test (an independent check of §2). Controls: negative 8-cycle stalls at 0.67; positive cross-only planted system 2e-7.
  - Exact mask laws on the 25 GF2 survivors: all DEAD (CELL-RANK at cells {01,23,45,67}, LOCAL-PIECEFIX, PC3).
  - **=> [P] The k8 nested-chain argmax type mix is DEAD in EVERY call order.**
    Chain of the proof: RELAY-HALL forces the shape; CELL-RANK kills aligned hubs; FLATNESS-GF2 kills 3425 of 3450 classes; mask laws kill the last 25.
    It is a type mix, not a type row: the LP still reaches it fractionally next to other types.
- NOT LOUD. The mid-k peak with TRIPLE is k13 143.252 (float dual; was 143.273). The bar needs about 10%.
