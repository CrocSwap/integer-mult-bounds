# THINQ TQ (Nov 20, Opus; theory + Lean + exact LP). Code tq1-tq3 (float frame scouts), tq4 (Q>=1 type LP, colgen, e-branches + leaf rows),
tq5 (crossing scan), tq6 (exact dual certificates, mpmath-50, exhaustive partition DP), tq7 (#7113 soundness), tq8 (closed form).
Lean: lean/decoder-duality/Nov15/CallerThin.lean (rc=0 via runlean.sh, no sorry, axioms propext/Classical.choice/Quot.sound only).
Why this differs: QBRANCH assumed RC2 for Q>=1 without proof and had no leaf law. Here thins are modelled as width-1 blocks of CallerSGram's
(already general) frame, which gives the proof, and a new excess-thin parameter e = T - Q exposes the real remaining gap.

## 1. Thin normal form [P, Lean]
Frame = CallerSGram with columns = 2k host columns + T thin columns (QUERY / IDLE_ODD odd unit = rank-1 event), any time order; prod = -I.
- sgForward is already general: rank K + n <= 2k + T. With one host K-block invertible (lambda != -1): n + 2 <= 2k + T, i.e. **Q <= T**
  (thin_count). So Q >= 1 needs thins (QB §2 now proved, for any thin placement).
- e := T - Q >= 0 (excess thins). rank K <= 2 + e. **e = 0 (T = Q): rank K = 2 and the RC2 pair form holds verbatim for every l >= 2**
  (thin_G_blk_unit, rc2_pair_thin; same piece hypotheses as CallerRC2). Off-diagonal host blocks of K are still +-G_st; thin columns don't enter.
- e >= 1: Schur gives rank G_st >= 2 - e only [P]: pair form rhs 2-e (e=1: 1; e>=2: nothing).
- **MAINS-DEEP [P]** = RC2 at l = 2 in the thin frame: every stage has >= 2 singleton pieces on roles of DEGREE >= 2. Leaves never count
  (D=1 is neither deep at l=2 nor covers t). This is what QB's LP missed: its chart put all 2k mains on leaves. Dead at e = 0.

## 2. Degree-1 (leaf) laws
- **LEAF-RANK [P, Lean leaf_eig/leaf_zero/leaf_rank]**: if B^T x vanishes off time-slot s then V_s x = -x; with lambda_s != -1 this forces x = 0.
  Corollary: for any role set F whose B-rows vanish off stage s except on a column set Th: |F| <= |Th|. For leaves of stage s: |F_s| <= #thins
  touching F_s (B-side; A-side symmetric). A leaf with no thin is impossible (frame-level; EVENPHASE's leaf lemma needed P-pure).
  Taking Th = all other columns it is also a LOCAL COUNT |F| <= #columns outside one stage touching F.
  Non-vacuity: 1 host + 1 thin, n = 1 over Q (a genuine leaf, tight).
- [P] THIN DELETION: removing a rank-1 factor changes the product by rank 1, so the host-only product P_h has rank(P_h + I) <= T, any placement.
  In the hubs+leaves chart (2 hubs, 2 leaves/stage, hub blocks invertible) ker(P_h+I) meets the leaf space trivially => T >= d1 [P, that chart].
- [CONJ] global d1 <= T (tq3 float scout on chart masks k2-4: rank(P_h+I) <= d1-1 not reached, residuals ~1e-5 vs control 3.5e-6: WEAK).

## 3. Reduced LP for Q >= 1, e = 0 [C, certified]  (rows: count n >= 2k-1, MAINS, RC2_l l = 2..k, per-stage leaf row d1 <= k*T)
Optimum = 2 all-main full hubs + d1 = k(2k-4)/(k-1) leaves as count fillers (leaf deficit .0310 < pure pair .0376):
  **HQ(k) = (104/k)[2k-2 - 2(1 - (8k+1)^s + 8^s k) - k(2k-4)/(k-1) (1 - 9^s + 8^s)]**, = HP(k) + ~0.7..1.2.
- Exact dual certificates (tq6): k8 141.6307, k12 143.8745, **k13 143.9473 (sup; closed form max over 3..2e5)**, k14 143.9246, k16 143.6847,
  k80 128.9814 (above), **k81 128.8207 < 128.891 (first)**, k82 128.6617, k83 128.5042. Float LP = closed form at k20..96. HQ strictly decreasing
  k >= 13 (checked to 2e5). Crossing k >= 81 is [C] at 81-83, [CONJ] beyond (float + closed form; no closed-form dual proof).
- QB's 152.08 / crossing 178 is superseded for e = 0 (MAINS-DEEP kills the leaf-main chart).
- With the [CONJ] global leaf law: certified k13 143.0254, k72 129.0752, k73 128.8995, **k74 128.7257** => e = 0 ~ Q = 0 (HP crossing 74).

## 4. The real open gap: excess thins e = T - Q >= 1 [C float, tq4]
Each excess thin costs 104/k but kills coverage: e=1 LP 145.9 (k8) / 157.0 (k13) / 164.0 (k32); e>=2 (no cover law) 169.6 (k13) / 188.6 (k32)
(leaf mains + fillers); with the [CONJ] leaf law still 163 / 181. So the universal caller bar for Q >= 1 now hinges on a COVER law robust in e.
Tried: rowspace argument gives sum_s (2 - rank K_{s, rest}) <= e [P] but K_{s,rest} includes thin columns, which leaves touch => weak.
Next: a cover law on HOST columns only (e.g. via P_h with rank(P_h+I) <= T) or show e >= 1 frames are reducible (merge an excess thin into a host).

## 5. Soundness [C, tq7 on #7113]
Type A: n 36, k 17, Q 4, QUERY 4 => e = 0; 4 leaves (stages 7,8 two each) <= T; singletons on degree>=2 roles = 4 at every stage (>= 2); RC2 pair
form (QB qb3, 0 violations, tight). Type B: Q 4, 0 QUERY but 4 IDLE_ODD pads on the 4 leaves: the odd unit is the rank-1 thin => T = 4 = Q; consistent.
