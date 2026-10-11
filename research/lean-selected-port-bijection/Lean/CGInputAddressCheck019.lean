import GeometryRangeComposition
import CGInputInverseData
namespace CurrentMain.CGInputAddressCheck019
open CurrentMain.ComplexGeometry CurrentMain.ComplexGeometryData CurrentMain.SignedTrace CurrentMain.BinaryFrame
set_option maxRecDepth 100000
set_option maxHeartbeats 16000000
theorem checked : rangeCheck (fun i => decide (inputMask i<2^22 ∧ get CurrentMain.ComplexGeometryInputs.inverseTable (inputMask i)=i)) 1216 64=true := by decide
end CurrentMain.CGInputAddressCheck019
#print axioms CurrentMain.CGInputAddressCheck019.checked
