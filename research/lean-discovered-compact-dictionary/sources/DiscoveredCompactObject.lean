import QuoteTokenScan
import KeyOnlyCompactObject

/-!
Discover candidate keys from the original artifact bytes, decode each actual
quoted token with String.fromUTF8?, and execute the unchanged full compact-object
checker. No ordered keys or column values are executable inputs. Successful
candidate discovery alone is not accepted: all original parser, named-column,
key policy, complete layout, bounded index and restricted recovery checks run.

Completeness uses the proved full-layout quoted-region invariant. The remaining
token-to-key UTF-8 decoding equation is explicit, as are the actual installed
artifact/fragment parser equations. This is not general JSON tokenization or a
parser specification. No digest authentication, external file identity, runtime
extern refinement, selected census or paid physical execution is asserted.
Author-checked context kappa=836330098538459/500000000000000000
=0.001672660197076918; generic statements do not use or change kappa.
Credits: Lean/Mathlib and accepted bank/frame strict codec, byte layout and
restricted recovery components; Jeremy Kothe T16/PR514 and Rohan Arun PR1094.
James Chang with OpenAI assistance, Apache-2.0. Uncompiled source preparation.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.DiscoveredCompactObject
open CheckedBinaryChart (Address Candidate)
open JsonPackedColumnDictionary (CheckedEntry dictionaryColumns columnOperator)
open ParsedBinaryChartCertificate (columnFunction vectorValue)
open CheckedCompactObject (Entry selected fields)
open CompactNatColumnFragment (payload)

def decodeKeys (tokens : List (List UInt8)) : Option (List String) :=
  tokens.mapM (fun token => String.fromUTF8? ⟨token.toArray⟩)

/-- Candidates are always subjected to the existing complete actual-byte checks. -/
def recover (n : Nat) (artifact : ByteArray) (position : Nat)
    (update coefficients : Address n) : Option (CheckedEntry n) :=
  match QuoteTokenScan.scan artifact.data.toList with
  | none => none
  | some tokens =>
      match decodeKeys tokens with
      | none => none
      | some keys => KeyOnlyCompactObject.recover n artifact keys position update coefficients

theorem recover_inputs {n : Nat} (artifact : ByteArray) (position : Nat)
    (update coefficients : Address n) (r : CheckedEntry n)
    (h : recover n artifact position update coefficients = some r) :
    ∃ tokens keys,
      QuoteTokenScan.scan artifact.data.toList = some tokens ∧
      QuoteTokenScan.Regions artifact.data.toList tokens ∧
      decodeKeys tokens = some keys ∧
      KeyOnlyCompactObject.recover n artifact keys position update coefficients = some r := by
  cases hs : QuoteTokenScan.scan artifact.data.toList with
  | none => simp only [recover, hs] at h; cases h
  | some tokens =>
      cases hd : decodeKeys tokens with
      | none => simp only [recover, hs, hd] at h; cases h
      | some keys =>
          refine ⟨tokens, keys, by simp only [hs], QuoteTokenScan.scan_sound _ _ hs,
            by simp only [hd], ?_⟩
          simpa only [recover, hs, hd] using h

/-- Actual original-byte success determines all discovered keys, all named fields,
complete layout equality and the independent operator with both inverse directions. -/
theorem recover_sound {n : Nat} (artifact : ByteArray) (position : Nat)
    (update coefficients : Address n) (r : CheckedEntry n)
    (h : recover n artifact position update coefficients = some r) :
    (∃ (tokens : List (List UInt8)) (keys : List String)
        (text : String) (dictionary : Lean.Json) (entries : List (Entry n))
        (hi : position < entries.length),
      QuoteTokenScan.Regions artifact.data.toList tokens ∧ decodeKeys tokens = some keys ∧
      String.fromUTF8? artifact = some text ∧ Lean.Json.parse text = .ok dictionary ∧
      entries.map Entry.key = keys ∧ position < keys.length ∧
      (∀ entry ∈ entries, ∃ raw : Lean.Json,
        dictionary.getObjVal? entry.key = .ok raw ∧
        StrictJsonValueBridge.reencode 2 (vectorValue entry.columns) = raw ∧
        ∀ j, columnFunction entry.columns j < 2 ^ n) ∧
      HexObjectLayout.checkKeys (fields entries) = true ∧
      artifact.data = (HexObjectLayout.encode (fields entries)).data ∧
      r.columns = (selected entries ⟨position, hi⟩).columns ∧
      KeyOnlyCompactObject.recover n artifact keys position update coefficients = some r) ∧
    columnOperator r.columns =
      (CheckedBinaryChart.checkedEquiv r.certificate.val r.certificate.property).toLinearMap ∧
    (∀ x, CheckedBinaryChart.inverseAddress r.certificate.val (columnOperator r.columns x) = x) ∧
    (∀ x, columnOperator r.columns (CheckedBinaryChart.inverseAddress r.certificate.val x) = x) := by
  obtain ⟨tokens, keys, _, hregions, hd, hr⟩ := recover_inputs artifact position update coefficients r h
  obtain ⟨⟨text, dictionary, entries, hi, hu, hj, hk, hb, hf, hv, ha, hc, _⟩,
    hop, hl, hr'⟩ := KeyOnlyCompactObject.recover_sound artifact keys position update coefficients r hr
  exact ⟨⟨tokens, keys, text, dictionary, entries, hi, hregions, hd, hu, hj, hk, hb,
    hf, hv, ha, hc, hr⟩, hop, hl, hr'⟩

/-- The full layout supplies its actual key-byte candidates without a scan-success premise. -/
theorem scan_entries {n : Nat} (artifact : ByteArray) (entries : List (Entry n))
    (hk : HexObjectLayout.checkKeys (fields entries) = true)
    (ha : artifact.data = (HexObjectLayout.encode (fields entries)).data) :
    QuoteTokenScan.scan artifact.data.toList =
      some (entries.map (fun e => HexObjectLayout.keyBytes e.key)) := by
  have hp : ∀ f ∈ fields entries, (34 : UInt8) ∉ f.payload.data.toList := by
    intro f hf
    obtain ⟨entry, _, he⟩ := List.mem_map.mp hf
    rw [← he]
    exact QuoteTokenScan.payload_quote_free entry.columns
  have hs := QuoteTokenScan.scan_layout (fields entries) hk hp
  simpa only [ha, fields, List.map_map, CheckedCompactObject.toField] using hs

/-- Restricted completeness retains actual UTF-8 key decoding and parser equations;
all quote-token discovery and complete layout checks are derived. -/
theorem recover_complete {n : Nat} (artifact : ByteArray) (dictionary : Lean.Json)
    (entries : List (Entry n)) (i : Fin entries.length) (c : Candidate n)
    (h : CheckedBinaryChart.check c = true)
    (hc : c.columns = columnFunction (selected entries i).columns)
    (hfields : ∀ entry ∈ entries, dictionaryColumns n dictionary entry.key = some entry.columns)
    (hk : HexObjectLayout.checkKeys (fields entries) = true)
    (ha : artifact.data = (HexObjectLayout.encode (fields entries)).data)
    (hkeys : decodeKeys (entries.map (fun e => HexObjectLayout.keyBytes e.key)) =
      some (entries.map Entry.key))
    (hp : ByteJsonGlobalCall.parseBytes artifact = .ok dictionary)
    (hf : ByteJsonGlobalCall.parseBytes (payload (selected entries i).columns) =
      .ok (StrictJsonValueBridge.reencode 2 (vectorValue (selected entries i).columns))) :
    recover n artifact i.val c.updateVector c.coefficients =
      some (⟨(selected entries i).columns, ⟨c, h⟩, fun j => congrFun hc j⟩ : CheckedEntry n) := by
  have hs := scan_entries artifact entries hk ha
  have hr := KeyOnlyCompactObject.recover_complete artifact dictionary entries i c h hc hfields hk ha hp hf
  simpa only [recover, hs, hkeys] using hr

end CurrentMain.DiscoveredCompactObject
#print axioms CurrentMain.DiscoveredCompactObject.recover_inputs
#print axioms CurrentMain.DiscoveredCompactObject.recover_sound
#print axioms CurrentMain.DiscoveredCompactObject.scan_entries
#print axioms CurrentMain.DiscoveredCompactObject.recover_complete
#check @CurrentMain.DiscoveredCompactObject.recover_sound
#check @CurrentMain.DiscoveredCompactObject.recover_complete
