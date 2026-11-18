import Nov15.CongestionI3DualSig
import Nov15.CongestionC56Defs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem sigK0 : sigOK (1 - tK1) (1 - tK0) sgK0 = true := by decide +kernel
end CongestionNative
