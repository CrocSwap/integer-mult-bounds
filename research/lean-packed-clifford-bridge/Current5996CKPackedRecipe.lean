import Current5996CKFirstRecipe
import PackedMonomialReindex
import PackedGaussianReindex

/-!
The current CK-HPE empty-to-[459] recipe as an explicit packed circuit.
Chronological execution is right monomial, exact Gaussian C0, left monomial.
All field/inverse/canonical certificates are reused; no finite algebra replay.
Apache-2.0; prepared with OpenAI assistance. See NOTICE.md.
-/
set_option Elab.async false
namespace CurrentMain.Current5996CKPackedRecipe
open Current535PackedCoordinates
open CliffordNineBitDecoder
open RankOneRecipeCertificate
open HyperplaneEnd.Clifford (Gate cL gC)

def leftCircuit : List Gate :=
  [.dg Current535Child002Canonical.leftQ Current535Child002Canonical.leftAlpha,
   .pm Current535Child002Canonical.leftRows Current535Child002Canonical.leftInverseRows,
   .xg Current535Child002Canonical.leftOffset, .ph Current535Child002Canonical.leftPhase]

def rightCircuit : List Gate :=
  [.dg Current535Child002Canonical.rightQ Current535Child002Canonical.rightAlpha,
   .pm Current535Child002Canonical.rightRows Current535Child002Canonical.rightInverseRows,
   .xg Current535Child002Canonical.rightOffset, .ph Current535Child002Canonical.rightPhase]

def recipe : List Gate := (rightCircuit ++ [.cg 1 true]) ++ leftCircuit

noncomputable section

theorem left_reindex (v : Packed → ℂ) :
    payloadEquiv (cL 512 leftCircuit v) =
      Current5996CKFirstRecipe.left.operator (payloadEquiv v) := by
  simpa only [leftCircuit, Current5996CKFirstRecipe.left,
    Current9594CKFirstRecipe.left, Current535Child002Canonical.left] using
    PackedMonomialReindex.monomial_reindex
      Current535Child002Canonical.leftRows Current535Child002Canonical.leftInverseRows
      Current535Child002Canonical.leftQ Current535Child002Canonical.leftAlpha
      (by rfl) (by rfl) (by rfl)
      Current535Child002Canonical.leftOffset Current535Child002Canonical.leftPhase
      (by decide) Current535Child002Canonical.left_inverses.1
      Current535Child002Canonical.left_inverses.2 v

theorem right_reindex (v : Packed → ℂ) :
    payloadEquiv (cL 512 rightCircuit v) =
      Current5996CKFirstRecipe.right.operator (payloadEquiv v) := by
  simpa only [rightCircuit, Current5996CKFirstRecipe.right,
    Current9594CKFirstRecipe.right, Current535Child002Canonical.right] using
    PackedMonomialReindex.monomial_reindex
      Current535Child002Canonical.rightRows Current535Child002Canonical.rightInverseRows
      Current535Child002Canonical.rightQ Current535Child002Canonical.rightAlpha
      (by rfl) (by rfl) (by rfl)
      Current535Child002Canonical.rightOffset Current535Child002Canonical.rightPhase
      (by decide) Current535Child002Canonical.right_inverses.1
      Current535Child002Canonical.right_inverses.2 v

/-- The source's direct old→new rank-one order is right, C0, then left. -/
theorem recipe_reindex (v : Packed → ℂ) :
    payloadEquiv (cL 512 recipe v) =
      Current5996CKFirstRecipe.left.operator
        (gaussian (Current5996CKFirstRecipe.right.operator (payloadEquiv v))) := by
  have hs (w : Packed → ℂ) : cL 512 [.cg 1 true] w = gC 512 (.cg 1 true) w := by
    simp only [HyperplaneEnd.Clifford.cL_cons, HyperplaneEnd.Clifford.cL_nil,
      LinearMap.comp_apply, LinearMap.id_apply, HyperplaneEnd.Clifford.gL_apply]
  rw [recipe, HyperplaneEnd.Clifford.cL_append_apply, left_reindex,
    HyperplaneEnd.Clifford.cL_append_apply, hs,
    PackedGaussianReindex.gaussian_reindex, right_reindex]

/-- The fully phase-sensitive packed circuit equals the reindexed canonical
child operator for every payload. Selected event/executor and full-work state
bindings are not premises silently supplied by this identity. -/
theorem packed_canonical_child (v : Packed → ℂ) :
    cL 512 recipe v = payloadEquiv.symm
      (canonicalK Current5996CKFirstRecipe.canonicalLinear.toEquiv
        Current5996CKFirstRecipe.canonicalPhase
        (gaussian ((canonicalK Current5996CKFirstRecipe.canonicalLinear.toEquiv
          Current5996CKFirstRecipe.canonicalPhase).symm (payloadEquiv v)))) := by
  apply payloadEquiv.injective
  rw [LinearEquiv.apply_symm_apply, recipe_reindex]
  exact Current5996CKFirstRecipe.selected_child_operator (payloadEquiv v)

end
end CurrentMain.Current5996CKPackedRecipe

#print axioms CurrentMain.Current5996CKPackedRecipe.left_reindex
#print axioms CurrentMain.Current5996CKPackedRecipe.right_reindex
#print axioms CurrentMain.Current5996CKPackedRecipe.recipe_reindex
#print axioms CurrentMain.Current5996CKPackedRecipe.packed_canonical_child
