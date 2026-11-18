import Nov15.CongestionC56Defs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem ptK1 : Fup cfC (1 - tK1) (1 - tK1) < 17 * LK1 := by unfold tK1 LK1 lcpK1 sgK1; decide +kernel
end CongestionNative
