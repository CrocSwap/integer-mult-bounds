/-
CallerWordHP (lane CALLERWORD, Nov 20).  TIGHTNESS IS WLOG for KASYM's HP law: the role-count hypothesis
`n = 2k-2` of CallerHP.total_le / frame_bound can be weakened to `n ≤ 2k-2` (each role's dual budget is
v2p = 17^s - 16^s > 0, so fewer roles only lower the bound).  With CallerWord.role_count_lam this is exactly what
a legal Q = 0 caller supplies (n + 2 ≤ #columns = 2k when λ ≠ -1 at one stage).
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Nov15.CallerHP

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace CallerHP
open Finset Set

theorem v2p_pos {σ : ℝ} (h0 : 0 < σ) : 0 < v2p σ := by
  unfold v2p
  have := Real.rpow_lt_rpow (by norm_num : (0:ℝ) ≤ 16) (by norm_num : (16:ℝ) < 17) h0
  linarith

theorem total_le_le {σ : ℝ} {k : ℕ} {R : Type*} [Fintype R] {τ : Type*} (hq : QF σ) (h0 : 0 < σ) (h1 : σ < 1)
    (hk : 3 ≤ k) (st : R → Finset τ) (a : R → τ → ℕ) (mn : R → τ → Bool)
    (hD2 : ∀ r, 2 ≤ (st r).card) (hDk : ∀ r, (st r).card ≤ k)
    (ha1 : ∀ r, ∀ s ∈ st r, 1 ≤ a r s) (haD : ∀ r, ∀ s ∈ st r, a r s ≤ (st r).card)
    (hmain : ∀ r, ∀ s ∈ st r, mn r s = true → a r s = 1)
    (hcard : (Fintype.card R : ℝ) ≤ 2 * (k : ℝ) - 2)
    (hrc : ∀ l ∈ Finset.Icc 3 k, 2 * (k : ℝ) * ((k : ℝ) - 1) ≤ ∑ r, rowS k (st r) (a r) l)
    (hmains : 2 * (k : ℝ) ≤ ∑ r, mainCnt (st r) (mn r)) :
    ∑ r, roleVal σ (st r) (a r) ≤ 2 * (((k : ℝ) - 2) * v2p σ + (8 * (k : ℝ) + 1) ^ σ - (8 : ℝ) ^ σ * k) := by
  have hk3 := hk_real hk
  have hk1 : (0 : ℝ) < (k : ℝ) - 1 := by linarith
  have hwm := wm_nonneg hq hk
  have hv := (v2p_pos (σ := σ) h0).le
  have hc : (Fintype.card R : ℝ) * v2p σ ≤ (2 * (k : ℝ) - 2) * v2p σ := mul_le_mul_of_nonneg_right hcard hv
  have hs := Finset.sum_le_sum (fun r (_ : r ∈ (Finset.univ : Finset R)) =>
    role_le hq h0 h1 hk (st r) (a r) (mn r) (hD2 r) (hDk r) (ha1 r) (haD r) (hmain r))
  rw [Finset.sum_add_distrib, Finset.sum_add_distrib, ← Finset.mul_sum, Finset.sum_const,
    Finset.card_univ, nsmul_eq_mul] at hs
  simp only [div_eq_mul_inv, ← Finset.sum_mul] at hs
  have hswap : ∑ r, ∑ l ∈ Finset.Icc 3 k, wt σ k l * rowS k (st r) (a r) l
      = ∑ l ∈ Finset.Icc 3 k, wt σ k l * ∑ r, rowS k (st r) (a r) l := by
    simp_rw [Finset.mul_sum]
    exact Finset.sum_comm
  rw [hswap] at hs
  have hY : 2 * (k : ℝ) * ((k : ℝ) - 1) * Tt σ k
      ≤ ∑ l ∈ Finset.Icc 3 k, wt σ k l * ∑ r, rowS k (st r) (a r) l := by
    rw [← sum_wt_all hk, Finset.mul_sum]
    refine Finset.sum_le_sum fun l hl => ?_
    rw [Finset.mem_Icc] at hl
    have := wt_nonneg hq hk hl.1 hl.2
    have h2 := hrc l (Finset.mem_Icc.mpr hl)
    nlinarith
  generalize (∑ l ∈ Finset.Icc 3 k, wt σ k l * ∑ r, rowS k (st r) (a r) l) = Y at *
  generalize (∑ r, mainCnt (st r) (mn r)) = MC at *
  have hY2 : 2 * (k : ℝ) * Tt σ k ≤ Y * ((k : ℝ) - 1)⁻¹ := by
    rw [← div_eq_mul_inv, le_div_iff₀ hk1]; nlinarith
  have hMC : wm σ k * (2 * (k : ℝ)) ≤ wm σ k * MC := mul_le_mul_of_nonneg_left hmains hwm
  have hslm := sl_mul (σ := σ) hk
  have hhk : hh σ k = k * qq σ k := hh_eq _ (by positivity)
  unfold hh at hhk
  unfold Tt wm at *
  nlinarith [hs, hY2, hMC, hslm, hhk, hc]

section frame
open CallerSign
variable {K : Type*} [Field K] {k : ℕ}

/-- frame_bound with the role count weakened to n + 2 ≤ 2k (tightness WLOG). -/
theorem frame_bound_le {R : Type} [Fintype R] [DecidableEq R] (hk : 3 ≤ k) (M : R → Finset (Fin k))
    (bh ah : R → Fin k → Fin 2 → K)
    (hbh : ∀ r s, s ∉ M r → ∀ a, bh r s a = 0) (hah : ∀ r s, s ∉ M r → ∀ a, ah r s a = 0)
    (P : Pieces M bh) (hG : ∀ s t, s ≠ t → IsUnit (gBlk bh ah s t).det)
    (main : R → Fin k → Bool) (hn : Fintype.card R + 2 ≤ 2 * k) (hdeg : ∀ r, 2 ≤ (M r).card)
    (hmain1 : ∀ r s, s ∈ M r → main r s = true → (P.pc r s).card = 1)
    (hmains : 2 * k ≤ ∑ r, ((M r).filter (fun s => main r s = true)).card) :
    104 / (k : ℝ) * ∑ r, roleVal σ0 (M r) (fun s => (P.pc r s).card) ≤ HPr k := by
  have hk3 : (3 : ℝ) ≤ k := by exact_mod_cast hk
  have hcard : (Fintype.card R : ℝ) ≤ 2 * (k : ℝ) - 2 := by
    have : ((Fintype.card R + 2 : ℕ) : ℝ) ≤ ((2 * k : ℕ) : ℝ) := by exact_mod_cast hn
    push_cast at this; linarith
  have hmains' : 2 * (k : ℝ) ≤ ∑ r, mainCnt (M r) (main r) := by
    have h2 : ((2 * k : ℕ) : ℝ) ≤ ((∑ r, ((M r).filter (fun s => main r s = true)).card : ℕ) : ℝ) := by
      exact_mod_cast hmains
    push_cast at h2
    simp only [mainCnt_eq]
    exact h2
  have hT := total_le_le qf_sigma0 (by norm_num : (0:ℝ) < σ0) (by norm_num : σ0 < 1) hk M
    (fun r s => (P.pc r s).card) main hdeg (fun r => card_le_k _)
    (fun r s hs => Finset.card_pos.mpr ⟨s, P.pc_mem r s hs⟩)
    (fun r s hs => Finset.card_le_card (P.pc_sub r s hs)) (fun r s hs hm => hmain1 r s hs hm) hcard
    (fun l hl => rc2_rows_real M bh ah hbh hah P hG (by omega) l (by have := (Finset.mem_Icc.mp hl).1; omega))
    hmains'
  unfold HPr
  have hk0 : (0 : ℝ) < k := by linarith
  calc 104 / (k : ℝ) * ∑ r, roleVal σ0 (M r) (fun s => (P.pc r s).card)
      ≤ 104 / (k : ℝ) * (2 * (((k : ℝ) - 2) * v2p σ0 + (8 * (k : ℝ) + 1) ^ σ0 - (8 : ℝ) ^ σ0 * k)) :=
        mul_le_mul_of_nonneg_left hT (by positivity)
    _ = _ := by ring

end frame
end CallerHP

#print axioms CallerHP.total_le_le
#print axioms CallerHP.frame_bound_le
