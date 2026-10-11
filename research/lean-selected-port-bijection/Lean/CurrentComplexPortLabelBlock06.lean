import CGInputData
import PairedCubeLabelBlocks
set_option maxRecDepth 100000
set_option maxHeartbeats 16000000
namespace CurrentMain.CurrentComplexPortLabels
open CurrentMain.ComplexGeometryData CurrentMain.PairedCubeSourceLabels

/-- Exact selected accessor interval [1240,1288) in its original order. -/
theorem block06 : (List.range' 1240 48).map inputMask = labelsFor 11 6 := by decide
end CurrentMain.CurrentComplexPortLabels
#print axioms CurrentMain.CurrentComplexPortLabels.block06
