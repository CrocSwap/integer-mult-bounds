import Nov15.CongestionI3DualSig
import Nov15.CongestionI3NumC1
import Nov15.CongestionNativeZDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem sigZ4 : sigOK (1 - tZ5) (1 - tZ4) sgZ4 = true := by unfold tZ4 tZ5 sgZ4; decide +kernel
end CongestionNative
