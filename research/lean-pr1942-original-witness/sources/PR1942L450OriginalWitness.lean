import JsonChartEnvelopeCompleteness
import Current1094L450FragmentData

/-!
A single original PR1942 witness application, source-bound to revision
c7d8c9febf0fcc52d2002db657165cd206ff9cec,
research/selected-sigma-chart-binding/WITNESSES.json.gz, original key below.
All five arrays have73 entries. The four small table/bit arrays below are
matched individually to the existing selected typed certificate. The73 packed
columns reuse the already accepted exact Nat list and typed-value theorem.
The original1,627-byte five-array value is preserved separately with its source
mapping; no replacement array or scalar census is silently substituted.

Four ordinary kernel decisions compare small ordered components only. The
existing candidate_check is transported through candidate equality; the new
envelope join derives success from exact original named-field AST equations.
Logical Json.parse success, external file/authentication, whole-witness coverage,
lexical or duplicate-key policy, physical execution, complex phases and costs
remain separate. No runtime verifier or full dictionary is executed here.
Author-checked context: kappa=836330098538459/500000000000000000
=0.001672660197076918. Credits: Adam Gall with OpenAI assistance, PR1942;
Rohan Arun PR1094; Jeremy Kothe T16/PR514; accepted bank/frame source and chart
proofs; Lean/Mathlib. James Chang with OpenAI assistance; Apache-2.0.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.PR1942L450OriginalWitness
open SelectedSourceSyntax (Value)
open ParsedBinaryChartCertificate (Witness witnessValue vectorValue)
open Current1094L450ParsedCertificate (candidate candidate_check)

def key : String := "ccf973ede5baca87618c361e2fe62bb8a80f11b79f1551237ab7a16c887b4e90"

def forwardValues : List Nat := [0, 2, 3, 4, 5, 6, 7, 1, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72]

def inverseValues : List Nat := [0, 7, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72]

def updateValues : List Nat := [1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

def coefficientValues : List Nat := [1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

def natArray (xs : List Nat) : Value :=
  .array (xs.map (fun n => .integer (n : Int)))

def originalValue : Value :=
  .array [natArray forwardValues, natArray inverseValues,
    natArray Current1094L450FragmentData.values,
    natArray updateValues, natArray coefficientValues]

def witness : Witness 73 :=
  ⟨BinaryChartCanonicalEncoding.permutationCertificate candidate.permutation,
    Current1094L450RecoveredEntry.columns,
    BinaryChartCanonicalEncoding.binaryVector candidate.updateVector,
    BinaryChartCanonicalEncoding.binaryVector candidate.coefficients⟩

private theorem encoded_list {b : Nat} (xs : List (Fin b)) :
    Value.array (xs.map StrictParsedIndexCodec.indexValue) = natArray (xs.map Fin.val) := by
  unfold natArray
  apply congrArg Value.array
  induction xs with
  | nil => rfl
  | cons x xs ih =>
      exact congrArg (List.cons (StrictParsedIndexCodec.indexValue x)) ih

private theorem forward_value :
    CheckedPermutationTables.tableValue witness.permutation.forward =
      natArray forwardValues := by
  have h : witness.permutation.forward.val.map Fin.val = forwardValues := by
    decide +kernel
  exact (encoded_list witness.permutation.forward.val).trans (congrArg natArray h)

private theorem inverse_value :
    CheckedPermutationTables.tableValue witness.permutation.backward =
      natArray inverseValues := by
  have h : witness.permutation.backward.val.map Fin.val = inverseValues := by
    decide +kernel
  exact (encoded_list witness.permutation.backward.val).trans (congrArg natArray h)

private theorem update_value : vectorValue witness.update = natArray updateValues := by
  have h : witness.update.val.map Fin.val = updateValues := by
    decide +kernel
  exact (encoded_list witness.update.val).trans (congrArg natArray h)

private theorem coefficient_value :
    vectorValue witness.coefficients = natArray coefficientValues := by
  have h : witness.coefficients.val.map Fin.val = coefficientValues := by
    decide +kernel
  exact (encoded_list witness.coefficients.val).trans (congrArg natArray h)

/-- Reuse the accepted typed-column-to-original-Nat-list equality. -/
theorem columns_value : vectorValue witness.columns =
    natArray Current1094L450FragmentData.values := by
  exact (encoded_list witness.columns.val).trans
    (congrArg natArray Current1094L450FragmentData.typed_values)

/-- Every original ordered component is retained, including the inverse table. -/
theorem witness_value : witnessValue witness = originalValue := by
  unfold witnessValue originalValue
  rw [forward_value, inverse_value, columns_value, update_value, coefficient_value]

theorem table_check : CheckedPermutationTables.check witness.permutation = true :=
  BinaryChartCanonicalEncoding.permutation_check candidate.permutation

/-- The original matched witness decodes to the existing selected Candidate. -/
theorem candidate_eq :
    BoundedChartWitnessCompleteness.candidate witness table_check = candidate := by
  have h := BoundedChartWitnessCompleteness.decode_witness witness table_check
  have hv : witnessValue witness =
      BinaryChartCanonicalEncoding.encodeCandidate candidate candidate_check := rfl
  rw [hv, BinaryChartCanonicalEncoding.decode_encodeCandidate candidate candidate_check] at h
  exact (Option.some.inj h).symm

/-- Transport the accepted structural scalar certificate; no new scalar census. -/
theorem scalar_check : CheckedBinaryChart.check
    (BoundedChartWitnessCompleteness.candidate witness table_check) = true := by
  rw [candidate_eq]
  exact candidate_check

/-- File/parser correspondence is retained as explicit original named fields. -/
theorem envelope_success (dictionary envelope entries : Lean.Json)
    (hf : envelope.getObjVal? "format" = .ok (.str JsonChartWitnessEnvelope.formatTag))
    (hd : envelope.getObjVal? "dimension" = .ok (.num ⟨73, 0⟩))
    (he : envelope.getObjVal? "entries" = .ok entries)
    (hk : entries.getObjVal? key = .ok (StrictJsonValueBridge.reencode 3 originalValue))
    (hfield : dictionary.getObjVal? key = .ok
      (StrictJsonValueBridge.reencode 2 (natArray Current1094L450FragmentData.values))) :
    JsonChartWitnessEnvelope.certify 73 dictionary envelope key =
      some (BoundedChartWitnessCompleteness.entry witness table_check scalar_check) := by
  apply JsonChartEnvelopeCompleteness.certify_original_witness witness table_check scalar_check
    dictionary envelope entries key hf hd he
  · simpa only [witness_value] using hk
  · simpa only [columns_value] using hfield

end CurrentMain.PR1942L450OriginalWitness
#print axioms CurrentMain.PR1942L450OriginalWitness.witness_value
#print axioms CurrentMain.PR1942L450OriginalWitness.table_check
#print axioms CurrentMain.PR1942L450OriginalWitness.candidate_eq
#print axioms CurrentMain.PR1942L450OriginalWitness.scalar_check
#print axioms CurrentMain.PR1942L450OriginalWitness.envelope_success
#check CurrentMain.PR1942L450OriginalWitness.witness_value
#check CurrentMain.PR1942L450OriginalWitness.envelope_success
