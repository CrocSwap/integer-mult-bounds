import TotalCompactProviderRecovery
import Current1094L450TotalDecoder

/-!
Source-matched application of the total original-byte recovery entrypoint.
The accepted original907-byte identity, old candidate_check and columns_match
supply generic completeness. No new data, finite decision, scalar census or
runtime replay occurs. Both full-address inverse equations refer to the old
independent selected source operator. The opaque JSON parser is unused here;
whole-artifact named-field identity and producer authentication remain external
source boundaries. No complex phase, physical execution or cost claim follows.
Author-checked context: kappa=836330098538459/500000000000000000
=0.001672660197076918. Credits: accepted bank/frame source, byte and recovery
proofs; Jeremy Kothe T16; Rohan Arun PR1094; Lean/Mathlib. James Chang with
OpenAI assistance. Apache-2.0. Independent acceptance is separate.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.Current1094L450TotalRecovery
open Current1094L450FragmentDiagnostic (originalFragment)
open Current1094L450RecoveredEntry (columns)
open Current1094L450ParsedCertificate (candidate candidate_check)

/-- Actual byte execution returns the original source columns and old certificate. -/
theorem recover_original :
    TotalCompactProviderRecovery.recover 73 originalFragment
      candidate.updateVector candidate.coefficients =
      some (columns, (⟨candidate, candidate_check⟩ : ParsedBinaryChartCertificate.Certified 73)) :=
  TotalCompactProviderRecovery.recover_complete originalFragment columns candidate candidate_check
    Current1094L450RecoveredEntry.columns_match
    Current1094L450FragmentBinding.literal_eq_payload

/-- The successful original-byte execution carries both inverse directions for
all addresses of the already accepted independent selected source operator. -/
theorem recovered_source_inverses :
    (∀ x, CheckedBinaryChart.inverseAddress candidate
      (Current1094L450OrderedChart.sourceLinear x) = x) ∧
    (∀ x, Current1094L450OrderedChart.sourceLinear
      (CheckedBinaryChart.inverseAddress candidate x) = x) := by
  have h := TotalCompactProviderRecovery.recover_sound originalFragment
    candidate.updateVector candidate.coefficients
    (columns, (⟨candidate, candidate_check⟩ : ParsedBinaryChartCertificate.Certified 73))
    recover_original
  have hinv := h.2.2.2.2.2
  simpa only [Current1094L450RecoveredEntry.source_operator] using hinv

end CurrentMain.Current1094L450TotalRecovery
#print axioms CurrentMain.Current1094L450TotalRecovery.recover_original
#print axioms CurrentMain.Current1094L450TotalRecovery.recovered_source_inverses
#check CurrentMain.Current1094L450TotalRecovery.recover_original
#check CurrentMain.Current1094L450TotalRecovery.recovered_source_inverses
