# TWINSWAP — constructive two-sided root swaps (Oct 15, evening)
Labels: PROVEN · CHECKED (exact script here, Fractions/sympy, seconds) · OPEN. python = W/venv/bin/python. Scripts: lib.py swapfam.py dbl.py.
Model as WALL: N₀ = G/2 = C′C′ᵀ (C′ = FC/2), Bd[t,s] = [t = s or t ⊥ s], cost = Σ_k rank_F2 Bd[supp p_k, supp q_k];
P = [C′ E]X̂, Q = [C′ F]Ŷ, X̂Ŷᵀ = diag(I₈, 0). lib.check verifies P Qᵀ = N₀ on ALL 112² entries (not only the mask).

## §0 Status
1. **Two-sided root-swap family (CHECKED swapfam.py, PROVEN ≥ 64 below).** Row swaps (j_a, r_a), column swaps (j_b, r_b), each with its OWN
   outside direction (E = δ_{r_a}, F = δ_{r_b}; s = k_r, t = k_c, m = 8 + k_r + k_c). Cost is EXACTLY 64 for every (k_r, k_c) with
   k_r, k_c ≤ 4 — e.g. (4,4): 8 non-full corrections (4 row, 4 column), m = 16, P Qᵀ = N₀ exactly, cost 64. No admissible configuration for k ≥ 5 on a side.
   **Answer to "shared excess paid once or twice": neither — nothing is shared.** Every correction (row or column) is paid by its own unit term
   (δ_r on its side, cost 1); the row and column swaps never touch the same inside rank-one term (forced, §1(c)).
2. **Double swap on one rank-one term (CHECKED dbl.py, PROVEN).** x = c_r, y ∝ c_{r′} (r, r′ non-orthogonal): block cost 7 + 1 + 1 = 9, and it kills
   the frame side of ≥ 1 other slot (indices in supp r ∩ supp r′ are unusable): cost ≥ 66 (attained 66).
3. **Disjoint (1,1), m = 10: independently re-derived RESIDUE's closure** (dual-basis normal form §2 below = RESIDUE R2/R3). Agreement, no new input.
4. **(1,1), m = 10 universal normal form (PROVEN, §2):** for ANY a ∈ J_Q, a′ ∈ J_P, a ≠ a′ (disjoint or not), after the shears μ ← q_a/y2_a,
   λ ← p_{a′}/x2_{a′} the other 8 terms are a dual-basis pair (x_k)·(y_k)ᵀ summing to I₈. The whole (1,1) m = 10 class is parametrised by
   (dual basis X, x2, y2 ∈ K⁸, one scalar, λ, μ ∈ K^L).
5. **Single-entry regime closed (§3):** if p_{a′} and q_a are single-entry (λ = δ_u, μ = δ_v), cost ≥ 64. PROVEN for disjoint; PROVEN-with-§6(ii) for non-disjoint (audit fix).

## §1 The two-sided swap family — tightness family: CHECKED + PROVEN within the root-swap family (not a general lower bound)
Inside rank-one terms: row swap a: (x, y) = (c_{r_a}, e_{j_a}/c_{r_a}[j_a]); column swap b: (e_{j_b}, c_{r_b}/c_{r_b}[j_b]); frame terms (e_i, ·) or (·, e_i).
They must be a dual-basis pair (Σ x yᵀ = I₈, 8 terms). Each swap splits into two decoder terms:
row swap: (p′ = C′c_r − 2δ_r, C′y) [cost 7: U_R = W_r, Z_A = ⟨z_j⟩ ⊂ W_r] + (2δ_r, C′y) [cost 1]; column swap dually.
(a) Duality conditions: c_{r_a}[j_{a′}] = 0 (a′ ≠ a); c_{r_b}[j_{b′}] = 0 (b′ ≠ b); ⟨c_{r_a}, c_{r_b}⟩ = 0 (every row root ⊥ every column root).
(b) Frame slot i ∉ J_r ∪ J_c can be x-frame iff i ∉ ∪ supp c_{r_b}, y-frame iff i ∉ ∪ supp c_{r_a}; a slot with neither costs 9.
(c) **J_r ∩ J_c = ∅ is forced:** a row swap and a column swap at the same j would need ⟨e_j, e_j⟩ = 0 (x_b vs y_a). The only way to put both
    corrections on one rank-one term is the double swap (§0.2), which costs ≥ 2 more.
(d) **Cost identity (PROVEN):** cost = Σ over the 8 inside rank-one blocks of block cost; a swap block costs ≥ 7 + 1 = 8 (rank on W_r × W_j ≥ 7,
    unit term ≥ 1 since Off(y) ⊄ Off(r) ∖ r), a frame block 8, a non-frame block 9. Hence cost = 64 + #(bad slots) + #(ineligible swaps) ≥ 64.
CHECKED (swapfam.py, exact, P Qᵀ = N₀ on all entries): min cost 64 attained for all (k_r, k_c) ∈ {0..4}², k_r + k_c ≥ 1; none for k ≥ 5 on a side.
**Lesson for PAYS/DUAL:** a two-sided proof must be exact on n_nf up to 8 (k_r = k_c = 4, m = 16): each non-full correction is paid by one unit term
on the SAME side; the one-sided projection of the (4,4) decoder has excess 8·4 per side, and Σ ε^row = Σ ε^col = 4·8 = 32 (p′: 1, δ: 7 each).

## §2 Universal (1,1), m = 10 normal form (PROVEN)
X̂, Ŷ ∈ K^{9×10}, X̂Ŷᵀ = diag(I₈, 0). Pick a ∈ J_Q, a′ ∈ J_P, a ≠ a′ (|J_P| ≥ 3). Shear μ ← μ + C′y_a/y2_a (Ŷ ← [[I, −y_a/y2_a],[0,1]]Ŷ keeps
X̂Ŷᵀ) so y_a = 0, and λ likewise so x_{a′} = 0. Then terms a, a′ contribute 0 to the inside block, so the other 8 satisfy Σ x_k y_kᵀ = I₈:
**dual bases.** Normalise y2_a = x2_{a′} = 1. Then x_a = −Σ_8 y2_k x_k, y_{a′} = −Σ_8 x2_k y_k, x2_a = −y2_{a′} − Σ_8 x2_k y2_k, and every choice
of (X invertible, x2, y2 ∈ K⁸, y2_{a′}, λ, μ) is a decoder. Consequences:
- ⟨x_a, y_l⟩ = −y2_l, ⟨x_l, y_{a′}⟩ = −x2_l for the 8 dual terms l (RESIDUE R3 in one line).
- Frame indices: J_Q-only terms with frame rows and J_P-only terms with frame columns use pairwise distinct indices (⟨f_j, f_i⟩ = δ).
(Disjoint closure = RESIDUE §Result; re-derived independently here with the same Ω step: swap lines ⊂ U_A ∩ W_{j0}, dim w − 1.)

## §3 Single-entry regime (PROVEN for disjoint; PROVEN-with-§6(ii) for non-disjoint)
If p_{a′} = λ = δ_u and q_a = μ = δ_v (after the shears): every dual term has R ⊇ Off(x_k) ∖ {u}, A ⊇ Off(y_k) ∖ {v}, so w(R), w(A) ≥ 8 and cost_k ≥ 7,
with 7 only if U_R ∈ {W_j (x ∝ f_j), W_u (x ∝ c_u, cancelled at u)} and U_A ∈ {W_i, W_v} with a correction (frame–frame never: β(z_i,z_j) = 1).
x_k ∝ c_u for at most one dual term (X is a basis), likewise y_k ∝ c_v: **≤ 2 dual terms cost 7**, so cost ≥ 1 + 1 + 2·7 + 6·8 = 64.
Audit fix (cost_a or cost_{a′} = 0 is possible). If x_a = 0, the circuit gives Σ_8 y2_k x_k = 0 with independent x_k, so y2 = 0 on the dual terms ⇒ |J_Q| ≤ 2 ⇒ closed by WALL Cor 5.2 (dually for a′).
Residue: x_a ∝ c_u cancelled at u with u = v (so a ∈ K, cost_a = 0 on Bd[u-cancelled row, {v}]), or its dual. This is a's row being a row swap at u, which is case §6(ii) (second bullet): u leaves the dual row-swap slots, so the count is unchanged and the bound ≥ 64 stands.

Scope note (task 1 mixed catalogue): frame-type outside corrections were not combined with swaps: at t = 1 frame-type columns have s_k = 1 (excess 0, WALL §8),
and in the δ-direction family they only re-route which frame slot is used; they cannot lower cost below the §1(d) block bound. Not built, deliberately.

## §4 Run log
- swapfam.py: (0,k) k ≤ 4 reproduces SMALL2 (64; none at 5). Two-sided: 64 for all (k_r,k_c) ≤ (4,4). First run had a sign bug in the column
  cancellation (cost 65–68); fixed (cancel by −(C′y)(r_b)), all 64.
- dbl.py: double swap 66–68 (random slot assignment over 200 trials; 66 = proven bound 9 + 9 + 6·8).

## §5 PAYS's Swap-Conjecture danger family T = C′|_Y, Y a dense label 7-flat (CHECKED: flat7.py exact sympy; flat7p.py mod 2^61−1; orbits7.py)
Exact cost_w via matroid greedy: V_w = Σ_{flats F of M|Y, rank ≤ w} T_F (T_F = vectors of T supported on F), cost = Σ_w w·(dim V_w − dim V_{w−1}).
- 448 seven-flats have 36 lines (max); under the frame stabiliser (signed permutations of F0 coordinates preserving the 112 lines) they form ≤ 2 orbits
  (224 + 224, reps #0, #8). **Both reps: exact cost_w = 43 = 1 + 6·7 ≥ 36 (margin 7). Not a counterexample.**
- Sub-flats of rep #0 (subflat.py): rank 6 / 20 lines: cost ≥ 26 (margin 6); rank 5 / 12 lines: ≥ 16 (margin 4); rank 4 / 8 lines: 8 or 12
  (EQUALITY 8 = 8 occurs: T = K^F, unit vectors); rank ≤ 3: equality. Margins shrink with the flat; equality only in the trivial T = K^Y regime.
- OPEN: non-flat Y ⊂ 7-flat (deleting lines) not searched.

## §6 Non-disjoint (1,1), m = 10 with BOTH outside cosets low of deficiency ≥ 5 (D_P, D_Q ≥ 5): CLOSED — PROVEN (hand; audited, fixes applied)
Inputs: WALL Thm 6.1 (catalogue, |S| ≤ 11) + WALL 8.2 (d ≥ 4 ⇒ unique low) + RESIDUE d4.py (12-overlap sets have span 7, so at |S| = 12, w = 5 none) + §2 duality.
Scope is D_P, D_Q ≥ 5. Case (i) needs N₂ ≤ w_P + w_Q ≤ 8, i.e. D_P + D_Q ≥ 10. D = 4 is NOT covered.
Setting: §2 normal form, a := lowest column (d^A_a = D_Q ≥ 5, q_a = μ, A = supp μ, w_Q = 9 − D_Q), a′ := lowest row (D_P ≥ 5), any K.
Per term s_k = 9 − cost_k = d^A_k + dim(U_A ∩ Z_R) = d^R_k + dim(U_R ∩ Z_A), so s_k ≤ d^R_k + d^A_k and s_k ≤ 9 (s = 9 for a cost-0 term; there is no blanket s ≤ 8).
(i) a = a′: every other term has d^R, d^A ≤ 1 (WALL 8.2 per coset; K irrelevant), so s ≤ 2. s = 2 needs a swap side (as in (ii)), so at most N₂ ≤ w_P + w_Q ≤ 8 terms have s = 2 and the rest have s ≤ 1. Σ s ≤ 9 (a) + 9 (the other nine, ≤ 1 each baseline) + 8 (one extra unit per N₂ term) = 26.
(ii) a ≠ a′: Σ s ≤ (D_Q + c_a) + (D_P + c_{a′}) + 8 + N₂, c_a := dim(U_A ∩ Z_{R_a}) ≤ 1, N₂ = #dual terms with s = 2.
 s = 2 needs both sides deficient and Ω-compatible; frame/frame-type classes have β = 1, 12-overlap excluded (D ≥ 4), so each such term has a
 row swap (x ∝ c_u, u ∈ S_λ) or a column swap (y ∝ c_v, v ∈ S_μ); swap lines on one side are pairwise non-orthogonal ⇒ Ω-orthonormal in U_S ⇒
 N₂ ≤ w_P + w_Q, giving Σ s ≤ 26 + c_a + c_{a′}. Each extra unit is paid by a lost swap slot (duality ⟨x_a, y_l⟩ = −y2_l ≠ 0, §2, valid for any K):
 - Z_{R_a} = ⟨z_j⟩ (frame row, inside or frame-type coset row): all column-swap lines lie in W_j ∩ U_A (dim w_Q − 1) ⇒ ≤ w_Q − 1 col swaps.
 - Z_{R_a} = ⟨u_u⟩ (a's row is itself a row swap at u ∈ S_λ, a ∈ K): u is then not available to the dual row swaps ⇒ ≤ w_P − 1 row swaps.
 - both extras: the two losses are distinct; the only coincidence case (a′'s column a swap at v, a's row frame f_j) is excluded because
   {u_v} ∪ dual col-swap labels is Ω-orthonormal, the dual ones lie in W_j, z_j ∈ U_A ⇒ z_j ∈ ⟨u_v⟩, impossible (line labels ≠ frame labels).
 Hence Σ s ≤ 26 < 27: cost ≥ 64.
**OPEN (non-disjoint residue):** K ≠ ∅ and some side with D ≤ 4: D = 4 (|S| = 12), P2 (two weight-7 lows), or D ≤ 3 (support up to 20 lines, catalogue 6.1 no longer applies).
Same mechanism expected (N₂ terms need swap slots; low-term extras paid by Ω-orthonormal exchange) but not written.

## §6b Exact tightness witnesses IN the open class (CHECKED witness16.py; P Qᵀ = N₀ on all entries; Lemma-D normalised: no proportional p's/q's)
From the (1,1) swap member, give frame terms an outside component cancelling at the swap line (q_k = C′e_i·c + y2_k δ_{r′}, r′ ∈ Off(f_i): span stays W_i, cost 8),
re-solving the δ-term's inside part (x_δ = e_j − (y2_k/v)x_k; its cost stays 1).
- disjoint: |J_P| = |J_Q| = 3, cost 64, Σ(s − 1) = 16 (E_Q = E_P = 8). **So E_Q + E_P = 16 is attained: the disjoint closure has exactly one unit of margin.**
- shared: one frame term inflated on BOTH sides + x2 on the column-δ term to restore x2·y2 = 0: K = {2 terms}, |J_P| = 4, |J_Q| = 3, cost 64.
  Non-disjoint exactness data point: any proof of the K ≠ ∅ residue must be exact here.

## §7 Lemma candidate for PAYS (what every construction above obeys)
**Ω-orthonormal exchange.** In a decoder of N₀, call a correction *swap-type* at line v (class u_v). (a) Swap lines of one outside coset are pairwise
non-orthogonal, hence their labels are Ω-orthonormal (independent) inside the label span of the coset's low vector. (b) By duality of the inside
rank-one terms (§2 / §1(d)), every term that carries an *extra* correction (a frame or swap class lying in the span of a low support) forces all
partner swap lines into the corresponding Ω-orthogonal complement, removing one slot. So each correction is paid exactly once: by its unit term
(one-sided swap family, §1), or by a lost Ω-orthonormal slot (low-term extras, §6). Exact on: all (k_r,k_c) ≤ (4,4) families (cost 64, n_nf ≤ 8),
the disjoint (1,1) optimum (E_Q = E_P = 8), and the single-entry regime (§3). Must be stated RELATIVE to 𝒞 (PAYS §4: absolute coloop counting fails).
