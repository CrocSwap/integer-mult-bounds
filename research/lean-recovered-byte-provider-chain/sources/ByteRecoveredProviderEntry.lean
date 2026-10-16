import ByteJsonGlobalCall
import RecoveredJsonProviderEntry

/-!
Reusable byte-input entrypoint for recovered packed-column dictionary charts.
Execution applies the accepted UTF-8/JSON parser to the original ByteArray,
then the unchanged named-entry recovery/checker to that exact dictionary AST.
Its inputs are bytes, key, update vector and coefficient vector. No inverse
table, permutation, auxiliary JSON witness or operator equality is supplied.

Success derives the original conversion equations, actual recovery success,
complete named packed-column field, independent column operator and both
inverse identities. Completeness retains the precise checked single-
transvection/permutation class and exact parser/named-field equations.

These statements use the installed parser as an executable function. Unicode/
JSON standards correctness, lexical normalization and duplicate-key policies,
artifact digests, authenticity of a named key and success on actual selected
bytes remain separate. No new JSON grammar or selected table census is added.
Binary address operators do not supply complex phases, affine shifts, physical
chart direction, allocation/executor, precision or runtime/bit costs.
Author-checked context: kappa=836330098538459/500000000000000000
=0.001672660197076918; these generic statements do not use or change kappa.
Credits: Lean UTF-8/JSON parser authors, accepted bank/frame strict parser and
chart components, Jeremy Kothe T16/PR514 and PR484/507 lineage, Rohan Arun
PR1094. James Chang with OpenAI assistance; Apache-2.0.
UNCOMPILED source preparation.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.ByteRecoveredProviderEntry
open CheckedBinaryChart (Address Candidate)
open JsonPackedColumnDictionary (Columns CheckedEntry dictionaryColumns columnOperator)
open ParsedBinaryChartCertificate (columnFunction vectorValue)

/-- Actual byte parsing and restricted recovery, with no default dictionary. -/
def recoverBytes (n : Nat) (bytes : ByteArray) (key : String)
    (update coefficients : Address n) : Option (CheckedEntry n) :=
  match ByteJsonGlobalCall.parseBytes bytes with
  | .error _ => none
  | .ok dictionary =>
      RecoveredJsonProviderEntry.recoverEntry n dictionary key update coefficients

/-- Either parser error prevents the downstream recovery call. Error detail
remains available through the unchanged parseBytes API. -/
theorem recoverBytes_parse_error {n : Nat} (bytes : ByteArray) (key : String)
    (update coefficients : Address n) (error : ByteJsonGlobalCall.InputError)
    (hp : ByteJsonGlobalCall.parseBytes bytes = .error error) :
    recoverBytes n bytes key update coefficients = none := by
  simp only [recoverBytes, hp]

/-- Completeness for the restricted checked class and an actually parsed,
exact named field. The proof-side Candidate is not an executable input. -/
theorem recoverBytes_complete {n : Nat} (bytes : ByteArray) (text : String)
    (dictionary : Lean.Json) (key : String) (cols : Columns n) (c : Candidate n)
    (h : CheckedBinaryChart.check c = true)
    (hc : c.columns = columnFunction cols)
    (hu : String.fromUTF8? bytes = some text)
    (hj : Lean.Json.parse text = .ok dictionary)
    (hd : dictionaryColumns n dictionary key = some cols) :
    recoverBytes n bytes key c.updateVector c.coefficients =
      some (⟨cols, ⟨c, h⟩, fun j => congrFun hc j⟩ : CheckedEntry n) := by
  have hp : ByteJsonGlobalCall.parseBytes bytes = .ok dictionary := by
    simp only [ByteJsonGlobalCall.parseBytes, hu, hj]
  simpa only [recoverBytes, hp] using
    RecoveredJsonProviderEntry.recoverEntry_complete dictionary key cols c h hc hd

/-- The sole premise is successful execution on the original bytes. It yields
both parser equations and independent operator/inverse facts, with the exact
named field and unchanged recovery call retained. -/
theorem recoverBytes_sound {n : Nat} (bytes : ByteArray) (key : String)
    (update coefficients : Address n) (r : CheckedEntry n)
    (h : recoverBytes n bytes key update coefficients = some r) :
    (∃ (text : String) (dictionary raw : Lean.Json),
      String.fromUTF8? bytes = some text ∧ Lean.Json.parse text = .ok dictionary ∧
      RecoveredJsonProviderEntry.recoverEntry n dictionary key update coefficients = some r ∧
      dictionary.getObjVal? key = .ok raw ∧
      StrictJsonValueBridge.reencode 2 (vectorValue r.columns) = raw) ∧
    columnOperator r.columns =
      (CheckedBinaryChart.checkedEquiv r.certificate.val r.certificate.property).toLinearMap ∧
    (∀ x, CheckedBinaryChart.inverseAddress r.certificate.val (columnOperator r.columns x) = x) ∧
    (∀ x, columnOperator r.columns (CheckedBinaryChart.inverseAddress r.certificate.val x) = x) := by
  cases hp : ByteJsonGlobalCall.parseBytes bytes with
  | error error =>
      simp only [recoverBytes, hp] at h
      cases h
  | ok dictionary =>
      have he : RecoveredJsonProviderEntry.recoverEntry n dictionary key update coefficients =
          some r := by
        simpa only [recoverBytes, hp] using h
      obtain ⟨text, hu, hj⟩ := ByteJsonGlobalCall.parseBytes_sound bytes dictionary hp
      obtain ⟨⟨raw, hk, hr⟩, hop, hleft, hright⟩ :=
        RecoveredJsonProviderEntry.recoverEntry_sound dictionary key update coefficients r he
      exact ⟨⟨text, dictionary, raw, hu, hj, he, hk, hr⟩, hop, hleft, hright⟩

end CurrentMain.ByteRecoveredProviderEntry
#print axioms CurrentMain.ByteRecoveredProviderEntry.recoverBytes_parse_error
#print axioms CurrentMain.ByteRecoveredProviderEntry.recoverBytes_complete
#print axioms CurrentMain.ByteRecoveredProviderEntry.recoverBytes_sound
#check @CurrentMain.ByteRecoveredProviderEntry.recoverBytes_complete
#check @CurrentMain.ByteRecoveredProviderEntry.recoverBytes_sound
