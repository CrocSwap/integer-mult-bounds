# S2 (exchange route, class F2S): status = NO proof of cost >= v; reformulation, partial theorems, negatives

## 1. Reformulation of F2S (proved, exact)
F2S = full-support points, lines with exactly 2 nonzero coords. A class-k line (q_k = 0) is a line through the coordinate
vertex e_k; points are off the coordinate triangle. So each point t lies on exactly one pencil line per class: label
lam_k(t) in V_k (pencil-k lines). A line s of class c has tail g(s) in V_c (its own pencil line), lam_c(s) != g(s).
Hyperarc model: line t = (tail g(t) in V_c(t); head set Hd(t) = {lam_0(t), lam_1(t), lam_2(t)}, 3 distinct labels, tail not in Hd).
Incidence t -> s  iff  g(s) in Hd(t).  B = I + N, N_ts free exactly on incidences.  Block j = columns whose tail lies in V_k u V_l.
(Two points share at most one label -- a net condition; not used below.)
tied_min: V has 6 vertices (the pairs of the 3 perfect matchings of K4), Hd(a) = 3 pairs containing a, tail of (a,k) = pair of M_k missing a.
Tight small members (all cost = v): K3 = one line per class, all six incidences (B = all-ones, ranks (1,1,1), v = 3);
one class with 4 lines on a 2-cycle of labels (ranks 0,2,2, v = 4); B0.

## 2. Proved facts
**Lemma SC (single class).**  If all n lines have one class (a loopless label digraph H, arc s : g(s) -> lam(s), incidence = line digraph:
t->s iff head(t) = tail(s)), then rank_F2(I+N) >= n/2 for every admissible N.  Proof: order the labels; arcs with tail<head
form an acyclic set (head(t)=tail(s) forces increasing chain) so B on them is unit triangular; same for tail>head; one of the two has >= n/2 arcs.  []
So rank B[:,C_k] >= rank B[C_k,C_k] >= n_k/2.  (sc.py: brute-force min rank over all N for 400 random small digraphs: never < n/2.)
**Theorem S2-1 (class-triangular).**  If class-level incidences are acyclic in some class order (no incidence from a class-l point to a class-k line
for k<l, say), then cost >= v: block j is block triangular on C_k u C_l, rank >= rank B_kk + rank B_ll >= (n_k+n_l)/2 by SC; sum over j gives v.  (Includes "no cross-class incidence".)
**Rowspace identity.**  W = rowspace(B) in F2^{C_0}+F2^{C_1}+F2^{C_2}.  r_j = rho - w_j, w_j = dim{x in W : supp x in C_j}, rho = rank B.  So cost = 3 rho - sum w_j.
**Polymatroid bound.** h(S)=rank B[:,C_S] is submodular, so 2 cost >= 3 rho + sum a_k  (a_k = rank B[:,C_k]).  (Recorded in PROOF 12.5 as giving only 9 on tied_min.)
**Hyperarc order.**  X = {t : tail(t) < Hd(t)}, Y = {tail > Hd} are acyclic (tail strictly monotone along incidences), P(t in X)=1/4: rho >= v/4.
Per block (tails restricted to V_k u V_l, 3 distinct labels): 1/3 each, giving cost >= 2v/3 = exactly Theorem M1 reversed (c(t) = 2/3 for F2S).  Nothing new.
**Monotonicity.** Taking B[S,S]: cost(config) >= cost(sub-configuration) for every line subset S.  Hence for the general case "F2S + M1" does NOT reduce:
the F2S part gives |F2S| at best (if proved) and M1 only v/2 on the rest; no superadditivity across the split (cross terms can cancel).  A reduction needs a separate
argument for lines with q full or p non-full; none found.

## 3. Negative results (all exact, CaDiCaL via S2_scripts/gen.py, a multi-block rank-feasibility CNF)
* Principal version (rows restricted to the block's own columns, i.e. sum_j rank B[A_j,A_j]) has min 11 < 12 on tied_min (SAT at K=11).  So rows of the third class are essential (as in 12.3(c)).
* Candidate Lemma X: 3 rho + sum a_k >= 2v.  Tight at K3, at block-diagonal optima (rho 6, a 2,2,2) and at B0 (rho 4, a 4,4,4), but FALSE on tied_min:
  (rho; a) = (5; 2,3,3) feasible, 3*5+8 = 23 < 24 (still cost >= 12 by integrality, 11.5 -> 12).  Frontier of (rho, sorted a) on tied_min:
  rho=4:(4,4,4); 5:(2,3,3); 6,7,8:(2,2,2).  The three tight examples span only the line X, so NO linear inequality in (rho, sum a) can prove cost >= v, and the polymatroid bound is
  intrinsically short; the proof needs an integer/rigidity step (as in 12.3(b),(c)).
* Random F2S configs (s2a, {+-1,+-2}, v 4-9) have cost >> v (tight ones need the special net structure), so random testing is uninformative; tightness lives on K3-like cliques,
  2-cycles of labels, and tied_min.
## 4. Data (S2_scripts/s2b.py: exact min cost of EVERY sub-configuration of tied_min)
Counts (cost -> #subsets), sizes 3..12: 3:{3:4,4:108,5:60,6:48}; 4:{4:51,...}; 5:{5:24}; 6:{6:94}; 7:{7:48}; 8:{8:63}; 9:{9:36}; 10:{10:18};
11:{12:12 (all)}; 12:{12}.  cost >= v for ALL 4095 subsets; many tight at every size <= 10 (size-11 subsets are strictly above: cost 12).
So (A) holds on every sub-quadrangle configuration, supporting a clean general F2S statement but not proving it.

## 5. What a proof would need (suggested)
Strengthen Theorem S2-1 from class-level to piece-level: find an ordered partition of lines into pieces so cross-piece incidences go forward and each piece is
either a single-class (SC) or a "K3-clique" piece with a direct rank count; the obstruction is exactly tied_min where no such partition exists and the exchange (12.3 c) is needed.
Open: an exchange lemma replacing the SAT step 12.3(b) ("rank-3 block has unique filling"): in hyperarc language, a block of rank < (#columns)/2 forces S_k = S_l and vanishing on rows of the third class.

# R2 follow-up (after PROOF 13): sum w_j <= 3 rho - v ?  and Conjecture PP  -- NOT proved; measurements

* In F2S Lemma Peel is vacuous (|pi|=3, |sigma|=2) and SCC is automatic-compatible (pi cap sigma != {}).  S2-1 (class-acyclic) is now just the SCC lemma applied
  to a class-level order; SCC says WLOG every line has an incoming and an outgoing incidence, and the cross-class incidences are cyclic at class level.
* "sum w_j <= 3 rho - v" is literally (A) (cost = 3rho - sum w_j), so it cannot be easier by restatement.  Data on tied_min (exact, S2 frontier): rho=4: w=0;
  rho=5: a=(2,3,3), so sum w <= 3 (cost >= 12 needs 15 - sum w >= 12); rho>=6: w=(2,2,2) max.  Equality sum w = 3rho - 12 at (4,0),(6,6); at rho=5 the slack is 0 or 1 only through
  integrality, matching 13.2 (no per-class rowspace inequality).  I found no proof of an upper bound on sum w_j; the obstruction is the same as in 12.5 (need joint rigidity of
  low-rank blocks, 12.3(b)).  Easy partial: w_j <= a_j-type bounds are useless since w_j <= rho - r_j is the definition.
* **Conjecture PP is FALSE as stated** (S2_scripts/pp.py, exact costs of all 4095 sub-configurations of tied_min, X in {same-point groups, same-line groups}, including singletons):
  272 of 4095 subsets have no X with cost(S) >= cost(S-X)+|X|; smallest failure v=2: lines (0,3) cost 2, and cost(single line) = 2 (a lone line costs 2, not 1), so deleting any group
  gives 2 >= 2+|X| false.  Failures also at v=3 (the K3 triangles, cost 3), and at every size up to 8 (counts by size 2:12, 3:4, 4:51, 5:24, 6:88, 7:48, 8:45); none at sizes 9-12.
  The cause: excess cost-v is NOT monotone under deletion (a lone line has excess +1, the tight pair excess 0).  Since PP is only needed on a minimal counterexample, a weaker
  form (PP only for configurations with cost <= v-1, or PP with cost replaced by max(cost, |lines|)) is untested by me; as stated, groups X_P/Y_l, including whole same-point groups of size >=2,
  fail 4084 times (strong form fails massively).
* So from the S2 side PP is NOT accessible as an induction; the data refute the plain statement.
