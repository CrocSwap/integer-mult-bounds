# S1 (matroid route): status = NOT PROVED, NOT REFUTED; two reductions proved, one gap precise

Code: fleet/S1_code/ (reg.py = exact F2 regularity test via F7 / F7* minor search: tests pass on F7, F7*, graphic examples).

## 1. Checked facts (machine, exact)
- tied_min, all 217 optima (tied_min_optBs.json): all 3x217 blocks B[R_j,A_j] (12x8, F2-rank 4) are REGULAR (t1.py).
- STRONGER: the WHOLE 12x12 matrix B is regular for all 217 (ranks 6 for the 216 class-diagonal ones, 4 for B0) (t1b.py).
- Exhaustive minimisation (enum.c, all 2^f B, f<=26) on ~85 random small T=3 configs (v=6..9, incl. configs with repeated lines q0 and collinear points):
  every config has an optimum with all blocks regular AND with whole B regular; in these no minimiser at all had a nonregular block. 3000 random B on tied_min-like configs: 0 nonregular blocks.

## 2. Do Fano-minor blocks occur at T=3?  YES (non-optimal B), constructed (gad.py, gad.json, v=10)
Block j in affine coordinates: rows = points u(t) of Q^2, columns = lines not through 0; support of B inside incidence + unit diagonal.
Gadget: a_0,a_1,a_2 non-collinear points (own lines q_0,q_1,q_2 concurrent at c, a_i not on q_i);
seven lines s with point c (coincident points!) and q(s) = a_i a_j / a_i / free lines chosen so that the 3x7 part F satisfies F G^T = I_3,
G^T = the 7 nonzero vectors of F2^3 as rows (1604 solutions with column weights <= 2). B = [[I3,F],[G^T,I7]].
Contracting the 3 columns i gives I7 + G^T F of rank 4 with 3-dim kernel = simplex code => F7* minor. Verified: block 2 (10x10) rank 7, regular = False.
So F7* blocks are realisable by admissible B (p.q=0 pattern), but this needs degenerate geometry: coincident points (or q_0=q_1=q_2) -- 7 points b_s lie on the 3 lines in all Fano patterns, which forces concurrency/coincidence over Q.
(Pure rank-3 F7-column B with unit diagonal and admissible also exists, fano7.py, v=7, but there the block cuts R_j,A_j break the F7 and the cost is 8>=7.)
That gadget config: SA (40k steps) min cost 19 (v=10); minimisers include 5/200 with a nonregular block, but 1499/1507 minimisers have all blocks AND the whole B regular. Regular-restricted SA reaches the same min (19) on this and 4 random gadget variants (var.py): no gap found.
=> "every optimum is regular" is FALSE; "some optimum is regular" is untested-to-refuted.

## 3. Proven (rigorous)
**Lemma W (whole-B regularity gives joint lift, no gluing needed).** If the whole F2 matrix B (v x v) has a regular column matroid, it has a TU signing B'
(Tutte/Camion). Every B[R_j,A_j] is a submatrix, hence TU, hence rank_Q = rank_F2 (all minors are 0,+-1 and nonzero over Q iff over F2). B' has the same
support, B'_tt != 0. By Lemma B: v <= sum rank_Q B'[R_j,A_j] = cost(B). So: **(A) at T=3 follows if SOME cost-minimiser B has regular column matroid.**
The block-wise condition is the weaker hypothesis whose only extra difficulty is gluing (below).

**Lemma G (gluing, partial).** Blocks overlap in H_jk = B[R_j∩R_k, A_j∩A_k], the same entries. A chordless cycle of H_jk is a chordless cycle in both blocks, and
Camion forces the holonomy of every chordless cycle (n_- = m mod 2 for length 2m), so sigma_j|H_jk and sigma_k|H_jk have equal holonomy on all cycles (chordless cycles generate the cycle space) => they differ by a +-1 row/column gauge on each component.
Hence any two blocks can be glued; blocks 0,1,2 glue iff the pairwise-corrected signings also agree around cycles of H02 ∪ H12 that mix both overlaps
(Cech-type obstruction on triple overlap R0∩R1∩R2 x A0∩A1∩A2). I could not rule the obstruction out in general; it vanishes when the whole B is regular (Lemma W) or when H012 has no entries.

## 4. Gap (precise)
Need: (G1) at T=3 some cost-minimiser B has a regular whole column matroid (or all blocks regular plus vanishing triple-overlap obstruction).
No proof. Mechanism that should be used: a Fano/F7* minor forces coincident points or equal lines (F7 is not realisable as a point-line configuration over Q, Sylvester-Gallai-type); the exchange needed is
"replace B by B' = B with rows/columns of coincident points/equal lines re-routed", which should lower or keep rank; verified only computationally (no counterexample found, gap search on gadget variants negative).
Not tested: cex_min_1 (v=19) whole-B regularity of its best known B (cost 22, > v anyway); large v with many coincidences.

---
# ADDENDUM (second pass, L6 / non-degenerate bridge)

## A. CORRECTION to Lemma W / Lemma G above
"Column matroid M[B] regular" is NOT enough for a same-support rank-preserving signing (regularity of M[B] gives a TU matrix representing the matroid, in general with a different support). The correct sufficient condition is
**TS(B): B is TU-signable, i.e. [I|B] is regular, i.e. some +-1 signing of supp(B) is totally unimodular** (Camion: all square Eulerian submatrices sum = 0 mod 4; this is a LINEAR system over F2 in the sign bits, solved exactly by tusign.c, tests: J2, odd 3-cycle signable; 3x7 Fano matrix not).
Lemma W': TS(whole B) => every submatrix (all blocks) TU => rank_Q = rank_F2 for the signed B' (same support) => joint Q-lift => cost >= v by Lemma B. (Note this is strictly stronger than needed: the 3x7 Fano matrix is not TU-signable but trivially lifts with equal rank 3.)
Rechecked with the right notion: tied_min, all 217 optima: whole B TU-signable (217/217) and all 651 blocks TU-signable. (The earlier "regular" results for M[B] still hold but are the weaker statement.)

## B. Q1/Q2: does non-degenerate (L6, K22-free off-diagonal, unit diagonal) imply regular?  NO.
- Exhaustive: all K22-free unit-diagonal matrices n=4 (2902) and n=5 (301826): M[B] regular (trivial: F7 needs >=7 columns).
- Random greedy K22-free, n=6..11 (thousands): M[B] always regular. (k22.py)
- But TU-signability fails already at n=5 for K22-free B (k22b.py): e.g. rows [11100],[01110],[01101],[10111],[11011]; minimal non-signable submatrix is 4x4 [[1,1,1,0],[0,1,1,1],[0,1,1,0],[1,0,1,1]]. This B is realised by 5 DISTINCT points of P^2(Q) (realiz.py) and the resulting config has 8 minimisers, all TU-signable (cfgchk.py): non-signable is harmless when rank is full.
- COUNTEREXAMPLE (search14.py -> aff14.py, aff14.json): n=14, B=[[I7,N],[M,I7]] with N,M sparse (<=3 ones per row), off-diagonal K22-free, and M[B] has an F7*/F7 minor (contracting the first 7 columns leaves I+MN nonregular; whole 14-column matroid verified regular=False, rank 11). Realised by 14 DISTINCT affine points (all z != 0) and 14 DISTINCT lines (all q_z != 0), so the whole B is one block, admissible, and non-degenerate. So "non-degenerate => regular" is FALSE (smallest found n=14; I did not search for smaller).
  BUT this B is far from optimal: cost 31 vs SA minimum 24 (v=14); the SA minimiser is TU-signable (sa14.py).
Conclusion: L6 alone (K22-freeness) does not force regularity; the property must come from OPTIMALITY (cost-minimal B), not from admissibility.

## C. Q3 degenerate case: not closed
Empirics only: gadget (coincident points/equal lines) minimisers are mostly TS; regular-restricted SA matches unrestricted SA. 120+ further random grid configs (7-9 lines, distinct and with repeats, exhaustive over all B, f<=23; drv3.py): in every one some minimiser is TU-signable (up to 28 non-signable minimisers coexisting). Among inclusion-minimal and min-cardinality minimisers (12-25 informative configs, drv4.py) all were TU-signable -- candidate selection rule "take a support-minimal optimum", unproved, tested only on small random configs (most have B=I optimal, so weak evidence).
No exchange proof found. Remaining precise gap: show a support-minimal (or otherwise canonical) cost-minimiser is TU-signable at T=3; admissibility alone cannot (section B).
