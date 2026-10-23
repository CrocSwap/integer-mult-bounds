# SEVEN — 7-heavy residue rows (theory card)
STATE: SEVEN: started; row 19 tight case KILLED (2 impls); working on Q4 extensions.
## S1. Lemma F (functional form of the E8 Circuit Lemma; PROVEN from CARRIER §2 E8 version, ClassI)
V := h(R) (dim d), φ_j := c_j∘h^{-1} ∈ V*. Evaluating Σ_j c_j y_j^E = p^E_{h(c)} at line t: for every E8 line t,
  ⟨·, r_t⟩|_V = Σ_{j : t ∈ supp y_j} y_j(t) φ_j  ∈ span{φ_j : t ∈ L_j}.     (F)
Consequence (pair pattern): if the 7-pieces P satisfy |P| − 2 ≤ d − 1 and c_ab := the element vanishing on P∖{a,b} is unique up to scale
(true whenever {c: supp ⊆ {a,b}} = 0, e.g. by G3 (7,7) uncoverable), then h_ab = ∩_{k∈P∖{a,b}} ker φ_k and the lines {h_ab} realise the graphic
matroid of K_|P| (rescale coordinates: h_ab ↔ e_a − e_b). In particular h_ab, h_ac, h_bc are coplanar, and for each k, H_k := ∩ ker φ_k ⊇ {h_ab : k ∉ ab}.
## S2. Row 19 [7^5,4] d=4 — KILLED (tight case of G777/Q4)
G777: 10 distinct roots r_ab, E_S = Q, all r_ab ∈ Q ∪ Roots(Q) = D4 (12 lines), V = span D4 (10 roots span 4 dims, G2).
H_k = ker φ_k (k = 1..5) contains the 6 roots r_ab, ab ⊆ [5]∖k ⇒ H_k is a 3-dim subspace with 6 D4 roots = an A3 (D3) hyperplane;
H_k ∩ H_l ⊇ {r_ab : ab ⊆ [5]∖{k,l}}: 3 distinct roots ⇒ an A2 plane.  D4 has exactly 12 such hyperplanes, in 3 triality classes of 4
(normals = one A1^4-type frame of D4 / its two triality images); two from the same class meet in A1×A1 (2 roots), from different classes in A2.
So {H_1..H_5} is a 5-clique in K_{4,4,4}: impossible (pigeonhole, 3 classes). ∎
CHECK: r19a.py (A: G777's Q2r.pkl Q's, sympy ranks, root-set intersections; 3 Q's): 12 six-root hyperplanes, 0 valid 5-configs.
       r19b.py (B: own E8 build, D4 = E8 ∩ span(e1..e4), integer 4-d cross products, exact triple intersection lines): 12 hyperplanes, 0 valid
       5-configs; pair intersections 48×3 roots, 18×2 roots (= 3 classes × C(4,2)). Uses: W(E8) transitive on D4 subsystems (classical).
Note (why tight): A4 has exactly 10 lines with this pattern; only Q4's D4 confinement kills it.
- SEVEN progress (~85k tokens): row 19 KILLED (S2). Lemma T3 (impl A, tri7.c): Off_E(h) ⊆ three 7-flats ⇒ h is a root or h ∈ an A2-plane
  (= E6^⊥; types E6, E6A1 coverable, 5442 flat-pairs each); D7, A7, A1A6, A1A2A4, A4A3, D5A2 (and every sub-parabolic) NOT coverable. Impl B running.
## S3. Lemma T3 (three 7-flats) — CHECKED (A: tri7.c on lib.py labels, maximal masks + F2-rank of leftover; B: triB.c, own E8 build/basis/labels,
all distinct masks, annihilator test).  Off_E(h) ⊆ L_A ∪ L_B ∪ L_C (7-flats) ⇒ ⊥-type of h ∈ {E7 (root), E6A1, E6}, i.e. h is a root or h lies in an
A2-plane (= E6^⊥). The rank-7 parabolic types D7(78) A7(92) A1A6(98) D5A2(97) A4A3(104) A1A2A4(106) are not coverable (A and B: 0 pairs); every other
non-root type has ⊥-set inside one of these (a J missing node 8 and another node m ≤ 7 lies in all∖m) except J = E6, checked separately (coverable).
Use: in an e = 2 ClassI row, every triple T of 7-pieces gives h_T (support T) of this kind; the 4 h_T of a 4-set are coplanar (W_M dim 2).
Not a kill by itself: 5-sets give 5 lines in general position in P(U) (U 3-dim) and an A3-span U carries 4 A2-lines, so the pattern fits (blocker = joint covering).
## S4. Lemma D7R — CHECKED (A: d7in6.c, B: d7B.c). Every two-7-flat leftover of a D7-type h with ≤ 20 lines has label rank ≥ 8 (A: min rank 8,
example leftover {0,1,3,4,8,9,15,16,24,25,35,36,112,113} rank 8, re-checked by plain elimination; B: no leftover ≤ 20 inside any ≤7-flat).
Hence in Q4's setting, if the small flats' labels span ≤ 7 dims (S = {6}, {6,1}, {5,1}, ...) every h_ab is a ROOT, and (S1) the roots h_ab form an
A_{|P|−1} root subsystem (graphic pattern + all triangles A2). Rows 113 [7^7,6] (A6), 262 [7^8,6,1] (A7), 159 [7^8,6], 302 [7^9,6] (A8; s ≤ 6) reduce to this.
Level-set count (lvl.py, Lemma F in A-coordinates: line t ∉ E_S lies in ≥ p − maxlevel(⟨r_t,u_a⟩) seven-flats): 113: Σ = 252 = 36·7 exactly (tight!),
but after excusing the 20 E_S lines 192 ≤ 252; 159/262: 228/224 ≤ 288. Not a kill (E_S lines need the φ_s refinement; A6 class uniqueness not checked).
## S5. Q4 re-verification of rows 103–111, 249–258 (already KILLED by the span pass; Q4 is an independent 2nd route): q4A.txt (python) = q4B.txt (awk), all KILL:
c_S ≤ 7: 103–108, 249–252 (pairs 21/28 > c_S); c_S ≤ 11: 109 (21>12), 110,111 (21>14), 253–255 (28>12), 256 (28>13), 257,258 (28>15). All s = 7, |P|−2 = d−1.
## Open list after SEVEN (37 of the 38): seven-heavy 113 159 262 263 302 398 399 579 596 597 598 599 600 601 602 + six-heavy 169 303 312 315 316 332 333
400 401 402 409 411 417 418 420 424 425 426 427 430 435 464 (untouched). Blockers: see final report / kills.json.
STATE: SEVEN: DONE (budget). Row 19 KILLED (A+B). New tools T3, D7R (A+B), Lemma F/A_{p-1} pattern. 37 open.
