# Paper-side line counts per dimension: Lagrangian bound v ≤ T(2^k′+1) with exact ladder D4/D6/E7/E8 and no-gos scoped to windows h ≤ 13 (no κ claim)

> **Scope, stated first.** This package is about the **paper side only**: how many lines v a unit (a set of lines with a prescribed non-orthogonality pattern) can carry per ambient dimension T, as a function of the F2 rank 2k′ of its non-orthogonality adjacency, and what that implies for the *dense estimate* T·h of the decoder cost. It does **not** model compensation (helpers, hosting, side programs), and it contains **no κ claim, no new supplier, no window closed**. Every "cannot beat" statement is restricted to **bounded windows h ≤ 13** and is conditional on the repo's recorded break-even fit x\*(h) (RECORDED, not reproduced here). **#2222 shows that large-h units escape** these paper-side no-gos: its unit is a cubic polynomial-kernel unit with h = 49 and dense x ≈ .037 (its displayed 19,648-term factorization is a valid upper bound but is overcomplete, §9); nothing below says anything against it, and the credit for that observation belongs to #2222 (§9).
>
> **Statuses.** **PROVEN** (full proof in this README); **CONDITIONAL [verify]** (the proof here is complete, but the stated value or identification depends on a cited external result whose exact source statement has not been checked; the claim is conditional on that citation); **CHECKED** (recomputed by `verify.sh`, exact integer/`Fraction`/bit arithmetic); **RECORDED** (taken from a working card or another PR, not re-run here); **EXPLORATORY** (floating-point numerics, evidence not proof); **OPEN**.

## 0. Reading this package

```sh
bash research/line-system-saturation/verify.sh /fresh/output/dir     # from a checkout or `git archive`; Python >= 3.11, standard library only; single process, no SAT
```

Step 0 checks every file against `MANIFEST.sha256` and every pin of `SOURCES.json` (including the 14 stored vector files `data/best_kprime_*.json`) and stops with exit 1 on mismatch; six check scripts then print one `PASS`/`FAIL` line per assertion (88 PASS lines including step 0's two; well under five minutes on one core).

**Prior work this builds on (none of its files is copied; `lib/exact.py`, `lib/report.py`, `lib/units.py` are carried over from the author's own package of #2228).**
- **#446, #595, #1590, #2111** (cost model: a decoder is M = PQᵀ with an admissible pairing B; cost = Σ_j rank_F2 B[R_j, A_j]) and **#2228** (this author, open): the dense polar law for *odd-or-zero* units, B = Gram of u_t = (1, ℓ_t) under Ω = 1 ⊕ b, with labels from G mod 2. Theorem A below removes the odd-or-zero hypothesis; its proof is #2228 Theorem 3's argument with a different label form.
- **#2125** (this author, open): explicit pairings and the T² threshold; its RECORDED numerics (the doily realises at T = 4 and not 3; the 63-point Sp(6,2) system at T = 7 and not 6) are the first rows of §10.
- **#968** (merged): the 8/7 block-rank rule on E8 (the E8 instance of Theorem A's rank statement; checked in #2228 §4.2). **#2162** (this author, open): the T = 3 side and a 2-adic/tropical place bound; not touched here.
- **#2222** (1337isnot1337, open): the dyadic norm-six lattice decoder (P48p, 26,208,000 lines, chart dimension 49, fitting kernel ((x·y)³ − 4(x·y))/192, 19,648 terms, bill ≤ 962,752). **Credit:** it is the large-h unit that escapes the bounded-window statements below (§9).
- **#598** (Leech/Turyn polynomial-lattice kernels, merged) is the lineage #2222 credits for kernel units. **#895** (DaysSky, open): the full Barnes–Wall BW16 shell (2160 lines) has a 72-clique, hence window ≥ 72. This does not contradict Theorem C, which concerns the 144-line subset made of nine orthogonal frames (§7.1). **#620, #606** (ADE/lattice screens), **#2111**, **#897**: related screens, not compared line by line.
- Literature: Roberson, projective packing number α_p and α_p ≤ ϑ′ (Schrijver) [verify, §6]; Thas, W(2n−1,q) has no ovoid for n ≥ 3 [verify, §5.1]; Tiep–Zalesskii minimal degrees [verify, §7.4].

## 1. Setting and notation

A **line system** (unit) is a list of v pairwise distinct lines t = 1..v, spanned by vectors r_t ∈ ℝ^T (rational in every example here) with Gram matrix M_ts = r_t · r_s, M_tt ≠ 0. T is the dimension of their span (rank M).

- **Non-orthogonality adjacency** Ā ∈ F2^{v×v}: Ā_ts = 1 iff t ≠ s and M_ts ≠ 0. It is symmetric with zero diagonal, hence **alternating**; its rank is even, **rank_F2 Ā = 2k′**. For odd-or-zero systems (all products 0 or odd, even norms) Ā = G mod 2.
- **Symplectic labels.** An alternating matrix of rank 2k′ factors as Ā = LᵀbL with L ∈ F2^{2k′×v} of full row rank and b the standard symplectic form on V = F2^{2k′}, b(p,q) = Σ_i (p_{2i}q_{2i+1} + p_{2i+1}q_{2i}). (Proof: pick e_1, f_1 with Ā(e_1,f_1) = 1, replace every other vector w by w + Ā(w,f_1)e_1 + Ā(w,e_1)f_1, which is Ā-orthogonal to e_1, f_1, and recurse; the unit vector δ_t equals Σ_i[Ā(δ_t,f_i)e_i + Ā(δ_t,e_i)f_i] modulo the radical, so ℓ_t := (Ā(δ_t,f_i), Ā(δ_t,e_i))_i. `lib/lines.py:alt_labels` performs exactly this and asserts b(ℓ_t,ℓ_s) = Ā_ts on all pairs.) The columns of L span V (full row rank). Lines with equal rows of Ā have equal labels (if the rows agree, b(ℓ_t − ℓ_s, ℓ_u) = 0 for all u and the labels span V).
- **W(2k′−1,2)** is the symplectic polar space on V: N = 4^{k′} − 1 points (nonzero vectors), p, q **collinear** iff b(p,q) = 0 (p ≠ q). A **generator** (Lagrangian) is a maximal totally isotropic subspace; it has 2^{k′} − 1 points; their number is N_L = ∏_{i=1..k′}(2^i + 1) (3, 15, 135, 2295, 75735 for k′ = 1..5), and every point lies on N_L/(2^{k′}+1) of them (Sp(2k′,2) is transitive on points, and each generator has 2^{k′}−1 points: count incident pairs).
- **Admissible pairing, window, dense estimate** (the model of #446/#595/#1590, as restated in #2228 §1): B ∈ F2^{v×v} with B_tt = 1 and B_ts = 1 (t ≠ s) only where M_ts = 0. The **dense pairing** is B = J + Ā (J all ones); its rank is the **window** h. For the coordinate decoder (P = Q = coordinates of the r_t in an orthonormal basis, T terms, supports R_j = A_j) every term has cost rank_F2 B[R_j,A_j] ≤ rank B = h, so the **dense estimate is cost ≤ T·h**, i.e. **x := hT/v** per line (the screen proxy of #620's `ade_screen.py`, also used by #895). The bound is on the *dense* pairing; sparser admissible B are not considered (OPEN, §11).
- **Saturation** σ := v / (T(2^{k′}+1)) ≤ 1 (Theorem B). **Class sizes**: for a generator L, c_L := number of lines with label in L.
- **Break-even fit x\*(h)** := .5385 − .01495 (h − 9): the dense ratio at which a unit ties the recorded P104 COPY56 construction; a fit from the author's working cards (BERTHA/fx), **RECORDED**, valid for h ≲ 17. Every row labelled "needed" below is conditional on it; the theorems are not.

## 2. Results at a glance

| # | statement | status | where |
|---|---|---|---|
| A | For **every** line system: B = J + Ā = Ω(u_t,u_s) with u_t = (1,ℓ_t); h = rank(J+Ā) = 2k′+1 if 1 ∉ col Ā, = 2k′ if 1 ∈ col Ā | **PROVEN**; CHECKED on D4/D5/D6/E6/E7/E8 | §3 |
| B | v ≤ T(2^{k′}+1); v ≤ T·2^{k′} on the even window; equality iff (no line orthogonal to all others, i.e. no label 0) every generator class is a full basis | **PROVEN**; ladder CHECKED | §4 |
| – | Saturation ladder: D4, D6, E7 attain 100%; E8 attains 15/17; the other 13 saved systems are far below | **CHECKED** | §8 |
| A′ | Same bound for non-Gram units M = PQᵀ (any field of characteristic 0, overcomplete included); best v/T = weighted idempotent packing number of the collinearity graph of W(2k′−1,2); saturation ⇔ "projective ovoid" | **PROVEN** | §5.1 |
| D | Descent: a saturated W(2k′−1,2) system gives a saturated W(2k′−3,2) system in dimension T − m_p; quantitative form σ_{k′} ≤ s_{k′−1} + (1−s_{k′−1})Σm_p²/(vT); saturation at any k′ ≥ 4 forces a saturated k′ = 4 system | **PROVEN**; E7→D6→D4, E8→E7 CHECKED | §5.2 |
| 2P | The two-point (Schrijver-ϑ′-type) program on W(2k′−1,2) has value exactly 2^{k′}+1 | **PROVEN**; feasible point CHECKED k′ = 2..5 | §6 |
| C | Unions of F ≥ 2 pairwise unbiased orthonormal frames have F ≤ 2k′+1 and dense x = 1; 2k′+1 generic rational frames attain it; every admissible B has window ≥ F | **PROVEN**; generic frames CHECKED | §7.1 |
| D(b) | Real m-fold blow-up multiplies T and v by m and keeps k′, σ | **PROVEN**; E7×2 CHECKED | §7.2 |
| E | Norm-2 systems with products in {0,±1}: v/T ≤ max(15, 2k′+1) | **PROVEN** (uses the ADE classification of root systems) | §7.3 |
| F | A symmetry group inducing a non-abelian simple S faithfully on the lines forces T ≥ d_proj(S); for Sp(10,2): 155 | proof **PROVEN**; smallest nontrivial degree 155 of Sp(10,2) **CHECKED** (GAP, ATLAS table, `checks/gap/`); equality with d_proj **CONDITIONAL [verify]** on Sp(10,2) having trivial Schur multiplier | §7.4 |
| G | Uniform-angle saturated systems: λ² = 2^{k′−1}m must be a perfect square (m = 1: k′ odd, cos = 2^{−(k′−1)/2}); k′ = 4 needs m ∈ {2, 8, 18, …} | **PROVEN**; arithmetic CHECKED | §7.5 |
| – | D16⁺ (roots + spinor code): at most 240 + 317 = 557 lines, against ≈ 650 needed | **CHECKED** (exact Delsarte dual certificate); "needed" conditional on x\* (RECORDED) | §8.2 |
| – | #2222: cubic-kernel unit, h = 49, x ≈ .037 (19,648 terms an upper bound; rank ≤ 19,600) | **RECORDED** from #2222, not re-run; rank remark **PROVEN** | §9 |
| – | Relaxed realisability numerics (W4, W5 fail at the break-even T) | **EXPLORATORY** | §10 |
| – | 510-vertex signing S² = 60S + 256I; level-2/three-point bounds; realisability of W4; Pauli-frame ansatz for W5 in ℝ³¹ | **OPEN** | §11 |

## 3. Theorem A (polar law for every line system) — PROVEN

**Theorem A.** Let Ā have rank 2k′ with labels ℓ_t ∈ V as in §1, u_t := (1, ℓ_t) ∈ F2 ⊕ V, Ω := 1 ⊕ b. Then B := J + Ā is admissible, B_ts = Ω(u_t, u_s) for **all** t, s, and
  h := rank_F2 B = 2k′ + 1 if the all-ones vector 1 ∉ col(Ā), and 2k′ if 1 ∈ col(Ā).
Moreover 1 ∈ col(Ā) iff there is w ∈ V with b(ℓ_t, w) = 1 for all t.

*Proof.* Admissible: B_ts = 1 for t ≠ s means Ā_ts = 0, i.e. M_ts = 0; B_tt = 1. Gram form: for t ≠ s, Ω(u_t,u_s) = 1 + b(ℓ_t,ℓ_s) = 1 + Ā_ts = B_ts; and Ω(u_t,u_t) = 1 + b(ℓ_t,ℓ_t) = 1 = B_tt (b alternating). Rank: B = Ā + 11ᵀ. Its kernel is {x : Āx = 1(1ᵀx)}. If 1ᵀx = 0 this says Āx = 0; if 1ᵀx = 1 it says Āx = 1. Since Ā is symmetric, col(Ā) = (ker Ā)^⊥. (i) If 1 ∉ col(Ā), then Āx = 1 has no solution, and some x ∈ ker Ā has 1ᵀx = 1 (else 1 ∈ (ker Ā)^⊥), so ker B = ker Ā ∩ 1^⊥ has codimension 1 in ker Ā and rank B = 2k′ + 1. (ii) If 1 ∈ col(Ā) then ker Ā ⊆ 1^⊥ and Āx = 1 with 1ᵀx = 1 would need xᵀĀx = 1ᵀx = 1, impossible for an alternating form; so ker B = ker Ā and rank B = 2k′. Last claim: (Āz)_t = (LᵀbLz)_t = b(ℓ_t, Lz), so 1 = Āz gives w := Lz with b(ℓ_t, w) = 1 for all t; conversely L is onto V, so every w equals Lz for some z, and then Āz = 1. ∎

**CHECKED (c1).** For D4, D5, D6, E6, E7, E8 (v = 12, 20, 30, 36, 63, 120; T = 4, 5, 6, 6, 7, 8): Ā equals G mod 2 off the diagonal; rank_F2 Ā = 2, 4, 4, 6, 6, 8 (k′ = 1, 2, 2, 3, 3, 4); the symplectic factorisation is verified on all v² pairs; B = Ω(u_t,u_s) on all v² pairs; 1 ∉ col(Ā) and h = 2k′+1 in all six cases.

**Remarks.** (1) *Odd-or-zero is the special case Ā ≡ G mod 2.* For lattice shells with even non-zero products, #2228's "dense rank B" was already rank(J + Ā); only the *label form* G mod 2 was the wrong invariant. (2) *Cliques:* c pairwise non-orthogonal lines give Ā|_c = J − I with F2 rank c or c − 1, so c ≤ 2k′ + 1 ≤ h + 1, and in fact every admissible B is the identity on a clique, so *every* admissible pairing has window ≥ ω(Γ) (Γ the non-orthogonality graph; #446 clique bound, #895). (3) Integrality is not used: a rational realisation of the pattern is all that the decoder needs.

## 4. Theorem B (Lagrangian bound) and the dense threshold

**Theorem B — PROVEN.** For any line system with rank_F2 Ā = 2k′ (equivalently any M = PQᵀ of rank T with a symmetric alternating C dominating the support, §5.1):
 (i) v ≤ T(2^{k′} + 1); (ii) if 1 ∈ col(Ā) (even window h = 2k′) then v ≤ T·2^{k′}.
Hence x = hT/v ≥ h / (2^{⌊h/2⌋} + [h odd]).

*Proof.* Let L be a generator and C_L the lines with label in L ∪ {0}. For t ≠ s in C_L, Ā_ts = b(ℓ_t,ℓ_s) = 0 (b vanishes on L, also for equal labels), so the lines of C_L are pairwise orthogonal; non-zero pairwise orthogonal vectors are independent, so |C_L| ≤ T. Write n_p for the number of lines with label p ≠ 0 and n_0 for those with label 0 (n_0 = 0 if 1 ∈ col Ā). Sum |C_L| ≤ T over all N_L generators: each non-zero point lies on N_L/(2^{k′}+1) generators, so N_L n_0 + (N_L/(2^{k′}+1))(v − n_0) ≤ N_L T, i.e. v ≤ T(2^{k′}+1) − n_0 2^{k′} ≤ T(2^{k′}+1). For (ii) choose w with b(p,w) = 1 for all occupied labels p. No generator through such a p contains w (b(p,w) ≠ 0), so every generator meeting the occupied labels lies in 𝓛_w := {L : w ∉ L}, and |𝓛_w| = N_L − N_L/(2^{k′}+1) = N_L 2^{k′}/(2^{k′}+1). Summing |C_L| ≤ T over 𝓛_w, each occupied point being counted N_L/(2^{k′}+1) times: v N_L/(2^{k′}+1) ≤ T N_L 2^{k′}/(2^{k′}+1). ∎

**Equality (PROVEN).** (i) with n_0 = 0 is an equality iff every generator class has exactly T lines, i.e. is an orthogonal basis of the span. Then with û_t = r_t/|r_t|, Σ_t û_t û_tᵀ = (2^{k′}+1)·Id_T (each line lies in N_L/(2^{k′}+1) generators and each class contributes Id_T), a tight frame; the normalised Gram matrix has exactly the eigenvalues 0 and 2^{k′}+1.

**Reduction (PROVEN, trivial).** A graph of F2 rank 2k′ is the blow-up (twins become independent sets) of an induced subgraph of the symplectic graph on W(2k′−1,2) plus isolated vertices. So v_max(T,k′) is the maximum of Σ_p m_p over label multisets (m_p) on W(2k′−1,2) whose blow-up has an exact-pattern realisation in rank ≤ T.

**CHECKED (c1).** Over all generators: D4 (3 generators), D6 (15), E7 (135): every class has exactly T lines, hence v = T(2^{k′}+1) = 12, 30, 63 and F = Σ r rᵀ/|r|² = (v/T)·(projection onto the span) with v/T = 3, 5, 9. E8 (2295 generators): every class has 0 or 8 lines (2025 full, 270 empty), v = 120 < 8·17 = 136, σ = 15/17. D5 and E6 have all classes of size 4 and are not saturated (σ = 4/5, 2/3).

**Thresholds (CHECKED arithmetic, conditional on the RECORDED x\*).** Needed v/T = h/x\*(h) and the fraction of the Theorem B cap it represents:

| h | k′ | x\*(h) | needed v/T | cap 2^{⌊h/2⌋}+[h odd] | needed saturation |
|---|---|---|---|---|---|
| 9 | 4 | .5385 | 16.71 | 17 | 98.3% |
| 10 (even window) | 5 | .5235 | 19.10 | 32 | 59.7% |
| 11 | 5 | .5086 | 21.63 | 33 | 65.5% |
| 12 (even window) | 6 | .4936 | 24.31 | 64 | 38.0% |
| 13 | 6 | .4787 | 27.16 | 65 | 41.8% |

Theorem B therefore does **not** rule out beating the recorded P104 break-even at h = 10..13 (the cap is far above the need). It only says how much of the cap must be filled.

## 5. Non-Gram units, idempotents and descent

### 5.1 Theorem A′ (what has to be realised) — PROVEN

Let K be a field of characteristic 0 and M = PQᵀ with P, Q ∈ K^{v×T}, M_tt ≠ 0. Let C ∈ F2^{v×v} be symmetric alternating with C_ts = 1 whenever M_ts ≠ 0 or M_st ≠ 0 (t ≠ s); write C = LᵀbL (rank 2k′) as in §1. Then:
 (i) B := J + C is admissible for M and Theorem A holds for it (window ≤ 2k′+1); every block of B has rank ≤ h, so the coordinate-type decoder costs ≤ (number of terms)·h.
 (ii) Theorem B holds with T replaced by rank M: v ≤ (rank M)(2^{k′}+1), and v ≤ (rank M)2^{k′} on the even window. (The classes C_L give diagonal submatrices M[C_L,C_L] with non-zero diagonal; a diagonal matrix with non-zero diagonal has rank |C_L| ≤ rank M.) Overcompleteness (more terms than rank M) never helps this count; it can help only through per-term costs below h, which is the non-dense question of §11.
 (iii) For a label p let C_p be its class and E_p := Q_{C_p}ᵀ D_p^{−1} P_{C_p}, D_p := M[C_p,C_p] (diagonal, invertible, because C_ts = 0 inside a class forces M_ts = M_st = 0). Then E_p is an idempotent of rank m_p := |C_p| (E_p² = Qᵀ D⁻¹(PQᵀ)D⁻¹P = E_p), and E_pE_q = 0 whenever b(p,q) = 0, p ≠ q (since M[C_p,C_q] = 0). Conversely, idempotents E_p = Y_pX_p (rank factorisations, X_pY_p = I) with E_pE_q = 0 for collinear p ≠ q give a unit (rows of X_p as P, columns of Y_p as Q; X_pY_q = 0 because Y_p is injective and X_q surjective). Hence
 **v_max(T,k′)/T = sup Σ_p rank E_p / T over idempotent families on K^T with E_pE_q = 0 on distinct collinear pairs of W(2k′−1,2)**;
for Gram units the E_p are orthogonal projections, and this coincides with the **projective packing number** α_p of the collinearity graph (Roberson; Mančinska–Roberson), CONDITIONAL [verify] on their definition matching ours; the bound itself does not use the identification. **Saturation** (v = T(2^{k′}+1)) holds iff Σ_{p∈L} E_p = Id for every generator L, a **projective ovoid** (classical ovoids of W(2n−1,q) do not exist for n ≥ 3 [verify: Thas, found only in survey statements]; E7 is a projective one at n = 3 with all ranks 1).
(iv) Exactness of the zero pattern is irrelevant to the *upper* bound: a realisation with additional orthogonalities is still a valid unit for the label form of the pattern it satisfies, provided its lines are non-zero and pairwise distinct (coincident lines must be merged).

*Proof of (i), (ii), (iv).* As in Theorems A and B, using only that B_ts = 1 (t ≠ s) forces C_ts = 0 and hence M_ts = M_st = 0. ∎

### 5.2 Descent — PROVEN

Work with idempotent families (E_p) on K^T (families on W(2k′−1,2), labels allowed to carry rank 0), saturated: Σ_{q∈L} E_q = Id for every generator L.

**Proposition D1 (exact).** Fix a label p with m_p > 0. For every generator L ∋ p, Σ_{q∈L∖{p}} E_q = Id − E_p, so all E_q with q ∈ p^⊥∖{p} live on U := im(Id − E_p), of dimension T − m_p (for projections: U = (class of p)^⊥). Put E_{[q]} := E_q + E_{q+p} for the classes [q] ∈ p^⊥/⟨p⟩ ≅ W(2k′−3,2) (q ≠ p, q + p ≠ p). Then (E_{[q]}) is a **saturated** W(2k′−3,2) family on U with ranks m_q + m_{q+p}.
*Proof.* b(q,q+p) = b(q,p) = 0 and q ≠ q+p, so E_qE_{q+p} = 0 and E_{[q]} is an idempotent of rank m_q + m_{q+p}. If [q] ≠ [r] are equal-or-collinear in the quotient, then b(q,r) = 0 and all four labels q, q+p, r, r+p are pairwise distinct and pairwise collinear (b(q,r+p) = b(q,r) + b(q,p) = 0), so E_{[q]}E_{[r]} = 0. A generator L′ of the quotient lifts uniquely to a generator L ∋ p; L ∖ {0,p} is the disjoint union of the pairs {q, q+p} over [q] ∈ L′, so Σ_{[q]∈L′} E_{[q]} = Σ_{q∈L∖p} E_q = Id − E_p = Id_U. ∎

**Corollary D2.** A saturated system at level k′ yields saturated systems at levels k′−1, …, 1. Hence **saturation at any k′ ≥ 4 forces a saturated k′ = 4 system** (for general multiplicities the levels 1, 2, 3 are realised by D4, D6, E7 and their real blow-ups, §7.2).

**CHECKED (c4).** E7 at a label p (m_p = 1) → the 30 lines with labels in p^⊥ ∖ {p}: orthogonal to p, span T − 1 = 6, k′ = 2, twin classes = {q, q+p} of size 2, every generator class a full basis (the D6 system); D6 at p (m_p = 2) → 12 lines in T = 4, k′ = 1, multiplicity 4 (D4); E8 at p → 63 lines in T = 7, k′ = 3, saturated (E7).

**Proposition D3 (quantitative).** Let s_{k′−1} be the supremum of σ over all families (Gram families, resp. idempotent families; the inequality holds in either class) on W(2k′−3,2) (any T, any multiplicities, labels allowed to be empty). For a family on W(2k′−1,2) with no zero labels and saturation σ: **σ ≤ s_{k′−1} + (1 − s_{k′−1}) · Σ_p m_p² / (vT).**
*Proof.* Let A_p := average of c_L over the generators L ∋ p. The derived system at p has class sizes c_L − m_p (L ∋ p, bijectively with generators of the quotient) in dimension T − m_p, so its saturation (A_p − m_p)/(T − m_p) ≤ s := s_{k′−1}, i.e. A_p ≤ sT + (1−s)m_p. Also Σ_p m_pA_p = ((2^{k′}+1)/N_L) Σ_L c_L² ≥ (2^{k′}+1)(avg c_L)² = vσT (Cauchy–Schwarz, avg c_L = v/(2^{k′}+1) = σT). Combine: vσT ≤ Σ m_p(sT + (1−s)m_p) = vsT + (1−s)Σm_p². ∎ (E8 CHECKED: A_p ≤ 8 for all occupied labels, Σ m_pA_p = 960 ≥ vσT = 14400/17.) It is an inheritance law: it turns any bound on s_4 into bounds at every k′ ≥ 5; it does not beat the thresholds of §4 by itself, since s_4 ≥ 15/17.

## 6. Two-point relaxations are exhausted (PROVEN; feasible point CHECKED)

Take the program P2 for a Gram unit with X_pq := tr(P_pP_q)/T (P_p the orthogonal projection onto the span of the lines of label p) and x_p := m_p/T: maximise Σ_p x_p subject to X_pp = x_p, X_pq = 0 for distinct collinear p, q, X ≥ 0 entrywise (tr P_pP_q = ‖P_pP_q‖_F² ≥ 0), and [[1, xᵀ],[x, X]] ⪰ 0. (This is the Schrijver-ϑ′-type program of the packing problem; α_p ≤ ϑ′ is Roberson's theorem [verify: confirmed only through the introduction of arXiv 2609.20678, not read in the original].)

**Proposition 2P — PROVEN.** The value of P2 is exactly 2^{k′} + 1.
*Proof.* *Invariance:* Sp(2k′,2) acts on points with exactly two orbits on ordered pairs of distinct points (collinear / non-collinear; Witt), the constraints are convex and invariant and the objective is linear, so averaging gives an optimal point with x_p ≡ x and X = xI + yA, A the adjacency of the non-collinearity graph (the collinear orbital has X = 0). *The graph is strongly regular* with degree d = 2^{2k′−1} and λ = μ = 2^{2k′−2}, so A² = (d − μ)I + μJ, A·1 = d·1, and the spectrum of A lies in {d, ±2^{k′−1}} (CHECKED for every pair of points, k′ = 2..5). On 1^⊥ the matrix X has eigenvalues x ± y2^{k′−1}, so PSD forces y ≤ x/2^{k′−1}. The lifted matrix is PSD iff X − x²J ⪰ 0 (Schur complement); on the all-ones vector this reads x + yd − x²N ≥ 0 (N = 4^{k′}−1). Since y ≥ 0, the best choice is y = x/2^{k′−1}, giving x(1 + 2^{k′}) ≥ x²N, i.e. x ≤ 1/(2^{k′}−1), and the objective is Nx ≤ (4^{k′}−1)/(2^{k′}−1) = 2^{k′}+1. The point x = 1/(2^{k′}−1), y = x/2^{k′−1} is feasible (all constraints with equality on the extremal directions), so the value is 2^{k′}+1. ∎

**CHECKED (c3), k′ = 2..5:** strong regularity on all point pairs; eigenvalues of X\* = xI + yA exactly {(2^{k′}+1)x, 2x, 0}; Schur complement eigenvalue 0 on 1; 0 < y ≤ x; objective 2^{k′}+1; and the **generator inequalities** Σ_{q∈L} X\*_pq ≤ X\*_pp hold **with equality** (for p ∉ L exactly 2^{k′−1} points of L are non-collinear to p because b(p,·)|_L is a non-zero functional; for p ∈ L the sum is x), exhaustively over all generators for k′ ≤ 4 and for 60 seeded random generators at k′ = 5.

**Consequence.** Every convex program built from the two-point data (Hilbert–Schmidt Gram data of {Id, P_p}) that contains the constraints of P2 and is satisfied by X\* (this includes adding the generator inequalities Σ_{q∈L} X_pq ≤ X_pp and Σ_{q∈L} x_q ≤ 1) has value exactly 2^{k′}+1. Improving on Theorem B by relaxation therefore needs words of length ≥ 3 (tr P_pP_qP_r, tr (P_pP_q)², i.e. level-2 moment matrices) or arithmetic input (§11).

## 7. Constructions and bounded-class no-gos

### 7.1 Theorem C (unions of unbiased frames) — PROVEN

Let the system be a union of F ≥ 2 orthogonal frames (each a full orthogonal basis of the T-dimensional span), any two lines from different frames non-orthogonal. Then **F ≤ 2k′ + 1, h = F, and x = hT/v = 1.** Every admissible pairing (dense or not) has window ≥ F (clique argument: #446 clique bound, #895). Conversely **2k′+1 generic rational orthonormal frames of ℚ^T realise v = (2k′+1)T, x = 1** for every T.
*Proof.* Inside a frame Ā = 0; across frames Ā = 1. So Ā = (J_F − I_F) ⊗ J_T, whose F2 rank is rank(J_F − I_F) = F − 1 (F odd) or F (F even); thus F − 1 ≤ 2k′, and since the rank is even, F ≤ 2k′+1. B = J + Ā is 1 inside a frame and 0 across: B = I_F ⊗ J_T, rank F = h, and x = F T/(F T) = 1. One line per frame is a clique, and any admissible B is the identity on a clique (B_ts = 1 only where M_ts = 0), so its rank is ≥ F. For the converse take Cayley transforms of random rational skew matrices; the cross products are non-zero generically. ∎
**CHECKED (c1):** generic frames for (T, F) = (3,3), (4,3), (4,5), (5,5), (3,7): all cross products non-zero, k′ = 1, 1, 2, 2, 3, window F, x = 1, saturation 1, 1, 1, 1, 7/9. So **Theorem C explains why Kerdock/mutually unbiased-type constructions cannot reach x < 1**; e.g. the 144-line, nine-frame subset of BW16 (k′ = 4, F = 9 = 2k′+1) is RECORDED from the author's cards as consistent with it. (The full BW16 shell, 2160 lines, is not a union of unbiased frames and has a 72-clique by #895.)

### 7.2 Theorem D(b) (real blow-up) — PROVEN

If a line system has vectors a_ℓ, replace each a_ℓ by the m vectors a_ℓ ⊗ h_{ℓ,i} (i = 1..m), where {h_{ℓ,i}}_i is an orthonormal basis of ℝ^m chosen for each ℓ so that all cross products h_{ℓ,i}·h_{ℓ′,j} (ℓ ≠ ℓ′) are non-zero (generic). Then products are (a_ℓ·a_ℓ′)(h_{ℓ,i}·h_{ℓ′,j}): twins are orthogonal, and Ā_new = Ā ⊗ J_m. So T → mT, v → mv, rank_F2 Ā (hence k′, h) and σ are unchanged. **CHECKED (c1):** E7 with m = 2: 126 lines in ℚ^14, pattern = Ā(E7) ⊗ J_2 on all 7875 pairs, k′ = 3, h = 7, v/T = 9. (The D4/D6 phenomenon that multiplicity can do *better* than tensoring, e.g. D4 with m = 4 in T = 4 against 8 for the tensor product, is seen only at k′ ≤ 2 in every case known; §10.)

### 7.3 Theorem E (norm-2 systems) — PROVEN (uses the ADE classification)

**Theorem E.** If every line has norm 2 and all products lie in {0, ±1}, then **v/T ≤ max(15, 2k′+1)**, where 2k′ = rank_F2 Ā (here Ā = G mod 2 off the diagonal). In particular such systems cannot reach the needed v/T of §4 for k′ ≥ 5 (needed 19.1 / 21.6 at h = 10 / 11 against max(15, 11) = 15 at k′ = 5). For full root systems this is #620's ADE screen (only E8 viable); Theorem E extends it to every norm-2 subsystem with products in {0, ±1}.

*Proof.* Let Λ be the lattice generated by the lines; it is even (norms of integer combinations are even because the generators have norm 2 and integral products), so the norm-2 vectors R of Λ form a simply-laced root system (closed under reflections) of rank T = dim span (the lines are in R). Split R into irreducible components R_1, …, R_m, orthogonal and with ranks T_i, ΣT_i = T. Each line lies in one component (every root of R lies in exactly one irreducible component). Let S_i be the lines in R_i. Then G is block-diagonal, v = Σ|S_i|, rank_F2 Ā = Σ rank_F2 Ā_i (so k′ ≥ k′_i), and since dim span S = T = Σ rank R_i, each S_i spans span R_i, i.e. T(S_i) = T_i. As v/T is a weighted average of the |S_i|/T_i, it suffices to prove |S_i|/T_i ≤ max(15, 2k′_i+1) for each irreducible component. By classification R_i is of type A, D, E6, E7 or E8.
 • E6, E7, E8: |S_i| ≤ 36, 63, 120 lines and T_i = 6, 7, 8: ratios ≤ 6, 9, 15.
 • **A_n.** Roots e_a − e_b on c = n + 1 coordinates; S_i is the edge set of a graph H on c vertices (distinct lines = distinct edges), and T_i = n forces H connected. With N the c × |S_i| unsigned incidence matrix, G mod 2 = NᵀN off the diagonal and also on it (the diagonal 2 ≡ 0), because |e ∩ f| = number of common vertices. Over F2, col(N) is the even-weight space (dimension c − 1 for connected H) and the form xᵀy on it has radical ⟨1⟩ ∩ (even weight) = ⟨1⟩ if c is even and 0 if c is odd; hence rank_F2 Ā_i = c − 1 − [c even] ≥ c − 2, i.e. c ≤ 2k′_i + 2. Then |S_i|/T_i ≤ (c(c−1)/2)/(c−1) = c/2 ≤ k′_i + 1 ≤ 2k′_i + 1.
 • **D_n.** Roots ±e_a ± e_b on n coordinates. Split S_i by the connected components of its support graph (coordinates joined by lines); different support components are orthogonal, so we may treat one with c vertices. Edges are signed, parallel edges at most 2 (e_a − e_b and e_a + e_b, which are *orthogonal*). Again G mod 2 = NᵀN (sharing exactly one coordinate gives ±1, sharing both gives 0 or ±2 ≡ 0), the support is connected, so rank_F2 Ā = c − 1 − [c even] and c ≤ 2k′+2 as above. The rank of the component is c if the signed graph is unbalanced and c − 1 if balanced. If balanced, it is switching-equivalent to an A-type edge set (no parallel pairs), ratio ≤ c/2. If unbalanced, |S| ≤ c(c−1) and T = c, ratio ≤ c − 1 ≤ 2k′+1.
Combining, v/T ≤ max over components of max(15, 2k′_i+1) ≤ max(15, 2k′+1). ∎
**CHECKED (c2):** the identity Ā = NᵀN mod 2, the rank formula c − 1 − [c even] for connected supports, T ∈ {c−1, c}, and the final inequality on all subsets of the A_c lines (c ≤ 6) and D_c lines (c ≤ 4) and on 1500 seeded random subsets for A_7 and D_5..D_7; E6/E7/E8 ratios 6, 9, 15.

### 7.4 Theorem F (symmetric realisations) — proof PROVEN; degrees CHECKED in GAP; Schur-multiplier input CONDITIONAL [verify]

**Theorem F.** Let H ≤ O(T) be a finite group permuting the lines of a system, let N ⊲ H be the subgroup acting trivially on the set of lines (every element of N acts by ±1 on each line), and suppose H/N ≅ S for a non-abelian finite simple group S acting non-trivially on the lines. Then **T ≥ d_proj(S)**, where d_proj(S) is the smallest degree of a non-scalar complex projective representation of S.
*Proof.* H is finite and faithful on ℂ^T. H is not solvable (S is a non-abelian simple quotient), so some irreducible constituent W of ℂ^T has non-solvable image of H (else H embeds in a product of solvable groups). N is abelian: each n ∈ N acts on every spanning vector r_t by a sign, so n ↦ (signs) embeds N in (ℤ/2)^v and N is diagonalisable on ℂ^T; so W|_N = ⊕_χ W_χ over characters χ of N, and by Clifford's theorem H permutes the W_χ transitively. *If there is one χ*, N acts by scalars on W, so W is a projective representation of H/N = S; it is non-scalar (otherwise the image of H would be abelian), hence dim W ≥ d_proj(S). *If there are t ≥ 2 characters*, S acts transitively on a set of size t, non-trivially, hence faithfully (S simple), with point stabiliser a proper subgroup of index t, so t is the index of a proper subgroup. Since a transitive permutation action of degree t yields a non-trivial linear representation of degree ≤ t − 1, dim W ≥ t > d_proj(S); hence T ≥ d_proj(S). ∎
**Application (multiplicity one).** A system with one line per label, a group inducing Sp(10,2) on its lines (so on all 1023 labels), has T ≥ d_proj(Sp(10,2)) = 155. The formula d_proj(Sp(2n,2)) = (2^n − 1)(2^{n−1} − 1)/3 (n = 3, 4, 5: 7, 35, 155; ATLAS degrees; Sp(2n,2) has trivial Schur multiplier for n ≥ 4) is the cited value [verify: the Tiep–Zalesskii 1996 formula (q^n−1)(q^n−q)/(2(q+1)) at q = 2; I could not retrieve the original statement, only that Tiep–Zalesskii determine these minimal degrees]; only the arithmetic is checked (c2). (The smallest index of a proper subgroup, m(Sp(2n,2)) = 2^{n−1}(2^n − 1), is a permutation-degree result of Cooperstein 1978 and is not needed.) **Checked (c8, GAP 4.13 + CTblLib ATLAS tables, `checks/gap/sp2n2_degrees.g`, recorded output beside it):** the smallest nontrivial ordinary character degrees of Sp(6,2), Sp(8,2), Sp(10,2) are 7, 35, 155. For n ≥ 4 these are the projective degrees provided the Schur multiplier is trivial, which we cite (Steinberg; ATLAS) and did not compute: GAP's multiplier computation for Sp(10,2) did not finish in 20 min. So T ≥ 155 is CONDITIONAL [verify] on that citation only. With it, v/T ≤ 1023/155 = 6.6 at k′ = 5, far below the needed 19.1–21.6; the E7 case is consistent with the formula (Sp(6,2), T = 7). *Not claimed:* the original card also listed lower bounds 120 / 119 for Ω^±(10,2); Theorem 1.3 of Nguyen (arXiv:0910.4885, read through its ar5iv rendering) lists the smallest non-trivial degree of Ω^−_10(2) as (2^5+1)(2^4−2)/3 = 154 and excludes Ω^+_10(2), so **those two numbers are dropped**. *Not covered:* multiplicity m ≥ 2, where N may be non-abelian (Clifford groups act irreducibly with a solvable N) — the proof above needs N abelian.

### 7.5 Theorem G (uniform-angle saturated systems) — PROVEN

Let a **saturated** system on W(2k′−1,2) have uniform multiplicity m (all N labels with exactly m lines), unit vectors, and constant |cos| = α on all non-orthogonal pairs. Write the normalised Gram matrix Ĝ = I + αS with S an integer-signed adjacency matrix of the blown-up non-collinearity graph (twins orthogonal), and λ := 1/α. Then λ² = 2^{k′−1} m, and λ is rational. So **m = 1 requires k′ odd (α = 2^{−(k′−1)/2}; k′ = 1 gives the degenerate α = 1); for k′ = 4, 2m must be a perfect square (m = 2, 8, 18, 32, 50, …)**; and T = m(2^{k′} − 1).
*Proof.* Saturation gives Ĝ² = (2^{k′}+1)Ĝ (§4, equality case), i.e. S² = (2^{k′}−1)λS + 2^{k′}λ²I. The diagonal of S² is the degree of the graph, 2^{2k′−1}m, so 2^{k′}λ² = 2^{2k′−1}m. S has eigenvalue 2^{k′}λ (multiplicity T) and −λ (multiplicity Nm − T). If λ were irrational (λ² = 2^{k′−1}m is an integer), the integer matrix S would have the Galois conjugate +λ of its eigenvalue −λ as an eigenvalue, but its only eigenvalues are −λ and 2^{k′}λ. So λ is an integer. The multiplicities follow from tr S = 0 and tr Ĝ = Nm: T(2^{k′}+1) = Nm. ∎
**CHECKED (c6):** the table of (k′, m, λ) with λ² = 2^{k′−1}m a square for k′ ≤ 9, m ≤ 50 (m = 1 exactly for odd k′; k′ = 4 needs m ∈ {2, 8, 18, 32, 50}); D4 (k′ = 1, m = 4), D6 (2, 2), E7 (3, 1) are uniform with |cos| = 1/2 = 1/λ; the common-neighbour counts of the blown-up symplectic graphs: for (k′, m) = (4, 2) [510 vertices, λ = 4] S² = 60S + 256I, degree 256, adjacent pairs have 128 common neighbours (a signing would need signed sum ±60, i.e. 94 agree / 34 disagree), non-adjacent distinct labels 128 (signed sum 0), twins 256 (signed sum 0); for (5, 1) [1023 vertices, λ = 4] S² = 124S + 512I, adjacent pairs 256 common neighbours (a signing would need 190 / 66). *Erratum to the source card:* it wrote the uniform angle as 2^{−(k′+1)/2}; the correct value is 2^{−(k′−1)/2} (E7: 1/2).

## 8. The exact ladder and the construction table

### 8.1 CHECKED
`checks/c5_l1cons.py` re-verifies, in exact integer arithmetic, the 14 vector files `data/best_kprime_*.json` (lines distinct up to sign, non-zero norms, every pairwise product 0 or odd, exact Q-rank T, rank_F2 Ā, window, saturation as a fraction). Window h is the actual rank_F2(J+Ā).

| k′ | system | T | v | v/T | σ | h | dense x = hT/v | x\*(h) (RECORDED fit) |
|---|---|---|---|---|---|---|---|---|
| 1 | D4 roots (c1) | 4 | 12 | 3 | 1 | 3 | 1.000 | – |
| 2 | D6 roots (c1) | 6 | 30 | 5 | 1 | 5 | 1.000 | – |
| 3 | E7 roots (c1) | 7 | 63 | 9 | 1 | 7 | .778 | – |
| 3 | Z8 (56 lines in ℤ^8) | 8 | 56 | 7 | 7/9 | 7 | 1.000 | .568 |
| 4 | E8 roots (= A_ham, 120) | 8 | 120 | 15 | 15/17 = .882 | 9 | .600 | .5385 |
| 5 | E8 + A3, norms 6 | 11 | 140 | 12.7 | .386 | 11 | .864 | .509 |
| 6 | E8 + D5, norms 4 | 13 | 166 | 12.8 | .196 | 13 | 1.018 | .479 |
| 7 | Z16a (240 lines) | 16 | 240 | 15 | .116 | 15 | 1.000 | .449 |
| 8 | D16⁺: roots + 256 spinor lines | 16 | 496 | 31 | .121 | 17 | .548 | .419 |
| 9 | Z20m | 20 | 55 | 2.75 | .005 | 19 | 6.909 | .389 |
| 12 | D24⁺ roots + 176 spinors | 24 | 728 | 30.3 | .007 | 25 | .824 | .299 |
| 15 | Z32RM1 | 32 | 992 | 31 | .0009 | 31 | 1.000 | .210 |
| 16 | four orthogonal copies of E8 (480 lines) | 32 | 480 | 15 | 2·10⁻⁴ | 33 | 2.200 | .180 |
| 20 | five orthogonal copies of E8 | 40 | 600 | 15 | 1.4·10⁻⁵ | 41 | 2.733 | .060 |
| 25 | E8⊗E8 frame-partition (960 lines) | 64 | 960 | 15 | 4.5·10⁻⁷ | **50** (even window) | 3.333 | < 0 |
| 32 | E8⊗E8 pool, local-search subset (666 lines) | 64 | 666 | 10.4 | 2.4·10⁻⁹ | 65 | 6.246 | < 0 |

(k′ = 0, E8 ⊗ Hadamard-8: 64 lines in T = 64, σ = 1/2, is the trivial control and is in `data/`.) **No saved system has dense x below the recorded break-even fit** (c5), and the best saturation per k′ at window h ≤ 13 is 7/9 (k′ = 3), 15/17 (k′ = 4), .386 (k′ = 5), .196 (k′ = 6). These constructions are heuristic (the pools were searched by iterated local search for a maximum independent set); they are *lower bounds on what is attainable*, not optima. **RECORDED, not in the package:** E8 ⊕ A2 with 139 lines in T = 10 (k′ = 5, σ ≈ .42) and E8 ⊕ A3 (BERTHA card).

### 8.2 The D16⁺ family and its exact Delsarte cap — CHECKED
In D16⁺ (doubled coordinates, norm 16, divisor 4) every root ±2e_i ± 2e_j has product ±4 or 0 (→ ±1, 0) with every spinor line, so v = 240 + (number of spinor lines), and two spinor lines (sign vectors s, s′ at Hamming distance d, products (16 − 2d)/4) are compatible iff d ∈ S = {2,6,10,14} ∪ {8, 16} (d = 16: the antipodal sign vector is the same line). So the spinor set is an antipodal binary code of length 16 with distance set S.
**Delsarte bound (proof).** For a binary code C with distance distribution (A_i) and Krawtchouk polynomials K_k, Σ_i A_iK_k(i) = |C|^{−1} Σ_{wt u = k} |Σ_{c∈C} (−1)^{u·c}|² ≥ 0 (K_k(d(x,y)) = Σ_{wt u=k}(−1)^{u·(x+y)}, CHECKED for n = 6 and the inequalities on RM(1,4)). If y_k ≥ 0 satisfy Σ_k y_k(−K_k(i)) ≥ 1 for all i ∈ S then |C| ≤ 1 + Σ_k y_k K_k(0). **c6 solves a 6 × 6 system exactly in `Fraction` for the dual support {2,3,5,6,7,8} (found by a floating-point LP), verifies y ≥ 0 and feasibility, and obtains |C| ≤ 18432/29 = 635.59, so |C| ≤ 634 (even), at most 317 spinor lines, and roots + spinors ≤ 240 + 317 = 557.** The needed v is h T/x\*(h) = 272/.4189 = 649.3 (conditional on the RECORDED fit), so **no D16⁺ roots-plus-spinors system can reach it**; the saved set has 496 (256 spinors, found by a coset-clique search). This is a statement about the D16⁺ construction only.

## 9. Scope: bounded window, and #2222

All "cannot reach the needed v/T" statements above assume (a) the dense pairing, (b) Gram or rank-bounded units, (c) **window h ≤ 13** (k′ ≤ 6), (d) the recorded fit x\*(h). They concern only the paper-side count.

**#2222 (credit).** RECORDED from its PR text (not re-run here): the P48p minimum vectors give 26,208,000 lines of norm 6 in a 48-dimensional even unimodular lattice; with f(t) = (t³ − 4t)/192 the kernel M = f(x·y) vanishes exactly when x·y is even, so the labels are x mod 2 in L/2L (dimension 48, the form x·y mod 2 alternating and non-degenerate), k′ ≤ 24, **h ≤ 49**; M has rank at most binom(50,3) + 48 = 19,648, which is the term count, so 19,648 is a valid (conservative) upper bound on the cost. **Correction (maintainer review):** this does not make the factorization complete. On the norm-six shell Σ_j x_j² = 6, so each linear feature is a combination of cubic ones, x_i = (1/6) Σ_j x_i x_j², and the cubic-plus-linear feature matrix has rank at most binom(50,3) = 19,600 < 19,648; the displayed factorization is therefore overcomplete (PROVEN, one line). An earlier version of this README wrongly called it complete. M is indefinite. Its bill ≤ 962,752 gives dense x = 962,752/26,208,000 ≈ .0367 at h = 49, far below any x\*(h). Theorem B (A′ form) holds for it (v ≤ 19,648·(2^{24}+1)) with saturation ≈ 8·10⁻⁵ and gives no obstruction. **So no unconditional paper-side no-go can exist; any one must be scoped to bounded h (here ≤ 13) or include compensation** (not modelled here). A general kernel remark (PROVEN, trivial): for a lattice shell in dimension n and a polynomial kernel of degree d, rank M ≤ the dimension of degree-≤ d polynomials on the shell, about n^d/d!, so paper wins need v ≫ n^d, hence large extremal lattices with h ≈ n + 1 (lineage: #598); at h ≤ 13 the shells are far too small.

## 10. EXPLORATORY evidence (floating point; scripts not shipped; not proof)

A block-coordinate/ALS solver was run on the *relaxed* problem (orthogonality enforced where Ā = 0; non-orthogonal pairs allowed to vanish — by Theorem A′(iv) a solution of the relaxed problem would still be a valid unit once lines are checked non-zero and distinct). Controls: D6 (W2, m = 2, T = 6) and E7 (W3, m = 1, T = 7) realise; W2 m = 1 needs T = 4 (the doily at T = 3 fails, also RECORDED in #2125). Results, symmetric and non-symmetric solvers agreeing: W3 m = 2 realises at T = 14 and fails at 13 (= tensoring); **W4 m = 1 (255 lines) fails (non-zero residual) for T ≤ 26 and gives only degenerate attractors (a vanishing non-orthogonal product) at T ≥ 28; W4 m = 2 (510 lines) fails at T = 30, 36, 40, 44; W5 m = 1 (1023 lines) fails at T = 31, 36, 47; W5 m = 2 fails at T = 62.** Reading: the multiplicity mechanism (D4: m = 4 in T = 4; D6: m = 2 in T = 6) is seen only at k′ ≤ 2; nothing suggests that dropping symmetry or positivity helps, so the obstruction looks algebraic (rank), not convex. These are local searches and prove nothing.

## 11. Open next questions

1. **The 510-vertex signing (OPEN, cheapest decisive object).** Does the non-collinearity graph of W(7,2) with every vertex doubled (twins orthogonal) admit a ±1 signing S with S² = 60S + 256I (equivalently 510 unit vectors in ℝ^30 with |cos| ∈ {0, 1/4}, saturated)? By §5.2 and §7.5 its non-existence rules out uniform-angle saturation with m = 1 at k′ = 5 (higher odd k′ descend to (k′ = 4, m = 2^{k′−4}, λ = 2^{(k′−1)/2}), a different object; descent of the 1023-vertex candidate in ℝ^31 with cos 1/4 passes through exactly this object at T = 30). c6 gives the required common-neighbour sign counts (94/34 on adjacent pairs, balanced elsewhere) for a pseudo-Boolean encoding. Not attempted here.
2. **Level-2 / three-point bounds (OPEN).** §6 shows that every two-point relaxation equals 2^{k′}+1. A bound s_4 < 1 for arbitrary multiplicities (a symmetry-reduced three-point SDP on W(7,2), reduced by Sp(8,2); the level-2 moment matrix has 1 + N + N·2^{2k′−1} rows before reduction) would bound all k′ ≥ 5 through Proposition D3. A bound at k′ = 5 would have to reach ≤ .65 to matter at h = 11.
3. **Realisability of W4 (OPEN).** Any *saturated* W4 system (any multiplicities) would be the first rung above E7 (E8 is 15/17) and would reopen k′ = 5 (needed 19.1 of cap 32 at h = 10); conversely, none exists if the signing of item 1 and its cousins fail. Also: asymmetric label subsets (not full W5) at h = 10..12 with ϑ-tight structure, and whether the Pauli-frame ansatz for W5 in ℝ³¹ (coordinate lines 4e_y and two ±1 bases on each hyperplane {a·y = 1}; an exact CNF with 29.9k variables was run by two SAT solvers for 22 and 30 minutes without a decision; not shipped) is satisfiable.
4. **Non-dense pairings.** Everything here bounds the *dense* B = J + Ā. A fitting B of smaller rank (lower bounded by the clique number ω(Γ), Remark 2 of §3), and per-term costs below h for overcomplete decoders, are the genuine extra levers and are untouched.
5. **Multiplicity m ≥ 2 symmetric systems** (Theorem F's N may be non-abelian) and the exact value d_proj(S) for Sp(2n,2), Ω^±(2n,2) beyond those cited.
6. **Compensation.** Whether a paper win at h ≥ 14 survives helper accounting (cf. #2222) is outside this package.

## 12. Files

`verify.sh`, `MANIFEST.sha256`, `SOURCES.json`, `scripts/provenance.py`; `lib/` (`exact.py`, `report.py`, `units.py` carried over from #2228's package; new: `lines.py` — Ā, symplectic labels, window; `sympl.py` — W(2k−1,2) and its generators; `rat.py` — exact rational matrices); `checks/c1_ladder.py` … `c6_delsarte_uniform.py`; `data/best_kprime_*.json` (14 files of exact integer vectors; the only data read).
