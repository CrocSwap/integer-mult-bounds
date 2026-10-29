# AUD-1 — independent audit of SEVEN / KILL-A8 / KILL-ALL7 / 113+262 (P112-PUSH, Oct 16)
STATE: AUD-1: DONE. 19, 113, 159, 262, 263, 302, 398, 602 PROVEN. SEVEN S4 (and with it 113/262) PROVEN-WITH-FIXES: the E6A1 exclusion comes from KILL-A8 (a). 399 PROVEN-WITH-FIXES: the card skipped s = 6 scenarios (II)/(III), and both close with no new computation (see item 3). Own 3rd implementation reproduces every finite number exactly.

## Own implementation (no shared code or data with lib.py/gen.py/s2.c/kb.py/kc.c)
e8.py: even-coordinate E8, Bourbaki simple roots, labels = simple-root coefficients mod 2 + constant bit. 2025 frames, 43181 distinct 7-flat masks
(all 2-dim dual subspaces; 11 W(E8) orbits, sizes 1,7560,4725,4320,8640,3360,3780,1575,4320,1120,3780).
cov.c: a brute-force search over all (A,B) mask pairs, leftover label rank <= R (optionally after deleting one line), then a triangle/K4 join with a global X and a global free line.
ps.c: Lemma PS/PS+1 (candidates: 120 roots + 3360 E6A1 lines (W-orbit of omega_7) + 1120 A2-planes (Off(generic point) = Off(r1) ∪ Off(r2), counted as 2 vectors)).
Rank-6 flat capacity = 20 lines (computed: max over independent triples of functionals).

## Results (out/*.out, ps_a.out, ps_b.out)
- Positive controls: A2 (P=3) X rank 6: x1=0 -> 1 solution, x1=1 -> 379 (= pc.c/s2.c). Root-type P=2 frame-exempt: 558854/558854 (frame orbit 0), 183686/563846 (frame orbit 1)
  ordered pairs = types.out/s2. T3 E6A1: 6009 unordered pairs (= PS1). E7 root, three 7-flats: 3.29M unordered (x0). PS histogram identical to KILL-ALL7's.
  P=4 join control (plant2.py): 4 planted 7-flats + a planted 6-flat. Targets = Off(h_ab)∖F ∩ (M_a∪M_b∪X), mask base = planted + 20 decoys -> 1 solution; with planted M3 removed from the base -> 0.
- (a) the 7 non-root maximal Levi types D7 A7 A1A6 A1A2A4 A4A3 D5A2 E6A1 × every frame orbit under W(perp) (3,4,6,13,10,6,3), with X = a rank-6 flat, x1 = 0/1: 0 everywhere.
- (c) A3 chain α1-α3-α4: 12 W(D5) frame orbits (orbit sizes match KILL-A8's), frame exempt, X = a rank-6 flat, x1 = 0 and 1: 0 solutions in all 24 runs. Without frame exemption (ClassI, 113/262): 0 for x1 = 0/1.
- T3 / T3+1: the six rank-7 Levi types: 0 pairs for three 7-flats, with and without one extra line.
- Two 7-flats never cover Off(root) (roots 0,57,119): 0.
- PS: for each of the 10 nonempty reps, exactly 3 B with Q >= 7, and these 3 are disjoint from A and from each other, with A ∪ partners = all 120 lines; Q(A,A) = 0. Histogram 0:350740 1:95322 2:21326 3:5112 4:2272 5:45 6:144 7:9 8:21.
  PS+1 (max over l0): exactly the same 3 B reach Q+ >= 8, and A itself stays < 8.

## Verdicts
1. SEVEN. Lemma F: PROVEN. It is a line-by-line evaluation of Σ c_j y_j^E = p_h. The graphic pattern holds because every target row has |P| = d+1, so the φ_P satisfy exactly one relation. This applies to the pair-pattern rows 19, 113, 159, 262, 302, 398 (263/399/602 have |P| = d+2 and use PS instead).
   T3: PROVEN (3rd impl agrees; the sub-Levi reduction is sound: dominant h, J ⊆ all∖m, Off(h) ⊇ Off(ω_m); m = 8 alone gives a root).
   D7R: CHECKED (it follows from the T3 D7 result: rank <= 7 never occurs). FIX: S4's claim "hence every h_ab is a ROOT" does not follow from T3 + D7R, because T3 leaves E6A1 and E6.
   It is repaired by KILL-A8 (a) / AUD-1 (a): E6A1 with a 6-flat (+1 line) is uncoverable even with the frame exempt => PROVEN-WITH-FIXES.
   Row 19: PROVEN (own D4: 12 six-root hyperplanes, pair intersections 48×3 + 18×2, largest set of hyperplanes pairwise sharing >= 3 roots = 3 < 5; intrinsic to D4).
   Imports from G777: the 10 r_ab are distinct, lie in D4 and span V.
2. KILL-A8 §3 (159, 302, 398): PROVEN. Steps (a) and (c) reproduced by an independent 3rd implementation. Step (b): the dim R_ab/R_abc/R_abcd argument is sound (the upper bounds come from
   a c supported on one 7-piece plus small pieces). It imports CARRIER P112 (7,6)+<=4 (2 impls). The scenario list is genuinely unnecessary: the argument is T-level with the frame exempt, so it holds in (I)/(II)/(III).
   SECOND/s2.c is independent: it reads no input files and builds E8 by reflection closure from the Cartan matrix.
3. KILL-ALL7. Lemma PS and PS+1: PROVEN (exact agreement with ka.c and kb.py; kc.c is a port of kb.py, so ps.c is the genuine 2nd independent build. In the Q+ histogram only the >= 8 bin is exact, because of a pruning shortcut, and that bin is all the argument uses). 263 (s=7): PROVEN. 602 (s=7): PROVEN (PS+1/T3+1 now have 3 impls; imports RS8 = G4).
   399: PROVEN-WITH-FIXES. Its slack is s = 6, so L120D0 scenarios (II) (one deficient level) and (III) (z = 1) exist, while Lemma F's E8 version needs ClassI. The card ignores this.
   Fix for (II) (τ_m = 1 at a single level, so by the Lemma N greedy exactly one piece δ of the min basis drops, here a 7-piece): for c with c_δ = 0,
   z = 0 makes Σ c_j y_j^E = p_h^E exactly, and the no-drop lifts have support in Λ_E(F_j). So plain Lemma F holds on the 9 non-dropping pieces.
   No-parallel still holds (two 7-flats never cover Off(root): 0). Every pair among the 9 then has 7 independent c^y with c_δ = 0, so Q >= 7.
   Plain PS (|N| = 3, A ∉ N(A)) allows at most 4 pieces < 9 => (II) closes.
   Fix for (III): Lemma F gains the frame line f. A bad pair (w_a ∥ w_b) gives Off(h) ⊆ L_a∪L_b∪{f}, and G4 forces h ∥ r_f, so there is at most one bad pair.
   A good pair gives 8 independent c^y, so Q_{+f} >= 8. The 602 pigeonhole then applies (9 partners, >= 8 good, |N_{+}| = 3, B ∉ N_{+}(B)) => (III) closes (PS+1 is computed as a max over l0, which bounds any fixed f).
4. 113, 262: PROVEN. satP.py encodes c[a][t] => both functionals of piece a vanish at t, e[t] => t ∈ X or t = the single global free line, and coverage Off_E(h_ab) ⊆ M_a∪M_b∪X(∪free) over 120 lines
   for an A3 chain. That is exactly Lemma F in ClassI (s = 7 for both rows), with X = the 6-piece flat and the free line = the weight-1 piece.
   The p262 chunks are W(A3)×W(D5) line orbits 6/20/30/64 (= the 248 branching rule). Using them is valid because piece relabelling is a symmetry of the problem.
   h_ab being a root needs the S4 fix above. AUD-1 (c, no frame) gives a 3rd independent zero.
