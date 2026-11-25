import JsonBinaryChartInterpreter

/-!
Reusable interpretation of the existing ACTUAL-SIGMAS dictionary layout:
a named object entry is an ordered array of packed nonnegative binary columns.
The selected emitter at main0b1cccf8 stores sigmas[hash]=sigma, with sigma[j]
the ambient bit vector of the jth source axis. This module generalizes the
array length and bit bound to n and2^n; it does not recensus a selected table.

Actual object lookup and strict depth-two JSON decoding retain the complete
entry AST. Every column is bounded before its bits are interpreted. A separate
actual JSON certificate is checked by the accepted interpreter, then an
executable scalar comparison requires all its columns to equal the dictionary
entry. The independently defined dictionary-column operator, both inverses and
arbitrary-payload pullback cancellation follow from those actual checks.

ACTUAL-SIGMAS does not contain the four auxiliary certificate fields. The new
certificate is an explicit witness supplied to this adapter, never a claim about
the provider grammar. The key is only selected, not cryptographically validated.
Byte parsing, duplicate-key/number spelling, artifact/key identity, complex
phase/affine translations, physical chart direction/executor and costs remain
separate. Generic results do not change or prove a multiplication exponent.
Author-checked context only: kappa=836330098538459/500000000000000000.
Attribution: Rohan Arun PR1094; Jeremy Kothe T16 emitter; inherited geometry
and accepted bank/frame strict JSON/index/permutation/chart certificates;
Lean and Mathlib. James Chang with OpenAI assistance; Apache-2.0. UNCOMPILED.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.JsonPackedColumnDictionary
open CheckedBinaryChart (Address bits)
open ParsedBinaryChartCertificate (BoundedVector vectorAt vectorValue columnFunction)

abbrev Columns (n : Nat) := BoundedVector n (2 ^ n)

/-- Array length n and every actual integer bound2^n are checked separately. -/
def decodeColumns (n : Nat) (raw : Lean.Json) : Option (Columns n) := do
  let values ← StrictJsonValueBridge.decode 2 raw
  ParsedBinaryChartCertificate.decodeVector n (2 ^ n) values

theorem decodeColumns_sound {n : Nat} (raw : Lean.Json) (cols : Columns n)
    (h : decodeColumns n raw = some cols) :
    StrictJsonValueBridge.reencode 2 (vectorValue cols) = raw ∧
      ∀ j, columnFunction cols j < 2 ^ n := by
  obtain ⟨values, hv, hc⟩ := Option.bind_eq_some_iff.mp h
  constructor
  · rw [ParsedBinaryChartCertificate.decodeVector_sound values cols hc]
    exact StrictJsonValueBridge.decode_sound 2 raw values hv
  · intro j
    exact (vectorAt cols j).isLt

/-- Constructive completeness for the exact ordered packed-column grammar. -/
theorem decodeColumns_canonical {n : Nat} (cols : Columns n) :
    decodeColumns n (StrictJsonValueBridge.reencode 2 (vectorValue cols)) = some cols := by
  have hs : JsonBinaryChartInterpreter.SupportedAt 2 (vectorValue cols) := by
    intro v hv
    obtain ⟨i, _, rfl⟩ := List.mem_map.mp hv
    trivial
  unfold decodeColumns
  rw [JsonBinaryChartInterpreter.decode_reencode 2 _ hs]
  change ParsedBinaryChartCertificate.decodeVector n (2 ^ n) (vectorValue cols) = some cols
  exact ParsedBinaryChartCertificate.decodeVector_complete cols

/-- Entry selection is by key, with no dictionary-order or digest assumption. -/
def dictionaryColumns (n : Nat) (dictionary : Lean.Json) (key : String) :
    Option (Columns n) :=
  match dictionary.getObjVal? key with
  | .error _ => none
  | .ok raw => decodeColumns n raw

theorem dictionaryColumns_sound {n : Nat} (dictionary : Lean.Json) (key : String)
    (cols : Columns n) (h : dictionaryColumns n dictionary key = some cols) :
    ∃ raw, dictionary.getObjVal? key = .ok raw ∧
      StrictJsonValueBridge.reencode 2 (vectorValue cols) = raw ∧
      ∀ j, columnFunction cols j < 2 ^ n := by
  cases he : dictionary.getObjVal? key with
  | error message =>
      simp only [dictionaryColumns, he] at h
      cases h
  | ok raw =>
      have hd : decodeColumns n raw = some cols := by
        simpa only [dictionaryColumns, he] using h
      exact ⟨raw, rfl, decodeColumns_sound raw cols hd⟩

/-- Independent operator of the decoded provider columns, without a certificate. -/
def columnOperator {n : Nat} (cols : Columns n) : Address n →ₗ[ZMod 2] Address n :=
  LinearMap.lsum (ZMod 2) (fun _ : Fin n => ZMod 2) (ZMod 2)
    (fun j => (LinearMap.id : ZMod 2 →ₗ[ZMod 2] ZMod 2).smulRight
      (bits (columnFunction cols j)))

theorem columnOperator_single {n : Nat} (cols : Columns n) (j : Fin n) (a : ZMod 2) :
    columnOperator cols (Pi.single j a) = a • bits (columnFunction cols j) := by
  rw [columnOperator, LinearMap.lsum_piSingle]
  rfl

private theorem columnOperator_eq_source {n : Nat} (cols : Columns n)
    (c : CheckedBinaryChart.Candidate n) (h : ∀ j, c.columns j = columnFunction cols j) :
    columnOperator cols = CheckedBinaryChart.sourceLinear c := by
  have he : c.columns = columnFunction cols := funext h
  unfold columnOperator CheckedBinaryChart.sourceLinear
  rw [he]

structure CheckedEntry (n : Nat) where
  columns : Columns n
  certificate : ParsedBinaryChartCertificate.Certified n
  column_match : ∀ j, certificate.val.columns j = columnFunction columns j

/-- The certificate and the provider entry are separately decoded, then compared.
All finite comparisons are performed; no operator equality is an input. -/
def certifyEntry (fuel n : Nat) (dictionary : Lean.Json) (key : String)
    (certificateJson : Lean.Json) : Option (CheckedEntry n) := do
  let cols ← dictionaryColumns n dictionary key
  let cert ← JsonBinaryChartInterpreter.certify fuel n certificateJson
  if h : ∀ j, cert.val.columns j = columnFunction cols j then
    some ⟨cols, cert, h⟩
  else none

/-- Actual success derives both source decodings, not only a typed certificate. -/
theorem certifyEntry_inputs {n : Nat} (fuel : Nat) (dictionary : Lean.Json)
    (key : String) (certificateJson : Lean.Json) (r : CheckedEntry n)
    (h : certifyEntry fuel n dictionary key certificateJson = some r) :
    dictionaryColumns n dictionary key = some r.columns ∧
      JsonBinaryChartInterpreter.certify fuel n certificateJson = some r.certificate := by
  change (dictionaryColumns n dictionary key >>= fun cols =>
    JsonBinaryChartInterpreter.certify fuel n certificateJson >>= fun cert =>
      if hm : ∀ j, cert.val.columns j = columnFunction cols j then
        some (⟨cols, cert, hm⟩ : CheckedEntry n) else none) = some r at h
  obtain ⟨cols, hc, ht⟩ := Option.bind_eq_some_iff.mp h
  obtain ⟨cert, he, hm⟩ := Option.bind_eq_some_iff.mp ht
  split at hm
  · rename_i hmatch
    have hr : (⟨cols, cert, hmatch⟩ : CheckedEntry n) = r := Option.some.inj hm
    cases hr
    exact ⟨hc, he⟩
  · cases hm

private theorem entry_operator {n : Nat} (r : CheckedEntry n) :
    columnOperator r.columns =
      (CheckedBinaryChart.checkedEquiv r.certificate.val r.certificate.property).toLinearMap := by
  rw [columnOperator_eq_source r.columns r.certificate.val r.column_match]
  exact CheckedBinaryChart.sourceLinear_eq_checked r.certificate.val r.certificate.property

/-- The original dictionary AST and full auxiliary certificate witness remain
bound while all-address operator identity and both inverse directions are derived. -/
theorem certifyEntry_sound {n : Nat} (fuel : Nat) (dictionary : Lean.Json)
    (key : String) (certificateJson : Lean.Json) (r : CheckedEntry n)
    (h : certifyEntry fuel n dictionary key certificateJson = some r) :
    (∃ raw, dictionary.getObjVal? key = .ok raw ∧
      StrictJsonValueBridge.reencode 2 (vectorValue r.columns) = raw) ∧
    (∃ w : ParsedBinaryChartCertificate.Witness n,
      StrictJsonValueBridge.reencode fuel (ParsedBinaryChartCertificate.witnessValue w) =
        certificateJson ∧ ParsedBinaryChartCertificate.Binds r.certificate.val w) ∧
    columnOperator r.columns =
      (CheckedBinaryChart.checkedEquiv r.certificate.val r.certificate.property).toLinearMap ∧
    (∀ x, CheckedBinaryChart.inverseAddress r.certificate.val (columnOperator r.columns x) = x) ∧
    (∀ x, columnOperator r.columns (CheckedBinaryChart.inverseAddress r.certificate.val x) = x) := by
  obtain ⟨hd, hc⟩ := certifyEntry_inputs fuel dictionary key certificateJson r h
  obtain ⟨raw, he, hr, _⟩ := dictionaryColumns_sound dictionary key r.columns hd
  obtain ⟨w, hw, hb, _, hl, hh⟩ :=
    JsonBinaryChartInterpreter.certify_sound fuel certificateJson r.certificate hc
  refine ⟨⟨raw, he, hr⟩, ⟨w, hw, hb⟩, entry_operator r, ?_, ?_⟩
  · rw [columnOperator_eq_source r.columns r.certificate.val r.column_match]
    exact hl
  · rw [columnOperator_eq_source r.columns r.certificate.val r.column_match]
    exact hh

/-- Explicit pullback convention on arbitrary payloads; it does not identify an
external physical executor's direction or insert a complex phase. -/
theorem arbitrary_payload_cancellation {n : Nat} {α : Type*} (r : CheckedEntry n)
    (f : Address n → α) :
    (fun x => f (columnOperator r.columns (CheckedBinaryChart.inverseAddress r.certificate.val x))) = f ∧
    (fun x => f (CheckedBinaryChart.inverseAddress r.certificate.val (columnOperator r.columns x))) = f := by
  rw [columnOperator_eq_source r.columns r.certificate.val r.column_match]
  constructor
  · funext x
    rw [CheckedBinaryChart.source_inverse r.certificate.val r.certificate.property]
  · funext x
    rw [CheckedBinaryChart.inverse_source r.certificate.val r.certificate.property]

end CurrentMain.JsonPackedColumnDictionary
#print axioms CurrentMain.JsonPackedColumnDictionary.decodeColumns_sound
#print axioms CurrentMain.JsonPackedColumnDictionary.decodeColumns_canonical
#print axioms CurrentMain.JsonPackedColumnDictionary.dictionaryColumns_sound
#print axioms CurrentMain.JsonPackedColumnDictionary.columnOperator_single
#print axioms CurrentMain.JsonPackedColumnDictionary.certifyEntry_inputs
#print axioms CurrentMain.JsonPackedColumnDictionary.certifyEntry_sound
#print axioms CurrentMain.JsonPackedColumnDictionary.arbitrary_payload_cancellation
#check @CurrentMain.JsonPackedColumnDictionary.certifyEntry_sound
#check @CurrentMain.JsonPackedColumnDictionary.arbitrary_payload_cancellation
