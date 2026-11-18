import Nov15.CongestionI3DualSig
import Nov15.CongestionI3NumC1
import Nov15.CongestionNativeNDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem sigN2 : sigOK (1 - tN3) (1 - tN2) sgN2 = true := by unfold tN2 tN3 sgN2; decide +kernel
end CongestionNative
