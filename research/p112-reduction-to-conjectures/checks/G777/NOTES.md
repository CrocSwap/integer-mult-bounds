# G777 — 7-heavy block of the one-sided K2 residue
STATE: G777: started; reformulation = dual pair lemma (see §1); computing two-7-flat leftover tables (lo1.py).
- G777: lo1.py (impl A): two 7-flats vs Off_E(h): non-root types need leftover >= 14 (D7 14, E6A1 23, E6 24, A7 25, D6 26); root r: min leftover 1 ({r}, G5),
  but if r is COVERED by the flats, min leftover = 8. => RS8: Off(h) in L_a u L_b u E, |E|<=7 => h root, r in E; |E|<=13 => h root.
- G777: Pair Lemma: P = 7-pieces, S = e-1 other pieces (cap c_S<=20): each pair {a,b} of P gives distinct roots r_ab; c_S<=7 => C(|P|,2)<=c_S. Kills row 18 ([7^5,3,1]: 10>5).
- G777: lo2.py/nq.py (impl A): r covered => minimal leftovers have sizes 8 (315/root, label rank 4 = a full 8-line 4-flat "Q"), 12 (5040, rank 6), 16 (4032, rank 6);
  nothing of size 9-11,13-15. Each Q is the leftover of exactly 4 roots (9450 Q's), none of them in Q. Two Q's share <= 4 lines (3-flat cap), so |E|<=11 holds <= 1 Q.
- G777: LEMMA Q4 (pair lemma, refined): ClassI, P = 7-pieces, S = e-1 non-P pieces with c_S = cap(S) <= 11. Then C(|P|,2) <= c_S + 4.
  Kills (9 sevens, d=8, s=7, S = all smalls): 582 583 584 585 586 587 588 589 590 591 (c_S 8..10; 36 > 14) and 18 (10 > 5). Row 19 (10 <= 12) needs rank-4 refinement.
- G777: implB.py (independent: own E8 build, membership matrix + integer products) reproduces ALL of lo1/lo2/nq: non-root min leftovers 14/23/24/25/26, root r covered min 8,
  315 minimal leftovers <=11 all size 8 F2-rank 4, N_Q = 4 for all 315, no root inside Q. => kills of 18, 582-591 CHECKED (A+B).
- G777: row 19 tight structure: Q u Roots(Q) = 12 lines of rank 4 = a D4 (Q = D4 minus one of its 3 orthogonal A1^4 frames); the 10 r_ab can sit in that D4 inside the 4-dim h(R).
  Not killed; joint 5-flat realisability search not done (row19.py).
- G777: 6-Q's-in-13-lines impossible (deg count: nine 4s + four 3s gives sum C(deg,2)=66 > 15*4). Running m13.py for E = M u {l} (M = 12-leftover).
- G777: m13.py (A): all roots, minimal leftovers (r covered) <=13: only sizes 8 (9450 Q's, 4 roots each) and 12 (219240 sets, 2-4 roots each).
  max served roots over E = M u {l} (M an r0 12-leftover, WLOG by W) = 4; E without any M holds <= 5 Q's (deg count) -> <= 20. So pairs <= 13 + 20 = 33 < 36:
  kills 592 593 594 595 (c_S 12,12,12,13). B check: implB2.py (superset count |Off(r) n E| >= 8).
- G777: implB2.py (B, own r0 enumeration: 315 x 8 + 5040 x 12 minimal leftovers) superset bound: <= 18 roots outside E with |Off(r) n E| >= 8 for E = M(+1): 13+18 < 36. 592-595 CHECKED (A+B).
STATE: G777: DONE. LEMMA Q4 (two-7-flat root-swap rigidity) kills 15 rows: 18, 582-595 (A+B). Open 7-heavy: 19 (tight D4 structure, see row19.py), 113 159 262 263 302 398 399 579 596-602
  (c_S >= 15, triples of 7s, or s=6) = all 10 class-A seven-heavy rows (same rows as 113,159,262,263,302,398,399,600,601,602). Next: leftovers 14-22 incl. D7-type h; (7,7,7) triple version.
## LEMMA Q4 (statement). Hyp: ClassI (s=7); P = set of 7-pieces, |P|-2 <= d-1; S = the e-1 non-P pieces (E_S = union of their E8 supports, |E_S| <= c_S = sum g); c_S <= 13.
 For each pair {a,b} in P, c_ab in R vanishing on P\{a,b}: Off_E(h_ab) in L_a u L_b u E_S. c_S<=13 => h_ab root (D7 floor 14); 36+c_S<57 => r_ab pairwise distinct.
 r_ab not in E_S => r_ab covered by the flats => a minimal leftover (Q:8 or M:12) lies in E_S.  Conclusions: c_S<=7: C(|P|,2)<=c_S; c_S<=11: <=c_S+4; c_S<=13: <=c_S+20.
 Deps = those of RRC (CARRIER s1.3 ClassI, Circuit Lemma E8, G1, g-table). Validation: lo1/implB reproduce G4 (|E|<=2 => r in E) and G5 (min leftover 1).
 kills.json = per-row certificates (583/584 c_S = 8). Note: ulimit -v is a no-op on macOS.
