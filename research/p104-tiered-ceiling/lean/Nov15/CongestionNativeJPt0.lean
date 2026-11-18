import Nov15.CongestionNativeJDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem ptJ0 : Fup cfC (1 - tJ0) (1 - tJ0) < 17 * LJ0 := by unfold tJ0 LJ0 lcpJ0 sgJ0; decide +kernel
end CongestionNative
