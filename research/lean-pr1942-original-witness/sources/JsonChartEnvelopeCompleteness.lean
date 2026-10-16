import JsonChartWitnessEnvelope
import BoundedChartWitnessCompleteness

/-!
A direct completeness join for the original PR1942 five-array witness envelope.
The original bounded tables, packed columns and bit vectors are retained.
The existing permutation and scalar checks, together with exact named-field
AST equations, derive the actual wrapper execution. Downstream certifyEntry
success is no longer an input premise; the accepted original-Witness theorem
supplies it without reimplementing any checker.

This is a generic AST-level result, including dimension zero. The named-field
and finite-check premises remain explicit. It does not assert actual selected
file parsing, chart census coverage, lexical or duplicate-key policy, digest
authentication, physical execution, complex phase or paid cost. In particular,
no logical equation for the opaque Lean.Json.parse implementation is assumed
or proved here. Author-checked context only:
kappa=836330098538459/500000000000000000=0.001672660197076918.
Credits: Adam Gall with OpenAI assistance for the PR1942 witness envelope;
Rohan Arun PR1094; Jeremy Kothe T16/PR514; accepted bank/frame checker and
original-Witness proofs; Lean/Mathlib. James Chang with OpenAI assistance;
Apache-2.0.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.JsonChartEnvelopeCompleteness
open ParsedBinaryChartCertificate (Witness witnessValue vectorValue)
open BoundedChartWitnessCompleteness (candidate entry)

/-- Original witness checks and exact named fields derive full envelope success. -/
theorem certify_original_witness {n : Nat} (w : Witness n)
    (ht : CheckedPermutationTables.check w.permutation = true)
    (hc : CheckedBinaryChart.check (candidate w ht) = true)
    (dictionary witnesses entries : Lean.Json) (key : String)
    (hf : witnesses.getObjVal? "format" =
      .ok (.str JsonChartWitnessEnvelope.formatTag))
    (hd : witnesses.getObjVal? "dimension" = .ok (.num ⟨(n : Int), 0⟩))
    (he : witnesses.getObjVal? "entries" = .ok entries)
    (hk : entries.getObjVal? key = .ok
      (StrictJsonValueBridge.reencode 3 (witnessValue w)))
    (hfield : dictionary.getObjVal? key = .ok
      (StrictJsonValueBridge.reencode 2 (vectorValue w.columns))) :
    JsonChartWitnessEnvelope.certify n dictionary witnesses key =
      some (entry w ht hc) := by
  exact JsonChartWitnessEnvelope.certify_complete dictionary witnesses entries
    (StrictJsonValueBridge.reencode 3 (witnessValue w)) key (entry w ht hc)
    hf hd he hk
    (BoundedChartWitnessCompleteness.certify_entry_witness w ht hc dictionary key hfield)

end CurrentMain.JsonChartEnvelopeCompleteness
#print axioms CurrentMain.JsonChartEnvelopeCompleteness.certify_original_witness
#check @CurrentMain.JsonChartEnvelopeCompleteness.certify_original_witness
