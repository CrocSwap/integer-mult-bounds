import Current1094HelperRowInterface

/-!
Four-call block021: exact calls84,85,86,87 in original order.
All four structural row clauses remain genuine kernel checks. This source
supplies no other block. See the shared interface for exhaustive join and
attribution; original PR1094 owner data is reused without transformation.
Apache-2.0; prepared with OpenAI assistance. Uncompiled source proposal.
-/
set_option Elab.async false
namespace CurrentMain.Current1094CallSequenceHelpersStructural

theorem block021_checked : ∀ offset : Fin 4,
    SortedRowOK (blockRow (21 : Fin 36) offset) := by
  unfold SortedRowOK
  decide +kernel

end CurrentMain.Current1094CallSequenceHelpersStructural
#print axioms CurrentMain.Current1094CallSequenceHelpersStructural.block021_checked
