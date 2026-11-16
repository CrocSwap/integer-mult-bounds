# CARRIER — the 18 d ∈ {1,2,3} T-level residues of L120 §6, the §3 audit item, and the §4 sliver
Labels: PROVEN (hand) · PROVEN-pa (hand, uses an unaudited card lemma) · CHECKED (exact script here; impl count given) · OPEN.
W = ~/repo_clones/intmult-work, python = W/venv/bin/python, scripts in W/cards/CARRIER (lib.py, cov.py, cov2.py, e8cov.py, e8cov6.py, e8extra.py,
pairs771.py, cell771.py, cell771b.py, sym771.py, ctrl771.py, t_rref.py, t_cov.py). Inputs: L120/THEORY, DUAL, DUAL7X, SIX, OS-CHARGE2, land7.out.

## STATE
- 23:21 CARRIER: started; read L120/DUAL/DUAL7X/SIX/OS-CHARGE2/land7.
- 23:36 CARRIER: Circuit Lemma (§2) found: replaces "carriers" for d ≥ 1; P112 covering (7,6)+≤3 lines impossible (2 impls) ⇒ 6 multisets dead universally.
- 23:40 CARRIER: E8-level: Off_E(root) = 57 lines; (7,7) uncoverable (= cell2 r_7 = 0, independent geometric reproduction); Root-swap lemma (§3 G4);
  root counting (§3 G2) ⇒ 13 of the 14 s = 7 multisets dead; [7,7,1] left.
- 23:50 CARRIER: [7,7,1] cell is RIGID: 127 covering pairs, q = p_r·1_Λa, S_{≤8} = T, cost 78 (2 impls). All 18 closed modulo the scenario analysis of §1.
- 23:55 CARRIER: audit item (|A|=4, q_3 drops, m=7) closed trivially (cost ≥ 64+κ+D). §4 sliver (Z ≠ 0): closed for the 18 cells and for κ = 7; open for d = 0, κ ≤ 6.

## §0 Result in one table (every row: cost_w(S) ≥ 72 for every S ⊇ 𝒞(E8) whose P112 restriction has this T-cell)
Cell = (d, min-basis multiset M of T=(ρS)_{≤7}), s = cost(M) − 8d. "univ" = pure P112 T-level kill, valid in every scenario; "ClassI" = E8-level argument in the
(forced) scenario of §1; the s = 6 rows also need the scenario sub-cases of §1.4.
| # | d | s | M | status | argument |
|---|---|---|---|---|---|
| 1 | 1 | 6 | [7,7] | CHECKED | z = 0 ⇒ dim S = 9 ⇒ L120 cell2 (all 9-dim S ≥ 72); also ClassI: (7,7) uncoverable (G3). z = 1 ⇒ §1.3 ⇒ [7,7,1] cell (G5) |
| 2 | 1 | 7 | [7,6,1,1] | CHECKED (2 impls) | univ: Circuit Lemma K=∅, (7,6)+2 lines uncoverable (G6) |
| 3 | 1 | 7 | [7,6,2] | CHECKED (2 impls) | univ: same |
| 4 | 1 | 7 | [7,7,1] | CHECKED (2 impls) | ClassI: rigid root-swap cell, cost 78 (G5) |
| 5 | 2 | 6 | [7,7,6,1,1] | CHECKED (2 impls) | univ: K = {a 7}, complement {7,6,1,1}, (7,6)+2 uncoverable |
| 6 | 2 | 6 | [7,7,6,2] | CHECKED (2 impls) | univ: K = {a 7}, complement {7,6,2}, (7,6)+2 |
| 7 | 2 | 6 | [7,7,7,1] | CHECKED | ClassI root-swap pigeonhole (3 roots, 1 line) + sub-cases §1.4 (all closed) |
| 8 | 2 | 7 | [7,7,6,1,1,1] | CHECKED (cov2 P112 + e8cov E8) | univ: (7,6)+3 lines |
| 9 | 2 | 7 | [7,7,6,2,1] | CHECKED (cov2 P112 + e8cov E8) | univ: (7,6)+3 lines |
| 10 | 2 | 7 | [7,7,6,3] | CHECKED | ClassI: (7,6,3-flat) uncoverable (E8) |
| 11 | 2 | 7 | [7,7,7,1,1] | CHECKED | ClassI: root-swap pigeonhole (3 roots, 2 lines) |
| 12 | 2 | 7 | [7,7,7,2] | CHECKED | ClassI: same (2-piece has ≤ 2 lines) |
| 13 | 3 | 7 | [6^5,1] | CHECKED+PROVEN | ClassI: root counting, 10 roots in a 3-dim space (G2) |
| 14 | 3 | 7 | [7,6^4] | CHECKED+PROVEN | ClassI: root counting, 10 roots in a 3-dim space |
| 15 | 3 | 7 | [7,7,7,5,4,1] | CHECKED | ClassI: K = {7,7}, complement (7,5,4)+1 uncoverable |
| 16 | 3 | 7 | [7,7,7,5,5] | CHECKED | ClassI: (7,5,5) uncoverable |
| 17 | 3 | 7 | [7,7,7,6,3,1] | CHECKED | ClassI: (7,6,3)+1 uncoverable |
| 18 | 3 | 7 | [7,7,7,6,4] | CHECKED | ClassI: (7,6,4) uncoverable |
Net: **all 18 closed** (CHECKED; single implementation for the E8-level coverings, whose tooling was validated against brute force and against cell2/DUAL data; two
implementations for the P112 coverings and for the [7,7,1] cell). Open items elsewhere: d = 0, Z ≠ 0, κ ≤ 6 (§5), and d ≥ 4 (not this card).

## §1 Accounting (PROVEN-pa: L120 §1 reduction + OS-CHARGE2 §2 identity)
Setting: S ⊇ 𝒞(E8), B a min-weight basis of S (E8 weights = label-span dimension), ρ = restriction to P112, F = ρB (spanning ρS), drop(b) = w(b) − w(ρb),
D = Σ drop, Δ = Σ_F w − 64, so **cost_w(S) = 64 + Δ + D** (zero ρb count 0). z := dim(ker ρ ∩ S), T = (ρS)_{≤7}, κ = cost(T), d = dim(T ∩ 𝒞_{112}),
s = κ − 8d, x := dim ρS − dim(T + 𝒞) ≥ 0, cost_w(ρS) = 64 + s + 8x + c_8 (L120 §1; c_8 ≥ 0 = excess of the non-T min-basis members over 8).
A violation is cost_w(S) ≤ 71. We only need cells with s ≤ 7; here s ∈ {6, 7}.

**1.1 Z-lemma (PROVEN).** cost_w(S) ≥ cost_w(ρS) + z.
*Proof.* B_0 := {b ∈ B : ρb = 0} (|B_0| = z_0, each drop = w(b) ≥ 1), B_1 := B ∖ B_0. ρB_1 spans ρS and has |B_1| = dim ρS + (z − z_0) members, so contains
a basis plus z − z_0 surplus members, each of weight ≥ 1: Σ_{B_1} w(ρb) ≥ cost_w(ρS) + (z − z_0); Σ_{B_0} w(b) ≥ z_0; w(b) ≥ w(ρb). ∎
Equality forces: every surplus member has weight 1, every B_0-member has weight 1, all drop sits in B_0.

**1.2 Σ_F w ≥ cost_w(ρS) ⇒ Δ ≥ s + 8x + c_8** (F spans ρS).

**1.3 Scenarios.** 8x + c_8 + z ≤ 7 − s from 1.1 and cost ≤ 71.
- **s = 7:** x = c_8 = z = 0, Δ = 7, D = 0, Σ_F w = 71 = cost_w(ρS) ⇒ F is a min-weight basis of ρS; the members of F of weight ≤ 7 form a min basis of T
  (matroid greedy). **So the pieces of M are basis members b of S with drop 0: ClassI.**
- **s = 6:** x = 0, c_8 + z ≤ 1.
  * (α) z = 1 (c_8 = 0, cost = 71, equality in 1.1): z_1 = 1, z_0 = 0 is impossible (the circuit J of F ⊆ B_1 must have all weights 1: ρb_j ∝ δ_t with the same t,
    b_j no-drop of weight 1 ⇒ b_j ∝ δ_t exactly (no frame line lies in ⟨ℓ_t⟩), contradicting independence of B). So z_0 = 1, B_0 = {δ_f} for a frame line f,
    F = ρ(B ∖ δ_f) is a min basis of ρS, Δ = 6, D = 1, all other members no-drop.
  * (β) z = 0, c_8 ∈ {0,1}, Δ ≥ 6 + c_8, Δ + D ≤ 7:
    (β1) Δ = 6, D = 0; (β2) Δ = 6, D = 1; (β3) Δ = 7, D = 0. Writing f = |F_T|: Σ_F = 64 + s + Σ_{i>f}(8 − w_(i)) + (excess) with w_(i) the sorted pieces,
    so besides "F_T ⊇ a min basis of T" there are exactly: (β3-i) F_T a basis of T with total κ + 1; (β3-B) f = a − 1, one weight-7 piece missing, non-T members all weight 8.

## §2 Circuit Lemma (PROVEN)
Let y_1..y_a (a = d + e) be a min basis of T (weights w_j, supports ⊆ Λ(F_j), dim F_j = w_j, Λ(V) := lines whose label lies in V), R := {c ∈ K^a : Σ c_j y_j ∈ 𝒞},
dim R = d (y independent). h(c) ∈ K^8 defined by Σ c_j y_j = p_{h(c)}|_{P112}; c ↦ h(c) is injective linear.
**Lemma.** For every K ⊆ [a], |K| ≤ d − 1: dim{c ∈ R : c|_K = 0} ≥ d − |K| ≥ 1. Each such c ≠ 0 gives Off(h(c)) ⊆ ∪_{j ∈ supp c} supp y_j ⊆ ∪_{j ∉ K} Λ(F_j), with
|Off(h)| ≥ 53 (OS-CHARGE §9) and the P112 direction list ≤ 80 (SIX §3: roots 53, frame 56, then 70/73/76/77/…). ∎
This is a T-level statement (no lift needed). It replaces DUAL's carriers when d ≥ 1: instead of bounding swaps by rank ℓ(supp T) ≤ κ (useless: rank ≤ 9 once T
contains a codeword) it bounds the *codewords inside T*, which must be covered by few flats.

**E8 version (ClassI).** If the pieces are basis members of S with drop 0 and z = 0 (ClassI, §1.3 s = 7, and the pieces of the s = 6 sub-cases below), the lifts y_j^E ∈ S have E8 supports
⊆ Λ_E(F_j) (frame lines included; drop 0 ⇒ every z_i with nonzero frame value is in F_j), Σ c_j y_j^E = p_h^E exactly, so **Off_E(h) ⊆ ∪_{j ∈ supp c} Λ_E(F_j)**.
(z = 1: add the extra line f.)

## §3 Geometric facts
**G1 (PROVEN, classical).** For h ≠ 0, lines ⊥ h form a closed root subsystem of rank ≤ 7: ≤ 63 lines (E7, iff h ∥ a root), next D7 with 42. Hence |Off_E(h)| = 57 iff h is
a root direction, else ≥ 78. Every cap Σ_J g(w_j) ≤ 77 therefore forces a *root* (g(1..7) = 1,2,4,8,12,20,36). W(E8) is transitive on roots and acts linearly on labels (1, r̄ ∈ E8/2E8),
so one root r0 suffices. Frame check (lib.py): 8 orthogonal lines, z-rank 4, 14 four-sets sum to 0, |Off_{P112}| = 53 (112 roots), 56 (frame) — matches SIX.
**G2 (PROVEN).** A d-dim subspace of K^8 contains ≤ 1, 3, 6 root lines for d = 1, 2, 3 (A1, A2, A3). Not "10".
**G3 (CHECKED, e8cov.py, e8cov6.py).** Off_E(r0) (57 lines) covered by a 7-flat ∪ rest:
(7,7): **no** (all 590 candidate first flats fail; this is exactly L120 cell2's "r_7 = 0": no two vectors of E8-weight ≤ 7 differ by a codeword — reproduced geometrically);
(7,7)+1, (7,7)+2: yes; (7,6)+k lines, k ≤ 4: **no** (no 7-flat covers ≥ 57 − 20 − k lines); (7,5,4)+1: no; (7,5,5): no; (7,6,3)+1: no; (7,6,3-flat): no; (7,6,4): no;
(6,6,6)(+1): yes (so [6^5,1], [7,6^4] need G2, not covering).
**G4 Root-swap lemma (CHECKED, e8extra.py + sym771.py).** If Off_E(r) ⊆ Λ_E(V_a) ∪ Λ_E(V_b) ∪ E with dim V_a = dim V_b = 7 and |E| ≤ 2 then **r ∈ E** (the only minimal
leftover set is {r}; all 1598 candidate V_a × all E of size ≤ 2 enumerated; re-run for roots 17, 77, 119: identical, 0 violations).
**G5 The [7,7,1] cell (CHECKED, 2 independent implementations).** The coverings of N(r0) = Off_E(r0) ∖ {r0} (56 lines) by two 7-flats: exactly **127 pairs**, all with
Λ_a ⊔ Λ_b = N(r0) (disjoint, sizes (28,28)×64, (24,32)×36, (32,24)×27, label ranks 7,7). Then y_1 ∝ p_r·1_{Λa}, y_2 ∝ p_r·1_{Λb}, unit at r: no free parameters.
S = 𝒞 + ⟨q, δ_r⟩ (dim 10). cell771.py: for each hyperplane φ, W_φ = {(g,c) : ⟨ℓ,g⟩ + c q(ℓ) = 0 on O_φ∖{r}}, V = ⟨r⟩ + Σ π_g(W_φ): **dim V = 1 in all 127** (controls in ctrl771.py:
q = 0 → 1, q = δ_u → 2). cell771b.py (explicit 120-coordinate S, V8 = Σ_φ {v ∈ S : v|_{O_φ} = 0}): **dim V8 = 3 = dim T in all 127**. Hence S_{≤8} = T, all other 7 dims have weight 9:
**cost = 1 + 7 + 7 + 7·9 = 78 ≥ 72.** (If S had extra weight ≤ 7 vectors they would show up in V8; none.)
**G6 (CHECKED, cover.py [rank/removal loops] and cov2.py [numpy masks + DFS], agree).** P112 Off sets of roots (53) and frame (56) are not covered by a 7-flat ∪ a 6-flat ∪ ≤ 2 (cov2: ≤ 3) lines.
Tooling validated: t_rref.py (rank/canonical basis/removal-cover vs brute force, 3000 cases), t_cov.py (multi-flat DFS vs brute force, 300 cases).

## §4 The 18, one by one
Throughout: "pigeonhole" = §2 (E8 version) gives, for each 7-piece X, an element c_X ∈ R vanishing on X; its support lies in the two other 7-pieces plus the small pieces
(units / the 2-piece), cap ≤ 74 < 78, so h(c_X) is a root; the 7-flats are two, E = small-piece lines (|E| ≤ 2), so by G4 **the root line of h(c_X) is a line of a small piece**.
The c_X are pairwise non-proportional (a coincidence would vanish on ≥ 2 sevens, support ⊆ {7, small}, cap ≤ 38 < 57), so the three roots are distinct lines.
- **#2, #3** [7,6,1,1], [7,6,2]: R is 1-dim; support ⊆ all pieces; complement = all = (7,6)+2 lines: uncoverable (G6, P112; also G3, E8). Dead in every scenario.
- **#5, #6** [7,7,6,1,1], [7,7,6,2] (s = 6): K = one 7 ⇒ c ≠ 0 with support in {7,6,1,1} / {7,6,2}; (7,6)+2 uncoverable (G6). Dead in every scenario (pure T-level).
- **#8, #9** [7,7,6,1,1,1], [7,7,6,2,1]: K = one 7, complement {7,6}+3 lines: uncoverable (G6 with 3). Dead in every scenario. **#10** [7,7,6,3]: complement {7,6,3-flat} (E8, G3). ClassI forced.
- **#15–#18** (d = 3, K = the two largest): complements (7,5,4)+1, (7,5,5), (7,6,3)+1, (7,6,4): uncoverable (G3). ClassI forced (s = 7).
- **#13, #14** [6^5,1], [7,6^4] (d = 3): for every pair K of pieces (of the five 6's, resp. {7} ∪ 6's) the element vanishing on K has support ⊆ the remaining 3 (+ unit), cap ≤ 62 < 78 ⇒ root;
  two different pairs cannot give the same element (it would vanish on ≥ 3 pieces, support in ≤ 2 pieces, cap ≤ 56 < 57 = min |Off_E|). That is **10 distinct root lines in the 3-dim space h(R)**; G2 allows 6. Contradiction.
- **#11, #12** [7,7,7,1,1], [7,7,7,2]: pigeonhole: 3 distinct roots whose own lines lie in the ≤ 2 small-piece lines. Contradiction.
- **#4** [7,7,1] (s = 7, ClassI, d = 1): single circuit {7,7,1}; G1 ⇒ root; G4 ⇒ unit at r; G5 ⇒ one of 127 rigid cells, cost 78. Contradiction with cost ≤ 71.
- **#7** [7,7,7,1] (s = 6): scenarios of §1.3: (β1) ClassI: pigeonhole with 1 small line (3 roots, 1 line). (β2) Δ = 6, D = 1, F min basis, one member b* drops:
  b* non-T ⇒ all pieces non-dropping ⇒ same pigeonhole; b* = the unit (E8 support {t, f_i}, |E| ≤ 2) ⇒ pigeonhole with 2 lines (3 roots, 2 lines); b* = a 7-piece A (E8 weight 8): the element
  vanishing on A is a circuit {B, C, δ} of non-dropping members ⇒ root-swap cell G5, and S = 𝒞 + ⟨B, δ⟩ (dim 10 = 8 + e) ⇒ cost 78.
  (β3) Δ = 7, D = 0: c_8 = 1 or non-T member of weight 9: pieces are members, pigeonhole; (β3-i) F_T = {u_2, y_1, y_2, y_3} (weights 2,7,7,7: forced, matroid domination): the K = {7-member} complements
  are {2,7,7} with E ⊆ supp u_2 (≤ 2 lines): pigeonhole; (β3-B) one 7 missing: F_T = {7,7,1}, T' = span F_T has T' ∩ 𝒞 ≥ 1 ⇒ circuit among them ⇒ G5, and dim S = 10 = dim(𝒞 + T') ⇒ cost 78.
  (α) z = 1, δ_f ∈ S: pieces are members, E = {t, f}: pigeonhole with 2 lines. All closed.
- **#1** [7,7] (s = 6): z = 0 ⇒ dim S = 8 + e = 9, and L120 cell2 (CHECKED: **every** 9-dim S ⊇ 𝒞(E8) has cost_w ≥ 72, any scenario) applies. (Independently in ClassI: (7,7) uncoverable, G3.)
  z = 1 ⇒ (α): δ_f ∈ S, F min basis, pieces members, circuit y_1 − c y_2 − p_h = k δ_f ⇒ Off_E(h) ⊆ Λ_a ∪ Λ_b ∪ {f}: root with line f (G1, G4); S = 𝒞 + ⟨q, δ_f⟩ ⇒ G5, cost 78.

## §5 L120 §3 audit item and L120 §4 sliver
**(a) Audit item (|A| = 4, q_3 drops, π(q_4) ≠ 0, m = 7) — CLOSED (PROVEN).** m = 7 forces κ = 7 ([4,3]). In the d = 0 cell cost_w(S) = 64 + Δ + D with Δ ≥ σ + c9 ≥ κ (D0.1: otherwise Δ ≥ 8).
A dropping piece gives D ≥ 1, so cost ≥ 64 + 7 + 1 = 72. More generally **in the d = 0 cell with κ = 7 no piece can drop and no member can drop at all** (D = 0 is forced), and with κ ≤ 6 only D ≤ 7 − κ is possible;
the §4 refined bookkeeping needs P2 only for pieces that cannot drop. So the whole of L120 §4's "Caveat (honest)" reduces to κ ≤ 6 cases, and the named audit sub-case is vacuous.
**(b) Z = ker ρ ∩ S ≠ 0.** §1.1 gives cost ≥ cost_w(ρS) + z = 64 + κ + c_8 + z for d = 0. Hence: **κ = 7, any z ≥ 1: cost ≥ 72 (CLOSED, PROVEN).** For the 18 d ≥ 1 cells: CLOSED (§1.3, (α)).
For d = 0, κ ≤ 6, 1 ≤ z ≤ 7 − κ: **OPEN** (reduced to κ + z ≤ 7). What remains is DUAL's carrier bound m_8 + dim π(no-drop pieces) ≤ κ with frame consistency P2 only modulo π(Z); sufficient: it holds with P2 replaced by
"mod the ≤ z-dimensional space π(Z)|…" — not written. Equality analysis of 1.1 at cost 71: Z contains frame-only units δ_f; then S = S⁰ ⊕ ⟨δ_f⟩ and the problem is the |I| = 7 lift statement on 119 lines.

## §6 What is and is not claimed
- Closed: the 18 d ≤ 3 residues of L120 §6 (modulo §1's PROVEN-pa accounting and the single-implementation E8 coverings G3/G4, whose tooling is validated and which reproduce cell2's r_7 = 0).
- The method (Circuit Lemma + E8 root geometry) is much stronger than Basis-kill for small d: it kills a cell as soon as the *codewords inside T* cannot be covered. It likely extends to d ≥ 4 (more circuits ⇒ more
  roots to place in a d-dim space: N_4 = 12, N_5 = 20, N_6 = 36, but the number of forced roots grows like C(a, d−1)). Not done here.
- Not touched: d ≥ 4 residues (603 multisets), E8-native d_E ≥ 4, the d = 0 Z ≠ 0 sliver for κ ≤ 6.
- Caveats: (i) G3/G4 single implementation (tools validated; cross-checked by cell2 for (7,7) and by root symmetry); (ii) G5 two implementations; (iii) §1.3 uses the L120 §1 peeling identity cost_w(ρS) = 64 + s + 8x + c_8
  as stated there (PROVEN-pa); (iv) E8 W-transitivity/label-equivariance used for "one root suffices" (classical; checked on roots 17, 77, 119).

## §7 Lead for d ≥ 4 (NOT proven here; scan scripts scan2.py, scan3.py on the dominate.py LEFT list)
For the 603 d ≥ 4 residues: s = 7 rows are ClassI-forced (§1.3). Pure cap/root-count bookkeeping (no covering runs, no scenario analysis) already shows, among the s = 7 rows of the 621 list:
35 have a (d−1)-subset K whose complement cap < 57 = min |Off_E| (immediate kill), and 27 more have more injective root-circuits than N_d (greedy count > 12/20/36 for d = 4/5/6). The s ≤ 6 rows need the §1.3-style
scenario enumeration (D ≥ 1 sub-cases) plus the universal P112 form of the Circuit Lemma (caps vs |Off| ≥ 53). The G3/G4-type covering runs (cheap: one root, 43181 7-flat masks) have not been run for d ≥ 4.
