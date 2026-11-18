import Nov15.CongestionNativeJDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem ptJ2 : Fup cfC (1 - tJ2) (1 - tJ2) < 17 * LJ2 := by unfold tJ2 LJ2 lcpJ2 sgJ2; decide +kernel
end CongestionNative
