import CGInputData
import PairedCubeLabelBlocks
set_option maxRecDepth 100000
set_option maxHeartbeats 16000000
namespace CurrentMain.CurrentComplexPortLabels
open CurrentMain.ComplexGeometryData CurrentMain.PairedCubeSourceLabels

/-- Exact selected accessor interval [0,360) in its original order. -/
theorem block00 : (List.range' 0 360).map inputMask = labelsFor 11 0 := by decide
end CurrentMain.CurrentComplexPortLabels
#print axioms CurrentMain.CurrentComplexPortLabels.block00
