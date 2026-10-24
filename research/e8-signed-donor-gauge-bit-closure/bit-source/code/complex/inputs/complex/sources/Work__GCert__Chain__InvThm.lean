import Work.GCert.Chain.Inv

/-!
# (key: gx-chain) THE CARRIER INVOCATION THEOREM on the generalised engine: `Lab.inv`

`CR.Phased.inv` (`Work/Carrier/PhasedInv.lean`) with subspace labels and `GRoute`.  Forward word:

    erase | y -= K s (old frame 0) | free adapters to the labels of the certificate | phase A |
    c += Cc s | copies down | y += Jr c | phase B | final climbs | free adapters to the old
    frames | slots := slot rows of the inverse (old frame 1) | erase

The backward word is the transposed inverse, gate by gate, on the same labels.  The scalar
identities are `Scal.fwd_scalar` / `Scal.bwd_scalar` (those of `CR.Phased`).

No `sorry`.
-/

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace OAI
namespace PowerSaving
namespace GX
open Binary Matrix Finset RAM SS CB BR CR GF RF
noncomputable section

section Thm
variable {H T Sl C : Type} [Fintype H] [DecidableEq H] [Fintype T] [DecidableEq T]
  [Fintype Sl] [DecidableEq Sl] [Fintype C] [DecidableEq C]
variable {α : Type} [Fintype α] [DecidableEq α]
variable {S : Scal T Sl C} (L : Lab H S) (W : GWin H α)

/-- **Forward word on clean frames.** -/
theorem Lab.fwd_erased (c0 c1 : C → CMat α) :
    GRoute (iin W.Xm L.tv (fun _ : Sl => W.Xm.Φ 0) c0)
      (iout W.Xm L.tv (fun _ : Sl => W.Xm.Φ 1) c1) shearF L.cost := by
  have a1 : GRoute (fun r : L3 T Sl => W.Xm.Φ (lab3 L.tv r).P)
      (fun r : L3 T Sl => W.Xm.Φ (lab3 L.tv r).P)
      (actPoint (g1 S.Mt)) (fun _ => 0) :=
    GRoute.gate (g1 S.Mt) _ _ (fun i j hij => by
      by_cases e : i = j
      · subst e; rfl
      · obtain ⟨h1, h2⟩ := offdiag_x (g1_x S.Mt).1 (g1_x S.Mt).2 hij e
        exact start_frames W.Xm L.tv i j h1 h2)
  have b3 : GRoute (fun r : L3 T Sl => W.Xm.Φ (labE L.tv r))
      (fun r : L3 T Sl => W.Xm.Φ (labE L.tv r))
      (actPoint (g8 S.Mti)) (fun _ => 0) :=
    GRoute.gate (g8 S.Mti) _ _ (fun i j hij => by
      by_cases e : i = j
      · subst e; rfl
      · have f := g8_facts S.hiy
        obtain ⟨h1, h2, h3⟩ := offdiag_s f.1 f.2.1 f.2.2 hij e
        exact end_old W.Xm L.tv i j h1 h2 h3)
  have seg1 : GRoute (fun r : L3 T Sl => W.Xm.Φ (lab3 L.tv r).P) (fun r => W.X.Φ (L.labA r))
      S.f1 (fun φ => rcost φ L.rA) :=
    ((a1.trans (L.ad0 W)).trans (L.pA W.X W.big).1).cast (fun φ => by simp)
  have seg2 : GRoute (fun r => W.X.Φ (L.labA r)) (fun r : L3 T Sl => W.Xm.Φ (labE L.tv r))
      S.f2 (fun φ => rcost φ L.rB + rcost φ L.rF) :=
    ((((L.pB W.X W.big).1.trans (L.pF W.X W.big)).trans (L.adF W)).trans b3).cast
      (fun φ => by simp)
  have e0 : GRoute (iin W.Xm L.tv (fun _ : Sl => W.Xm.Φ 0) c0)
      (glue (fun r : L3 T Sl => W.Xm.Φ (lab3 L.tv r).P) (fun k => W.X.Φ (L.cen k)))
      eraseC (fun _ => 0) :=
    GRoute.ofX (xerase (fun t => rfl) (fun t => rfl) (fun q => rfl))
  have L1 := glift_live (fun k => W.X.Φ (L.cen k)) seg1
  have m1 : GRoute (glue (fun r => W.X.Φ (L.labA r)) (fun k => W.X.Φ (L.cen k)))
      (glue (fun r => W.X.Φ (L.labA r)) (fun k => W.X.Φ (L.cen k)))
      (fun z => addBlk bC (ap S.Cc (z ∘ bS)) z) (fun _ => 0) :=
    GRoute.ofX (xgate_shear bC bS bS_inj S.Cc (fun k q h => congrArg W.X.Φ (L.hAc k q h)))
  have m2 := L.cdown W (fun r => W.X.Φ (L.labA r))
  have m3 : GRoute (glue (fun r => W.X.Φ (L.labA r)) (fun _ : C => W.X.Φ L.z0))
      (glue (fun r => W.X.Φ (L.labA r)) (fun _ : C => W.X.Φ L.z0))
      (fun z => addBlk bY (ap S.Jr (z ∘ bC)) z) (fun _ => 0) :=
    GRoute.ofX (xgate_shear bY bC bC_inj S.Jr (fun t k _ => congrArg W.X.Φ (L.hAy t)))
  have L2 := glift_live (fun _ : C => W.X.Φ L.z0) seg2
  have e1 : GRoute (glue (fun r : L3 T Sl => W.Xm.Φ (labE L.tv r)) (fun _ : C => W.X.Φ L.z0))
      (iout W.Xm L.tv (fun _ : Sl => W.Xm.Φ 1) c1) eraseC (fun _ => 0) :=
    GRoute.ofX (xerase (fun t => rfl) (fun t => rfl) (fun q => rfl))
  have tot := (((((e0.trans L1).trans m1).trans m2).trans m3).trans L2).trans e1
  refine (tot.castg (g' := shearF) (funext fun z => S.fwd_scalar z)).cast (fun φ => ?_)
  simp only [Lab.cost, zero_add, add_zero]
  ring

/-- **Backward word on clean frames**: the transposed inverse gates, same labels; the copies
start at the zero frame and climb. -/
theorem Lab.bwd_erased (c0 c1 : C → CMat α) :
    GRoute (iin W.Xm L.tv (fun _ : Sl => W.Xm.Φ 0) c0)
      (iout W.Xm L.tv (fun _ : Sl => W.Xm.Φ 1) c1) shearB L.cost := by
  have a1 : GRoute (fun r : L3 T Sl => W.Xm.Φ (lab3 L.tv r).P)
      (fun r : L3 T Sl => W.Xm.Φ (lab3 L.tv r).P)
      (actPoint (g1i S.Mt)ᵀ) (fun _ => 0) :=
    GRoute.gate (g1i S.Mt)ᵀ _ _ (fun i j hij => by
      by_cases e : i = j
      · subst e; rfl
      · have hij' : g1i S.Mt j i ≠ 0 := hij
        obtain ⟨h1, h2⟩ := offdiag_x (g1i_x S.Mt).1 (g1i_x S.Mt).2 hij' (Ne.symm e)
        exact start_frames W.Xm L.tv i j h2 h1)
  have b3 : GRoute (fun r : L3 T Sl => W.Xm.Φ (labE L.tv r))
      (fun r : L3 T Sl => W.Xm.Φ (labE L.tv r))
      (actPoint (h8 S.Mt)ᵀ) (fun _ => 0) :=
    GRoute.gate (h8 S.Mt)ᵀ _ _ (fun i j hij => by
      by_cases e : i = j
      · subst e; rfl
      · have hij' : h8 S.Mt j i ≠ 0 := hij
        have f := h8_facts S.hmy
        obtain ⟨h1, h2, h3⟩ := offdiag_s f.1 f.2.1 f.2.2 hij' (Ne.symm e)
        exact (end_old W.Xm L.tv j i h1 h2 h3).symm)
  have seg1 : GRoute (fun r : L3 T Sl => W.Xm.Φ (lab3 L.tv r).P) (fun r => W.X.Φ (L.labA r))
      S.b1 (fun φ => rcost φ L.rA) :=
    ((a1.trans (L.ad0 W)).trans (L.pA W.X W.big).2).cast (fun φ => by simp)
  have seg2 : GRoute (fun r => W.X.Φ (L.labA r)) (fun r : L3 T Sl => W.Xm.Φ (labE L.tv r))
      S.b2 (fun φ => rcost φ L.rB + rcost φ L.rF) :=
    ((((L.pB W.X W.big).2.trans (L.pF W.X W.big)).trans (L.adF W)).trans b3).cast
      (fun φ => by simp)
  have e0 : GRoute (iin W.Xm L.tv (fun _ : Sl => W.Xm.Φ 0) c0)
      (glue (fun r : L3 T Sl => W.Xm.Φ (lab3 L.tv r).P) (fun _ : C => W.X.Φ L.z0))
      eraseC (fun _ => 0) :=
    GRoute.ofX (xerase (fun t => rfl) (fun t => rfl) (fun q => rfl))
  have L1 := glift_live (fun _ : C => W.X.Φ L.z0) seg1
  have m1 : GRoute (glue (fun r => W.X.Φ (L.labA r)) (fun _ : C => W.X.Φ L.z0))
      (glue (fun r => W.X.Φ (L.labA r)) (fun _ : C => W.X.Φ L.z0))
      (fun z => addBlk bC (ap S.Jrᵀ (z ∘ bY)) z) (fun _ => 0) :=
    GRoute.ofX (xgate_shear bC bY bY_inj S.Jrᵀ (fun k t _ => (congrArg W.X.Φ (L.hAy t)).symm))
  have m2 := L.cup W (fun r => W.X.Φ (L.labA r))
  have m3 : GRoute (glue (fun r => W.X.Φ (L.labA r)) (fun k => W.X.Φ (L.cen k)))
      (glue (fun r => W.X.Φ (L.labA r)) (fun k => W.X.Φ (L.cen k)))
      (fun z => addBlk bS (ap (-S.Ccᵀ) (z ∘ bC)) z) (fun _ => 0) :=
    GRoute.ofX (xgate_shear bS bC bC_inj (-S.Ccᵀ)
      (fun q k h => (congrArg W.X.Φ (L.hAc k q (ne_of_negT S.Cc h))).symm))
  have L2 := glift_live (fun k => W.X.Φ (L.cen k)) seg2
  have e1 : GRoute (glue (fun r : L3 T Sl => W.Xm.Φ (labE L.tv r)) (fun k => W.X.Φ (L.cen k)))
      (iout W.Xm L.tv (fun _ : Sl => W.Xm.Φ 1) c1) eraseC (fun _ => 0) :=
    GRoute.ofX (xerase (fun t => rfl) (fun t => rfl) (fun q => rfl))
  have tot := (((((e0.trans L1).trans m1).trans m2).trans m3).trans L2).trans e1
  refine (tot.castg (g' := shearB) (funext fun z => S.bwd_scalar z)).cast (fun φ => ?_)
  simp only [Lab.cost, zero_add, add_zero]
  ring

/-- **THE CARRIER INVOCATION THEOREM on the generalised engine.**  The two halves of a
certificate are an invocation package for the bridged network, with the price `L.cost`. -/
def Lab.inv : GInv H T Sl C where
  tv := L.tv
  hunit := L.hunit
  hgap := L.hgap
  cost := L.cost
  fwd := fun W N0 Wn hN hW Z c0 c1 =>
    gdirty_of_erased W.Xm L.tv N0 Wn hN hW Z c0 c1 (L.fwd_erased W c0 c1)
      (shearF_comm (fun _ => 1) (fun q => N0 * Z q) (fun _ => 1))
  bwd := fun W N0 Wn hN hW Z c0 c1 =>
    gdirty_of_erased W.Xm L.tv N0 Wn hN hW Z c0 c1 (L.bwd_erased W c0 c1)
      (shearB_comm (fun _ => 1) (fun q => N0 * Z q) (fun _ => 1))

@[simp] lemma Lab.inv_cost (φ : ℕ → ℝ) : L.inv.cost φ = L.cost φ := rfl
@[simp] lemma Lab.inv_tv : L.inv.tv = L.tv := rfl

end Thm
end
end GX
end PowerSaving
end OAI

#print axioms OAI.PowerSaving.GX.Lab.fwd_erased
#print axioms OAI.PowerSaving.GX.Lab.bwd_erased
#print axioms OAI.PowerSaving.GX.Lab.inv
