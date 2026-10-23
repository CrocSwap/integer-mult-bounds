import HexObjectLayout
import LocatedCompactEntry

/-!
A checked complete-layout witness for the compact column dictionary format.
Every witness payload is constructed from the existing bounded ordered Columns
encoder. The original artifact is compared against the complete ordered object,
with actual serialized hex-key validity and uniqueness checked. A bounded index
selects the field; its byte offset is derived from preceding serialized fields.
No arbitrary offset, skipped surrounding context or detached dictionary is used.

Execution retains the existing artifact/fragment parser and provider recovery
checks. It additionally compares every recovered column with the selected typed
witness column; byte equality is not silently used as decimal injectivity or
numeral-parser correctness. Actual success derives the verified layout, selected
columns, parser/named-value equations and independent binary operator/inverses.

The derived position belongs to the verified restricted serialization. This
module does not identify the installed parser's internal source span, prove a
parser round trip, authenticate a file/digest, verify Python serialization or
runtime externs, supply complex phases/physical execution, or bound costs.
Completeness retains the actual parser/named-field and restricted-class premises.
No selected dictionary census or new JSON grammar is introduced.
Author-checked context: kappa=836330098538459/500000000000000000
=0.001672660197076918; generic statements do not use or change kappa.
Credits: Lean/Mathlib, Jeremy Kothe T16/PR514, Rohan Arun PR1094, and accepted
bank/frame byte layout, compact columns, parser and restricted recovery work.
James Chang with OpenAI assistance; Apache-2.0. Uncompiled source preparation.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.CheckedCompactObject
open CheckedBinaryChart (Address Candidate)
open JsonPackedColumnDictionary (Columns CheckedEntry columnOperator dictionaryColumns)
open ParsedBinaryChartCertificate (columnFunction vectorValue)
open CompactNatColumnFragment (payload)

structure Entry (n : Nat) where
  key : String
  columns : Columns n

def toField {n : Nat} (entry : Entry n) : HexObjectLayout.Field :=
  ⟨entry.key, payload entry.columns⟩

def fields {n : Nat} (entries : List (Entry n)) : List HexObjectLayout.Field :=
  entries.map toField

def selected {n : Nat} (entries : List (Entry n)) (i : Fin entries.length) : Entry n :=
  entries[i.val]'i.isLt

def beforeFields {n : Nat} (entries : List (Entry n)) (i : Fin entries.length) :
    List HexObjectLayout.Field := (entries.take i.val).map toField

def afterFields {n : Nat} (entries : List (Entry n)) (i : Fin entries.length) :
    List HexObjectLayout.Field := (entries.drop (i.val + 1)).map toField

def offset {n : Nat} (entries : List (Entry n)) (i : Fin entries.length) : Nat :=
  HexObjectLayout.offset (beforeFields entries i) (toField (selected entries i))

/-- The original bounded index determines a complete split, without missing fields. -/
theorem fields_split {n : Nat} (entries : List (Entry n)) (i : Fin entries.length) :
    fields entries = beforeFields entries i ++
      toField (selected entries i) :: afterFields entries i := by
  have h : entries.take i.val ++ [entries[i.val]'i.isLt] ++
      entries.drop (i.val + 1) = entries := by
    rw [List.take_append_getElem i.isLt, List.take_append_drop]
  have hm := congrArg (List.map (toField (n := n))) h
  simpa only [fields, beforeFields, afterFields, selected, List.map_append,
    List.map_cons, List.map_nil, List.append_assoc, List.nil_append] using hm.symm

/-- Complete artifact equality supplies the selected slice check; it is not a premise. -/
theorem layout_checkBytes {n : Nat} (artifact : ByteArray) (entries : List (Entry n))
    (i : Fin entries.length)
    (h : artifact.data = (HexObjectLayout.encode (fields entries)).data) :
    CheckedArraySlice.checkBytes artifact (payload (selected entries i).columns)
      (offset entries i) = true := by
  have he : artifact.data = (HexObjectLayout.encode (beforeFields entries i ++
      toField (selected entries i) :: afterFields entries i)).data := by
    rw [← fields_split]
    exact h
  exact HexObjectLayout.artifact_checkBytes (beforeFields entries i)
    (toField (selected entries i)) (afterFields entries i) artifact he

/-- Actual keys, full artifact bytes, original index and full recovered columns are checked. -/
def recover (n : Nat) (artifact : ByteArray) (entries : List (Entry n))
    (i : Fin entries.length) (update coefficients : Address n) : Option (CheckedEntry n) :=
  if HexObjectLayout.checkKeys (fields entries) then
    if artifact.data = (HexObjectLayout.encode (fields entries)).data then
      match LocatedCompactEntry.recoverAt n artifact (payload (selected entries i).columns)
          (offset entries i) (selected entries i).key update coefficients with
      | none => none
      | some r => if r.columns.val = (selected entries i).columns.val then some r else none
    else none
  else none

theorem recover_inputs {n : Nat} (artifact : ByteArray) (entries : List (Entry n))
    (i : Fin entries.length) (update coefficients : Address n) (r : CheckedEntry n)
    (h : recover n artifact entries i update coefficients = some r) :
    HexObjectLayout.checkKeys (fields entries) = true ∧
    artifact.data = (HexObjectLayout.encode (fields entries)).data ∧
    r.columns = (selected entries i).columns ∧
    LocatedCompactEntry.recoverAt n artifact (payload (selected entries i).columns)
      (offset entries i) (selected entries i).key update coefficients = some r := by
  by_cases hk : HexObjectLayout.checkKeys (fields entries) = true
  · by_cases ha : artifact.data = (HexObjectLayout.encode (fields entries)).data
    · cases hr : LocatedCompactEntry.recoverAt n artifact (payload (selected entries i).columns)
        (offset entries i) (selected entries i).key update coefficients with
      | none =>
          simp only [recover, if_pos hk, if_pos ha, hr] at h
          cases h
      | some found =>
          by_cases hm : found.columns.val = (selected entries i).columns.val
          · have he : found = r := Option.some.inj
              (by simpa only [recover, if_pos hk, if_pos ha, hr, if_pos hm] using h)
            have hc : found.columns = (selected entries i).columns := Subtype.ext hm
            rw [he] at hc hr
            exact ⟨hk, ha, hc, congrArg some he⟩
          · simp only [recover, if_pos hk, if_pos ha, hr, if_neg hm] at h
            cases h
    · simp only [recover, if_pos hk, if_neg ha] at h
      cases h
  · simp only [recover, if_neg hk] at h
    cases h

/-- The verified complete layout and its computed position accompany actual semantic recovery. -/
theorem recover_layout {n : Nat} (artifact : ByteArray) (entries : List (Entry n))
    (i : Fin entries.length) (update coefficients : Address n) (r : CheckedEntry n)
    (h : recover n artifact entries i update coefficients = some r) :
    (∀ f ∈ fields entries, HexObjectLayout.keyPolicy f.key = true) ∧
    ((fields entries).map (fun f => HexObjectLayout.keyBytes f.key)).Nodup ∧
    artifact.data =
      (HexObjectLayout.prefixBytes (beforeFields entries i) (toField (selected entries i))).toArray ++
        (payload (selected entries i).columns).data ++
        (HexObjectLayout.suffixBytes (afterFields entries i)).toArray ∧
    CheckedArraySlice.checkBytes artifact (payload (selected entries i).columns)
      (offset entries i) = true ∧ r.columns = (selected entries i).columns := by
  obtain ⟨hk, ha, hc, _⟩ := recover_inputs artifact entries i update coefficients r h
  obtain ⟨hkeys, hn⟩ := (HexObjectLayout.checkKeys_iff (fields entries)).mp hk
  refine ⟨hkeys, hn, ?_, layout_checkBytes artifact entries i ha, hc⟩
  rw [ha, fields_split]
  exact HexObjectLayout.encode_decomposition (beforeFields entries i)
    (toField (selected entries i)) (afterFields entries i)

/-- Both original parser computations, the selected named AST, and operator/inverses
are consequences of execution, with no assumed span or target operator equality. -/
theorem recover_sound {n : Nat} (artifact : ByteArray) (entries : List (Entry n))
    (i : Fin entries.length) (update coefficients : Address n) (r : CheckedEntry n)
    (h : recover n artifact entries i update coefficients = some r) :
    r.columns = (selected entries i).columns ∧
    (∃ (wholeText : String) (dictionary : Lean.Json) (text : String) (raw : Lean.Json),
      String.fromUTF8? artifact = some wholeText ∧ Lean.Json.parse wholeText = .ok dictionary ∧
      String.fromUTF8? (payload (selected entries i).columns) = some text ∧
      Lean.Json.parse text = .ok raw ∧ dictionary.getObjVal? (selected entries i).key = .ok raw ∧
      JsonPackedColumnDictionary.decodeColumns n raw = some r.columns ∧
      StrictJsonValueBridge.reencode 2 (vectorValue r.columns) = raw) ∧
    columnOperator r.columns =
      (CheckedBinaryChart.checkedEquiv r.certificate.val r.certificate.property).toLinearMap ∧
    (∀ x, CheckedBinaryChart.inverseAddress r.certificate.val (columnOperator r.columns x) = x) ∧
    (∀ x, columnOperator r.columns (CheckedBinaryChart.inverseAddress r.certificate.val x) = x) := by
  obtain ⟨_, _, hc, hr⟩ := recover_inputs artifact entries i update coefficients r h
  obtain ⟨_, _, _, hp, _, _, _, hop, hl, hr'⟩ :=
    LocatedCompactEntry.recoverAt_sound artifact (payload (selected entries i).columns)
      (offset entries i) (selected entries i).key update coefficients r hr
  exact ⟨hc, hp, hop, hl, hr'⟩

/-- Restricted completeness derives its slice obligation from the checked whole layout. -/
theorem recover_complete {n : Nat} (artifact : ByteArray) (entries : List (Entry n))
    (i : Fin entries.length) (dictionary : Lean.Json) (c : Candidate n)
    (h : CheckedBinaryChart.check c = true)
    (hc : c.columns = columnFunction (selected entries i).columns)
    (hk : HexObjectLayout.checkKeys (fields entries) = true)
    (ha : artifact.data = (HexObjectLayout.encode (fields entries)).data)
    (hd : dictionaryColumns n dictionary (selected entries i).key = some (selected entries i).columns)
    (hp : ByteJsonGlobalCall.parseBytes artifact = .ok dictionary)
    (hf : ByteJsonGlobalCall.parseBytes (payload (selected entries i).columns) =
      .ok (StrictJsonValueBridge.reencode 2 (vectorValue (selected entries i).columns))) :
    recover n artifact entries i c.updateVector c.coefficients =
      some (⟨(selected entries i).columns, ⟨c, h⟩, fun j => congrFun hc j⟩ : CheckedEntry n) := by
  have hs := layout_checkBytes artifact entries i ha
  have hr := LocatedCompactEntry.recoverAt_complete artifact (offset entries i) dictionary
    (selected entries i).key (selected entries i).columns c h hc hd hs hp hf
  unfold recover
  rw [if_pos hk, if_pos ha, hr]
  simp only [if_pos rfl, if_true]

end CurrentMain.CheckedCompactObject
#print axioms CurrentMain.CheckedCompactObject.fields_split
#print axioms CurrentMain.CheckedCompactObject.layout_checkBytes
#print axioms CurrentMain.CheckedCompactObject.recover_inputs
#print axioms CurrentMain.CheckedCompactObject.recover_layout
#print axioms CurrentMain.CheckedCompactObject.recover_sound
#print axioms CurrentMain.CheckedCompactObject.recover_complete
#check @CurrentMain.CheckedCompactObject.recover_layout
#check @CurrentMain.CheckedCompactObject.recover_sound
