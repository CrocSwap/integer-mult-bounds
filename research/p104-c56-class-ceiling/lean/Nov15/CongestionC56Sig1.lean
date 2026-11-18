import Nov15.CongestionI3DualSig
import Nov15.CongestionC56Defs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem sigK1 : sigOK (1 - tK2) (1 - tK1) sgK1 = true := by decide +kernel
end CongestionNative
