# DEG2 (P112-PUSH) row 579: no seven carries two non-root pair directions
STATE: DEG2: NOT CLOSED (budget). Triple (a,b,c) alone, size+shape, leaves coverable configurations in orbit reps 4 and 6; 4th/5th-seven stage NOT coded; impl B NOT coded.
Impl A triA.c (e8.h from R579b): L_a over the 10 mask-orbit reps, h_ab=A,h_ac=C over full Off-mask orbits of D7,A7,E6A1,D6,E6 (leftover<=28 after some L_b/L_c, all (h,b) entries kept, no dominance),
 U = A\(La|Lb) | C\(La|Lc) | (A^C)\(Lb|Lc)  [relaxation: Off(h_bc) >= A^C for any h_bc in span with both coefficients nonzero; collinear A==C nongeneric: A\(Lb|Lc), reported as "same-Off"].
 Then U (|U|<=28) tested for cover by 3 affine 3-flats + 1 affine 2-flat of F2^8 labels (own DFS over maximal flat masks).
Results mode 0 (C0_*.out): reps 0,2,3,9: 0 coverable (rep 2,9: no U<=28 at all). Reps 4 (464 of 1808 distinct U) and 6 (196 of 505) HAVE coverable U (min size 25 / 24). Reps 1,5,7,8 were still running (see C0_*.out).
 Size-only min |U| per rep: 27 22 33 27 25 21 24 28 23 42 => size alone does not kill (3rd pair adds little).
Controls: pairs-only (mode 1, drops X_bc) min |U| 14-27 (reproduces stepb R4 21-line config at rep5 size-only: 21 -> here 14 because mode 1 also admits same-Off). Cover-function planted/random control (CTL=1) was launched, result not read.
Not done: 4th/5th sevens (K5-type constraints) on the coverable triples of reps 4,6 (+1,5,7,8 if any); independent impl B.
UPDATE: reps 1 (5181/10537 coverable, min 23) and 8 (414/3026, min 23) also coverable; rep 5 not finished (process killed). Zero-coverable: 0,2,3,7,9.
