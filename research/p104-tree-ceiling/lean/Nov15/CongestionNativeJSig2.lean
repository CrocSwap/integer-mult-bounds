import Nov15.CongestionI3DualSig
import Nov15.CongestionNativeJDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem sigJ2 : sigOK (1 - tC0) (1 - tJ2) sgJ2 = true := by decide +kernel
end CongestionNative
