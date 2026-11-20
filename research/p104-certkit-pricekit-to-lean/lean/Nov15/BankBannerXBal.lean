/-
BankBannerXBal (lane LEAN-BANNER, Nov 18).  Discharges the X ≥ 2D hypothesis of BankBanner.bank_kappa_lt_banner from
LEAN-XBAL's chart-conservation model (XBalA: XBal.Model.X_ge).
  model_D / model_X : an XBal.Model whose moves are the banks and whose publics are the fields of G, with heights = ht,
                      has Model.D = descMass G and Model.X = excess G.
  xbal_bank         : Flow + W ≥ 0 (owned registers net non-descending; W = 0 with no owned) ⟹ 2·descMass G ≤ excess G.
  bank_kappa_lt_banner_xbal : bank_kappa_lt_banner with hXD replaced by per-call XBal models (Flow, W ≥ 0).
Kernel only.
-/
import Nov15.BankBanner
import Nov15.XBalA

namespace BankBanner
open Finset Module BankNC0 BankHelp BankFit SafeRungsPrice BankFitHS

variable {K : Type} {Fld Bank : Type} [Field K] [Fintype Fld] [DecidableEq Fld]
  [Fintype Bank] [LinearOrder Bank]

/-- an XBal model of G: banks = moves, fields = publics, chart heights = ht. -/
structure XModel (G : BankedGraph K Fld Bank) (C O : Type) [Fintype C] [DecidableEq C] [Fintype O] where
  M : XBal.Model C Bank Fld O
  hsrc : ∀ k, M.h (M.src k) = (ht (G.N.src k) : ℤ)
  hdst : ∀ k, M.h (M.dst k) = (ht (G.N.dst k) : ℤ)
  hini : ∀ f, M.h (M.ini f) = (ht (G.N.A f) : ℤ)
  hfin : ∀ f, M.h (M.fin f) = (ht (G.N.B f) : ℤ)

variable {C O : Type} [Fintype C] [DecidableEq C] [Fintype O]

theorem model_D (G : BankedGraph K Fld Bank) (Z : XModel G C O) : Z.M.D = descMass G := by
  unfold XBal.Model.D XBal.Model.delta descMass
  refine Finset.sum_congr rfl fun k _ => ?_
  rw [Z.hsrc, Z.hdst]; congr 1; ring

theorem model_X (G : BankedGraph K Fld Bank) (Z : XModel G C O) : Z.M.X = excess G := by
  unfold XBal.Model.X XBal.Model.absMass XBal.Model.climb XBal.Model.delta excess
  congr 1
  · refine Finset.sum_congr rfl fun k _ => ?_
    rw [Z.hsrc, Z.hdst]; simp only [dh]; push_cast
    exact abs_sub_comm _ _
  · refine Finset.sum_congr rfl fun f _ => ?_
    rw [Z.hini, Z.hfin]
    have := (G.climb f).2
    simp only [ht]; omega

theorem xbal_bank (G : BankedGraph K Fld Bank) (Z : XModel G C O) (hF : Z.M.Flow) (hW : 0 ≤ Z.M.W) :
    2 * descMass G ≤ excess G := by
  have := XBal.Model.X_ge Z.M hF hW
  rwa [model_D, model_X] at this

/-- **#7761** banner with X ≥ 2D discharged by chart conservation (XBal); remaining hypothesis: D ≥ 56. -/
theorem bank_kappa_lt_banner_xbal (G : Fin 2048 → BankedGraph K Fld Bank) (hc : ∀ i, HSContract (G i).N)
    (hD : ∀ i, 56 ≤ descMass (G i))
    (Z : ∀ i, XModel (G i) C O) (hF : ∀ i, (Z i).M.Flow) (hW : ∀ i, 0 ≤ (Z i).M.W)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (paid : Fin 2048 → Bank → ℝ) (hpaid : ∀ i k, bankPrice (G i) (1 - κ) k ≤ paid i k)
    (hcaller : ∑ i, ∑ k, paid i k - ∑ i, helperCredit (G i).N (1 - κ) (G i).Mn ≤
      cdat (1 - κ) BankBannerCert.TB - cdat (1 - κ) BankBannerCert.PB) :
    κ < 2381707 / 250000000 :=
  bank_kappa_lt_banner G hc hD (fun i => xbal_bank (G i) (Z i) (hF i) (hW i)) κ hκ0 hκ1 paid hpaid hcaller

end BankBanner
#print axioms BankBanner.xbal_bank
#print axioms BankBanner.bank_kappa_lt_banner_xbal
