# TWOSIDE — K1 two-sided residues R-b (b_Q>=5), R-dep, CONJ-G cost-64 residue (Oct 16)
Labels PROVEN / CHECKED (two implementations) / CHECKED-1 (single implementation) / OPEN. python = W/venv/bin/python.
## STATE
- TWOSIDE: read #3029 README, CONJ-G, R-B, SIX §1-3 (Lemma B, S66, Basis-kill), SMALL2 §4.
- TWOSIDE: bk1.py (impl 1): Basis-kill (Lemma B + S66) applied to all size/cap-feasible σ-multisets for b=5..8. Closes (5,1),(5,2) [ (b,1) already vacuous by WALL 8.3 b_Q<=1 ].

- TWOSIDE: F7 lemma CHECKED (f7.py/f7r.py, rank + explicit-cover impls agree). bk1b/bk2b (BK + F7) survivor counts agree in all 24 cells. R-dep reformulated exactly (§2, PROVEN). CONJ-G residue restated (§3). Card DONE at ~115k.

## §1 R-b (b_Q >= 5): Basis-kill transfer (PROVEN mod S66, which is CHECKED twice in SIX)
**Lemma BK.** Let B be a basis of span q(Lo) (|B| = ρ + b, b = b_Q), all pieces low (w <= 7). If some ρ pieces X0 ⊆ B have
Σ_{X0} g(w) < 53 and their weights pack into two groups of total weight <= 6 (+ at most one 1-piece), then b <= 3.
*Proof.* |∪_{X0} A_k| < 53 = d_1, so span q(X0) ∩ 𝒞 = 0: X0 is λ-independent for λ: span q(B) → span q(B)/(span ∩ 𝒞) ≅ K^ρ, hence a λ-basis.
SIX Lemma B (valid for every d; it uses only that B is a basis) gives b independent h_y (y ∉ X0) with Off(h_y) ⊆ U_{X0} ∪ Λ(F_y), w_y <= 7, so
rank ℓ(Off(h_y) ∖ X) <= 7 with X = Λ(V_1) ∪ Λ(V_2) [∪ t] ⊇ U_{X0}. S66 / S66+t: such h span <= 3. ∎
bk1.py table (impl 1; σ=0 pieces treated as weight 2, X0 = ρ smallest; level 1/2 caps (32,20,12) on |Off|<=72 / E6 targets, global otherwise):
| b \ t | 1 | 2 | 3 | 4 | 5 | 6 |  (min-Σσ survivor deficit; #survivors)
| 5 | 0 | 0 | 2 (4) | 2 (15) | 3 (38) | 3 (77) |
| 6 | 1 (1) | 1 (2) | 4 | 4 | 5 | 5 |
| 7 | 2 | 2 | 6 | 6 | 7 | 7 |
| 8 | 3 | 3 | 8 | 8 | 10 | 10 |
These are single-implementation survivor lists, NOT bounds on anything beyond "BX can fail only on these multisets".
- TWOSIDE: bk2.py (impl 2, own caps/brute packing) agrees: (5,1),(5,2) no survivors; (5,3) same 4 survivors. (5,2) CHECKED. ~75k tokens used.

**Lemma F7 (CHECKED, two implementations: f7r.py rank = Gaussian elimination; f7r.py cover = explicit 7-flat pair search).** For every
7-dim label space V (all 43435), the directions h with rank ℓ(Off(h) ∖ Λ(V)) <= 7 are at most 2, and they are frame directions.
Completeness: such h has Off(h) ⊆ Λ(V) ∪ Λ(G), G 7-dim; |Off| >= 73 is impossible (36+36), |Off| <= 72 gives |Off| <= 32+32 = 64 (C11),
so h is one of the 120 root/frame directions (SIX §3 list), all tested. Histogram: 0:41431, 1:1976, 2:28 (roots never qualify).
**Corollary BK7 (PROVEN mod F7).** If some ρ pieces X0 with Σ_{X0} g < 53 have Σ_{X0} w <= 7, then b <= 2 (Lemma B gives b independent h_y).
bk1b.py (impl 1) / bk2b.py (impl 2): BK + BK7. Survivor counts agree in all 24 cells (CHECKED; full lists cross-checked only at (5,3), bk2):
| b \ t | 1 | 2 | 3 | 4 | 5 | 6 | (max deficit of a survivor; #survivors) |
| 5 | closed | closed | 2 (4) | 2 (15) | 3 (38) | 3 (77) |
| 6 | closed | 1 (1: 5^7,0) | 4 (17) | 4 (69) | 5 (174) | 5 (364) |
| 7 | closed | 2 (2: 5^8,0/1) | 6 (37) | 6 (154) | 7 (403) | 7 (885) |
| 8 | closed | 3 (3: 5^9,0/1/2) | 8 (60) | 8 (251) | 10 (684) | 10 (1556) |
So **BX holds at (5,1),(5,2) and every (b,1)** (CHECKED; (b,1) also by WALL 8.3).
**Exact residue R-b (OPEN).** Every survivor has a λ-basis X0 = ρ smallest pieces with |U_X0| < 53 that fails both packings. The two shapes:
(α) t = 2, b >= 6: all pieces weight 7 plus one piece of weight <= 4 (X0 = {small, 7}). Needed lemma F7+P: for V 7-dim and a set P of <= 4 lines
   (a weight-<=4 piece: <= 8 lines, P ⊆ a 4-flat), the h with rank ℓ(Off(h) ∖ (Λ(V) ∪ P)) <= 7 span <= 5.
(β) t >= 3: weight-6 majority, X0 = {6,6,small...} (e.g. (5,3): [6^7,2], [7,6^6,2], [6^7,3], [6^6,5,4]). Needed lemma S66+P: for V1,V2 6-dim and P a
   common set of <= 2 (resp. <= 4) lines, the h with rank ℓ(Off(h) ∖ X) <= w_y (w_y = 6 for the weight-6 non-basis pieces) span <= b − 1.
   Both are kill46-shaped finite computations (orbit reps of V1 + all V2 + P), not attempted here (S66 mode t took 7 min in C; +2 lines ~ x50).

## §2 R-dep, exactly (PROVEN algebra)
cost_k = ρ(R_k,A_k) = rank of Ω on U_{R_k} × U_{A_k} = w(A_k) − dim(U_{A_k} ∩ Z_{R_k}) (rank of a bilinear pairing is symmetric), so
**ε^row_k = w(A_k) − cost_k** exactly. The R-dep condition "for every k0 ∈ J: Σ_{k≠k0} ε^row_k >= cost_k0 + 1" becomes
Σ_J ε − (w_k0 − cost_k0) >= cost_k0 + 1 ⇔ **Σ_{k∈J} ε^row_k >= w(A_k0) + 1 for all k0 ⇔ Σ_J ε^row_k >= max_J w(A_k) + 1.**
(The "every k0" quantifier collapses to the heaviest column.) With ε^row_k <= min(w(A_k), 9 − w(R_k)):
rows of weight 9 give 0, weight 8 give <= 1 (Z_R = <z>, corrected iff z ∈ U_A), weight 7 <= 2.
s = 1 (J = J_P ⊆ Lo_Q): row-side WALL Lemma 8.2 (transposed; PROVEN there from kpr15 CHECKED cover facts) gives two cases:
 (i) no row of weight <= 6: Σ ε <= 2 n_7 + n_8^corr with all weight-7 rows on one frame line ⇒ **#corrected rows >= ⌈(w_max+1)/2⌉**;
 (ii) exactly one row k1 of weight r <= 6 (the only low row), the rest weight >= 8: **n_8^corr >= w_max + 1 − min(w_{k1}, 9 − r)**.
Exact residue (OPEN): a low column circuit J at tight m meeting (i) or (ii) together with the cost-63 budget (N2). Not closed: the
circuit structure of the columns (A_k0 ⊆ ∪_{k≠k0} A_k) carries no codeword, so the cover tables bite only on the row side (pair lemma).
For s >= 2 the transposed Lemma 8.2 is not available (rows of J_P are a coset of an s-dim outside space): residue stated only via the boxed condition.

## §3 CONJ-G residue (exact restatement; not closed)
D′: one-sided, 8+t terms (t = 2,3), corrected cost 64, n_c >= 4 (>= 3 unconditionally), so raw/ε-free cost Σw = 64 + n_c >= 67.
(a) #2816 uniqueness (Theorem U) is about ε-free cost 64 (δ = 0); D′ has ε-free cost >= 67, outside its scope: it gives nothing.
(b) #3074 padding sends D′ to a one-sided P120 decoder of cost exactly 64 + 8 = 72 = the L120 floor (equality case). L120 is not
   unique at 72: the padded k = 4 root-swap family (t = 4) also attains it. So padding + uniqueness cannot kill D′ unless the L120
   equality case is classified; that classification (for 16 + t <= 19 terms) is the exact open statement.
(c) Branch d = 0, x = 0, m_T = 0 and no D7-type weight-8 member (|supp T| <= 4 suffices; SIX §7(b)) (NOT forced by peeling here, since slack = n_c >= 3): Δ_D = n_c gives cost_w(T) + c_9 = n_c <= |R| + c_9',
   so |R| >= cost_w(T); the (k,g) mechanism of CONJ-G (A)/(B) yields a further swap line v ∉ R, so |R ∪ {v}| > cost_w(T), contradicting the
   Swap Conjecture (SIX §7: #swap lines <= cost_w(T); PROVEN for κ <= 3, dim T = 1, or A nonsingular). This only re-derives CONJ-G's remark.
   Open branches, exactly: m_T >= 1 (carriers in T), x >= 1, a D7-type weight-8 member, or d >= 1 with cost(T) − 8d + 8x + c_8 <= n_c (DP: d <= 5 ⇒ cost(T) − 8d >= 2).
