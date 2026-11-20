/-
Bridge7761T4 (lane CHAINTIE, Nov 18).  #7761 inhabits the HEADLINE's full premise set (BankBannerHead.bank_kappa_lt_banner_head):
  cnt_push / gflow7761 / gW7761 : Flow and W = 0 of the BankTieB `gModel` of G7761 (no owned registers), transferred from the XB0 model's
                                  `flow7761` along the chart map c ↦ chartOf c (conservation pushes forward along any chart map);
  kappa7761_lt_banner_head      : κ < 2381707/250000000 for #7761's caller block; hypotheses: ONLY Valid (SPEC invoice crossing) -- instance of
                                  bank_kappa_lt_banner_head with ChainTie τ7761, ComputesS (c = cc), hin/hout (O1), hcov (T3), Flow/W above.
Kernel only.
-/
import Nov15.Bridge7761T3
import Nov15.BankBannerHead

namespace Bridge7761
open Finset Module BankNC0 BankWireC BankFit BankHelp BankBanner SafeRungsPrice BankFitHS BankPrem BankTie

theorem cnt_push {C C' α : Type} [Fintype C] [DecidableEq C] [Fintype C'] [DecidableEq C'] [Fintype α]
    (f : α → C) (φ : C → C') (c' : C') :
    XBal.Model.cnt (fun a => φ (f a)) c' = ∑ x ∈ univ.filter (fun x => φ x = c'), XBal.Model.cnt f x := by
  unfold XBal.Model.cnt
  have h := Finset.card_eq_sum_card_fiberwise (s := univ.filter (fun a => φ (f a) = c')) (t := univ.filter (fun x => φ x = c'))
    (f := f) (fun a ha => by simpa using ha)
  rw [h]; push_cast
  refine Finset.sum_congr rfl fun x hx => ?_
  simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hx
  congr 2
  ext a
  simp only [Finset.mem_filter, Finset.mem_univ, true_and]
  constructor
  · exact fun h => h.2
  · exact fun h => ⟨by rw [h, hx], h⟩

theorem cnt_empty {C α : Type} [Fintype C] [DecidableEq C] [Fintype α] [IsEmpty α] (f : α → C) (c : C) :
    XBal.Model.cnt f c = 0 := by
  unfold XBal.Model.cnt; simp

theorem srcId_lt1099 (k : Fin 5746) : srcId k % 1099 = srcId k := Nat.mod_eq_of_lt (srcId_lt k k.2)

noncomputable def phiC (c : CF) : Submodule (ZMod 2) V := chartOf c.val

theorem gM_src : ∀ k, (G7761 hO7761).N.src k = phiC (model.src k) := fun k => by
  show chartOf (srcId k) = chartOf ((bS.getD k 0) % 1099)
  rw [← srcId_eq, Nat.mod_eq_of_lt (srcId_lt k k.2)]
theorem gM_dst : ∀ k, (G7761 hO7761).N.dst k = phiC (model.dst k) := fun k => by
  show chartOf (dstId k) = chartOf ((bT.getD k 0) % 1099)
  rw [← dstId_eq, Nat.mod_eq_of_lt (dstId_lt k k.2)]
theorem gM_ini : ∀ f, (G7761 hO7761).N.A f = phiC (model.ini f) := fun f => by
  show chartOf (sl FAK 11 f) = chartOf ((fA.getD f 0) % 1099)
  rw [← fAK_eq, Nat.mod_eq_of_lt (fA_lt f f.2)]
theorem gM_fin : ∀ f, (G7761 hO7761).N.B f = phiC (model.fin f) := fun f => by
  show chartOf (sl FBK 11 f) = chartOf ((fB.getD f 0) % 1099)
  rw [← fBK_eq, Nat.mod_eq_of_lt (fB_lt f f.2)]

noncomputable def gM7761 : XBal.Model Chart (Fin 5746) (Fin 1262) Empty :=
  gModel (G7761 hO7761) (fun e : Empty => e.elim) (fun e : Empty => e.elim)

theorem gflow7761 : gM7761.Flow := by
  intro c'
  have hs : gM7761.src = fun k => phiC (model.src k) := funext gM_src
  have hd : gM7761.dst = fun k => phiC (model.dst k) := funext gM_dst
  have hi : gM7761.ini = fun f => phiC (model.ini f) := funext gM_ini
  have hf : gM7761.fin = fun f => phiC (model.fin f) := funext gM_fin
  rw [hs, hd, hi, hf, cnt_empty gM7761.oinit, cnt_empty gM7761.oclear, cnt_push, cnt_push, cnt_push, cnt_push]
  simp only [add_zero]
  rw [← Finset.sum_add_distrib, ← Finset.sum_add_distrib]
  refine Finset.sum_congr rfl fun x _ => ?_
  have := flow7761 x
  rw [cnt_empty model.oinit, cnt_empty model.oclear] at this
  simpa using this

theorem gW7761 : gM7761.W = 0 := by simp [XBal.Model.W]

theorem hC7761 (i : Fin 2048) : ComputesS ((caller7761 hO7761).G i) τ7761.xin τ7761.yout cc :=
  ⟨fun t => computes7761.1 t, fun t s hts _ => computes7761.2 t s hts⟩

/-- **#7761 inhabits the headline's full premise set**: only `Valid` (= the definition of κ as a crossing of the SPEC invoice) remains. -/
theorem kappa7761_lt_banner_head (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid (caller7761 hO7761) (1 - κ) (fun i k => specInvoice ((caller7761 hO7761).G i) (1 - κ) k)) :
    κ < 2381707 / 250000000 :=
  BankBannerHead.bank_kappa_lt_banner_head (caller7761 hO7761) rfl rfl (fun _ => HS7761 hO7761)
    (T := Fin 8) (fun _ => τ7761) (by simp) (fun _ => cc) hC7761
    (fun _ p => hin7761 p) (fun _ s y hy => hout7761 s y hy) (fun _ k h => hcov7761G k h)
    (fun _ => fun e : Empty => e.elim) (fun _ => fun e : Empty => e.elim)
    (fun _ => gflow7761) (fun _ => le_of_eq gW7761.symm)
    κ hκ0 hκ1 hV

end Bridge7761
#print axioms Bridge7761.gflow7761
#print axioms Bridge7761.gW7761
#print axioms Bridge7761.kappa7761_lt_banner_head
