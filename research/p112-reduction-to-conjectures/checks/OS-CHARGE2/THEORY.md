# OS-CHARGE2 — one-sided P112 ≥ 64? (continues cards/OS-CHARGE/THEORY.md)
Labels: PROVEN / CHECKED (exact script) / OPEN. python = W/venv/bin/python. Scripts are in this folder.

## §0 Status (Oct 15)
1. **ε-free one-sided P112 ≥ 64 for every d (CHECKED).**
   - This is the OS-CHARGE helper's LP closure, independently verified (§1).
2. **LIFT-LEVEL X_I THEOREM (PROVEN mod CHECKED inputs; FRAMEX form; Sonnet audit PASS on all 7 steps, audit/a.py; char 0 assumed for the E7-subsystem step).**
   - For every I ⊆ [8] and every subspace S ⊇ 𝒞_{X_I}:
     **cost_w(S) ≥ 64 + min(|I|, 2)**,
     and **cost_w(S) ≥ 64 + |I| unless Δ ≥ 2 and ρ_0 > Δ** (definitions in §2).
   - So the FRAMEX lift-level statement (≥ 64+|I|) holds for |I| ≤ 2.
   - **E8 version (I = [8]): every lift of the E8 root code has cost_w ≥ 66** (Theorem 56 gave 64). It is ≥ 72 unless the P112 restriction has excess Δ ≥ 2.
3. **Lemma N (SMALL2) independently re-implemented: CHECKED, in a stronger form** (§3).
   - For each 7-flat F, the exceptional set L may be chosen separately for each direction, and still at most 2 directions qualify.
   - I also audited the Pencil Lemma proof: it is correct, and gives d ≤ 2 directly.
4. **Negative results (§4).**
   - The X_I DP+LP alone does not close |I| ≥ 1. Every survivor has ≥ 8 pieces of weight 7.
   - Coupled "profile" LP (lines of a piece in u-dim y-spans): no gain for E8. E6-type 36-line 7-flats have the generic profile min(N_u, 36).
5. **OPEN.** Lift-level X_I for |I| ≥ 3 with Δ ≥ 2. This needs: Δ ≥ ρ_0, i.e. each z-carrying basis vector of the P112 restriction (with independent frame parts) costs one unit of excess. It is the lift-level twin of SMALL2's open "Δ ≥ n_nf for n_nf ≥ 3".

## §1 ε-free verification (CHECKED)
**Enumeration.**
- enum.py (OS-CHARGE) reproduces the dp3 survivors: 7 multisets at d=8, [7,6^8] at d=7, none at d=6.
- Its recursion covers every count vector with total < target, so the enumeration is complete.

**LP lemma: soundness re-derived.**
- C = QM, where Q is a basis of T = S_{≤7}, so c_t ∈ span{y_j : t ∈ supp q_j}.
- Each line t gets a minimal M(t).
- (a) Lines with M(t) ⊆ U lie in a ≤|U|-dim subspace, so there are at most N_|U| of them. In char 0 the roots in a subspace form a root subsystem of that rank, so N is the E8 maximum (A1 A2 A3 D4 D5 E6 E7).
- (b) Σ_{S∋j} m_S ≤ |supp q_j| ≤ g(w_j).
- Quotient (d<8): c̄_t ∈ K^8/H^⊥, N'_u = N_{u+8−d}, and lines with c̄_t = 0 number ≤ N_{8−d}.

**Independent check (symlp.py).**
- The LP is symmetrised over equal-weight pieces, which is exact by averaging.
- The dual certificate is repaired exactly with Fractions.
- Bounds: d=8 gives 96.92–101.82 < 112; d=7 gives 97.78 < 111.
- Control: 8 pieces of weight 8 give 112, so the control is not excluded.

**Limits of the LP.**
- The LP alone, without the DP, fails for d = 3..6 (sweep.py), so the DP is essential.
- At target 8d+2 (c65.py) the survivors are exactly:
  - the 7^k + small multisets at d = 7, 8;
  - [7^5,6^5] at d = 8.

## §2 Lift-level X_I theorem
**Setting.**
- X = X_I = P112 ∪ {f_i : i ∈ I}, with labels ℓ(f_i) = z_i, and S ⊇ 𝒞_X.
- B is a min-weight basis of S, and ρ is restriction to the P112 coordinates.
- π_F is the projection to the frame coordinates K^I.
- drop(b) := w(b) − w(ρb) ≥ 0, D := Σ drop, and Δ := Σ_b w(ρb) − 64.

**Identity.** cost_w(S) = 64 + Δ + D.

**R1.** Δ ≥ 0.
- ρB spans ρS ⊇ 𝒞, so Σ w(ρb) ≥ cost_w(ρS) ≥ 64 by the ε-free lift theorem (§1).

**R2 (frame rank).** π_F(S) ⊇ π_F(𝒞_X) = K^I, since π_F p_h = (⟨f_i,h⟩)_i. So
  |I| ≤ rank{π_F b} ≤ ρ_0 + |B_+| ≤ ρ_0 + D, where:
- B_+ = {b : drop(b) ≥ 1};
- B_0 = {b : drop 0, π_F b ≠ 0};
- ρ_0 = rank π_F(B_0).

**Z.** If b ∈ B_0, then ρb ≠ 0 (a zero restriction would drop the whole weight). Also ⟨ℓ(supp ρb)⟩ ∋ z_i for every f_i ∈ supp b. Call such a ρb **z-carrying**.

**Hence cost_w(S) ≥ 64 + |I| + (Δ − ρ_0)** and cost_w(S) ≥ 64 + Δ.

**Δ = 0.**
- Σ w(ρb) = 64, so ρS = 𝒞. This uses lift-level uniqueness: cost_w = 64 ⇒ T = 0, s = 8 ⇒ S = 𝒞 (peeling; d = 6, 7, 8 slack-0 multisets are killed by LP and Pencil, §3).
- The nonzero ρb are a min basis, i.e. 8 weight-8 codewords. These are the frame codewords p_{f_j}, whose flat is W_j.
- β(z_i, z_j) = 1 for all i, j, so W_j contains no z. Hence ρ_0 = 0.

**Δ = 1, case (i): cost_w(ρS) = 64.**
- ρS = 𝒞. Nonzero codewords weigh ≥ 8, so the nonzero ρb are 7 frame codewords plus one weight-9 vector.
- Hence ρ_0 ≤ 1.

**Δ = 1, case (ii): cost_w(ρS) = 65.** The nonzero ρb form a min basis.
- *Lift-level cost-65 classification.* Peeling gives cost_w = 64 + (cost(T) − 8d) + 8x + c_8.
  - d ≤ 5 gives DP slack ≥ 2.
  - d = 6, 7, 8 at slack ≤ 1: LP kills everything except 7^k + small (killed by Pencil) and [7^5,6^5] (killed by the e=2 triple rule: 10 triples > 8 f-directions).
  - d = 0 and S = 𝒞 gives 64.
  - So d = 0, T = ⟨δ_t⟩, s = 9, and the other 8 basis vectors have weight 8 in 𝒞 ⊕ ⟨δ_t⟩.
- *Weight-8 vectors p_h + λδ_t.*
  - The support has ≤ 64 lines, so |Off(h)| ≤ 65.
  - Hence ≥ 47 P112 lines are ⊥ h, which forces an E7 subsystem (D7 has only 42), so h ∝ a root or a frame vector.
  - h = f_j: the vector is supported in N(f_j) ⊆ W_j, so it is not z-carrying.
  - h = r_s with s ≠ t: weight 9, because N(r_s) ∖ {t} still has rank 8 (no coloops, c65.py, CHECKED).
  - h = r_t with t cancelled: the **root swap** p_{r_t} − cδ_t with flat W_t. It is unique up to scale.
  - δ_t is not z-carrying.
- Hence ρ_0 ≤ 1.

**Conclusion.**
- Δ ≤ 1 ⇒ ρ_0 ≤ Δ ⇒ cost ≥ 64 + |I|.
- Δ ≥ 2 ⇒ cost ≥ 64 + Δ ≥ 66, and ≥ 64+|I| whenever |I| ≤ 2, since ρ_0 ≤ |I|.
- Corrected P112 (decoder form, = X_I − |I|) gets the same bound: ≥ 64 − max(0, |I| − 2).
- The open case is precisely Δ ≥ 2 with ρ_0 > Δ: at least 3 z-carrying restricted basis vectors with independent frame parts.

## §3 Lemma N (CHECKED, lemmaN.c, 72 s) and Pencil audit
**Directions.**
- The direction list (1200 directions with |Off| ≤ 76, lnprep.py) is complete.
- |Off| ≤ 76 needs ≥ 36 P112 lines ⊥ h. The only subsystems with that many lines are E7, D7, E6+A1 and E6.
- An E6 or E6+A1 always contains ≥ 2 frame lines, because the frame lines ⊥ an A2 are the complement of two overlapping Hamming supports. So those types give |Off| ≥ 77 or 78 and drop out.
- What remains: root (53), f (56) and D7 (70/73/76), each with a unique direction.

**Result.**
- For all 43435 7-flats F, at most 2 directions h have |Off(h)∖F∖G| ≤ 4 for some 7-flat G.
- This holds with no shared L, which is stronger than Lemma N.

**Pencil Lemma (SMALL2 §7).** Audited step by step, all correct:
- λ(A) is independent;
- x ∉ span λ(A);
- every fundamental circuit C_y contains x;
- distinct y give distinct directions, and Off(h_y)∖F_x∖L ⊆ F_y;
- so a − e ≤ 2, i.e. d ≤ 2.

## §4 Negative / supporting results
- **dpX.py.** The X_I DP (the dp3 constraints transfer, since X_I targets contain the P112 targets) plus the LP leaves only 7^8+small survivors at d = 7, 8 for |I| ≥ 1. The LP value equals NL, i.e. it is non-binding.
- **E8 7-flat profiles (gwuE8.py).** The single Pareto profile is (1,3,6,12,20,36,36,36) from E6-type flats, so a coupled profile LP gains nothing for E8.
- **P112 7-flat profiles (gwu2.py).** The Pareto profiles are A = (1,2,4,8,12,20,35,36) for the 36-line flats, which have no A2 inside, and B = (1,3,6,12,20,34,34,34) for E6∩P112.
- **ω-relaxation.** Giving −1 to any z-carrying vector is too weak: 224 label hyperplanes contain z_i and hold 60 lines (om.py).

## §5 |I| = 3 at lift level reduces to SMALL2's six multisets (PROVEN mod CHECKED + OPEN six)
For |I| = 3 we need: Δ = 2 ⇒ ρ_0 ≤ 2. Write Σ w(ρb) = 66 and split on cost_w(ρS).

**(A) cost_w(ρS) = 64.**
- ρS = 𝒞, and the nonzero ρb are 8 codewords of weight 8 or 9 summing to 66: six frame codewords and two weight-9 vectors.
- So there are ≤ 2 z-carriers.

**(B) cost_w(ρS) = 65.** Then ρS = 𝒞 ⊕ ⟨δ_t⟩, and there are two sub-cases.
- Min basis plus one extra vector of weight 1, which must be ∝ δ_t: z-carriers ≤ 1.
- A basis of cost 66. It must contain δ_t, since otherwise the cost is ≥ 9·8. The rest is 7×8 + 1×9, so z-carriers ≤ root swap + one weight-9 vector = 2.

**(C) cost_w(ρS) = 66 with a min basis.** Peeling slack (cost(T) − 8d) + 8x + c_8 = 2.
- **c_8 = 1, slack 1:** d = 0 and T = ⟨δ_t⟩. Then z-carriers ≤ 2.
- **slack 2, d = 0:** T = ⟨δ_t, δ_u⟩ or one 2-piece on {t,u}.
  - A weight-8 vector p_h + τ needs |Off(h)| ≤ 66, so h is a root or frame vector.
  - For a root h = r_x with x ∉ {t,u}, the vector has weight 9: N(r) minus any ≤ 3 lines keeps rank 8 (coloop2.py, CHECKED).
  - Distinct h are independent mod T, so z-carriers ≤ 2 (root swaps on t, u).
- **slack 2, d ≥ 1:**
  - The DP gives slack ≥ 3 for d ≤ 4.
  - For d = 5..8, c66.py (my LP plus the mechanical Pencil and e=2 triple rules) reproduces SMALL2's list exactly. The only survivors are the SIX d = 8 multisets:
    - [7^5,6^5,1]
    - [7^6,6^4]
    - [7^8,5,4,1]
    - [7^8,5,5]
    - [7^8,6,3,1]
    - [7^8,6,4]
  - Every kill is a statement about the basis of T = (ρS)_{≤7}, so it is lift-level.

**Consequences.**
- **If the six die (by any T-level argument, e.g. SMALL2's Lemma-N extension), lift-level X_I ≥ 64+|I| holds for |I| ≤ 3.**
- In general: cost_w(S_X) ≥ 64 + Δ + max(0, |I| − ρ_0).
- E8 conditional: with the six dead, Δ = 2 ⇒ E8 ≥ 72, and Δ ≥ 3 ⇒ E8 ≥ 67.
