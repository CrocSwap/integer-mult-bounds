/-
NoFlowA (lane LEAN-NOFLOW, Nov 19).  Flow is NOT a premise (PREMSCOPE): for every BankedGraph G the owned registers
  O = Bank ⊕ Fld,  oi = (src k | B f),  oc = (dst k | A f)  balance chart flow (flow_canon), and for EVERY choice of
  owned registers with Flow, W (gModel G oi oc) = ascMass G - descMass G - climbG G   (W_of_flow).
  bank_kappa_lt_unified_noflow : the unified banner with oi/oc/hF/hW deleted and hW replaced by climbG + descMass ≤ ascMass.
  kappa7761_lt_unified_noflow  : #7761 (A 9721, D 56, Σc 9665 from Bridge7761F2); only Valid remains.
Kernel only.
-/
import Nov15.BankUnifyB

namespace NoFlow
open Finset Module BankNC0 BankHelp BankFit SafeRungsPrice BankFitHS BankBanner DecoderWall BankTie BankUnify
  ChainRow BankWireC BankPrem BankCallerGen BankBig ThmG

variable {Fld Bank : Type} [Fintype Fld] [DecidableEq Fld] [Fintype Bank] [LinearOrder Bank]

/-- ascent mass A of a banked graph. -/
noncomputable def ascMass (G : BankedGraph ℚ Fld Bank) : ℤ :=
  ∑ k, max ((ht (G.N.dst k) : ℤ) - ht (G.N.src k)) 0

/-- total public climb Σc. -/
noncomputable def climbG (G : BankedGraph ℚ Fld Bank) : ℤ := ∑ f, (G.cl f : ℤ)

section xmodel
variable (G : BankedGraph ℚ Fld Bank) {C O : Type} [Fintype C] [DecidableEq C] [Fintype O]

theorem model_A (Z : XModel G C O) : Z.M.A = ascMass G := by
  unfold XBal.Model.A XBal.Model.delta ascMass
  exact Finset.sum_congr rfl fun k _ => by rw [Z.hsrc, Z.hdst]

theorem model_climb (Z : XModel G C O) : Z.M.climb = climbG G := by
  unfold XBal.Model.climb climbG
  refine Finset.sum_congr rfl fun f _ => ?_
  rw [Z.hini, Z.hfin]
  have := (G.climb f).2
  simp only [ht]; omega

/-- **(2)** for ANY owned registers satisfying Flow: W = A - D - Σc. -/
theorem W_of_flow {O : Type} [Fintype O] (oi oc : O → Chart) (hF : (gModel G oi oc).Flow) :
    (gModel G oi oc).W = ascMass G - descMass G - climbG G := by
  have h := XBal.Model.telescope (gModel G oi oc) hF
  have e1 : (gModel G oi oc).A = ascMass G := model_A G (gX G oi oc)
  have e2 : (gModel G oi oc).D = descMass G := model_D G (gX G oi oc)
  have e3 : (gModel G oi oc).climb = climbG G := model_climb G (gX G oi oc)
  linarith

theorem W_nonneg_iff {O : Type} [Fintype O] (oi oc : O → Chart) (hF : (gModel G oi oc).Flow) :
    0 ≤ (gModel G oi oc).W ↔ climbG G + descMass G ≤ ascMass G := by
  rw [W_of_flow G oi oc hF]; constructor <;> intro h <;> linarith

end xmodel

/-- canonical owned registers. -/
noncomputable def oiC (G : BankedGraph ℚ Fld Bank) : Bank ⊕ Fld → Chart := Sum.elim G.N.src G.N.B
noncomputable def ocC (G : BankedGraph ℚ Fld Bank) : Bank ⊕ Fld → Chart := Sum.elim G.N.dst G.N.A

theorem cnt_eq {γ : Type} [Fintype γ] (f : γ → Chart) (c : Chart) :
    XBal.Model.cnt f c = ∑ a, if f a = c then (1 : ℤ) else 0 := by
  unfold XBal.Model.cnt
  rw [Finset.card_filter]
  push_cast
  exact Finset.sum_congr rfl fun a _ => by split_ifs <;> simp

theorem cnt_elim {α β : Type} [Fintype α] [Fintype β] (f : α → Chart) (g : β → Chart) (c : Chart) :
    XBal.Model.cnt (Sum.elim f g) c = XBal.Model.cnt f c + XBal.Model.cnt g c := by
  rw [cnt_eq, cnt_eq, cnt_eq, Fintype.sum_sum_type]
  rfl

/-- **(1)** Flow holds for the canonical owned registers of ANY banked graph. -/
theorem flow_canon (G : BankedGraph ℚ Fld Bank) : (gModel G (oiC G) (ocC G)).Flow := by
  intro c
  show XBal.Model.cnt G.N.dst c + XBal.Model.cnt G.N.A c + XBal.Model.cnt (Sum.elim G.N.src G.N.B) c =
    XBal.Model.cnt G.N.src c + XBal.Model.cnt G.N.B c + XBal.Model.cnt (Sum.elim G.N.dst G.N.A) c
  rw [cnt_elim, cnt_elim]; ring

theorem W_canon (G : BankedGraph ℚ Fld Bank) :
    (gModel G (oiC G) (ocC G)).W = ascMass G - descMass G - climbG G := W_of_flow G _ _ (flow_canon G)

/-! ## **(3)** the unified banner without Flow -/

theorem bank_kappa_lt_unified_noflow (K : ℕ) (hK : 0 < K) (c : Caller ℚ Fld Bank K)
    (hTP : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → cdat s c.T - cdat s c.P ≤ K * (cdat s T1 - cdat s P1))
    (hc : ∀ i, HSContract (c.G i).N)
    {R Tr Tu Tz : Fin K → Type} [∀ i, Fintype (R i)] [∀ i, Fintype (Tr i)] [∀ i, Fintype (Tu i)]
    [∀ i, Fintype (Tz i)] [∀ i, DecidableEq (Tr i)] [∀ i, DecidableEq (Tu i)]
    (Λ : ∀ i, ULayout (c.G i) (R i) (Tr i) (Tu i) (Tz i)) (h8 : ∀ i, (Λ i).pieces ≤ 8)
    (cs : Fin K → Fin 104 → ℚ) (hC : ∀ i, ComputesS (c.G i) (Λ i).xin (Λ i).yout (cs i))
    (hin : ∀ i p, DF.lq p ∈ (c.G i).N.A ((Λ i).xin p))
    (hout : ∀ i s, ∀ y ∈ (c.G i).N.B ((Λ i).yout s), dot (DF.lq s) y = 0)
    {C D : Fin K → Type} [∀ i, Fintype (C i)] [∀ i, DecidableEq (C i)] [∀ i, Fintype (D i)]
    [∀ i, DecidableEq (D i)] (cr : ∀ i, R i → C i) (ct : ∀ i, Tr i → C i) (dr : ∀ i, R i → D i)
    (du : ∀ i, Tu i → D i) (hWc : ∀ i c', (Λ i).DischW (cr i) (ct i) c')
    (hUc : ∀ i d', (Λ i).DischU (dr i) (du i) d')
    (hAD : ∀ i, climbG (c.G i) + descMass (c.G i) ≤ ascMass (c.G i))
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid c (1 - κ) (fun i k => specInvoice (c.G i) (1 - κ) k)) :
    κ < 952721 / 100000000 :=
  bank_kappa_lt_unified K hK c hTP hc Λ h8 cs hC hin hout cr ct dr du hWc hUc (O := Bank ⊕ Fld)
    (fun i => oiC (c.G i)) (fun i => ocC (c.G i)) (fun i => flow_canon (c.G i))
    (fun i => (W_nonneg_iff (c.G i) _ _ (flow_canon (c.G i))).2 (hAD i)) κ hκ0 hκ1 hV

theorem bank_kappa_lt_unified_disjoint_noflow (K : ℕ) (hK : 0 < K) (c : Caller ℚ Fld Bank K)
    (hTP : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → cdat s c.T - cdat s c.P ≤ K * (cdat s T1 - cdat s P1))
    (hc : ∀ i, HSContract (c.G i).N)
    {R Tr Tu Tz : Fin K → Type} [∀ i, Fintype (R i)] [∀ i, Fintype (Tr i)] [∀ i, Fintype (Tu i)]
    [∀ i, Fintype (Tz i)] [∀ i, DecidableEq (Tr i)] [∀ i, DecidableEq (Tu i)]
    (Λ : ∀ i, ULayout (c.G i) (R i) (Tr i) (Tu i) (Tz i)) (h8 : ∀ i, (Λ i).pieces ≤ 8)
    (cs : Fin K → Fin 104 → ℚ) (hC : ∀ i, ComputesS (c.G i) (Λ i).xin (Λ i).yout (cs i))
    (hin : ∀ i p, DF.lq p ∈ (c.G i).N.A ((Λ i).xin p))
    (hout : ∀ i s, ∀ y ∈ (c.G i).N.B ((Λ i).yout s), dot (DF.lq s) y = 0)
    (hdW : ∀ i r r', r ≠ r' → Disjoint ((Λ i).ancL r).toFinset ((Λ i).ancL r').toFinset)
    (hdU : ∀ i r r', r ≠ r' → Disjoint ((Λ i).tailL r).toFinset ((Λ i).tailL r').toFinset)
    (hAD : ∀ i, climbG (c.G i) + descMass (c.G i) ≤ ascMass (c.G i))
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid c (1 - κ) (fun i k => specInvoice (c.G i) (1 - κ) k)) :
    κ < 952721 / 100000000 :=
  bank_kappa_lt_unified_disjoint K hK c hTP hc Λ h8 cs hC hin hout hdW hdU (O := Bank ⊕ Fld)
    (fun i => oiC (c.G i)) (fun i => ocC (c.G i)) (fun i => flow_canon (c.G i))
    (fun i => (W_nonneg_iff (c.G i) _ _ (flow_canon (c.G i))).2 (hAD i)) κ hκ0 hκ1 hV

end NoFlow

/-! ## **(4)** #7761 -/
namespace Bridge7761
open BankBanner BankUnify NoFlow ThmG BankBig BankTie BankPrem BankCallerGen

theorem asc7761 : ascMass (G7761 hO7761) = 9721 := by
  rw [← model_A (G7761 hO7761) (Z7761 hO7761)]; exact A7761
theorem climb7761G : climbG (G7761 hO7761) = 9665 := by
  rw [← model_climb (G7761 hO7761) (Z7761 hO7761)]; exact climb7761
theorem ad7761 : climbG (G7761 hO7761) + descMass (G7761 hO7761) ≤ ascMass (G7761 hO7761) := by
  rw [asc7761, climb7761G, descMass7761]; norm_num

theorem kappa7761_lt_unified_noflow (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid (caller7761 hO7761) (1 - κ) (fun i k => specInvoice ((caller7761 hO7761).G i) (1 - κ) k)) :
    κ < 952721 / 100000000 :=
  bank_kappa_lt_unified_disjoint_noflow 2048 (by norm_num) (caller7761 hO7761) (by exact hTP7761)
    (fun _ => HS7761 hO7761) (R := fun _ => Fin 8) (Tr := fun _ => Empty) (Tu := fun _ => Empty)
    (Tz := fun _ => Empty) (fun _ => ofGLayout (ofChainTieG τ7761 hcov7761G) len7761_pos)
    (fun _ => (ofGLayout_pieces _ _).trans_le (by simp)) (fun _ => cc) hC7761
    (fun _ p => hin7761 p) (fun _ s y hy => hout7761 s y hy)
    (fun _ r r' _ => by simp [ofGLayout, ofChainTieG]) (fun _ r r' _ => by simp [ofGLayout, ofChainTieG])
    (fun _ => ad7761) κ hκ0 hκ1 hV

end Bridge7761

#print axioms NoFlow.flow_canon
#print axioms NoFlow.W_of_flow
#print axioms NoFlow.W_canon
#print axioms NoFlow.bank_kappa_lt_unified_noflow
#print axioms NoFlow.bank_kappa_lt_unified_disjoint_noflow
#print axioms Bridge7761.ad7761
#print axioms Bridge7761.kappa7761_lt_unified_noflow
