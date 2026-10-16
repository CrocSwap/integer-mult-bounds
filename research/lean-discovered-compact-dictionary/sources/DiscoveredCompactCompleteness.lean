import DiscoveredCompactObject
import HexKeyUtf8RoundTrip

/-!
The executed complete-layout key policy discharges the remaining token-decoding
premise of the discovered-key checker. This is a proof-only composition: no
scanner, parser, recovery function, literal table or byte representation changes.
Actual installed artifact/fragment parser equations and the restricted checked
chart remain explicit in completeness. Runtime extern refinement, external
artifact/digest authentication, selected-file success, physical execution and
costs remain separate.
Author-checked context kappa=836330098538459/500000000000000000
=0.001672660197076918; generic statements do not use or change kappa.
Credits: Lean/Mathlib, accepted bank/frame hex/ASCII/scanner/recovery components;
Jeremy Kothe T16/PR514 and Rohan Arun PR1094. James Chang with OpenAI assistance.
Apache-2.0. Source preparation; actual dependency acceptance remains separate.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.DiscoveredCompactCompleteness
open CheckedBinaryChart (Candidate)
open JsonPackedColumnDictionary (CheckedEntry dictionaryColumns)
open ParsedBinaryChartCertificate (columnFunction vectorValue)
open CheckedCompactObject (Entry selected fields)
open CompactNatColumnFragment (payload)

/-- Every actual serialized token is decoded to its original checked key, in order. -/
theorem decode_entries {n : Nat} (entries : List (Entry n))
    (hk : HexObjectLayout.checkKeys (fields entries) = true) :
    DiscoveredCompactObject.decodeKeys (entries.map (fun e => HexObjectLayout.keyBytes e.key)) =
      some (entries.map Entry.key) := by
  have hpolicy : ∀ key ∈ entries.map Entry.key, HexObjectLayout.keyPolicy key = true := by
    intro key hm
    obtain ⟨entry, he, hkey⟩ := List.mem_map.mp hm
    rw [← hkey]
    have hfield : CheckedCompactObject.toField entry ∈ fields entries :=
      List.mem_map.mpr ⟨entry, he, rfl⟩
    exact ((HexObjectLayout.checkKeys_iff (fields entries)).mp hk).1 _ hfield
  have h := HexKeyUtf8RoundTrip.hex_tokens_roundtrip (entries.map Entry.key) hpolicy
  simpa only [DiscoveredCompactObject.decodeKeys, List.map_map, List.mapM_map,
    Function.comp_def] using h

/-- The original checker is complete for a full checked restricted layout without
any supplied key order, column data or additional token-decoding success premise. -/
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
    DiscoveredCompactObject.recover n artifact i.val c.updateVector c.coefficients =
      some (⟨(selected entries i).columns, ⟨c, h⟩, fun j => congrFun hc j⟩ : CheckedEntry n) := by
  exact DiscoveredCompactObject.recover_complete artifact dictionary entries i c h hc
    hfields hk ha (decode_entries entries hk) hp hf

end CurrentMain.DiscoveredCompactCompleteness
#print axioms CurrentMain.DiscoveredCompactCompleteness.decode_entries
#print axioms CurrentMain.DiscoveredCompactCompleteness.recover_complete
#check @CurrentMain.DiscoveredCompactCompleteness.recover_complete
