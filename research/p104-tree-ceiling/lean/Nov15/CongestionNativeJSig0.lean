import Nov15.CongestionI3DualSig
import Nov15.CongestionNativeJDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem sigJ0 : sigOK (1 - tJ1) (1 - tJ0) sgJ0 = true := by decide +kernel
end CongestionNative
