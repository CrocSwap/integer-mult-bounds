import Nov15.CongestionTreeCertCGDefs
import Nov15.CongestionI3DualSig
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem sigCG0 : sigOK (1 - tCG1) (1 - tCG0) sgCG0 = true := by unfold tCG0 tCG1 sgCG0; decide +kernel
end CongestionNative
