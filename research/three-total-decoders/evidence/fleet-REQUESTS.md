# Requests from the math lead (relay to the fleet)

R1 (S1, matroid / LC): before theory, measure.
- On tied_min's 217 optima (../tied_min_optBs.json, entries are (t,s) incidences set to 1) and on any optimum you can
  get with tiny CP-SAT (cex_min_1 has cost in [20,22]), test each block for regularity: try a TU signing via Camion's
  propagation, then check TU by brute force on small minors.
- Report:
  - whether any optimal block contains an F7 or F7* minor;
  - whether the per-block signings can be made compatible on shared entries.  An entry (t,s) is shared by the blocks
    j in pi(t) cap sigma(s), which has size 2 or 3.
- Compatibility is the real content of LC.  Find the smallest obstruction: a cycle of shared entries whose sign
  constraints conflict.

R2 (S2, exchange): use the two new reductions in PROOF.md section 13.
- Lemma SCC: H is strongly connected, WLOG.
- Lemma Peel: every point and every line has >= 2 nonzero coordinates, WLOG.
- Then try to prove "cost = 3 rho - sum w_j >= v" in F2S via an upper bound on sum_j w_j.  w_j counts row-space vectors
  supported on class-j columns, i.e. dependencies of rows restricted to the two other classes ("flow conservation"
  on the pencil-k fibres).
- Concrete target: sum_j w_j <= 3 rho - v, at least when rho < v/2, which is the only open case since cost >= 2 rho.

R3 (S3, adversary): hunt only inside the reduced class.
- Strongly connected H, every point and every line with >= 2 nonzero coordinates.
- Prefer F2S with rho < v/2 possible: dense label coincidences, quadrangle-like nets.
- tied_min is the smallest tight example known; report any configuration whose min cost equals v (tight), not only
  ones below v.  Tight examples are what a proof must explain.

R4 (S1/S3, literature hook): (A) is a coupled Haemers-minrank / linear index-coding comparison between F_2 and Q
(PROOF.md 13.1).
- S1: check whether the matroid obstruction in the known T >= 7 counterexamples is literally an F7 / F7* minor inside
  one block, or only appears through the coupling.  Whichever it is tells us where a T = 3 proof must look.
- S3: use Lubetzky-Stav-type F_2-cheap digraphs as seeds.  Ask which of them embed as point-line incidence digraphs in
  P^2(Q) (K_{2,2}-free in the L6 sense, no transitive 4-tournament).

R5 (S1, URGENT correction to Lemma W).  reg.py tests the column matroid M[B].  A TU signing of B exists iff
M[I | B] is regular (Camion), and that is NOT implied by M[B] regular:
- any full-rank B has M[B] free (hence regular);
- A = [[1,1,0,1],[1,0,1,1],[0,1,1,1]] has M[A] graphic, but M[I|A] = F7, so A has no TU signing.
So Lemma W must read: "if B has a TU signing (M[I|B] regular), then cost(B) >= v".  Please re-run t1b.py on
[I | B].  Note that F7 search at rank 12 with 24 elements is still feasible.
More useful than TU, and exactly what Lemma B needs: a signing (or any rational lift on supp B, nonzero diagonal) with
rank_Q = rank_F2 on the three blocks only.  I checked this directly: all 217 tied_min optima have a +-1 joint lift
with Q-ranks (4,4,4) (liftall.py, exact).  Suggested precise gap G1': "some cost-minimiser has a joint rank-preserving
lift on the three blocks".  Lemma G (gluing) is the right tool for it; the triple-overlap obstruction is the content.

R6 (S3, test an induction scheme; exact costs on small configurations, CP-SAT tiny OK).
Single-line deletion can't drive an induction: tied_min minus any one line still costs 12.  Test group peeling.
For a point P, let X_P = {t : p(t) = P}; for a line l, let Y_l = {t : q(t) = l}.
- Conjecture PP: every configuration with v >= 1 has a point P or a line l such that
    cost(config) >= cost(config - X) + |X|   (X = X_P or Y_l).
  PP implies (A) by induction.
- Mechanism: B[X_P, X_P] = I (same-point lines are never incident), so rank B_j = |X_P cap D_j| + rank(Schur
  complement).  The Schur complement adds B_ut B_ts along paths u -> t -> s through X_P.  It can leave the incidence
  class, so PP is not automatic.
- On tied_min it holds: remove a point (3 lines), 12 >= 9 + 3; remove a q-line (2 lines), 12 >= 10 + 2.
- Please test PP on every 4095-subset of tied_min (S2 has all their exact costs: S2_scripts/s2b.py), on cex_min_1
  sub-configurations, and on random configurations with coincident points and lines.
- Report the smallest failure.  If none, also test the stronger "every P with |X_P| >= 2 works".
