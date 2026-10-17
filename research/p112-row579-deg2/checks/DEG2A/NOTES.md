# DEG2A (impl A, finite search) row 579, conjecture C6 = DEG2
STATE: DEG2A: CLOSED at mask level (impl A only; B = DEG2B pending): no 6 sevens survive; 4- and 5-seven survivors exist only in La-orbit reps 1 and 8 (3464 / 3105 quads, then 2448 / 3672 five-sets), 0 six-sets.
Model: sevens a..; each pair has an Off-mask from the orbit list D4 (D7,A7,E6A1,D6,E6 + roots; gen = E6/D6 continuum, same-mask allowed only for gen; non-gen equal masks = parallel => excluded, graphic matroid is simple).
Constraints: every triangle of pairs: no line in exactly one of the 3 Off masks (necessary for h_bc = c.h_ac - a.h_ab); U = union of all pair leftovers Off(h_xy)\(L_x|L_y) <= 28 AND coverable by 3F4+F3 (triA coverable()). a has h_ab,h_ac non-root; La over 10 orbit reps; b,c,d,e.. over all 43180 masks (prefilter |Off\La|<=68 sound since max|L|=36).
quad.c: quad stage (4 sevens) all reps: survivors only rep1 (3464), rep8 (3105); reps 0,2,3,4,5,6,7,9: 0. ext.c: add one seven to configs (n->n+1), geomN.py: exact rational check that the pair vectors are realisable by points u_x (non-gen only; gen kept unchecked = conservative).
5-sets: rep1 2448 (72 exactly realisable, 2304 contain gen types unchecked, 72 not realisable), rep8 3672 (108 / 3456 / 108). 6-sets: 0 for both (ext found 0 on all e5_ok_*). Control: ext 4->5 reproduces quad5's stage5.
Files: quad.c quad5.c ext.c geom.py geomN.py pipe.sh surv_rep1.txt surv_rep8.txt q4_rep*.txt e5_ok_*.txt pipe_*.log
Caveat: single implementation; mask-level relaxation only (superset, so CLOSED is sound if code correct).
