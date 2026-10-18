# F' (T = 3 lower bounds) -- third prover, Oct 13 night

Setting and notation as ../PROOF.md: lines t = (p(t), q(t)), pi = supp p, sigma = supp q, D(t) = pi cap sigma,
incidence t -> s iff p(t).q(s) = 0 (s != t); L8 certificate = labels a(t) subset pi(t), b(t) subset sigma(t), a set S with
|a(t) cap b(t)| odd on S, and an order on S in which every incidence t -> s inside S with |a(t) cap b(s)| odd points forward.
cost >= sum_j r_j >= |S| for every admissible B (L8).  Scripts in this directory; python = intmult-work/venv/bin/python.

## 0. Calibration on cex_min_1 (v = 19)

| bound | value | script |
|---|---|---|
| D-types | {0,2}:5, {0}:4, {1,2}:3, {0,1}:3, {2}:2, {0,1,2}:1, {1}:1 (11 tied, 8 odd) | t_cex.py |
| MAS-sum  sum_j MAS(G[D_j]) | 6+4+6 = 16 | t_cex.py (mas.c, exact subset DP) |
| Theorem P (e = 0) | 8 | (= # odd-|D| lines, see section 1) |
| max L8 certificate | 18 (OPTIMAL, explicit labels + order re-checked) | certsol.py |
| restricted certificate (section 2 label family) | 18 (OPTIMAL, re-checked) | restricted.py |

MAS-sum (a rigorous cost bound: an acyclic X subset D_j makes B[X,X] unit-triangular) is not a route to F': a digon whose
two lines are both private to D_1 exists (p = (1,1,0), q = (1,0,1); p = (1,0,-1), q = (1,-1,0)), MAS-sum = 1 of v = 2, while
its L8 certificate is 2 (labels a = {1,2}, b = {1} ; a = {1}, b = {1,2}).

## 1. The {-1,0,1} world: exact parity structure

**Lemma 1.1.** If all entries of p, q lie in {-1,0,1}, then an incidence t -> s forces |pi(t) cap sigma(s)| in {0, 2}.
Proof: p(t).q(s) is a sum of |pi(t) cap sigma(s)| terms equal to +-1; an odd number of +-1 cannot vanish.  []

So the canonical labels a = pi, b = sigma kill every incidence (K = 0 off the diagonal) and K_tt = |D(t)| mod 2: the lines
with |D(t)| odd (call them G) form an L8 certificate on their own (Theorem P at e = 0).  The others have |D(t)| = 2: *tied*.

**Lemma 1.2 (sign classes).** For a tied line with D(t) = {i,j}, M_tt = p_i q_i + p_j q_j != 0 forces p_i q_i = p_j q_j, so
eps(t) := p_i(t) p_j(t) = q_i(t) q_j(t) in {+1,-1} (invariant under p -> -p, q -> -q).  Two tied lines t, s with the same
D = {i,j} and the same eps are never incident.  Proof: p_i(t) q_i(s) + p_j(t) q_j(s) = eps p_j(t) q_i(s) (1 + 1) = +-2 (using
p_i(t) = eps p_j(t), q_j(s) = eps q_i(s)) and the third term is in {0, +-1}.  []
Checked: signclass.py (no violation of 1.1 or 1.2 on cex and on the 121-line pool).

**Lemma 1.2' (unit world, halves).**  More generally, call a configuration *unit* if for some e in Z^3 and some per-line
rational scalars lambda_t, mu_t, every nonzero entry of the rescaled vectors lambda_t 2^{e_k} p_k(t) and mu_t 2^{-e_k} q_k(t)
is a 2-adic unit (M changes only by row/column scalings, so supports, incidences and M_tt != 0 are unchanged).  All
statements below are applied to the rescaled vectors.
Lemma 1.1 holds verbatim in the unit world (an odd number of odd numbers is odd).  For a tied line with D(t) = {i,j}
(i < j) put alpha(t) = p_i/p_j, beta(t) = -q_j/q_i (rationals; alpha != beta because p_i q_i + p_j q_j = M_tt != 0, the
third product being 0 as k is not in D(t)).  Split the class C_ij = {t : D(t) = {i,j}} into the halves
H^< = {alpha < beta} and H^> = {alpha > beta} (any total order of the SET Q works -- the argument below uses only the
exact equality alpha(t) = beta(s) and transitivity, never field compatibility; we use the usual one).
Claim: if t, s in C_ij and t -> s then alpha(t) = beta(s).  Proof: pi(t) cap sigma(s) contains {i,j} and is even
(Lemma 1.1), so it is {i,j}; the k-th product p_k(t) q_k(s) is exactly 0 and p_i(t)q_i(s) + p_j(t)q_j(s) = 0.  []
Hence inside H^<, t -> s gives alpha(s) < beta(s) = alpha(t): alpha strictly decreases along incidences; inside H^>,
beta(t) < alpha(t) = beta(s): beta strictly increases.  Each half is acyclic in G.  (This is the T = 2 alpha/beta
argument run inside one class; in the {-1,0,1} world the halves are the sign classes eps = -1, +1 and are even
independent sets.)

## 2. Theorem U (unit world: certificate >= |G| + |I|/2)

**Theorem U.**  Let the configuration be unit (Lemma 1.2').  Let G = {t : |D(t)| odd}, and for each of the three tied
classes C_01, C_02, C_12 let H_ij be either half (H^< or H^>).  Then the L8 certificate is at least
  |G| + |H_01| + |H_02| + |H_12|,
so, taking the larger half of every class,  cost >= sum_j r_j >= |G| + |I|/2 >= v/2,  I = all tied lines.
(Coordinate 0 plays a special role below; the three choices of the special coordinate give the same bound.)

*Labels.*  G: a = pi, b = sigma.  H_02: a = pi - {0}, b = sigma ("A, delete 0").  H_01: a = pi, b = sigma - {0}
("B, delete 0").  H_12: if 0 in pi(t): a = pi - {2}, b = sigma ("A, delete 2"); otherwise a = pi, b = sigma - {2}
("B, delete 2").  Every label has |a cap b| = |D| - 1 = 1 on the tied lines: the diagonal of B o K is 1 on S.
*Order.*  A_12 := {t in H_12 : 0 in pi(t)}, then H_02, then G, then H_01, then B_12 := H_12 - A_12; inside a half,
order by alpha decreasing (H^<) or beta increasing (H^>).  Claim: every incidence t -> s inside S with
|a(t) cap b(s)| odd ("conflict") has t before s; then B o K[S,S] is unit upper-triangular for EVERY admissible B (L8).

*Proof.*  Write a(t) = pi(t) - d_A(t) and b(s) = sigma(s) - d_B(s) (d_A = the deleted coordinate for an A-line, empty set
otherwise; same for d_B).  For an incidence t -> s, Lemma 1.1 gives |pi(t) cap sigma(s)| even, so
  |a(t) cap b(s)| = [d_A(t) in sigma(s)] + [d_B(s) in pi(t)] + [d_A(t) = d_B(s)]   (mod 2)          (*)
(the last term only when t is an A-line and s a B-line: the deleted coordinate is then in pi(t) cap sigma(s)).
(i) No conflict leaves a non-A line toward a non-B line: all three terms of (*) vanish.  So conflicts start in
    A = A_12 + H_02 or end in B = H_01 + B_12; those from A to G or B and from G or A to B point forward.
(ii) Conflicts inside A: by (*), t -> s conflicts iff d_A(t) in sigma(s).
    - t in H_02 (d_A = 0), s in A_12: sigma(s) = D(s) = {1,2} (0 is in pi(s) and not in D(s)), so 0 not in sigma(s): none.
    - t in A_12 (d_A = 2), s in H_02: 2 in D(s) is in sigma(s): conflicts may occur; they point forward (A_12 first).
    - t, s in the same half: incidences there are monotone in alpha (or beta), so they point forward in the half's order.
(iii) Conflicts inside B: t -> s conflicts iff d_B(s) in pi(t).
    - s in H_01 (d_B = 0), t in B_12: pi(t) does not contain 0 (definition of B_12): none.
    - s in B_12, t in H_01: may occur; forward (H_01 before B_12).
    - same half: monotone, forward.
So all conflicts point forward and B o K[S,S] is unit upper triangular: rank |S|.  []

*Checks* (exact rationals; certsol.check re-verifies labels, |a cap b| odd on S, and every conflict's direction):
 - theoremU.py: cex_min_1 15/19 (|G| = 8, larger halves 7), 121-pool 106/121, and 3000 random unit configurations
   (odd entries {+-1,+-3,5}, 4-80 lines, forced incidences, up to ~650 incidences each): all valid, worst ratio 2/3.
 - stressU.py: 1800 tied-only configurations (entries {+-1,+-3,0}, 6-44 lines, 189k incidences in total): all valid,
   worst ratio exactly 1/2 (the bound is attained by the scheme, not by the true certificate).  Negative control: a
   naive scheme (delete the smallest D-coordinate, no halves) is rejected by check() in 299/300 trials.
 - Optimality of 1/2 *for this kind of scheme*: colgen.py / colgen3.py solve the minimax over all group-level schemes
   (groups = (class, half, pi, sigma), options: A or B with either deleted coordinate, acyclic group digraph) by column
   generation (CP-SAT pricing, HiGHS LP): the value is exactly 1/2 both with the exact {-1,0,1} incidence table
   (groups.py, exhaustive over the 121 lines) and with the conservative unit-world table.  So one-deletion schemes
   cannot beat |G| + |I|/2 in the worst case; the true certificate on cex (18/19) uses more.

## 3. What Theorem U does and does not give

 - cost and the L8 certificate depend only on the *combinatorial type* tau = (supports pi, sigma; incidence digraph).
   So Theorem U bounds every decoder whose type has SOME unit realisation (over Q, or over any field with a valuation of
   residue characteristic 2 -- the proof only uses parity of units and a total order on the field).  (A type realisable
   over a field of characteristic 2 has cost >= v outright: B o M = diag(M_tt) over that field.)
 - It does not cover all rational decoders: a type can force 2-adic structure (von Staudt / harmonic constructions force
   a point (1,2,0) next to (1,1,0), which no column rescaling makes simultaneously unit).  For those, Theorem P handles
   the odd lines at each e; the missing piece is the analogue of Lemma 1.2' when the third product p_k(t)q_k(s) is
   even but NOT zero (section 4).
 - Windows: v/2 would close D7 h>=18, D8 h>=18, E6 h>=18, E7 h>=17 (N(h) <= ceil(v/2)) -- but only once it holds for
   all rational decoders; restricted to unit types it closes nothing on its own.

## 4. Handoff: the general rational case (not attempted to completion)

1. *Generic-e framework.*  Take e in R^3 generic (realised in a ramified extension Q_2(2^{1/m}); residue field still F_2).
   Then a(t) = argmin_k (nu p_k(t) + e_k) and b(t) = argmin_k (nu q_k(t) - e_k) are single coordinates for every line: an
   "arrow" (a(t), b(t)).  Lemma 1.1 (odd number of leading units) gives a(t) != b(s) on every incidence.  G_e = diagonal
   arrows (k,k); every other line is an off-diagonal arrow (i,j) (tied lines always are).  A-repair a = {i,j} needs
   j in pi(t); B-repair b = {i,j} needs i in sigma(t).  By Lemma 1.1, A-conflicts occur only between A-lines with EQUAL
   b-label, B-conflicts only between B-lines with EQUAL a-label.  So a general theorem reduces to (a) a splitting lemma
   "lines with the same arrow (and same support type) split into O(1) parts, each acyclic in G", then (b) the same
   group-level minimax (colgen*.py) over (arrow, part, pi, sigma) groups.
2. *Template for (a): the T = 2 splitting.*  With only coordinates i, j: put g(t) = (nu p_j + e_j) - (nu p_i + e_i) > 0 and
   h(s) = (nu q_i - e_i) - (nu q_j - e_j) > 0.  t -> s forces g(t) = h(s), and g(t) - h(t) = z_j(t) - z_i(t)
   (z_k = nu(p_k q_k), independent of e).  Dominant-i lines (z_i < z_j): g strictly increases along incidences; dominant-j
   lines: h strictly decreases; tied lines (z_i = z_j): g is constant along incidences, so each level set is a unit-world
   problem and Lemma 1.2' (alpha/beta halves) orders it.  With three coordinates the incidence condition is "the minimum
   of nu(p_k(t) q_k(s)) is attained exactly twice" and the third product can be even but nonzero; the 2-adic-digit
   version of the alpha/beta argument then needs nu(p_k(t) q_k(s)) > nu(alpha(s) - beta(s)), which is e-independent
   and can fail.  That digit lemma is the first missing piece.
3. *e-selection obstruction.*  Any single-e argument gives a bound of the form max_e(...).  Unrepairable arrows (e.g.
   pi = {i,l}, sigma = {j,l}, arrow (i,j)) occupy cones of e-space with arbitrary apexes, which can cover all of it; and
   full-support tied lines (e.g. p = (1,1,1), q = (1,1,2)) are never in G_e nor e-unit for any e, so the general form
   of Theorem U, cert >= max_e (|G_e| + |T_e|/2) (T_e = tied lines that are unit at e), bounds a configuration made of
   them by 0.  Yet the true certificate is v there (fulltied.py: 12/12 random such configurations, 10-18 lines, cert = v).
   Quantified (gap.py, 20 random non-unit configs, entries {+-1,+-2,+-3,4,0}, 10-16 lines, e in {-2..2}^2):
   max_e(|G_e| + |T_e|/2) / v ranged 0.50-0.88, while the true certificate was v in all 20.  So in the general case
   the certificate's strength comes from mixed labels across scales, not from one reduction; a proof needs an
   e-selection (or multi-scale) argument on top of the digit lemma.

## 5. Status of the targets

 - (A) cost >= v: untouched.  On cex_min_1, cost is still known only to lie in [18, 23] (L8 certificate 18; best B found 23).
 - (B) F': proved with c = 1/2 for unit types (Theorem U); open in general.  c = 2/3 needs labels beyond one deletion even
   in the unit world (minimax = 1/2 exactly for one-deletion schemes).
 - (C) not attempted (root-system SAT route belongs to ../PROOF.md section 4).
 - Windows closed: none.

## 6. Continuation (general rational case)

**6.1 Gap 1 is false as posed: no "halves" lemma exists for non-unit tied classes.**  The lines
p = (3,-1,-6), q = (1,-1,-2);  p = (-1,7,-4), q = (-3,3,-2);  p = (1,1,0), q = (23,9,10)
are all tied with Z = {0,1} (z = (0,0,2), (0,0,3), (0,0,inf)), so they lie in class {0,1} at every scale where they are
I_2.  Each line passes through the other two points: G is the complete digraph on 3 vertices, so the class cannot be split
into 2 acyclic parts by ANY rule (k3class.py found 3 such triangles among 200k random small-integer triangles).  Their
true certificate is 3 (certsol.py), using labels on coordinate 2, i.e. labels from another scale.  So the general case
needs labels that mix scales; a single-scale digit lemma cannot exist.

**6.2 Lemma (private lines; any field, rigorous).**  Let P_j = {t : D(t) = {j}}.  Then
  MAS(G[P_j]) >= #(I) + #(II) + ceil(#(III or IV)/2),
where, writing k, l for the other two coordinates: I = {p_k = p_l = 0} (sinks: p(t) = E_j, which is on no line of D_j),
II = {q_k = q_l = 0} (sources), III = {p_k = 0, q_l = 0}, IV = {p_l = 0, q_k = 0}.
Proof: III -> III has p(t).q(s) = p_j q_j != 0, so there are no such edges, and likewise IV -> IV.  III t -> IV s iff
p_l(t)/p_j(t) = -q_j(s)/q_l(s), and IV s -> III t iff p_k(s)/p_j(s) = -q_j(t)/q_k(t).  So G[III + IV] is the line digraph of
the bipartite digraph Gamma_j whose vertices are the values on two copies of Q*.  Here III t is the arc
(-q_j/q_k)(t) -> (p_l/p_j)(t) and IV s is the arc (-q_j/q_l)(s) -> (p_k/p_j)(s), and t -> s iff head(t) = tail(s).  A set
of arcs induces an acyclic subdigraph of a line digraph iff it contains no closed walk, so for any linear order of the
vertices of Gamma_j, the forward arcs or the backward arcs (at least half) qualify.  Sources and sinks can be added
to any acyclic set.  []
Hence cost >= sum_j MAS(G[D_j]) >= sum_j MAS(G[P_j]) >= |P|/2 for every decoder, over any field.
Check: private.py, 400 random private-only configurations (entries {+-1,+-2,3,0}, 6-15 lines): 0 violations, 34 tight.

**6.3 Two-shared lines.**  For S_12 = {t : D(t) = {1,2}} (so p_3 q_3 = 0), an incidence t -> s is "tame" (third product
0, so alpha(t) = beta(s) exactly, as in the T = 2 argument) whenever p_3(t) = 0 or q_3(s) = 0.  The four sets
{alpha < beta or alpha > beta} x {p_3 = 0, or q_3 = 0 and p_3 != 0} contain only tame edges, so each is acyclic and
MAS(G[S_12]) >= |S_12|/4.  Since S_12 lies in both D_1 and D_2, these lines alone contribute >= |S_12|/2 to the MAS-sum.

**6.4 Conjecture M (MAS-sum >= v/2) and its char-2 obstruction.**  Conjecture: sum_j MAS(G[D_j]) >= v/2 for every
rational T = 3 decoder.  This is field-sensitive and would give cost >= v/2 (closing D7, D8 and E6 h >= 18, and
E7 h >= 17).
Evidence:
- 6.2 and 6.3 handle private lines and each two-shared class separately; what is missing is the interaction between
  classes inside one D_j, and full-D lines, which need weight 1/6 per D_j.
- Hill-climb searches (massrch.py) found minima of 5/8 and 6/9 (pool {-1,0,1}) and 8/10 (pool {-1,0,1,2}).
- The natural way to go below 1/2 fails exactly in characteristic != 2.  The gadget is one full-D line x forming a
  triangle with a private III/IV digon in each of D_1, D_2, D_3, so MAS-sum = 3 on 7 lines.  This forces p(x)'s three
  traces (0,x2,x3), (x1,0,x3), (x1,x2,0) onto the line l(x).  Their determinant is -2 x1 x2 x3 (sympy), so they are
  collinear only in characteristic 2 (Fano), the same obstruction as for cost < v at T >= 7.
A proof needs (i) a weighted version of 6.2 and 6.3 inside one D_j (an acyclic-set distribution covering private lines
with probability >= 1/2, two-shared lines >= 1/4 and full-D lines >= 1/6) and (ii) bounded fractional dichromatic number
(<= 6) for full-D incidence digraphs.  (ii) is plausible: a complete digraph on 3 vertices gives 3, and fullmas2.py
found MAS/v = 1/2 at its worst.

**6.5 Where the obvious weighted version of 6.2 and 6.3 stops.**  Fix D_1 and normalise p_1 = q_1 = 1.  Put
PT(t) = {k in {2,3} : p_k(t) != 0} and LT(s) = {k : q_k(s) != 0}.  An incidence t -> s uses the terms PT(t) cap LT(s),
which is nonempty.  Each family F_k^p = {PT = {k}} and F_k^q = {LT = {k}} has only coordinate-k ("tame") edges, so it is
a T = 2 structure: sources, sinks and two acyclic halves.  Private lines are sources or sinks in both families that
contain them (coverage 1/2, which is how 6.2 arises).  But a line with |pi| = 2 and sigma = [3] lies in one family per D_j
it belongs to.  The six resulting constraints P_1(F_2^p) + P_2(F_1^p) >= 1, ... use every family probability exactly
once (total 3 < 6).  So tame families cover such lines only with weight 1/4 in total, and MAS-sum >= v/2 needs acyclic
sets that contain wild edges.  In D_1, the lines of these types form a "one head, two tails" digraph: each t has a head
(c(t), -1/u_c(t)) and tails (2, w_2), (3, w_3), and t -> s iff head(t) is a tail of s.  A random vertex order gives
MAS >= 1/3 there, and complete digraphs on 3 vertices are impossible (they would need three distinct coordinates in
{2,3}).  Whether 1/2 holds for this digraph class is the next concrete question.

## 7. Theorem M1: cost >= v/2 when no point has full support (any field)

**Theorem M1.**  If every point p(t) has a zero coordinate (|pi(t)| <= 2 for all t), then
  cost >= sum_j r_j >= sum_j MAS(G[D_j]) >= sum_t c(t) >= v/2,
where c(t) = |D(t)| / C(|pi(t)|+|sigma(t)|-2, |pi(t)|-1).  The same holds if every line q(s) has a zero coordinate
(|sigma(s)| <= 2): reverse all edges.  It holds over every field, and v/2 is sharp: a configuration of private
digons (section 0) has MAS-sum exactly v/2, and its certificate is v, so MAS-sum is the weak link there.

*Proof.*  Fix j and a chart: for t in D_j put x_k(t) = p_k(t)/p_j(t) and y_k(t) = q_k(t)/q_j(t) (k != j).  Let
V = {(k, c) : k != j, c in F*}, a set of "vertices".  Give t the vertices xi_k(t) = (k, -1/x_k(t)) for
k in pi(t) - {j} and eta_k(t) = (k, y_k(t)) for k in sigma(t) - {j}.
(a) Edges are vertex coincidences.  For t, s in D_j, pi(t) cap sigma(s) contains j and is not {j} (a single nonzero
    product cannot vanish).  Since |pi(t)| <= 2 it equals {j,k} with pi(t) = {j,k}, and
    p(t).q(s) = p_j(t) q_j(s) (1 + x_k(t) y_k(s)).  So t -> s iff xi_k(t) = eta_k(s).
(b) A line's vertices are distinct.  Different coordinates give different vertices.  xi_k(t) = eta_k(t) would give
    p(t).q(t) = 0, because pi(t) = {j,k}.
(c) Random order.  Order V uniformly at random and let X_j = {t in D_j : every eta-vertex of t precedes every
    xi-vertex of t}.  Along an edge t -> s inside X_j, the vertex xi_k(t) = eta_k(s) precedes every xi-vertex of s.
    So the earliest xi-vertex strictly increases along edges, X_j is acyclic, and B[X_j, X_j] is unit triangular.
    By (b), P(t in X_j) = 1 / C(m_xi + m_eta, m_xi), with m_xi = |pi(t)| - 1 and m_eta = |sigma(t)| - 1.
(d) Summing E|X_j| over j: line t contributes |D(t)| / C(...).  Going through the cases with |pi| <= 2:
    - |pi| = 1, or |sigma| = 1: contribution >= 1;
    - |pi| = 2, |sigma| = 2: 1/2 each, so 1/2 if |D| = 1 and 1 if |D| = 2;
    - |pi| = 2, |sigma| = 3: D = pi, so 2 x 1/3 = 2/3.
    Every line contributes >= 1/2, and for each j some order attains at least the expectation.  []
Check: thmM1.py, 300 random configurations with every point having a zero coordinate (6-14 lines, dense forced
incidences, entries {+-1,+-2,3,0}): MAS-sum >= sum c(t) in all of them, sum c(t) >= v/2 asserted.
Lemma 6.2 (private lines) is the case |pi|, |sigma| <= 2 inside one D_j.

**What blocks the general case (precise).**  The only edges not of form (a) are *wild*: t -> s with
pi(t) = sigma(s) = [3] (a full-support point on a full-support line), where 1 + x_2(t) y_2(s) + x_3(t) y_3(s) = 0.
Three kinds of lines are affected:
- B = {|pi| = 3, |sigma| <= 2}, the sources of wild edges;
- A' = {|pi| <= 2, |sigma| = 3}, their targets;
- F = full-support lines, which are both.
Excluding B or A' per chart (randomly) still gives MAS-sum >= (1/2)|others| + (1/3)|A' + B|.  This is a valid bound
whenever F is empty, but it is below v/2.  F needs a lower bound on MAS for general point-line incidence digraphs
(fraction 1/6 per chart would do; a complete digraph on 3 vertices gives 1/3).  So the next step is a potential
for wild edges.  For example, with all x_k > 0 > y_k a wild edge t -> s gives eta_k(s) < xi_k(t) in value for both
k, which matches the order of tame edges under the rule "xi before eta" (max xi strictly decreases along both
kinds of edge).  Sign patterns therefore look like the right way to split.

## 8. Attempts to remove the hypothesis of Theorem M1 (negative, exact)

- *Sign-order potentials for wild edges* (signlp*.py).  If a wild source t has both xi_k(t) > 0 (after per-coordinate sign
  flips) and the vertex order is by value, then every wild edge t -> s has some k with eta_k(s) < xi_k(t): write
  r_k = eta_k(s)/xi_k(t), so r_2 + r_3 = 1 and some r_k < 1.  So the rule "all xi before all eta" stays acyclic on wild
  edges too.  The LP below allows 16 orders per chart: sign flips, extreme interleavings of the two coordinates, and
  forward or reversed (p <-> q) mode.  Over all line sign-types (124 found by sampling):
  - optimum coverage = 0.  The full-support lines whose three products p_k q_k share a sign are never covered: their
    xi and eta have opposite signs in every coordinate, so safety and the rule clash.
  - Without full-support lines (p and q both full): optimum 5/16 < 1/2.
  So value-order potentials cannot give v/2 in general; wild edges need a block-rank argument.
- A trivial general corollary of M1: M1 on {|pi| <= 2} and its reverse on {|sigma| <= 2} give cost >= (v - |F|)/4,
  where F = lines with p and q both of full support.  Too weak for any window.
- Useful structural fact for the next attempt: with the support labels a = pi, b = sigma, K_ts = |pi(t) cap sigma(s)|
  mod 2 is 0 on every tame edge and 1 on every wild edge.  So the L8 sum and the MAS-sum kill complementary edge
  classes, and a hybrid (sums of 2 blocks plus a single block) is the natural next object.

## 9. The multi-copy certificate (MCC) -- strictly stronger than L8; cost(cex_min_1) >= 20 > v

**Lemma MC.**  Take any finite family of *copies* (t, c) of lines.  Give each copy labels a(t,c) subset pi(t) and
b(t,c) subset sigma(t), with |a(t,c) cap b(t,c)| odd.  Order the copies so that every pair (t,c) != (s,c') with
|a(t,c) cap b(s,c')| odd and (t -> s an incidence, or t = s) is forward.  Then cost >= sum_i r_i >= #copies.
Proof: let U_i[(t,c), t] = [i in a(t,c)] and V_i[s, (s,c')] = [i in b(s,c')].  Then
N := sum_i U_i B[R_i, A_i] V_i has entries N[(t,c),(s,c')] = B_ts |a(t,c) cap b(s,c')| (mod 2), so rank N <= sum_i r_i.
B_ts != 0 only on the diagonal and on incidences, and B_tt = 1, so N is unit upper triangular in the given order.  []
L8 is the one-copy case.  MAS-sum is the case of copies (t,j), j in D(t), with a = b = {j}: copies with different j
never interact.  So MCC >= max(L8 certificate, MAS-sum), and Theorem M1 and Theorem U are both MCC bounds.

**cex_min_1: MCC = 20 (CP-SAT OPTIMAL, up to 3 copies per line; mcc.py).**  The solution was re-verified by an
independent checker (verify() in mcc.py: label supports, odd diagonals, every odd entry on an incidence or same-line
pair is forward).  The solution is saved in mcc_cex_min_1_solution.json.  Hence **cost(cex_min_1) >= 20 >= v = 19**.
This refutes cex_min_1 as an obstruction to (A): it was only an obstruction to the one-copy certificate.
Sanity check: the private digon has MCC = 2 = v (its MAS-sum is 1).
More MCC data (all verified by verify()):
- 8 random {-1,0,1} configurations (9-14 lines, 22-62 incidences): L8 = v in each; MCC = v+1 to v+5 (OPTIMAL).
  Script: mcctest.py.
- 121-line pool: MCC >= 119 with 2 copies per line (FEASIBLE; two 9.5-min runs with different seeds; bound 164).
  L8 gives 115, so the pool is not yet shown to have cost >= v.
- Direction this points to: **Conjecture MCC: MCC >= v for every rational T = 3 configuration.**  It would give (A).
  It is a finite, checkable object per configuration.

**Heuristic warning about pure-MAS routes (not proved).**  Look at full-support configurations, where MAS-sum is
3 MAS(G) and G is an arbitrary point-line incidence digraph after a generic projective change.  Take v grid points
and v lines with Szemerédi–Trotter-extremal incidence counts (average degree ~ v^{1/3}).  If these digraphs behave
randomly, MAS(G) is ~ v^{2/3} log v = o(v), so Conjecture M (6.4) would fail asymptotically.  The only general lower
bound I have there is the hyperarc order argument, 1/(k+1) per line with k = number of used lines through its point.
So a general v/2 must use the F_2 / 2-adic label part of MCC (Theorem P-type copies) for full-support lines, together
with M1-type chart copies for the rest.  The interaction between the two kinds of copies (conflicts [j in a(t)] in both
directions) is the open step.

## 10. Per-scale 2-adic multi-copy certificate (rmcc.py, rmcc_run.py; all solutions re-verified by mcc.verify)

Each line gets one copy per scale e in E, labelled with the 2-adic reductions at e
(a = argmin_k nu(p_k) + e_k, b = argmin_k nu(q_k) - e_k); identical copies are merged.
- 'canon': these labels only.
- 'rep': also one-sided repairs at that scale (a' subset pi with |a' cap b| odd and b kept, or the mirror).
- 'target': adds, for every non-tied line, a (possibly half-integral) scale inside its good box.
  Tied lines have no scale at which they are non-isotropic.
E1 = {0,1}^3 - {(1,1,1)} (the 7 classes mod the all-ones vector); E2 = {0,1,2}^3.

| instance | v | L8 | canon E1 | rep E1 | rep+target | unrestricted MCC |
|---|---|---|---|---|---|---|
| cex_min_1 | 19 | 18 | 8 (opt; E2 also 8) | 20 | 20 | >= 20 (opt 20) |
| gap-1 triangle | 3 | 3 | 0 (opt; E2 also 0) | 3 (opt) | 3 | 3 |
| 121-pool | 121 | 115 | 91 (= |G|) | 119 | -- | >= 119 |
| 10 random {-1,0,1}, v 9-12 | | = v | 4-10 (< v in 10/10) | v+1..v+5 | same | equal to rep in 10/10 |
| 9 random {-2..2}, v 8-12 | | = v | 11-14 (>= v in 9/9) | v+3..v+7 | same | equal to rep in 9/9 |

(rep/MCC values on the random sets are best-found within 30-60 s, mostly FEASIBLE rather than proved optimal; canon
values are OPTIMAL.  The 10th {-2..2} instance was cut by the 10-min cap.)

Reading:
- The pure 2-adic derivation fails exactly on tied (unit-world) lines.  Those are isotropic at every scale, so the
  smallest failing instance is a single tied line, e.g. p = q = (1,1,0): canon = 0, v = 1.  On non-unit data
  ({-2..2}) canon alone already reaches >= v.
- With one-sided repairs per scale, the restricted certificate matches the best unrestricted multi-copy value on
  every instance tried, and is >= v everywhere except the pool.  On the pool it is 119 < 121, open: neither solver
  proved a bound.
- So the multi-scale object that would need a proof is "Theorem P at every scale, plus one-sided repairs, with copies
  of different scales ordered together".  Theorem P (one scale) and Theorem U (unit world, repairs + halves) are its
  one-scale cases.  The missing formal step is ordering across scales.  A conflict between copies at scales e != e'
  needs |a_e(t) cap b_e'(s)| odd on an incidence, and Lemma 1.1 says nothing about mixed scales.

## 11. Toward "cost >= v" (Oct 14): what the cross-scale lemma can and cannot be

**11.1 The per-scale 2-adic labels are inert on exactly the lines that matter.**  Canonical per-scale labels give |G|
(cex 8, pool 91) and 0 on tied lines, at every scale (§10).  A tied line is isotropic at every scale, so its
reductions have even |a cap b| everywhere.  Every gain to >= v comes from the one-sided repairs, i.e. from one free side.
So a cross-scale ordering lemma *for reductions* would formalise the part that contributes nothing.  The object that
needs a proof is a label-and-order scheme for tied lines that uses their real alpha/beta values (Theorem U does half).

**11.2 Proven ceiling: group-level schemes stop at 1/2, even with copies (unitmc.py).**  In the unit world, let a
scheme give each group a list of copies with labels.  The groups are (pi, sigma) for odd |D|, and (pi, sigma, half) for
tied lines, with clusters (D, half).  Multiple copies per line are allowed, ordered so that a later copy sends only even
entries back to an earlier one.  Cross-cluster conflicts are allowed only along an acyclic cluster order.  Incidence
between groups is "possible iff |pi(g) cap sigma(h)| is even" (Lemma 1.1).  Column generation (CP-SAT pricing, exact
LP) gives c* = 1/2 exactly.  The dual is supported uniformly (weight 1/6 each) on the six groups pi = D of size 2,
sigma = [3], all three classes, both halves.  So any rule of the form "scale order, then within-scale order", which in
the unit world is a function of (pi, sigma, half), cannot prove MCC >= v.  It is capped at 1/2 on that obstruction.

**11.3 The obstruction world W (pi = D of size 2, sigma = [3]).**
- Every incidence there is tame: t -> s iff head_{pi(t)}(t) = tail_{pi(t)}(s) in P^1 of the pair pi(t).
- Theorem M1 applies and gives MAS-sum >= 2v/3.
- Exact data (obst2.py, 8 random {-2..2} instances): MAS-sum >= v in all of them, MCC = v to v+1.  Hill-climbing
  (obstclimb.py, v = 10, entries {-3..3}) found minimum MAS-sum / v = 1.0 exactly.
- So in W the target is the purely combinatorial statement MAS-sum >= v, with no labels needed.
- It does NOT hold chart by chart.  In chart 1 the data (head, tail_12, tail_13) are three independent values, and
  abstract one-head-two-tails digraphs reach MAS/n = 0.4 (headtails.py).  So a proof must use the coupling between
  charts: tail_23 = tail_13 / tail_12.

**11.4 Pool status.**  Unrestricted MCC on the 121-line pool: 119 (C = 2, two seeds), and a C = 3 run with that
solution as hint is in progress.  Upper bound on the pool's cost by simulated annealing: 183 (uninformative).  Random
25-45-line sub-pools all have L8 = v, so they cannot separate.  Structured sub-pools are being tested (subtypes.py).

**11.5 Refutation of the certificate route to (A): the 12-line tetrahedral configuration.**
tied_min.json: the 4 full-support points p = (1,+-1,+-1), each paired with the 3 two-support lines q among
(0,1,+-1), (1,+-1,0), (1,0,+-1) that miss it.  So there are 12 lines, all tied (|D| = 2), with 72 incidences.  It was
found by greedily shrinking the 30 tied lines of the 121-pool while keeping MCC < v (shrinkmcc.py).
- L8 certificate = 11 (OPTIMAL).
- Multi-copy certificate = 11 with 1, 2, 4 and 6 copies per line (all OPTIMAL; solutions re-verified).
- True cost = 12 = v, from two independent exact solvers:
  - actualcost.py (CP-SAT) gives OPTIMAL 12;
  - costsat.py (pure CNF, Tseitin XOR chains, CaDiCaL) is UNSAT for every rank split with r_1 + r_2 + r_3 = 11, and SAT
    only at (4,4,4) for sum 12.
Consequences:
- (A) holds here, with equality.
- No certificate of the multi-copy kind can prove it: MCC = 11 < 12 = cost.  That kind includes L8, MAS-sum,
  Theorem P, Theorem U and the per-scale 2-adic copies with repairs, so it includes every cross-scale ordering lemma
  for them.
- **The cross-scale lemma requested on Oct 14 cannot exist in a form that yields cost >= v.**
- The same deficit shows in the 30 tied lines of the pool (MCC = 27 OPTIMAL with up to 4 copies, v = 30), and very
  likely explains the pool's 119 < 121.
- A proof of (A) must see genuine F_2 rank, not a single triangular minor of sum_j U_j B_j V_j with
  copy-type U_j, V_j.
- Next certificate class to test: general F_2 matrices U_j, V_j, i.e. arbitrary row and column combinations inside
  each block.  On the 12-line configuration, the optimum (4,4,4) means each block has rank exactly 4 at the minimum.

## 12. Why cost(tied_min) = 12 is forced, and the second-order lift framework

**12.1 Structure of tied_min.**  Points: the 4 vertices a of K4, realised as (1,+-1,+-1).  Classes k = 0,1,2, one per
missing coordinate of q, i.e. one per perfect matching M_k of K4.  Line (a,k) has point a and the class-k q-line that
misses a.  Every block row set R_j is everything, since points have full support.  Block j consists of the columns
of the two classes k != j: block j = S_k + S_l, where S_k is the span of the class-k columns.  Entry (row (x,c),
column (b,k)) is free iff x lies in the pair of M_k not containing b; the diagonal is 1; everything else is 0.  Rows of
class j have no diagonal entry inside block j.

**12.2 Exhaustive optimum structure (enumW.py, anaB.py; CaDiCaL with blocking clauses, run to exhaustion).**  There
are exactly 217 matrices B of cost 12, all with block ranks (4,4,4).
- 216 = 6^3 of them are class-block-diagonal: only same-class entries are used, and each 4x4 class block
  [[I,U],[V,I]] has rank 2.  So the S_k have disjoint row supports and cost = 2 sum_k dim S_k = 12.
- 1 of them, B0, uses 24 cross-class entries and has rank 4 with S_0 = S_1 = S_2 = W: cost = 3 dim W = 12.

**12.3 Proof that cost(tied_min) >= 12 (computer-assisted in step (b) only).**
(a) Every block has rank >= 3: MAS(G[D_j]) = 3 gives a unit-triangular 3x3 principal minor.
(b) A block of rank exactly 3 has a unique filling of its 8 columns (rank3.py, exhaustive SAT enumeration, the same
    for j = 0, 1, 2).  In it dim S_k = dim S_l = dim(S_k + S_l) = 3 (so S_k = S_l =: U), and every class-j row is 0 in
    those columns.
(c) Exchange.  If block j has rank 3, each other block contains class j and one of k, l, say S_j + S_l = S_j + U.
    U vanishes on the class-j rows T_j.  The projection of S_j onto T_j is B[T_j, C_j] = [[I_2, *],[*, I_2]], whose
    rank is >= 2 (the two identity blocks sit in different rows and columns of each pair).  So
    dim(S_j + U) >= rank B[T_j, C_j] + dim U >= 2 + 3 = 5.
(d) So either all blocks have rank >= 4, giving cost >= 12, or some block has rank 3 and cost >= 3 + 5 + 5 = 13.  []
Cross-checks: costsat.py gives UNSAT for every split with sum 11, and the only SAT split at 12 is (4,4,4).  The SAT
splits at 13 are exactly the permutations of (3,5,5) and (4,4,5), as (c) predicts.

**12.4 The second-order (mod 4) lift framework (recorded; not by itself a proof tool).**
- For any F_2 rank factorisation B_j = U V^T and integer lifts U + 2X, V + 2Y, the matrix
  N = sum_j D(p_j)(U+2X)(V+2Y)^T D(q_j) has rank_Q N <= sum_j r_j.
- On tied unit lines N = Delta + 2W.  Halving the tied rows gives
  N' mod 2 = diag(M_tt/2 mod 2) + sum_j Cbar_j.
- Cbar_j ranges over a coset of the tangent space {X V^T + U Y^T}.  Its class is the linking form
  phi_j(x,y) = (x^T B_j y)_Z / 2 mod 2 on (left kernel) x (right kernel).  If every phi_j vanishes, N' = I and
  cost >= v.
- This framework subsumes L8 and the multi-copy certificate.  Generic rank over a large unramified extension is the
  right invariant.
- But for a FIXED B, "some lift has rank v" is equivalent to sum r_j >= v (generic lifts give min(v, sum r_j)).  So
  it only becomes a proof tool through a B-independent argument on the coset family.
- On the 217 optima of tied_min the linking forms are mostly nonzero (rank 1-2 per block), so vanishing forms are not
  the mechanism there.

**12.5 Further evidence and failed general routes.**
- *F2S class* (full-support points, two-support lines; tied_min is its sharp member).  30 random {-2..2} F2S
  configurations with 8-13 lines and 20-66 incidences (f2stest.py): exact "cost <= v-1" is UNSAT for every rank split
  in all 30 (CaDiCaL), so cost >= v in all of them.  MCC there is v+2 to v+8 (OPTIMAL).  tied_min is special: it is
  the complete quadrangle against its own diagonal triangle (quads.py regenerates it from (a,b) = (1,1)).
- *Induction by deleting a line fails.*  Call a line rank-critical for B if deleting its row and column lowers some
  block rank.  If every B had one, (A) would follow by induction.  Among 1117 low-cost B on tied_min (splits (4,4,4),
  (3,5,5), (4,4,5), (5,5,5)), 850 have no rank-critical line (critical.py).
- *Per-class principal bounds fail.*  The polymatroid bound 2 cost >= 3 rank B + sum_k dim S_k gives only 9.  The
  principal 2-class minor can have rank 3 < 4.  The inequality cost >= sum_j mr_j + (1/2) sum_{i != j} dim(S_i cap K_j)
  (from the projection in 12.3(c)) is tight at both optimum types of tied_min.  A general lower bound
  sum_{i != j} dim(S_i cap K_j) >= v - 2 sum mr_j is what it would take; it is not proved.

**12.6 Exact-cost tool and current values.**  costsat2.py decides "cost <= K" with ONE CNF: per-block factorisations
with activity-ordered columns, plus a cardinality bound on the active columns (CaDiCaL).  Every SAT answer comes with a
B whose block ranks are recomputed by independent F_2 elimination.
- tied_min: K = 11 UNSAT, K = 12 SAT (4,4,4), in about 1 s.  This is a third independent confirmation of cost 12.
- cex_min_1 (v = 19): cost <= 22 (SAT, verified ranks (10,6,6)); MCC gives cost >= 20.  K = 21 and 20 were pending at
  the time of writing.
- 30 tied pool lines: cost <= 30 (split (10,10,10) SAT); MCC gives >= 27.  "cost <= 29" was not decided in 25 min.

**12.7 Liftability of the optima (L7 view).**
- All 216 class-block-diagonal optima of tied_min lift to Q with the same support and the same block ranks: each
  class block [[I,U],[V,I]] with UV = I over F_2 lifts with signs.
- The special optimum B0 also lifts: a +-1 assignment on its support gives Q-ranks (4,4,4) (liftB0.py).
- So on tied_min the F_2 optimum is attained by Q-realisable sign patterns, and L7 explains cost >= v there.
- Natural structural conjecture behind (A): *some cost-minimising B is jointly Q-liftable.*  It is false at T >= 7
  (Fano-type F_2 cancellation), so a proof must use T = 3, i.e. rank 3 / P^2 geometry.

## 13. Math-lead notes (Oct 14 midday): reductions valid for every configuration

**Lemma SCC (strong components).**  Let H be the digraph t -> s (t != s) with p(t).q(s) = 0 and
pi(t) cap sigma(s) != {} (exactly the incidences that land inside some block; incidences with
pi(t) cap sigma(s) = {} never appear in any block).  Order the strong components of H topologically.  Then every
block B[R_j, A_j] is block upper triangular in that order for EVERY admissible B, so
cost(config) >= sum over strong components C of cost(C).  Hence (A) needs only be proved for configurations whose
H is strongly connected.  (scc.py checks the triangularity on 500 random configurations.  tied_min and cex_min_1 are
each one strong component, of sizes 12 and 19.)
Proof: an entry (t,s) of a block that can be nonzero has t = s or t -> s in H, and then comp(t) <= comp(s).  A block
upper-triangular matrix has rank >= the sum of the ranks of its diagonal blocks, and the diagonal block of
component C in block j is exactly block j of the sub-configuration C.  []

**Lemma Peel (unit rows).**  If |pi(t)| = 1 (or |sigma(t)| = 1), then cost(config) >= cost(config - t) + 1.
Proof: say pi(t) = {j}.  Then t lies only in R_j, and t is in A_j because M_tt != 0.  For s in A_j,
p(t).q(s) = p_j q_j(s) != 0, so row t of block j is the unit vector e_t, and rank B_j = 1 + rank(B_j minus row t and
column t).  Deleting column t from the other blocks does not raise their ranks.  []
So (A) also reduces to configurations where every point and every line has at least two nonzero coordinates.

**F2S rowspace identity (cf. fleet/S2.md).**  If every point has full support (R_j = all lines), let
W = rowspace(B), rho = dim W and w_j = dim(W cap F_2^{C_j}).  Then cost = 3 rho - sum_j w_j >= 2 rho.  So in F2S, (A)
holds for every B with rank_F2 B >= v/2.  On tied_min both optimum types are tight in different ways:
- block-diagonal: rho = 6, w = (2,2,2);
- B0: rho = 4, w = (0,0,0).

**13.1 Framing: (A) is a coupled Haemers-minrank comparison between F_2 and Q.**
- For a digraph D, minrk_F(D) is the least rank of an F-matrix with nonzero diagonal and zeros off the arcs (Haemers;
  this is the linear index-coding optimum).
- Here block j is a matrix of exactly that kind for the digraph of incidences inside block j.  cost is a *sum* of
  three such ranks with the free entries *shared* between blocks, since an incidence t -> s sits in every block of
  pi(t) cap sigma(s).
- Lemma B says the Q-version of this coupled sum is >= v.
- (A) says F_2 cannot do better.  For single digraphs, F_2 minrank can be far below the real minrank
  (Lubetzky-Stav 2009, "Non-linear index coding outperforming the linear optimum": field-dependent minrank gaps).  So
  (A) cannot follow from minrank theory alone; it must use the P^2 incidence structure (K_{2,2}-freeness L6, no
  transitive 4-tournament L3, cliques meet all totals L4) and the coupling.
- tied_min shows the coupling is essential: the three decoupled F_2 minranks sum to 3+3+3 = 9 < 12.  The T >= 7
  failures are the coupled analogue of a Lubetzky-Stav gap, of Fano type.

**13.2 F2S exact decomposition, and three natural lemmas that are FALSE (adversarial annealing, exact F_2 ranks).**
Take W = rowspace(B), W_j^0 = W cap F_2^{C_j} (w_j = dim), U = W_0^0 + W_1^0 + W_2^0 (a direct sum) and
rho' = rho - sum w_j = dim W/U.  Then exactly
  cost = 3 rho - sum w_j = 2 sum_j w_j + 3 rho'.
- Block-diagonal optima of tied_min: w = (2,2,2), rho' = 0.
- B0: w = 0, rho' = 4.
With a_j = rank B[:, C_j] <= w_j + rho' this gives cost >= sum_j (a_j + w_j).  Natural sufficient lemmas, each
checked by annealing over B (lemmaN.py, lemmaNsum.py, lemmaN2.py), all FALSE by exactly 1 on small F2S
configurations (4-7 lines) where cost >= v still holds:
- N:   a_j + w_j >= n_j            (fails, e.g. a class with n = 2, a = 1, w = 0);
- N-sum: sum_j (a_j + w_j) >= v    (fails by 1; the step a_j <= w_j + rho' is lossy);
- N':  n_j <= 2 w_j + rho'         (fails by 1 on single classes; its sum is exactly (A)).
So in F2S the slack must move between classes.  No per-class rowspace inequality closes the proof; any proof needs
a joint argument across the three classes, as in the exchange of 12.3.

**13.3 The lift route, corrected (with fleet S1).**
- *Lemma W.*  If B has a signing B' (entries +-1 on supp B) that is totally unimodular, then every block of B' has
  rank_Q = rank_F2, and Lemma B gives cost(B) >= v.
  - Camion: a TU signing exists iff the binary matroid M[I | B] is regular.
  - Regularity of the column matroid M[B] alone is NOT enough: a full-rank B has M[B] free.
- Weaker hypothesis that still suffices: (G1') some cost-minimiser B has a rational lift B' with the same support,
  nonzero diagonal, and rank_Q B'[R_j,A_j] = rank_F2 B[R_j,A_j] for j = 1, 2, 3.  Then (A) follows from Lemma B.
- Checked: all 217 optima of tied_min have such a lift with +-1 entries (liftall.py, exact Q-ranks).
- S1 shows F7* blocks do occur for non-optimal admissible B, so (G1') must be a statement about some minimiser, not
  about all B.

**13.4 Structure of a minimal counterexample (rigorous).**  Monotonicity: restricting B to a subset S of lines gives
an admissible matrix for S, whose blocks are submatrices, so cost(S) <= cost(config).  Let config be a counterexample
to (A) with v minimal, and let B be a minimiser.  Then:
1. cost(config) = v - 1, and cost(config - t) = v - 1 for every line t.  Each one-line deletion is a *tight*
   configuration: by minimality v - 1 <= cost(config - t) <= cost(config) <= v - 1.
2. No line is rank-critical for B: deleting row t and column t lowers no block rank (by 1, B restricted is a minimiser
   of config - t with the same total).
3. H is strongly connected (Lemma SCC); every point and every line has >= 2 nonzero coordinates (Lemma Peel).
4. For every point P (and line l), with X = X_P (resp. Y_l), cost(config - X) <= v - 1 < (v - |X|) + |X|.  So
   Conjecture PP (fleet R6) would rule out minimal counterexamples.
Tight configurations (cost = v) are therefore the building blocks.  On tied_min, S2 found tight sub-configurations of
every size <= 10, but none of size 11 (all of those cost 12).

## 14. Synthesis after the fleet round (Oct 14, ~12:30)

**Proved, any field / any rational configuration:**
- Lemma B (lift identity).
- Lemma W' (fleet S1, corrected): if B has a TU signing (Camion: [I|B] regular), then cost(B) >= v.  More generally
  the same holds whenever B has a same-support rational lift with rank_Q = rank_F_2 on the three blocks.
- Lemma SCC and Lemma Peel (section 13): H strongly connected and no 1-support points or lines, WLOG.
- Minimal counterexample structure (13.4): cost = v - 1, every one-line deletion is tight, no rank-critical line.
- Exact F2S identities: cost = 3 rho - sum w_j = 2 sum w_j + 3 rho' >= 2 rho.  So (A) holds in F2S whenever
  rank B >= v/2.
- tied_min: cost = 12 by the exchange proof (12.3).  All 217 optima are TU-signable (S1) and lift (liftall.py).
- Theorems P, U (unit world, |G| + |I|/2) and M1 (no full-support points, v/2).

**Refuted (exact):**
- Certificate routes: L8, multi-copy, and per-scale 2-adic copies all stop at 11 on tied_min.
- Per-class rowspace lemmas N, N-sum and N' (13.2).
- "Every optimum is regular": S1's F7* gadget, v = 10, has a non-regular minimiser.
- "Non-degenerate admissible B is regular": S1's aff14, 14 distinct points and lines.
- Peeling induction PP: S2, 272 of 4095 tied_min subsets; a lone line costs |D(t)|.

**Evidence for (A):**
- S3: hill-climb over configurations (R <= 2, v <= 12) never below v; every climb ends exactly at cost = v.
- Exact: all 4095 sub-configurations of tied_min, 30 random F2S configurations, and every small instance checked earlier.

**The single remaining gap, sharpest form (G1'):**
  at T = 3, some cost-minimising admissible B has a same-support rational lift with nonzero diagonal and the same
  rank on each of the three blocks.
G1' implies (A) by Lemma B, and it fails at T >= 7 (Fano-type cancellation).
- Empirical selection rule (S1): a support-minimal minimiser is TU-signable.  Tested on about 120 small random grid
  configurations, all sub-configurations of tied_min, and the gadgets.
- Admissibility alone cannot give G1': non-regular admissible B exist, so the proof must use optimality, i.e. an
  exchange that removes Fano / F7* minors without raising any block rank.
