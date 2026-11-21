/-
CallerHPQ (lane LEANTHIN, Nov 20).  The LEAF-CHANNEL closed-form caller law for the Q >= 1, e = 0 branch
(cards/WILD/NOVEL/leanthin/LT.md).  Extends KASYM's chord dual (CallerHP/HPDual) with two leaf multipliers.
Rows (all [P] on the lambda != -1, T = Q branch): role count enters only through
  DEEP   : 2k main singletons on roles of degree >= 2           (THINQ MAINS-DEEP),
  RC2_l  : l = 3..k averaged rows (leaves contribute 0),
  LC     : #{roles of degree >= 2} >= k - 2                      (LEAF-CHANNEL d1 <= k + T, CallerThinDel.leaf_channel_thin, with n = 2k-2+T),
  LEAF   : k*n - #leaves >= k(2k-2)                              (LEAF-RANK d1 <= k*T, T = n-(2k-2)).
Objective  val = (104/k) (sum_r roleVal r - n + 2k - 2)  (each excess role costs one unit).
Dual:  y_DEEP = wm, y_RC2 = wt_l/(k-1), y_LEAF = mu = (1-u1)/(k-1), y_LC = nu = (1-v2p) - k mu  (u1 = 9^s-8^s, v2p = 17^s-16^s).
Proved here (kernel only):  role_leQ (per-role feasibility incl. leaves), valQ_le_F2 (weak duality, k >= 77),
  F2_lt (the closed form < 128.891 for real k >= 77),  valQ_lt: every configuration satisfying `LawQ` with k >= 77 has val < 128.891.
Closed form (not LP-optimised, it IS the optimum of the reduced LP):  HQ2(k) = (104/k)[2k-2+2((8k+1)^s-8^s k-1) - (1-u1)k^2/(k-1) - (k-4)(1-v2p)],
  HQ2(77) = 128.8814.
-/
import Nov15.CallerHP

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CallerHP
open Finset Set
open SafeCertGen (phi enc_lo enc_hi)

/-! ## rpow enclosures (a/10^8 <= x^(99/100) <= (a+1)/10^8) -/
theorem r17lo : 1652511278 / 10 ^ 8 ≤ (17:ℝ) ^ σ0 := by
  have h := enc_lo 17 1 100 1652511278 (10 ^ 8) (17:ℝ) (1 / 100) 1652511278 (10 ^ 8)
    (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num)
    (by decide +kernel) (by norm_num)
  unfold phi at h
  have e : (1:ℝ) - 1 / 100 = 99 / 100 := by norm_num
  rw [e] at h
  simpa using h

theorem r8hi : (8:ℝ) ^ σ0 ≤ 783536239 / 10 ^ 8 := by
  have h := enc_hi 8 1 100 783536239 (10 ^ 8) (8:ℝ) (1 / 100) 783536239 (10 ^ 8)
    (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num)
    (by decide +kernel) (by norm_num)
  unfold phi at h
  have e : (1:ℝ) - 1 / 100 = 99 / 100 := by norm_num
  rw [e] at h
  simpa using h

theorem r9lo : 880440647 / 10 ^ 8 ≤ (9:ℝ) ^ σ0 := by
  have h := enc_lo 9 1 100 880440647 (10 ^ 8) (9:ℝ) (1 / 100) 880440647 (10 ^ 8)
    (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num)
    (by decide +kernel) (by norm_num)
  unfold phi at h
  have e : (1:ℝ) - 1 / 100 = 99 / 100 := by norm_num
  rw [e] at h
  simpa using h

theorem r9hi : (9:ℝ) ^ σ0 ≤ 880440648 / 10 ^ 8 := by
  have h := enc_hi 9 1 100 880440648 (10 ^ 8) (9:ℝ) (1 / 100) 880440648 (10 ^ 8)
    (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num)
    (by decide +kernel) (by norm_num)
  unfold phi at h
  have e : (1:ℝ) - 1 / 100 = 99 / 100 := by norm_num
  rw [e] at h
  simpa using h

theorem r617lo : 57860517335 / 10 ^ 8 ≤ (617:ℝ) ^ σ0 := by
  have h := enc_lo 617 1 100 57860517335 (10 ^ 8) (617:ℝ) (1 / 100) 57860517335 (10 ^ 8)
    (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num)
    (by decide +kernel) (by norm_num)
  unfold phi at h
  have e : (1:ℝ) - 1 / 100 = 99 / 100 := by norm_num
  rw [e] at h
  simpa using h

theorem r617hi : (617:ℝ) ^ σ0 ≤ 57860517336 / 10 ^ 8 := by
  have h := enc_hi 617 1 100 57860517336 (10 ^ 8) (617:ℝ) (1 / 100) 57860517336 (10 ^ 8)
    (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num)
    (by decide +kernel) (by norm_num)
  unfold phi at h
  have e : (1:ℝ) - 1 / 100 = 99 / 100 := by norm_num
  rw [e] at h
  simpa using h


/-! ## constants -/
noncomputable def u1 : ℝ := (9:ℝ) ^ σ0 - (8:ℝ) ^ σ0
noncomputable def muQ (x : ℝ) : ℝ := (1 - u1) / (x - 1)
noncomputable def nuQ (x : ℝ) : ℝ := (1 - v2p σ0) - x * muQ x
noncomputable def F2 (x : ℝ) : ℝ :=
  2 * x - 2 - 2 * hh σ0 x - nuQ x * (x - 2) - muQ x * x * (2 * x - 2)

theorem u1_lt : u1 < 1 := by
  unfold u1
  have := r9hi; have := r8lo
  norm_num at *; linarith

theorem muQ_nonneg {x : ℝ} (hx : 1 < x) : 0 ≤ muQ x := by
  unfold muQ
  exact div_nonneg (by linarith [u1_lt]) (by linarith)

theorem nuQ_nonneg {x : ℝ} (hx : 77 ≤ x) : 0 ≤ nuQ x := by
  unfold nuQ muQ
  have h1 : x * ((1 - u1) / (x - 1)) ≤ (77 / 76) * (1 - u1) := by
    have e : x * ((1 - u1) / (x - 1)) = (1 - u1) * (x / (x - 1)) := by ring
    rw [e]
    have : x / (x - 1) ≤ 77 / 76 := by rw [div_le_iff₀ (by linarith)]; linarith
    have h0 : 0 ≤ 1 - u1 := by linarith [u1_lt]
    nlinarith
  have h2 : (77 / 76) * (1 - u1) ≤ 1 - v2p σ0 := by
    unfold u1 v2p
    have := r9lo; have := r8hi; have := r17hi; have := r16lo
    norm_num at *; linarith
  linarith

/-! ## per-role feasibility, leaves included -/
theorem role_leQ {k : ℕ} (hk : 3 ≤ k) {τ : Type*} (st : Finset τ) (a : τ → ℕ) (mn : τ → Bool)
    (hD1 : 1 ≤ st.card) (hDk : st.card ≤ k) (ha1 : ∀ s ∈ st, 1 ≤ a s) (haD : ∀ s ∈ st, a s ≤ st.card)
    (hmain : ∀ s ∈ st, mn s = true → a s = 1) :
    roleVal σ0 st a + (∑ l ∈ Finset.Icc 3 k, wt σ0 k l * rowS k st a l) / ((k : ℝ) - 1)
      + wm σ0 k * (if 2 ≤ st.card then mainCnt st mn else 0)
    ≤ if 2 ≤ st.card then v2p σ0 else u1 := by
  by_cases h : 2 ≤ st.card
  · simp only [h, if_true]
    exact role_le qf_sigma0 (by norm_num) (by norm_num) hk st a mn h hDk ha1 haD hmain
  · simp only [h, if_false, mul_zero, add_zero]
    have hc : st.card = 1 := by omega
    obtain ⟨s0, rfl⟩ := Finset.card_eq_one.1 hc
    have hs0 : s0 ∈ ({s0} : Finset τ) := Finset.mem_singleton_self s0
    have ha : a s0 = 1 := le_antisymm (by simpa using haD s0 hs0) (ha1 s0 hs0)
    have hrow : ∀ l ∈ Finset.Icc 3 k, rowS k ({s0} : Finset τ) a l = 0 := by
      intro l hl
      have hl3 := (Finset.mem_Icc.1 hl).1
      unfold rowS
      rw [Finset.sum_singleton, Finset.card_singleton]
      have : ¬ (l ≤ 1) := by omega
      simp [this, ha]
    have : ∑ l ∈ Finset.Icc 3 k, wt σ0 k l * rowS k ({s0} : Finset τ) a l = 0 :=
      Finset.sum_eq_zero (fun l hl => by rw [hrow l hl, mul_zero])
    rw [this, zero_div, add_zero]
    unfold roleVal u1
    rw [Finset.sum_singleton, Finset.card_singleton, ha]
    norm_num

/-! ## the model and weak duality -/
structure Cfg.LawQ {k : ℕ} (C : Cfg k) : Prop where
  deg : ∀ r, 1 ≤ (C.st r).card
  piece1 : ∀ r, ∀ s ∈ C.st r, 1 ≤ C.a r s
  pieceD : ∀ r, ∀ s ∈ C.st r, C.a r s ≤ (C.st r).card
  mainsing : ∀ r, ∀ s ∈ C.st r, C.mn r s = true → C.a r s = 1
  mains : 2 * (k : ℝ) ≤ ∑ r, (if 2 ≤ (C.st r).card then mainCnt (C.st r) (C.mn r) else 0)
  rc2 : ∀ l, 3 ≤ l → l ≤ k → 2 * (k : ℝ) * ((k : ℝ) - 1) ≤ ∑ r, rowS k (C.st r) (C.a r) l
  lc : (k : ℝ) - 2 ≤ ((Finset.univ.filter (fun r => 2 ≤ (C.st r).card)).card : ℝ)
  leaf : (k : ℝ) * (2 * k - 2) ≤ k * (Fintype.card C.R : ℝ)
      - ((Finset.univ.filter (fun r => (C.st r).card = 1)).card : ℝ)

noncomputable def Cfg.valQ {k : ℕ} (C : Cfg k) : ℝ :=
  104 / (k : ℝ) * (∑ r, roleVal σ0 (C.st r) (C.a r) - (Fintype.card C.R : ℝ) + 2 * k - 2)

theorem valQ_le_F2 {k : ℕ} (hk : 77 ≤ k) (C : Cfg k) (h : C.LawQ) :
    ∑ r, roleVal σ0 (C.st r) (C.a r) - (Fintype.card C.R : ℝ) + 2 * k - 2 ≤ F2 k := by
  have hk3 : 3 ≤ k := by omega
  have hK77 : (77 : ℝ) ≤ k := by exact_mod_cast hk
  have hk1 : (0 : ℝ) < (k : ℝ) - 1 := by linarith
  have hq := qf_sigma0
  have hwm := wm_nonneg hq hk3
  have hs := Finset.sum_le_sum (fun r (_ : r ∈ (Finset.univ : Finset C.R)) =>
    role_leQ hk3 (C.st r) (C.a r) (C.mn r) (h.deg r) (card_le_k _) (h.piece1 r) (h.pieceD r) (h.mainsing r))
  rw [Finset.sum_add_distrib, Finset.sum_add_distrib, ← Finset.mul_sum] at hs
  rw [← Finset.sum_div] at hs
  have hswap : ∑ r, ∑ l ∈ Finset.Icc 3 k, wt σ0 k l * rowS k (C.st r) (C.a r) l
      = ∑ l ∈ Finset.Icc 3 k, wt σ0 k l * ∑ r, rowS k (C.st r) (C.a r) l := by
    simp_rw [Finset.mul_sum]
    exact Finset.sum_comm
  rw [hswap] at hs
  -- right-hand side: n_l v2p + n_1 u1
  have e : (Finset.univ.filter (fun r => ¬ 2 ≤ (C.st r).card))
      = (Finset.univ.filter (fun r => (C.st r).card = 1)) := by
    ext r
    simp only [Finset.mem_filter, Finset.mem_univ, true_and]
    have := h.deg r
    omega
  have hsplit : ∑ r, (if 2 ≤ (C.st r).card then v2p σ0 else u1)
      = ((Finset.univ.filter (fun r => 2 ≤ (C.st r).card)).card : ℝ) * v2p σ0
        + ((Finset.univ.filter (fun r => (C.st r).card = 1)).card : ℝ) * u1 := by
    rw [Finset.sum_ite, Finset.sum_const, Finset.sum_const, nsmul_eq_mul, nsmul_eq_mul, e]
  have hcnt : (Fintype.card C.R : ℝ)
      = ((Finset.univ.filter (fun r => 2 ≤ (C.st r).card)).card : ℝ)
        + ((Finset.univ.filter (fun r => (C.st r).card = 1)).card : ℝ) := by
    have := Finset.card_filter_add_card_filter_not (s := (Finset.univ : Finset C.R))
      (fun r => 2 ≤ (C.st r).card)
    rw [e] at this
    simp only [Finset.card_univ] at this
    exact_mod_cast this.symm
  rw [hsplit] at hs
  -- RC2 rows
  have hY : 2 * (k : ℝ) * ((k : ℝ) - 1) * Tt σ0 k
      ≤ ∑ l ∈ Finset.Icc 3 k, wt σ0 k l * ∑ r, rowS k (C.st r) (C.a r) l := by
    rw [← sum_wt_all hk3, Finset.mul_sum]
    refine Finset.sum_le_sum fun l hl => ?_
    rw [Finset.mem_Icc] at hl
    have := wt_nonneg hq hk3 hl.1 hl.2
    have h2 := h.rc2 l hl.1 hl.2
    nlinarith
  have hMC : wm σ0 k * (2 * (k : ℝ)) ≤ wm σ0 k * ∑ r, (if 2 ≤ (C.st r).card then mainCnt (C.st r) (C.mn r) else 0) :=
    mul_le_mul_of_nonneg_left h.mains hwm
  generalize (∑ l ∈ Finset.Icc 3 k, wt σ0 k l * ∑ r, rowS k (C.st r) (C.a r) l) = Y at *
  generalize (∑ r, (if 2 ≤ (C.st r).card then mainCnt (C.st r) (C.mn r) else 0)) = MC at *
  have hY2 : 2 * (k : ℝ) * Tt σ0 k ≤ Y / ((k : ℝ) - 1) := by
    rw [le_div_iff₀ hk1]; nlinarith
  -- identities
  have hslm := sl_mul (σ := σ0) hk3
  have hhk : hh σ0 k = k * qq σ0 k := hh_eq _ (by positivity)
  have hTW : (k : ℝ) * (Tt σ0 k + wm σ0 k) = hh σ0 k := by
    unfold Tt wm
    linear_combination (k : ℝ) * hslm - hhk
  have hnu := nuQ_nonneg hK77
  have hmu := muQ_nonneg (by linarith : (1 : ℝ) < k)
  have hmuk : muQ k * ((k : ℝ) - 1) = 1 - u1 := by
    unfold muQ; field_simp
  have ha1 : 1 - v2p σ0 = nuQ k + k * muQ k := by unfold nuQ; ring
  have hb1 : 1 - u1 = ((k : ℝ) - 1) * muQ k := by rw [← hmuk]; ring
  have hlc := mul_le_mul_of_nonneg_left h.lc hnu
  have hleaf := mul_le_mul_of_nonneg_left h.leaf hmu
  generalize ((Finset.univ.filter (fun r => 2 ≤ (C.st r).card)).card : ℝ) = nl at *
  generalize ((Finset.univ.filter (fun r => (C.st r).card = 1)).card : ℝ) = n1 at *
  rw [hcnt] at hleaf ⊢
  unfold F2
  have hcomb : nl * (1 - v2p σ0) + n1 * (1 - u1) = nuQ k * nl + muQ k * ((k : ℝ) * nl + ((k : ℝ) - 1) * n1) := by
    rw [ha1, hb1]; ring
  have hkn : (k : ℝ) * (nl + n1) - n1 = (k : ℝ) * nl + ((k : ℝ) - 1) * n1 := by ring
  rw [hkn] at hleaf
  nlinarith [hs, hY2, hMC, hTW, hcomb, hlc, hleaf]

/-! ## the closed form is below the bar for real x >= 77 -/
noncomputable def cQ : ℝ := 2 * v2p σ0 + (1 - u1) / 2

theorem g_at_77 : g0 σ0 77 = (617 : ℝ) ^ σ0 ∧ g1 σ0 77 = 8 * σ0 * (617 : ℝ) ^ σ0 / 617 := by
  have e : (8 * (77 : ℝ) + 1) = 617 := by norm_num
  have h : (617 : ℝ) ≠ 0 := by norm_num
  refine ⟨?_, ?_⟩
  · unfold g0; rw [e]
  · unfold g1; rw [e, Real.rpow_sub_one h]; ring

theorem M77_le : Mf σ0 cQ 77 ≤ 0 := by
  obtain ⟨h0, h1⟩ := g_at_77
  unfold Mf cQ u1 v2p; rw [h0, h1]
  have := r17hi; have := r16lo; have := r617lo; have := r9lo; have := r8hi
  norm_num at *
  linarith

theorem bar77 : 104 * (2 - 2 * (8 : ℝ) ^ σ0 - (1 - v2p σ0) - (1 - u1)) + 208 * Ff σ0 cQ 77 < 128891 / 1000 := by
  have h0 : g0 σ0 77 = (617 : ℝ) ^ σ0 := g_at_77.1
  unfold Ff cQ u1 v2p
  rw [h0]
  have := r17hi; have := r16lo; have := r17lo; have := r16hi; have := r617lo; have := r617hi
  have := r9lo; have := r9hi; have := r8lo; have := r8hi
  norm_num at *
  linarith

theorem F2_lt {x : ℝ} (hx : 77 ≤ x) : 104 / x * F2 x < 128891 / 1000 := by
  have hx0 : 0 < x := by linarith
  have hx1 : x - 1 ≠ 0 := by intro h; linarith
  have hμ := muQ_nonneg (x := x) (by linarith)
  have hμx : muQ x * (x - 1) = 1 - u1 := by unfold muQ; field_simp
  have key : muQ x * x ^ 2 = (1 - u1) * (x + 1) + muQ x := by linear_combination (x + 1) * hμx
  have hFe : F2 x = 2 * x - 2 - 2 * hh σ0 x - (1 - v2p σ0) * (x - 2) - muQ x * x ^ 2 := by
    unfold F2 nuQ; ring
  have hF : F2 x ≤ 2 * x - 2 - 2 * hh σ0 x - (1 - v2p σ0) * (x - 2) - (1 - u1) * (x + 1) := by
    rw [hFe]; linarith
  have h104 : 104 / x * F2 x ≤ 104 / x * (2 * x - 2 - 2 * hh σ0 x - (1 - v2p σ0) * (x - 2) - (1 - u1) * (x + 1)) :=
    mul_le_mul_of_nonneg_left hF (by positivity)
  have hG : 104 / x * (2 * x - 2 - 2 * hh σ0 x - (1 - v2p σ0) * (x - 2) - (1 - u1) * (x + 1))
      = 104 * (2 - 2 * (8 : ℝ) ^ σ0 - (1 - v2p σ0) - (1 - u1)) + 208 * Ff σ0 cQ x := by
    unfold Ff hh cQ g0
    field_simp
    ring
  have hanti := F_anti (σ := σ0) (by norm_num) (by norm_num) cQ 77 (by norm_num) M77_le
  have hle : Ff σ0 cQ x ≤ Ff σ0 cQ 77 := hanti (mem_Ici.mpr le_rfl) (mem_Ici.mpr hx) hx
  have := bar77
  linarith

/-- HEADLINE: every configuration satisfying the LEAF-CHANNEL laws with k >= 77 stages has
`c^(.99) < 128.891` (Q >= 1, e = 0 branch). -/
theorem valQ_lt {k : ℕ} (hk : 77 ≤ k) (C : Cfg k) (h : C.LawQ) : C.valQ < 128891 / 1000 := by
  have hK : (77 : ℝ) ≤ k := by exact_mod_cast hk
  have h1 := valQ_le_F2 hk C h
  unfold Cfg.valQ
  calc 104 / (k : ℝ) * (∑ r, roleVal σ0 (C.st r) (C.a r) - (Fintype.card C.R : ℝ) + 2 * k - 2)
      ≤ 104 / (k : ℝ) * F2 k := mul_le_mul_of_nonneg_left h1 (by positivity)
    _ < 128891 / 1000 := F2_lt hK


/-! ## non-vacuity: for every k >= 4 the chart "2 all-main hubs + (k-4) pure pairs + (k+2) leaves" satisfies `LawQ`. -/
section inst
variable (k : ℕ) (hk : 4 ≤ k)

def cfgQ : Cfg k where
  R := Fin 2 ⊕ Fin (k - 4) ⊕ Fin (k + 2)
  st := fun r => match r with
    | Sum.inl _ => Finset.univ
    | Sum.inr (Sum.inl _) => {⟨0, by omega⟩, ⟨1, by omega⟩}
    | Sum.inr (Sum.inr _) => {⟨0, by omega⟩}
  a := fun r _ => match r with
    | Sum.inl _ => 1
    | Sum.inr (Sum.inl _) => 2
    | Sum.inr (Sum.inr _) => 1
  mn := fun r _ => match r with
    | Sum.inl _ => true
    | _ => false

theorem cfgQ_law : (cfgQ k hk).LawQ := by
  have h01 : (⟨0, by omega⟩ : Fin k) ≠ ⟨1, by omega⟩ := by simp [Fin.ext_iff]
  have hpair : ({⟨0, by omega⟩, ⟨1, by omega⟩} : Finset (Fin k)).card = 2 := Finset.card_pair h01
  have hmcT : mainCnt (Finset.univ : Finset (Fin k)) (fun _ => true) = k := by unfold mainCnt; simp
  have hmcF : ∀ (st : Finset (Fin k)), mainCnt st (fun _ => false) = 0 := by intro st; unfold mainCnt; simp
  have hrowH : ∀ l, 3 ≤ l → l ≤ k → rowS k (Finset.univ : Finset (Fin k)) (fun _ => 1) l = (k : ℝ) * ((k : ℝ) - 1) := by
    intro l h3 hl
    unfold rowS
    simp [Finset.card_univ, hl, show 1 < l by omega]
    ring
  have hrowP : ∀ l, 3 ≤ l → rowS k ({⟨0, by omega⟩, ⟨1, by omega⟩} : Finset (Fin k)) (fun _ => 2) l = 0 := by
    intro l h3
    unfold rowS
    have : ¬ (l ≤ 2) := by omega
    simp [hpair, this]
  have hrowL : ∀ l, 3 ≤ l → rowS k ({⟨0, by omega⟩} : Finset (Fin k)) (fun _ => 1) l = 0 := by
    intro l h3
    unfold rowS
    have : ¬ (l ≤ 1) := by omega
    simp [this]
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · intro r; rcases r with _ | _ | _ <;> simp [cfgQ, hpair] <;> omega
  · intro r; rcases r with _ | _ | _ <;> simp [cfgQ]
  · intro r; rcases r with _ | _ | _ <;> intro s hs <;> simp [cfgQ, hpair] <;> omega
  · intro r; rcases r with _ | _ | _ <;> intro s hs h <;> simp_all [cfgQ]
  · show 2 * (k : ℝ) ≤ ∑ r : Fin 2 ⊕ Fin (k - 4) ⊕ Fin (k + 2),
      (if 2 ≤ ((cfgQ k hk).st r).card then mainCnt ((cfgQ k hk).st r) ((cfgQ k hk).mn r) else 0)
    rw [Fintype.sum_sum_type, Fintype.sum_sum_type]
    simp [cfgQ, hmcT, hmcF, hpair, Finset.card_univ]
    rw [if_pos (by omega)]
  · intro l h3 hl
    show 2 * (k : ℝ) * ((k : ℝ) - 1) ≤ ∑ r : Fin 2 ⊕ Fin (k - 4) ⊕ Fin (k + 2),
      rowS k ((cfgQ k hk).st r) ((cfgQ k hk).a r) l
    rw [Fintype.sum_sum_type, Fintype.sum_sum_type]
    simp [cfgQ, hrowH l h3 hl, hrowP l h3, hrowL l h3]
    linarith
  · show (k : ℝ) - 2 ≤ ((Finset.univ.filter (fun r : Fin 2 ⊕ Fin (k - 4) ⊕ Fin (k + 2) => 2 ≤ ((cfgQ k hk).st r).card)).card : ℝ)
    rw [Finset.card_filter]
    rw [Fintype.sum_sum_type, Fintype.sum_sum_type]
    simp [cfgQ, hpair]
    have hc : ((k - 4 : ℕ) : ℝ) = (k : ℝ) - 4 := by rw [Nat.cast_sub hk]; norm_num
    rw [if_pos (by omega), hc]
    linarith
  · show (k : ℝ) * (2 * k - 2) ≤ k * (Fintype.card (Fin 2 ⊕ Fin (k - 4) ⊕ Fin (k + 2)) : ℝ)
      - ((Finset.univ.filter (fun r : Fin 2 ⊕ Fin (k - 4) ⊕ Fin (k + 2) => ((cfgQ k hk).st r).card = 1)).card : ℝ)
    rw [Finset.card_filter]
    rw [Fintype.sum_sum_type, Fintype.sum_sum_type]
    simp [cfgQ, hpair, Fintype.card_sum]
    have hc : ((k - 4 : ℕ) : ℝ) = (k : ℝ) - 4 := by rw [Nat.cast_sub hk]; norm_num
    have hk1 : ¬ (k = 1) := by omega
    have hkr : (4 : ℝ) ≤ k := by exact_mod_cast hk
    simp only [if_neg hk1, hc]
    nlinarith

/-- the headline applies to a genuine configuration (k = 77). -/
theorem nonvac_77 : (cfgQ 77 (by norm_num)).valQ < 128891 / 1000 :=
  valQ_lt (by norm_num) _ (cfgQ_law 77 (by norm_num))

end inst

end CallerHP

#print axioms CallerHP.role_leQ
#print axioms CallerHP.valQ_le_F2
#print axioms CallerHP.F2_lt
#print axioms CallerHP.valQ_lt
#print axioms CallerHP.cfgQ_law
#print axioms CallerHP.nonvac_77
