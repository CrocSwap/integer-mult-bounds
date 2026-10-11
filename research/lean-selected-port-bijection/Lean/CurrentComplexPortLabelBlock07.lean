import CGInputData
import PairedCubeLabelBlocks
set_option maxRecDepth 100000
set_option maxHeartbeats 16000000
namespace CurrentMain.CurrentComplexPortLabels
open CurrentMain.ComplexGeometryData CurrentMain.PairedCubeSourceLabels

/-- Exact selected accessor interval [1288,1312) in its original order. -/
theorem block07 : (List.range' 1288 24).map inputMask = labelsFor 11 7 := by decide
end CurrentMain.CurrentComplexPortLabels
#print axioms CurrentMain.CurrentComplexPortLabels.block07
