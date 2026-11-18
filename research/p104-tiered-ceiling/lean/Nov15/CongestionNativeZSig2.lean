import Nov15.CongestionI3DualSig
import Nov15.CongestionI3NumC1
import Nov15.CongestionNativeZDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem sigZ2 : sigOK (1 - tZ3) (1 - tZ2) sgZ2 = true := by unfold tZ2 tZ3 sgZ2; decide +kernel
end CongestionNative
