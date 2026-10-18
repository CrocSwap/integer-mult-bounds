# KPR4 T >= 3 under Thm C: proofs and closure status (Oct 13, second prover)

Model (FL C.6 / #446 Thm C): B over F2, unit diagonal, 0 on non-orthogonal root pairs, free on orthogonal pairs;
decoder M = sum_{j<=T} p_j q_j^T over Q, M_tt != 0, M_ts = 0 where B_ts = 1 (s != t); R_j = supp p_j, A_j = supp q_j,
D_j = R_j cap A_j, r_j = rank_F2 B[R_j, A_j], cost = sum_j max(w, r_j).  A window (unit, T, h) closes iff cost >= N(h) := c(h)+1,
c(h) = ceil(v x*(h)) - 1 (open_cases.py).

## 0. What each window actually needs (scratch need.py; N(h) = c(h)+1)

| unit | v | w | 3w | N(h) over the open T=3 range |
|---|---|---|---|---|
| D5 | 20 | 4 | 12 | h7-8: 13 |
| D6 | 30 | 5 | 15 | h7 20, h8-9 19, h10 18, h11-13 17, h14-17 16 |
| D7 | 42 | 6 | 18 | h7 28, h8 27, h9 26, h10 25, h11-12 24, h13-14 23, h15-17 22, h18-19 21, h20-21 20, h22-24 19 |
| D8 | 56 | 7 | 21 | h7 37, h8 35, h9 34, h10 33, h11 32, h12-13 31, h14-15 30, h16-17 29, h18 28, h19-20 27, h21-22 26, h23-24 25, h25-26 24, h27 23, h28-29 22 |
| E6 | 36 | 5 | 15 | h8 23, h9 22, h10-11 21, h12-14 20, h15-17 19, h18-19 18, h20-22 17, h23-25 16 |
| E7 | 63 | 7 | 21 | h8 40, h9 38, h10 37, h11 36, h12-13 35, h14 34, h15-16 33, h17 32, h18-19 31, h20-21 30, h22 29, h23-24 28, h25 27, h26-27 26, h28-29 25, h30 24, h31-32 23, h33 22 |

Two targets: (i) top of every window needs only N = 3w+1, i.e. "the three totals cannot all have r_j <= w";
(ii) the low-h end needs ~0.62-0.67 v.

(sections below are filled as results land)

## 1. Decoder-free bound: does NOT close anything (exact)

Since D_j = R_j cap A_j, r_j >= rank B[D_j, D_j] >= f(D_j) := min F2 rank of a unit-diagonal matrix on D_j vanishing on
non-orthogonal pairs, and every line lies in some D_j (M_tt != 0).  Pure root-system bound: Phi = min over 3-covers of
sum_j max(w, f(D_j)).  **D5: Phi = 12 = 3w < 13.**  Witness (new/verify_partition.py, B blocks re-verified by elimination):
parts {0,4} (rank 2), {6,8,9,11,12,13,15,16,17} (rank 3: three disjoint orthogonal triples, B = J_3 + J_3 + J_3),
{1,2,3,5,7,10,14,18,19} (rank 4).  Lines indexed as ade.D(5).  So the decoder geometry is indispensable even at the top
of the smallest window; the obstruction is dense J-blocks on orthogonal triples/pairs.

## 2. Decoder lemmas (all rigorous; each is a constraint of new/coversat.py)

Notation: omega_j(t) = p_j(t) q_j(t) / M_tt, so sum_j omega_j(t) = 1 and t in D_j iff omega_j(t) != 0.

**L1 (cover).** Every t lies in some D_j.  (M_tt = sum_j p_j(t) q_j(t) != 0.)

**L2 (principal block).** r_j >= rank B[X, Y] for X subset R_j, Y subset A_j; in particular for X = Y = D_j.

**L3 (no transitive (T+1)-tournament).** No T+1 lines t_1..t_{T+1} with B_{t_i t_k} = 1 for all i < k.
Proof: M[S,S] would be triangular with nonzero diagonal, rank T+1 > rank M.

**L4 (full clique meets every total).** If |S| = T and B[S,S] = J (all off-diagonal ones), then S meets every D_j.
Proof: M[S,S] = P_S Q_S^T = Delta is diagonal invertible, so P_S (T x T) is invertible and Q_S^T = P_S^{-1} Delta.
Then sum_{t in S} omega_j(t) = sum_i (P_S)_{ij} (P_S^{-1})_{ji} = (P_S^{-1} P_S)_{jj} = 1, so some omega_j(t) != 0.
(Consequence: the 3-disjoint-triples part above is impossible as a single D_j with the triples private to it.)

**L5 (single surviving product).** If B_ts = 1 (t != s) then |pi(t) cap sigma(s)| != 1, pi = row support, sigma = column
support: a single nonzero product p_j(t) q_j(s) cannot sum to 0.  (Consequence: if a digon t,s (B_ts = B_st = 1) has
t, s in D_j and in no other D_k, then pi(t) cap sigma(s) has size >= 2, so it contains some k != j and B_ts = 1 sits in
block k; likewise B_st sits in some block k'; if pi(t), sigma(t), pi(s), sigma(s) force k' != k, all three totals are
nonzero on {t,s}.  A digon spread over two totals, e.g. p(t)=q(t)=e_1, p(s)=q(s)=e_2, costs exactly 2.)

**L6 (K22).** Distinct t,t',s,s' with B_ts = B_ts' = B_t's = B_t's' = 1: two distinct points cannot lie on two distinct
lines, so P_t = P_t' (then B_tt' = B_t't = 0 and pi(t) = pi(t')) or L_s = L_s' (then B_ss' = B_s's = 0, sigma(s) = sigma(s')).

**L7 (lift identity; new).** For every rational matrix B' supported on supp(B) with nonzero diagonal,
  v <= sum_j rank_Q B'[R_j, A_j].
Proof: B' o M = diag(B'_tt M_tt) (off-diagonal: B'_ts != 0 only where B_ts = 1, where M_ts = 0), and
B' o M = sum_j D(p_j) B' D(q_j), whose j-th term has rank <= rank_Q B'[R_j, A_j].
Consequence: a decoder with cost < v needs B whose blocks are *jointly non-liftable*: no common rational re-weighting of
the ones of B brings every block's Q-rank down to its F2 rank.  J-block (clique) structures, unimodular blocks, and
anything with a sign-lift are therefore never cheaper than v.  This is the precise sense in which the T = 3 question is
cross-characteristic, and why the cost < v phenomenon needs F2-specific (Fano-like) cancellation, as at T >= 7.

## 3. A global F2 certificate (rigorous) and the 2-adic theorem P

**L8 (labelling certificate).** For any F2 vectors a(t) subset pi(t), b(s) subset sigma(s) (pi, sigma the row/column supports),
cost >= sum_j r_j >= rank_F2( sum_j D(x_j) B D(y_j) ) = rank_F2( B o K ),  K_ts = a(t).b(s) mod 2,
where x_j(t) = a(t)_j, y_j(s) = b(s)_j (each term is a sub-block of B[R_j, A_j]).  If there is a linear order on a set S
with K_tt = 1 on S and K_ts = 0 for every incidence p(t).q(s) = 0 with t before s (t, s in S), then B o K restricted to
S x S is unit lower-triangular for EVERY admissible B, so cost >= |S|.  (This is the T >= 1 generalisation of the T = 2
alpha/beta triangularity; the T = 2 proof is the case a = b = e_1 on {alpha < beta}, a = b = e_2 on {alpha > beta}.)

**Theorem P (2-adic reduction with one-sided repairs).**  Fix e in Z^3 and rescale p_k -> 2^{e_k} p_k, q_k -> 2^{-e_k} q_k
(M unchanged, supports unchanged); scale each p(t), q(s) to a primitive 2-integral vector and reduce mod 2: a(t), b(s).
Then a(t).b(s) = 0 for every incidence (an odd number of odd terms cannot sum to 0).  Let G = {t : a(t).b(t) = 1} and
I = the rest ("isotropic").  Call t in I *b-repairable* if some delta subset sigma(t) has a(t).delta = 1 and a(u).delta = 0
for all u in I with p(u).q(t) = 0, and *a-repairable* dually (delta subset pi(t), delta.b(t) = 1, delta.b(s) = 0 for all
s in I with p(t).q(s) = 0).  Let F = repairable lines.  Then **cost >= |G| + |F|**.
Proof.  Labels a'(u) = a(u) + delta_u on a-repaired u, b'(t) = b(t) + delta_t on b-repaired t (each repaired line uses one
side), unchanged otherwise; S = G + F.  K_tt = 1 on S.  For an incidence u -> t (p(u).q(t) = 0, u != t), since
a(u).b(t) = 0:  K_ut = [t b-rep] a(u).delta_t + [u a-rep] delta_u.b(t) + [both] delta_u.delta_t.
 - t b-repaired, u not a-repaired: a(u).delta_t = 0 if u in I (choice of delta_t); possibly 1 if u in G.
 - u a-repaired, t not b-repaired: delta_u.b(t) = 0 if t in I; possibly 1 if t in G.
 - u a-repaired, t b-repaired: the first two terms vanish (u, t in I); delta_u.delta_t possibly 1.
So every kept incidence goes a-repaired -> G, G -> b-repaired or a-repaired -> b-repaired.  In the order
(a-repaired, G, b-repaired) all kept entries of B o K[S,S] lie above the unit diagonal: rank |S|, so cost >= |G| + |F|.  []
Check: new/thmP.py (exact Fraction valuations).  On random rational configurations (v = 6-12, pools {-1,0,1,2},
{+-1,+-2}) theorem P gives >= 0.75 v (worst sampled ratio 0.75; e.g. 7/8, 8/10); it alone is not a uniform 2/3 bound.

**Conjecture F -- FALSE as stated (cex/cex_min_1.json, hunter, Oct 13).**  Original statement:  For every rational T = 3 decoder there are labels
a(t) subset pi(t), b(t) subset sigma(t) and an order with K_tt = 1 for all t and every forward incidence killed.
Refuted: a 19-line {-1,0,1}^3 configuration has max L8 certificate 18 (two CP-SAT encodings, cex/); its best known
Thm-C cost is 23 >= v, so it is NOT a decoder win -- only the certificate is too weak there.  Theorem P gives just 8/19 on
it (all entries +-1/0: heavily isotropic).  Earlier sampling evidence (local search reached |S| = v on ~90 random
configurations tried (v = 6-12,
dense pools), including the v = 9 example whose per-total MAS sum is only 7.  Not proven.  Over R the analogue is
doubtful (Kochen-Specker / 4-chromatic orthogonality graphs of S^2), over Q the 2-adic structure is what makes it plausible
(Godsil-Zaks: the orthogonality graph of Q^3 is 3-colourable -- not re-checked against the paper; per LIT.md their
argument avoids isotropy via the unit-norm constraint, which our p, q lack, so it does not transfer directly), and theorem P is the first half of such a proof: what is
left is ordering the unrepairable isotropic lines (|Z(t)| = 2: two tied minimal 2-adic valuations among p_k(t) q_k(t)).)
What the windows need is only Conjecture F': certificate >= c v with c ~ 0.67 (low h) or >= 3w+1 (top); open.

## 4. Root-system relaxation (SAT, no proof logs) -- status

new/coversat.py encodes L1-L6 (+ valid symmetry breaking --sb: totals sorted by |D_j|, a line of the largest D moved to
line 0 by W transitivity) and asks for B, supports pi/sigma and rank-<=c_j factorisations of every B[R_j, A_j].
UNSAT at caps (w,w,w) would close the top of the window ("not all r_j <= w").
 - D4, caps 2,2,2: UNSAT in 0.1 s (calibration only; D4 is closed by T <= 2).
 - **D4, caps 3,3,3 (--sb --C7): UNSAT in 1710 s** (CaDiCaL, no proof log): the relaxation alone proves that a D4 T=3
   decoder has some r_j >= 4, i.e. cost >= 10 of v = 12 (D4 is already closed by T <= 2; this is the calibration -- the
   relaxation is strong, not near-vacuous).
 - D5, caps 4,4,4: undecided.  Without --sb/C7: 60 min timeout.  Running: jobs/cov_d5_sb (--sb --C7, started ~16:27,
   2 h cap) and jobs/cov_d5_sb_noc7 (--sb, started 16:58, 2.5 h cap); logs in jobs/cov_d5_sb*.log.  **UNSAT would close
   the whole D5 T3 window (h7 and h8 both need exactly 3w+1 = 13)**, provisionally (no proof log).  DIMACS for a
   DRAT/LRAT rerun: new/cov_D5_T3_4-4-4_sb_c7.cnf, new/cov_D4_T3_3-3-3_sb_c7.cnf (new/dumpcnf.py).
The D-only version (C2 on D_j x D_j instead of R_j x A_j) is SAT instantly for D5 4,4,4: the off-D_j rows/columns that
L5 forces into other totals (a digon private to one total puts its off-diagonal ones into other blocks) are essential.

## 5. Open table after this pass

Nothing in the open list is closed yet.  Unchanged: D5 T3 h7-8; D6 T3 h7-17; D7 T3 h7-24, T4 h7-10; D8 T3 h7-29, T4 h7-17,
T5 h7; E6 T3 h8-25, T4 h8-11; E7 T3 h8-33, T4 h8-22, T5 h8-11.

Sharpest remaining obstruction (two faces of one gap):
 (a) root side: the orthogonality graph alone allows three totals of F2 rank <= w on D5 (section 1); what kills it is
     decoder geometry -- L4 (a mutually-paired triple meets every total) and L5 (a pair private to one total spills into the others) -- whose SAT closure
     is computationally hard as encoded;
 (b) decoder side: by L7 a cheap decoder needs jointly non-liftable F2 blocks; by theorem P the only lines that resist
     the 2-adic certificate are isotropic lines that cannot be repaired on either side.  Conjecture F (repair + order; now refuted, F' with c ~ 2/3 suffices)
     would have given cost >= v for every B; a proven F' would close every T = 3 window and, at T = 4, the T = 4 ones
     (T = 4 needs the analogous statement in PG(3,2)).

## 6. T = 4, 5 (free extensions)

L1, L2, L5, L6, L7, L8 hold verbatim for any T.  L3: no transitive (T+1)-tournament.  L4: a T-set with B[S,S] = J meets
every D_j (same proof, P_S is T x T).  Theorem P holds verbatim with reductions in PG(T-1, 2) (a(t), b(s) in F2^T).
A constant-factor F' at T = 4 would close the T = 4 windows; F itself fails already at T = 3 (cex) and cost >= v fails by T = 7 (E7 coordinates give cost < v).

Note (coordinator question): theorem P cannot by itself close the top of a window -- it is a bound for a GIVEN decoder
(it reads the decoder's 2-adic valuations), so closing a window needs it (or Conjecture F) for every decoder, which is
exactly the unproven step.  It would close a window only together with a classification of the possible isotropic
(unrepairable) sets, which is not done.
