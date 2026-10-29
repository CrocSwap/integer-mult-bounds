# ARCHITECT — blueprint for a proof that the decoder optimum is global (C(P112) = 64, C(P120) = 72)
Labels: PROVEN (written proof, cited) · PROVEN-pa (pending audit) · CHECKED (exact script) · OPEN. W = ~/repo_clones/intmult-work.
Scripts here (python = W/venv/bin/python, each < 2 min): p120cat.py, p120swap.py (P120 catalogue), retract.py (retraction test on all exact
witnesses), rls1.py (Theorem RL-s1 bound on witnesses). Oct 15, 21:00–.

## 1. The exact target statement

**Model M(L)** (L = P112 or P120, lines of E8). Labels ℓ_t ∈ F2⁹, dense table Bd[t,s] = β(ℓ_t,ℓ_s) = [t = s or t ⊥ s]. A decoder is P, Q ∈ K^{L×m}
(char K = 0, any m) with (PQᵀ)_tt = 1 and (PQᵀ)_ts = 0 for t ⊥ s, all other entries free. Cost = Σ_k ρ(R_k, A_k), ρ(R,A) = rank_F2 Bd[R,A],
R_k = supp p_k, A_k = supp q_k. C(L) := min cost. **T112: C(P112) ≥ 64. T120: C(P120) ≥ 72.** Both attained (coordinate decoders).

**B is fixed by the labels; K6 is out of scope.** In the hosted format a term is charged against a fitting table B (B_tt = 1, B_ts = 0 on non-orthogonal
pairs, free on orthogonal pairs) of global F2-rank h. At the minimum h = 9 B is FORCED to Bd (#2338 Theorem R, merged; DRAT on P112, E8, P104, P111),
so "every h = 9 table" = M(L). K6 (h ≥ 12), like h = 10, 11, concerns different quantities C_h(L): non-dense B exist from h = 10 (SAT witness), the bar
is the break-even price of the wider window (≤ 59 at h = 10, ≤ 55 at h = 11, ≤ 51/46/42 at h = 12/13/14; RECORDED), and what is proven there covers
root-code (inside) factors only (every term ≥ 8 at h ≤ 10, ≥ 7 at h = 11: #2639 states its class as "root code = Gram realisation, any m, any fitting B of rank ≤ h"). **T112/T120 are statements at h = 9 with B = Bd;
K6 is not a node of their DAG.** The physical claim "decoder optimisation is dead" = T120 (or T112) + window statements C_h ≥ bar(h) for every h ≥ 10
(outside factors open at every h ≥ 10; K6 is the h ≥ 12 inside part) + batching (K5). Universality (#2832 §2.1) uses only B_ts = 0 on non-orthogonal
pairs, so it holds at every h; Theorem R does not, and nothing below uses h ≥ 10.

## 2. Dependency DAG

### 2.0 Trunk (both targets)
- **U0 Universality** — PROVEN (#2832 §2.1): C(L) = min over exact decoders of N₀ = G/2. Realisation-level fronts (rank-9 B-form/A2 #2819/#2784/#2830,
  BFORM, extra zeros = ZPIN [≤ 1 extra zero / one-row zeros UNSAT, drat-checked; general → ZPIN2] / philippeVV R1, R2) are therefore NOT on the critical path; they matter only as landing places of reductions (GEN21 Lemma 4.6).
- **S0 Structure** — PROVEN (#2832 §2.2): P = [C E]X̂, Q = [C F]Ŷ, X̂Ŷᵀ = diag(I₈,0), E, F free; classes (s,t); Sylvester m ≥ 8 + s + t.
- **GL (monotone half of the gain law)** — PROVEN here, one line: C(L) ≤ C(L′) + |L ∖ L′| for L′ ⊆ L (extend every factor by 0 on the new lines, add δ_vδ_vᵀ,
  cost 1, per new line; Bd restricts to Bd). Hence **T120 ⇒ T112** (and P111 ≥ 63, P104 ≥ 56). Superadditivity is not needed anywhere.
- **R1′ ε-free lift floor** — PROVEN (#2816 Thm 1): cost_w(S) ≥ 64 for every S ⊇ 𝒞. Any decoder has col P ⊇ 𝒞, so Σ_k w(R_k) ≥ 64 and, exactly,
  **cost = 64 + Δ_P − Σ_k c_k**, Δ_P := Σ_k w(R_k) − 64 ≥ 0, c_k := dim(U_{R_k} ∩ Z_{A_k}). So **T112 ⇔ (GK2) Σ_k c_k ≤ Δ_P for every decoder of N₀**:
  K2 is GK2 for one-sided decoders (only frame classes correct), K1 is GK2 with outside-column classes added. (Tautological, but it is the right ledger.)

### 2.1 T112
```
T112 ⇐ U0 ∧ A ∧ B ∧ C        (exhaustive split of decoders of N₀ by (s,t))
A  inside (0,0), any m ............................... PROVEN  #2338 Thm P (merged)
B  one-sided, any m  ⇔  K2: Δ ≥ n_nf ................. PARTIAL
   B.1 ε-free ≥ 64, unique optimum ................... PROVEN  #2816 R1/R2 (open PR, audited)
   B.2 n_nf ≤ 2 ................................... PROVEN  #2816 R3
   B.3 Δ ≤ 2 ⇒ n_nf ≤ Δ; n_nf ≤ 3 ⇒ ≥ 64; lift ≥ 64+min(|I|,3) ... PROVEN #2826 (two impls)
   B.4 Δ = 3 ...................................... PROVEN-pa  SIX §8 (single impl.)
   B.5 Δ ∈ {4..7}  (Δ ≥ 8 vacuous since n_nf ≤ 8)
       d = 0 half ................................. PROVEN-pa  DUAL D0.1–D0.7, EXCEPT cell [4,3]-overlap (OPEN);
                                                    caveats: dependent-F case, [7] cell float/single-impl (exact rerun needed)
       d ≥ 1 half ................................. RUNNING   MS3c killed 24/47; S3FLAT card note 21:05: (6,6,4) s=0 kills all but ≤ 4 "big" of the 23, (6,6,5) running (no STATE line yet)
C  two-sided (= K1) .................................... PARTIAL
   C.0 projection transfer, pivot bound, Lemma-D, catalogue, pair lemma, collinearity ... PROVEN #2832 §3 (COND. #2816)
   C.1 (1,1), m = 10 (= K3) ....................... PROVEN-pending-PR (AUDIT-LOWD confirmed coverage table; CONDITIONAL only on #2816,
       #2724 NOT needed): disjoint #2832 §3.6; D_P,D_Q ≥ 5 TWINSWAP §6; some side D̂ ≤ 3 LOWD Thm; D = 4 Case A LOWD/d4A3, Case B → MOONSHOT2 (B)
   C.2 (1,1), m ≥ 11 ............................ OPEN — no card. §3: RL-s1 reduces it to (G1)+(G2)+K2.
   C.3 (2,1)/(1,2), m = 11 ...................... PARTIAL (GEN21 stopped; patterns A/B → MASK-RANK9 Case B / A2COST m ≥ 10).
                                                  §3: RL-s1 on the single column direction applies verbatim (any m).
   C.4 (s,t), s,t ≥ 2, any m ..................... OPEN; needs RL for a side with ≥ 2 directions (§3.5)
```
**Leak K2 → K1.** The pivot bound carries −(|I| − 3)₊ (after #2826): its residue is lift-level K2 (ρ₀ ≤ Δ). The retraction route of §3 never uses the pivot
bound; it needs K2 only at the one-sided leaves.
**Minimal open set for T112** (K3 closed; assuming SIX §8 audit passes): **(O1)** K2 for Δ ∈ {4..7} (cell [4,3], S3FLAT's last survivors, DUAL caveats);
**(O2)** the unpaid-swap lemma G1 (§3.4); **(O3)** the large-pivot lemma G2 (§3.4); **(O4)** RL for sides with ≥ 2 directions (§3.5).
C.1 becomes a corollary/cross-check once O2–O3 hold; C.2, C.3 are covered by RL-s1 + O2 + O3 + K2.

### 2.2 T120 (details §4)
```
T120 ⇐ U0 ∧ A′ ∧ B′ ∧ C′
A′ inside, any m ..................... PROVEN  #2338 row 3 / #2277 Cor 5.3 (on E8 every inside term costs 9)
B′ one-sided ⇔ L120: cost_w(S) ≥ 72 ∀ S ⊇ 𝒞(E8)   (no corrections on P120, CHECKED p120cat.py)
                                       PARTIAL: ≥ 67, and ≥ 72 unless the P112 restriction has Δ ≥ 3 (#2826 S6)
C′ two-sided ......................... OPEN; RL-s1 holds on P120 with one correction type (root swaps), threshold 13
```

## 3. The key generalisation: the Retraction Lemma

### 3.1 The move
For a decoder (P,Q) of N₀, a row direction e_a (column of E) and h ∈ K⁸, the **retraction** ρ_{a,h} replaces e_a by C′h. By S0 the result is again a
decoder of N₀, with ≤ s − 1 row directions, same columns. Put λ := e_a − C′h, S_λ := supp λ. Row k changes only on S_λ and only if x2_k[a] ≠ 0.
Choosing h = −x_π/x2_π (s = 1) makes p_π = x2_π λ: term π is the **pivot**, R_π = S_λ, and it disappears. Then
**Δ_π := cost(ρ_π) − cost = Σ_{k≠π} ε_k − cost_π**, ε_k := ρ(Off(x_k + x2_k h), A_k) − ρ(R_k, A_k) (LOWD L2 / GEN21 §3 identity, m-free).
Projection transfer (#2832 §3.1) is the retraction with GENERIC h on the column side: there Δ = +Σ c_k ≥ 0, so generic h never helps; RL needs special h.

### 3.2 Statement
**RL (strong).** Every decoder of N₀ with s + t ≥ 1 has a side, a direction and h with cost(ρ_{a,h}) ≤ cost.
**RL₆₃ (sufficient).** Every decoder with s + t ≥ 1 and cost ≤ 63 has a retraction of cost ≤ 63.
**Theorem (PROVEN, induction on s + t).** RL₆₃ + #2338 Thm P ⇒ T112. RL₆₃ restricted to s, t ≥ 1 + K2 ⇒ T112. Same on P120 with 71/72.
**Unification.** In the tight case m = 8 + s + t, RL at every pivot is the "block identity" cost = 64 + Σ_pivots cost_π − Σ_dual (s_l − 1) read one pivot at a
time; MS3a's cost = 64 + #bad is that identity on the swap family (each pivot pays the one dual term it serves: Δ_π = 0); LOWD's L2 is RL at the low row
(Δ ≤ |T₀|); GEN21 §3 is RL with both row directions at once; RESIDUE's idempotent/Ω step and L1/L3 are the tight-m proofs of the large-pivot case G2.
**Evidence (CHECKED retract.py, exact).** Every exact witness has Δ = 0 at some pivot on EVERY side and direction: witness16 disjoint and shared, MS3a (2,1)
decoder.json (all 3 directions), swap family (1,1), (2,2), (1,3), (4,4) (all 4+4 directions), double swap (cost 68, both sides). No witness needs RL₆₃.

### 3.3 Theorem RL-s1 (PROVEN here; m-free; P112, and P120 with 11 → 13)
Let (P,Q) be Lemma-D-normalised with exactly one row direction (s = 1; any t, any m), π ∈ J_P a pivot with |R_π| = |S_λ| ≤ 11. Call v ∈ S_λ a **swap line**
if some k ≠ π has x′_k := x_k + x2_k h ∝ c_v and p_k(v) = 0; **paid** if q_π(v) ≠ 0, **unpaid** otherwise (U_π). Then
**cost(ρ_π) ≤ cost + |U_π|.**
*Proof.* (i) ε_k = dim(U_{R′}+Z_A) − dim(U_R+Z_A) ≤ 9 − w(R_k) = d^R_k; ε_k ≥ 1 ⇒ R_k ∩ O_z = ∅ for some z. Since p_k = C′x′_k + x2_k λ, C′x′_k vanishes on
O_z ∖ S_λ, so |Off(x′_k) ∩ O_z| ≤ 11; the catalogue (#2832 §3.4) leaves x′_k = 0 (ε ≤ 0), frame type x′_k ∝ f_i, z = z_i (R_k ⊇ Off(f_i) ∖ S_λ still spans W_i,
LOWD micro.py: ε ≤ 0), or x′_k ∝ c_v, z = u_v, v ∈ S_λ, p_k(v) = 0; then R_k ⊇ Off(c_v) ∖ S_λ has ≥ 42 > g(7) = 36 lines, w ≥ 8, ε_k ≤ 1.
(ii) Two swap rows at the same v: both p's lie in span(C′c_v, λ) and vanish at v, so they are proportional — merged by Lemma D. So ≤ 1 swap row per line.
(iii) A swap row at v vanishes on O_{u_v} = {v} ∪ v^⊥; on v′ ∈ S_λ ∩ v^⊥ it equals x2_k λ(v′) ≠ 0. So S_λ ∩ v^⊥ = ∅: swap lines are pairwise
non-orthogonal, Bd[V,V] = I.
(iv) cost_π = ρ(S_λ, A_π) ≥ rank Bd[V ∩ A_π, V ∩ A_π] = |V ∖ U_π|. So Δ_π ≤ |V| − |V ∖ U_π| = |U_π|. ∎
The case x′_k = 0 is in fact excluded by Lemma D (then p_k ∝ p_π).
**t = 0 reading.** With t = 0 (case (b), s = 1, col P of dimension 9) RL-s1 says: a small pivot whose swaps are all paid retracts to an INSIDE decoder, so cost ≥ 64 by Thm P. Cross-check against #2816 §5.2 (Δ = 1 / dim-9 lift classification, root swap = the unique non-full correction): it is either a corollary of it or a small new piece of K2 — flag before citing.
(Used: catalogue + direction-list completeness (#2816/#2832 §3.4), micro.py, gtab.py. New vs GEN21 4.4/LOWD L2: no normal form, no duality, any m, any t.)
**CHECKED rls1.py:** on every pivot with |R_π| ≤ 11 of every witness side with one direction, Δ_π = 0 = |U_π| (paid swap); pivots with large R_π have Δ ∈ {0,1,2,8}.
**P120 version (CHECKED p120cat.py, p120swap.py):** catalogue min |O_z ∩ Off(h)| is 1 only for (root r_v, z = u_v), otherwise ≥ 14, so threshold 13; there
is no frame type; Off(c_v) has 57 lines and a 7-dim label space holds ≤ 32 of them (< 57 − 13).

### 3.4 The two gaps (exact statements; these ARE O2, O3)
**G1 (unpaid swaps).** Decoder with s = 1, cost ≤ 63: show some side admits a retraction of cost ≤ 63 even if every small pivot has U_π ≠ ∅ — e.g. by proving
"cost(ρ_π) ≥ 64 + |U_π|" (GEN21's missing lemma, now m-free in form) or by retracting the other side. Known facts at tight m (GEN21 2.2, LOWD L2(e)): an unpaid v
forces π ∈ J_P ∩ J_Q and μ(v)y2_π λ(v) = −1, and v ∈ A_a for every other a ∈ J_Q. **The open sub-lemma is the m-free form of that identity**, using only
P Y₂ᵀ = 0 (Σ_{J_Q} p_k(t) y2_k = 0), Σ_k x2_k q_k = 0, and row v of PQᵀ = N₀ on O_{u_v}. Cost-0 pivots are off-mask padding (GEN21 Lemma 4.6), so G1 ⊆ "one-sided
m ≥ 10 decoders of |supp c| = 1 B-form rank-9 realisations" (A2COST) — an existing front, now an edge.
**G2 (large pivots).** All pivots of all one-direction sides have |R_π| ≥ 12 (P120: ≥ 14). Then every J_P row has w ≥ 5 (g(4) = 8 < 12), and WALL 8.1–8.3
(pair lemma, collinearity, ≤ 2 weight-7) are m-free (they use only that J_P rows lie in one coset λ + 𝒞). Needed: an m-free deficiency budget
(LOWD L1 is Σ s ≤ Σ d^R + Σ d^A with the t = 1 coset count; at general m the inside-both terms and the second side need Σ d^A bounded by D̂_Q + #terms).
At m = 10 LOWD/TWINSWAP/RESIDUE close it; witnesses show Δ = 0 is also reached at large pivots (w16 disjoint pivot 6, |R| = 55).
**Not a gap: K2** at the leaves (O1), or — stronger — RL on one-sided decoders (retraction to inside, base Thm P), which would prove K2 too.

### 3.5 Several directions on one side (O4)
For s ≥ 2, retract one direction e_a with h; terms carrying e_a and another e_b have rows C′x′ + x2[a]λ + x2[b]e_b, so (i) runs with S_λ ∪ supp e_b and the
pivot (p_π ∝ λ) exists only if some term carries e_a alone. GEN21's two-at-once deletion (Π-normal form) is the tight-m substitute. Untested idea: retract
the side with fewer directions first (if min(s,t) = 1, RL-s1 applies directly — this covers every (1,t) and (s,1) for all m).

## 4. The P120 step
**What changes on P120 (CHECKED p120cat.py).** (a) For every y ≠ 0, ℓ(Off(y)) spans F2⁹ (all 511 classes O_z have real rank 8): there is no frame exception,
because Off(f_i) now contains the line f_i with label z_i ∉ W_i. (b) Catalogue: min_z |O_z ∩ Off(h)| = 1 exactly for roots (intersection {v}, class u_v), 14 for
the 945 norm-4 directions (|Off| = 78), and ≥ 83 − 64 = 19 for all others (|Off| ≥ 83 since rank-7 flats other than E7, D7 hold ≤ 37 lines).
**Consequences.** (1) One-sided P120 decoders have NO corrections: cost = Σ_k w(R_k) ≥ cost_w(col P). So **B′ ⇔ L120: cost_w(S) ≥ 72 for every S ⊇ 𝒞(E8)** —
one lift statement, no n_nf bookkeeping. #2826 S6: ≥ 67, ≥ 72 unless the P112 restriction has Δ ≥ 3 with ρ₀ > Δ. So the P120 one-sided residue IS the lift-level
K2 residue at I = [8] (DUAL's [7] cell = its d = 0 extreme). (2) Two-sided: one correction type (root swap), threshold 13, RL-s1 holds as stated (§3.3).
The swap family is tight on P120 too (swap row 8 + unit 1 = 9 = coordinate term). (3) The frame F0 is not special on P120: everything is W(E8)-equivariant,
and the frame-type corrections that complicate P112 (Lemma P, n_nf normalisation, −(|I|−3)₊) disappear.
**Beyond P112.** T112 does not imply T120. What T120 needs beyond the P112 programme: L120 (the I = [8] lift — equivalently the hardest K2 cell, Δ ≥ 3 with
ρ₀ = 8 > Δ), and the two-sided gaps G1/G2/O4 on P120 (same proofs, thresholds 13/14). #2338's P120 rank-8 case = A′.
**Recommendation.** Run the two-sided programme on P120 directly: the statements are cleaner (no frame type, no |I| penalty), T120 ⇒ T112 by GL, and the
P112 one-sided K2 cells are subsumed by L120 + GL only through the full T120 (not cell by cell) — so K2 work on P112 should continue as the fallback.

## 5. Next assignments (in order of leverage)
1. **G1-MFREE (Opus, ≤ 2 h):** the unpaid-swap sub-lemma for s = 1, any m, any t: either cost(ρ_π) ≥ 64 + |U_π| or a retraction on the other side with
   cost ≤ 63. Inputs: RL-s1 (§3.3), GEN21 2.2/4.5(c)/4.6, LOWD L2(e). Test first on P120 (one correction type). Deliver: proof or an exact decoder with
   U_π ≠ ∅ at every small pivot (a structural counter-pressure). Also try coordinator's route (a): retract the COLUMN direction of (2,1) → (2,0), n_nf ≤ 3 ⇒ #2826.
2. **L120 (Opus/Sonnet, finite):** cost_w(S) ≥ 72 for every S ⊇ 𝒞(E8) — the P120 one-sided node B′ and the I = [8] cell of lift-level K2. Start from #2826 S6
   (≥ 72 unless Δ ≥ 3, ρ₀ > Δ); on E8 there is no frame type, so the peeling/LP/flat machinery runs W(E8)-equivariantly (orbit reduction 696729600).
   Merge with DUAL [4,3] + S3FLAT survivors into one K2/L120 ledger (one card, not three).
3. **G2-BUDGET (Sonnet, theory + small checks):** m-free deficiency budget for one-direction sides whose pivots all have |R_π| ≥ 12 (P120: ≥ 14): generalise
   LOWD L1 (Σ s ≤ Σ d^R + Σ d^A) using WALL 8.1–8.3 per coset (m-free) and a bound on Σ d^A over inside-both terms; check against witness16 pivot 6 (|R| = 55, Δ = 0).
Audit item: one read-only Sonnet audit of RL-s1 (§3.3, 4 steps) before anything cites it.
