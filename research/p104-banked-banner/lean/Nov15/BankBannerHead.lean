/-
BankBannerHead .  Composition only, no new mathematics:
  BankMed.bank_kappa_lt_banner_tiedS_loc  (Mediated discharged; D ≥ 56 and X ≥ 2D derived from the chain tie + XBal)
  + BankPrem.bankPrice_le_specInvoice     (P-1S' discharged with paid := SPEC invoice)
  + BankPrem.hcaller_of_valid             (P-CALLER' reduced to Valid: κ is a crossing of the SPEC invoice)
  ⟹ κ < 2381707/250000000 on #7761's caller block (T/P = BankBannerCert lists).
-/
import Nov15.BankMedA
import Nov15.BankPrem

namespace BankBannerHead
open Finset Module BankNC0 BankWireC BankFit BankHelp BankBanner SafeRungsPrice BankFitHS BankTie BankPrem DecoderWall

variable {Fld Bank : Type} [Fintype Fld] [DecidableEq Fld] [Fintype Bank] [LinearOrder Bank]

/-- **headline**: banner for the banked class, chain-tied, with P-1S' proved and P-CALLER' = Valid. -/
theorem bank_kappa_lt_banner_head (c : Caller ℚ Fld Bank 2048)
    (hT : c.T = BankBannerCert.TB) (hP : c.P = BankBannerCert.PB)
    (hc : ∀ i, HSContract (c.G i).N)
    {T : Type} [Fintype T] (τ : ∀ i, ChainTie (c.G i) T) (h8 : Fintype.card T ≤ 8) (cs : Fin 2048 → Fin 104 → ℚ)
    (hC : ∀ i, ComputesS (c.G i) (τ i).xin (τ i).yout (cs i))
    (hin : ∀ i p, DF.lq p ∈ (c.G i).N.A ((τ i).xin p))
    (hout : ∀ i s, ∀ y ∈ (c.G i).N.B ((τ i).yout s), dot (DF.lq s) y = 0)
    (hcov : ∀ i k, ¬ (c.G i).N.src k ≤ (c.G i).N.dst k → ∃ x, (τ i).e x = k)
    {O : Type} [Fintype O] (oi oc : Fin 2048 → O → Chart)
    (hF : ∀ i, (gModel (c.G i) (oi i) (oc i)).Flow) (hW : ∀ i, 0 ≤ (gModel (c.G i) (oi i) (oc i)).W)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid c (1 - κ) (fun i k => specInvoice (c.G i) (1 - κ) k)) :
    κ < 2381707 / 250000000 :=
  BankMed.bank_kappa_lt_banner_tiedS_loc c.G hc τ h8 cs hC hin hout hcov oi oc hF hW κ hκ0 hκ1 _
    (fun i k => bankPrice_le_specInvoice (c.G i) (by linarith) k)
    (by have := hcaller_of_valid c _ _ hV; rw [hT, hP] at this; exact this)

end BankBannerHead
#print axioms BankBannerHead.bank_kappa_lt_banner_head
