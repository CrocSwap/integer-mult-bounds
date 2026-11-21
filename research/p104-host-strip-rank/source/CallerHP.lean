/-
CallerHP (lane LEANHP, Nov 20).  KASYM's closed-form caller law, formalised.  (cards/WILD/NOVEL/kasym/KA.md; notes cards/WILD/NOVEL/leanhp/NOTES.md)

CC model (Q = 0, rho = 2, n = 2k-2 roles, D >= 2, lambda /= -1), s = 99/100, role value  (8D+1)^s - sum_pieces (8L)^s.
From (i) the role count n = 2k-2 with D >= 2, (ii) MAINS (>= 2k main singletons, 2 per stage) and (iii) the averaged RC2_l rows for l = 3..k
(stage form = the right-hand side of CallerRC2.rc2_avg), the explicit chord dual proves, for every k >= 3,
     c^(.99) := (104/k) * sum_r value_r  <=  HP(k) := (208/k) * [ (k-2)(17^s - 16^s) + (8k+1)^s - 8^s k ].
Files: HPCalc (real analysis: F_c antitone / convex, t^s concave), HPDual (chord dual algebra, weak duality), this file (numerics, frames, corollary).
Proved here:
  qf_sigma0        : the QF package at s = 99/100: q = h/x concave and increasing on [2,oo), q 3 <= 2 q 2 (rpow enclosures a/10^8, kernel).
  reduced_bound    : every `Cfg` satisfying `Reduced` has val <= HP k  (k >= 3).
  frame_bound      : the same for a CallerRC2 frame (rc2_avg supplies the RC2 rows; pieces = Pieces.pc; MAINS and D >= 2 are hypotheses).
  hp_lt_128891     : HP(k) < 128.891 for every real k >= 74 (monotone: M_c(74) <= 0; HP(74) = 128.7692...).
  corollary_ge72   : for k >= 72, val < 128.891, with k = 72, 73 taken from the full-LP certificates as NAMED DATA (h72, h73: not formalised).
  nonvac_*         : k = 3 HUBPAIR chart satisfies `Reduced` and attains HP(3) exactly.
Kernel only (no sorry / native_decide / new axioms).
-/
import Nov15.CallerRC2
import Nov15.HPDual
import Nov15.HPCalc
import Nov15.SafeCertGen

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CallerHP
open Finset Set
open SafeCertGen (phi enc_lo enc_hi)

noncomputable abbrev σ0 : ℝ := 99 / 100

/-! ## rpow enclosures (a/10^8 <= x^(99/100) <= (a+1)/10^8), certified by integer inequalities -/

theorem r17hi : (17:ℝ) ^ σ0 ≤ 1652511279 / 10 ^ 8 := by
  have h := enc_hi 17 1 100 1652511279 (10 ^ 8) (17:ℝ) (1 / 100) 1652511279 (10 ^ 8)
    (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num)
    (by decide +kernel) (by norm_num)
  unfold phi at h
  have e : (1:ℝ) - 1 / 100 = 99 / 100 := by norm_num
  rw [e] at h
  simpa using h

theorem r16lo : 1556247915 / 10 ^ 8 ≤ (16:ℝ) ^ σ0 := by
  have h := enc_lo 16 1 100 1556247915 (10 ^ 8) (16:ℝ) (1 / 100) 1556247915 (10 ^ 8)
    (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num)
    (by decide +kernel) (by norm_num)
  unfold phi at h
  have e : (1:ℝ) - 1 / 100 = 99 / 100 := by norm_num
  rw [e] at h
  simpa using h

theorem r16hi : (16:ℝ) ^ σ0 ≤ 1556247916 / 10 ^ 8 := by
  have h := enc_hi 16 1 100 1556247916 (10 ^ 8) (16:ℝ) (1 / 100) 1556247916 (10 ^ 8)
    (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num)
    (by decide +kernel) (by norm_num)
  unfold phi at h
  have e : (1:ℝ) - 1 / 100 = 99 / 100 := by norm_num
  rw [e] at h
  simpa using h

theorem r8lo : 783536238 / 10 ^ 8 ≤ (8:ℝ) ^ σ0 := by
  have h := enc_lo 8 1 100 783536238 (10 ^ 8) (8:ℝ) (1 / 100) 783536238 (10 ^ 8)
    (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num)
    (by decide +kernel) (by norm_num)
  unfold phi at h
  have e : (1:ℝ) - 1 / 100 = 99 / 100 := by norm_num
  rw [e] at h
  simpa using h

theorem r25lo : 2420809464 / 10 ^ 8 ≤ (25:ℝ) ^ σ0 := by
  have h := enc_lo 25 1 100 2420809464 (10 ^ 8) (25:ℝ) (1 / 100) 2420809464 (10 ^ 8)
    (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num)
    (by decide +kernel) (by norm_num)
  unfold phi at h
  have e : (1:ℝ) - 1 / 100 = 99 / 100 := by norm_num
  rw [e] at h
  simpa using h

theorem r593lo : 55631932504 / 10 ^ 8 ≤ (593:ℝ) ^ σ0 := by
  have h := enc_lo 593 1 100 55631932504 (10 ^ 8) (593:ℝ) (1 / 100) 55631932504 (10 ^ 8)
    (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num)
    (by decide +kernel) (by norm_num)
  unfold phi at h
  have e : (1:ℝ) - 1 / 100 = 99 / 100 := by norm_num
  rw [e] at h
  simpa using h

theorem r593hi : (593:ℝ) ^ σ0 ≤ 55631932505 / 10 ^ 8 := by
  have h := enc_hi 593 1 100 55631932505 (10 ^ 8) (593:ℝ) (1 / 100) 55631932505 (10 ^ 8)
    (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num)
    (by decide +kernel) (by norm_num)
  unfold phi at h
  have e : (1:ℝ) - 1 / 100 = 99 / 100 := by norm_num
  rw [e] at h
  simpa using h


/-! ## QF at s = 99/100 -/

theorem qq_eq {σ : ℝ} (x : ℝ) (hx : 0 < x) : qq σ x = (8 : ℝ) ^ σ - Ff σ (v2p σ) x := by
  unfold qq hh Ff g0; field_simp; ring

theorem g_at_2 : g0 σ0 2 = (17 : ℝ) ^ σ0 ∧ g1 σ0 2 = 8 * σ0 * (17 : ℝ) ^ σ0 / 17 ∧
    g2 σ0 2 = 64 * σ0 * (σ0 - 1) * (17 : ℝ) ^ σ0 / 289 := by
  have e : (8 * (2 : ℝ) + 1) = 17 := by norm_num
  have h17 : (17 : ℝ) ≠ 0 := by norm_num
  refine ⟨?_, ?_, ?_⟩
  · unfold g0; rw [e]
  · unfold g1; rw [e, Real.rpow_sub_one h17]; ring
  · unfold g2; rw [e, Real.rpow_sub_one h17, Real.rpow_sub_one h17]; ring

theorem M2_le : Mf σ0 (v2p σ0) 2 ≤ 0 := by
  obtain ⟨h0, h1, h2⟩ := g_at_2
  unfold Mf; rw [h0, h1]; unfold v2p
  have := r17hi; have := r16lo
  norm_num at *
  linarith

theorem N2_ge : 0 ≤ Nf σ0 (v2p σ0) 2 := by
  obtain ⟨h0, h1, h2⟩ := g_at_2
  unfold Nf; rw [h0, h1, h2]; unfold v2p
  have := r17hi; have := r16lo
  norm_num at *
  linarith

theorem q3_le : qq σ0 3 ≤ 2 * qq σ0 2 := by
  have e3 : (8 * (3 : ℝ) + 1) = 25 := by norm_num
  have e2 : (8 * (2 : ℝ) + 1) = 17 := by norm_num
  unfold qq hh v2p
  rw [e3, e2]
  have h1 := r17hi; have h2 := r16hi; have h3 := r25lo; have h4 := r8lo
  norm_num at *
  linarith

theorem qf_sigma0 : QF σ0 := by
  have h0 : (0 : ℝ) < σ0 := by norm_num
  have h1 : σ0 < 1 := by norm_num
  have hconv := F_convex h0 h1 (v2p σ0) N2_ge
  have hanti := F_anti h0 h1 (v2p σ0) 2 (by norm_num) M2_le
  refine ⟨⟨convex_Ici 2, ?_⟩, ?_, q3_le⟩
  · intro x hx y hy a b ha hb hab
    have hxy := (convex_Ici (2:ℝ)) hx hy ha hb hab
    have hx0 : 0 < x := by have := mem_Ici.mp hx; linarith
    have hy0 : 0 < y := by have := mem_Ici.mp hy; linarith
    have hxy0 : 0 < a • x + b • y := by have := mem_Ici.mp hxy; linarith
    have h := hconv.2 hx hy ha hb hab
    simp only [smul_eq_mul] at h hxy0 ⊢
    rw [qq_eq x hx0, qq_eq y hy0, qq_eq _ hxy0]
    have : a * (8 : ℝ) ^ σ0 + b * (8 : ℝ) ^ σ0 = (8 : ℝ) ^ σ0 := by rw [← add_mul, hab, one_mul]
    nlinarith [h, this]
  · intro x hx y hy hxy
    have hx0 : 0 < x := by have := mem_Ici.mp hx; linarith
    have hy0 : 0 < y := by have := mem_Ici.mp hy; linarith
    have := hanti hx hy hxy
    show qq σ0 x ≤ qq σ0 y
    rw [qq_eq x hx0, qq_eq y hy0]
    linarith

/-! ## HP and the model-level statement -/

noncomputable def HPr (x : ℝ) : ℝ :=
  208 / x * ((x - 2) * v2p σ0 + (8 * x + 1) ^ σ0 - (8 : ℝ) ^ σ0 * x)

structure Cfg (k : ℕ) where
  R : Type
  [fin : Fintype R]
  st : R → Finset (Fin k)
  a : R → Fin k → ℕ
  mn : R → Fin k → Bool

attribute [instance] Cfg.fin

noncomputable def Cfg.val {k : ℕ} (C : Cfg k) : ℝ :=
  104 / (k : ℝ) * ∑ r, roleVal σ0 (C.st r) (C.a r)

/-- the laws of the reduced LP: role count `n = 2k-2` with `D >= 2` (SIGN1), pieces inside their masks
(a piece of a stage has size between 1 and `D`), mains are singletons, MAINS (2k main singletons), RC2_l (l = 3..k). -/
structure Cfg.Reduced {k : ℕ} (C : Cfg k) : Prop where
  card : Fintype.card C.R + 2 = 2 * k
  deg : ∀ r, 2 ≤ (C.st r).card
  piece1 : ∀ r, ∀ s ∈ C.st r, 1 ≤ C.a r s
  pieceD : ∀ r, ∀ s ∈ C.st r, C.a r s ≤ (C.st r).card
  mainsing : ∀ r, ∀ s ∈ C.st r, C.mn r s = true → C.a r s = 1
  mains : 2 * k ≤ ∑ r, ((C.st r).filter (fun s => C.mn r s = true)).card
  rc2 : ∀ l, 3 ≤ l → l ≤ k → 2 * (k : ℝ) * ((k : ℝ) - 1) ≤ ∑ r, rowS k (C.st r) (C.a r) l

theorem card_le_k {k : ℕ} (A : Finset (Fin k)) : A.card ≤ k := by
  simpa using Finset.card_le_univ A

theorem mainCnt_eq {τ : Type*} (st : Finset τ) (mn : τ → Bool) :
    mainCnt st mn = ((st.filter (fun s => mn s = true)).card : ℝ) := by
  unfold mainCnt; rw [Finset.sum_boole]

theorem reduced_bound {k : ℕ} (hk : 3 ≤ k) (C : Cfg k) (h : C.Reduced) : C.val ≤ HPr k := by
  have hk3 : (3 : ℝ) ≤ k := by exact_mod_cast hk
  have hcard : (Fintype.card C.R : ℝ) = 2 * (k : ℝ) - 2 := by
    have : ((Fintype.card C.R + 2 : ℕ) : ℝ) = ((2 * k : ℕ) : ℝ) := by rw [h.card]
    push_cast at this; linarith
  have hmains : 2 * (k : ℝ) ≤ ∑ r, mainCnt (C.st r) (C.mn r) := by
    have := h.mains
    have h2 : ((2 * k : ℕ) : ℝ) ≤ ((∑ r, ((C.st r).filter (fun s => C.mn r s = true)).card : ℕ) : ℝ) := by
      exact_mod_cast this
    push_cast at h2
    simp only [mainCnt_eq]
    exact h2
  have hT := total_le qf_sigma0 (by norm_num : (0:ℝ) < σ0) (by norm_num : σ0 < 1) hk C.st C.a C.mn
    (fun r => h.deg r) (fun r => card_le_k _) h.piece1 h.pieceD h.mainsing hcard
    (fun l hl => h.rc2 l (Finset.mem_Icc.mp hl).1 (Finset.mem_Icc.mp hl).2) hmains
  unfold Cfg.val HPr
  have hk0 : (0 : ℝ) < k := by linarith
  calc 104 / (k : ℝ) * ∑ r, roleVal σ0 (C.st r) (C.a r)
      ≤ 104 / (k : ℝ) * (2 * (((k : ℝ) - 2) * v2p σ0 + (8 * (k : ℝ) + 1) ^ σ0 - (8 : ℝ) ^ σ0 * k)) :=
        mul_le_mul_of_nonneg_left hT (by positivity)
    _ = _ := by ring

/-! ## HP(k) < 128.891 for k >= 74 -/

theorem HPr_eq (x : ℝ) (hx : 0 < x) :
    HPr x = 208 * (v2p σ0 - (8 : ℝ) ^ σ0) + 208 * Ff σ0 (2 * v2p σ0) x := by
  unfold HPr Ff g0; field_simp; ring

theorem g_at_74 : g0 σ0 74 = (593 : ℝ) ^ σ0 ∧ g1 σ0 74 = 8 * σ0 * (593 : ℝ) ^ σ0 / 593 := by
  have e : (8 * (74 : ℝ) + 1) = 593 := by norm_num
  have h : (593 : ℝ) ≠ 0 := by norm_num
  refine ⟨?_, ?_⟩
  · unfold g0; rw [e]
  · unfold g1; rw [e, Real.rpow_sub_one h]; ring

theorem M74_le : Mf σ0 (2 * v2p σ0) 74 ≤ 0 := by
  obtain ⟨h0, h1⟩ := g_at_74
  unfold Mf; rw [h0, h1]; unfold v2p
  have := r17hi; have := r16lo; have := r593lo
  norm_num at *
  linarith

theorem HP74_lt : HPr 74 < 128891 / 1000 := by
  have e : (8 * (74 : ℝ) + 1) = 593 := by norm_num
  unfold HPr v2p
  rw [e]
  have h1 := r17hi; have h2 := r16lo; have h3 := r593hi; have h4 := r8lo
  norm_num at *
  linarith

theorem hp_lt_128891 (x : ℝ) (hx : 74 ≤ x) : HPr x < 128891 / 1000 := by
  have hanti := F_anti (σ := σ0) (by norm_num) (by norm_num) (2 * v2p σ0) 74 (by norm_num) M74_le
  have h := hanti (mem_Ici.mpr le_rfl) (mem_Ici.mpr hx) hx
  rw [HPr_eq x (by linarith)]
  have h74 := HP74_lt
  rw [HPr_eq 74 (by norm_num)] at h74
  linarith

/-- every reduced configuration with `k >= 74` stages has `c^(.99) < 128.891` -/
theorem reduced_lt_128891 {k : ℕ} (hk : 74 ≤ k) (C : Cfg k) (h : C.Reduced) : C.val < 128891 / 1000 :=
  lt_of_le_of_lt (reduced_bound (by omega) C h) (hp_lt_128891 k (by exact_mod_cast hk))

/-- k >= 72: k = 72, 73 are taken from the FULL-LP dual certificates (CALLERCUT cc2 / KASYM cert73.log) as NAMED DATA
(`h72`, `h73`: bounds 128.851 and 128.682 on `val` for configurations satisfying the reduced laws AND the remaining CC rows `Extra`;
not formalised here). -/
theorem corollary_ge72 (Extra : ∀ k, Cfg k → Prop)
    (h72 : ∀ C : Cfg 72, C.Reduced → Extra 72 C → C.val ≤ 128851 / 1000)
    (h73 : ∀ C : Cfg 73, C.Reduced → Extra 73 C → C.val ≤ 128682 / 1000)
    {k : ℕ} (hk : 72 ≤ k) (C : Cfg k) (h : C.Reduced) (hx : Extra k C) : C.val < 128891 / 1000 := by
  rcases (show k = 72 ∨ k = 73 ∨ 74 ≤ k by omega) with h1 | h1 | h1
  · subst h1; exact lt_of_le_of_lt (h72 C h hx) (by norm_num)
  · subst h1; exact lt_of_le_of_lt (h73 C h hx) (by norm_num)
  · exact reduced_lt_128891 h1 C h

/-! ## frames: rc2_avg supplies the RC2 rows -/

section frame
open CallerSign
variable {K : Type*} [Field K] {k : ℕ}

theorem rowS_eq {R : Type} [Fintype R] (M : R → Finset (Fin k)) (pc : R → Fin k → Finset (Fin k))
    (hsub : ∀ r s, s ∈ M r → pc r s ⊆ M r) (r : R) (l : ℕ) :
    (((∑ s : Fin k, (if s ∈ M r ∧ l ≤ (M r).card ∧ (pc r s).card < l then k - (pc r s).card else 0)) +
      (∑ s : Fin k, (if s ∈ M r ∧ (M r).card < l then (M r).card - (pc r s).card else 0)) : ℕ) : ℝ)
      = rowS k (M r) (fun s => (pc r s).card) l := by
  classical
  unfold rowS
  rw [← Finset.sum_add_distrib, Nat.cast_sum]
  have hpt : ∀ s : Fin k, (((if s ∈ M r ∧ l ≤ (M r).card ∧ (pc r s).card < l then k - (pc r s).card else 0)
      + (if s ∈ M r ∧ (M r).card < l then (M r).card - (pc r s).card else 0) : ℕ) : ℝ)
      = if s ∈ M r then (if l ≤ (M r).card then (if (pc r s).card < l then ((k : ℝ) - (pc r s).card) else 0)
          else (((M r).card : ℝ) - (pc r s).card)) else 0 := by
    intro s
    by_cases hs : s ∈ M r
    · have hc1 : (pc r s).card ≤ (M r).card := Finset.card_le_card (hsub r s hs)
      have hD := card_le_k (M r)
      have hck : (pc r s).card ≤ k := hc1.trans hD
      by_cases h1 : l ≤ (M r).card
      · by_cases h2 : (pc r s).card < l
        · have : ¬ (M r).card < l := not_lt.mpr h1
          simp [hs, h1, h2, this, Nat.cast_sub hck]
        · have : ¬ (M r).card < l := not_lt.mpr h1
          simp [hs, h1, h2, this]
      · have h1' : (M r).card < l := not_le.mp h1
        simp [hs, h1, h1', Nat.cast_sub hc1]
    · simp [hs]
  rw [Finset.sum_congr rfl (fun s _ => hpt s), Finset.sum_ite_mem, Finset.univ_inter]

theorem rc2_rows_real {R : Type} [Fintype R] [DecidableEq R] (M : R → Finset (Fin k))
    (bh ah : R → Fin k → Fin 2 → K)
    (hbh : ∀ r s, s ∉ M r → ∀ a, bh r s a = 0) (hah : ∀ r s, s ∉ M r → ∀ a, ah r s a = 0)
    (P : Pieces M bh) (hG : ∀ s t, s ≠ t → IsUnit (gBlk bh ah s t).det) (hk : 1 ≤ k) (l : ℕ) (hl : 2 ≤ l) :
    2 * (k : ℝ) * ((k : ℝ) - 1) ≤ ∑ r, rowS k (M r) (fun s => (P.pc r s).card) l := by
  have h := rc2_avg M bh ah hbh hah P l hl hG
  have hc : ((2 * (k * (k - 1)) : ℕ) : ℝ) ≤ ((∑ r, (
      (∑ s, (if s ∈ M r ∧ l ≤ (M r).card ∧ (P.pc r s).card < l then k - (P.pc r s).card else 0)) +
      (∑ s, (if s ∈ M r ∧ (M r).card < l then (M r).card - (P.pc r s).card else 0))) : ℕ) : ℝ) := by
    exact_mod_cast h
  rw [Nat.cast_sum] at hc
  simp_rw [rowS_eq M P.pc P.pc_sub] at hc
  push_cast [Nat.cast_sub hk] at hc
  linarith

/-- KASYM's caller law for a CallerRC2 frame (`m = 2`): pieces `P.pc`, masks `M`, any family `main` of main-singleton flags
with `2k` mains (MAINS) and `D_r >= 2` (SIGN1), `n = 2k-2` roles.  `c^(.99) <= HP(k)`. -/
theorem frame_bound {R : Type} [Fintype R] [DecidableEq R] (hk : 3 ≤ k) (M : R → Finset (Fin k))
    (bh ah : R → Fin k → Fin 2 → K)
    (hbh : ∀ r s, s ∉ M r → ∀ a, bh r s a = 0) (hah : ∀ r s, s ∉ M r → ∀ a, ah r s a = 0)
    (P : Pieces M bh) (hG : ∀ s t, s ≠ t → IsUnit (gBlk bh ah s t).det)
    (main : R → Fin k → Bool) (hn : Fintype.card R + 2 = 2 * k) (hdeg : ∀ r, 2 ≤ (M r).card)
    (hmain1 : ∀ r s, s ∈ M r → main r s = true → (P.pc r s).card = 1)
    (hmains : 2 * k ≤ ∑ r, ((M r).filter (fun s => main r s = true)).card) :
    104 / (k : ℝ) * ∑ r, roleVal σ0 (M r) (fun s => (P.pc r s).card) ≤ HPr k := by
  let C : Cfg k := ⟨R, M, fun r s => (P.pc r s).card, main⟩
  have hred : C.Reduced :=
    { card := hn
      deg := hdeg
      piece1 := fun r s hs => Finset.card_pos.mpr ⟨s, P.pc_mem r s hs⟩
      pieceD := fun r s hs => Finset.card_le_card (P.pc_sub r s hs)
      mainsing := hmain1
      mains := hmains
      rc2 := fun l h3 _ => rc2_rows_real M bh ah hbh hah P hG (by omega) l (by omega) }
  exact reduced_bound hk C hred

end frame

/-! ## non-vacuity: the k = 3 HUBPAIR chart (2 all-main hubs of degree 3 + 2 pure pairs) satisfies `Reduced` and attains HP(3) -/

def hubC : Cfg 3 where
  R := Fin 4
  st := fun r => if r.val < 2 then Finset.univ else {0, 1}
  a := fun r _ => if r.val < 2 then 1 else 2
  mn := fun r _ => decide (r.val < 2)

theorem hubC_sum4 (f : Fin 4 → ℝ) : ∑ r : hubC.R, f r = f 0 + f 1 + f 2 + f 3 := Fin.sum_univ_four f

theorem hubC_reduced : hubC.Reduced := by
  refine ⟨by simp [hubC], ?_, ?_, ?_, ?_, ?_, ?_⟩
  · intro r; fin_cases r <;> simp [hubC]
  · intro r s hs; fin_cases r <;> simp [hubC]
  · intro r s hs; fin_cases r <;> simp [hubC] at hs ⊢
  · intro r s hs h; fin_cases r <;> simp [hubC] at hs h ⊢
  · simp [hubC, Fin.sum_univ_four]
    decide
  · intro l h3 hl
    have : l = 3 := by omega
    subst this
    erw [hubC_sum4 (fun r => rowS 3 (hubC.st r) (hubC.a r) 3)]
    simp [hubC, rowS, Fin.sum_univ_three]
    norm_num

theorem hubC_val : hubC.val = HPr 3 := by
  unfold Cfg.val
  erw [hubC_sum4 (fun r => roleVal σ0 (hubC.st r) (hubC.a r))]
  simp [HPr, roleVal, hubC, Fin.sum_univ_three, v2p]
  norm_num
  ring

theorem hubC_nonvac : hubC.Reduced ∧ hubC.val = HPr 3 ∧ hubC.val ≤ HPr 3 :=
  ⟨hubC_reduced, hubC_val, hubC_val.le⟩

#print axioms qf_sigma0
#print axioms reduced_bound
#print axioms frame_bound
#print axioms hp_lt_128891
#print axioms reduced_lt_128891
#print axioms corollary_ge72
#print axioms hubC_nonvac

end CallerHP
