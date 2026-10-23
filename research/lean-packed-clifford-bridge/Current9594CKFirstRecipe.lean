import Current535Child002Canonical

/-!
The selected9594 CK catalog's first directed child, with its complete literal
fields and ordered descriptors, reuses the accepted459 operator on Address.
Apache-2.0; prepared with OpenAI assistance. See NOTICE.md.
This is a source-record binding, not a decoded event or physical-executor claim.
-/
set_option Elab.async false
namespace CurrentMain.Current9594CKFirstRecipe

open CliffordNineBitDecoder
open RankOneRecipeCertificate

def oldFrame : Nat := 0
def newFrame : Nat := 2
def rank : Nat := 1
def oldDescriptor : List Nat := []
def newDescriptor : List Nat := [459]
def leftRows : List Nat := [3, 5, 8, 17, 32, 64, 129, 257, 1]
def leftQ : List Nat := [1, 0, 0, 0, 0, 0, 0, 0, 0]
def leftAlpha : List Nat := [3, 0, 0, 0, 0, 0, 0, 0, 0]
def leftOffset : Nat := 0
def leftPhase : Nat := 0
def rightRows : List Nat := [203, 257, 258, 4, 264, 16, 32, 320, 384]
def rightQ : List Nat := [459, 459, 0, 459, 0, 0, 459, 459, 203]
def rightAlpha : List Nat := [1, 1, 0, 1, 0, 0, 1, 1, 2]
def rightOffset : Nat := 0
def rightPhase : Nat := 0
def rightPresent : Bool := true

theorem key_and_descriptors :
    oldFrame = Current535Child002Canonical.oldFrame ∧
    newFrame = Current535Child002Canonical.newFrame ∧
    rank = Current535Child002Canonical.rank ∧
    oldDescriptor = Current535Child002Canonical.oldDescriptor ∧
    newDescriptor = Current535Child002Canonical.newDescriptor := by
  exact ⟨rfl, rfl, rfl, rfl, rfl⟩

theorem left_fields :
    leftRows = Current535Child002Canonical.leftRows ∧
    leftQ = Current535Child002Canonical.leftQ ∧
    leftAlpha = Current535Child002Canonical.leftAlpha ∧
    leftOffset = Current535Child002Canonical.leftOffset ∧
    leftPhase = Current535Child002Canonical.leftPhase := by
  exact ⟨rfl, rfl, rfl, rfl, rfl⟩

theorem right_fields : rightPresent = true ∧
    rightRows = Current535Child002Canonical.rightRows ∧
    rightQ = Current535Child002Canonical.rightQ ∧
    rightAlpha = Current535Child002Canonical.rightAlpha ∧
    rightOffset = Current535Child002Canonical.rightOffset ∧
    rightPhase = Current535Child002Canonical.rightPhase := by
  exact ⟨rfl, rfl, rfl, rfl, rfl, rfl⟩

/-- These aliases retain the accepted decoder and certified inverse/basis data.
The three equalities above bind every serialized field to that interpretation. -/
abbrev left := Current535Child002Canonical.left
abbrev right := Current535Child002Canonical.right
abbrev canonicalLinear := Current535Child002Canonical.canonicalLinear
abbrev canonicalPhase := Current535Child002Canonical.canonicalPhase

noncomputable section
/-- Exact directed empty-to-singleton identity for arbitrary complex payloads. -/
theorem selected_child_operator (v : Address → ℂ) :
    left.operator (gaussian (right.operator v)) =
      canonicalK canonicalLinear.toEquiv canonicalPhase
        (gaussian ((canonicalK canonicalLinear.toEquiv canonicalPhase).symm v)) :=
  Current535Child002Canonical.selected_child_operator v
end
end CurrentMain.Current9594CKFirstRecipe

#print axioms CurrentMain.Current9594CKFirstRecipe.key_and_descriptors
#print axioms CurrentMain.Current9594CKFirstRecipe.left_fields
#print axioms CurrentMain.Current9594CKFirstRecipe.right_fields
#print axioms CurrentMain.Current9594CKFirstRecipe.selected_child_operator
