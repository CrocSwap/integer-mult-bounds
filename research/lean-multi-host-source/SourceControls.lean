import MatrixCertificate
set_option maxRecDepth 100000
set_option maxHeartbeats 0

/-!
Focused source controls. These retain the distinction between arbitrary
original inputs and the required clean private register. The mutation is an
intentional alteration of one actual instruction, not a claim about the
submitted program.
-/
namespace SourceControls
open LinearReplay (Event)
open TreeReplay SourceMatrix

/-- Event 218 of the actual word, at offset 18 in its second chunk. -/
theorem actual_add_event : chunk1[18]? = some (⟨1,126,243,true⟩ : Event) := by rfl

def omittedAdd : List Event := chunk1.set 18 ⟨1,126,243,false⟩

/-- Omitting this source XOR loses exactly original variable 243 from row126. -/
theorem omitted_add_changes_row :
    (runCheckedRows omittedAdd state1).1.get 126 ^^^ state2.1.get 126 =
      1 <<< 243 := by rfl

/-- The missing XOR is not detected merely by clean-work checks. -/
theorem omitted_add_keeps_guards :
    (runCheckedRows omittedAdd state1).2 = true := by rfl

/-- Event13558 is the first actual COPY, into private role987. -/
theorem actual_first_copy : chunk67[158]? = some (⟨2,0,987,true⟩ : Event) := by rfl

def firstCopy : Event := ⟨2,0,987,true⟩
def dirtyPrivate : Tree Nat := initial.put 987 (1 <<< 243)

theorem dirty_private_copy_rejected : rowChecks dirtyPrivate firstCopy = false := by rfl

theorem dirty_private_copy_would_overwrite :
    (rowStep dirtyPrivate firstCopy).get 987 = 1 := by rfl

/-- This is a result of the actual complete word, using its checked certificate. -/
theorem literal_helper_three_survives :
    (runRows forwardWord initial).get 243 = 1 <<< 243 := by
  rw [literal_word_rows]
  rfl

/-- The complete word cannot have the often-mistaken all-zero helper endpoint. -/
theorem literal_helper_three_not_zero :
    (runRows forwardWord initial).get 243 ≠ 0 := by
  rw [literal_helper_three_survives]
  decide

#print axioms omitted_add_changes_row
#print axioms omitted_add_keeps_guards
#print axioms dirty_private_copy_rejected
#print axioms dirty_private_copy_would_overwrite
#print axioms literal_helper_three_survives
#print axioms literal_helper_three_not_zero
end SourceControls
