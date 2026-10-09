import FullModelProof
import FullTargetProof
import ActualDecoderWeights
import FreshResponseInterface
namespace FullCoefficientIdentity
open PairedWord PairedDecoder DagSemantics MaskModels PackedModels WeightedRows SignedPacking ReadoutAlgebra FullTraceData

/- Equality of the complete 1,760-entry integer coefficient vectors for every
listed target, proved by bounded radix injectivity, not by a hash. -/
theorem actual_combined_coefficients (target : Nat) (ht : target<1760) :
    WeightedRows.vector 1760 FullModelData.rows
      ((FullTargetPacking.readout target).map (remap FullTargetPacking.roleNode) ++ CubeCorrection.terms target) =
    (basis 1760 target).map (fun x => (6:Int)*x) := by
  let ts := (FullTargetPacking.readout target).map (remap FullTargetPacking.roleNode) ++ CubeCorrection.terms target
  have hw : weight ts = 60 := combined_weight target _ _ (ActualDecoderWeights.target_row_weight target ht)
  have he : encode (WeightedRows.vector 1760 FullModelData.rows ts) =
      encode ((basis 1760 target).map (fun x => (6:Int)*x)) := by
    rw [encode_vector, encode_scale, encode_basis 1760 target ht]
    calc
      PairedDecoder.evaluate ts (fun n => encoded 1760 (FullModelData.rows n)) =
          PairedDecoder.evaluate ts FullModelData.packed := by
        apply PairedDecoder.evaluate_congr
        intro term hterm
        exact (packed_equals_coefficient_encoding 1760 graph FullModelData.rows FullModelData.packed
          FullModelData.all_row_checks FullModelData.all_packed_checks term.role).symm
      _ = _ := FullTargetPacking.all_target_checks target ht
  apply encode_injective_radii _ _ 60 6 (by decide)
  · simp [WeightedRows.vector_length, basis]
  · intro d hd
    have h := WeightedRows.vector_bound 1760 FullModelData.rows ts d hd
    rw [hw] at h
    exact h
  · exact scaled_basis_bound 1760 target
  · exact he

end FullCoefficientIdentity
#print axioms FullCoefficientIdentity.actual_combined_coefficients
