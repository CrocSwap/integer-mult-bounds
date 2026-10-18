# G1' at T = 3 (some cost-minimising B is TU-signable): status file

Status: G1' in the form "some minimiser is TU-signable as a whole matrix" is FALSE at T = 3 (section 6, v = 9).
The weaker form that Lemma B needs (one signing that makes each of the three BLOCKS TU) holds on every instance tested. No general proof.

Tools: enumall.c (exhaustive 2^f enumeration of all B, exact F2 block ranks, outputs every minimiser),
tusign.c (S1's Camion TU-signability test), g1lib.py, gadtest.py, fewest.py, dense.py, nonpack.py.

## 1. Exact data on S1's gadget (gad.json, v = 10, seven coincident points c, f = 29 free entries)
Exhaustive over all 2^29 B: min cost 19, 23552 minimisers, 3052 of them NOT TS (S1's SA sample reported 5/200).
- Every fewest-ones minimiser (6 ones; 5 of them) is TS: each is three disjoint 2-cycles (J2 pieces).
- Every non-TS minimiser has a minimiser on a proper sub-support, and every inclusion-minimal
  (support-minimal) minimiser is TS (0 of 3052). So "support-minimal => TS" holds here; fewest-ones is a corollary.
- Single-entry deletion does NOT suffice: 32 minimisers are non-TS yet no single deletion keeps cost 19.
  Their nearest sub-minimisers need removal of 2 entries (26 cases) or 3 entries (6 cases).
  So any exchange proof must be a multi-entry move.

## 2. Packing structure: TRUE on random configs, FALSE in general (refuted, exact)
Observation: for 450 random configs (v 6-12, exhaustive), every fewest-ones minimiser is TS, and in most of them
its support is a vertex-disjoint union of directed cycles (I + permutation) and K3 cliques (J3). Such "packings" are
direct sums of TU-signable pieces, hence TS, and would give (A) directly.
But three configurations (nonpack_cfgs.json: c47 v=7 cost 8; c511 v=7 cost 9; c58 v=10 cost 16) have NO packing
minimiser at all (all 12 / 8 / 4 minimisers checked). Their fewest-ones minimisers contain strongly connected pieces with
(vertices, edges) = (4,7), (5,11), (5,8). They are still TS. So the optimum genuinely uses non-principal block effects
(R_j != A_j), and G1' cannot be reduced to cycle/clique packings.

## 3. Proved facts used
- Every off-diagonal admissible entry (t,s) lies in >= 2 blocks: p(t).q(s)=0 forces |supp p(t) cap supp q(s)| != 1.
- Clique pieces have size <= 3 (cliques need distinct points and lines; a 4-clique forces three collinear points
  on two different lines). A K2 piece meets >= 2 blocks and a K3 piece meets all 3 (proof: a K2 bad in two blocks
  forces q_s = L_a containing p_s). [direct check; packings satisfy (A) without lifts]
- Deleting a 1 at (t,s) from a block M raises rank iff row t is in the span of the other rows of M and column s
  in the span of the other columns.

## 4. Mining the TS-restoring move on gad.json (mine.py, obst.py; exact, all 3052 non-TS minimisers)
For each non-TS minimiser B, the smallest X subset supp(B) with B - X a TS minimiser has |X| = 1 (1952), 2 (832), 3 (228),
4 (36), 5 (4). (These counts allow X with B - X TS but not support-minimal; section 1's "32 need 2-3" is about single
deletions that stay minimisers at all.)
- In 1952 cases X is one entry, and in 2280 cases some optimal X lies in ONE column with rows at the coincident
  point c (the "re-route coincident rows" move S1 anticipated). The other 772 need X spread over 2-3 columns:
  the coincident-point move alone does not cover every case.
- Minimal non-signable submatrices (greedy row/column deletion, 300 samples) are tiny: 4x4 with 9 ones (147),
  3x4 or 4x3 with 9 ones (98; this is the F7 matrix [110,011,101,111] itself, as a plain submatrix), 4x5/5x5 with 11.
  Some optimal X lies INSIDE that obstruction in 251/300 cases and meets it in all 300. So the exchange is local to the obstruction,
  but the obstruction is not unique (deleting inside the first one found is not always optimal).
Geometric reading: a 3x4 F7 submatrix whose ones are all off-diagonal needs three collinear points on four columns
whose lines all equal that line (or coincident points). With distinct points and lines, every F7 submatrix must use diagonal entries.

## 5. Gadget variants (gadvar.py, exhaustive, six random realisations of the F G^T = I_3 gadget, v = 10, f = 21-27)
| f | min cost | #minimisers | non-TS | support-minimal minimisers (non-TS) |
|---|---|---|---|---|
| 26 | 20 | 3072 | 144 | 2 (0) |
| 21 | 15 | 80896 | 12284 | 4 (0) |
| 26 | 20 | 4096 | 101 | 4 (0) |
| 23 | 17 | 115200 | 20308 | 10 (0) |
| 27 | 16 | 384 | 14 | 2 (0) |
| 23 | 14 | 4608 | 184 | 3 (0) |
Up to 18% of the minimisers are non-TS, but every support-minimal minimiser is TS (30/30), so G1' holds in all of them.

## 6. COUNTEREXAMPLE to whole-matrix G1' (found by worker w1, verified here exactly): cex_wholeTS_v9.json
P = (2,-1,-2) (1,0,-1) (2,2,-1) (0,-6,3) (-3,-2,1) (3,2,-1) (-2,0,-2) (1,3,1) (-2,2,0)
Q = (-2,2,2) (1,1,2) (1,1,2) (0,6,-3) (4,0,8) (3,-1,-3) (4,0,8) (1,0,1) (-1,0,-1)
v = 9, f = 13. Exhaustive: min cost 18, 16 minimisers, block ranks (7,4,7) for all of them.
- NONE of the 16 minimisers is TU-signable as a whole 9x9 matrix. tusign.c and an independent Python Camion
  solver (jointsign.py) agree.
- Every block of every minimiser is TU-signable, and a JOINT signing exists (one sign per entry; the Camion
  equations of the three blocks are solved together). Its exact Fraction block ranks are (7,4,7), equal to the F2 ranks,
  for all 16 minimisers. So the lift that Lemma B needs exists, and (A) holds here (18 >= 9).
Fewest-ones minimiser (8 off-diagonal ones), rows:
  100100001 / 010000001 / 001000100 / 011100000 / 000010000 / 000001000 / 100000100 / 000000010 / 001000001
The whole-matrix obstruction combines entries that never sit together in one block (row 3 is not in R_0, row 8 is not
in R_2, and so on). So whole-matrix TS is the wrong invariant.

## 7. Corrected target (G1-joint), open
At T = 3, some cost-minimiser B admits one +-1 signing of supp(B) under which every block B[R_j,A_j] is TU.
This is a linear system over F2 (the union of the three blocks' Camion equations; jointsign.py). It implies
rank_Q = rank_F2 on each block, so by Lemma B it implies (A). It is weaker than whole-B TS and stronger than G1' (lift).
Evidence: it holds on every configuration tested here (gadget, its variants, c47/c511/c58, the v = 9 example).

## 8. Consequences for the selection rules (corrections to sections 1 and 5)
- The 8-ones minimiser of cex_wholeTS_v9 is both support-minimal and fewest-ones (w1: no minimiser on a proper sub-support),
  and it is not whole-TS. So "support-minimal => whole-TS" and "fewest-ones => whole-TS" (S1's rule) are FALSE.
  In w1/cfgA.json (v = 9, f = 18) the two fewest-ones minimisers split: one TS, one not.
  Sections 1 and 5 hold only on those instances.
- What survives everywhere tested: "support-minimal => joint block-TU signable" (section 7).
- cex_wholeTS_v9 is DEGENERATE on both sides. Lines 1 and 2 are equal, (1,1,2). Lines 4 and 6 are equal, (4,0,8).
  Lines 7 and 8 are the same projective line. Points 4 and 5 coincide, (-3,-2,1) ~ (3,2,-1). So "whole-TS fails only in
  degenerate configurations" remains open.
- w1's random +-1..3 lifts matched the block ranks in only 1 of 48000 trials. That does not conflict with section 6:
  the joint signing is a structured solution of the Camion linear system, not a random draw.

## 9. G1-joint: exact formulation (proved)
Let G be the bipartite support graph of B: row vertices t, column vertices s, an edge for every 1 (diagonal included).
Block j is the INDUCED subgraph G_j = G[V_j], with V_j = (rows R_j) + (columns A_j). Off-diagonal edges lie in >= 2 of
the G_j (section 3), and a diagonal edge (t,t) lies in |pi(t) cap sigma(t)| >= 1 of them.
Signs are written additively: x in F2^{E(G)}, x_e = 1 meaning entry e gets sign -1.

**Lemma 9.1 (chordless holonomy).** If a signing of a 0/1 matrix M is TU, then every chordless cycle gamma of its
support graph (length 2m) has sum_{e in gamma} x_e = m mod 2.
Proof: the rows and columns of gamma span a square submatrix whose support is exactly gamma (chordless), so it is a
2m-cycle matrix. Its determinant is +-(Pi_1 + (-1)^{m-1} Pi_2), where Pi_1, Pi_2 are the sign products of the two
perfect matchings (they differ by an m-cycle permutation). So it lies in {0, +-2}, and TU forces 0, i.e.
Pi_1 Pi_2 = (-1)^m: the number of -1 entries on gamma is = m mod 2 (check: J2, m = 2, all +1, det 0). []

**Lemma 9.2 (uniqueness up to scaling; Camion).** Two TU signings of M differ by a coboundary: x' = x + (r_t + c_s).
Proof: chordless cycles span the cycle space Z(G) over F2. By 9.1, x and x' have the same sum on each of them, hence on
all of Z(G). A vector orthogonal to Z(G) is a coboundary. Coboundaries (row and column scalings) preserve TU. []

**Theorem 9.3 (joint signability is a linear system).** B admits one signing with all three blocks TU iff
(i) each block B[R_j,A_j] is TU-signable, and
(ii) the F2 system { sum_{e in gamma} x_e = |gamma|/2 mod 2 : gamma a chordless cycle of some G_j } is consistent.
Proof: (=>) by 9.1 applied to each block. (<=) take a solution x and a TU signing s_j of block j. On G_j, x and s_j have
equal sums on every chordless cycle of G_j, hence on Z(G_j), so x|G_j = s_j + coboundary, and x|G_j is TU. []
Equivalently: with h_j the holonomy functional on Z(G_j), (ii) says h_0(g_0) + h_1(g_1) + h_2(g_2) = 0 whenever
g_0 + g_1 + g_2 = 0 with g_j in Z(G_j). Pairwise relations (g in Z(G_j) cap Z(G_k) = Z(G[V_j cap V_k])) never obstruct,
because a chordless cycle of the induced graph G[V_j cap V_k] is chordless in both G_j and G_k (S1, Lemma G). So an
obstruction to (ii) is a genuinely three-block ("Cech") relation.
Check: jsign.c builds exactly this system (Camion Eulerian equations of the three blocks, one shared variable per
entry). On cex_wholeTS_v9 all 16 minimisers pass (i) and (ii), while the whole-matrix system fails.

So G1-joint has two separate failure modes for a given minimiser: (F1) one block is not TU-signable (an F7/F7* minor
inside one block, as on the gadget, where block 2 is the whole matrix); (F2) a Cech relation across the three blocks.

## 10. Testing G1-joint (jsign.c, jsweep.py; exact; w1-style configurations: 3 points a_i with lines q_i plus lines
whose point/line pass through 0-2 of the q_i / a_i; v = 6-10, exhaustive over all B)
- **Both failure modes occur among minimisers.** (F2) Cech failures, where every block is TU-signable but there is no joint
  signing, show up already at v = 6 (cech_v8.json: v = 8, f = 11, one of 320 minimisers). (F1) failures, where a single block is not
  TU-signable, are common (up to ~25% of minimisers).
- **"Support-minimal => jointly signable" is FALSE.** Smallest instance found: supmin_fail_v8.json (v = 8, f = 12, cost 14).
  It has exactly 2 minimisers, both with 9 ones, both support-minimal, block ranks (4,5,5).
  One is whole-TS. The other has block 0 not TU-signable. They differ by the one-for-one SWAP (3,0) <-> (1,6).
  So neither fewest-ones nor support-minimality selects a good minimiser; any selection rule must see signability.
  The minimal obstruction in block 0 is rows (0,1,2,6) x cols (0,3,4,6) = [1110 / 0011 / 0101 / 1001]: an induced
  "odd theta" (branch vertices row 0 and column 6, three paths of length 3). Each path joins a row to a column, so it has
  odd length; the three chordless cycles would need holonomy (a+b)/2 + (b+c)/2 + (a+c)/2 = a+b+c = 9 = 1 mod 2, but their sum is 0.
  This is the basic F1 obstruction. It uses two DIAGONAL entries, (0,0) and (6,6), so non-degenerate geometry does not exclude it.
- Random sweep totals (jsweep_11.log): 6018 configurations; 60 have a Cech-failing minimiser, 1311 a block-non-TS minimiser, and none had zero jointly signable minimisers. Targeted climbing (jclimb.py) then found such configurations, see section 11.

## 11. COUNTEREXAMPLE to G1-joint (exact): cex_joint_v7.json, found by jclimb.py
P = (2,0,-2) (-32,-32,-48) (-4,-4,-4) (0,1,1) (-2,0,-1) (0,-1,1) (-2,-2,0)
Q = (2,-12,-4) (1,-2,0) (-2,2,-1) (-1,2,-1) (-2,0,2) (-4,4,0) (32,64,-64)
v = 7, f = 11. Exhaustive: min cost 12, exactly 4 minimisers (7, 8, 9 and 10 ones), all with block ranks (4,4,4).
In ALL FOUR, block 2 (rows 0-5, cols 0,2,3,4,6) is not TU-signable (tusign.c; the Python Camion solver agrees: no joint signing).
So no minimiser is jointly signable: G1-joint is FALSE at T = 3. (A) holds here: 12 >= 7.
Obstruction: the nonzero rows of block 2 are rows 0,2,3,4 = [10100 / 01110 / 00101 / 10011]. Dropping the leaf column 2
leaves an induced odd theta (branch vertices row 4 and column 3; paths r4-c0-r0-c3, r4-c4-r2-c3, r4-c6-r3-c3), using the
diagonal entries (0,0), (3,3) and (4,4).
**But the lift that Lemma B needs exists.** For the 7-ones minimiser, the same-support rational matrix
  [[-1,0,0,-2,0,0,0],[0,3,0,0,0,0,0],[0,0,1,-2,1,0,0],[0,0,0,-2,0,0,-1],[-2,0,0,0,-2,0,2],[0,0,0,0,0,2,0],[0,0,2,0,0,0,2]]
has exact Fraction block ranks (4,4,4) = the F2 ranks. Reason: block 2 has only 4 nonzero rows and F2 rank 4, so ANY odd lift
has Q-rank exactly 4. TU is irrelevant for a full-row-rank block.
For the 8-, 9- and 10-ones minimisers, 2000 random weightings in {+-1,+-2,3} found no lift. That is not a proof that none exists.

**Hierarchy, all now exact at T = 3:**
  whole-B TS (false, v = 9)  =>  joint block-TU (false, v = 7)  =>  G1'-lift (holds on every case tested).
So TU-signability is too strong an invariant. The surviving target is G1'-lift: some minimiser B has a rational B' with
supp B' = supp B and rank_Q B'[R_j,A_j] = rank_F2 B[R_j,A_j] for j = 0,1,2. A TU signing is needed only where a block is
rank-deficient. A rank-preserving lift has to kill the (r_j+1)-minors of each block, which is an algebraic condition, not a linear one.

## 12. G1'-lift settled EXACTLY on every no-joint configuration: a lift always exists, with +-1 entries
Tool: exactlift.py (sympy). Row and column scalings W -> D1 W D2 preserve all three block ranks, so the entries on a spanning forest
of supp(B) are fixed to 1 (gauge). One variable stays per independent cycle. The conditions are all (r_j+1)-minors of
each block = 0, plus prod(vars) != 0 (Rabinowitsch variable tinv). A lex Groebner basis decides the system over C.
rational_point() then finds an explicit point with entries in {+-1, +-2} and re-verifies the block ranks with exact Fractions.
Only rank_Q <= rank_F2 is needed for Lemma B (rank_Q >= rank_F2 holds automatically for odd integer lifts).
Results:
- cex_joint_v7 (= nojoint_5): all 4 minimisers lift, each with a UNIQUE gauge class, and all variables are +-1.
  So these are +-1 signings that preserve every block rank without being TU.
- All 14 no-joint configurations from jclimb2.py (nojoint_21_1..14, v = 7-10; 1 to 256 minimisers; first <= 12 minimisers each
  by ones count): EVERY minimiser tested is consistent, and almost all have a unique +-1 solution.
- Gadget gad.json: 8 non-TS minimisers (sample) all lift. S1's hand-built F7* matrix (gad.json B, ranks (7,7,7), no block
  TU-signable) also lifts, with entries in {+-1,+-2}.
- Beyond minimisers: random ADMISSIBLE B (not optimised) with at least one non-TU-signable block: 60/60 (w1-style configs) and
  74/74 (dense grid configs; 6 skipped with > 9 cycle variables) have a small rational rank-preserving lift.

**New sharpened conjecture (Lift-all, T = 3):** every admissible B, not only a minimiser, has a same-support rational lift
B' with rank_Q B'[R_j,A_j] <= rank_F2 B[R_j,A_j] for j = 0,1,2. By Lemma B, this gives cost(B) >= v for every B, i.e. (A).
It would make the selection problem disappear. Evidence: everything above; no counterexample in about 160 exact tests.
It is false at T >= 7 (Fano cancellation), so a proof must use the P^2(Q) incidence pattern.
Hierarchy now: whole-B TS (false, v = 9) => joint block-TU (false, v = 7) => Lift-all (open, no counterexample) => (A).

## 13. Hesse / Q(omega) test (hesse.py, hesse_hc.py; coordinator's runs in hesse_runs/)
Configurations from the Hesse configuration (9 points, 12 lines, plus the 12 extra pairwise intersection points) over the
Eisenstein integers, with exact arithmetic in Z[omega], under random projective transforms. In all runs (mine: 300 random +
20 climbs x 150 steps; coordinator: seeds 1-4 x 400 random, hc seeds 11-13), cost >= v everywhere, with many tight (cost = v) cases.
No "BELOW v" event. Lemma B holds over any field of characteristic 0, and the F2 obstructions seen are Fano-type
(characteristic 2) and not Hesse-type (characteristic 3). So there is no sign that the ORDER of Q (Sylvester-Gallai) is the
mechanism. The relevant input looks like "characteristic 0 geometry cannot host F2-cancelling patterns".

## 14. What the lift route really needs, and where a proof must come from
- Lemma B needs only SOME rational B' supported on (incidences + diagonal), with nonzero diagonal and
  sum_j rank_Q B'[R_j,A_j] <= cost(B). Same support is not required. So the honest target is
    **(Q <= F2):** min over rational admissible B' of the Q-cost <= min over F2 admissible B of the F2-cost,
  and (A) = (Q <= F2) + Lemma B. Same-support rank-preserving lifts (section 12) are a convenient witness for it.
  Every exact test so far has produced such a witness, almost always with +-1 entries in a unique gauge class.
- **Same-support Lift-all is probably the wrong final form.** With a_i collinear on a line L, all Y-lines equal
  to L and all Y-points equal to one point c not on L, and X-lines through c, the admissible pattern contains
  B = [[I_k, F],[G, I_m]] with F and G ARBITRARY 0/1 matrices. (Checked exactly for k = 3, m = 4: c = (1,2,3), L = (1,1,1),
  a = (1,2,-3),(2,1,-3),(1,-3,2); the free set is exactly X x Y + Y x X.) So any F2/Q minrank gap of a 0/1 pattern (Lubetzky-Stav type)
  embeds into a same-support lift question at T = 3. But there sub-support lifts always reach the F2 optimum
  (rank max(k,m)), so (Q <= F2) is unaffected. Any proof must therefore allow the support to change, e.g. an exchange
  that moves to a minimiser with a liftable pattern, or a direct construction of a cheap rational B'.
- **Mechanism status:** no proof. Every candidate invariant short of (Q <= F2) is now refuted at small v (whole-TS v = 9,
  joint-TU v = 7, packing, single-entry exchange, support-minimal/fewest-ones selection). The data point to
  "F2-optimal patterns at T = 3 admit +-1 rank-preserving signings", and these are not TU signings.
