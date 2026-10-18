import FullFreshIdentity
import ActualCorrectionMatrix
namespace FullActualIdentity
open PairedWord PairedDecoder PairedWordData PairedWordCorollaries

theorem actual_source_matrix_fresh_response (payload : State) (target : Nat) (ht : target<1760) :
    decode6 ActualDecoder.rows (run word (inject payload)) target +
      ActualCorrectionMatrix.actualInputResponse target payload = 6*payload target := by
  rw [← ActualCorrectionMatrix.correction_is_actual_input_matrix target ht payload]
  exact FullFreshIdentity.actual_fresh_response payload target ht

theorem actual_source_matrix_dirty_response (z payload target : State) (i : Nat) (hi : i<1760) :
    (targetAdd (sub target (decode6 ActualDecoder.rows (run word z)))
      (decode6 ActualDecoder.rows (run word (add z (inject payload))))) i +
      ActualCorrectionMatrix.actualInputResponse i payload = target i + 6*payload i := by
  rw [← ActualCorrectionMatrix.correction_is_actual_input_matrix i hi payload]
  exact FullFreshIdentity.actual_dirty_corrected_response z payload target i hi

end FullActualIdentity
#print axioms FullActualIdentity.actual_source_matrix_fresh_response
#print axioms FullActualIdentity.actual_source_matrix_dirty_response
