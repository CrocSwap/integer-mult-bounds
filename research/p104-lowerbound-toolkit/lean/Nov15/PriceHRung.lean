/-
PriceHRung (lane PRICEH, Nov 20).  rung_port_h: UniPort.rung_port with `hprice` discharged by PriceH.price_h (S = 0), any label rank h >= 3.
Kernel only.
-/
import Nov15.WordRungPort
import Nov15.PriceH

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace PriceH
open Finset BankNC0 BankMassF

open SafeRungsPrice in
/-- **rung_port_h**: UniPort.rung_port with the per-call premise `hprice` DISCHARGED by price_h (S = 0), at any label rank h >= 3
with a molecule certificate `MD` and the budget premise `hbud` (the m1-budget on [kbar, 1]). -/
theorem rung_port_h (h n QR : ℕ) (hh : 3 ≤ h) (MD : MolData h) (ρD ρR kbar : ℝ) (L : ℕ) (T P : List (ℕ × ℕ))
    (hcert : Cert (fun s => cdat s T - cdat s P - (L : ℝ) * UniPort.PortInv n QR h ρD ρR 0 s) kbar)
    {Fld Bank : Fin L → Type} [∀ i, Fintype (Fld i)] [∀ i, DecidableEq (Fld i)] [∀ i, Fintype (Bank i)]
    (C : ∀ i, HCall h n QR (Fld i) (Bank i)) (Dm Rm : Fin L → ℝ)
    (hD : ∀ i, ρD * n ≤ Dm i) (hR : ∀ i, ρR * n ≤ Rm i) (hX : ∀ i, Dm i + Rm i ≤ (C i).excess)
    (κ : ℝ) (hκ0 : 0 ≤ κ) (hκ1 : κ < 1)
    (hbud : kbar ≤ κ → 0 ≤ bud h MD (fun d : ℕ => (d : ℝ) ^ (1 - κ)))
    (hV : cdat (1 - κ) P + ∑ i, (C i).spec (1 - κ) ≤ cdat (1 - κ) T + ∑ i, (C i).cred (1 - κ)) :
    κ < kbar := by
  refine UniPort.rung_port n QR h ρD ρR 0 kbar L T P hcert (fun i s => (C i).spec s) (fun i s => (C i).cred s)
    Dm Rm (fun i => (C i).excess) hD hR hX κ hκ1 ?_ hV
  intro hge i X hXi
  have := price_h MD hh (C i) (s := 1 - κ) (by linarith) (by linarith) (hbud hge) X hXi
  simp only [UniPort.PortInvX, UniPort.mains, zero_mul, add_zero]
  exact this

end PriceH

#print axioms PriceH.rung_port_h
