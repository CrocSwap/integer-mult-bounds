/-
Bridge7761S2 (lane BRIDGE7, Nov 18).  FINAL ASSEMBLY for #7761, conditional on the single expansion identity hO (BRIDGE-OUT) and the SPEC statement Valid:
  G7761 hO       : BankedGraph ℚ (Fin 1262) (Fin 5746)   (N = Net7761 hO, minors, Contract (S1), nest, climb/cl/Mn/main8/card (R2/R3))
  HS7761 hO      : HSContract (G7761 hO).N                (G2: π = piF, Ehi/Elo 104+104)
  Z7761 hO       : XModel (G7761 hO) CF Empty             (the XBal model of Bridge7761XB0 IS the graph's chart-height model: srcId/dstId/fA/fB = bS/bT/fA/fB)
  descMass7761   : descMass G = 56 EXACTLY  (D7761 + model_D);   xd7761 : 2·descMass ≤ excess  (flow7761, W = 0 + xbal_bank)
  kappa7761_lt_banner : κ < 2381707/250000000 for the caller block (TB, PB) of 2048 copies of G7761, hypotheses: hO and Valid only.
NOTE: D ≥ 56 is read off the data (descMass G = 56 exactly), so the chain-tie route (ChainTie, ComputesS, hin, hout, hcov) is not needed for this concrete graph.
Kernel only.
-/
import Nov15.Bridge7761S1
import Nov15.Bridge7761F2
import Nov15.Bridge7761F1
import Nov15.BankPrem
import Nov15.BankBannerXBal

namespace Bridge7761
open Finset Module BankNC0 BankWireC BankFit BankHelp BankBanner SafeRungsPrice BankFitHS BankPrem BankBanner

theorem srcId_eq (k : ℕ) : srcId k = bS.getD k 0 := by
  unfold srcId; rw [← pack_bS]
  exact pkw_get 11 bS (fun x hx => by have := lt_bS x hx; omega) k
theorem dstId_eq (k : ℕ) : dstId k = bT.getD k 0 := by
  unfold dstId; rw [← pack_bT]
  exact pkw_get 11 bT (fun x hx => by have := lt_bT x hx; omega) k
theorem fAK_eq (f : ℕ) : sl FAK 11 f = fA.getD f 0 := by
  rw [← pack_fA]; exact pkw_get 11 fA lt_fA' f
theorem fBK_eq (f : ℕ) : sl FBK 11 f = fB.getD f 0 := by
  rw [← pack_fB]; exact pkw_get 11 fB lt_fB' f

noncomputable def G7761 (hO : ∀ f, outVec Recipe7761 (ofld7761 f) (oref7761 f) = O7761 f) :
    BankedGraph ℚ (Fin 1262) (Fin 5746) where
  N := Net7761 hO
  minors := Net7761_minors hO
  con := Con7761 hO
  nest := Net7761_nest hO
  cl := cl7761
  climb := climbA7761
  Mn := Mn7761
  main8 := main8_7761
  card := card_Mn7761

noncomputable def HS7761 (hO : ∀ f, outVec Recipe7761 (ofld7761 f) (oref7761 f) = O7761 f) :
    HSContract (G7761 hO).N where
  π := piF
  πinj := piF_inj
  hsupp := fun f g h => hsupp7761 f g h
  Ehi := Ehi7761
  Elo := Elo7761
  hi_card := Ehi_card
  lo_card := Elo_card
  hi_h := hi_h7761
  lo_h := lo_h7761
  nz_hi := nz_hi7761
  nz_lo := nz_lo7761

noncomputable def Z7761 (hO : ∀ f, outVec Recipe7761 (ofld7761 f) (oref7761 f) = O7761 f) :
    XModel (G7761 hO) CF Empty where
  M := model
  hsrc := fun k => by
    have hk := srcId_lt k k.2
    show hgt (bS.getD (k : ℕ) 0 % 1099) = ((finrank (ZMod 2) (chartOf (srcId k)) : ℕ) : ℤ)
    rw [finrank_chartOf _ hk, srcId_eq, hp_eq]
  hdst := fun k => by
    have hk := dstId_lt k k.2
    show hgt (bT.getD (k : ℕ) 0 % 1099) = ((finrank (ZMod 2) (chartOf (dstId k)) : ℕ) : ℤ)
    rw [finrank_chartOf _ hk, dstId_eq, hp_eq]
  hini := fun f => by
    show hgt (fA.getD (f : ℕ) 0 % 1099) = ((finrank (ZMod 2) (ChA7761 f) : ℕ) : ℤ)
    rw [finrank_A, fAK_eq, hp_eq]
  hfin := fun f => by
    show hgt (fB.getD (f : ℕ) 0 % 1099) = ((finrank (ZMod 2) (ChB7761 f) : ℕ) : ℤ)
    rw [finrank_B, fBK_eq, hp_eq]

theorem descMass7761 (hO : ∀ f, outVec Recipe7761 (ofld7761 f) (oref7761 f) = O7761 f) :
    descMass (G7761 hO) = 56 := by
  rw [← model_D (G7761 hO) (Z7761 hO)]; exact D7761

theorem xd7761 (hO : ∀ f, outVec Recipe7761 (ofld7761 f) (oref7761 f) = O7761 f) :
    2 * descMass (G7761 hO) ≤ excess (G7761 hO) :=
  xbal_bank (G7761 hO) (Z7761 hO) flow7761 (by have := W7761; show 0 ≤ model.W; rw [this])

/-- the caller block of #7761: 2048 copies of the native graph, T/P = the BankBannerCert lists. -/
noncomputable def caller7761 (hO : ∀ f, outVec Recipe7761 (ofld7761 f) (oref7761 f) = O7761 f) :
    Caller ℚ (Fin 1262) (Fin 5746) 2048 where
  G := fun _ => G7761 hO
  T := BankBannerCert.TB
  P := BankBannerCert.PB

/-- **FINAL**: κ_7761 < 2381707/250000000, hypotheses: hO (outVec = O7761, BRIDGE-OUT) and Valid (κ is a crossing of the SPEC invoice). -/
theorem kappa7761_lt_banner (hO : ∀ f, outVec Recipe7761 (ofld7761 f) (oref7761 f) = O7761 f)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid (caller7761 hO) (1 - κ) (fun i k => specInvoice ((caller7761 hO).G i) (1 - κ) k)) :
    κ < 2381707 / 250000000 :=
  bank_kappa_lt_banner_spec (caller7761 hO) rfl rfl (fun _ => HS7761 hO)
    (fun _ => le_of_eq (descMass7761 hO).symm) (fun _ => xd7761 hO) κ hκ0 hκ1 hV

end Bridge7761
#print axioms Bridge7761.G7761
#print axioms Bridge7761.descMass7761
#print axioms Bridge7761.kappa7761_lt_banner
