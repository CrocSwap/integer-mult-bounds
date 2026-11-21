# TRIBUILD TB (Nov 20, Opus; construction -> obstruction). Code: tb0 (float scout, inconclusive, superseded by tb2),
tb1 (= EXTRATHIN et6 + LEAF-CHANNEL row; LC=0 reproduces et6), tb2 (EXACT Fraction checks of the law + tightness),
tb3 (float frame scout of the witness; scout only). 1-2 procs, threads=1. No Lean / advisor / push.
Why this differs: EXTRATHIN priced the TRIANGLE with the averaged leaf row d1 <= kT (LEAF-RANK summed per stage). Here the
witness is taken literally (3 hubs + 2k-4 leaves + T = 2 thins) and the leaf/thin budget is computed GLOBALLY through the
host-only product, which is where it breaks. Not a cross-stage hub term.

## 0. Verdict: (b). The TRIANGLE witness is UNBUILDABLE for every k >= 7 [P], and below the bar for k <= 6 [C exact:
k3 86.71, k6 126.989 < 128.891]. NOT LOUD. The obstruction is a new k-uniform, pattern-free law (all e):
  **LEAF-CHANNEL [P]:  d1 <= k + T + sigma**   (d1 = degree-1 roles, T = thin columns, sigma = #stages with K_tt singular;
  sigma = 0 on the lambda != -1 branch used by THINQ/EXTRATHIN).  With e := T + 2k - 2 - n (the excess, as in ET/TQ):
  **#non-leaf roles >= k - 2 - e.**  The witness has 3 non-leaf roles and e = 1, so it needs k <= 6.

## 1. Proof (caller schema: k stages x 2 host columns, T thin rank-1 columns, any time order)
(1) THIN DELETION (TQ): P_h := host-only product (thins deleted) has rank(P_h + I) <= T.  So
    S := ker(P_h + I) cap U  (U = span of leaf coordinates) has dim S >= d1 - T.
(2) Reduction [P]. For x in S put y_0 = x, y_{t+1} = V_t y_t, c_t = B_t^T y_t in K^2. A leaf of stage t is touched only by V_t
    (host support law, bridged in CallerWord), so its final coordinate is x_t + (A_t c_t)_L = -x_t, i.e. x_t = -1/2 A_{L,t} c_t.
    Substituting: S ~= { c in K^{2k} : N_t c_t = 2 B_{H,t}^T u_t (all t),  u_k = 0 },  u_t := sum_{t'<t} A_{H,t'} c_{t'} (non-leaf
    "hub" state), N_t := 2I + B_{L,t}^T A_{L,t}. (x -> c is a bijection.) Equivalently S ~= ker K_hh cap ker Acal_nonleaf, where
    K_hh is the host block of K (leaf rows never meet two stages, so off-diagonal K blocks are hub-only).
(3) Sequential count. Pi_t = solutions of the first t block equations, K_t = {c in Pi_t : u_t = 0}, r_t = rank(Pi_t -> u_t).
    dim Pi_{t+1} = dim Pi_t - rho_t + a_t, a_t := dim ker N_t, rho_t >= 0.
    dim K_{t+1} = dim K_t + gamma_t, and an element of K_{t+1} has u_t = -A_{H,t} c_t, so N_t c_t = -2 X_tt c_t, i.e.
    c_t in Z_t := ker(K_tt + X_tt) (X_tt = B_{H,t}^T A_{H,t}, K_tt = N_t + X_tt); c_t -> A_{H,t} c_t is injective on Z_t, so
    gamma_t <= z_t := dim Z_t.  Telescoping (r_0 = 0, r_k >= 0): dim S = dim K_k = sum(a_t - rho_t) - r_k <= sum a_t.
    Also dim S = sum gamma_t <= sum z_t.
(4) Per stage a_t + z_t <= 2 if K_tt invertible (a_t = 2 => N = 0 => Z = ker 2X = ker K... = 0; a_t = 1 and z_t = 2 =>
    N = -2X, K_tt = -X of rank 1, contradiction).  Always a_t, z_t <= 2.
    => dim S <= min(sum a, sum z) <= k + sigma.  With (1): d1 - T <= k + sigma.  QED.
[C exact tb2.log] (i) dim S = dim(ker K_hh cap ker Acal) and (ii)-(iii) hold on 120 random/structured rational instances
(triangle chart, 2 leaves/stage, incl. K-singular stages), 0 violations. TIGHTNESS: an explicit host-only family (2 hubs,
2 leaves/stage, alternating injector Y = -2I / absorber Y = 2I, X = -2I, det V_t = 1) has dim S = k exactly at k = 2,4,6,8.
So host-level reasoning cannot improve k + T; TQ's [CONJ] d1 <= T needs the full frame (P = -I with thins / pieces).

## 2. Consequences
- TRIANGLE witness (d1 = max(2k-4, ceil(k(2k-6)/(k-1))), T = 2): needs 2k-4 <= k+2, so k <= 6. k6: d1 = 8 = k+T (tight),
  chat 126.989 < bar. => the e = 1 indecomposable obstruction quoted in ET §4 (k21 144.0425, above bar to k120) is DEAD.
- It generalises to every e and every pattern (not only indecomposable): direct sums satisfy it with slack 2.
  It also cuts THINQ's HQ chart (2 hubs + ~2k-2 leaves, T ~ 2: needs k <= 4).
- LP effect [C float, HiGHS colgen, tb1.log; rows = ET's + LC]:
  | pattern | k | ET (no LC) | + LC |
  | tri e1 | 9 | 137.731 | 137.509 |
  | tri e1 | 12 | 141.784 | 141.451 |
  | tri e1 | 15 | 143.430 | 143.030 |
  | one e0 (HQ chart) | 12 / 13 | 143.875 / 143.947 (HQ) | 143.625 / 143.672 |
  | tri e1 | 18 / 21 | 144.005 / 144.043 | 143.560 / 143.566 |
  | two e1 | 18 / 20 | 143.087 / 143.154 | 142.643 / 142.687 |
  So after LC every e = 1 pattern LP sits BELOW the e = 0 LC value (143.672 at k13) and below old sup HQ 143.947 [C float].
  The LP escapes by replacing leaves with PURE PAIRS inside a class (mask 2 stages of one class, one 2-piece). With LC the
  triangle is no longer above the e = 0 sup: the "e = 1 excess" was entirely the leaf-filler.
- Next law for the pure-pair escape [P, paper]: TRIPLE holds WITHIN a class at e = 1 (stages of one class have invertible
  U_s W_t^T blocks since p_c is not on L_c; MP §4(2) proof verbatim with eps antisymmetric), so every class triple needs a
  third role covering >= 2 of its stages; the LC optimum at k15 (9 pure pairs all in one class) violates it. Within a class
  the design is a 2-hub slaved e = 0 design, so FLATNESS (MP §2) applies too. Not yet added as LP rows.

## 3. Build attempts (scout only)
tb3 (float LM, frame level: P = -I with 2 dense end thins, det K_tt, det V_t barriers): stalls at 2.6e-4 even for k3 (d1 = 2,
inside the LC bound) and at 5e-3..2e-2 with wrong counts. The scout is too weak to decide anything and was stopped; no build
claim either way below k7. Above k6 the law makes building pointless.

## 4. Next
- Add TRIPLE-in-class (and FLATNESS) rows to tb1 for the pure-pair escape; rerun 'one' e0 + LC across k to get the new HQ sup
  and bar crossing (LC moved k12/k13 by -0.25/-0.28).
- Lean: the reduction S ~= ker K_hh cap ker Acal and the telescoping count are short linear algebra; worth a CallerLeafChannel.lean.
- Try to lift LC to full frames (thins + pieces) toward TQ's [CONJ] d1 <= T.

## 5. Round 2 (coordinator): scans with LC + TRIPLE, Lean
Code tb4.py = tb1 + TRIPLE-in-class averaged rows (TR=1): per class c, sum_r C(a_c,3) + C(a_c,2)(g - a_c) >= 3 C(g,3).
- [P] TRIPLE-in-class (any e): for stages s,t,r of one line class, G_xy = eps_xy U_x W_y^T with U_x W_y^T invertible (the class
  point p_x is not on its own line L_c, i.e. K_xx invertible), so MP §4(2)'s eps-antisymmetry contradiction applies verbatim:
  every same-class triple meets >= 3 roles in >= 2 of its stages. For m = 1 (e = 0) this is MP's TRIPLE row.
- [P] within-class FLATNESS adds NO order-free row: an uncovered same-class 4-set whose 3 pairings include the interleaving
  one would need K4 in the uncovered graph, already excluded by TRIPLE (triangle-free); C4s are order-dependent (MP: no type row).
- TURAN (INTCALLER) not added: it is a drop-two-roles integer row, not a type-LP row; SPARSE not added: it is a Q = 0 gauge law
  (roles form a basis of Z), false with thins (leaves inside one stage). LC is its thin-aware replacement.
Results [C float, HiGHS colgen; logs tb4_one.log, tb4_q0.log, tb4_tri.log, tb4_two.log]:
- e = 0 (Q >= 1, 'one' pattern, LC+TRIPLE), every k = 5..120: sup k13 143.5806 (HQ was 143.947); k72 129.697, k76 > bar,
  **k77 128.839 < bar = first crossing, below for all k = 77..120** (HQ was k81).
- Q = 0: LC is vacuous (T = 0 forces d1 = 0 by LEAF-RANK), so HP/KASYM is unchanged: crossing k74 [P Lean CallerHP]. The et6
  row family at Qmin = 0 gives the same numbers as Q >= 1 (k13 143.581, k74 129.348), i.e. weaker than HP's closed form
  (HP(74) = 128.769): the Q >= 1 crossing 77 would move toward 74 if KASYM's role-count rows were added to tb4.
- e = 1 TRIANGLE (X = 2 set rows, LC + TRIPLE-in-class): k6 126.989, k9 137.509, k12 141.451, k15 143.017, k18 143.537,
  k21 143.536, k24 143.257; peak about 143.54, below the e = 0 sup 143.581. The sweep was stopped at k24 (cost grows with g), so there is no e = 1 crossing yet.
  TRIPLE-in-class effect: k15 -0.013, k18 -0.023, k21 -0.030 (small; e = 0: k13 143.672 -> 143.581).
- 'two' (e = 1) and e = 2: not run in round 2. For e = 2, direct sums of e = 0 frames give the k-weighted mean of their values, so there is no k-crossing
  without an indecomposability hypothesis; the LC row there reads #non-leaf >= k - 4.
- Lean: Nov15/CallerLeafChannel.lean BUILT (runlean rc=0, 12 s, no sorry/native_decide), axioms propext/Classical.choice/
  Quot.sound for count_le, reduce_le, S1_le, leaf_channel, inst_channel, inst_tight. leaf_channel: #Lf <= k + rank(P_h + 1)
  (λ ≠ -1 at every stage, <= 2 columns per stage). Thin deletion rank(P_h + 1) <= T stays a paper proof. inst_tight: a k = 2 instance where the
  2-dimensional leaf space lies in ker(P + 1), so the bound is attained.
