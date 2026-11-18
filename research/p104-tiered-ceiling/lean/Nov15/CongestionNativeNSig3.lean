import Nov15.CongestionI3DualSig
import Nov15.CongestionI3NumC1
import Nov15.CongestionNativeNDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem sigN3 : sigOK (1 - tN4) (1 - tN3) sgN3 = true := by unfold tN3 tN4 sgN3; decide +kernel
end CongestionNative
