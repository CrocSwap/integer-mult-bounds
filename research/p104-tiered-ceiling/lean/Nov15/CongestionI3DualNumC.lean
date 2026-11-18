import Nov15.CongestionI3DualConst
import Nov15.CongestionI3NumC4
namespace CongestionI3Dual
open NumCertK CongestionI3
theorem ptC0 : Fup cfC (1 - tC0) (1 - tC0) < 17 * LC0 := by unfold tC0 LC0 lcpC0 sgC0; decide +kernel
theorem ptC1 : Fup cfC (1 - tC1) (1 - tC1) < 17 * LC1 := by unfold tC1 LC1 lcpC1 sgC1; decide +kernel
theorem ptC2 : Fup cfC (1 - tC2) (1 - tC2) < 17 * LC2 := by unfold tC2 LC2 lcpC2 sgC2; decide +kernel
end CongestionI3Dual
