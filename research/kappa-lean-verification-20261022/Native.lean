import NativeForward
import NativeBackward

set_option maxRecDepth 100000
set_option maxHeartbeats 0

namespace NativeVerification
open NativeCertificate NativeData

theorem every_declared_frame_independent (i : Fin frameEntries.length) :
    independent (frameEntries.get i).data = true := (frameEntries.get i).valid

theorem every_declared_operator_has_exact_inverse (i : Fin operatorEntries.length) :
    checkOperator (operatorEntries.get i).data = true := (operatorEntries.get i).valid

theorem every_paid_class_checked (i : Fin paidEntries.length) :
    checkPaid frames (paidEntries.get i).data = true := (paidEntries.get i).valid

theorem every_warp_class_checked (i : Fin warpEntries.length) :
    checkWarp frames operators (warpEntries.get i).data = true := (warpEntries.get i).valid

theorem every_helper_interface_checked (i : Fin helperEntries.length) :
    checkPaid frames (helperEntries.get i).data = true := (helperEntries.get i).valid

theorem every_forward_segment_checked (i : Fin forwardSegments.length) :
    checkSegment frames paid warps (forwardSegments.get i).data = true :=
  (forwardSegments.get i).valid

theorem every_backward_segment_checked (i : Fin backwardSegments.length) :
    checkSegment frames paid warps (backwardSegments.get i).data = true :=
  (backwardSegments.get i).valid

theorem finite_catalogue_sizes :
    frameEntries.length = 4429 ∧ operatorEntries.length = 72 ∧
    paidEntries.length = 2863 ∧ warpEntries.length = 180 ∧
    helperEntries.length = 408 ∧ newPaidIndices.size = 128 := by decide

theorem exactly_34_operator_changes :
    operatorEntries.foldl (fun n g => n + if g.data.columns == g.data.oldColumns then 0 else 1) 0 = 34 := by decide

theorem all_128_new_paid_indices_in_range :
    newPaidIndices.all (fun i => i < paidEntries.length) = true := by decide

theorem all_128_new_paid_indices_distinct :
    newPaidIndices.toList.Nodup := by decide

def helperCensus : Array Nat :=
  (List.range 10).toArray.map (fun r =>
    helperEntries.foldl (fun n p => n + if p.data.rank == r then 1 else 0) 0)

theorem complete_productive_helper_census :
    helperCensus = #[0,0,0,0,28,0,0,7,47,326] := by decide

theorem helpers_are_actual_endpoint_interfaces :
    (helperEntries.zipIdx).all (fun (h, i) =>
      h.data.input == initialFrames.get (224+i) &&
      h.data.output == finalFrames.get (224+i)) = true := by decide

/-- Complete finite frame/contact/invoice certificate for the two emitted
words. This proposition does not assert a symbolic or amplitude endpoint. -/
theorem complete_finite_native_certificate :
    linked initialFrames finalFrames forwardData = true ∧
    linked initialFrames backwardFinalFrames backwardData = true ∧
    totalPaid forwardData = #[0,2201,412,506,135,36,0,0,8,0] ∧
    totalPaid backwardData = #[0,2201,412,506,135,36,0,0,8,0] ∧
    totalScalarCost forwardData = 158120 ∧
    totalScalarCost backwardData = 158168 ∧
    totalEvents forwardData = 21449 ∧ totalEvents backwardData = 21449 ∧
    backwardFinalFrames.toList.take 632 = finalFrames.toList.take 632 :=
  ⟨forward_linked, backward_linked, forward_paid, backward_paid,
    forward_scalar_cost, backward_scalar_cost, forward_event_count, backward_event_count,
    backward_persistent_final_matches⟩

theorem paid_call_count :
    (#[0,2201,412,506,135,36,0,0,8,0] : Array Nat).foldl (· + ·) 0 = 3298 := by decide

theorem all_embedded_catalogues_and_segments_checked :
    (frames.wellFormed && operators.wellFormed && paid.wellFormed && warps.wellFormed) = true ∧
    frameEntries.map (·.data) = frames.toList ∧
    operatorEntries.map (·.data) = operators.toList ∧
    paidEntries.map (·.data) = paid.toList ∧
    warpEntries.map (·.data) = warps.toList ∧
    (∀ i : Fin frameEntries.length, independent (frameEntries.get i).data = true) ∧
    (∀ i : Fin operatorEntries.length, checkOperator (operatorEntries.get i).data = true) ∧
    (∀ i : Fin paidEntries.length, checkPaid frames (paidEntries.get i).data = true) ∧
    (∀ i : Fin warpEntries.length, checkWarp frames operators (warpEntries.get i).data = true) ∧
    (∀ i : Fin helperEntries.length, checkPaid frames (helperEntries.get i).data = true) ∧
    (∀ i : Fin forwardSegments.length, checkSegment frames paid warps (forwardSegments.get i).data = true) ∧
    (∀ i : Fin backwardSegments.length, checkSegment frames paid warps (backwardSegments.get i).data = true) :=
  ⟨raw_tables_well_formed, frame_transcription_exact, operator_transcription_exact,
    paid_transcription_exact, warp_transcription_exact,
    every_declared_frame_independent, every_declared_operator_has_exact_inverse,
    every_paid_class_checked, every_warp_class_checked,
    every_helper_interface_checked,
    every_forward_segment_checked, every_backward_segment_checked⟩

#print axioms every_declared_frame_independent
#print axioms every_declared_operator_has_exact_inverse
#print axioms every_paid_class_checked
#print axioms every_warp_class_checked
#print axioms every_forward_segment_checked
#print axioms every_backward_segment_checked
#print axioms complete_productive_helper_census
#print axioms complete_finite_native_certificate
#print axioms all_embedded_catalogues_and_segments_checked

end NativeVerification
