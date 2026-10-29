# KILL-A8 (P112-PUSH) rows 159 [7^8,6] d7 s6, 302 [7^9,6] d8 s5, 398 [7^9,6,1] d8 s6
STATE: KILL-A8: DONE. 159/302/398 KILLED in ALL scenarios by a scenario-free T-level argument (§3), impl C only for the frame/type steps (SAT 2nd impl timed out); 159 (I) has 2 impls.

## §1 Row 159 scenario (I): KILLED — no relief bound needed
ClassI + SEVEN S4 (D7R) => h_ab roots with the A7 pattern; Lemma F at h_ab (phi_k(h_ab)=0, k not in ab) gives Off_E(h_ab) ⊆ L_a ∪ L_b ∪ L_0.
Exempt ALL six-flat lines (strongest possible relief: any phi_0, any relief term). Any 4 pieces give an A3 sub-pattern; W(E8) has one A3 class,
so the fixed-chain relaxed pair cover applies to both A7 classes. It is UNSAT:
 - impl A: JOINT2 satP.py 4 3 0 (kissat UNSAT, drat-trim VERIFIED, satP_4_3_0_r.cnf/.drat).
 - impl C (here, non-SAT): gen.py (own E8 build, labels in lattice basis e_i-e_{i+1} (i<=6), e6+e7, -s; 43180 maximal 7-flat masks) + pc.c:
   per pair all ordered (L_a,L_b) with leftover Off∖(L_a∪L_b) of <=20 lines and label rank <=6 (181862 each), triangle join, union rank <=6.
   `./pc dat_4.txt 0` -> solutions=0 (9.5 s). Control `./pc dat_3.txt 0` -> 1 solution (A2 SAT, matches JOINT2 p=3 SAT).
So the "exact six-flat relief" asked for is moot: even unlimited relief on L_0 kills 159 (I). (Same argument re-kills 302 (I).)
Bonus (for KILL-SMALL / 398 (I)): `./pc dat_4.txt 1` (six-flat + ONE free line exempt) -> solutions=0 (115 s), control P=3 X1=1 -> 379.
 => JOINT2's timed-out case p=4 nx=3 x1=1 is UNSAT by impl C (impl A timed out: single impl). Applies to 262 (I) and 398 (I).

## §2 Scenarios (II),(III): frame-exempt pair cover (all three rows)
T-level Circuit Lemma (CARRIER §2, no lift, valid in every scenario): c_ab vanishing on the 7-pieces outside {a,b} (|K|=p-2<=d-1) gives
Off(h_ab) ∩ P112 ⊆ L_a ∪ L_b ∪ L_0 [∪ unit line], i.e. Off_E(h_ab) ∖ F ⊆ ... with F the frame. Drops (II) and kernel vectors (III) live on F only.
pcf.c = pc.c with all 8 frame lines removed from every Off. Frames: 2025, 12 orbits under W(D5) = pointwise stabiliser of the A3 chain
(frames.py, orbit sizes 120,60,960,240,120,120,120,120,15,120,15,15 sum 2025). frames_P4.out: all 12 orbits solutions=0.
=> IF h_ab are roots carrying an A3 pair pattern, (II) and (III) die for 159 and 302 (impl C only; 2nd impl NOT done).

## §3 Scenario-free kill (supersedes the conditional in §2)
(a) h_ab = h(c_ab) exists (|K|=p-2<=d-1) and is a ROOT in every scenario: types.py + pcf2 (P=2): for each maximal non-E7 perp type
    (D7,A7,A1A6,A1A2A4,A4A3,D5A2,E6A1; every other non-root h has Off ⊇ one of these, E6 ⊂ E6A1) and every frame orbit under W(perp h)
    (3,4,6,13,10,6,3 reps): allowed (L_a,L_b) = 0 with Off∖F ⊆ L_a∪L_b∪6-flat, both X1=0 and X1=1 (types.out). Control: root type allowed 183686..563846.
(b) c_ab unique up to scale (else c supported on {b}+small: root Off∖F ⊆ 7-flat∪6-flat[∪1], CARRIER P112 (7,6)+<=4 uncoverable, 2 impls);
    dim R_abc = 2 and dim R_abcd = 3 by the same argument, so each triangle is 3 coplanar roots = an A2 and each 4-set's 6 roots = an A3
    (rank-3 simply-laced subsystem with 6 lines), labelled graphically (triangle-preserving edge bijections of K4 come from S4).
(c) pcf.c: A3 pair cover with all 8 frame lines exempt, 12 frame orbits: 0 solutions (X1=0: frames_P4.out, rows 159/302; X1=1: frames_P4_x1.out, row 398).
=> No scenario survives for 159, 302, 398 (the scenario list is not even needed).
Second implementation status: (I) of 159 = impl A (JOINT2 DRAT) + impl C. Frame steps (a),(c): impl C only. satF.py (satP + solver-chosen orthogonal
exempt set) control P=3 SAT, P=4 'UNKNOWN' at 1150 s (20-min cap) -> AUDIT NEEDED: an independent 2nd impl of (a) and (c) (C or SAT by frame orbit).
Files: gen.py pc.c pcf.c frames.py types.py runf.sh runf1.sh runh.sh satF.py dat_*.txt fr_h*.txt frames_rep.txt *.out
