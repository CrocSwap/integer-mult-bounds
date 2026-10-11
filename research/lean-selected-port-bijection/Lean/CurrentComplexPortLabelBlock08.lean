import CGInputData
import PairedCubeLabelBlocks
set_option maxRecDepth 100000
set_option maxHeartbeats 16000000
namespace CurrentMain.CurrentComplexPortLabels
open CurrentMain.ComplexGeometryData CurrentMain.PairedCubeSourceLabels

/-- Exact selected accessor interval [1312,1320) in its original order. -/
theorem block08 : (List.range' 1312 8).map inputMask = labelsFor 11 8 := by decide
end CurrentMain.CurrentComplexPortLabels
#print axioms CurrentMain.CurrentComplexPortLabels.block08
