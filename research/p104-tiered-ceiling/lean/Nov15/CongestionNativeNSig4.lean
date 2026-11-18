import Nov15.CongestionI3DualSig
import Nov15.CongestionI3NumC1
import Nov15.CongestionNativeNDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem sigN4 : sigOK (1 - tN5) (1 - tN4) sgN4 = true := by unfold tN4 tN5 sgN4; decide +kernel
end CongestionNative
