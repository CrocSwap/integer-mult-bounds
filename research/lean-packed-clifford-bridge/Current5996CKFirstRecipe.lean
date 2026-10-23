import Current9594CKFirstRecipe

/-!
Exact current5996 CK-HPE ordinal0 source binding. The complete serialized
monomial fields and ordered descriptors match the accepted459 interpretation.
Apache-2.0; prepared with OpenAI assistance. See NOTICE.md.
The current Fin1082 event-label embedding and physical execution are separate.
-/
set_option Elab.async false
namespace CurrentMain.Current5996CKFirstRecipe
open CliffordNineBitDecoder
open RankOneRecipeCertificate

theorem key_and_descriptors :
    Current9594CKFirstRecipe.oldFrame = 0 ∧
    Current9594CKFirstRecipe.newFrame = 2 ∧
    Current9594CKFirstRecipe.rank = 1 ∧
    Current9594CKFirstRecipe.oldDescriptor = [] ∧
    Current9594CKFirstRecipe.newDescriptor = [459] := by
  exact ⟨rfl, rfl, rfl, rfl, rfl⟩

theorem left_fields :
    Current9594CKFirstRecipe.leftRows = [3, 5, 8, 17, 32, 64, 129, 257, 1] ∧
    Current9594CKFirstRecipe.leftQ = [1, 0, 0, 0, 0, 0, 0, 0, 0] ∧
    Current9594CKFirstRecipe.leftAlpha = [3, 0, 0, 0, 0, 0, 0, 0, 0] ∧
    Current9594CKFirstRecipe.leftOffset = 0 ∧
    Current9594CKFirstRecipe.leftPhase = 0 := by
  exact ⟨rfl, rfl, rfl, rfl, rfl⟩

theorem right_fields : Current9594CKFirstRecipe.rightPresent = true ∧
    Current9594CKFirstRecipe.rightRows = [203, 257, 258, 4, 264, 16, 32, 320, 384] ∧
    Current9594CKFirstRecipe.rightQ = [459, 459, 0, 459, 0, 0, 459, 459, 203] ∧
    Current9594CKFirstRecipe.rightAlpha = [1, 1, 0, 1, 0, 0, 1, 1, 2] ∧
    Current9594CKFirstRecipe.rightOffset = 0 ∧
    Current9594CKFirstRecipe.rightPhase = 0 := by
  exact ⟨rfl, rfl, rfl, rfl, rfl, rfl⟩

abbrev left := Current9594CKFirstRecipe.left
abbrev right := Current9594CKFirstRecipe.right
abbrev canonicalLinear := Current9594CKFirstRecipe.canonicalLinear
abbrev canonicalPhase := Current9594CKFirstRecipe.canonicalPhase

noncomputable section
/-- The matched directed source record retains its exact all-payload action. -/
theorem selected_child_operator (v : Address → ℂ) :
    left.operator (gaussian (right.operator v)) =
      canonicalK canonicalLinear.toEquiv canonicalPhase
        (gaussian ((canonicalK canonicalLinear.toEquiv canonicalPhase).symm v)) :=
  Current9594CKFirstRecipe.selected_child_operator v
end
end CurrentMain.Current5996CKFirstRecipe

#print axioms CurrentMain.Current5996CKFirstRecipe.key_and_descriptors
#print axioms CurrentMain.Current5996CKFirstRecipe.left_fields
#print axioms CurrentMain.Current5996CKFirstRecipe.right_fields
#print axioms CurrentMain.Current5996CKFirstRecipe.selected_child_operator
