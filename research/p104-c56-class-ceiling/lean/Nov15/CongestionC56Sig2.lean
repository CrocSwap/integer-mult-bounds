import Nov15.CongestionI3DualSig
import Nov15.CongestionC56Defs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem sigK2 : sigOK (1 - tC0) (1 - tK2) sgK2 = true := by decide +kernel
end CongestionNative
