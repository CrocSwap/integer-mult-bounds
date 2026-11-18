import Nov15.CongestionI3DualSig
import Nov15.CongestionI3NumC1
import Nov15.CongestionNativeNDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem sigN0 : sigOK (1 - tN1) (1 - tN0) sgN0 = true := by unfold tN0 tN1 sgN0; decide +kernel
end CongestionNative
