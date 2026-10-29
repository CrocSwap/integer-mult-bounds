# KILL-ALL7 — rows 263 [7^9] d=7 e=2, 399 [7^10] d=8 e=2, 602 [7^10,1] d=8 e=3 (Oct 16)
STATE: KILL-ALL7: DONE. 263, 399 KILLED (PS: impl A ka.c/ka2.c + impl B kb.py agree: 11 orbits, |N(A)|=3 disjoint partners, never A, two-flat covers 0). 602 KILLED via PS+1/T3+1 = impl A only (ka1.c, t3p.c); impl B +1 mode not run (Python ~>20 min) -> 602 CHECKED-1.
## Lemma PS (pair-span; CHECKED impl A ka.c/ka2.c, impl B kb.py). Call a direction h *qualifying* for 7-flats (A,B) if
rank_F2 ℓ(Off_E(h) ∖ (A ∪ B)) ≤ 7 (i.e. Off(h) ⊆ A ∪ B ∪ some 7-flat). By T3 (SEVEN S3) every qualifying h is a root, an E6A1 direction
or a point of an A2-plane (= E6^⊥); candidates = 120 roots + 3360 E6A1 dirs + 1120 A2-planes (plane = 2 vectors; generic point ⊇ all Off's).
Q(A,B) := dim span{qualifying h}. Over all 11 W(E8)-orbit reps A of the 43181 distinct 7-flat masks and all B:
  Q(A,B) ≥ 7 for exactly 3 B per A, and these 3 are the other three parts of the 4-part partition of the 120 lines cut by A's two functionals
  (|A∩B| = 0, A ∪ N(A) = all 120); never B = A. Q ≥ 8 for ≤ 3 B. (Histogram of Q over (rep,B): 0:350740 1:95322 2:21326 3:5112 4:2272 5:45 6:144 7:9 8:21.)
## Lemma PS+1 (602; ka1.c). Same with one extra global line l0 removed (qualifying iff rank ℓ(Off(h) ∖ (A∪B∪{l0})) ≤ 7, any l0):
  Q ≥ 8 for exactly 3 B per rep A, never B = A (self-span ≤ 1). Candidate list still complete: T3+1 (t3p.c, exhaustive over all pairs of
  maximal masks, no pruning beyond |L| ≤ 37): the six non-coverable rank-7 Levi types D7 A7 A1A6 A1A2A4 A4A3 D5A2 stay uncoverable with one
  extra line (0 pairs); with SEVEN's sub-Levi argument only E7/E6A1/E6 (all in the candidate list) remain.
## Kill argument (PROVEN mod Lemma F (SEVEN S1), T3, PS/PS+1).
Write R = {c ∈ K^p : Σ c_k w_k = 0} (w_k ∈ K^e Gale vectors; e = p − d). Lemma F: Off(h(c)) ⊆ ∪_{c_k≠0} L_k (∪ E_S).
* e = 2 (263, 399; P = all p pieces, all weight 7). w_k ≠ 0 (else Off ⊆ one 7-flat, ≤ 36 < 57). No w_a ∥ w_b (else Off(h) ⊆ two 7-flats:
  T3 ⇒ root, |Off|=57, but two flats never cover Off(root) — G777 lo1 'min leftover 1'; also kb.py 'two-flat covers' = 0).
  Fix any pair a,b: c^y (support {a,b,y}, c^y_y ≠ 0) for the d = p−2 other y are independent, and h(c^y) qualifies for (L_a,L_b) (L_k ⊆ its
  7-flat mask; qualification is monotone in A∪B). So Q(M_a,M_b) ≥ d ≥ 7 for EVERY pair of pieces ⇒ the p ≥ 9 flats M_k are pairwise distinct
  and pairwise in N(·), but |N(A)| = 3 ⇒ at most 4 pieces. Contradiction: 263, 399 KILLED.
* 602 (e = 3, S = {s} weight 1, E_S ⊆ {l0}: labels injective, g(1) = 1). w_s ≠ 0; w̄_k := w_k mod w_s ≠ 0 for sevens (else Off ⊆ L_k ∪ {l0}).
  Bad pair = w̄_a ∥ w̄_b ⇒ Off(h_ab) ⊆ L_a ∪ L_b ∪ {l0} ⇒ (RS8) h_ab ∥ r_{l0}; two bad pairs give proportional h's with different supports
  ⇒ at most ONE bad pair. Good pair a,b: {w_a,w_b,w_s} basis ⇒ 8 independent c^y (support {a,b,y,s}) ⇒ Q_{+l0}(M_a,M_b) ≥ 8.
  Piece a has ≥ 8 good partners whose flats lie in N(M_a) (3 flats) ⇒ some flat B carries ≥ 3 of them ⇒ ≥ 2 good pairs (B,B), but
  B ∉ N(B). Contradiction: 602 KILLED.
Controls: special pairs exist (Q = 7/8 attained, qualifying counts 56/63/64/169 per special pair) ⇒ test is not vacuous; T3+1 reproduces T3's
plain counts (E6A1 6009 pairs, root 2.7M) and min ranks; orbit sizes sum to 43181.
Files: gen.py → ka.in/lab.in; ka.c, ka2.c (PS list), ka1.c (PS+1), t3p.c (T3+1); kb.py (impl B, own E8/basis/labels/orbits/candidates, numpy).
