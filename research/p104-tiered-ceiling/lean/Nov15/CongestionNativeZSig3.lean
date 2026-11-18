import Nov15.CongestionI3DualSig
import Nov15.CongestionI3NumC1
import Nov15.CongestionNativeZDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem sigZ3 : sigOK (1 - tZ4) (1 - tZ3) sgZ3 = true := by unfold tZ3 tZ4 sgZ3; decide +kernel
end CongestionNative
