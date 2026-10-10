import Work.GCert.Chain.Win
import Work.BridgeGeom.Stage

/-!
# (key: gx-chain) THE WINDOW LIFT (spec statement 3): the windows of the bridged geometry

For the block frame map `BG.fmapB hB hH d q` of a stage of the bridged word (label space
`LB B H = H ⊕ (B × H)`, old frame of the projector `P`: `PhiB d q P`) the stage-B frame map is
`BXMap.ofConj d q` (`U ↦ d (U ⊕ span q)`, arbitrary subspaces `U` of `H`).  At a coordinate
subspace of an orthonormal basis `A` of `H` the two name the SAME subspace of the address space
(`insub_old_new`), so the old frame and the representative of any label of that subspace
differ by a free factor (`frame_core_free`, `rep_change`): `old_to_new`, `new_to_old`.

`gwinB hB hH d q : GWin H (LB B H)` with `(gwinB hB hH d q).Xm = fmapB hB hH d q` (`rfl`).

No `sorry`.
-/

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace OAI
namespace PowerSaving
namespace GX
open Binary Matrix Finset RAM SS CB RF BR BG GF
noncomputable section

section
variable {B H : Type} [Fintype B] [DecidableEq B] [Fintype H] [DecidableEq H]

lemma blkT_mulVec (A : OBase H) (z : Space (LB B H)) (k : LB B H) :
    ((blkB B A)ᵀ *ᵥ z) k = Sum.elim (fun i => dot (A.v i) (fun j => z (Sum.inl j)))
      (fun b => z (Sum.inr b)) k := by
  cases k with
  | inl i =>
    simp [blkB, Matrix.fromBlocks_transpose, Matrix.mulVec, dotProduct, Fintype.sum_sum_type,
      cmat, dot]
  | inr b =>
    simp [blkB, Matrix.fromBlocks_transpose, Matrix.mulVec, dotProduct, Fintype.sum_sum_type,
      Matrix.one_apply]

/-- coordinates of `y` in the basis `d (A ⊕ std)`. -/
lemma dot_cols (d : Orth (LB B H)) (A : OBase H) (y : Space (LB B H)) (k : LB B H) :
    dot ((ofCols (d.1 * blkB B A) (mul_orth d.2 (blkB_orth A))).v k) y
      = Sum.elim (fun i => dot (A.v i) (fun j => (d.1ᵀ *ᵥ y) (Sum.inl j)))
          (fun b => (d.1ᵀ *ᵥ y) (Sum.inr b)) k := by
  rw [← blkT_mulVec A (d.1ᵀ *ᵥ y) k, Matrix.mulVec_mulVec, ← Matrix.transpose_mul]
  rfl

/-- **the old frame and the lifted label name the same subspace of the address space.** -/
theorem insub_old_new (d : Orth (LB B H)) (q : Finset (B × H)) (A : OBase H) (s : Finset H)
    (U : SLbl H) (h : ∀ x, U.Mem x ↔ InSub (coordPerm A) s x) (y : Space (LB B H)) :
    InSub (coordPerm (ofCols (d.1 * blkB B A) (mul_orth d.2 (blkB_orth A)))) (JB s q) y ↔
      InSub (conjPerm d.1 d.2 (Orth.orth' d) U.G) (U.s.disjSum q) y := by
  rw [insub_conj, insub_coordPerm]
  have hU := h (fun i => (d.1ᵀ *ᵥ y) (Sum.inl i))
  constructor
  · intro hk
    refine ⟨hU.mpr ((insub_coordPerm A s _).mpr (fun i hi => ?_)), fun b hb => ?_⟩
    · have h1 := hk (Sum.inl i) (fun hm => hi (Finset.inl_mem_disjSum.mp hm))
      rw [dot_cols] at h1
      exact h1
    · have h1 := hk (Sum.inr b) (fun hm => hb (Finset.inr_mem_disjSum.mp hm))
      rw [dot_cols] at h1
      exact h1
  · rintro ⟨h1, h2⟩ k hk
    rw [dot_cols]
    cases k with
    | inl i =>
      exact (insub_coordPerm A s _).mp (hU.mp h1) i
        (fun hm => hk (Finset.inl_mem_disjSum.mpr hm))
    | inr b => exact h2 b (fun hm => hk (Finset.inr_mem_disjSum.mpr hm))

/-- old frame of a coordinate subspace → representative of any label naming it: FREE. -/
theorem old_to_new (d : Orth (LB B H)) (q : Finset (B × H)) (A : OBase H) (s : Finset H)
    (U : SLbl H) (h : ∀ x, U.Mem x ↔ InSub (coordPerm A) s x) :
    GReach (PhiB d q (A.mat s)) ((BXMap.ofConj d.1 d.2 (Orth.orth' d) q).Φ U) (fun _ => 0) := by
  rw [PhiB_eq]
  obtain ⟨N, hN, e⟩ := repChange (LB B H) _ _ _ _ (insub_old_new d q A s U h)
  have a : GReach (frame (ofCols (d.1 * blkB B A) (mul_orth d.2 (blkB_orth A))) (JB s q))
      (core (coordPerm (ofCols (d.1 * blkB B A) (mul_orth d.2 (blkB_orth A)))) (JB s q))
      (fun φ => rcost φ []) :=
    GReach.ofReach (fmv_old_to_core _ _).reach
  have b : GReach
      (core (coordPerm (ofCols (d.1 * blkB B A) (mul_orth d.2 (blkB_orth A)))) (JB s q))
      (core (conjPerm d.1 d.2 (Orth.orth' d) U.G) (U.s.disjSum q)) (fun φ => rcost φ []) :=
    GReach.ofReach (fmv_of_free hN e).reach
  exact (a.trans b).cast (fun φ => by simp [rcost])

/-- the same, backwards. -/
theorem new_to_old (d : Orth (LB B H)) (q : Finset (B × H)) (A : OBase H) (s : Finset H)
    (U : SLbl H) (h : ∀ x, U.Mem x ↔ InSub (coordPerm A) s x) :
    GReach ((BXMap.ofConj d.1 d.2 (Orth.orth' d) q).Φ U) (PhiB d q (A.mat s)) (fun _ => 0) := by
  rw [PhiB_eq]
  obtain ⟨N, hN, e⟩ := repChange (LB B H) _ _ _ _
    (fun y => (insub_old_new d q A s U h y).symm)
  have a : GReach (core (conjPerm d.1 d.2 (Orth.orth' d) U.G) (U.s.disjSum q))
      (core (coordPerm (ofCols (d.1 * blkB B A) (mul_orth d.2 (blkB_orth A)))) (JB s q))
      (fun φ => rcost φ []) :=
    GReach.ofReach (fmv_of_free hN e).reach
  have b : GReach
      (core (coordPerm (ofCols (d.1 * blkB B A) (mul_orth d.2 (blkB_orth A)))) (JB s q))
      (frame (ofCols (d.1 * blkB B A) (mul_orth d.2 (blkB_orth A))) (JB s q))
      (fun φ => rcost φ []) :=
    GReach.ofReach (fmv_core_to_old _ _).reach
  exact (a.trans b).cast (fun φ => by simp [rcost])

/-- **The window of a stage of the bridged geometry.** -/
def gwinB (hB : 1 ≤ Fintype.card B) (hH : 1 ≤ Fintype.card H) (d : Orth (LB B H))
    (q : Finset (B × H)) : GWin H (LB B H) where
  Xm := fmapB hB hH d q
  X := BXMap.ofConj d.1 d.2 (Orth.orth' d) q
  big := by
    rw [card_LB]
    have := Nat.mul_le_mul_right (Fintype.card H) (show 2 ≤ Fintype.card B + 1 by omega)
    omega
  toNew := fun A s U h => old_to_new d q A s U h
  toOld := fun A s U h => new_to_old d q A s U h

@[simp] lemma gwinB_Xm (hB : 1 ≤ Fintype.card B) (hH : 1 ≤ Fintype.card H) (d : Orth (LB B H))
    (q : Finset (B × H)) : (gwinB hB hH d q).Xm = fmapB hB hH d q := rfl

end
end
end GX
end PowerSaving
end OAI

#print axioms OAI.PowerSaving.GX.insub_old_new
#print axioms OAI.PowerSaving.GX.old_to_new
#print axioms OAI.PowerSaving.GX.new_to_old
#print axioms OAI.PowerSaving.GX.gwinB
