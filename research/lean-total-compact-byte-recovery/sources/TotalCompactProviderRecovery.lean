import TotalCompactColumnDecoder
import RecoveredProviderChart

/-!
Actual total compact-byte decoding followed by the unchanged restricted chart
recovery algorithm. Execution receives the original ByteArray and update/form
vectors; it receives neither decoded columns, a permutation, inverse indices,
a certificate JSON value nor an operator equality. Its result retains both the
ordered Columns and the recovered checked certificate.

Success derives exact canonical byte identity, the original column function,
update/form values, the independent column operator and both inverse laws.
Completeness is confined to the existing scalar-checked single-transvection /
permutation class. No new finite checker, grammar or selected census occurs.
The opaque Json.parse interface is not used. Whole-artifact named-field
identity, producer authentication, general JSON compatibility, runtime extern
refinement, complex phase, physical execution and paid costs remain separate.
Author-checked context: kappa=836330098538459/500000000000000000
=0.001672660197076918; no generic statement changes or uses that exponent.
Credits: accepted bank/frame byte, chart and recovery proofs; Lean/Mathlib;
Jeremy Kothe T16 sigma encoding; Rohan Arun PR1094. James Chang with OpenAI
assistance. Apache-2.0. Independent acceptance remains separate.
-/
set_option Elab.async false
set_option autoImplicit false

namespace CurrentMain.TotalCompactProviderRecovery
open JsonPackedColumnDictionary (Columns columnOperator)
open ParsedBinaryChartCertificate (Certified columnFunction)
open CheckedBinaryChart (Address Candidate)

/-- Retain both actual ordered columns and the checked recovered certificate. -/
def recover (n : Nat) (bytes : ByteArray) (update coefficients : Address n) :
    Option (Columns n × Certified n) :=
  match TotalCompactColumnDecoder.decodePacked n bytes with
  | none => none
  | some cols =>
      match RecoveredProviderChart.recover ⟨columnFunction cols, update, coefficients⟩ with
      | none => none
      | some cert => some (cols, cert)

/-- Extract the two actual successful executions from their composite result. -/
theorem recover_inputs {n : Nat} (bytes : ByteArray) (update coefficients : Address n)
    (r : Columns n × Certified n) (h : recover n bytes update coefficients = some r) :
    TotalCompactColumnDecoder.decodePacked n bytes = some r.1 ∧
    RecoveredProviderChart.recover ⟨columnFunction r.1, update, coefficients⟩ = some r.2 := by
  cases hd : TotalCompactColumnDecoder.decodePacked n bytes with
  | none => simp only [recover, hd] at h; cases h
  | some cols =>
      cases hc : RecoveredProviderChart.recover
          (⟨columnFunction cols, update, coefficients⟩ : RecoveredProviderChart.Input n) with
      | none => simp only [recover, hd, hc] at h; cases h
      | some cert =>
          have he : (cols, cert) = r := Option.some.inj
            (by simpa only [recover, hd, hc] using h)
          cases he
          constructor
          · simp only [hd]
          · simp only [hc]

/-- Original bytes and the independent decoded-column operator are linked by
actual success, rather than a supplied global inverse or output equality. -/
theorem recover_sound {n : Nat} (bytes : ByteArray) (update coefficients : Address n)
    (r : Columns n × Certified n) (h : recover n bytes update coefficients = some r) :
    bytes = CompactNatColumnFragment.payload r.1 ∧
    r.2.val.columns = columnFunction r.1 ∧
    r.2.val.updateVector = update ∧ r.2.val.coefficients = coefficients ∧
    columnOperator r.1 =
      (CheckedBinaryChart.checkedEquiv r.2.val r.2.property).toLinearMap ∧
    (∀ x, CheckedBinaryChart.inverseAddress r.2.val (columnOperator r.1 x) = x) ∧
    (∀ x, columnOperator r.1 (CheckedBinaryChart.inverseAddress r.2.val x) = x) := by
  obtain ⟨hd, hr⟩ := recover_inputs bytes update coefficients r h
  obtain ⟨hc, hu, ha, _, he, hl, hh⟩ :=
    RecoveredProviderChart.recover_sound
      (⟨columnFunction r.1, update, coefficients⟩ : RecoveredProviderChart.Input n) r.2 hr
  have ho : columnOperator r.1 = CheckedBinaryChart.sourceLinear r.2.val := by
    unfold columnOperator CheckedBinaryChart.sourceLinear
    rw [hc]
  refine ⟨(TotalCompactColumnDecoder.decodePacked_eq_some_iff bytes r.1).mp hd,
    hc, hu, ha, ho.trans he, ?_, ?_⟩
  · rw [ho]
    exact hl
  · rw [ho]
    exact hh

/-- Completeness for the existing checked provider class. The candidate is a
proof-side specification; no permutation or certificate is an executable input. -/
theorem recover_complete {n : Nat} (bytes : ByteArray) (cols : Columns n)
    (c : Candidate n) (hcheck : CheckedBinaryChart.check c = true)
    (hcolumns : c.columns = columnFunction cols)
    (hbytes : bytes = CompactNatColumnFragment.payload cols) :
    recover n bytes c.updateVector c.coefficients =
      some (cols, (⟨c, hcheck⟩ : Certified n)) := by
  have hd := (TotalCompactColumnDecoder.decodePacked_eq_some_iff bytes cols).mpr hbytes
  have hi : (⟨columnFunction cols, c.updateVector, c.coefficients⟩ :
      RecoveredProviderChart.Input n) = RecoveredProviderChart.inputOf c := by
    rw [← hcolumns]
    rfl
  unfold recover
  rw [hd]
  change (match RecoveredProviderChart.recover
    (⟨columnFunction cols, c.updateVector, c.coefficients⟩ : RecoveredProviderChart.Input n) with
      | none => none
      | some cert => some (cols, cert)) = some (cols, (⟨c, hcheck⟩ : Certified n))
  rw [hi, RecoveredProviderChart.recover_complete c hcheck]

end CurrentMain.TotalCompactProviderRecovery
#print axioms CurrentMain.TotalCompactProviderRecovery.recover_inputs
#print axioms CurrentMain.TotalCompactProviderRecovery.recover_sound
#print axioms CurrentMain.TotalCompactProviderRecovery.recover_complete
#check @CurrentMain.TotalCompactProviderRecovery.recover_sound
#check @CurrentMain.TotalCompactProviderRecovery.recover_complete
