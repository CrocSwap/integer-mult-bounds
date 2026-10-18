# Root-code floors T·r_min for exact root-unit decoders with the dense pairing (sharp on E8, P112, P104, E7, D4, D6), a dense polar law and a place bound (no κ claim)

> **What is claimed, and what is not.**
> **Claimed (PROVEN, proofs in this README).** (1) A *place bound* valid for every T and every prime above 2: cost ≥ |S_a| (Theorem 1), and the *tropical ceiling* |S_a| ≤ τ(M), which is ≤ T for Gram decoders M = D₁GD₂ on every even root unit (Proposition 2). Theorem 1's mechanism and Proposition 2's cycle condition are already contained in #2162 (Lemma CR2's 2-adic/tropical corollary, Lemma VCR2); see below. (2) A *dense polar law*: for an odd-or-zero unit the dense pairing B is a Gram matrix of vectors u_t = (1, ℓ_t) for a form Ω = 1 ⊕ b on F2 ⊕ F2^k, so every term costs at most k + 1 and the F2 rank of any block is an Ω-pairing rank (Theorem 3); this proves the upper bounds of the 8/7 rule of #968. (3) A *root-code floor*: for decoders whose two factors lie in the live root code, for the dense pairing, **with any number of terms**, cost ≥ T·r_min, and this is attained by an explicit decoder on E8 (72), P112 (64), P104 (56), **E7 (49)**, E7 minus a 7-frame (42), D4 (12), D6 (30) (Theorem 4). For D5 and E6 the pairwise floor (15, 30) is below v, and a coupling lemma shows that *square* root-code decoders cost ≥ 20 and ≥ 36 (= v).
> **Checked (exact, `verify.sh`).** Every number above, the label ranks, the E8 block-rank law, the P104 frame-pair decoder (rebuilt), the deficient-direction incidences of D5 and E6, the rank-44 witnesses, the 2-adic carry of the dense E8 blocks, the forced-minor bound ω_non.
> **Not claimed.** **No κ claim, no window closed, no new supplier.** Theorem 4 is a floor *in a class*: root-code factors, the **dense** pairing B (B_ts = 1 iff t = s or r_t ⊥ r_s), exact decoders over a field of characteristic 0. It does **not** bound the cost over sparser admissible B, over decoders whose factors leave the root code (cf. the 9-term example of #1180), or over non-Gram geometries; those gaps are listed as open questions in §6. Conjecture ID (§6) is a conjecture.

## 0. Reading this package

Statuses: **PROVEN** (written proof here, self-contained), **CHECKED** (recomputed by `verify.sh` with exact arithmetic), **CONJECTURE**, **OPEN**. Nothing is RECORDED-only: every number in the claims box is recomputed.

```sh
bash research/ideal-decoder-floors/verify.sh /fresh/output/dir     # from a checkout or `git archive`; Python >= 3.11, standard library only; single process, no SAT
```

Step 0 checks every file against `MANIFEST.sha256` and every pin of `SOURCES.json` and stops with exit 1 on mismatch; then six check scripts run one after the other (all arithmetic is `Fraction`/integer/F2-bit; no floating point except exact half-integer shift values in the c5 hill-climb, no randomness except a seeded hill-climb whose result is only used as a lower bound against a proven ceiling) and print one `PASS`/`FAIL` line per assertion.

**Prior work this builds on.**
- **#446, #595, #1590, #2111** (ours, closed / merged / merged / open): the cost model (Theorem C: a decoder is M = PQᵀ, a pairing B, cost Σ_j rank_F2 B[R_j, A_j]), exact decoders, Lemma A/B, ERR1 (dyadic E7 and E8 decoders at 49 and 72). This package does not repeat them.
- **#2125** (ours, open): the T² threshold and the table of costs of explicit pairings (E7 first gain found at 49 < 63). See §7 for the exact difference.
- **#620** (first P112 64 / P120 72 records), **#717** D1 and **#1212** (eight-term E-graph floors 64 / 72 / 56; #717 D1(b) is the P112 label-span census: 9 spans, minimum pairing rank 8, cost ≥ 64 for exactly 8 costly terms, of which Theorem 4's types are the general form), **#968** (8-term frame-pair decoders and the exact 8-term copy-cost floor 72 − p / 56 for punctures of E8), **#1077** (complex coefficients), **#1180** (overcomplete factor-linear decoders keep the floor *in the live root code*), **#1236** (root-star supports), **#1744** (rank ≥ 9 for any fitting B on P111/P112), **#1714** (P112 batch floor 64k in the block-root-code model): the E8/P112/P104 floors. Theorem 4 re-derives them from one argument and extends it to other units.
- **#2017** (sharp cost 40 for Eisenstein binary decoders) and **#798, #1977** (clique / submatrix-minrank certificates): the odd-geometry case; Theorem 1 is the same reduction-mod-2 idea in model C (#2017 works in its own bit model and reduces the normalised Hermitian Gram matrix to F4).
- **#2176** (forced triangular minors: the eleven-line `jf0` example costs exactly 19) and **#2162** (ours, open; jets, anti-Fano): the T = 3 side. #2162's Lemma CR2 2-adic/tropical corollary is the all-lines-survive case of Theorem 1 at T = 3, and its Lemma VCR2 is the cycle-dominance companion of Proposition 2; we do not claim novelty for that part. §5.4 uses the same *forced principal minor* tool on E8 and records that it reaches only 7 per co-flat term.
- **#1140** (sharp k8 factory register bound via incomparable support frames): the same kind of support-counting tool for a different object; not used here.
- **#2137** (E6 B0 coordinate-form decoders have at least five totals: the zero-pattern constraints on L have a one-dimensional kernel QG): the same fact as our `N`-space check for E6 (C1.E6-Nspace), obtained independently and **first** by #2137; its per-total floor w = 5 equals r_min(E6).

## 1. Setting and notation

A **unit** is a set of v lines t = 1..v spanned by vectors r_t ∈ Q^n with Gram matrix G (integers; for root units G_tt = 2, G_ts ∈ {0, ±1}). The span V has dimension T = rank G. The units used: D4, D5, D6, E6, E7, E8 (all roots up to sign; v = 12, 20, 30, 36, 63, 120; T = 4, 5, 6, 6, 7, 8), and punctures: **P112** = E8 minus an orthogonal 8-frame F0; **P104** = E8 minus two orthogonal 8-frames F0, F1 (see §4.3); **E7 − F** = E7 minus an orthogonal 7-frame.

A **decoder** with T' terms over a field K ⊇ Q is a pair P, Q ∈ K^{v×T'}; M = PQᵀ; p(t), q(t) are row t of P, Q; p_j, q_j columns; R_j = supp p_j, A_j = supp q_j. A **pairing** is B ∈ F2^{v×v} with B_tt = 1 and B_ts = 1 (t ≠ s) only where M_ts = 0 (**admissible**; B̃ is its 0/1 integer lift). The decoder is **exact** when M_tt ≠ 0 for all t (so B̃ ∘ M is the diagonal matrix of the M_tt). The **cost** of (P, Q, B) is Σ_j r_j with r_j = rank_F2 B[R_j, A_j] (the "Model C" of #446/#595/#1590; per-total floors of the form Σ_j max(w, r_j) only increase it, so every lower bound below holds for them a fortiori). The **dense pairing** of a unit is B_ts = 1 iff t = s or G_ts = 0; every admissible pairing of an exact Gram decoder lies inside it.

Identity used throughout (for any matrices X, Y with columns x_j, y_j and D(·) the diagonal matrix of a vector):  **B ∘ (XYᵀ) = Σ_j D(x_j) B D(y_j)** (entrywise (B ∘ XYᵀ)_ts = B_ts Σ_j x_j(t) y_j(s)).

## 2. Results at a glance

| # | statement | status | where |
|---|---|---|---|
| T1 | Place bound: for every number field K, every prime 𝔭 \| 2, every shift a: cost(B) ≥ \|S_a\| for every admissible B (all T) | **PROVEN** | §3.1 |
| P2 | Tropical ceiling \|S_a\| ≤ τ_𝔭(M); on every even root unit (M = D₁GD₂) \|S_a\| ≤ ω ≤ T | **PROVEN** | §3.2 |
| – | Tightness: frame bases attain s = ω = T (E8, E7, D4, D6); simple-root bases reach ω after a shift; coordinate / punctured bases have s(0) = 0 | **CHECKED** | §3.3 |
| – | No certificate of the form rank_Q(G∘C) over admissible coverage C (bit model) proves more than 44 on E8 (witness rank 44 against the floor 72); 2-adic carry 26 per dense E8 term, 208 in total | **CHECKED** | §3.4 |
| T3 | Dense polar law: B = Gram of u_t under Ω; r = dim U_R − dim(U_R ∩ U_A^⊥Ω) ≤ k + 1; cost ≤ T(k + 1) | **PROVEN** | §4 |
| – | Label ranks k = 2, 4, 4, 6, 6, 8; rank B = k + 1; E8 block ranks 9 / 8 / 8 / 7 (the 8/7 rule) on all 14,400 normal pairs | **CHECKED** | §4.2 |
| – | P104 frame-pair decoder rebuilt: exact on 104 lines, 8 terms of rank 7, cost 56 | **CHECKED** | §4.3 |
| T4 | Root-code floor: cost ≥ T·r_min with any number of terms (hypotheses in §5.1) | **PROVEN** | §5.1 |
| – | r_min and sharpness: E8 72, P112 64, P104 56, E7 49, E7 − F 42, D4 12, D6 30 (explicit decoders attain the floor) | **CHECKED** | §5.2 |
| L5 | Coupling lemma: square root-code decoders cost ≥ 20 on D5 and ≥ 36 on E6; N is forced ∝ Gram | **PROVEN** from CHECKED incidences | §5.3 |
| – | Forced minors give ω_non = 7 per co-flat E8 term (8 needed) | **CHECKED** | §5.4 |
| ID | Conjecture ID: cost* = min(v, T(k + 1) − usable deficiencies) for odd-or-zero units | **CONJECTURE** | §6 |
| – | non-dense B; factors outside the root code / non-Gram M; overcomplete coupling (E6 m = 7, D5 m ≥ 6); T = 3 | **OPEN** (questions) | §6 |

## 3. The place bound and its ceiling (every T)

### 3.1 Theorem 1 (place bound) — PROVEN

Let K be a number field containing the entries of P, Q; 𝔭 a prime of K above 2; ν the valuation of the completion K_𝔭 normalised by ν(2) = 1 (so ν(K_𝔭^×) = (1/e)Z, e the ramification index); O the valuation ring, k_𝔭 = O/𝔭 = F_{2^f}. For a ∈ ((1/e)Z)^{T'} put

  m_t(a) = min_j ( ν p_j(t) + a_j ),  n_t(a) = min_j ( ν q_j(t) − a_j ),

and call line t **a-surviving** if p(t)·q(t) ≠ 0 and ν(p(t)·q(t)) = m_t(a) + n_t(a) (no leading-term cancellation), **a-cancelling** otherwise (then ν(p(t)·q(t)) > m_t + n_t). Let S_a be the set of a-surviving lines. **Then for every admissible B, cost(B) ≥ |S_a|**; equivalently v − cost ≤ #(a-cancelling lines). The decoder need not be a Gram decoder; no hypothesis on T' is used.

*Proof.* Choose c_j ∈ K_𝔭^× with ν(c_j) = a_j (possible since a_j ∈ ν(K_𝔭^×)) and replace p_j ← c_j p_j, q_j ← c_j^{-1} q_j. Every product p(t)·q(s), hence M, every incidence and every support, is unchanged, and now m_t(0) = m_t(a), n_t(0) = n_t(a). Next scale row t of P by an element of valuation −m_t and row t of Q by one of valuation −n_t. This multiplies M on the left and on the right by invertible diagonal matrices, so supports, incidences and the admissibility of B are unchanged, and now every p(t), q(t) lies in O^{T'} and has an entry of valuation 0. Reduce modulo 𝔭: P̄, Q̄ ∈ k_𝔭^{v×T'} with supp p̄_j ⊆ R_j, supp q̄_j ⊆ A_j. If B_ts = 1 and t ≠ s then p(t)·q(s) = M_ts = 0 exactly, hence p̄(t)·q̄(s) = 0. Put N := B ∘ (P̄Q̄ᵀ), computed in k_𝔭 ⊇ F2. Then N is **diagonal**, and N_tt = p̄(t)·q̄(t) is the reduction of an element of O whose valuation is ν(p(t)·q(t)) − m_t − n_t ≥ 0; it is nonzero iff that valuation is 0, i.e. iff t ∈ S_a. So rank N = |S_a|. By the identity of §1, N = Σ_j D(p̄_j) B D(q̄_j), and rank_{k_𝔭} D(p̄_j) B D(q̄_j) ≤ rank_{k_𝔭} B[R_j, A_j] = rank_{F2} B[R_j, A_j] = r_j (rank of an F2 matrix does not change under field extension). Rank subadditivity gives |S_a| ≤ Σ_j r_j. ∎

**Corollaries (PROVEN).** (1) S_a depends on (P, Q, 𝔭, a) only, not on B. (2) *No cancellation anywhere ⇒ no gain.* If S_a is the set of all lines for some 𝔭 and a, then cost ≥ v. For the Eisenstein unit of 40 lines (K = Q(ω), 𝔭 = (2) inert, k_𝔭 = F4) #2017 proves cost ≥ 40 = v for every Eisenstein decoder by reducing the normalised Hermitian Gram matrix to F4 (tight by Lam's row-star); Corollary (2) is the Model-C analogue, conditional on survival. We do not re-derive that case here. The all-lines-survive case at T = 3 is #2162's 2-adic/tropical corollary. (3) A gain g = v − cost needs ≥ g a-cancelling lines in every frame of reference (every 𝔭, every a).

### 3.2 Proposition 2 (tropical ceiling) — PROVEN

For P, Q realising M, every 𝔭 and every a: for every cyclic sequence t_1 → … → t_k → t_1 in S_a,  Σ_i ν(M_{t_i t_{i+1}}) ≥ Σ_i ν(M_{t_i t_i}).

*Proof.* After the normalisation of Theorem 1, ν(p(t)·q(s)) ≥ 0 for all t, s (ultrametric inequality), with equality on the diagonal for t ∈ S_a; undoing the normalisation, ν(M_ts) ≥ m_t + n_s for all t, s, with equality at t = s for t ∈ S_a. Sum around the cycle: Σ ν(M_{t_i t_{i+1}}) ≥ Σ (m_{t_i} + n_{t_i}) = Σ ν(M_{t_i t_i}). ∎

Hence |S_a| ≤ τ_𝔭(M) := max{ |S| : the identity is a minimum-weight assignment for the weights ν(M_ts) on S }, a quantity of the geometry M alone.

**Corollary 2.1 (even root units) — PROVEN.** Let M = D_1 G D_2 (the Gram matrix of a root unit up to diagonal rescalings, ν(G_tt) = ν(2) = 1, ν(G_ts) = 0 for non-orthogonal t ≠ s since G_ts = ±1). For t ≠ s in S_a non-orthogonal, the 2-cycle t → s → t has weight ν(M_ts) + ν(M_st) = 0 < 2 = ν(M_tt) + ν(M_ss) (the diagonal rescalings cancel around a cycle), contradicting Proposition 2. So S_a is pairwise orthogonal, M[S_a, S_a] is diagonal and nonsingular, and **|S_a| ≤ ω ≤ T**, where ω is the largest pairwise orthogonal set of lines. Every order-0 (cancellation) certificate on E6, E7, E8, D_n and their punctures is capped at T (at 8 on P112, against the floor 64 of Theorem 4).

**Corollary 2.2 (odd geometry) — PROVEN.** If M has an integral normalisation with unit diagonal (Eisenstein, h(r, r) = 1) then τ_𝔭(M) = v, so Proposition 2 puts no ceiling on |S_a|; cost ≥ v follows from Theorem 1 for every decoder in which all lines survive for some (𝔭, a) (Corollary (2)). It does not follow for every decoder; for the Eisenstein unit, cost ≥ 40 for every decoder is #2017's theorem, by a different argument (reduction of the normalised Gram matrix to F4).

### 3.3 Tightness (CHECKED: `checks/c5_place.py`)

Exact 2-adic valuations of the coordinate decoders (half-integer shifts on rational decoders are legitimate through Theorem 1's "every number field": K = Q(√2), 𝔭 = (√2), e = 2); ω computed by exhaustive search (stops at T, a proven upper bound).

| unit | basis | s(a = 0) | best s found (seeded hill-climb, half-integers in [−3, 3]) | ω = ceiling |
|---|---|---|---|---|
| E8 | frame of roots / simple roots / coordinates | 8 / 0 / 0 | 8 / 8 / – | 8 |
| E7 | frame / simple | 7 / 0 | 7 / 7 | 7 |
| E6 | simple | 0 | 4 | 4 (T = 6) |
| D4 | frame / simple / coordinates | 4 / 0 / 0 | 4 / 4 / – | 4 |
| D5 | simple / coordinates | 0 / 0 | 4 / – | 4 (T = 5) |
| D6 | frame / simple / coordinates | 6 / 0 / 0 | 6 / 6 / – | 6 |
| P112 | basis F0 (cost 64) | 0 | – | 8 |

*Reading.* The best shift reaches the proven ceiling ω in every searched simple-root and frame case, so these s* are exact; for coordinate bases only s(0) = 0 is claimed. Nowhere is the place bound close to the optimum (8 against 72 on E8, 8 against 64 on P112, 7 against 49 on E7): the E-type floors are **not** cancellation phenomena. In odd geometry the ceiling is v; for Eisenstein the value 40 = v is #2017's theorem (not recomputed here).

### 3.4 Beyond order 0 (CHECKED: `checks/c6_beyond.py`)

A "Hadamard" certificate bounds the cost by the rank of a *sum* Σ_j D(x_j) B D(y_j). In the dual bit model (#798/#2017: B = Σ_j 1_{R_j}1_{A_j}ᵀ over F2, charge rank_K M[R_j, A_j]) the rank-of-sum object is rank_Q(G ∘ C) for the integer coverage matrix C = Σ_j 1_{R_j}1_{A_j}ᵀ; any admissible C has C_tt odd and C_ts even where G_ts ≠ 0. On E8 take C_tt = 3, C_ts = 2 where G_ts = +1 and 0 otherwise (a nonnegative integer matrix). Then G ∘ C = 2Z⁺ with Z⁺ = (G∘G + G)/2 integral, odd diagonal, zero on orthogonal pairs, and **rank_Q Z⁺ = 44 = 36 + 8** (rank G∘G = 36 = dim Sym² Q⁸); likewise Z⁻ = (G∘G − G)/2 has rank 44. So **no certificate of this rank-of-sum shape can prove more than 44 for the E8 value 72** (we do not claim this coverage matrix is realised by a decoder of total charge < 72). In Model C the 2-adic Smith profile of each dense block B[D_j, D_j] (D_j the 78 lines with nonzero coordinate j) is {0: 9, 1: 26, 2: 22, 3: 14, 6: 6, 8: 1}: 9 unit invariants (the F2 rank) and 26 invariant factors exactly 2 per term, 72 and 208 over the 8 terms. *Interpretation (not a theorem):* the E-type floors behave as rank-splitting phenomena (a sum of T' blocks of rank k+1 against a sum of low rank), not as cancellation.

## 4. The dense polar law

### 4.1 Theorem 3 — PROVEN

A unit is **odd-or-zero** if G_tt is even and G_ts is odd whenever t ≠ s and G_ts ≠ 0 (all root units). Let Ḡ = G mod 2 ∈ F2^{v×v} (symmetric with zero diagonal), V := F2^v / ker Ḡ, k := dim V = rank Ḡ, ℓ_t := the class of e_t, and b(x̄, ȳ) := xᵀḠy (well defined, bilinear, symmetric, nondegenerate on V, alternating because b(x̄, x̄) = Σ_t x_t Ḡ_tt + 2Σ_{t<s}(…) = 0). Put Ω := 1 ⊕ b on F2 ⊕ V (nondegenerate, symmetric) and u_t := (1, ℓ_t). For U_X := span{u_t : t ∈ X}:

1. **B_ts = Ω(u_t, u_s)** for the dense pairing: Ω(u_t, u_s) = 1 + Ḡ_ts, which is 1 for t = s (Ḡ_tt = 0) and, for t ≠ s, equals 1 iff G_ts is even iff G_ts = 0 (odd-or-zero).
2. **rank_F2 B[R, A] = dim U_R − dim(U_R ∩ U_A^{⊥Ω})** for all line sets R, A; in particular **≤ dim U_R ≤ k + 1**.
3. If R ⊆ N(α) := {t ≠ α : G_tα ≠ 0} for a line α (live or dead), then U_R ⊆ u_α^{⊥Ω}, a hyperplane (u_α ≠ 0 as its first coordinate is 1): **the block rank is ≤ k**. If also A ⊆ N(β), U_R = u_α^{⊥Ω} (the labels of R span the hyperplane) and G_αβ is odd (⇔ Ω(u_α, u_β) = 0), then 0 ≠ u_β ∈ U_R ∩ U_A^{⊥Ω} and **the rank is ≤ k − 1** (for a dead α, labels and Ω are those of the unpunctured unit).

*Proof.* (1) is the computation above. (2) By (1), B[R, A] is the matrix of the composition F2^A → F2 ⊕ V → F2^R, c ↦ Σ_{s∈A} c_s u_s ↦ (Ω(u_t, ·))_{t∈R} applied to that vector. The first map has image U_A; the second has kernel U_R^{⊥Ω}. So rank B[R, A] = dim U_A − dim(U_A ∩ U_R^{⊥Ω}). Ω is symmetric, so B[R, A]ᵀ = B[A, R], and the same formula with the roles exchanged gives rank = dim U_R − dim(U_R ∩ U_A^{⊥Ω}). (3) For t ∈ N(α): Ω(u_t, u_α) = 1 + Ḡ_tα = 1 + 1 = 0. The second part: U_A ⊆ u_β^{⊥Ω} gives u_β ∈ U_A^{⊥Ω} (Ω symmetric); u_β ∈ u_α^{⊥Ω} = U_R iff Ω(u_α, u_β) = 0, i.e. Ḡ_αβ = 1. So u_β ∈ U_R ∩ U_A^{⊥Ω}, and the rank is at most dim U_R − 1 = k − 1. ∎

**Corollary 3.1 (upper bound) — PROVEN.** If an odd-or-zero unit has an exact T-term Gram decoder, its dense-pairing cost is ≤ T(k + 1) (T blocks of rank ≤ k + 1), so cost* ≤ min(v, T(k + 1)); a dead (punctured) line used as a normal saves one rank (≤ k); a second, when both normals are dead and G_αβ is odd, saves another (≤ k − 1), by item 3.

### 4.2 CHECKED (`checks/c1_polar.py`)

| unit | v | T | odd-or-zero | k | rank B | T(k+1) | min(v, T(k+1)) |
|---|---|---|---|---|---|---|---|
| D4 | 12 | 4 | yes | 2 | 3 | 12 | 12 |
| D5 | 20 | 5 | yes | 4 | 5 | 25 | 20 |
| D6 | 30 | 6 | yes | 4 | 5 | 30 | 30 |
| E6 | 36 | 6 | yes | 6 | 7 | 42 | 36 |
| E7 | 63 | 7 | yes | 6 | 7 | 49 | 49 |
| E8 | 120 | 8 | yes | 8 | 9 | 72 | 72 |

On E8, with C(α) = N(α) ∪ {α}, over all 120 × 120 ordered pairs: r(C(α), C(β)) = 9 = k + 1; r(N(α), C(β)) = 8 = k; r(N(α), N(β)) = 8 for α = β or α·β even (7,680 pairs) and **7 for α·β odd (6,720 pairs)**. This is #968's rule "a term costs 7 iff both normals are punctured and α·β is odd, else 8", now a consequence of item 3 (the equalities are CHECKED; Theorem 3 proves the upper bounds).

### 4.3 The P104 decoder (CHECKED: `checks/c2_decoders.py`, `lib/p104.py`)

Rebuilt from scratch with exact Fractions and the dense B. F0 = the coordinate frame {e_{2i} ± e_{2i+1}}; the 112 remaining lines contain 1,260 orthogonal 8-frames F1; the first admissible one (lines 2, 18, 40, 52, 77, 86, 107, 112 in our 0-based order) gives 8 pairs (α_k, β_k), 4 with α_k in F0 and 4 in F1, with α_k·β_l = 0 (k ≠ l) and α_k·β_k = ±1; P_{t,k} = r_t·α_k, Q_{t,k} = (α_k·β_k)(r_t·β_k) satisfy PQᵀ = Gram on the **104 live lines**, every term has rank 7 and the cost is **56**; the 16 normals are exactly the dead lines F0 ∪ F1 (both normals of every term are punctured and α·β is odd: item 3 gives rank ≤ k − 1 = 7).

## 5. The root-code floor

### 5.1 Theorem 4 — PROVEN

**Hypotheses (exactly).** A unit with live lines r_t ∈ Q^n (rows of R), Gram G, span V of dimension T. A field K of **characteristic 0**. Matrices P = D_1 R X, Q = D_2 R Y with D_1, D_2 invertible diagonal and X, Y ∈ K^{n×m}, m arbitrary (**the factors lie in the live root code**; no bound on the number of terms). M = PQᵀ is **exact for the dense pairing**: M_tt ≠ 0 for all t, and M_ts = 0 whenever t ≠ s and G_ts = 0 (this is admissibility of the dense B; every exact Gram decoder has this zero pattern — the root-code hypothesis on P, Q is separate). The cost is the cost of the **dense pairing B** of the unit (restricted to the live lines). Let ω be the largest pairwise orthogonal live set.

**Types.** Let B = Ξ Ηᵀ be a factorisation over F2 with labels ξ_t, η_s ∈ F2^{k'} (any factorisation; we use a rank factorisation, k' = k + 1 for the units below; row labels ξ, column labels η). For z ∈ F2^{k'} \ {0} put O_z = {t live : ξ_t·z = 1}, W_z = span_K{r_t : t ∈ O_z} ⊆ K^n. For a term with row normal x ∈ K^n (so R(x) = {t : r_t·x ≠ 0} is the support of that column of P):

  Def(x) := ( span{ξ_t : t ∈ R(x)} )^⊥ = {z : O_z ∩ R(x) = ∅} = {z : W_z ⊆ x^⊥}.

If S(x) := Σ_{z ∈ Def(x)} W_z, then Def(x) = Def(S(x)) where Def(S) := {z : W_z ⊆ S}, because x ⊥ S(x). Only the finitely many **types** S = sums of *proper* W_z (dim S < T; for x ∉ V^⊥ the space x^⊥ ∩ V is proper) matter, and each type is realised: for a proper sum S, a generic x ∈ V ∩ S^⊥ avoids the finitely many proper subspaces W_z^⊥ ∩ S^⊥ for W_z ⊄ S, so Def(x) = Def(S) (K is infinite). The same for columns with η. For a term with normals x, y the F2 rank of its block is, by Theorem 3(2) (the proof of which is the pairing-rank argument for any factorisation),

  r(x, y) = dim U_x − dim(U_x ∩ Def^col(y)),  U_x := Def(x)^⊥ ,  Def^col(y) := ( span{η_s : s ∈ A(y)} )^⊥ ,

so r(x, y) depends only on the types of x (rows) and y (columns). Put **r_min := min over all pairs of types.**

**Theorem 4.** In the class above, **cost ≥ m_0 · r_min ≥ ω · r_min**, where m_0 ≥ ω is the number of terms with p_j ≠ 0 ≠ q_j (i.e. x_j, y_j ∉ V^⊥). In particular if ω = T the cost is **≥ T · r_min with any number of terms**. The same bound T·r_min holds for D5 and E6 (where ω < T) by §5.3 (the form N = XYᵀ is forced to be proportional to the Gram form).

*Proof.* Terms with p_j = 0 or q_j = 0 contribute 0 to M and to the cost; drop them (m_0 terms remain). Then rank M ≤ m_0. A pairwise orthogonal live set F has M[F, F] diagonal (M_ts = 0 for orthogonal t ≠ s) with nonzero diagonal, so rank M ≥ |F| and m_0 ≥ ω. Each remaining term costs r(x_j, y_j) = rank_F2 B[R(x_j), A(y_j)] ≥ r_min by the formula above (supports are unchanged by D_1, D_2). Sum over the m_0 terms. ∎

*What the proof does not use:* exactness M = Gram is not needed, only the zero pattern of M on orthogonal pairs and M_tt ≠ 0; the field is used only through "K infinite, W_z has its rational rank" (characteristic 0).

### 5.2 CHECKED: r_min and sharpness (`checks/c3_floor.py`, `checks/c2_decoders.py`)

All types are enumerated (closure of the proper W_z under proper sums), all 2^{k'} − 1 classes z, exact ranks.

| unit | v | T | ω (live) | k+1 | proper W_z | types | r_min | floor T·r_min | explicit exact decoder (cost) | status |
|---|---|---|---|---|---|---|---|---|---|---|
| E8 | 120 | 8 | 8 | 9 | 0 | 1 | 9 | **72** | coordinate / frame, 72 | sharp |
| P112 | 112 | 8 | 8 | 9 | 8 | 9 | 8 | **64** | basis = removed frame F0, 64 | sharp |
| P104 | 104 | 8 | 8 | 9 | 16 | 17 | 7 | **56** | frame pairs (§4.3), 56 | sharp |
| **E7** | 63 | 7 | 7 | 7 | 0 | 1 | 7 | **49** | frame basis, 49 | **sharp** |
| E7 − F (7-frame) | 56 | 7 | 7 | 7 | 7 | 8 | 6 | **42** | basis = removed frame, 42 | sharp (new unit) |
| D4 | 12 | 4 | 4 | 3 | 0 | 1 | 3 | 12 = v | coordinate, 12 | sharp |
| D6 | 30 | 6 | 6 | 5 | 0 | 1 | 5 | 30 = v | coordinate, 30 | sharp |
| D5 | 20 | 5 | 4 | 5 | 5 | 6 | 3 | 15 | coordinate, 20 = v | pairwise gap; square ≥ 20 (L5) |
| E6 | 36 | 6 | 4 | 7 | 27 | 28 | 5 | 30 | v terms of rank 1, 36 (not in verify.sh; T-term 36 is #2125) | pairwise gap; square ≥ 36 (L5) |

Every decoder in the column "explicit exact decoder" satisfies PQᵀ = Gram on every live pair, and, except in the D5/E6 rows, its per-term ranks are all equal to the r in the table. So **on the seven sharp units the dense-pairing cost of root-code decoders is exactly the floor**, whatever the number of terms. "No deficient directions" (no proper W_z: E8, E7, D4, D6) means every term of every root-code decoder has the full rank k + 1; deficiencies come from (i) dead roots (punctures: P112, P104, E7 − F), matching Theorem 3(3), and (ii) non-root lattice directions, observed on E6 (27 weight directions) and D5 (5).

### 5.3 The non-unimodular units D5 and E6: N-space and coupling — PROVEN from CHECKED data (`checks/c4_coupling.py`)

**N-space (CHECKED).** The space of bilinear forms N on V with r_t N r_sᵀ = 0 for every ordered orthogonal pair (t ≠ s) is **1-dimensional** for D5 (140 pairs) and E6 (540 pairs). Hence for the class of §5.1, N|_V := XYᵀ|_V = c·Gram with c ≠ 0 (the diagonal is nonzero), rank N ≥ T, m_0 ≥ T, and Theorem 4 gives the floors **15 (D5) and 30 (E6)** for any number of terms (the constant is the same over every K ⊇ Q since the system has rational coefficients).

**Incidences (CHECKED).** The deficient directions (the unique direction d ∈ V orthogonal to a proper W_z, rank T − 1): E6 has 27 on each side, D5 has 5. Pair ranks recomputed directly from supports agree with the type table. E6: **every one of the 27 × 27 pairs (x, y) is non-orthogonal**; 432 pairs have rank 5 and 297 rank 6; deficient/generic pairs have rank 6; generic/generic rank 7. D5: the 20 orthogonal deficient pairs have rank 3, the 5 non-orthogonal pairs (a perfect matching: each x meets exactly one y) have rank 4; deficient/generic 4; generic/generic 5.

**Lemma 5 (square root-code decoders on E6 and D5) — PROVEN.** *Square* means m = T terms, so N = XYᵀ = c·Gram forces (rescale c = 1) (πy_i)·(πx_j) = δ_ij (X′Y′* = c·Id_V with X′ square implies Y′*X′ = c·I), π the projection to V.

*E6.* Let a (resp. b) be the number of j with x_j (resp. y_j) deficient. Term costs: 7 − [x_j deficient] − [y_j deficient] when at most one is deficient, 5 or 6 when both. If y_j is deficient then for i ≠ j, y_j ⊥ x_i, so x_i is not deficient (a deficient x_i would be non-orthogonal to every deficient y_j direction). Hence if a ≥ 1 and b ≥ 1 then a = b = 1 with the same j and cost ≥ 5 + 5·7 = 40 (that term costs 5 or 6, each of the other five costs 7); if b = 0 the cost is 42 − a ≥ 36; symmetrically for a = 0. **So every square E6 root-code decoder costs ≥ 36 = v: the E6 tie is PROVEN in this class.**

*D5.* In a square decoder y_j·x_j = 1 ≠ 0, so a term with both normals deficient is a matched pair (rank 4); every other term has rank ≥ 4 (deficient/generic 4, generic/generic 5). **Square D5 root-code decoders cost ≥ 5·4 = 20 = v.**

*Not covered (OPEN):* overcomplete E6 (m = 7 with seven rank-5 pairs would give 35 < 36) and overcomplete D5 (six rank-3 pairs, 18 < 20); in the overcomplete case the orthogonal deficient pairs of D5 may be used and the coupling above fails.

### 5.4 Forced minors (CHECKED: `checks/c6_beyond.py`)

For a symmetric incidence (M = Gram) a principal minor B[S, S] is unit triangular (indeed the identity) for *every* admissible pairing iff S is pairwise non-orthogonal, so r_j ≥ ω_non(D_j) with no assumption on B (this is the tool of #2176 in the symmetric case). On E8: ω_non(all lines) = 8, ω_non(N(α)) = 7, ω_non(N(α) ∩ N(β)) = 6 for every β ≠ α (α fixed; all α by W(E8)-transitivity) (|N(α) ∩ N(β)| = 24 for the 63 lines β with α·β even, i.e. orthogonal, and 28 for the 56 with α·β odd). So **forced minors give at most 7 per co-flat term, short of the 8 (P112) and 9 (E8) of Theorem 4**; they prove ≥ 56 for the P112 frame-decoder family and cannot close non-dense pairings. With asymmetric M the incidences are directed and larger triangular minors can occur.

## 6. Conjecture ID and open questions

**Two dual models.** Model C (here): M = Σ_j p_j q_jᵀ over K, charge rank_F2 B[R_j, A_j]. Bit model (#798/#2017): B = Σ_j u_j v_jᵀ over F2, charge rank_K M[R_j, A_j]. Same Hadamard identity with the fields swapped; dense E8 is 8 × 9 = 72 in Model C and 9 × 8 in the bit model.

**Conjecture ID (CONJECTURE).** For a unit (lines in an O_K-lattice, Gram M) and a prime 𝔭 | 2, the minimum cost cost* over decoders and pairings is: (a) *odd geometry* (τ_𝔭(M) = v): v; (b) *even, odd-or-zero geometry of label rank k*: min(v, T(k + 1) − p_eff) with p_eff the deficiencies (dead roots, non-root classes) that exactness lets a decoder use simultaneously (and never below T(k − 1)); for E8 punctures p_eff = p up to 16 (the frame pairs of §4.3), for E6 the coupling lemma gives p_eff = 0; (c) mixed geometry: open. A gain over v exists iff v > T(k + 1) − p_eff, the T² law of #2125 made exact.

| unit | v | T | k | formula | best value on record | lower bound on record (scope) |
|---|---|---|---|---|---|---|
| Eisenstein | 40 | 4 / Q(ω) | odd | v = 40 | 40 | #2017 (its model, any number of terms) |
| E8 | 120 | 8 | 8 | 72 | 72 | exactly 8 terms (#968, #1077); live root code, any number of terms (#1180, Theorem 4) |
| P112 | 112 | 8 | 8 | 72 − 8 = 64 | 64 | same scopes; root-star supports (#1236); Theorem 4 |
| P104 | 104 | 8 | 8 | max(72 − 16, 56) = 56 | 56 | #968 (8 terms); Theorem 4 (any number, dense B) |
| E7 | 63 | 7 | 6 | 49 | 49 (#1590 ERR1, #2125) | **Theorem 4: root-code factors, dense B, any number of terms** |
| E7 − 7-frame | 56 | 7 | 6 | 42 | 42 | Theorem 4 |
| E6 | 36 | 6 | 6 | min(36, 42) = 36 | 36 (tie) | Theorem 4 + Lemma 5 (square); m = 7 OPEN |
| D4 / D5 / D6 | 12 / 20 / 30 | 4 / 5 / 6 | 2 / 4 / 4 | 12 / 20 / 30 | v | Theorem 4 (D4, D6); Lemma 5 (D5, square); T ≤ 2: #1590 Lemma A; T = 3 open |

The formula matches every value on record in the table, each under the scope stated; this is a consistency check on Conjecture ID, not a proof. Frame-pair analogues (the second deficiency) exist only on E8: a root basis whose dual basis consists of roots needs a unimodular lattice (our census found no admissible frame pair on E7 or D6; this is not re-run in `verify.sh`).

**Open next questions.** Questions only; nothing below is claimed.
1. *Non-dense pairing B.* Relevance: would lift Theorem 4 from the dense pairing to every admissible B (E7 49 over all pairings). First step: a block fitting-minrank computation for B[R_j, A_j] on the co-flat pairs of E7, then E8 (a block version of #1744, rank ≥ 9 for any fitting B on P112). Blocker: the size of the fitting-minrank search; forced minors reach only 7 (§5.4).
2. *Factors outside the root code / non-Gram M* (e.g. the 9-term decoder of #1180 outside the code). Relevance: this is the other half needed for an unconditional ideal-decoder theorem. First step: classify the supports of non-root-code columns on D4, where T = 4 is small. Blocker: supports are then arbitrary sets and Def(x) loses its meaning.
3. *Overcomplete coupling on non-unimodular lattices (E6 m = 7, D5 m = 6).* Relevance: decides whether 35 < 36 (E6) or 18 < 20 (D5) is attainable. First step: enumerate rank-5 (E6) and rank-3 (D5) deficient pair configurations compatible with N ∝ Gram for m = 7, resp. 6. Blocker: in the overcomplete case the orthogonal deficient pairs of D5 may be used and the square-case coupling no longer applies.
4. *Mixed geometry, BW16 / K12 and T = 3.* Relevance: units where some lines survive and some cancel, and the smallest T not covered. First step: for BW16 / K12 count the non-orthogonal pairs with even inner product (Theorem 3 needs odd-or-zero). Blocker: no analogue of Theorem 3 outside odd-or-zero units.

If questions 1 and 2 close in the form "every term costs at least the root-code value of its nearest co-flat pair", Theorem 4 becomes the ideal-decoder theorem for odd-or-zero units.

## 7. Relation to #2125 and to the E8 floors

- **#2125 (ours, open)** found E7 at cost **49 = T²** as the first gain (an explicit pairing for an exact decoder, hence an *upper* bound for the minimum) and explained the threshold T²; E8 72 was known (#1590 ERR1). **This package proves the matching lower bound in a class:** for every exact decoder of E7 whose factors lie in the live root code (any number of terms, any field of characteristic 0) the cost of the **dense** pairing is ≥ 49, so 49 is optimal *there*. It is **not** a lower bound over all admissible pairings B (sparser B are not covered), nor over decoders outside the root code, nor over non-Gram geometry. The dense polar law (Theorem 3) also explains the observed block rank k + 1 in the law of #2125: it is derived, not observed, for odd-or-zero units.
- **#620 / #717 / #1212 / #968 / #1180 / #1236 / #1744 / #1714** prove floors for E8, P112 and P104 under various scopes; Theorem 4 re-derives 72 / 64 / 56 by one argument (it does not extend #1180 on E8 punctures) (and ω = T gives the number of terms for free) and adds E7, E7 − F, D4, D6, and the square statements for D5, E6.
- The place bound (Theorem 1) extends #2162's 2-adic/tropical corollary (T = 3, all lines surviving) to every T, every 𝔭 and partial survival; the new content of §3 is the count |S_a|, the tropical ceiling (Proposition 2: order-0 certificates are capped at ω ≤ T on even root units, which bounds what #2162's '2-adic shadow' route can give at T ≥ 7), and the rank-of-sum witness (§3.4). The reduction-mod-2 idea itself is that of #1590/#2017.

## 8. Files

| file | content |
|---|---|
| `verify.sh` | step 0 (manifest, pins), then six check scripts, PASS/FAIL per row, non-zero exit on any FAIL |
| `lib/exact.py`, `lib/units.py`, `lib/floor.py`, `lib/p104.py`, `lib/report.py` | exact arithmetic over Q and F2; root units; the types/Def/r_min machinery of Theorem 4; the P104 construction |
| `checks/c1_polar.py` | label ranks and the E8 block-rank law (§4.2) |
| `checks/c2_decoders.py` | explicit decoders: E8 72, P112 64, P104 56, E7 49, E7 − F 42, D4 12, D5 20, D6 30 (§4.3, §5.2) |
| `checks/c3_floor.py` | Theorem 4: types, r_min, ω, sharpness (§5.2) |
| `checks/c4_coupling.py` | D5/E6 deficient directions, incidences, N-space (§5.3) |
| `checks/c5_place.py` | place bound survivors, tightness table (§3.3) |
| `checks/c6_beyond.py` | rank-44 witnesses, 2-adic carry, forced minors (§3.4, §5.4) |

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0 (`LICENSE`, copied from the repository root). See `NOTICE.md` for credits.
