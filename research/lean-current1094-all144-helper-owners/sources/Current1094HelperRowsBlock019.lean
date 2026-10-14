import Current1094HelperRowInterface

/-!
Four-call block019: exact calls76,77,78,79 in original order.
All four structural row clauses remain genuine kernel checks. This source
supplies no other block. See the shared interface for exhaustive join and
attribution; original PR1094 owner data is reused without transformation.
Apache-2.0; prepared with OpenAI assistance. Uncompiled source proposal.
-/
set_option Elab.async false
namespace CurrentMain.Current1094CallSequenceHelpersStructural

theorem block019_checked : ∀ offset : Fin 4,
    SortedRowOK (blockRow (19 : Fin 36) offset) := by
  unfold SortedRowOK
  decide +kernel

end CurrentMain.Current1094CallSequenceHelpersStructural
#print axioms CurrentMain.Current1094CallSequenceHelpersStructural.block019_checked
