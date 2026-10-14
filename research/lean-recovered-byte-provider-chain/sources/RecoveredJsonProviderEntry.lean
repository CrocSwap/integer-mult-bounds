import RecoveredProviderChart
import JsonPackedColumnDictionary

/-!
Actual named packed-column entries now generate their auxiliary certificate
internally. Execution takes the dictionary/key and provider update/form vectors,
not inverse tables, a supplied permutation, an auxiliary JSON certificate or
operator equality. It reuses finite recovery, canonical JSON generation and the
unchanged dictionary certifier. The dictionary AST is immutable; its second
lookup in the reused certifier refers to exactly the same value and key.

Completeness is deliberately restricted to the accepted single-transvection /
permutation factorization. The proof-side checked Candidate specifies this
class; it is not an executable input. Source-byte/key correspondence and actual
selected entry equality, complex phases, affine shifts, physical direction,
allocation/executor and all costs remain separate. No table census or complexity
claim accompanies the finite searches or repeated lookup.
Author-checked context: kappa=836330098538459/500000000000000000.
Generic statements do not use kappa. Credits: Jeremy Kothe T16/PR514 and inherited
PR484/507 lineage, Rohan Arun PR1094, accepted bank/frame strict JSON/chart
components and Lean/Mathlib. James Chang with OpenAI assistance, Apache-2.0.
UNCOMPILED source preparation.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.RecoveredJsonProviderEntry
open CheckedBinaryChart (Address Candidate)
open JsonPackedColumnDictionary (Columns CheckedEntry dictionaryColumns certifyEntry columnOperator)
open ParsedBinaryChartCertificate (columnFunction vectorValue)

/-- Same original field data, now with an internally constructed witness. -/
def recoverEntry (n : Nat) (dictionary : Lean.Json) (key : String)
    (update coefficients : Address n) : Option (CheckedEntry n) := do
  let cols ← dictionaryColumns n dictionary key
  let cert ← RecoveredProviderChart.recover ⟨columnFunction cols, update, coefficients⟩
  certifyEntry 3 n dictionary key
    (JsonBinaryChartInterpreter.canonicalJson cert.val cert.property)

/-- The existing certifier accepts a matching checked Candidate's canonical JSON. -/
theorem certifyEntry_generated {n : Nat} (dictionary : Lean.Json) (key : String)
    (cols : Columns n) (c : Candidate n) (h : CheckedBinaryChart.check c = true)
    (hc : c.columns = columnFunction cols)
    (hd : dictionaryColumns n dictionary key = some cols) :
    certifyEntry 3 n dictionary key (JsonBinaryChartInterpreter.canonicalJson c h) =
      some (⟨cols, ⟨c, h⟩, fun j => congrFun hc j⟩ : CheckedEntry n) := by
  unfold certifyEntry
  rw [hd]
  change (JsonBinaryChartInterpreter.certify 3 n (JsonBinaryChartInterpreter.canonicalJson c h) >>=
    fun cert => if hm : ∀ j, cert.val.columns j = columnFunction cols j then
      some (⟨cols, cert, hm⟩ : CheckedEntry n) else none) =
    some (⟨cols, ⟨c, h⟩, fun j => congrFun hc j⟩ : CheckedEntry n)
  rw [JsonBinaryChartInterpreter.certify_canonical c h]
  change (if hm : ∀ j, c.columns j = columnFunction cols j then
    some (⟨cols, ⟨c, h⟩, hm⟩ : CheckedEntry n) else none) =
    some (⟨cols, ⟨c, h⟩, fun j => congrFun hc j⟩ : CheckedEntry n)
  rw [dif_pos (fun j => congrFun hc j)]

/-- Actual recovery and auxiliary certification succeed for the precise class,
using the original named-entry correspondence as the only source-data premise. -/
theorem recoverEntry_complete {n : Nat} (dictionary : Lean.Json) (key : String)
    (cols : Columns n) (c : Candidate n) (h : CheckedBinaryChart.check c = true)
    (hc : c.columns = columnFunction cols)
    (hd : dictionaryColumns n dictionary key = some cols) :
    recoverEntry n dictionary key c.updateVector c.coefficients =
      some (⟨cols, ⟨c, h⟩, fun j => congrFun hc j⟩ : CheckedEntry n) := by
  unfold recoverEntry
  rw [hd]
  change (RecoveredProviderChart.recover
    (⟨columnFunction cols, c.updateVector, c.coefficients⟩ : RecoveredProviderChart.Input n) >>=
    fun cert => certifyEntry 3 n dictionary key
      (JsonBinaryChartInterpreter.canonicalJson cert.val cert.property)) =
    some (⟨cols, ⟨c, h⟩, fun j => congrFun hc j⟩ : CheckedEntry n)
  have hi : (⟨columnFunction cols, c.updateVector, c.coefficients⟩ : RecoveredProviderChart.Input n) =
      RecoveredProviderChart.inputOf c := by
    rw [← hc]
    rfl
  rw [hi, RecoveredProviderChart.recover_complete c h]
  change certifyEntry 3 n dictionary key (JsonBinaryChartInterpreter.canonicalJson c h) = _
  exact certifyEntry_generated dictionary key cols c h hc hd

/-- Successful execution retains the real recovery step and generated witness. -/
theorem recoverEntry_generated {n : Nat} (dictionary : Lean.Json) (key : String)
    (update coefficients : Address n) (r : CheckedEntry n)
    (h : recoverEntry n dictionary key update coefficients = some r) :
    ∃ cols cert, dictionaryColumns n dictionary key = some cols ∧
      RecoveredProviderChart.recover ⟨columnFunction cols, update, coefficients⟩ = some cert ∧
      certifyEntry 3 n dictionary key
        (JsonBinaryChartInterpreter.canonicalJson cert.val cert.property) = some r := by
  unfold recoverEntry at h
  obtain ⟨cols, hd, ht⟩ := Option.bind_eq_some_iff.mp h
  obtain ⟨cert, hr, he⟩ := Option.bind_eq_some_iff.mp ht
  exact ⟨cols, cert, hd, hr, he⟩

/-- The independent dictionary-column operator and both inverses follow from
actual success. No auxiliary certificate is an argument or success premise. -/
theorem recoverEntry_sound {n : Nat} (dictionary : Lean.Json) (key : String)
    (update coefficients : Address n) (r : CheckedEntry n)
    (h : recoverEntry n dictionary key update coefficients = some r) :
    (∃ raw, dictionary.getObjVal? key = .ok raw ∧
      StrictJsonValueBridge.reencode 2 (vectorValue r.columns) = raw) ∧
    columnOperator r.columns =
      (CheckedBinaryChart.checkedEquiv r.certificate.val r.certificate.property).toLinearMap ∧
    (∀ x, CheckedBinaryChart.inverseAddress r.certificate.val (columnOperator r.columns x) = x) ∧
    (∀ x, columnOperator r.columns (CheckedBinaryChart.inverseAddress r.certificate.val x) = x) := by
  obtain ⟨cols, cert, hd, hr, he⟩ := recoverEntry_generated dictionary key update coefficients r h
  have hs := JsonPackedColumnDictionary.certifyEntry_sound 3 dictionary key
    (JsonBinaryChartInterpreter.canonicalJson cert.val cert.property) r he
  exact ⟨hs.1, hs.2.2⟩

end CurrentMain.RecoveredJsonProviderEntry
#print axioms CurrentMain.RecoveredJsonProviderEntry.certifyEntry_generated
#print axioms CurrentMain.RecoveredJsonProviderEntry.recoverEntry_complete
#print axioms CurrentMain.RecoveredJsonProviderEntry.recoverEntry_generated
#print axioms CurrentMain.RecoveredJsonProviderEntry.recoverEntry_sound
#check @CurrentMain.RecoveredJsonProviderEntry.recoverEntry_complete
#check @CurrentMain.RecoveredJsonProviderEntry.recoverEntry_sound
