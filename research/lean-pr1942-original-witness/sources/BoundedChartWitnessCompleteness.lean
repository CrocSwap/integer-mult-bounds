import JsonPackedColumnDictionary

/-!
Completeness for an original bounded five-array chart witness. The input data
are the existing ordered forward/inverse tables, packed columns, update bits
and coefficient bits. Checked table round trips construct the permutation;
the independent scalar check supplies the restricted chart certificate.
Neither an externally supplied Equiv nor an operator equality is assumed.

Unlike canonical encoding of a preconstructed Candidate, this result keeps the
original Witness arrays and proves that the actual Value and Lean.Json paths
accept those arrays unchanged. A named dictionary application retains the exact
field equation and uses the unchanged provider decoder and column comparison.

Dimension zero and arbitrary finite dimensions are covered by the existing
bounded types. Bounds/lengths, table-check success, scalar-check success and the
named field equation remain explicit. This does not prove actual file parsing,
the PR1942 witness census, opaque Json.parse success, digest/key authentication,
complex phases, a physical executor or cost. Author-checked context only:
kappa=836330098538459/500000000000000000=0.001672660197076918.
Credits: Lean/Mathlib; accepted bank/frame strict parsed chart and dictionary
components; PR1942 five-array witness motivation; Rohan Arun PR1094 and Jeremy
Kothe T16/PR514 lineage. James Chang with OpenAI assistance; Apache-2.0.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.BoundedChartWitnessCompleteness
open ParsedBinaryChartCertificate (Witness Certified witnessValue vectorValue
  columnFunction binaryFunction)
open CheckedPermutationTables (Certificate tableValue checkedEquiv)

/-- The original two tables are decoded and checked; no inverse is recomputed. -/
theorem decodePermutation_tables {n : Nat} (t : Certificate n)
    (ht : CheckedPermutationTables.check t = true) :
    CheckedPermutationTables.decodePermutation n (tableValue t.forward)
      (tableValue t.backward) = some (checkedEquiv t ht) := by
  have hd : CheckedPermutationTables.decodeCertificate n (tableValue t.forward)
      (tableValue t.backward) = some t := by
    simp only [CheckedPermutationTables.decodeCertificate,
      CheckedPermutationTables.decodeTable_complete]
    all_goals rfl
  unfold CheckedPermutationTables.decodePermutation
  rw [hd]
  change (if h : CheckedPermutationTables.check t = true then
    some (checkedEquiv t h) else none) = some (checkedEquiv t ht)
  rw [dif_pos ht]

/-- Candidate fields are read directly from the bounded original witness. -/
def candidate {n : Nat} (w : Witness n)
    (ht : CheckedPermutationTables.check w.permutation = true) :
    CheckedBinaryChart.Candidate n :=
  .mk (columnFunction w.columns) (checkedEquiv w.permutation ht)
    (binaryFunction w.update) (binaryFunction w.coefficients)

theorem decode_witness {n : Nat} (w : Witness n)
    (ht : CheckedPermutationTables.check w.permutation = true) :
    ParsedBinaryChartCertificate.decode n (witnessValue w) =
      some (candidate w ht) := by
  change ParsedBinaryChartCertificate.decodeFields n
    ⟨tableValue w.permutation.forward, tableValue w.permutation.backward,
      vectorValue w.columns, vectorValue w.update, vectorValue w.coefficients⟩ =
    some (candidate w ht)
  unfold ParsedBinaryChartCertificate.decodeFields
  rw [decodePermutation_tables w.permutation ht,
    ParsedBinaryChartCertificate.decodeVector_complete w.columns,
    ParsedBinaryChartCertificate.decodeVector_complete w.update,
    ParsedBinaryChartCertificate.decodeVector_complete w.coefficients]
  all_goals rfl

theorem certify_witness {n : Nat} (w : Witness n)
    (ht : CheckedPermutationTables.check w.permutation = true)
    (hc : CheckedBinaryChart.check (candidate w ht) = true) :
    ParsedBinaryChartCertificate.certify n (witnessValue w) =
      some (⟨candidate w ht, hc⟩ : Certified n) := by
  unfold ParsedBinaryChartCertificate.certify
  rw [decode_witness w ht]
  change (if h : CheckedBinaryChart.check (candidate w ht) = true then
    some (⟨candidate w ht, h⟩ : Certified n) else none) =
      some (⟨candidate w ht, hc⟩ : Certified n)
  rw [dif_pos hc]

private theorem array_supported {b : Nat} (xs : List (Fin b)) :
    JsonBinaryChartInterpreter.SupportedAt 2
      (.array (xs.map StrictParsedIndexCodec.indexValue)) := by
  intro x hx
  obtain ⟨i, _, rfl⟩ := List.mem_map.mp hx
  trivial

theorem witness_supported {n : Nat} (w : Witness n) :
    JsonBinaryChartInterpreter.SupportedAt 3 (witnessValue w) := by
  change ∀ v ∈ [tableValue w.permutation.forward,
    tableValue w.permutation.backward, vectorValue w.columns,
    vectorValue w.update, vectorValue w.coefficients],
    JsonBinaryChartInterpreter.SupportedAt 2 v
  intro v hv
  simp only [List.mem_cons, List.mem_nil_iff, or_false] at hv
  rcases hv with rfl | rfl | rfl | rfl | rfl
  all_goals exact array_supported _

/-- The original five arrays, encoded as ASTs, are accepted at exact depth three. -/
theorem certify_json_witness {n : Nat} (w : Witness n)
    (ht : CheckedPermutationTables.check w.permutation = true)
    (hc : CheckedBinaryChart.check (candidate w ht) = true) :
    JsonBinaryChartInterpreter.certify 3 n
      (StrictJsonValueBridge.reencode 3 (witnessValue w)) =
      some (⟨candidate w ht, hc⟩ : Certified n) := by
  unfold JsonBinaryChartInterpreter.certify
  rw [JsonBinaryChartInterpreter.decode_reencode 3 _ (witness_supported w)]
  exact certify_witness w ht hc

def entry {n : Nat} (w : Witness n)
    (ht : CheckedPermutationTables.check w.permutation = true)
    (hc : CheckedBinaryChart.check (candidate w ht) = true) :
    JsonPackedColumnDictionary.CheckedEntry n :=
  ⟨w.columns, ⟨candidate w ht, hc⟩, fun _ => rfl⟩

/-- A real named-field equation supplies dictionary decoding; both actual finite
checks then accept the original five-array witness, without assumed entry success. -/
theorem certify_entry_witness {n : Nat} (w : Witness n)
    (ht : CheckedPermutationTables.check w.permutation = true)
    (hc : CheckedBinaryChart.check (candidate w ht) = true)
    (dictionary : Lean.Json) (key : String)
    (hfield : dictionary.getObjVal? key = .ok
      (StrictJsonValueBridge.reencode 2 (vectorValue w.columns))) :
    JsonPackedColumnDictionary.certifyEntry 3 n dictionary key
      (StrictJsonValueBridge.reencode 3 (witnessValue w)) =
      some (entry w ht hc) := by
  have hd : JsonPackedColumnDictionary.dictionaryColumns n dictionary key =
      some w.columns := by
    unfold JsonPackedColumnDictionary.dictionaryColumns
    rw [hfield]
    exact JsonPackedColumnDictionary.decodeColumns_canonical w.columns
  unfold JsonPackedColumnDictionary.certifyEntry
  rw [hd, certify_json_witness w ht hc]
  have hm : ∀ j, (candidate w ht).columns j = columnFunction w.columns j :=
    fun _ => rfl
  change (if h : ∀ j, (candidate w ht).columns j = columnFunction w.columns j then
    some (⟨w.columns, ⟨candidate w ht, hc⟩, h⟩ : JsonPackedColumnDictionary.CheckedEntry n)
    else none) = some (entry w ht hc)
  rw [dif_pos hm]
  all_goals rfl

end CurrentMain.BoundedChartWitnessCompleteness
#print axioms CurrentMain.BoundedChartWitnessCompleteness.decodePermutation_tables
#print axioms CurrentMain.BoundedChartWitnessCompleteness.decode_witness
#print axioms CurrentMain.BoundedChartWitnessCompleteness.certify_witness
#print axioms CurrentMain.BoundedChartWitnessCompleteness.witness_supported
#print axioms CurrentMain.BoundedChartWitnessCompleteness.certify_json_witness
#print axioms CurrentMain.BoundedChartWitnessCompleteness.certify_entry_witness
#check @CurrentMain.BoundedChartWitnessCompleteness.certify_json_witness
#check @CurrentMain.BoundedChartWitnessCompleteness.certify_entry_witness
