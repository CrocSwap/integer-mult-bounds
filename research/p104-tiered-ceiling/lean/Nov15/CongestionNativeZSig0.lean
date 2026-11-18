import Nov15.CongestionI3DualSig
import Nov15.CongestionI3NumC1
import Nov15.CongestionNativeZDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem sigZ0 : sigOK (1 - tZ1) (1 - tZ0) sgZ0 = true := by unfold tZ0 tZ1 sgZ0; decide +kernel
end CongestionNative
