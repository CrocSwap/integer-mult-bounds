# FINITE — residues (alpha) F7+P and (beta) S66+P of TWOSIDE (Oct 16)
Impl: t.c (adapted from SIX/s66.c; usage ./t d1 d2 p R): V1 = orbit reps of d1-dim label flats (12 gens), V2 = ALL d2-dim flats,
direction list = data80.txt (ALL |Off|<=80, 5680 incl. pencils; caps: 73/76 -> 36, everything else 32 at 7-flats), h qualifies iff
exists <=p lines whose removal gives rank_F2 l(Off(h) \ (L(V1) u L(V2))) <= R. Exact "remove one of R+1 independent lines" branching. Report = real rank of span.
## STATE
- FINITE: control: ./t 6 6 0 7 reproduces S66 (159 orbits, span 3, <=6 dirs). 
- FINITE: alpha ./t 7 4 0 7 (V 7-flat, F = ALL 4-flats, so P = any <=8-line weight<=4 piece): max span 4 (<=12 dirs), 52 orbit reps. alpha CLOSED-1 (span<=5). Single implementation (2nd impl not written: token cap).
- FINITE: beta rank<=6 (all non-basis y weight 6): ./t 6 6 2 6 and ./t 6 6 4 6 (p lines removed per h = superset of a common P): span 1 (1 dir). CLOSED-1 for b>=3.
- FINITE: beta rank<=7 (y of weight 7 allowed): ./t 6 6 2 7 see b_p2_R7.out; ./t 6 6 4 7 UNFINISHED (too slow).
- FINITE: beta p=2,R=7 still running at handoff (b_p2_R7.out; 82/159 reps, max span 4 so far, i.e. exactly b-1 for b=5; a rank-5 hit would reopen). p=4,R=7 not run. Card stopped at token cap.
