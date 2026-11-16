# L120D0 notes (theory card; P112-PUSH)
STATE: L120D0: DONE (budget). s-general scenario list PROVEN (§1). Scenario (I)=ClassI of rows 302, 398 KILLED (2 impls, §2).
  302/398 scenarios (II),(III) and row 159 (all scenarios) OPEN. d=0 sliver OPEN (lead §4). d=0 PROVEN-pa cells NOT rewritten.

## §1 Level identity and the scenario list for any s (PROVEN; replaces CARRIER §1.3's Δ/D bookkeeping, agrees with it)
Notation as CARRIER §1. For a space U with weight w, U_{≤m} := span of vectors of weight ≤ m; greedy ⇒ cost_w(U) = Σ_{m≥0} (dim U − dim U_{≤m}).
**Lemma L (z = 0).** If Z = ker ρ ∩ S = 0 then cost_w(S) = cost_w(ρS) + Σ_{m=1}^{8} τ_m, τ_m := dim (ρS)_{≤m} − dim ρ(S^E_{≤m}) ≥ 0.
*Proof.* ρ is injective, dim S = dim ρS, dim S^E_{≤m} = dim ρ(S^E_{≤m}) and ρ(S^E_{≤m}) ⊆ (ρS)_{≤m} (w(ρu) ≤ w_E(u)); weights ≤ 9 so m ≥ 9 terms vanish. ∎
**Lemma N (no-drop min basis).** If z = 0 and τ_1 = … = τ_7 = 0 then T has a min-weight basis y_1..y_a whose (unique) lifts y_j^E ∈ S have E8 weight
w(y_j) (drop 0). *Proof.* Greedy level by level: (ρS)_{≤m} = ρ(S^E_{≤m}) is spanned by images ρu of S-vectors with w_E(u) ≤ m; extend a basis of
(ρS)_{≤m−1} by such ρu. A chosen ρu has w(ρu) = m (else it lies in (ρS)_{≤m−1}, already spanned), so m = w(ρu) ≤ w_E(u) ≤ m. ∎
(So "ClassI" = {z = 0, τ_{≤7} ≡ 0}: exactly the hypothesis of CARRIER §2 E8 version / SEVEN Lemma F; no basis-member condition is needed.)
**Scenario list, slack s (COMPLETE by construction).** Violation: cost_w(S) ≤ 71. Z-lemma (CARRIER 1.1) + cost_w(ρS) = 64 + s + 8x + c_8 give
x = 0 and c_8 + z ≤ 7 − s. If z = 0, Lemma L gives c_8 + Σ_{m≤8} τ_m ≤ 7 − s. Scenarios:
 (I) z = 0, τ_{≤7} ≡ 0 [ClassI; any c_8, τ_8 with c_8 + τ_8 ≤ 7 − s];
 (II) z = 0, 1 ≤ Σ_{m≤7} τ_m ≤ 7 − s − c_8 [deficient levels: some piece of every min basis drops];
 (III) 1 ≤ z ≤ 7 − s − c_8.
s = 5: (I); (II) with Σ_{m≤7}τ_m ∈ {1,2}; (III) z ∈ {1,2}. s = 6: (I); (II) one deficient level, τ_m = 1, c_8 = 0; (III) z = 1, c_8 = 0 (= CARRIER (α)).
s = 6 consistency with CARRIER/AUDIT-SC: (β1)/(β3-i) ⊆ (I) [Lemma N], (β2) and (β3-B) ⊆ (I) ∪ (II), (α) = (III). (I) ∪ (II) ∪ (III) is the whole case
space, so no Gale-dominance argument is needed for completeness.

## §2 ClassI kill for rows 302 [7^9,6] (s=5) and 398 [7^9,6,1] (s=6), d = 8 (PROVEN mod imports; CHECKED impl A, impl B below)
Imports: SEVEN S1 (Lemma F, pair pattern; uses G3 (7,7) uncoverable), S4 (D7R ⇒ every h_ab a root; small flats {6},{6,1} span ≤ 7 labels),
S4's conclusion that {h_ab} is an A8 root subsystem with h_ab = ±(e_a − e_b) in A-coordinates; W(E8) acts linearly on labels (CARRIER G1);
A8 ⊂ E8 unique up to W(E8) (classical; tight.py's chain search finds one class).
Lemma F in A-coordinates: V = h(R) = span A8 (d = 8 = rank), φ_k (k ∈ [9]) vanishes on all e_a − e_b with k ∉ ab, so φ_k = λ_k x_k on V
(V* = K^9/⟨1⟩). For a line t write f_t := ⟨·, r_t⟩|_V = g_t ∈ K^9/⟨1⟩ (g_t computed from a chain, lf.py). σ(g) := min_ν #{k : g_k ≠ ν} = least |J| with
g ∈ span{x_j : j ∈ J}. Lemma F: with J_t := {k ∈ [9] : t ∈ L_k} (L_k = Λ_E(F_k), |L_k| ≤ 36 = max lines of a 7-flat), t ∉ L_0 ⇒ |J_t| ≥ need(t) := σ(g_t),
and J_t ⊇ P_t (unique minimal pattern) or |J_t| ≥ need + ex_t. A8 data (lf.py impl A g-vector formula = impl B brute-force ranks): need = 3 on the 84 Λ³ lines,
2 on the 36 A8 lines, Σ = 324 = 9·36: exactly tight. A_a := {t : a ∈ P_t} (36 lines) has label rank 9 and meets every 7-flat in ≤ m = 21 lines.
Lines t ∈ L_0 (six-flat lines, |L_0| ≤ 20): f_t ∈ span{x_J} + ⟨φ_0⟩; subadditivity of σ gives |J_t| ≥ |need(t) − σ_0|, σ_0 := σ(φ_0), i.e. relief ≤ min(σ_0, 2need − σ_0).
Count: 36·9 ≥ Σ_k |L_k| = Σ_t |J_t| ≥ 324 − Σ_{L_0} relief + Σ_{t∈B} ex_t (B := non-L_0 lines with J_t ⊉ P_t), and for each a: A_a ∖ (L_0 ∪ B) ⊆ L_a ⇒
Σ_{t∈B} need(t) ≥ H(L_0) := Σ_a max(0, |A_a ∖ L_0| − 21); ex_t ≥ need(t) (r = 1). So H(L_0) ≤ Σ_{L_0} relief is necessary.
tight2.py over all 788035 six-dim label subspaces and σ_0 = 1..8: min (H − Σ relief) = 15 (σ_0 = 3) > 0 ⇒ **302 (I) dead**. Row 398: the unit line u adds
≤ need(u) ≤ 3 to relief and removes ≤ 3 from H: needs margin > 6; 15 > 6 ⇒ **398 (I) dead**.
CHECK impl B implB.py (Bourbaki simple roots + reflection closure, A8 = roots with α2-coefficient ∈ {0,±3}, labels ⟨r,α_i⟩ mod 2,
need = 9 − max K with r_t ⊥ all A8 roots inside K, 6-flats by numpy over dual 3-subspaces deduped by line set: 777241 distinct sets, max 20 lines):
need hist {2:36, 3:84}, m = 21, min margins by σ_0 = 55,35,15,35,55,75,75,75 — identical to impl A. Non-kill control: the same test does NOT kill
either A7 class (§3), so it is not vacuous.
## §3 Row 159 [7^8,6] d = 7: ClassI NOT killed
Two A7 classes in E8 (perp-line count 1 / 0). Totals 308 / 288 vs capacity 288. With the §2 count the min margins over 6-flats are −4 (σ_0 = 2) and −20 (σ_0 = 3):
not a kill. Needs the exact φ_0-relief (not the σ-subadditivity bound) or JOINT2's φ_s refinement.
## §4 d = 0 sliver (OPEN; lead only)
Structure (PROVEN): at d = 0, κ ≤ 6, x = 0: S = 𝒞(E8) ⊕ T̃ ⊕ Z (T̃ any lift of T), W := T̃ ⊕ Z, dim W = a + z ≤ 7, supp W ⊆ Λ := supp T ∪ F,
|Λ| ≤ 20 + 8. Any v ∈ S with a codeword component has |supp v| ≥ 57 − 28 > 8, so every frame-supported vector of S lies in W.
Lead (not proven): pick another frame F' (W(E8) has 2025 frames) with W ∩ K^{F'} = 0; then ker ρ_{F'} ∩ S = 0 and the Z = 0 ledger for F' applies —
but F'-cell may have d' ≥ 1, so this only reduces the sliver to the (open) Z = 0 ledger, not to a closed cell. Existence of F' not checked.
