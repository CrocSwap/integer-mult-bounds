import Nov15.CongestionI3DualSig
import Nov15.CongestionI3NumC1
import Nov15.CongestionNativeZDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem sigZ1 : sigOK (1 - tZ2) (1 - tZ1) sgZ1 = true := by unfold tZ1 tZ2 sgZ1; decide +kernel
end CongestionNative
