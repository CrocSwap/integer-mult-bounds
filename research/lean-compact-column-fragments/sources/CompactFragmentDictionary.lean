import CompactNatColumnFragment
import RecoveredJsonProviderEntry

/-!
Reusable connection between a compact Nat-column fragment and a named entry in
an actual dictionary AST. Execution validates the original fragment bytes,
executes the unchanged provider recovery on the dictionary/key, then compares
the two complete ordered bounded-column lists. The recovery result retains its
original dictionary columns, so no extra dictionary lookup is needed here.

Successful execution gives the same parsed fragment AST at the selected named
field, exact original byte equality and the independently defined column
operator with both inverse laws. Array order and repeated columns are retained.
No supplied auxiliary JSON, inverse table or operator equality is an input.

Completeness reuses the existing restricted checked-Candidate class and keeps
the compact parser round-trip and actual named-field decoding premises visible.
The dictionary's source bytes, duplicate-key history, physical containment of
the fragment, cryptographic digest/key identity and all execution costs remain
separate. No selected census or new JSON grammar is introduced.
Author-checked context: kappa=836330098538459/500000000000000000
=0.001672660197076918; these generic results do not use or change kappa.
Credits: Jeremy Kothe T16/PR514 packed-column payload and inherited geometry;
Rohan Arun PR1094; accepted bank/frame parser, column codec and recovery work;
Lean/Mathlib. James Chang with OpenAI assistance, Apache-2.0.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.CompactFragmentDictionary
open CheckedBinaryChart (Address Candidate)
open JsonPackedColumnDictionary (Columns CheckedEntry decodeColumns dictionaryColumns columnOperator)
open ParsedBinaryChartCertificate (columnFunction vectorValue)
open CompactNatColumnFragment (validateFragment payload natValues)
open RecoveredJsonProviderEntry (recoverEntry)

/-- Compare complete original-order lists after both actual computations. -/
def recoverFragment (n : Nat) (bytes : ByteArray) (dictionary : Lean.Json)
    (key : String) (update coefficients : Address n) : Option (CheckedEntry n) := do
  let cols ← validateFragment n bytes
  let r ← recoverEntry n dictionary key update coefficients
  if cols.val = r.columns.val then some r else none

/-- Invalid or noncompact fragments never reach an accepted result. -/
theorem recoverFragment_reject {n : Nat} (bytes : ByteArray) (dictionary : Lean.Json)
    (key : String) (update coefficients : Address n)
    (h : validateFragment n bytes = none) :
    recoverFragment n bytes dictionary key update coefficients = none := by
  unfold recoverFragment
  rw [h]
  rfl

/-- The executed list comparison identifies the full dependent column values. -/
theorem recoverFragment_inputs {n : Nat} (bytes : ByteArray) (dictionary : Lean.Json)
    (key : String) (update coefficients : Address n) (r : CheckedEntry n)
    (h : recoverFragment n bytes dictionary key update coefficients = some r) :
    validateFragment n bytes = some r.columns ∧
      recoverEntry n dictionary key update coefficients = some r := by
  unfold recoverFragment at h
  obtain ⟨cols, hf, ht⟩ := Option.bind_eq_some_iff.mp h
  obtain ⟨found, hr, he⟩ := Option.bind_eq_some_iff.mp ht
  by_cases hm : cols.val = found.columns.val
  · have hh : found = r := Option.some.inj (by simpa only [if_pos hm] using he)
    have hc : cols = found.columns := Subtype.ext hm
    rw [hh] at hc hr
    rw [hc] at hf
    exact ⟨hf, hr⟩
  · simp only [if_neg hm] at he
    cases he

/-- The exact parsed fragment is the original named field, with all columns and
bytes preserved; operator equality and inverses come from actual recovery. -/
theorem recoverFragment_sound {n : Nat} (bytes : ByteArray) (dictionary : Lean.Json)
    (key : String) (update coefficients : Address n) (r : CheckedEntry n)
    (h : recoverFragment n bytes dictionary key update coefficients = some r) :
    (∃ (text : String) (raw : Lean.Json),
      String.fromUTF8? bytes = some text ∧ Lean.Json.parse text = .ok raw ∧
      dictionary.getObjVal? key = .ok raw ∧ decodeColumns n raw = some r.columns ∧
      StrictJsonValueBridge.reencode 2 (vectorValue r.columns) = raw) ∧
    bytes = payload r.columns ∧ (natValues r.columns).length = n ∧
    (∀ j, columnFunction r.columns j < 2 ^ n) ∧
    columnOperator r.columns =
      (CheckedBinaryChart.checkedEquiv r.certificate.val r.certificate.property).toLinearMap ∧
    (∀ x, CheckedBinaryChart.inverseAddress r.certificate.val (columnOperator r.columns x) = x) ∧
    (∀ x, columnOperator r.columns (CheckedBinaryChart.inverseAddress r.certificate.val x) = x) := by
  obtain ⟨hf, hr⟩ := recoverFragment_inputs bytes dictionary key update coefficients r h
  obtain ⟨⟨text, raw, hu, hj, hd, hv⟩, hb, hl, hbound⟩ :=
    CompactNatColumnFragment.validate_sound bytes r.columns hf
  obtain ⟨⟨entry, he, hv'⟩, hop, hleft, hright⟩ :=
    RecoveredJsonProviderEntry.recoverEntry_sound dictionary key update coefficients r hr
  have same : entry = raw := hv'.symm.trans hv
  rw [same] at he
  exact ⟨⟨text, raw, hu, hj, he, hd, hv⟩, hb, hl, hbound, hop, hleft, hright⟩

/-- Restricted completeness retains both actual parser and named-field premises.
The checked Candidate is proof-side class evidence, not executable input. -/
theorem recoverFragment_complete {n : Nat} (dictionary : Lean.Json) (key : String)
    (cols : Columns n) (c : Candidate n) (h : CheckedBinaryChart.check c = true)
    (hc : c.columns = columnFunction cols)
    (hd : dictionaryColumns n dictionary key = some cols)
    (hparse : ByteJsonGlobalCall.parseBytes (payload cols) =
      .ok (StrictJsonValueBridge.reencode 2 (vectorValue cols))) :
    recoverFragment n (payload cols) dictionary key c.updateVector c.coefficients =
      some (⟨cols, ⟨c, h⟩, fun j => congrFun hc j⟩ : CheckedEntry n) := by
  unfold recoverFragment
  rw [CompactNatColumnFragment.validate_complete cols hparse]
  change (recoverEntry n dictionary key c.updateVector c.coefficients >>= fun r =>
    if cols.val = r.columns.val then some r else none) = _
  rw [RecoveredJsonProviderEntry.recoverEntry_complete dictionary key cols c h hc hd]
  change (if cols.val = cols.val then
    some (⟨cols, ⟨c, h⟩, fun j => congrFun hc j⟩ : CheckedEntry n) else none) = _
  simp only [if_pos rfl, if_true]

end CurrentMain.CompactFragmentDictionary
#print axioms CurrentMain.CompactFragmentDictionary.recoverFragment_reject
#print axioms CurrentMain.CompactFragmentDictionary.recoverFragment_inputs
#print axioms CurrentMain.CompactFragmentDictionary.recoverFragment_sound
#print axioms CurrentMain.CompactFragmentDictionary.recoverFragment_complete
#check @CurrentMain.CompactFragmentDictionary.recoverFragment_sound
#check @CurrentMain.CompactFragmentDictionary.recoverFragment_complete
