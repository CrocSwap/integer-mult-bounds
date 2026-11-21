/-
EasyWireC (lane EASYWIRE, Nov 20).  Wrappers using `EasyWireK.hlam_of_ab` (hlam <=> a_s b_s /= -1 for type-B words) and `legal_frame`.
 C13: `legal_sg_laws`   a legal odd caller word satisfies P = -1 (DERIVED, not assumed) and then every CallerSGram law:
                       rank K + n <= |iota|, rank G = n, A H B^T = -2, tight => rank K <= 2.
      `legal_hG`/`legal_rc2_pair` the RC2 pair form / Ghat_st invertibility for type-B words: only a_s b_s /= -1 left (no P, no hlam).
 C10: `word_hp_B_ab`  word_hp_B with hlam replaced by a_s b_s /= -1;   `c1_hp_full` = QZERO's C1 word: cHat C1W <= HP(3) with NO hypothesis.
 C14: `word_hpq_ab`    word_hpq (type B) with hlam replaced by a_s b_s /= -1.
Kernel only.
-/
import Nov15.EasyWireK
import Nov15.CallerCfgBridge
import Nov15.CallerQZero

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace EasyWire
open Matrix Finset CallerSign CallerWord CallerAsm CallerHP

variable {n k : ℕ} {w : CWord n k}

/-- C13, word form: P_k = -1 is derived from legality; all CallerSGram consequences follow. -/
theorem legal_sg_laws (hL : Legal w) (hodd : ∀ r, w.ex r % 2 = 1) :
    sgProd (Aw w Complex.I) (Bw w Complex.I) (βw w) w.evs.length = -1 ∧
    (sgK (βw w) (sgG (Aw w Complex.I) (Bw w Complex.I))).rank + n ≤ Fintype.card (Iota w) ∧
    (sgG (Aw w Complex.I) (Bw w Complex.I)).rank = n ∧
    Aw w Complex.I * (1 - sgLow (βw w) (sgG (Aw w Complex.I) (Bw w Complex.I)))⁻¹ * (Bw w Complex.I)ᵀ
      = (-2 : ℂ) • (1 : Matrix (Fin n) (Fin n) ℂ) ∧
    (n + 2 = Fintype.card (Iota w) → (sgK (βw w) (sgG (Aw w Complex.I) (Bw w Complex.I))).rank ≤ 2) := by
  obtain ⟨hP, h1, h2⟩ := legal_frame w hL hodd
  refine ⟨hP, h1, h2, sg_AHB _ _ (βw w) w.evs.length (beta_lt w) hP, fun hn => by omega⟩

/-- C13: Ghat_st invertible for a tight legal type-B word: only `a_s b_s /= -1` remains. -/
theorem legal_hG (hL : Legal w) (J : JB w) (hodd : ∀ r, w.ex r % 2 = 1)
    (hn : n + 2 = Fintype.card (Iota w)) (hab : ∀ s, J.a s * J.b s ≠ -1) (s t : Fin k) (hst : s ≠ t) :
    IsUnit (gBlk (fun r s a => Bw w Complex.I r (J.sch.col s a))
      (fun r s a => Aw w Complex.I r (J.sch.col s a)) s t).det :=
  word_hG hL J.sch hodd hn (hlam_of_ab hL J hab) s t hst

/-- C13: RC2 pair form of a tight legal type-B word, event-indexed. -/
theorem legal_rc2_pair (hL : Legal w) (J : JB w) (hodd : ∀ r, w.ex r % 2 = 1)
    (hn : n + 2 = Fintype.card (Iota w)) (hab : ∀ s, J.a s * J.b s ≠ -1)
    (s t : Fin k) (hst : s ≠ t) (l : ℕ) :
    2 + (CallerEv.gSet (evS w) s t l).card ≤ (CallerEv.wSet w.mask s t l).card :=
  word_rc2_pair hL J.sch hodd hn (hlam_of_ab hL J hab) s t hst l

/-- C10 headline, type B, with `hlam` replaced by the explicit coefficient condition. -/
theorem word_hp_B_ab (hL : Legal w) (J : JB w) (hodd : ∀ r, w.ex r % 2 = 1) (hk : 3 ≤ k)
    (hQ0 : Fintype.card (Iota w) = 2 * k) (hn : n + 2 = Fintype.card (Iota w))
    (hab : ∀ s, J.a s * J.b s ≠ -1) (hdeg : ∀ r, 2 ≤ (w.mask r).card) :
    cHat w ≤ HPr k :=
  word_hp_B hL J hodd hk hQ0 hn (hlam_of_ab hL J hab) hdeg

/-- C14 headline, type B, with `hlam` replaced by the explicit coefficient condition. -/
theorem word_hpq_ab (hL : Legal w) (J : JB w) (hodd : ∀ r, w.ex r % 2 = 1) (hk : 77 ≤ k)
    (hn : n + 2 = Fintype.card (Iota w)) (hab : ∀ s, J.a s * J.b s ≠ -1)
    (hdeg1 : ∀ r, 1 ≤ (w.mask r).card) :
    CallerBridge.cHatQ w < 128891 / 1000 :=
  CallerBridge.word_hpq hL J hodd hk hn (hlam_of_ab hL J hab) hdeg1

/-! ### C10 non-vacuity at word level: QZERO's legal C1 word, nothing left to assume -/
theorem c1_hab : ∀ s, CallerQZero.c1J.a s * CallerQZero.c1J.b s ≠ -1 := by
  intro s
  fin_cases s <;> simp [CallerQZero.c1J] <;> norm_num

theorem c1_hlam : ∀ s, IsUnit ((sgK (βw CallerQZero.C1W) (sgG (Aw CallerQZero.C1W Complex.I) (Bw CallerQZero.C1W Complex.I))).submatrix
    (CallerQZero.c1J.col s) (CallerQZero.c1J.col s)).det :=
  hlam_of_ab CallerQZero.c1_legal CallerQZero.c1J c1_hab

/-- the three K-block determinants of C1 are exactly 2, -4, -5 (as in the [C] note). -/
theorem c1_kdets : ∀ s, ((sgK (βw CallerQZero.C1W) (sgG (Aw CallerQZero.C1W Complex.I) (Bw CallerQZero.C1W Complex.I))).submatrix
    (CallerQZero.c1J.col s) (CallerQZero.c1J.col s)).det = ![(2 : ℂ), -4, -5] s := by
  intro s
  have hb : replay (1 : ℂ) Complex.I 1 CallerQZero.C1W.evs = 1 := by
    have h1 := (legal_pm _ CallerQZero.c1_legal).1
    unfold LegalAt at h1
    rw [h1]; unfold target; simp [one_qp]
  rw [kblock_det hb]
  fin_cases s <;> simp [CallerQZero.c1J] <;> norm_num

/-- word-level non-vacuity of word_hp_B: the explicit legal Q = 0 word C1 (n = 4, k = 3) meets EVERY hypothesis, hlam included. -/
theorem c1_hp_full : cHat CallerQZero.C1W ≤ HPr 3 :=
  word_hp_B_ab CallerQZero.c1_legal CallerQZero.c1J CallerQZero.c1_odd (le_refl 3) CallerQZero.c1_card
    (by rw [CallerQZero.c1_card]) c1_hab CallerQZero.c1_deg

/-- and the C13 laws for C1 (P = -1 derived). -/
theorem c1_P : sgProd (Aw CallerQZero.C1W Complex.I) (Bw CallerQZero.C1W Complex.I) (βw CallerQZero.C1W)
    CallerQZero.C1W.evs.length = -1 :=
  (legal_sg_laws CallerQZero.c1_legal CallerQZero.c1_odd).1

theorem c1_rankK : (sgK (βw CallerQZero.C1W) (sgG (Aw CallerQZero.C1W Complex.I) (Bw CallerQZero.C1W Complex.I))).rank ≤ 2 :=
  (legal_sg_laws CallerQZero.c1_legal CallerQZero.c1_odd).2.2.2.2 (by rw [CallerQZero.c1_card])

end EasyWire

#print axioms EasyWire.legal_sg_laws
#print axioms EasyWire.legal_hG
#print axioms EasyWire.legal_rc2_pair
#print axioms EasyWire.word_hp_B_ab
#print axioms EasyWire.word_hpq_ab
#print axioms EasyWire.c1_hlam
#print axioms EasyWire.c1_kdets
#print axioms EasyWire.c1_hp_full
#print axioms EasyWire.c1_P
#print axioms EasyWire.c1_rankK
