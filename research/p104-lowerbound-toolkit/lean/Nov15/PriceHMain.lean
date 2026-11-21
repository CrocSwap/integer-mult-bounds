/-
PriceHMain (lane PRICEH, Nov 20).  Rung instances at the PORTGEN danger label ranks h = 8 (half-spin 64, E7+A1) and h = 7 (E7),
plus h = 9 (P104's rank) and a NON-VACUITY instance of HCall/price_h at h = 8.
  rung_port_h7 / rung_port_h8 / rung_port_h9 : UniPort.rung_port with `hprice` DISCHARGED (price_h + molecule certificate md_h),
     for any (n, QR), any caller block (T,P) with an exact Cert of  cdat T - cdat P - L·PortInv n QR h ρD ρR 0,
     remaining premises: HCall cut contract `hcut` per call (the port set's height-cut lemma), wall densities ρD, ρR (D, R walls),
     budget `hbud` (m1-budget c_1 - Σ β_L c_L >= 0 on [kbar,1]; [C] true on (1e-5, 0.2] for every h in 4..19, not Lean-proved here).
  nonvac_h8: toy call n = 1, QR = 0 (fields (0,7),(1,8); banks fields + (1,0),(8,7)) satisfies the contract at h = 8; price_h at s = 1.
Kernel only.
-/
import Nov15.PriceHRung
import Nov15.PriceHI7
import Nov15.PriceHI8
import Nov15.PriceHI9

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace PriceH
open Finset BankNC0 SafeRungsPrice

theorem rung_port_h7 (n QR : ℕ) (ρD ρR kbar : ℝ) (L : ℕ) (T P : List (ℕ × ℕ))
    (hcert : Cert (fun s => cdat s T - cdat s P - (L : ℝ) * UniPort.PortInv n QR 7 ρD ρR 0 s) kbar)
    {Fld Bank : Fin L → Type} [∀ i, Fintype (Fld i)] [∀ i, DecidableEq (Fld i)] [∀ i, Fintype (Bank i)]
    (C : ∀ i, HCall 7 n QR (Fld i) (Bank i)) (Dm Rm : Fin L → ℝ)
    (hD : ∀ i, ρD * n ≤ Dm i) (hR : ∀ i, ρR * n ≤ Rm i) (hX : ∀ i, Dm i + Rm i ≤ (C i).excess)
    (κ : ℝ) (hκ0 : 0 ≤ κ) (hκ1 : κ < 1)
    (hbud : kbar ≤ κ → 0 ≤ bud 7 md7 (fun d : ℕ => (d : ℝ) ^ (1 - κ)))
    (hV : cdat (1 - κ) P + ∑ i, (C i).spec (1 - κ) ≤ cdat (1 - κ) T + ∑ i, (C i).cred (1 - κ)) :
    κ < kbar :=
  rung_port_h 7 n QR (by norm_num) md7 ρD ρR kbar L T P hcert C Dm Rm hD hR hX κ hκ0 hκ1 hbud hV

theorem rung_port_h8 (n QR : ℕ) (ρD ρR kbar : ℝ) (L : ℕ) (T P : List (ℕ × ℕ))
    (hcert : Cert (fun s => cdat s T - cdat s P - (L : ℝ) * UniPort.PortInv n QR 8 ρD ρR 0 s) kbar)
    {Fld Bank : Fin L → Type} [∀ i, Fintype (Fld i)] [∀ i, DecidableEq (Fld i)] [∀ i, Fintype (Bank i)]
    (C : ∀ i, HCall 8 n QR (Fld i) (Bank i)) (Dm Rm : Fin L → ℝ)
    (hD : ∀ i, ρD * n ≤ Dm i) (hR : ∀ i, ρR * n ≤ Rm i) (hX : ∀ i, Dm i + Rm i ≤ (C i).excess)
    (κ : ℝ) (hκ0 : 0 ≤ κ) (hκ1 : κ < 1)
    (hbud : kbar ≤ κ → 0 ≤ bud 8 md8 (fun d : ℕ => (d : ℝ) ^ (1 - κ)))
    (hV : cdat (1 - κ) P + ∑ i, (C i).spec (1 - κ) ≤ cdat (1 - κ) T + ∑ i, (C i).cred (1 - κ)) :
    κ < kbar :=
  rung_port_h 8 n QR (by norm_num) md8 ρD ρR kbar L T P hcert C Dm Rm hD hR hX κ hκ0 hκ1 hbud hV

theorem rung_port_h9 (n QR : ℕ) (ρD ρR kbar : ℝ) (L : ℕ) (T P : List (ℕ × ℕ))
    (hcert : Cert (fun s => cdat s T - cdat s P - (L : ℝ) * UniPort.PortInv n QR 9 ρD ρR 0 s) kbar)
    {Fld Bank : Fin L → Type} [∀ i, Fintype (Fld i)] [∀ i, DecidableEq (Fld i)] [∀ i, Fintype (Bank i)]
    (C : ∀ i, HCall 9 n QR (Fld i) (Bank i)) (Dm Rm : Fin L → ℝ)
    (hD : ∀ i, ρD * n ≤ Dm i) (hR : ∀ i, ρR * n ≤ Rm i) (hX : ∀ i, Dm i + Rm i ≤ (C i).excess)
    (κ : ℝ) (hκ0 : 0 ≤ κ) (hκ1 : κ < 1)
    (hbud : kbar ≤ κ → 0 ≤ bud 9 md9 (fun d : ℕ => (d : ℝ) ^ (1 - κ)))
    (hV : cdat (1 - κ) P + ∑ i, (C i).spec (1 - κ) ≤ cdat (1 - κ) T + ∑ i, (C i).cred (1 - κ)) :
    κ < kbar :=
  rung_port_h 9 n QR (by norm_num) md9 ρD ρR kbar L T P hcert C Dm Rm hD hR hX κ hκ0 hκ1 hbud hV

/-- NON-VACUITY: a concrete call at h = 8, n = 1, QR = 0. -/
def toy8 : HCall 8 1 0 (Fin 2) (Fin 4) where
  fa := ![0, 1]
  fb := ![7, 8]
  bs := ![0, 1, 1, 8]
  bt := ![7, 8, 0, 7]
  hfa := by decide
  hfb := by decide
  hbs := by decide
  hbt := by decide
  Mn := Finset.univ
  hmain := by decide
  hcard := by simp
  hcut := by
    intro m
    cases h0 : m.testBit 0 <;> cases h1 : m.testBit 1 <;> cases h7 : m.testBit 7 <;> cases h8 : m.testBit 8 <;>
      simp [xcut, isSepH, Fin.sum_univ_two, Fin.sum_univ_four, h0, h1, h7, h8]

/-- price_h on the toy call at s = 1, X = 2 (tight): 14 + 2 <= 16. -/
theorem nonvac_h8 :
    ((2 * 1 + 2 * 0 : ℕ) : ℝ) * ((8 : ℕ) - 1 : ℝ) ^ (1 : ℝ) + 2 * (((8 : ℕ) : ℝ) ^ (1 : ℝ) - ((8 : ℕ) - 1 : ℝ) ^ (1 : ℝ))
      + ((1 : ℕ) : ℝ) * (1 + ((8 : ℕ) - 2 : ℝ) ^ (1 : ℝ) - ((8 : ℕ) - 1 : ℝ) ^ (1 : ℝ))
      ≤ toy8.spec 1 - toy8.cred 1 := by
  refine price_h md8 (by norm_num) toy8 (s := 1) (by norm_num) le_rfl ?_ 2 ?_
  · have hz : ∀ L : ℕ, 1 ≤ L → ccg (fun d : ℕ => (d : ℝ) ^ (1 : ℝ)) L = 0 := by
      intro L hL
      obtain ⟨j, rfl⟩ : ∃ j, L = j + 1 := ⟨L - 1, by omega⟩
      simp only [ccg, Real.rpow_one, Nat.add_sub_cancel]
      push_cast; ring
    unfold bud
    rw [hz 1 le_rfl]
    rw [Finset.sum_eq_zero (fun L hL => by rw [hz L (by have := (Finset.mem_Icc.mp hL).1; omega), mul_zero])]
    norm_num
  · simp [HCall.excess, HCall.bankd, HCall.climb, toy8, dh, Fin.sum_univ_two, Fin.sum_univ_four]
    norm_num

end PriceH

#print axioms PriceH.rung_port_h7
#print axioms PriceH.rung_port_h8
#print axioms PriceH.rung_port_h9
