import Nov15.CongestionC56Defs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem ptK2 : Fup cfC (1 - tK2) (1 - tK2) < 17 * LK2 := by unfold tK2 LK2 lcpK2 sgK2; decide +kernel
end CongestionNative
