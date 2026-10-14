import GuardedParsedLabelLowering
import Current1094Helper450CompanionLabels

/-!
UNCOMPILED exact23-row decoded companion slice. Both source orientations have
these identical raw relabel rows; all part/rank/pair fields are retained.
The original reviewed extraction44559112 is the source-binding input. This
proves decoder output and typed-event correspondence for these23 rows only.
It does not assert that no selected write was omitted from a whole raw prefix,
or derive full-prefix phase-cut transport, physical recipes or execution.

Context is arbitrary except for the actual L508 endpoint2/999 when used by its
residual wrapper. Patching those two values is a proof device: the final theorem
uses the explicit source endpoint facts to prove the patch equals the supplied
context. No default identity or guessed labels are used for other registers.

Upstream source and Apache-2.0 credits are retained in the companion/schema
packets: DreamingOfClouds, Jeremy Kothe, icekylinx and Hanson Sun/PR1611.
New preparation with OpenAI assistance; no compiler or supplier execution.
-/
set_option Elab.async false
namespace CurrentMain.Current1094CompanionDecodedRows
open CurrentMain.Current1094Helper450RelabelSlice
open CurrentMain.GuardedParsedLabelLowering
open CurrentMain.SelectedSourceSyntax (Value)

def selectedRows : List Value := [
  .array [.text "adapter", .text "old_to_new", .integer 157, .integer 0],
  .array [.text "adapter", .text "old_to_new", .integer 219, .integer 0],
  .array [.text "adapter", .text "old_to_new", .integer 230, .integer 0],
  .array [.text "residual_adapter", .text "pre", .integer 508, .integer 2, .integer 999],
  .array [.text "climb", .text "A", .integer 230, .integer 0, .integer 12, .integer 1],
  .array [.text "climb", .text "A", .integer 230, .integer 12, .integer 25, .integer 1],
  .array [.text "climb", .text "A", .integer 230, .integer 25, .integer 31, .integer 1],
  .array [.text "climb", .text "B", .integer 157, .integer 0, .integer 2, .integer 1],
  .array [.text "climb", .text "B", .integer 219, .integer 0, .integer 2, .integer 1],
  .array [.text "climb", .text "B", .integer 157, .integer 2, .integer 173, .integer 1],
  .array [.text "climb", .text "B", .integer 219, .integer 2, .integer 172, .integer 1],
  .array [.text "climb", .text "B", .integer 230, .integer 31, .integer 550, .integer 3],
  .array [.text "climb", .text "B", .integer 508, .integer 2, .integer 552, .integer 2],
  .array [.text "climb", .text "B", .integer 508, .integer 552, .integer 556, .integer 3],
  .array [.text "climb", .text "B", .integer 219, .integer 172, .integer 600, .integer 2],
  .array [.text "climb", .text "B", .integer 157, .integer 173, .integer 750, .integer 5],
  .array [.text "climb", .text "B", .integer 508, .integer 556, .integer 750, .integer 1],
  .array [.text "climb", .text "B", .integer 219, .integer 600, .integer 751, .integer 3],
  .array [.text "climb", .text "B", .integer 230, .integer 550, .integer 755, .integer 1],
  .array [.text "climb", .text "B", .integer 219, .integer 751, .integer 859, .integer 1],
  .array [.text "climb", .text "B", .integer 157, .integer 750, .integer 867, .integer 1],
  .array [.text "climb", .text "cleanup_tail", .integer 508, .integer 750, .integer 999, .integer 1],
  .array [.text "climb", .text "cleanup_tail", .integer 230, .integer 755, .integer 999, .integer 1]]

def selectedInstructions : List Instruction := [
  .action (.relabel (.inl 157) (.frame (.canonical 0)) (.frame (.canonical 0)) .identity),
  .action (.relabel (.inl 219) (.frame (.canonical 0)) (.frame (.canonical 0)) .identity),
  .action (.relabel (.inl 230) (.frame (.canonical 0)) (.frame (.canonical 0)) .identity),
  .action (.relabel (.inl 508) (.prew (.inl 508)) (.frame (.canonical 2)) (.inverseRight 508 2 999 false)),
  .action (.relabel (.inl 230) (.frame (.canonical 0)) (.frame (.canonical 12)) (.child "A" 230 0 12 1)),
  .action (.relabel (.inl 230) (.frame (.canonical 12)) (.frame (.canonical 25)) (.child "A" 230 12 25 1)),
  .action (.relabel (.inl 230) (.frame (.canonical 25)) (.frame (.canonical 31)) (.child "A" 230 25 31 1)),
  .action (.relabel (.inl 157) (.frame (.canonical 0)) (.frame (.canonical 2)) (.child "B" 157 0 2 1)),
  .action (.relabel (.inl 219) (.frame (.canonical 0)) (.frame (.canonical 2)) (.child "B" 219 0 2 1)),
  .action (.relabel (.inl 157) (.frame (.canonical 2)) (.frame (.canonical 173)) (.child "B" 157 2 173 1)),
  .action (.relabel (.inl 219) (.frame (.canonical 2)) (.frame (.canonical 172)) (.child "B" 219 2 172 1)),
  .action (.relabel (.inl 230) (.frame (.canonical 31)) (.frame (.canonical 550)) (.child "B" 230 31 550 3)),
  .action (.relabel (.inl 508) (.frame (.canonical 2)) (.frame (.canonical 552)) (.child "B" 508 2 552 2)),
  .action (.relabel (.inl 508) (.frame (.canonical 552)) (.frame (.canonical 556)) (.child "B" 508 552 556 3)),
  .action (.relabel (.inl 219) (.frame (.canonical 172)) (.frame (.canonical 600)) (.child "B" 219 172 600 2)),
  .action (.relabel (.inl 157) (.frame (.canonical 173)) (.frame (.canonical 750)) (.child "B" 157 173 750 5)),
  .action (.relabel (.inl 508) (.frame (.canonical 556)) (.frame (.canonical 750)) (.child "B" 508 556 750 1)),
  .action (.relabel (.inl 219) (.frame (.canonical 600)) (.frame (.canonical 751)) (.child "B" 219 600 751 3)),
  .action (.relabel (.inl 230) (.frame (.canonical 550)) (.frame (.canonical 755)) (.child "B" 230 550 755 1)),
  .action (.relabel (.inl 219) (.frame (.canonical 751)) (.frame (.canonical 859)) (.child "B" 219 751 859 1)),
  .action (.relabel (.inl 157) (.frame (.canonical 750)) (.frame (.canonical 867)) (.child "B" 157 750 867 1)),
  .action (.relabel (.inl 508) (.frame (.canonical 750)) (.frame (.canonical 999)) (.child "cleanup_tail" 508 750 999 1)),
  .action (.relabel (.inl 230) (.frame (.canonical 755)) (.frame (.canonical 999)) (.child "cleanup_tail" 230 755 999 1))]

def selectedRawIndices : List Nat := [7559, 7621, 7632, 7910, 9406, 9474, 9496, 12768, 12770, 13428, 13430, 14097, 14140, 14142, 14444, 15142, 15143, 15145, 15170, 15831, 15867, 16493, 16506]
def selectedEventIndices : List Nat := [7557, 7619, 7630, 7908, 9403, 9471, 9493, 12763, 12765, 13423, 13425, 14092, 14135, 14137, 14439, 15137, 15138, 15140, 15165, 15826, 15862, 16487, 16500]

private def at508 (ctx : Context) : Context :=
  ⟨Function.update ctx.start 508 2, Function.update ctx.terminal 508 999⟩

private theorem at508_eq (ctx : Context)
    (hE : ctx.start 508 = 2) (hU : ctx.terminal 508 = 999) : at508 ctx = ctx := by
  cases ctx with
  | mk start terminal =>
      have hs : Function.update start 508 2 = start := by
        funext r
        by_cases h : r = 508
        · subst r; simpa using hE.symm
        · simp [Function.update, h]
      have ht : Function.update terminal 508 999 = terminal := by
        funext r
        by_cases h : r = 508
        · subst r; simpa using hU.symm
        · simp [Function.update, h]
      simp only [at508, hs, ht]

/-- Literal reduction checks every raw token, bound, part and recipe field.
Only two endpoint fields are consulted by this selected slice. -/
private theorem decoded_at508 (ctx : Context) :
    selectedRows.map (decode (at508 ctx)) = selectedInstructions.map some := by
  rfl

theorem selected_decode (ctx : Context)
    (hE : ctx.start 508 = 2) (hU : ctx.terminal 508 = 999) :
    selectedRows.map (decode ctx) = selectedInstructions.map some := by
  have h := decoded_at508 ctx
  rw [at508_eq ctx hE hU] at h
  exact h

private def eventAt (l : Register → Label) : Instruction →
    Option (LemmaG.Event Register Label Rat)
  | .phase _ => none
  | .action a => some (a.event l)

/-- For these relabel rows the Event is independent of l. No stateful COPY is
present, and no physical operations are dropped from an asserted full word. -/
theorem selected_events_exact (l : Register → Label) :
    selectedInstructions.filterMap (eventAt l) =
      Current1094Helper450CompanionLabels.moves.map
        Current1094Helper450CompanionLabels.Move.event := by
  rfl

theorem selected_indices_exact :
    selectedRawIndices = Current1094Helper450CompanionLabels.moves.map
        Current1094Helper450CompanionLabels.Move.rawIndex ∧
    selectedEventIndices = Current1094Helper450CompanionLabels.moves.map
        Current1094Helper450CompanionLabels.Move.eventIndex := by
  exact ⟨rfl, rfl⟩

end CurrentMain.Current1094CompanionDecodedRows
#print axioms CurrentMain.Current1094CompanionDecodedRows.selected_decode
#print axioms CurrentMain.Current1094CompanionDecodedRows.selected_events_exact
#print axioms CurrentMain.Current1094CompanionDecodedRows.selected_indices_exact
