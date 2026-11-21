# LEANTHIN LT (Nov 20, Sonnet; Lean + exact certificates). Code: lt1 (own LP: Q>=1,e=0 'one' pattern, colgen), lt2 (dump duals), lt3 (INDEPENDENT
exact verifier: integer DP over ALL (D,partition), rigorous mpmath intervals), lt4 (row variants), lt5 (closed-form dual -> lt3), run_*.sh; logs
cert_final.log (LP duals k13,76..100,110,120), closed_all.log (closed-form dual k76..140,160,200). Lean: lean/decoder-duality/Nov15/CallerThinDel.lean,
CallerHPQ.lean (both runlean rc=0, no sorry/native_decide, axioms propext/Classical.choice/Quot.sound).

## 1. THIN DELETION + leaf_channel_thin [P Lean, CallerThinDel.lean]
Thin columns Th deleted from A,B by right-multiplication with the 0/1 diagonal hostD.  stage_sub: V_t - V_t^h = A E_t B^T, E_t = diag(1_{beta i = t, i in Th});
prod_rank: rank(P_t - P_t^h) <= #{thins in slots < t} (telescoping); **thin_deletion: P = -1 => rank(P_h + 1) <= |Th|**.
S1_le_live (S1_le with non-live slots = zero columns), kinj_host (lambda != -1 of a thin-free slot survives deletion), and
**leaf_channel_thin: #Lf <= |Hs| + |Th|** (k = #host slots, T = thins; leaves = roles vanishing off one slot on HOST columns; <= 2 columns/slot;
K-block of every host slot injective; full product -1).  Non-vacuity inst_thin: CallerThin's 1-host + 1-thin frame (A1,B1), all hypotheses checked.
So LEAF-CHANNEL d1 <= k + T (lambda != -1) is now fully kernel-checked (the TB.md §5 paper step is closed).  With n = 2k-2+T (e = 0): #non-leaf >= k-2.

## 2. Q >= 1, e = 0 crossing
LP (rows re-derived: DEEP, RC2_l c<=3, count n>=2k-1, LEAFAVG kn-d1 >= k(2k-2), LC #nonleaf >= k-2, TRIPLE-in-class) reproduces TRIBUILD (k13 143.5806, k77 128.8390).
**EXACT-rational certificates (lt3: dual y/2^110, exhaustive integer partition DP for every D<=k with rigorous rounded rpow, weak duality, eps absorbed by
shifting the LEAFAVG dual) [C exact]:**  k13 143.580633 (sup of the LP, float sweep k5..120 agrees) ;  k76 129.0076 (> bar) ;  **k77 128.839029 < 128.891 (first
crossing)** ; k78 128.672748, k79 128.508221, k80 128.345394, ... every k = 77..100, 110, 120 certified below the bar (margins .052 -> 5.97; cert_final.log).
## 3. Closed form (all k >= 77) [P Lean + C]
TRIPLE is NOT needed for the crossing.  Reduced LP = {DEEP, RC2_l (c=1, l>=3), LC, LEAFAVG} (count row has dual 0).  Its optimum is the chart
2 all-main hubs (D=k) + k^2/(k-1) leaves + (k-4) pure pairs:
  HQ2(k) = (104/k)[2k-2 + 2((8k+1)^s - 8^s k - 1) - (1-u1)k^2/(k-1) - (k-4)(1-v2p)],  u1 = 9^s-8^s, v2p = 17^s-16^s, s=.99.  HQ2(76)=129.0498, HQ2(77)=128.8814.
Dual = KASYM's chord dual (y_DEEP = wm, y_RC2_l = w_l/(k-1)) + y_LEAFAVG = mu = (1-u1)/(k-1), y_LC = nu = (1-v2p) - k mu  (>=0 for k>=77).  Key point: the leaf and the pure
pair are tight, so mu,nu are forced by the two equations leaf: u1 + mu(k-1) = 1 and pair: v2p + mu k + nu = 1; every D>=2 type then reduces to KASYM's role_le verbatim
(role value + RC2/(k-1) + wm*mains <= v2p), leaves contribute 0 to RC2 rows.  Weak duality = HQ2 exactly (algebra: 2k(T+wm) = 2hh(k)).
Lean CallerHPQ.lean (imports CallerHP): role_leQ (per-role incl. leaves), valQ_le_F2 (weak duality, k >= 77), F2_lt (HQ2-type bound < 128.891 for REAL x >= 77:
x^2/(x-1) >= x+1, then KASYM's F_anti with c = 2 v2p + (1-u1)/2, M_c(77) <= 0 and an rpow-enclosure evaluation at 77),
**valQ_lt: every Cfg with LawQ and k >= 77 has c^(.99) < 128.891**; cfgQ_law: for every k >= 4 the chart (2 hubs + (k-4) pairs + (k+2) leaves) satisfies LawQ; nonvac_77.
lt3 confirms the closed-form dual feasible over all types for k = 76..140, 160, 200 (bound = HQ2 to 6 digits, mode 'none': no slack at all).
LawQ rows: DEEP / RC2_{l>=3} / LC / LEAFAVG are the [P] laws of THINQ+TRIBUILD at e = 0, lambda != -1 (LC = leaf_channel_thin with n = 2k-2+T; LEAFAVG = leaf_rank summed over stages).
Scope: e = 0 (T = Q) only; e >= 1 is the direct-sum situation of ET.md (no k-crossing without indecomposability), TRIANGLE witness already dead (TB §0).
Margins: HQ2(77) is 0.0096 below the bar (TRIPLE would lower it to 128.839, LP-exact).  Not formalised: hypotheses LC/LEAFAVG are LawQ fields (their derivation from a frame
is leaf_channel_thin + CallerThin.leaf_rank, not wired into one frame-to-Cfg theorem), the Q>=1 frame -> Cfg bridge (as for CallerHP.frame_bound), TRIPLE row.
