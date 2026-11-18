import Nov15.CongestionI3DualSig
import Nov15.CongestionNativeJDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem sigJ1 : sigOK (1 - tJ2) (1 - tJ1) sgJ1 = true := by decide +kernel
end CongestionNative
