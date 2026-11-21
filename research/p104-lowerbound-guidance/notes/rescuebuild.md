# RESCUEBUILD RB (Nov 20, Opus; construction + theory).
VERDICT: (b), NOT LOUD. No caller frame beating the bar was built at k=5 or k=6.  Every relay-rescue design at the top of the
mask-level sup (k5 133.804 plateau, k6 best 131.871, CS's k6 .01-breaker 137.557) is DEAD by exact laws [P].  The failing
equation is the stage-wise biorthogonality y_q . x_q' = 0 restricted to the shared relay roles: a relay set C serves at most
|C| pieces per stage with a nonzero relay pairing; with 3+ pieces on a 2-role relay all relays collapse to ONE combination h
of the relay rows (STAR-3), and zero sums along the relayed pieces then force h = 0.  Open: lower-value k=5 survivors
(129-130 > bar) pass every law incl. STAR-EXT and are being tested numerically (all stall so far); k>=7 not reached.
Own code: rbcore.py (design model, exact invoice, numeric frame+piece solver: fixed rational-ish walk, analytic-Jacobian LM),
rb1-rb4 (controls), rb5 (type multisets), rb6/rb7 (CP-SAT mask-level enumeration under proved laws, no-good + dihedral dedupe),
rb9 (c33 frame), rb10 (numeric build attempts), rb11 (built frames pass all encoded laws). 1-2 procs, threads=1. No Lean/advisor/push.
Why this differs: SK/BL/MAINSCAN priced TYPE rows (mask-free LP). This lane works at MASK level: it enumerates actual
designs (masks + labelled pieces + call order) above the bar under every proved mask-level law, then tries to BUILD each one
(frame + all piece vectors) and records exactly what fails.

## 0. Model (frame level)  [P, from BL 1 + SK 1]
Frame <=> walk Q_t (SL2, Q_0=I, Q_k=-I) and two bases {ah_r}, {phi_r} of Z (zero-block-sum vectors in R^{2k}) with
phi_r . ah_o = delta_ro, supp ah_r in M_r, supp (Ghat phi_r) in M_r   (then bh_r = Ghat phi_r, Bh^T Ah = Ghat P_Z = Ghat).
Pieces: xi_q in span{phi_r : r in E(q)} with (Ghat xi_q)|_q = 0; eta_q in span{ah_r : r in E(q)} with eta_q|_q = 0;
eta_q . xi_q' = delta for pieces sharing a stage.  (x_q, y_q are the coordinate vectors of xi_q, eta_q.)
E1 / E1~ (the D-polynomial identities of D3 1) are NOT imposed: every BUILD claim below is frame-level.

## Controls
- #7113 invoice 105.94742 (s=.99) reproduced by CALLERINV ci1 (role-piece objective = invoice).
- C1 (k3) frame: solves at generic fixed walks, prod V = -I to 1e-13 after mapping back (rbcore.to_real).
- c33 frame (k6, degree-1 pads dropped; HAS multi pieces {2,3} x2 and pure pairs {4,5} x2): solves at generic walks.
- Dead controls stall at O(0.1): K4 #3, K4 #4 (K4BUILD), C1 with a (k-1)-piece (PIECEFIX x=k-1).

## 1. New mask-level laws (all proved from the model in 0; built frames C1, c33 pass all of them [C rb11])
- [P] CELL-RANK. Disjoint cells X_1..X_m; S = roles whose mask is a union of cells. Then |S| <= sum_i (|E(X_i)| - pi(X_i)).
  Proof: x_q (q >= X_i) are independent (common stage), supported on E(q) in E(X_i), and kill Bh|X_i; so V_i = span{bh_r|X_i : r in E(X_i)}
  has dim <= |E(X_i)| - pi(X_i); every r in S has bh_r in (+)V_i; the bh_r are independent.
- [P] LOCAL-PIECEFIX. For X and T in X^c: #{pieces q >= X : (U_{r in E(q)} M_r) - q in T} + #{roles with M_r in T} <= max(0, 2|T|-2).
  Proof: u_q = Bh^T x_q is a nonzero zero-sum vector vanishing on q, supported on (U_{E(q)} M_r) - q; with the bh_r of roles inside T
  they are independent in Z cap R^T.  (T = X^c gives PIECEFIX; x = k-1 forbids (k-1)-pieces.)
- [P] PC3 (piece-aware CROSS). rank Ghat_XY = 2c(X,Y) <= |R(X,Y)| - #{pieces q >= X : every role containing q meets Y} (and X<->Y).
  The mask-level form of CSL-WITNESS; contains PIECE-CROSS for pieces >= X u Y and SEPARATION.
- [P] PURE-CELL. If #{roles with mask exactly X} >= dbar := |E(X)| - pi(X), then V_E(X) lies in Z_X (zero sum on X), so
  #{mask = X} + #{r >= X with |M_r - X| = 1} <= dbar and #{roles meeting X without containing it} >= 2.
  (Pure-on-X roles are independent zero-sum vectors in V_E(X); the one-extra-stage roles then have a zero extra block.)
- Also encoded (from the notes, mask-level): mains 2/stage, CROSS, PIECEFIX, RESCUE, ADJ (linear), e-row, SPAN on every set partition.
Calibration [C rb7]: at k=4 the encoded mask-level laws give max 127.395 = W_4 (CALLERINV); before PC3/SPAN/e they allowed 129.842
(and all such k4 designs stalled numerically).
- [P] SATURATED-CELL (the relay-saturation law; answers "which equation fails"). If #{mask = X} >= dbar = |E(X)| - pi(X), the y_q
  (q >= X) span the WHOLE left kernel of Ah_E(X)|X, so biorthogonality eta_q . xi_q' = 0 forces x_q'|E(X) into col(Ah_E(X)|X);
  the pure-on-X rows vanish on q' (q' not inside X), and they span that column space, so x_q'|E(X) = 0 (same for y_q').
  => every piece q' meeting X but not inside X is relayed ONLY by roles containing q' but not X: needs >= 2 of them, or one
  with >= 2 stages outside q' (a single one with <= 1 outside stage is inert on q' and then zero by zero-sum).
  Failing equation: the biorthogonality block Y_X^T x_q' = 0 at a shared stage (y_q supports fill E(X) cap E(q')).

## 2. Builds at k=5 (frame level)
- [C rb16, CP-SAT exact on integer-scaled values] mask-level sup under section-1 laws minus SATURATED-CELL: 133.804 (type LP 134.05).
  Argmax = 2 hubs {01234} pieces (01|23|main4), (04|12|main3) + chords 01,04,12,23 + 2 pure pairs {34}: the relay-rescue pattern
  (hub pieces relayed by chords and by the other hub).  Build: fixed generic walks stall (9e-2), joint walk/frame LM stalls,
  Delta-zero(3,4) walks stall (0.26).  Exact kill [P]: PURE-CELL at X={3,4} (two pure pairs, dbar = 4-2 = 2) saturates, so
  SATURATED-CELL hits H1's piece {2,3}: the only role containing {2,3} but not {3,4} is chord 23 -> chord 23 = 0. DEAD.
- Generic-walk scans are NOT sufficient: the coordinate version of design #1 (129.134) stalls at every generic walk (1e-2) but
  BUILDS at a special walk found by joint walk+frame LM (residual 9e-12, prod V + I 4e-9, traces -3.66,-4.99,-4.77,-5.48,0.35).
  Reason [P]: pairs served only by Laplacian-type contributions (degree-2 roles, or roles forced zero-sum on the pair) force
  Ghat_st = Ghat_ts (BL PAIR-SYMMETRY), a codimension-4 condition on the walk.
- [P] SATURATED-CELL v2 (used in rb6): under saturation of X, a crossing piece q' has x_q' supported on I = E(q') - E(X), so
  u = Bh^T x_q' is a nonzero zero-sum vector on (U_{o in I} M_o) - q': this set needs >= 2 stages.  (Kills the second 133.804
  argmax: 2 hubs (02|14|3) + 2 pure pairs {01} + chords 02,02,14,14 - X={01} saturated, piece {02} relayed only by the two
  chords 02 whose masks lie inside {02}.)
- [P] STAR-3 (one relay PAIR serves <= 2 pieces per stage two-sidedly). At a stage t let pieces q_1..q_m (m >= 3) have
  E(q_i) = C u {o_i}, |C| = 2, o_i distinct, o_i not in C, and a_i = x_i|C, b_i = y_i|C all nonzero (else o_i is inert on q_i).
  Biorthogonality gives b_i . a_j = 0 (i != j); with m >= 3 this forces all a_i onto one line l and all b_i onto l^perp.
  Hence bh_{o_i}|q_i = s_i h|q_i and ah_{o_i}|q_i = s'_i g|q_i for ONE pair h = u.Bh_C, g = v.Ah_C: the two relays act as one.
  (Kills the third 133.804 argmax: hubs H1 (01|m2,m3,m4), H2 (02|34|m1), chords 01,02,34, pure pairs 03,04,12.  At stage 0 the
  four pieces 01,02,03,04 all have E = {H1,H2} u {own}; collinearity + masks = pieces give c01,c02,p03,p04 proportional to h on
  their pairs; zero sums force h[j] = -h[0] (j=1..4), then sum h = -3h[0] = 0, so h = 0 and those roles vanish. DEAD.)
- [P] ONE-RELAY (c = 1 case of the same computation). Pieces q, q' at a common stage with E(q) n E(q') = {o}: y_q[o] x_q'[o] = 0.
  So among pieces relayed through a single role o at one stage, at most ONE is relayed on both sides; the others are relayed on
  one side only (the owner's B- or A-row vanishes on that piece).  General capacity [P]: if pieces at a stage have pairwise
  E-intersections inside C (|C| = c), at most c of them have x_i|C . y_i|C != 0, and with A = span x_i|C, B = span y_i|C,
  dim A + dim B <= c + #{i : x_i|C . y_i|C != 0}.  This is the quantitative replacement of the LP's "one relay per stage
  rescues any number of big-piece roles".
- [P] CS k6 counter-design is DEAD (any call order). CALLERSHAPE's k6 design (137.557; the smallest design that breaks .01 under
  X112; hubs H1 (1)(2)(34)(05), H2 (1)(03)(24)(5); pure 12,13,14,25; chords 03,05,24,34) passes every encoded mask law in 4 orders
  [C rblaw], but STAR-3 kills it: at stage 1 the pieces 12,13,14 and at stage 2 the pieces 12,25,{24 of H2} each have
  E = {H1,H2} u {own degree-2 role}; piece 12 is shared, so ONE combination h of the hub rows carries all five relays.  The
  degree-2 roles are multiples of h on their pairs, so h_a = -h_b on each edge of {12,13,14,25,24}; the triangle 1-2-4 forces
  h = 0, so p12 = 0. Contradiction. (CS had marked it killable only by an unproved PAIR-ADJ extension.)
- PAIR-RELAY pattern [P, the general mechanism]: when two roles C relay >= 3 pairs at each stage of a connected family of pair
  pieces whose relay-partners are the degree-2 roles on those pairs, all relays share one h, h alternates sign along the pair
  graph, and (h in Z) an odd cycle, or a bipartite graph with a full-mask zero-sum mismatch, forces h = 0.
- [P] STAR closure. Once a class has its line l (a's on l, b's on l^perp, all nonzero), any further C-relayed piece sharing a
  stage with a member (distinct partner, so the E-overlap is C) satisfies b_member . a_q = 0, so a_q is on l too: classes
  propagate along shared stages and merge. (Kills the 4th 133.804 design: stage-0 star {01,04,03} and stage-2 star {23,12,24}
  are linked at stage 1 by pieces 01 and 12, so one h obeys h1=h3=h4=-h0, h2=2h0 and h1=h3=h4=-h2, h0=2h2, forcing h = 0.)
  Implemented exactly (Fractions) as rblaw.star_zero: per relay pair C, classes by closure, then the scalar block-sum system
  {sum_{s in q} h_s = 0 for partners with mask = q; sum_s h_s = 0; h_s = 0 off supp C}; kill if some q is forced h|q = 0.
  Premises: pieces with E(q) = C u {o}, |M_o - q| <= 1 (so a, b != 0), distinct partners per stage.  C1, c33 pass.
- [P] STAR-EXT. With a class (line l) for relay pair C: a piece q with E(q) >= C sharing a stage with a member p where
  E(p) n E(q) = C gets a_q on l, b_q on l^perp; then every member p' at a shared stage with E(p') n E(q) = C u {o_p'}
  forces x_q[o_p'] = y_q[o_p'] = 0 (because b_q . a_p' = 0 and the partner coefficient of p' is nonzero, as b.a = 0 on
  members).  If a single role o is left outside C and M_o = q, o's row is c.h|q with c != 0: q joins the class with a
  zero-sum row.  (Kills the k6 mask-level best 131.871 [hubs Ha all-main, Hb (0135|24); pure 012, 0245, 1235, 03, 13;
  0135 all-main; 024 (0|m2,m4); 235 (25|3)]: the class {012, 0135, 0245, 1235} gives h = (1,-2,1,2,-1,-1) x omega, and the
  pure pair 03 joins with h_0 + h_3 = 3 omega != 0, so p03 = 0.  Numerics agreed: fixed-walk residual stuck at 1.00 with
  rows 0135, 03, 13 collapsing to zero.)

## 3. Status of the search (logs in this dir)
- k=4 [C]: mask-level sup under section-1 laws = 127.395 = W_4 (calibration; < bar anyway).
- k=5 [C]: CP-SAT sup 133.804 (type LP 134.05).  The 133.804 plateau = 2 full hubs with 2-pieces + 6 degree-2 roles (chords /
  pure pairs): 87+ signature classes cut, every one by STAR-ZERO (rb22_k5_v3.log); hand proofs for 4 representatives above.
  Above-bar feasibility CEGAR with STAR-EXT (rb22_k5bar.log, running, CONT=1) lists SURVIVORS at 129.2-129.9 (22 when written,
  none STAR-killed); numeric follower rb24_k5.log: every one tested so far stalls (fixed generic walks AND joint walk LM).
  Inspection of the 129.213 survivor (rb25): the pure pair {0,4} collapses (x = e_p04): its relay pair {H,B} meets three
  co-stage pieces (02, 01, 012) whose relay parts must be collinear, a STAR variant with one star piece. Not yet a law.
- k=6 [C]: CP-SAT (55 min) best 131.871, bound 137.557 (not closed; type LP 138.184); the best is STAR-EXT-dead (above).
  The CS k6 design (137.557) is STAR-dead in every order.
- k=7, 8: not run. The full CP-SAT model is too large (cell families ~ (k+1)^k); rb23.py (light model + full lazy checks with
  rblaw + STAR) is written, untested.
- Generic-walk scans miss designs that need special walks (section 2); every "stall" above used fixed generic walks plus the
  joint walk/frame LM, so a stall is numerical evidence only, not a proof.

## 4. What it unlocks / next
- The LP's escape ("one relay per stage rescues any number of big-piece roles") is false at mask level: relay capacity per
  stage is |C| (ONE-RELAY, STAR-3, capacity bound), and saturated cells block relaying altogether (SATURATED-CELL).
- These are mask-level laws; the type LP is mask-free, so they cannot be plugged into sk2/bl5 as type rows. The mask-level
  CP-SAT (rb6 build + rb22 CEGAR) IS the replacement program for small k: sups above.
- Next: (1) turn the 129.213 collapse into a law (STAR with one star piece + a collinear triple), add it to rblaw, re-run
  rb22 CONT; if the survivor list empties, k=5 is closed [C+P]. (2) Run rb23 at k=7,8. (3) Exactify any numeric build.

## 5. Continuation (coordinator round 2)
- [P] TRIANGLE seed (added to rblaw.star_zero): STAR-3 needs only b_i.a_j = 0 for i != j, so three C-relayed star pieces
  that PAIRWISE share a stage (distinct partners) already force the collinear collapse; classes then grow along co-stage edges.
- The 129.213 / 130.866 collapses are NOT yet laws. 130.866: pure pair {1,4} with C = {H, r0134}; the stars p14, r0123's {0,1,3},
  r0134's {0,4} form a triangle (stages 1, 0, 4), so they collapse onto one h, and H{0,1} joins with chord 01 (STAR-EXT). But
  the zero-sum system (h1 = -h4 = -h0, total 0) leaves h nonzero, so the kill (if any) must use Ghat / walk structure.
  Triangle seeds + STAR-EXT kill 0 of the 35 recorded k=5 survivors (129.0-130.866).  k=5 is NOT closed.
- Joint-walk follower (rb24_k5.log + rb24_top.log): 7/35 survivors incl. the top three (130.866, 130.787, 130.578) done, all stall under fixed AND joint walks (129.0-129.2). Slow under
  load (~5-8 min each); left running (rb24.py, then idles).
- k=7 light CEGAR (rb23, MAXP=3): first solve hit its 1200 s limit, FEASIBLE 140.070, killed by PC3; at ~20 min per cut it
  cannot finish; left running to its 2 h timeout. k=8 not started (model ~4x larger; CPU cap).
- General k (question 4), honest assessment. ONE-RELAY/capacity: at a stage, at most |C| pieces have a nonzero relay pairing
  through C; the rest collapse (dim A + dim B <= |C| + #nonzero). This is a per-stage count, but it is only a contradiction
  once zero sums close it, and that needs SMALL E-sets (E = C + one partner). In the LP argmax at large k, each hub/pure-half
  piece has E = all full-mask roles + its pure halves, so |C| grows with the number of deep roles and the capacity does not bind.
  CELL-RANK/SATURATED-CELL give a 1:1 count (big-piece roles <= relay roles inside ALIGNED cells), k-uniform, but the type LP
  evades it with unaligned hub splits. [CONJ] route to a k-uniform row: an ALIGNMENT lemma (unaligned splits pay singletons
  via PC3) + a relay-incidence row sum_{multi q} |q| [q relayed through C] <= sum_t |C_t|. Neither is proved.
