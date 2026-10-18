# HELPER: independent re-check of MASK9 case (b), d0 = 5, 6 (P112)  (Oct 15)
Code: helper/ind.py (stage 1: admissible subspaces), helper/ind2.py (stage 2: K / extras / support filter), helper/diag.py. Own lb propagation, own
matching/J-condition DFS, own orbit reduction (plane orbits under all 197 verified generators; dim-3 orbits under a random 16-gen subgroup).
Reused geometric inputs only: setup9.load (lines, frames, nbar, label classes) and the 197 perms (asserted orth-preserving, linear on labels, survivors fixed).
Results (exact agreement with MASK9):
- plane orbits 71. D=5 (need k>=4): 3-dim reps 104; dim4 5723 -> 2468; dim5 34741 -> 2035. D=6 (need k>=3): 3-dim reps 170 (204 orbits); dim4 9397 -> 7016; dim5 72159 -> 21982; dim6 71191? -> 3498 (final 3498).
- Stage 2: residue 0 for D=5 (2035 subspaces) and D=6 (3498). Reason, via diag.py: S0 (survivors s0 with rank B0[~C(Z0),~O_s0] = 8-D) is EMPTY for every Z0, so tau0 = 0;
  then sigma0 = D-1 needs k >= 10-D smalls (5 resp. 4) but max valid k is 4 (D=5) resp. 3 (D=6) on every Z0. Support filter never reached (vacuous), cliques counted 50940 (sizes 6-8) / 11852 (7-8, = MASK9).
Caveats: orbit-rep reduction relies on perms being automorphisms (checked); J-conditions applied to all K+extras subsets (only matters for rc>=2, impossible here).
Theorem U: IDEAL2 allows extra zeros on non-orthogonal pairs, so the iff hypothesis is NOT established for case-(b) N. Not needed here: class-level count already closes d0=5,6 (and tau0 kill is immediate).
