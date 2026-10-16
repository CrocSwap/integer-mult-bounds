import ParsedBinaryChartCertificate
import Mathlib.Data.List.OfFn

/-!
UNCOMPILED reusable completeness of canonical parsed chart certificates.
Finite functions are encoded in their full ordered List.ofFn arrays. Binary
values use canonical representatives in [0,2). A scalar-checked Candidate
therefore round-trips through the actual strict parsed interpreter, including
its permutation table checks and final scalar check. No selected array census
or assumed decoder success is used.

This is typed-data-to-Value completeness. It does not prove an external byte
serializer/parser, emitted-file conversion, actual physical chart convention,
complex phase, affine shifts, recipe/executor correctness, precision or cost.
The accepted checker remains a sufficient factorization certificate, not a
classification of every invertible binary map.
Author-checked context only:
kappa=836330098538459/500000000000000000=0.001672660197076918.
The generic theorem is independent of this number.
Credits: accepted strict index/permutation/parsed chart components and
Lean/Mathlib List.ofFn, Fin and ZMod canonical representatives. Motivating
source lineage retains Jeremy Kothe, Rohan Arun/PR1094 and icekylinx.
Apache-2.0; OpenAI assistance.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.BinaryChartCanonicalEncoding
open SelectedSourceSyntax (Value)


/-- Full ordered table; its inverse is never inferred from a set of entries. -/
def tableOfFunction {n : Nat} (f : Fin n → Fin n) : CheckedPermutationTables.Table n :=
  ⟨List.ofFn f, List.length_ofFn⟩

theorem tableAt_ofFunction {n : Nat} (f : Fin n → Fin n) (i : Fin n) :
    CheckedPermutationTables.tableAt (tableOfFunction f) i = f i := by
  change (List.ofFn f).get _ = f i
  rw [List.get_ofFn]
  apply congrArg f
  apply Fin.ext
  rfl

def vectorOfFunction {n b : Nat} (f : Fin n → Fin b) : ParsedBinaryChartCertificate.BoundedVector n b :=
  ⟨List.ofFn f, List.length_ofFn⟩

theorem vectorAt_ofFunction {n b : Nat} (f : Fin n → Fin b) (i : Fin n) :
    ParsedBinaryChartCertificate.vectorAt (vectorOfFunction f) i = f i := by
  change (List.ofFn f).get _ = f i
  rw [List.get_ofFn]
  apply congrArg f
  apply Fin.ext
  rfl

def permutationCertificate {n : Nat} (p : Equiv.Perm (Fin n)) : CheckedPermutationTables.Certificate n :=
  ⟨tableOfFunction p, tableOfFunction p.symm⟩

theorem permutation_check {n : Nat} (p : Equiv.Perm (Fin n)) :
    CheckedPermutationTables.check (permutationCertificate p) = true := by
  apply (CheckedPermutationTables.check_iff _).mpr
  intro i
  change CheckedPermutationTables.tableAt (tableOfFunction p.symm) (CheckedPermutationTables.tableAt (tableOfFunction p) i) = i ∧
    CheckedPermutationTables.tableAt (tableOfFunction p) (CheckedPermutationTables.tableAt (tableOfFunction p.symm) i) = i
  constructor
  · simp only [tableAt_ofFunction, Equiv.symm_apply_apply]
  · simp only [tableAt_ofFunction, Equiv.apply_symm_apply]

private theorem checkedEquiv_ofPermutation {n : Nat} (p : Equiv.Perm (Fin n)) :
    CheckedPermutationTables.checkedEquiv (permutationCertificate p) (permutation_check p) = p := by
  apply Equiv.ext
  intro i
  exact tableAt_ofFunction p i

private theorem decodeCertificate_complete {n : Nat} (c : CheckedPermutationTables.Certificate n) :
    CheckedPermutationTables.decodeCertificate n (CheckedPermutationTables.tableValue c.forward) (CheckedPermutationTables.tableValue c.backward) = some c := by
  simp only [CheckedPermutationTables.decodeCertificate, CheckedPermutationTables.decodeTable_complete]
  all_goals rfl

/-- Actual parser and both finite table checks accept every encoded permutation. -/
theorem decodePermutation_ofEquiv {n : Nat} (p : Equiv.Perm (Fin n)) :
    CheckedPermutationTables.decodePermutation n (CheckedPermutationTables.tableValue (tableOfFunction p))
      (CheckedPermutationTables.tableValue (tableOfFunction p.symm)) = some p := by
  unfold CheckedPermutationTables.decodePermutation
  have hd := decodeCertificate_complete (permutationCertificate p)
  dsimp only [permutationCertificate] at hd
  rw [hd]
  change (if h : CheckedPermutationTables.check (permutationCertificate p) = true then
    some (CheckedPermutationTables.checkedEquiv (permutationCertificate p) h) else none) = some p
  rw [dif_pos (permutation_check p)]
  exact congrArg some (checkedEquiv_ofPermutation p)

def binaryVector {n : Nat} (x : CheckedBinaryChart.Address n) : ParsedBinaryChartCertificate.BoundedVector n 2 :=
  vectorOfFunction (fun i => ⟨(x i).val, ZMod.val_lt (x i)⟩)

private theorem binaryFunction_eq {n : Nat} (x : CheckedBinaryChart.Address n) :
    ParsedBinaryChartCertificate.binaryFunction (binaryVector x) = x := by
  funext i
  change ((ParsedBinaryChartCertificate.vectorAt (vectorOfFunction
    (fun j => (⟨(x j).val, ZMod.val_lt (x j)⟩ : Fin 2))) i).val : ZMod 2) = x i
  rw [vectorAt_ofFunction]
  exact ZMod.natCast_zmod_val (x i)

def columnVector {n : Nat} (c : CheckedBinaryChart.Candidate n) (h : CheckedBinaryChart.check c = true) :
    ParsedBinaryChartCertificate.BoundedVector n (2 ^ n) :=
  vectorOfFunction (fun i => ⟨c.columns i, CheckedBinaryChart.checked_column_bounds c h i⟩)

private theorem columnFunction_eq {n : Nat} (c : CheckedBinaryChart.Candidate n)
    (h : CheckedBinaryChart.check c = true) : ParsedBinaryChartCertificate.columnFunction (columnVector c h) = c.columns := by
  funext i
  change (ParsedBinaryChartCertificate.vectorAt (vectorOfFunction
    (fun j => (⟨c.columns j, CheckedBinaryChart.checked_column_bounds c h j⟩ : Fin (2 ^ n)))) i).val = c.columns i
  rw [vectorAt_ofFunction]

def candidateFields {n : Nat} (c : CheckedBinaryChart.Candidate n) (h : CheckedBinaryChart.check c = true) : ParsedBinaryChartCertificate.RawFields :=
  ⟨CheckedPermutationTables.tableValue (tableOfFunction c.permutation),
    CheckedPermutationTables.tableValue (tableOfFunction c.permutation.symm),
    ParsedBinaryChartCertificate.vectorValue (columnVector c h), ParsedBinaryChartCertificate.vectorValue (binaryVector c.updateVector),
    ParsedBinaryChartCertificate.vectorValue (binaryVector c.coefficients)⟩

def encodeCandidate {n : Nat} (c : CheckedBinaryChart.Candidate n) (h : CheckedBinaryChart.check c = true) : Value :=
  ParsedBinaryChartCertificate.fieldsValue (candidateFields c h)

private theorem decodeShape_fieldsValue (r : ParsedBinaryChartCertificate.RawFields) :
    ParsedBinaryChartCertificate.decodeShape (ParsedBinaryChartCertificate.fieldsValue r) = some r := by
  cases r
  rfl

/-- Every typed field, including both ordered index functions, is recovered by
actual strict parsing. Scalar-check validity is used only for column bounds. -/
theorem decode_encodeCandidate {n : Nat} (c : CheckedBinaryChart.Candidate n) (h : CheckedBinaryChart.check c = true) :
    ParsedBinaryChartCertificate.decode n (encodeCandidate c h) = some c := by
  unfold ParsedBinaryChartCertificate.decode encodeCandidate
  rw [decodeShape_fieldsValue]
  change ParsedBinaryChartCertificate.decodeFields n (candidateFields c h) = some c
  unfold ParsedBinaryChartCertificate.decodeFields candidateFields
  rw [decodePermutation_ofEquiv c.permutation,
    ParsedBinaryChartCertificate.decodeVector_complete (columnVector c h),
    ParsedBinaryChartCertificate.decodeVector_complete (binaryVector c.updateVector),
    ParsedBinaryChartCertificate.decodeVector_complete (binaryVector c.coefficients)]
  change some (CheckedBinaryChart.Candidate.mk (ParsedBinaryChartCertificate.columnFunction (columnVector c h)) c.permutation
    (ParsedBinaryChartCertificate.binaryFunction (binaryVector c.updateVector))
    (ParsedBinaryChartCertificate.binaryFunction (binaryVector c.coefficients))) = some c
  rw [columnFunction_eq, binaryFunction_eq, binaryFunction_eq]

/-- The final executable scalar check accepts the same recovered Candidate. -/
theorem certify_encodeCandidate {n : Nat} (c : CheckedBinaryChart.Candidate n) (h : CheckedBinaryChart.check c = true) :
    ParsedBinaryChartCertificate.certify n (encodeCandidate c h) = some (⟨c, h⟩ : ParsedBinaryChartCertificate.Certified n) := by
  unfold ParsedBinaryChartCertificate.certify
  rw [decode_encodeCandidate]
  change (if hc : CheckedBinaryChart.check c = true then some (⟨c, hc⟩ : ParsedBinaryChartCertificate.Certified n) else none) =
    some (⟨c, h⟩ : ParsedBinaryChartCertificate.Certified n)
  rw [dif_pos h]

theorem checkParsed_encodeCandidate {n : Nat} (c : CheckedBinaryChart.Candidate n) (h : CheckedBinaryChart.check c = true) :
    ParsedBinaryChartCertificate.checkParsed n (encodeCandidate c h) = true := by
  simp only [ParsedBinaryChartCertificate.checkParsed, certify_encodeCandidate, Option.isSome_some]

end CurrentMain.BinaryChartCanonicalEncoding
#print axioms CurrentMain.BinaryChartCanonicalEncoding.tableAt_ofFunction
#print axioms CurrentMain.BinaryChartCanonicalEncoding.vectorAt_ofFunction
#print axioms CurrentMain.BinaryChartCanonicalEncoding.permutation_check
#print axioms CurrentMain.BinaryChartCanonicalEncoding.decodePermutation_ofEquiv
#print axioms CurrentMain.BinaryChartCanonicalEncoding.decode_encodeCandidate
#print axioms CurrentMain.BinaryChartCanonicalEncoding.certify_encodeCandidate
#print axioms CurrentMain.BinaryChartCanonicalEncoding.checkParsed_encodeCandidate
#check @CurrentMain.BinaryChartCanonicalEncoding.certify_encodeCandidate
