# EXTRATHIN ET (Nov 20, Opus; theory + Lean + float LP). Code et1 (symmetric LP, DEFICIT row), et2 (grouped LP, pair rows),
et3 (triangle + cross-set rows), et4 (two-cluster, all set rows), et5/et6 (general e=1 class patterns, all set rows |T|<=3; et6 adds
e and Qmin args), run7.sh batch. 1 proc at a time, threads=1. Lean: lean/decoder-duality/Nov15/CallerExtraThin.lean (runlean rc=0,
no sorry, axioms propext/Classical.choice/Quot.sound).
Why this differs from THINQ: THINQ bounded rank K_{s,rest} with THIN columns included (weak, leaves touch thins) and summed pair rows
with rhs 2-e. Here everything is on HOST columns only, the pair law is generalised to partner SETS, and the rank pattern of K_hh is
classified instead of averaged.

## 0. Verdict
(b) holds in the form "cover laws on host columns for every e" [P Lean], but (a) "WLOG e = 0" is FALSE at fixed k, and an
e-independent bound can only be a SUP over k, not HQ(k):
- [P] DIRECT SUM: frames C1 (k1, e1), C2 (k2, e2) give C1+C2 with k = k1+k2, e = e1+e2+2, F additive, chat = k-weighted mean.
  So any caller above the bar at k0 has copies above the bar at every multiple of k0: no large-k crossing (THINQ's k >= 81) can hold
  for unrestricted e. It is an e = 0 statement only. Even indecomposable e = 1 (TRIANGLE witness) stays above the bar to k120. (Same for Q < 0, T = 0, n < 2k-2: rank K > 2 there too.)
- [C, float LP] the minimal INDECOMPOSABLE obstruction is e = 1, the TRIANGLE pattern (below), with the proved law set
  (count, MAINS, DEFICIT, SET-RC2 all |T|<=3, leaf row): see table section 4. It beats sup HQ = 143.947 (k13) at k >= 18.
- Mechanism (not a cover failure): rank-3 K_hh lets three hubs each live on 2/3 of the stages; every pair still gets the coverage
  rank demands. The caller EMULATES an e = 0 caller at hub size h = 2k/3 with fewer leaves per stage (count n >= 2k-1 is spread over
  k > h stages). Excess over HQ is a count/leaf-granularity term, O(0.1-0.5), not a hub saving.

## 1. SET-RC2 [P, Lean CallerExtraThin.rc2_set]
For a stage s, any partner set T (s notin T), any l >= 2: if rho independent vectors lie in the column space of the strip
G_{s,T} = [G_st]_{t in T} (G_st = sum_r b_r[s] a_r[t]^T), then
  rho <= #{r at s : |M_r| >= l, |P_r(s)| < l, P_r(s) cap T = 0} + #{r at s : M_r meets T, |M_r| < l, P_r(s) cap T = 0}.
T = {t}, rho = 2 is CallerRC2.rc2_pair. rho = rank G_{s,T} is valid for every e (no frame hypothesis at all beyond the piece model).
Core: rc2_lin_rank (span contains rho independent vectors, instead of span = K^m). Non-vacuity: inst_set (+ inst_set_val: the deep
singleton is counted, = 1).
- Strip corollary [P]: T = H \ {s}, l = 2: deep singletons at s >= rank R_s, R_s = G_{s, H\s} (host columns only).

## 2. DEFICIT [P, Lean CallerExtraThin.deficit]
Kh = host block of K (indices (stage, slot)), diagonal 2x2 blocks invertible (lambda != -1). If stage s carries d_s independent
left-null vectors of its off-diagonal strip and d_{t0} = 0, then sum_s d_s + 2 <= rank Kh <= rank K <= 2 + e (sgForward).
With d_s = 2 - rank R_s (rank-nullity): if some stage has rank R_t = 2, then sum_s (2 - rank R_s) <= e; otherwise (k-1) <= e.
=> MAINS-DEEP-e [P]: total deep singletons >= 2k - e (k >= e+2). At e = 0 this is MAINS-DEEP (THINQ) again.
Non-vacuity: inst_deficit on Kh = 1 (k = 2, d = (0,2)) with inst_deficit_tight (rank 4): the bound is attained.
[C et1] MAINS-DEEP-e alone does NOT close e >= 1 (symmetric LP k13: e1 152.7, e2 158.8): the RC2_l (l >= 3) pair rows are the
binding laws, and those lose rank on singular pairs.

## 3. Rank patterns of K_hh at e = 1 [P]
rank K_hh <= 3 = U W^T. Stage s: point p_s = ker U_s, line L_s = row space of W_s (P^2), p_s notin L_s (K_ss invertible).
rank G_{s,T} = dim U_s(sum_{t in T} Pi_t) = 2, unless all t in T have the SAME line L and p_s in L (then 1).
So an e = 1 frame is a set of LINE CLASSES with point-on-line incidences. Examples: TWO (2 classes, cross rank 1 for every T inside the
other class), TRIANGLE (3 classes, p of class i = intersection of the other two lines; rank 1 only for T inside ONE other class),
NEAR-PENCIL, PATH. Pair-only rows see TRIANGLE as "2/3 of pairs rank 1"; set rows with T across two classes restore rank 2.
Also [P]: pairwise K_st = 0 stages (no common coverage) form a set of size <= 1 + e/2 (block-diagonal submatrix has rank 2|S|).

## 4. Pattern LPs [C float, HiGHS, column generation; rows count n >= 2k-2+Qmin, MAINS, DEEP, SET-RC2 (all T, |T| <= 3), leaf d1 <= kT]
(sup HQ = 143.947 at k13; HQ(k): k12 143.874, k15 143.831, k18 143.282, k20 142.787, k21 ~142.5, k24 141.668)
| pattern (e=1) | rows | k: chat |
| TWO | pair only | k16 144.176, k18 144.434, k20 144.517 (peak), k24 144.309, k32 143.075 |
| TWO | all sets | k12 140.868, k16 142.788, k18 143.087, k20 143.154 (peak), k22 143.066, k28 142.304  (< sup HQ, > HQ(k) for k >= 16) |
| TRIANGLE | pair only | k12 145.802, k15 147.656 |
| TRIANGLE | all sets | k9 137.731, k12 141.784, k15 143.430, k18 144.0046, k21 144.0425 |
| NEAR-PENCIL | all sets | k12 137.915, k15 139.588 |
TRIANGLE optimum (all sets): three all-main hubs, each on two of the three classes (mask (g,g,0) and rotations), + leaves; every
stage has 2 deep singletons, every within-class pair 2 coverers, every cross pair 1, every cross SET 2.
**[C exact] TRIANGLE witness (et7_exact.py -> et7.log)**: k = 3g, x = 1 on each of the three two-class all-main hubs (D = 2g),
d1 = max(2k-4, ceil(k(2k-6)/(k-1))) leaves, T = 2. Checked in integer arithmetic against EVERY row: count, MAINS, DEEP, leaf, and
SET-RC2 for all l in 2..k and ALL partner sets T of every size (rank from section 3); tightest set rows are tight (ratio 1).
chat (mpmath 60 digits): k15 143.429831, k18 144.004569, **k21 144.042543**, k24 143.791967, k27 143.380251, k30 142.877568,
k36 141.745774, k42 140.565416.  So the e = 1 law set admits an INTEGRAL type vector 0.0955 above sup HQ (k21) and above HQ(k) at
every k >= 15 (k21 +1.52 over HQ(21) 142.519; k42 +3.92 over HQ(42) 136.649).  It equals the float LP at k15/18/21 (the LP picks exactly this point).
[C exact, et7b.log] the witness stays ABOVE the bar 128.891 for every k = 3g <= 120 (k81 133.874, k120 129.007) and is below it
for all k = 3g >= 123 (checked to 9000). So THINQ's e = 0 crossing k >= 81 does not extend to e = 1: with one excess thin the
crossing moves to ~k123 (indecomposable frame), and to never for e >= 2 (direct sums).
Not run (stopped, not needed for the claim): run7.sh rows for TRIANGLE at k24-30 LP, Qmin = -e (count n >= 2k-2-e; can only
RAISE values), e = 0 'one' pattern with set rows (can only LOWER the e = 0 side). Both directions strengthen the obstruction.

## 5. Soundness on #7113 (types A/B)
Both types have e = 0 (THINQ tq7: A has T = Q = 4 QUERY; B's 4 IDLE_ODD pads are its thins, T = Q = 4). At e = 0 DEFICIT gives
sum d_s = 0, i.e. every strip R_s has rank 2: consistent with A's 4 deep singletons at every stage (tq7). rc2_set with T = {t} is
rc2_pair (qb3: 0 violations, tight). No #7113 stage is deficient, so nothing new is exercised there; the new laws only bite at e >= 1.

## 6. What it unlocks / next
- The caller program must quote the caller bar as a SUP over k for e >= 1 (direct sums), and handle indecomposable e = 1 frames by
  the same mid-k machinery as e = 0: the TRIANGLE is an e = 0-like caller at hub size 2k/3.
- To kill the TRIANGLE excess: either a law tying the count to hub size (leaves must touch thins: per-stage LEAF-RANK uses T = Q+1
  globally; a per-CLASS leaf law would restore the e = 0 leaf density), or show the 3-hub rank-3 K_hh is not D-exact (three
  hubs each meeting only 2/3 of the stages; cf. STAIRKILL cross-stage terms).
- Lean: the rank-nullity link d_s = 2 - rank R_s and the e = 1 incidence formula (section 3) are paper proofs, not yet in Lean.
