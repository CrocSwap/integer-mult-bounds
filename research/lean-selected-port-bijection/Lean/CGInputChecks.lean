import CGInputAddressChecks
namespace CurrentMain.ComplexGeometryInputs
open CurrentMain.ComplexGeometry CurrentMain.ComplexGeometryData CurrentMain.SignedTrace CurrentMain.BinaryFrame
set_option maxRecDepth 100000
set_option maxHeartbeats 16000000
theorem input_facts (i : Nat) (hi : i<1320) : inputMask i<2^22 ∧ get inverseTable (inputMask i)=i := of_decide_eq_true (rangeCheck_sound _ 0 1320 i CurrentMain.ComplexGeometryInputCertificates.address_checked (Nat.zero_le _) hi)
theorem input_bound (i : Nat) (hi : i<1320) : inputMask i<2^22 := (input_facts i hi).1
theorem input_injective (i : Nat) (hi : i<1320) (j : Nat) (hj : j<1320) (equal : inputMask i=inputMask j) : i=j := by
  have left := (input_facts i hi).2
  have right := (input_facts j hj).2
  rw [equal] at left
  exact left.symm.trans right
end CurrentMain.ComplexGeometryInputs
#print axioms CurrentMain.ComplexGeometryInputs.input_facts
#print axioms CurrentMain.ComplexGeometryInputs.input_bound
#print axioms CurrentMain.ComplexGeometryInputs.input_injective
