> NOTE (package): the Results/Controls below were produced with the FIRST impl C (`d2.c`, not shipped) whose slot-cover oracle had a bug (a single `seen_empty` flag instead of one per slot dimension, see ../../MODEL.md). They are NOT claimed. The shipped `d2fix.c` is the fixed oracle; its rerun is the SLOT in ../../PROOF_MAP.md. Model description and usage below remain valid (usage: ./d2fix K MODE TYPE USECOV [SHARD NSHARDS]).

# DEG2C (second implementation of DEG2 check, independent of DEG2/triA.c and DEG2A/*)
STATE: DEG2C (pre-fix run, superseded; see note above)
Code d.c (pair stage, superseded), d2.c (search). Own Bourbaki E8 (same construction as R579/b.c), reuse of R579/b.c slot-cover oracle verbatim.
Usage: ./d2 K MODE TYPE USECOV [SHARD NSHARDS]; MODE 0 = DEG2 (h01,h02 non-root), MODE 1 = all-root control; TYPE 1..5 = D7,A7,E6A1,E6,D6 for h01.
## Model (mask level; relaxation of Lemma F)
 - Direction masks: Off(h)={lines t: <r_t,h>!=0}; all W-conjugates of the 6 masks root(w8) D7(w1) A7(w2) E6A1(w7) E6(w7+w8) D6(w1+w8) (union of Off(w_i), i in support,
   exact for positive combos). Orbit sizes 120/1080/8640/3360/1120/3780 (check printed). E6/D6 are one mask per A2-/A1A1-plane: for h in an A2-plane the projections of E8 roots
   lie on 6 line directions (3 root, 3 weight), so the only special directions are root and E6A1 types (own masks); in an A1A1-plane only a, b, a+-b (root, root, D7). So the finite
   mask set is exhaustive; continuum = same mask.
 - Triangle (x,y,z): <r,h_xy>,<r,h_yz>,<r,h_xz> dependent => no line in exactly one of three Off masks (sound necessary cond.). Equal masks allowed only for E6/D6 (distinct directions in one plane), else parallel => excluded (K8-graphic pattern needs distinct lines). Applied to all pairs.
 - L_x: maximal 7-flats (43180 masks = codim-2 subspaces of F2^9; count reproduced). Lo_xy = Off(h_xy)\(L_x u L_y); U = union of all Lo; need |U|<=28 and U covered by 3 four-flats+1 three-flat (b.c slot oracle); cover is monotone so used as prune at every stage.
 - Orbit reduction: h_01 = dominant rep of its type; L_0 over orbit reps of the stabiliser parabolic (union-find under simple reflections on the 43180 masks; masks closed under W checked). All else full (labelled, no seven-permutation symmetry breaking).
 - Only 3-term (triangle) dependencies of the graphic matroid are used (no 4-term / vector-realisability) => relaxation; a 0 is a valid kill, a positive count is only an upper bound.
## Controls (done)
 - 43180 L masks; pair covers: A7 71 size-ok pairs, 0 coverable (matches R579: A7 not coverable); E6A1 min coverable leftover 23 (144 coverable (La rep,Lb)); E6 24 (219); D7 14 (425).
 - Root-only (MODE 1) triple FOUND (L 0 1 38096, roots #0 #1 #112) and quad FOUND (L 0 2105 37648 4254; 6 root masks).
## Results (sharded runs sh_t{1,4,5}_*.out; E6A1 single run; labelled states, cover-pruned at every stage, h_01 = type rep, L_0 orbit rep; seven-permutations NOT quotiented)
 type of h_ab : triples(sevens 0,1,2) | quads | five-sets | six-sets
 D7   : 131 (606 size-only) | 101 | 40 | 0
 A7   : 0 (no coverable pair) | 0 | 0 | 0
 E6A1 : 401 | 921 | 196 | 0
 E6   : 807 | 2484 | 576 | 0
 D6   : 392 (400 size-only) | 338 | 232 | 0      [totals: quads 3844, fives 1044]
 Impl A (reported): quads at only 2 orbit reps (3464, 3105), fives 2448 / 3672, sixes 0.
 AGREE on sixes (0). DISAGREE on quad/five counts and on which types survive (mine: 4 of 5 types; totals 3844/1044 vs 6569/6120); counting conventions not reconciled.
