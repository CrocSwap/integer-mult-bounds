import Nov15.CongestionI3DualSig
import Nov15.CongestionI3NumC1
import Nov15.CongestionNativeNDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem sigN1 : sigOK (1 - tN2) (1 - tN1) sgN1 = true := by unfold tN1 tN2 sgN1; decide +kernel
end CongestionNative
