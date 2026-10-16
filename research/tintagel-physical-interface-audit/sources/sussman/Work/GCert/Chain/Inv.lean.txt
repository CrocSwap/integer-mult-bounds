import Work.GCert.Chain.Win
import Work.Carrier.PhasedInv

/-!
# (key: gx-chain) The generalised invocation package `GInv`, and the pieces of the carrier word

`GInv H T Sl C` = `BR.Inv` on the generalised engine: for every window `W : GWin H α` the
invocation is a `GRoute` between the OLD bank frames (`BR.iin`, `BR.iout` of `W.Xm`), with
scalar map `shearF` / `shearB`, on helper slots that carry arbitrary matrices.

Pieces for `Lab.inv` (`Work/GCert/Chain/InvThm.lean`): `glift_live` (a route on the live roles),
`Lab.ad0` / `Lab.adF` (the free adapters at the two ends), `Lab.cdown` / `Lab.cup` (the copies).

No `sorry`.
-/

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace OAI
namespace PowerSaving
namespace GX
open Binary Matrix Finset RAM SS CB BR CR GF RF
noncomputable section

/-- **A generalised invocation, as a package.** -/
structure GInv (H T Sl C : Type) [Fintype H] [DecidableEq H] [Fintype T] [DecidableEq T]
    [Fintype Sl] [DecidableEq Sl] [Fintype C] [DecidableEq C] where
  tv : T → Space H
  hunit : ∀ t, dot (tv t) (tv t) = 1
  hgap : ∀ t, ∃ p, tv t p = 0
  cost : (ℕ → ℝ) → ℝ
  fwd : ∀ {α : Type} [Fintype α] [DecidableEq α] (W : GWin H α) (N0 Wn : CMat α),
    W.Xm.Φ 0 * N0 = 1 → W.Xm.Φ 1 = Wn * W.Xm.Φ 0 → ∀ (Z : Sl → CMat α) (c0 c1 : C → CMat α),
    GRoute (iin W.Xm tv Z c0) (iout W.Xm tv (fun q => Wn * Z q) c1) shearF cost
  bwd : ∀ {α : Type} [Fintype α] [DecidableEq α] (W : GWin H α) (N0 Wn : CMat α),
    W.Xm.Φ 0 * N0 = 1 → W.Xm.Φ 1 = Wn * W.Xm.Φ 0 → ∀ (Z : Sl → CMat α) (c0 c1 : C → CMat α),
    GRoute (iin W.Xm tv Z c0) (iout W.Xm tv (fun q => Wn * Z q) c1) shearB cost

section Pieces
variable {H T Sl C : Type} [Fintype H] [DecidableEq H] [Fintype T] [DecidableEq T]
  [Fintype Sl] [DecidableEq Sl] [Fintype C] [DecidableEq C]
variable {α : Type} [Fintype α] [DecidableEq α]

/-- old projectors of the live roles at the END of an invocation. -/
def labE (tv : T → Space H) : L3 T Sl → Matrix H H F :=
  Sum.elim (Sum.elim (fun _ => 1) (fun t => 1 + tt (tv t))) (fun _ => 1)

lemma end_old (Xm : XMap H α) (tv : T → Space H) (i j : L3 T Sl) (hi : iX i = 0)
    (hi' : iY i = 0) (hj : iY j = 0) : Xm.Φ (labE tv i) = Xm.Φ (labE tv j) := by
  rcases i with ((t|t)|q)
  · exact absurd (show (1:ℚ) = 0 from hi) one_ne_zero
  · exact absurd (show (1:ℚ) = 0 from hi') one_ne_zero
  · rcases j with ((t'|t')|q')
    · rfl
    · exact absurd (show (1:ℚ) = 0 from hj) one_ne_zero
    · rfl

/-- **A generalised route on the live roles is a route on all roles** (as `CR.lift_live`). -/
theorem glift_live {S S' : L3 T Sl → CMat α} (c : C → CMat α)
    {h : (L3 T Sl → ℂ) → (L3 T Sl → ℂ)} {cost : (ℕ → ℝ) → ℝ} (q : GRoute S S' h cost) :
    GRoute (glue S c) (glue S' c) (liveAct h) cost := by
  refine GRoute.lift upE (S := glue S c) (T := glue S' c) (h := h) ?_ ?_ ?_ ?_
  · rw [glue_up, glue_up]
    exact q
  · intro x
    exact glue_up _ _
  · intro x i hi
    rcases i with (b|(q'|k))
    · exact absurd ((cover_iff ..).mpr ⟨Sum.inl b, rfl⟩) hi
    · exact absurd ((cover_iff ..).mpr ⟨Sum.inr q', rfl⟩) hi
    · rfl
  · intro i hi
    rcases i with (b|(q'|k))
    · exact absurd ((cover_iff ..).mpr ⟨Sum.inl b, rfl⟩) hi
    · exact absurd ((cover_iff ..).mpr ⟨Sum.inr q', rfl⟩) hi
    · rfl

variable {S : Scal T Sl C} (L : Lab H S) (W : GWin H α)

/-- the free adapters at the start: old frames (line, 0, 0) to the labels of the certificate. -/
theorem Lab.ad0 :
    GRoute (fun r : L3 T Sl => W.Xm.Φ (lab3 L.tv r).P) (fun r => W.X.Φ (L.lab0 r)) id
      (fun _ => 0) := by
  refine (GRoute.reach_all _ _ (fun _ _ => 0) ?_).cast (fun φ => by simp)
  rintro ((t|t)|q)
  · obtain ⟨p, hp⟩ := L.hgap t
    obtain ⟨A, k, hA⟩ := exists_base_one (L.tv t) (L.hunit t) p hp
    have h := W.line A k (L.lab0 (lX t)) (L.h0x t).1 (by rw [hA]; exact (L.h0x t).2)
    rw [hA] at h
    exact h
  · exact W.zero _ (L.h0y t)
  · exact W.zero _ (L.h0s q)

/-- the free adapters at the end: the labels of the certificate to the old frames
(1, port-perp, 1). -/
theorem Lab.adF :
    GRoute (fun r => W.X.Φ (L.labF r)) (fun r : L3 T Sl => W.Xm.Φ (labE L.tv r)) id
      (fun _ => 0) := by
  refine (GRoute.reach_all _ _ (fun _ _ => 0) ?_).cast (fun φ => by simp)
  rintro ((t|t)|q)
  · exact W.full _ (L.hFx t)
  · obtain ⟨p, hp⟩ := L.hgap t
    obtain ⟨A, k, hA⟩ := exists_base_one (L.tv t) (L.hunit t) p hp
    have h := W.perp A k (L.labF (lY t)) (L.hFy t).1 (by rw [hA]; exact (L.hFy t).2)
    rw [hA] at h
    exact h
  · exact W.full _ (L.hFs q)

lemma Lab.cfacts (hb : Fintype.card H < Fintype.card α) (k : C) :
    (∀ x, L.z0.Mem x → (L.cen k).Mem x) ∧ L.z0.dim < (L.cen k).dim ∧
    (L.cen k).dim - L.z0.dim < Fintype.card α := by
  refine ⟨fun x hx => ?_, by rw [L.hz0]; exact L.hcen k, ?_⟩
  · rw [mem_dim_zero L.z0 L.hz0 hx]
    exact insub_zero _ _
  · have h1 : (L.cen k).dim ≤ Fintype.card H := Finset.card_le_univ _
    omega

lemma Lab.cdn (k : C) :
    GReach (W.X.Φ (L.cen k)) (W.X.Φ L.z0) (fun φ => bcost φ (L.cen k).dim) := by
  obtain ⟨h0, h1, h2⟩ := L.cfacts W.big k
  have h := (W.X.fmv_sup L.z0 (L.cen k) h0 h1 h2).reach
  have h' : GReach (W.X.Φ (L.cen k)) (W.X.Φ L.z0)
      (fun φ => rcost φ [(L.cen k).dim - L.z0.dim]) := GReach.ofReach h
  exact h'.cast (fun φ => by rw [rcost_single, L.hz0, Nat.sub_zero])

lemma Lab.cupk (k : C) :
    GReach (W.X.Φ L.z0) (W.X.Φ (L.cen k)) (fun φ => bcost φ (L.cen k).dim) := by
  obtain ⟨h0, h1, h2⟩ := L.cfacts W.big k
  have h := (W.X.fmv_sub L.z0 (L.cen k) h0 h1 h2).reach
  have h' : GReach (W.X.Φ L.z0) (W.X.Φ (L.cen k))
      (fun φ => rcost φ [(L.cen k).dim - L.z0.dim]) := GReach.ofReach h
  exact h'.cast (fun φ => by rw [rcost_single, L.hz0, Nat.sub_zero])

/-- every copy moves by its own word; the live roles stay. -/
theorem greach_copies (Sf : L3 T Sl → CMat α) (a b : C → CMat α) (c : C → (ℕ → ℝ) → ℝ)
    (h : ∀ k, GReach (a k) (b k) (c k)) :
    GRoute (glue Sf a) (glue Sf b) id (fun φ => ∑ k, c k φ) := by
  have H0 := GRoute.reach_all (glue Sf a) (glue Sf b)
    (fun r φ => Sum.elim (fun _ => (0:ℝ)) (Sum.elim (fun _ => (0:ℝ)) (fun k => c k φ)) r) (by
      rintro (r|(q|k))
      · exact GReach.refl _
      · exact GReach.refl _
      · exact h k)
  refine H0.cast (fun φ => ?_)
  first
    | (simp only [Fintype.sum_sum_type, Sum.elim_inl, Sum.elim_inr, Finset.sum_const_zero,
        zero_add, add_zero]; done)
    | simp [Fintype.sum_sum_type]

/-- every copy comes down from its label to the zero frame: ONE block of rank `dim`. -/
theorem Lab.cdown (Sf : L3 T Sl → CMat α) :
    GRoute (glue Sf (fun k => W.X.Φ (L.cen k))) (glue Sf (fun _ : C => W.X.Φ L.z0)) id
      (fun φ => ∑ k, bcost φ (L.cen k).dim) :=
  greach_copies Sf _ _ _ (fun k => L.cdn W k)

/-- every copy climbs from the zero frame to its label: ONE block of rank `dim`. -/
theorem Lab.cup (Sf : L3 T Sl → CMat α) :
    GRoute (glue Sf (fun _ : C => W.X.Φ L.z0)) (glue Sf (fun k => W.X.Φ (L.cen k))) id
      (fun φ => ∑ k, bcost φ (L.cen k).dim) :=
  greach_copies Sf _ _ _ (fun k => L.cupk W k)

end Pieces
end
end GX
end PowerSaving
end OAI

#print axioms OAI.PowerSaving.GX.glift_live
#print axioms OAI.PowerSaving.GX.Lab.ad0
#print axioms OAI.PowerSaving.GX.Lab.adF
#print axioms OAI.PowerSaving.GX.Lab.cdown
#print axioms OAI.PowerSaving.GX.Lab.cup
