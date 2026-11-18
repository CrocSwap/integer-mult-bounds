import Nov15.CongestionTreeCertCGDefs
import Nov15.CongestionI3DualSig
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem sigCG1 : sigOK (1 - tCG2) (1 - tCG1) sgCG1 = true := by unfold tCG1 tCG2 sgCG1; decide +kernel
end CongestionNative
