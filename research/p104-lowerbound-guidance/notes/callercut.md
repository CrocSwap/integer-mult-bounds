# CALLERCUT CC (Nov 20, Opus; theory + exact LP). Own code: cc0.py (exact soundness on built frames), cc1.py (witness LP = sk2 base via bl5 + RC/RC2 rows), cc2.py (high-precision dual certificate, rows re-derived exactly), cc3.py (SIZING only, unproved pure-pair cap). Logs lp1-lp4.log, cert.log, cert2.log. 1 proc, threads=1. No Lean/advisor/kill/push.
Why this differs: CROSS/DYADIC/PIECE-CROSS cut STAGE sets; COVER/CLOSURE (BL) use inertness; ONE-RELAY/STAR (RB) are mask-level. RC2 is a cut over a ROLE set (relay set W = deep roles at s plus the shallow roles covering the pair), taken at every stage pair. It is type-expressible, holds in every call order, and needs no alignment or profile branching.

## 1. Law [P] RELAY-CUT RC2_l (model: RB §0 frame, Q=0, n = 2k-2, lambda != -1)
Notation: E_s = roles whose mask contains s; P_r(s) = the piece of r that contains s; "deep" means D_r >= l.
PAIR FORM. For all stages s != t and every l >= 2:
  #{r in E_s : D_r >= l, |P_r(s)| < l, t not in P_r(s)} + #{r in E_s cap E_t : D_r < l, t not in P_r(s)}  >=  2.
Proof.
- (a) Ghat_st (s != t) is invertible: Ghat_st = 1/4 eps alpha_s beta_t, alpha_s = Q_s^-1 (I + A_s), and lambda != -1 (BL 1, SK 1). Ghat_st = sum_{r in E_s cap E_t} bh_r[s] ah_r[t]^T, so 2 <= rank{bh_r[s] : r in E_s cap E_t}.
- (b) Let W = (deep roles in E_s) u (E_s cap E_t), so W ⊇ E_s cap E_t. Each multi piece q at s gives x_q with sum_r x_q(r) bh_r[s] = 0 (this is (Ghat xi_q)|_q = 0), supported on E(q) = roles whose mask ⊇ P_q. The x_q at a common stage are independent (biorthogonal to the y_q).
- (c) E(q) ⊆ W in two cases. If |P_q| >= l, every role ⊇ P_q has degree >= l, so it is deep. If P_q contains t, every role ⊇ P_q lies in E_s cap E_t.
- So rank B_s|W <= |W| minus #{such pieces}, which is exactly the left side.
AVERAGED (order-free type row). Sum over t != s, then over s, and divide by k-1:
  RC2_l:  sum_r ( [D_r >= l] * sum_{pieces L < l} L(k-L)/(k-1)  +  [D_r < l] * (D_r^2 - sum_L L^2)/(k-1) )  >=  2k.
- l = 2 gives "2 singletons per stage" (the MAINS count). l = k+1 gives SEPARATION. RC2 interpolates between them.
- A PURE shallow role adds 0. A deep role adds only through its small pieces.
- The weaker row RC_l (deep weight L, shallow weight D(D-1)/(k-1); min-over-t form) is implied by RC2.
Relation to ONE-RELAY: this is the c = 1 relay cut over role sets. The deep/shallow split is the only containment-closed role class a type LP can see.

## 2. Soundness [C exact, cc0]
- C1 (rb1), c33 (rb9, multi pieces), c12, c22, c11, B11_core (json; degree-1 pads dropped; singleton idles) all pass RC, HULL and the RC2 pair form for every (s,t,l).
- Min slack is 0 on every frame (tight), e.g. c33 at (s,t,l) = (0,3,4).
- On all-singleton frames the pair form follows from pair coverage. c33 is the only nontrivial check.

## 3. Witness LP [C, dual certificates; cc2 = duals -> Fractions, exhaustive DP, (8L)^.99 in mpmath-50]
Base = sk2 (ms9 coord,pfix,shal + DYADIC_J), reproduced as 134.050 / 142.837 / 148.859. Base + RC_l + RC2_l (l = 3..k):

| k | base (SK) | +RC2 (certified c^ <=) |
|---|---|---|
| 4 | 127.395 | 127.395 (float) |
| 5 | 134.050 | 133.8043 |
| 6 | 138.184 | 137.557 (float) |
| 8 | 142.837 | 141.3205 |
| 13 | 147.436 | 143.2731 (sup over k, float scan k = 4..24) |
| 16 | 148.859 | 142.8088 |
| 32 | 151.971 | 138.0881 |
| 64 | 153.483 | 130.3287 |
| 72 | — | **128.8501** < 128.891 |
| 80 | — | 127.4784 |
| 96 | — | 125.0467 |
| 128 | — | 121.0871 |

- Float scan: k = 9..24 gives 142.23, 142.79, 143.11, 143.25, 143.27, 143.21, 143.04, (16) 142.81, 142.62, 142.38, 141.82 (k20), 140.57 (k24). It peaks at k13 and decreases after.
- Certified near the crossing: k68 129.5859, k70 129.2202, k71 129.0373 (still above), k72 128.8501 (first k below the bar).
- Below the bar at every certified k >= 72 (72, 80, 96, 128). Uncertified k in 73..127 and k > 128 are [CONJ], from the monotone trend.

## 4. Remaining gap (where the LP now sits)
- Large k (>= ~72): below the bar [C at the certified k].
- Mid k (5..~70): sup 143.27 at k13. The argmax is the NP chart: 2 full all-main hubs + (2k-4) pure pairs (k10, k13).
  - That exact design is DEAD by CALLERLAW's HUBPAIR theorem (mask-level, Lemma A/E). A type LP cannot see this.
  - Sizing [cc3, NOT a law]: capping pure pairs at k, 0.5k or 0 moves k13 only 143.27 -> 143.17 -> 142.97. The LP substitutes pure triples plus 2-piece hubs relayed by 2 hubs (the PP / private-piece family).
  - So the next row must be a type-level form of PP / STAR: pieces whose only non-owner relays are a 2-role set C collapse (rank of owner rows <= 1). Combined with Lemma A's direct sum (sum_{t != f} rank A_t|S >= |S| for every role set S [P, CL 1]), that caps privately relayed pieces per stage.
- Order-free and alignment-free: RC2 needs neither, so RB's alignment conjecture is bypassed for this row. CELL-RANK alignment is still unproved and is not needed here.

## 5. Next
1. Type-level PP row: "relay pair C serving >= 3 private pieces at t => rank_A(owners) = rank_B(owners) = 1" + Lemma A on S = privately relayed owners. Size it with cc3-style caps first. The bar at k13 needs about -10%.
2. Lean: RC2 pair form is short linear algebra (rank of a sum of rank-1 terms <= rank of a row set minus independent kernel vectors). It fits next to Nov15/CallerSGram.lean.
3. Extend the certificates to k = 97..200 (cost ~k^3 per pricing pass).

## 6. Round 2 (coordinator: type-level PP/STAR + HUBPAIR rows)
- [P] STAR-PURE (type-free, stage-local). At stage t, let p_1..p_m (m >= 3) be pure roles (one piece = mask) with pairwise non-nested masks.
  Suppose all their relays E(q_i) \ {p_i} lie in one 2-role set C.
  Then every alpha_i beta_i = 1, and the rows b_{p_i}[t] are all multiples of one h, and the rows a_{p_i}[t] multiples of one g, so rank <= 1.
  Proof:
  - a_i = x_i|C != 0. Otherwise x_i = alpha e_p kills b_p on the whole mask, so bh_p = 0, which contradicts rank Ghat = n. Likewise b_i != 0.
  - b_i . a_j = 0 for i != j (p_j is not in E(q_i)).
  - With m >= 3 vectors in R^2, all a_i lie on one line l and all b_i on l^perp (RB STAR-3). So b_i . a_i = 0 and alpha_i beta_i = 1 != 0.
- [P] LEMMA-A DEFICIENCY (CL 1, projected onto a role set S): sum_{t != f} rank A_t|S >= |S|. Equivalently sum_{t != f} (2 - rank A_t|S) <= n - |S|.
- [P] HUBPAIR COUNT, the core of CALLERLAW 7/8 as a lemma. Take a design whose only non-pure roles are 2, with pure masks an antichain, and apply the two laws above with S = the pure roles.
  - At most 2 stages t != f have pure-row rank <= 1.
  - Every other stage carries exactly 2 pure pieces: m >= 3 collapses, and m <= 1 is deficient.
  - Hence sum_t m_t <= 2(k-3) + (pieces at 3 stages).
- [C] NO TYPE ROW from these.
  - The deep-set Lemma-A rows LA_l (sum_{D>=l} (sum_{L<l} L - 1) >= 0) are valid and do not move the LP (k8, k13 unchanged).
  - The STAR collapse needs the relay sets (placement), and its per-stage rank function psi(m) = 0,1,2,1,1,... is not concave. Averaging over stages puts psi back at ~2, so no linear row in type counts captures it.
  - HUBPAIR excludes isolated integral type points. Cutting such a point does not cut a neighbourhood of it.
- [C SIZING, decisive] Even forbidding ALL pure roles (every role >= 2 pieces; NOT a law, an upper bound on what any PP/HUBPAIR row could do) the certified-style LP stays at k8 140.98, k13 142.66, k20 141.11.
  - The mid-k argmax then becomes a NESTED SPLIT CHAIN: 13:(5|8) -> 8:(4|4) -> 4:(2|2) (+ 5:(2|3), 3:(1|2)), with all 2k mains on (1,1) chords.
  - So PP/HUBPAIR rows can buy at most ~0.6 at mid k. The bar needs ~-10%, i.e. a law on nested split chains / main placement (MAIN-DEPTH-type), not on pure pieces.
- [C certified, cc2, RC2 LP] k = 5..31: 133.80, 137.56, 139.87, 141.32, 142.23, 142.79, 143.11, 143.25, **143.273 (k13, sup)**, 143.21, 143.04, 142.81, 142.62, 142.38, 142.12, 141.82, 141.54, 141.23, 140.91, 140.57, 140.28, 139.97, 139.67, 139.34, 139.04, 138.72, 138.41.
  - Further certified points: k40 135.85, k48 133.81, k32 138.09, k64 130.33, k68 129.59, k70 129.22, k71 129.04, k56 131.99, k72 128.85, k76 128.16, k84 126.85, k88 126.22, k104 123.97, k112 122.95 k120 121.995. Below the bar at every certified k >= 72.
- NOT LOUD: max over k is 143.273 at k13. The caller-universal bar for every k is NOT reached.

## 6. Lean (LEANRC2, Nov 20) [P, Lean]: lean/decoder-duality/Nov15/CallerRC2.lean, notes in cards/WILD/NOVEL/leanrc2/NOTES.md
RC2 pair form (rc2_pair), its per-stage average (rc2_avg), and the SGram-frame bridge (rc2_pair_sg) are kernel-checked. Clarifications found: pieces must be
role-piece INSTANCES (one kernel vector per role-piece; with one vector per stage set, step (c)'s "|W| minus #pieces" is not the role count and a term sum_q(n_q-1) is missing);
the L(k-L) form of the averaged row additionally uses that a role's pieces partition its mask (not formalised; per-stage form is); x_q, y_q existence is the RB model (hypothesis).
