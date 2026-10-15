import TotalCompactColumnDecoder
import Current1094L450FragmentBinding

/-!
Thin application of the generic total compact-column decoder to the accepted
original907-byte L450 fragment. The prior literal-to-payload equality is reused;
no source literal, numeric decision, runtime diagnostic or scalar census is
repeated. The new strict decoder succeeds without a logical Json.parse premise.
This does not prove the old installed-parser validation equation. External
artifact origin/authentication and named whole-file field identity remain the
separate source correspondence boundary recorded by the imported binding.
Author-checked context: kappa=836330098538459/500000000000000000
=0.001672660197076918; no multiplication or new exponent claim.
Credits: Jeremy Kothe T16 compact sigma artifact; Rohan Arun PR1094; accepted
bank/frame source and byte binding. James Chang with OpenAI assistance.
Apache-2.0. Generic predecessor acceptance is required before this application.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.Current1094L450TotalDecoder
open Current1094L450FragmentDiagnostic (originalFragment)
open Current1094L450RecoveredEntry (columns)

/-- Every original ordered column is logically recovered by the new total path. -/
theorem decode_original :
    TotalCompactColumnDecoder.decodePacked 73 originalFragment = some columns :=
  (TotalCompactColumnDecoder.decodePacked_eq_some_iff originalFragment columns).mpr
    Current1094L450FragmentBinding.literal_eq_payload

/-- The independently interpreted Nat list is the same accepted ordered source list. -/
theorem decode_original_values :
    TotalCompactColumnDecoder.decodeNatArray originalFragment =
      some Current1094L450FragmentData.values := by
  apply (TotalCompactColumnDecoder.decodeNatArray_eq_some_iff _ _).mpr
  rw [Current1094L450FragmentBinding.literal_eq_payload]
  unfold CompactNatColumnFragment.payload
  rw [Current1094L450FragmentData.typed_values]

end CurrentMain.Current1094L450TotalDecoder
#print axioms CurrentMain.Current1094L450TotalDecoder.decode_original
#print axioms CurrentMain.Current1094L450TotalDecoder.decode_original_values
#check CurrentMain.Current1094L450TotalDecoder.decode_original
#check CurrentMain.Current1094L450TotalDecoder.decode_original_values
