import CGInputData
import PairedCubeLabelBlocks
set_option maxRecDepth 100000
set_option maxHeartbeats 16000000
namespace CurrentMain.CurrentComplexPortLabels
open CurrentMain.ComplexGeometryData CurrentMain.PairedCubeSourceLabels

/-- Exact selected accessor interval [360,648) in its original order. -/
theorem block01 : (List.range' 360 288).map inputMask = labelsFor 11 1 := by decide
end CurrentMain.CurrentComplexPortLabels
#print axioms CurrentMain.CurrentComplexPortLabels.block01
