import GeometryRangeComposition
import CGInputInverseData
namespace CurrentMain.CGInputAddressCheck014
open CurrentMain.ComplexGeometry CurrentMain.ComplexGeometryData CurrentMain.SignedTrace CurrentMain.BinaryFrame
set_option maxRecDepth 100000
set_option maxHeartbeats 16000000
theorem checked : rangeCheck (fun i => decide (inputMask i<2^22 ∧ get CurrentMain.ComplexGeometryInputs.inverseTable (inputMask i)=i)) 896 64=true := by decide
end CurrentMain.CGInputAddressCheck014
#print axioms CurrentMain.CGInputAddressCheck014.checked
