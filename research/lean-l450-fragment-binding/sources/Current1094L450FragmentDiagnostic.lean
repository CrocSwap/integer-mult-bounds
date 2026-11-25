import CompactNatColumnFragment
import Current1094L450ParsedCertificate

/-!
One executable diagnostic on the exact retained selected L450 907-byte fragment.
The UInt8 literal is mechanically byte-bound to the original decompressed member
slice; it is not reconstructed from a proposed parser output. The accepted
validator executes original UTF-8/JSON parsing, strict ordered73-column decoding
and exact canonical byte equality. We then compare all columns to the unchanged
accepted L450 definition and execute the existing scalar chart check on those
actual parsed columns with the accepted factorization fields.

The printed runtime PASS is execution evidence only, not a kernel proof of a
logical Json.parse equation or native/extern refinement. No whole dictionary,
gzip decoder, file/digest authentication, parser span, full-phase operator,
physical executor or cost claim is made. No accepted source is rebuilt.
Source-matched context: kappa=836330098538459/500000000000000000
=0.001672660197076918. Rohan Arun PR1094; Jeremy Kothe T16/PR514;
accepted bank/frame columns/checker and Lean/Mathlib. James Chang with OpenAI
assistance. Apache-2.0.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.Current1094L450FragmentDiagnostic

def originalFragment : ByteArray := ⟨#[
    91, 51, 56, 54, 44, 52, 44, 56, 44, 49, 54, 44, 51, 50, 44, 54, 52, 44, 50, 53, 57, 44, 51, 56, 53, 44, 49, 51, 49, 44, 53, 49,
    50, 44, 49, 48, 50, 52, 44, 50, 48, 52, 56, 44, 52, 48, 57, 54, 44, 56, 49, 57, 50, 44, 49, 54, 51, 56, 52, 44, 51, 50, 55, 54,
    56, 44, 54, 53, 53, 51, 54, 44, 49, 51, 49, 48, 55, 50, 44, 50, 54, 50, 49, 52, 52, 44, 53, 50, 52, 50, 56, 56, 44, 49, 48, 52,
    56, 53, 55, 54, 44, 50, 48, 57, 55, 49, 53, 50, 44, 52, 49, 57, 52, 51, 48, 52, 44, 56, 51, 56, 56, 54, 48, 56, 44, 49, 54, 55,
    55, 55, 50, 49, 54, 44, 51, 51, 53, 53, 52, 52, 51, 50, 44, 54, 55, 49, 48, 56, 56, 54, 52, 44, 49, 51, 52, 50, 49, 55, 55, 50,
    56, 44, 50, 54, 56, 52, 51, 53, 52, 53, 54, 44, 53, 51, 54, 56, 55, 48, 57, 49, 50, 44, 49, 48, 55, 51, 55, 52, 49, 56, 50, 52,
    44, 50, 49, 52, 55, 52, 56, 51, 54, 52, 56, 44, 52, 50, 57, 52, 57, 54, 55, 50, 57, 54, 44, 56, 53, 56, 57, 57, 51, 52, 53, 57,
    50, 44, 49, 55, 49, 55, 57, 56, 54, 57, 49, 56, 52, 44, 51, 52, 51, 53, 57, 55, 51, 56, 51, 54, 56, 44, 54, 56, 55, 49, 57, 52,
    55, 54, 55, 51, 54, 44, 49, 51, 55, 52, 51, 56, 57, 53, 51, 52, 55, 50, 44, 50, 55, 52, 56, 55, 55, 57, 48, 54, 57, 52, 52, 44,
    53, 52, 57, 55, 53, 53, 56, 49, 51, 56, 56, 56, 44, 49, 48, 57, 57, 53, 49, 49, 54, 50, 55, 55, 55, 54, 44, 50, 49, 57, 57, 48,
    50, 51, 50, 53, 53, 53, 53, 50, 44, 52, 51, 57, 56, 48, 52, 54, 53, 49, 49, 49, 48, 52, 44, 56, 55, 57, 54, 48, 57, 51, 48, 50,
    50, 50, 48, 56, 44, 49, 55, 53, 57, 50, 49, 56, 54, 48, 52, 52, 52, 49, 54, 44, 51, 53, 49, 56, 52, 51, 55, 50, 48, 56, 56, 56,
    51, 50, 44, 55, 48, 51, 54, 56, 55, 52, 52, 49, 55, 55, 54, 54, 52, 44, 49, 52, 48, 55, 51, 55, 52, 56, 56, 51, 53, 53, 51, 50,
    56, 44, 50, 56, 49, 52, 55, 52, 57, 55, 54, 55, 49, 48, 54, 53, 54, 44, 53, 54, 50, 57, 52, 57, 57, 53, 51, 52, 50, 49, 51, 49,
    50, 44, 49, 49, 50, 53, 56, 57, 57, 57, 48, 54, 56, 52, 50, 54, 50, 52, 44, 50, 50, 53, 49, 55, 57, 57, 56, 49, 51, 54, 56, 53,
    50, 52, 56, 44, 52, 53, 48, 51, 53, 57, 57, 54, 50, 55, 51, 55, 48, 52, 57, 54, 44, 57, 48, 48, 55, 49, 57, 57, 50, 53, 52, 55,
    52, 48, 57, 57, 50, 44, 49, 56, 48, 49, 52, 51, 57, 56, 53, 48, 57, 52, 56, 49, 57, 56, 52, 44, 51, 54, 48, 50, 56, 55, 57, 55,
    48, 49, 56, 57, 54, 51, 57, 54, 56, 44, 55, 50, 48, 53, 55, 53, 57, 52, 48, 51, 55, 57, 50, 55, 57, 51, 54, 44, 49, 52, 52, 49,
    49, 53, 49, 56, 56, 48, 55, 53, 56, 53, 53, 56, 55, 50, 44, 50, 56, 56, 50, 51, 48, 51, 55, 54, 49, 53, 49, 55, 49, 49, 55, 52,
    52, 44, 53, 55, 54, 52, 54, 48, 55, 53, 50, 51, 48, 51, 52, 50, 51, 52, 56, 56, 44, 49, 49, 53, 50, 57, 50, 49, 53, 48, 52, 54,
    48, 54, 56, 52, 54, 57, 55, 54, 44, 50, 51, 48, 53, 56, 52, 51, 48, 48, 57, 50, 49, 51, 54, 57, 51, 57, 53, 50, 44, 52, 54, 49,
    49, 54, 56, 54, 48, 49, 56, 52, 50, 55, 51, 56, 55, 57, 48, 52, 44, 57, 50, 50, 51, 51, 55, 50, 48, 51, 54, 56, 53, 52, 55, 55,
    53, 56, 48, 56, 44, 49, 56, 52, 52, 54, 55, 52, 52, 48, 55, 51, 55, 48, 57, 53, 53, 49, 54, 49, 54, 44, 51, 54, 56, 57, 51, 52,
    56, 56, 49, 52, 55, 52, 49, 57, 49, 48, 51, 50, 51, 50, 44, 55, 51, 55, 56, 54, 57, 55, 54, 50, 57, 52, 56, 51, 56, 50, 48, 54,
    52, 54, 52, 44, 49, 52, 55, 53, 55, 51, 57, 53, 50, 53, 56, 57, 54, 55, 54, 52, 49, 50, 57, 50, 56, 44, 50, 57, 53, 49, 52, 55,
    57, 48, 53, 49, 55, 57, 51, 53, 50, 56, 50, 53, 56, 53, 54, 44, 53, 57, 48, 50, 57, 53, 56, 49, 48, 51, 53, 56, 55, 48, 53, 54,
    53, 49, 55, 49, 50, 44, 49, 49, 56, 48, 53, 57, 49, 54, 50, 48, 55, 49, 55, 52, 49, 49, 51, 48, 51, 52, 50, 52, 44, 50, 51, 54,
    49, 49, 56, 51, 50, 52, 49, 52, 51, 52, 56, 50, 50, 54, 48, 54, 56, 52, 56, 44, 52, 55, 50, 50, 51, 54, 54, 52, 56, 50, 56, 54,
    57, 54, 52, 53, 50, 49, 51, 54, 57, 54, 93]⟩

def runDiagnostic : IO Unit := do
  let some cols := CompactNatColumnFragment.validateFragment 73 originalFragment
    | throw (IO.userError "L450_FRAGMENT_VALIDATION_FAILED")
  let expected := List.ofFn Current1094L450ParsedCertificate.candidate.columns
  unless CompactNatColumnFragment.natValues cols == expected do
    throw (IO.userError "L450_COLUMN_SOURCE_MISMATCH")
  let parsedCandidate : CheckedBinaryChart.Candidate 73 :=
    { Current1094L450ParsedCertificate.candidate with
      columns := ParsedBinaryChartCertificate.columnFunction cols }
  unless CheckedBinaryChart.check parsedCandidate do
    throw (IO.userError "L450_PARSED_SCALAR_CERTIFICATE_FAILED")
  IO.println "EXECUTABLE_L450_FRAGMENT_PASS bytes=907 columns=73 exact_source_match=true scalar_certificate=true"

end CurrentMain.Current1094L450FragmentDiagnostic
#eval CurrentMain.Current1094L450FragmentDiagnostic.runDiagnostic
#print axioms CurrentMain.Current1094L450ParsedCertificate.candidate_check
#check CurrentMain.Current1094L450FragmentDiagnostic.runDiagnostic
