import CheckedArraySlice
import CompactFragmentDictionary

/-!
An actual byte-input join: check a supplied fragment at a supplied artifact
offset, parse the same artifact bytes with the accepted byte entrypoint, then
run the accepted compact fragment/dictionary recovery checker on that parsed
AST. No detached dictionary AST, assumed slice equality or auxiliary operator
certificate is supplied to execution.

Success derives exact ordered byte containment, both artifact and fragment
UTF-8/JSON parser equations, the named field's complete column AST, exact compact
fragment bytes and the recovered column operator with both inverses. Repeated
values and original byte positions are retained by the existing checks.

Literal containment at the offset does not prove that this occurrence is the
structural JSON field location. The supplied artifact value still needs external
file provenance and digest authentication. Parser implementation/specification,
duplicate-key policy, cryptographic identity, physical execution and costs remain
separate. No parser is unfolded, replaced or assigned a new grammar here.
Author-checked context: kappa=836330098538459/500000000000000000
=0.001672660197076918; generic statements do not use or change kappa.
Credits: Lean/Mathlib, Jeremy Kothe T16/PR514 and Rohan Arun PR1094, accepted
bank/frame byte, slice, compact-column and recovery components. James Chang
with OpenAI assistance, Apache-2.0.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.LocatedCompactEntry
open CheckedBinaryChart (Address Candidate)
open JsonPackedColumnDictionary (Columns CheckedEntry decodeColumns dictionaryColumns columnOperator)
open ParsedBinaryChartCertificate (vectorValue columnFunction)
open CompactNatColumnFragment (payload natValues)
open CheckedArraySlice (checkBytes)
open CompactFragmentDictionary (recoverFragment)

/-- Both arrays are actual inputs; the same artifact supplies the dictionary AST. -/
def recoverAt (n : Nat) (artifact fragment : ByteArray) (start : Nat) (key : String)
    (update coefficients : Address n) : Option (CheckedEntry n) :=
  if checkBytes artifact fragment start then
    match ByteJsonGlobalCall.parseBytes artifact with
    | .error _ => none
    | .ok dictionary => recoverFragment n fragment dictionary key update coefficients
  else none

theorem recoverAt_reject {n : Nat} (artifact fragment : ByteArray) (start : Nat)
    (key : String) (update coefficients : Address n)
    (h : checkBytes artifact fragment start = false) :
    recoverAt n artifact fragment start key update coefficients = none := by
  unfold recoverAt
  rw [h]
  rfl

/-- Actual combined success retains the original artifact parser computation. -/
theorem recoverAt_inputs {n : Nat} (artifact fragment : ByteArray) (start : Nat)
    (key : String) (update coefficients : Address n) (r : CheckedEntry n)
    (h : recoverAt n artifact fragment start key update coefficients = some r) :
    checkBytes artifact fragment start = true ∧
      ∃ dictionary, ByteJsonGlobalCall.parseBytes artifact = .ok dictionary ∧
        recoverFragment n fragment dictionary key update coefficients = some r := by
  by_cases hb : checkBytes artifact fragment start = true
  · cases hp : ByteJsonGlobalCall.parseBytes artifact with
    | error error =>
        simp only [recoverAt, if_pos hb, hp] at h
        cases h
    | ok dictionary =>
        have hr : recoverFragment n fragment dictionary key update coefficients = some r := by
          simpa only [recoverAt, if_pos hb, hp] using h
        exact ⟨hb, dictionary, by simp only [hp], hr⟩
  · simp only [recoverAt, if_neg hb] at h
    cases h

/-- Containment, both actual parser equations and semantic recovery are derived
from this single executed input path, without identifying a structural field offset. -/
theorem recoverAt_sound {n : Nat} (artifact fragment : ByteArray) (start : Nat)
    (key : String) (update coefficients : Address n) (r : CheckedEntry n)
    (h : recoverAt n artifact fragment start key update coefficients = some r) :
    start + fragment.size ≤ artifact.size ∧
    (∀ i : Fin fragment.size, ∃ hi : start + i.val < artifact.size,
      artifact.data[start + i.val]'hi = fragment.data[i.val]'i.isLt) ∧
    artifact.data.extract 0 start ++ fragment.data ++
      artifact.data.extract (start + fragment.size) artifact.size = artifact.data ∧
    (∃ (wholeText : String) (dictionary : Lean.Json) (text : String) (raw : Lean.Json),
      String.fromUTF8? artifact = some wholeText ∧ Lean.Json.parse wholeText = .ok dictionary ∧
      String.fromUTF8? fragment = some text ∧ Lean.Json.parse text = .ok raw ∧
      dictionary.getObjVal? key = .ok raw ∧ decodeColumns n raw = some r.columns ∧
      StrictJsonValueBridge.reencode 2 (vectorValue r.columns) = raw) ∧
    fragment = payload r.columns ∧ (natValues r.columns).length = n ∧
    (∀ j, columnFunction r.columns j < 2 ^ n) ∧
    columnOperator r.columns =
      (CheckedBinaryChart.checkedEquiv r.certificate.val r.certificate.property).toLinearMap ∧
    (∀ x, CheckedBinaryChart.inverseAddress r.certificate.val (columnOperator r.columns x) = x) ∧
    (∀ x, columnOperator r.columns (CheckedBinaryChart.inverseAddress r.certificate.val x) = x) := by
  obtain ⟨hs, dictionary, hp, hr⟩ := recoverAt_inputs artifact fragment start key update coefficients r h
  obtain ⟨wholeText, hw, hj⟩ := ByteJsonGlobalCall.parseBytes_sound artifact dictionary hp
  obtain ⟨⟨text, raw, hu, hjf, hk, hd, hv⟩, hb, hl, hbound, hop, hleft, hright⟩ :=
    CompactFragmentDictionary.recoverFragment_sound fragment dictionary key update coefficients r hr
  exact ⟨((CheckedArraySlice.checkBytes_iff artifact fragment start).mp hs).1,
    CheckedArraySlice.checkBytes_position artifact fragment start hs,
    CheckedArraySlice.checkBytes_decomposition artifact fragment start hs,
    ⟨wholeText, dictionary, text, raw, hw, hj, hu, hjf, hk, hd, hv⟩,
    hb, hl, hbound, hop, hleft, hright⟩

/-- Restricted completeness keeps both parser premises and the actual bounded
slice check explicit; no whole-artifact authenticity is inferred. -/
theorem recoverAt_complete {n : Nat} (artifact : ByteArray) (start : Nat)
    (dictionary : Lean.Json) (key : String) (cols : Columns n) (c : Candidate n)
    (h : CheckedBinaryChart.check c = true) (hc : c.columns = columnFunction cols)
    (hd : dictionaryColumns n dictionary key = some cols)
    (hs : checkBytes artifact (payload cols) start = true)
    (hp : ByteJsonGlobalCall.parseBytes artifact = .ok dictionary)
    (hf : ByteJsonGlobalCall.parseBytes (payload cols) =
      .ok (StrictJsonValueBridge.reencode 2 (vectorValue cols))) :
    recoverAt n artifact (payload cols) start key c.updateVector c.coefficients =
      some (⟨cols, ⟨c, h⟩, fun j => congrFun hc j⟩ : CheckedEntry n) := by
  unfold recoverAt
  rw [if_pos hs, hp]
  exact CompactFragmentDictionary.recoverFragment_complete dictionary key cols c h hc hd hf

end CurrentMain.LocatedCompactEntry
#print axioms CurrentMain.LocatedCompactEntry.recoverAt_reject
#print axioms CurrentMain.LocatedCompactEntry.recoverAt_inputs
#print axioms CurrentMain.LocatedCompactEntry.recoverAt_sound
#print axioms CurrentMain.LocatedCompactEntry.recoverAt_complete
#check @CurrentMain.LocatedCompactEntry.recoverAt_sound
#check @CurrentMain.LocatedCompactEntry.recoverAt_complete
