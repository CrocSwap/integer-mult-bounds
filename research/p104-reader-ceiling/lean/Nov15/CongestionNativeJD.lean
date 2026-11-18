import Nov15.CongestionNativeJDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem cfC_dJ : 0 < dLo cfC (93 / 100) (1 - tJ0) := by unfold tJ0; decide +kernel
end CongestionNative
