# DYADRELAY DR (Nov 20, Opus; theory + exact IP). Own code: dr0/dr0b (sizing, LP duals), dr1 (RC2Y), dr2 (SUBDY), dr3 (weighted SUBDY),
dr4 (SUBDY + MASKK13 SPARSE_u), dr5_sound (frames). All on top of INTCALLER ic1/ic3/ic4 (imported, unmodified). 1 proc, threads=1.
Why this differs: CC/KA/IC used only the GLOBAL dyadic tree (DYADIC_J) and per-pair relay cuts (RC2). Here CROSS is applied on the dyadic
tree of an ARBITRARY stage set M (local CROSS), then averaged over random M into a type row. RC2 is generalised from a stage t to a stage set Y.

## 0. Sizing at k71 [C, dr0]
IC IP 129.0349. Dropping DYADIC_J alone -> 129.2531; dropping every extra row -> HP 129.2982. So DYADIC_J carries 0.218 of the 0.263 below HP.
The argmax meets DYADIC_J with cheap pure dyadic roles (2x 32:32, 4x 16:16, 3x 8:8, 6:6). Equal-value face: hubs are 2-piece or singleton.

## 1. [P] RC2Y (set-relay cut; generalises RC2_l)
For stage s, nonempty Y in [k]-{s}, l >= 2:  #{r in E_s : |P_r(s)| < l, P_r(s) cap Y = 0, (D_r >= l or (M_r - P_r(s)) cap Y != 0)} >= 2.
Proof: W = deep_l u {r in E_s meeting Y} contains E_s cap E_t (t in Y), so rank B_s|W = 2 (Ghat_st invertible). Pieces at s with
|P| >= l or P meeting Y have E(q) in W; their x_q are independent and kill B_s|W. The untrapped roles lie in the set counted.
Averaged over uniform y-subsets: sum_r sum_L L g(L,D) >= 2k, g = [D>=l][L<l] C(k-L,y)/C(k-1,y) + [D<l](C(k-L,y)-C(k-D,y))/C(k-1,y).
y=1 is RC2_l; y=k-1 is "ones". [C dr1] INERT: k20, k71 unchanged. Coefficients are linear in y for L <= 2, and the argmax only uses pieces 1, 2
on small-l rows (it is exactly tight for all y at l=3).

## 2. [P] PIECE2-CROSS (strengthening of SK CROSS)
For disjoint X, Y with c = cyclic alternations: #{r : M_r meets X and Y, and no piece of r contains X and meets Y} >= 2c.
Proof: rank G_XY = 2c (SK). It is at most dim span{b_r[X] : r in R(X,Y)}. A piece q with P_q >= X and P_q meeting Y has E(q) in R(X,Y), and x_q kills
b on P_q >= X. These pieces share X, so their x_q are independent (biorthogonal). Same with X <-> Y (y_q kills a).
X = {s} gives the shallow part of RC2Y. PIECE-CROSS (SK 3) is the variant with W = R(X,Y) u E(X).

## 3. [P] SUBDY_{d,J} (local dyadic CROSS, averaged): the new row
For EVERY stage set M (|M| = d), list M in call order m_0 < ... < m_{d-1}. Level l <= J: Z = {m_i : i = j mod 2^l}, X = even-indexed half, Y = odd half.
Then c(X,Y) = floor(|Z|/2), since X and Y alternate perfectly (cyclically too). CROSS at each node, summed over the tree:
   sum_r branch_r(M) >= R_J(d),   with branch_r <= (min(|M_r cap M|, 2^{J+1}) - 1)^+   (binary-tree branching bound, any placement).
|M_r cap M| ~ HG(k, D_r, d) for uniform M, independent of placement. So we get the type row
   SUBDY_{d,J}:  sum_r E_{i~HG(k,D_r,d)} (min(i,2^{J+1})-1)^+  >=  R_J(d).     (d = k: DYADIC_J; d = 2: pair coverage.)
Why it is stronger: in the global tree pure pairs earn credit 1 each. In a random d-set a pair earns d(d-1)/(k(k-1)), but hubs keep min(d,2^{J+1})-1.
So local trees need medium-degree roles; pure pairs cannot carry them.
[C dr3] Level-weighted variants (max over class profiles n_{l+1} <= min(2n_l, 2^{l+1}, i)) add nothing at k71.
[P, not used] Piece awareness inside SUBDY hurts a pure role only at nodes with X inside its mask. Under max-over-placement that bites only when
|M_r cap M| > d/2, so it is inert for pure roles with D < k/2.

## 4. Soundness [C exact, dr5_sound.log]
C1, c33, c12, c22: every node of every local tree (all M, all J, both orientations) passes PIECE2-CROSS (0 violations; 10/258/10/34 nodes).
Per-set SUBDY min slack 0; SPARSE (all U) min slack 0. All averaged rows (ic1 + SUBDY + SPARSE) pass via the ic2 checker.

## 5. Results [C: HiGHS MIP gap 1e-10, optimum disaggregated and re-verified row by row in Fractions]
(filled from dr4_k5_71.log below)
Full log: dr4_k5_71.log (IC rows + TURAN + PARITY + SUBDY_{d,J} for all d=2..k, J<=ceil(log2 d)-1, + SPARSE_u). Every k=5..71 disaggregates exactly, with all rows OK.
| k | IC (INTCALLER) | + SUBDY + SPARSE | gain | above bar by |
| 5-13 | = | = (k13 143.1905 sup, unchanged) | 0 | |
| 16 / 20 / 21 | 142.8016 / 141.8088 / 141.52 | 142.7529 / 141.7212 / 141.4263 | .049 / .088 / .094 (max) | |
| 32 / 40 / 48 / 56 / 64 | 138.0828 / 135.8480 / 133.8015 / 131.9864 / 130.3287 | 138.0473 / 135.7902 / 133.7546 / 131.9360 / 130.2904 | .04-.06 | |
| 66 / 68 / 69 / 70 / 71 | 129.9574 / 129.5859 / 129.4053 / 129.2170 / 129.0349 | 129.9056 / 129.5292 / 129.3411 / 129.1577 / **128.9773** | .05-.06 | 1.01 / .64 / .45 / .27 / **.086** |
- The gain is 0.035-0.094 for every k >= 14 (about 0.05%). k71 is left 0.086 above the bar. NOT LOUD: no k closes, and the >= 72 theorem is not extended.
- [C] SPARSE_u (MASKK13, averaged): INERT at every k tested (5-20, 30, 40, 50, 60, 66, 71; dr4_sparseonly.log). The expected number of roles inside a random u-set is
  about 2u^2/k for pair-heavy designs, far below 2u-2. SPARSE kills the k13 Turan face only through placement (a specific U), and averaging loses that.
- New argmax (k66-71): the dyadic sizes are gone. Big pure roles of degree ~k/6-k/2 (31:31, 30:30, 29:29, 23:23, 11:11) plus single-big-piece roles (31:27|2|2, 27:14|11|2).
  The binding local rows are SUBDY_{36,1} and SUBDY_{32,2..3} (LP duals, dr0b).

## 6. What is left / next
- The obstruction is PURE (or one-big-piece) medium roles. Every CROSS/RC2 family credits them in local trees, or traps them only when they contain a whole class X.
  Under type averaging (max over placement) that happens only for D > k/2. So no CROSS-type type row can price them [P-sketch, sec 3 last bullet].
- The needed law is about their RELAYS. A pure role P has b_P|M_P and a_P|M_P in the span of its relays (roles containing M_P, all of degree > D_P).
  Next row to try: a SPARSE/CELL-RANK-type count on nested pure chains, i.e. pure roles inside U versus relays containing U (PURE-CELL saturation, RB 1),
  averaged over random U. The SPARSE average shows plain counts are too weak, so it must be the PURE-CELL / SATURATED-CELL form (pure roles inside U together with relays inside E(U)).
- k71 needs only 0.086 more (0.07%). Any valid row costing more than about 1.5 pure roles at k71 closes it.
