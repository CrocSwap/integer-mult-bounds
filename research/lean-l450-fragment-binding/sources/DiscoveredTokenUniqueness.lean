import DiscoveredCompactObject

/-!
Successful actual-byte recovery determines the complete ordered quote-token list
and makes it duplicate-free. The proof compares the actual scanner result with
the proved scan of the checked complete restricted layout, then uses checked
serialized-key uniqueness. No scanner, parser or checker is changed.

This concerns the original byte scanner and the accepted hex-key/compact-Nat
serializer. It does not identify an internal Lean.Json parser trace or assert a
general JSON duplicate-key policy. External artifact identity, authentication,
parser specification and paid physical access remain separate.
Author-checked context kappa=836330098538459/500000000000000000
=0.001672660197076918; generic statements do not use or change kappa.
Credits: Lean/Mathlib; accepted bank/frame scanner and complete-layout checker;
Rohan Arun PR1094, Jeremy Kothe T16/PR514. James Chang with OpenAI assistance.
Apache-2.0. Source preparation; native acceptance recorded separately.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.DiscoveredTokenUniqueness
open CheckedBinaryChart (Address)
open JsonPackedColumnDictionary (CheckedEntry)
open CheckedCompactObject (Entry fields)

/-- Actual recovery supplies every original quote token, aligned with the same
complete checked layout and distinct as serialized byte lists. -/
theorem recover_tokens {n : Nat} (artifact : ByteArray) (position : Nat)
    (update coefficients : Address n) (r : CheckedEntry n)
    (h : DiscoveredCompactObject.recover n artifact position update coefficients = some r) :
    ∃ (tokens : List (List UInt8)) (entries : List (Entry n)),
      QuoteTokenScan.scan artifact.data.toList = some tokens ∧
      QuoteTokenScan.Regions artifact.data.toList tokens ∧
      tokens = entries.map (fun e => HexObjectLayout.keyBytes e.key) ∧
      tokens.Nodup ∧
      HexObjectLayout.checkKeys (fields entries) = true ∧
      artifact.data = (HexObjectLayout.encode (fields entries)).data := by
  obtain ⟨⟨tokens, keys, text, dictionary, entries, hi, hregions, hd, hu, hj,
    hkeys, hbound, hfields, hcheck, hartifact, hcolumns, hrun⟩, hop, hl, hr⟩ :=
    DiscoveredCompactObject.recover_sound artifact position update coefficients r h
  have hs := QuoteTokenScan.scan_complete hregions
  have he : tokens = entries.map (fun e => HexObjectLayout.keyBytes e.key) :=
    Option.some.inj (hs.symm.trans
      (DiscoveredCompactObject.scan_entries artifact entries hcheck hartifact))
  have hn : (entries.map (fun e => HexObjectLayout.keyBytes e.key)).Nodup := by
    simpa only [fields, List.map_map, CheckedCompactObject.toField] using
      ((HexObjectLayout.checkKeys_iff (fields entries)).mp hcheck).2
  exact ⟨tokens, entries, hs, hregions, he, he.symm ▸ hn, hcheck, hartifact⟩

/-- Any actual scan result of the successfully recovered artifact is duplicate-free. -/
theorem scan_nodup_of_recovery {n : Nat} (artifact : ByteArray) (position : Nat)
    (update coefficients : Address n) (r : CheckedEntry n)
    (h : DiscoveredCompactObject.recover n artifact position update coefficients = some r)
    (tokens : List (List UInt8))
    (hs : QuoteTokenScan.scan artifact.data.toList = some tokens) : tokens.Nodup := by
  obtain ⟨actual, entries, ha, hregions, he, hn, hcheck, hartifact⟩ :=
    recover_tokens artifact position update coefficients r h
  have ht : actual = tokens := Option.some.inj (ha.symm.trans hs)
  exact ht ▸ hn

end CurrentMain.DiscoveredTokenUniqueness
#print axioms CurrentMain.DiscoveredTokenUniqueness.recover_tokens
#print axioms CurrentMain.DiscoveredTokenUniqueness.scan_nodup_of_recovery
#check @CurrentMain.DiscoveredTokenUniqueness.recover_tokens
#check @CurrentMain.DiscoveredTokenUniqueness.scan_nodup_of_recovery
