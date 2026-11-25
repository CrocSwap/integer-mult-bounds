import CheckedCompactObject

/-!
An ordered key-only witness for the complete compact column dictionary layout.
The executable input contains original artifact bytes, a list of String keys,
a natural selected index and the binary update/coefficient functions. Every
column vector is obtained by strict named-field decoding of the dictionary
actually parsed from those same bytes. No column data is supplied by the caller.

The complete derived field list is passed to the accepted whole-layout checker,
which verifies actual serialized key validity/uniqueness and full artifact byte
coverage, computes the selected offset, and retains actual recovery and full
selected-column comparison. This module exposes original parser equations,
all ordered named-field decoding facts and the independent operator/inverses.

The key order is still an explicit checked witness. The verified restricted
serialization position is distinct from installed-parser internal source-span
correspondence. No general parser/serializer theorem, pre-collapse trace proof,
file/digest authentication, selected census, complex phase, physical execution
or runtime-cost theorem is supplied. Completeness retains actual parser and
restricted checked-Candidate conditions; it assumes no target operator equality.
Author-checked context: kappa=836330098538459/500000000000000000
=0.001672660197076918; generic results do not use or change kappa.
Credits: Lean/Mathlib, Jeremy Kothe T16/PR514, Rohan Arun PR1094, and accepted
bank/frame strict columns, byte parser, layout and recovery components.
James Chang with OpenAI assistance; Apache-2.0. Uncompiled source preparation.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.KeyOnlyCompactObject
open CheckedBinaryChart (Address Candidate)
open JsonPackedColumnDictionary (Columns CheckedEntry dictionaryColumns columnOperator)
open ParsedBinaryChartCertificate (columnFunction vectorValue)
open CheckedCompactObject (Entry selected fields)
open CompactNatColumnFragment (payload)

def decodeField (n : Nat) (dictionary : Lean.Json) (key : String) : Option (Entry n) :=
  match dictionaryColumns n dictionary key with
  | none => none
  | some cols => some ⟨key, cols⟩

def decodeFields (n : Nat) (dictionary : Lean.Json) (keys : List String) :
    Option (List (Entry n)) := keys.mapM (decodeField n dictionary)

private theorem decodeField_sound {n : Nat} (dictionary : Lean.Json) (key : String)
    (entry : Entry n) (h : decodeField n dictionary key = some entry) :
    entry.key = key ∧ dictionaryColumns n dictionary entry.key = some entry.columns := by
  cases hd : dictionaryColumns n dictionary key with
  | none =>
      simp only [decodeField, hd] at h
      cases h
  | some cols =>
      have he : entry = (⟨key, cols⟩ : Entry n) :=
        (Option.some.inj (by simpa only [decodeField, hd] using h)).symm
      rw [he]
      exact ⟨rfl, hd⟩

/-- Every output field has its actual named value and retains the complete original key order. -/
theorem decodeFields_sound {n : Nat} (dictionary : Lean.Json) (keys : List String)
    (entries : List (Entry n)) (h : decodeFields n dictionary keys = some entries) :
    entries.map Entry.key = keys ∧
      ∀ entry ∈ entries, dictionaryColumns n dictionary entry.key = some entry.columns := by
  induction keys generalizing entries with
  | nil =>
      have he : ([] : List (Entry n)) = entries := Option.some.inj
        (by simpa only [decodeFields, List.mapM_nil] using h)
      rw [← he]
      exact ⟨rfl, by intro entry hm; cases hm⟩
  | cons key keys ih =>
      change (key :: keys).mapM (decodeField n dictionary) = some entries at h
      rw [List.mapM_cons] at h
      change (decodeField n dictionary key >>= fun entry =>
        keys.mapM (decodeField n dictionary) >>= fun rest => some (entry :: rest)) = some entries at h
      obtain ⟨entry, he, ht⟩ := Option.bind_eq_some_iff.mp h
      obtain ⟨rest, hr, hs⟩ := Option.bind_eq_some_iff.mp ht
      have hall : entry :: rest = entries := Option.some.inj hs
      obtain ⟨hk, hd⟩ := decodeField_sound dictionary key entry he
      obtain ⟨hkeys, hrest⟩ := ih rest hr
      rw [← hall]
      constructor
      · simp only [List.map_cons, hk, hkeys]
      · intro x hx
        rcases List.mem_cons.mp hx with hx | hx
        · rw [hx]
          exact hd
        · exact hrest x hx

/-- Actual per-field decode equations suffice to reconstruct the ordered witness. -/
theorem decodeFields_complete {n : Nat} (dictionary : Lean.Json) (entries : List (Entry n))
    (h : ∀ entry ∈ entries, dictionaryColumns n dictionary entry.key = some entry.columns) :
    decodeFields n dictionary (entries.map Entry.key) = some entries := by
  induction entries with
  | nil => rfl
  | cons entry rest ih =>
      have hd := h entry (List.mem_cons_self)
      have ht := ih (fun x hx => h x (List.mem_cons_of_mem entry hx))
      have he : decodeField n dictionary entry.key = some entry := by
        unfold decodeField
        rw [hd]
      change ((entry :: rest).map Entry.key).mapM (decodeField n dictionary) = some (entry :: rest)
      simp only [List.map_cons, List.mapM_cons, he]
      change (decodeFields n dictionary (rest.map Entry.key) >>= fun tail => some (entry :: tail)) = _
      rw [ht]
      rfl

/-- Parse the original artifact and derive all columns before checking the complete layout. -/
def recover (n : Nat) (artifact : ByteArray) (keys : List String) (position : Nat)
    (update coefficients : Address n) : Option (CheckedEntry n) :=
  match ByteJsonGlobalCall.parseBytes artifact with
  | .error _ => none
  | .ok dictionary =>
      match decodeFields n dictionary keys with
      | none => none
      | some entries =>
          if hi : position < entries.length then
            CheckedCompactObject.recover n artifact entries ⟨position, hi⟩ update coefficients
          else none

theorem recover_inputs {n : Nat} (artifact : ByteArray) (keys : List String) (position : Nat)
    (update coefficients : Address n) (r : CheckedEntry n)
    (h : recover n artifact keys position update coefficients = some r) :
    ∃ (dictionary : Lean.Json) (entries : List (Entry n)) (hi : position < entries.length),
      ByteJsonGlobalCall.parseBytes artifact = .ok dictionary ∧
      decodeFields n dictionary keys = some entries ∧
      CheckedCompactObject.recover n artifact entries ⟨position, hi⟩ update coefficients = some r := by
  cases hp : ByteJsonGlobalCall.parseBytes artifact with
  | error error =>
      simp only [recover, hp] at h
      cases h
  | ok dictionary =>
      cases hd : decodeFields n dictionary keys with
      | none =>
          simp only [recover, hp, hd] at h
          cases h
      | some entries =>
          by_cases hi : position < entries.length
          · refine ⟨dictionary, entries, hi, by simp only [hp], by simp only [hd], ?_⟩
            simpa only [recover, hp, hd, dif_pos hi] using h
          · simp only [recover, hp, hd, dif_neg hi] at h
            cases h

/-- All witness values come from the original parsed dictionary. Full byte coverage,
selected columns and the independent operator/inverses derive from actual execution. -/
theorem recover_sound {n : Nat} (artifact : ByteArray) (keys : List String) (position : Nat)
    (update coefficients : Address n) (r : CheckedEntry n)
    (h : recover n artifact keys position update coefficients = some r) :
    (∃ (text : String) (dictionary : Lean.Json) (entries : List (Entry n))
        (hi : position < entries.length),
      String.fromUTF8? artifact = some text ∧ Lean.Json.parse text = .ok dictionary ∧
      entries.map Entry.key = keys ∧ position < keys.length ∧
      (∀ entry ∈ entries, ∃ raw : Lean.Json,
        dictionary.getObjVal? entry.key = .ok raw ∧
        StrictJsonValueBridge.reencode 2 (vectorValue entry.columns) = raw ∧
        ∀ j, columnFunction entry.columns j < 2 ^ n) ∧
      HexObjectLayout.checkKeys (fields entries) = true ∧
      artifact.data = (HexObjectLayout.encode (fields entries)).data ∧
      r.columns = (selected entries ⟨position, hi⟩).columns ∧
      CheckedCompactObject.recover n artifact entries ⟨position, hi⟩ update coefficients = some r) ∧
    columnOperator r.columns =
      (CheckedBinaryChart.checkedEquiv r.certificate.val r.certificate.property).toLinearMap ∧
    (∀ x, CheckedBinaryChart.inverseAddress r.certificate.val (columnOperator r.columns x) = x) ∧
    (∀ x, columnOperator r.columns (CheckedBinaryChart.inverseAddress r.certificate.val x) = x) := by
  obtain ⟨dictionary, entries, hi, hp, hd, hr⟩ := recover_inputs artifact keys position update coefficients r h
  obtain ⟨text, hu, hj⟩ := ByteJsonGlobalCall.parseBytes_sound artifact dictionary hp
  obtain ⟨hkeys, hfields⟩ := decodeFields_sound dictionary keys entries hd
  have hlength : entries.length = keys.length := by
    simpa only [List.length_map] using congrArg List.length hkeys
  have hkbound : position < keys.length := hlength ▸ hi
  obtain ⟨hvalid, hbytes, hcols, _⟩ :=
    CheckedCompactObject.recover_inputs artifact entries ⟨position, hi⟩ update coefficients r hr
  obtain ⟨_, _, hop, hl, hr'⟩ :=
    CheckedCompactObject.recover_sound artifact entries ⟨position, hi⟩ update coefficients r hr
  refine ⟨⟨text, dictionary, entries, hi, hu, hj, hkeys, hkbound, ?_, hvalid, hbytes, hcols, hr⟩,
    hop, hl, hr'⟩
  intro entry hm
  exact JsonPackedColumnDictionary.dictionaryColumns_sound dictionary entry.key entry.columns
    (hfields entry hm)

/-- Restricted completeness decodes all values internally; no column list is an executable input. -/
theorem recover_complete {n : Nat} (artifact : ByteArray) (dictionary : Lean.Json)
    (entries : List (Entry n)) (i : Fin entries.length) (c : Candidate n)
    (h : CheckedBinaryChart.check c = true)
    (hc : c.columns = columnFunction (selected entries i).columns)
    (hfields : ∀ entry ∈ entries, dictionaryColumns n dictionary entry.key = some entry.columns)
    (hk : HexObjectLayout.checkKeys (fields entries) = true)
    (ha : artifact.data = (HexObjectLayout.encode (fields entries)).data)
    (hp : ByteJsonGlobalCall.parseBytes artifact = .ok dictionary)
    (hf : ByteJsonGlobalCall.parseBytes (payload (selected entries i).columns) =
      .ok (StrictJsonValueBridge.reencode 2 (vectorValue (selected entries i).columns))) :
    recover n artifact (entries.map Entry.key) i.val c.updateVector c.coefficients =
      some (⟨(selected entries i).columns, ⟨c, h⟩, fun j => congrFun hc j⟩ : CheckedEntry n) := by
  have hd := decodeFields_complete dictionary entries hfields
  have hs : selected entries i ∈ entries := List.getElem_mem i.isLt
  have hr := CheckedCompactObject.recover_complete artifact entries i dictionary c h hc hk ha
    (hfields (selected entries i) hs) hp hf
  simpa only [recover, hp, hd, dif_pos i.isLt] using hr

end CurrentMain.KeyOnlyCompactObject
#print axioms CurrentMain.KeyOnlyCompactObject.decodeFields_sound
#print axioms CurrentMain.KeyOnlyCompactObject.decodeFields_complete
#print axioms CurrentMain.KeyOnlyCompactObject.recover_inputs
#print axioms CurrentMain.KeyOnlyCompactObject.recover_sound
#print axioms CurrentMain.KeyOnlyCompactObject.recover_complete
#check @CurrentMain.KeyOnlyCompactObject.recover_sound
#check @CurrentMain.KeyOnlyCompactObject.recover_complete
