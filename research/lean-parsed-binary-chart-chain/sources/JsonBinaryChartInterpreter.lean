import StrictJsonValueBridge
import BinaryChartCanonicalEncoding

/-!
UNCOMPILED reusable execution of binary chart certificates from actual Lean.Json
ASTs. The interpreter runs the strict fuel-bounded AST bridge and then the
accepted parsed chart certifier. Its soundness derives the complete ordered AST
witness, binary operator equality and both inverse identities from actual success.

The canonical encoder has a constructive completeness theorem at depth three:
outer certificate array, field arrays, integer entries. A general supported-at-
fuel theorem proves AST decode/reencode completeness before this specialization.
No selected table or L450 literal is copied. A scalar-checked typed Candidate is
needed to generate its canonical certificate, not to interpret arbitrary input.

The grammar is the new five-array chart certificate, not a claim about existing
provider files. JSON byte parsing, lexical number spelling, source-artifact
conversion, complex phases, affine translations, physical executor, precision and
cost remain separate. The actual AST numeric policy is exponent zero only.
Fuel is a structural nesting bound, not a time or memory bound.
Author-checked context only:
kappa=836330098538459/500000000000000000=0.001672660197076918.
Generic results are independent of kappa. Credits: accepted strict Json bridge,
parsed index/permutation/chart certificates, canonical encoder, and Lean/Mathlib.
James Chang with OpenAI assistance; Apache-2.0.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.JsonBinaryChartInterpreter
open SelectedSourceSyntax (Value)

/-- Exact domain for round-trip completeness at a specified structural fuel. -/
def SupportedAt : Nat → Value → Prop
  | 0, _ => False
  | fuel + 1, .array xs => ∀ x ∈ xs, SupportedAt fuel x
  | _ + 1, .other => False
  | _ + 1, _ => True

private theorem mapM_encode {α β : Type} (encode : α → β) (decode : β → Option α)
    (xs : List α) (h : ∀ x ∈ xs, decode (encode x) = some x) :
    (xs.map encode).mapM decode = some xs := by
  revert h
  induction xs with
  | nil => intro _; rfl
  | cons x xs ih =>
      intro h
      have hx := h x (by simp)
      have ht := ih (fun y hy => h y (by simp [hy]))
      rw [List.map_cons, List.mapM_cons, hx, ht]
      all_goals rfl

/-- General constructive completeness of the actual fuel-bounded AST bridge. -/
theorem decode_reencode (fuel : Nat) (v : Value) (h : SupportedAt fuel v) :
    StrictJsonValueBridge.decode fuel (StrictJsonValueBridge.reencode fuel v) = some v := by
  induction fuel generalizing v with
  | zero => cases h
  | succ fuel ih =>
      cases v with
      | text s => rfl
      | integer z => rfl
      | boolean b => rfl
      | other => cases h
      | array xs =>
          change ((xs.map (StrictJsonValueBridge.reencode fuel)).mapM
            (StrictJsonValueBridge.decode fuel) >>= fun ys => some (Value.array ys)) =
              some (Value.array xs)
          have hm := mapM_encode (StrictJsonValueBridge.reencode fuel)
            (StrictJsonValueBridge.decode fuel) xs (fun x hx => ih x (h x hx))
          rw [hm]
          all_goals rfl

private theorem index_array_supported {n : Nat} (xs : List (Fin n)) :
    SupportedAt 2 (.array (xs.map StrictParsedIndexCodec.indexValue)) := by
  intro v hv
  obtain ⟨i, _, rfl⟩ := List.mem_map.mp hv
  trivial

/-- Every canonical chart field has precisely the depth needed by the bridge. -/
theorem canonical_supported {n : Nat} (c : CheckedBinaryChart.Candidate n)
    (h : CheckedBinaryChart.check c = true) :
    SupportedAt 3 (BinaryChartCanonicalEncoding.encodeCandidate c h) := by
  change ∀ v ∈ [CheckedPermutationTables.tableValue
      (BinaryChartCanonicalEncoding.tableOfFunction c.permutation),
    CheckedPermutationTables.tableValue
      (BinaryChartCanonicalEncoding.tableOfFunction c.permutation.symm),
    ParsedBinaryChartCertificate.vectorValue
      (BinaryChartCanonicalEncoding.columnVector c h),
    ParsedBinaryChartCertificate.vectorValue
      (BinaryChartCanonicalEncoding.binaryVector c.updateVector),
    ParsedBinaryChartCertificate.vectorValue
      (BinaryChartCanonicalEncoding.binaryVector c.coefficients)], SupportedAt 2 v
  intro v hv
  simp only [List.mem_cons, List.mem_nil_iff, or_false] at hv
  rcases hv with rfl | rfl | rfl | rfl | rfl
  · exact index_array_supported _
  · exact index_array_supported _
  · exact index_array_supported _
  · exact index_array_supported _
  · exact index_array_supported _

/-- Actual AST conversion and actual strict certificate checking, in order. -/
def certify (fuel n : Nat) (raw : Lean.Json) : Option (ParsedBinaryChartCertificate.Certified n) := do
  let v ← StrictJsonValueBridge.decode fuel raw
  ParsedBinaryChartCertificate.certify n v

/-- Success provides the original ordered AST witness and the checked operator. -/
theorem certify_sound {n : Nat} (fuel : Nat) (raw : Lean.Json)
    (r : ParsedBinaryChartCertificate.Certified n) (h : certify fuel n raw = some r) :
    ∃ w : ParsedBinaryChartCertificate.Witness n,
      StrictJsonValueBridge.reencode fuel (ParsedBinaryChartCertificate.witnessValue w) = raw ∧
      ParsedBinaryChartCertificate.Binds r.val w ∧
      CheckedBinaryChart.sourceLinear r.val =
        (CheckedBinaryChart.checkedEquiv r.val r.property).toLinearMap ∧
      (∀ x, CheckedBinaryChart.inverseAddress r.val (CheckedBinaryChart.sourceLinear r.val x) = x) ∧
      (∀ x, CheckedBinaryChart.sourceLinear r.val (CheckedBinaryChart.inverseAddress r.val x) = x) := by
  obtain ⟨v, hv, hr⟩ := Option.bind_eq_some_iff.mp h
  obtain ⟨w, hw, hb, hop, hl, hh⟩ := ParsedBinaryChartCertificate.certify_sound v r hr
  refine ⟨w, ?_, hb, hop, hl, hh⟩
  rw [hw]
  exact StrictJsonValueBridge.decode_sound fuel raw v hv

def canonicalJson {n : Nat} (c : CheckedBinaryChart.Candidate n)
    (h : CheckedBinaryChart.check c = true) : Lean.Json :=
  StrictJsonValueBridge.reencode 3 (BinaryChartCanonicalEncoding.encodeCandidate c h)

/-- Canonical typed certificates are actually accepted through the JSON-AST path. -/
theorem certify_canonical {n : Nat} (c : CheckedBinaryChart.Candidate n)
    (h : CheckedBinaryChart.check c = true) :
    certify 3 n (canonicalJson c h) =
      some (⟨c, h⟩ : ParsedBinaryChartCertificate.Certified n) := by
  unfold certify canonicalJson
  rw [decode_reencode 3 _ (canonical_supported c h)]
  change ParsedBinaryChartCertificate.certify n (BinaryChartCanonicalEncoding.encodeCandidate c h) =
    some (⟨c, h⟩ : ParsedBinaryChartCertificate.Certified n)
  exact BinaryChartCanonicalEncoding.certify_encodeCandidate c h

def checkJson (fuel n : Nat) (raw : Lean.Json) : Bool := (certify fuel n raw).isSome

theorem checkJson_canonical {n : Nat} (c : CheckedBinaryChart.Candidate n)
    (h : CheckedBinaryChart.check c = true) : checkJson 3 n (canonicalJson c h) = true := by
  simp only [checkJson, certify_canonical, Option.isSome_some]

end CurrentMain.JsonBinaryChartInterpreter
#print axioms CurrentMain.JsonBinaryChartInterpreter.decode_reencode
#print axioms CurrentMain.JsonBinaryChartInterpreter.canonical_supported
#print axioms CurrentMain.JsonBinaryChartInterpreter.certify_sound
#print axioms CurrentMain.JsonBinaryChartInterpreter.certify_canonical
#print axioms CurrentMain.JsonBinaryChartInterpreter.checkJson_canonical
#check @CurrentMain.JsonBinaryChartInterpreter.certify_sound
#check @CurrentMain.JsonBinaryChartInterpreter.certify_canonical
