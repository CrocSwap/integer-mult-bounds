import Nov15.CongestionNativeJDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem ptJ1 : Fup cfC (1 - tJ1) (1 - tJ1) < 17 * LJ1 := by unfold tJ1 LJ1 lcpJ1 sgJ1; decide +kernel
end CongestionNative
