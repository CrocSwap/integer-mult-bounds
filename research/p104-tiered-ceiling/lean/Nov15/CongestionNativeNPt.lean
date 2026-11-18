import Nov15.CongestionI3DualConst
import Nov15.CongestionI3NumC1
import Nov15.CongestionNativeJUnit
import Nov15.CongestionNativeNDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem cfC_dN : 0 < dLo cfC (93 / 100) (1 - tN0) := by unfold tN0; decide +kernel
theorem ptN0 : Fup cfC (1 - tN0) (1 - tN0) < 17 * LN0 := by unfold tN0 LN0 lcpN0 sgN0; decide +kernel
theorem ptN1 : Fup cfC (1 - tN1) (1 - tN1) < 17 * LN1 := by unfold tN1 LN1 lcpN1 sgN1; decide +kernel
theorem ptN2 : Fup cfC (1 - tN2) (1 - tN2) < 17 * LN2 := by unfold tN2 LN2 lcpN2 sgN2; decide +kernel
theorem ptN3 : Fup cfC (1 - tN3) (1 - tN3) < 17 * LN3 := by unfold tN3 LN3 lcpN3 sgN3; decide +kernel
theorem boxN4a : Fup cfC (9 / 10) (915 / 1000) < 17 * LN4 := by unfold LN4 lcpN4 sgN4; decide +kernel
theorem boxN4b : Fup cfC (915 / 1000) (93 / 100) < 17 * LN4 := by unfold LN4 lcpN4 sgN4; decide +kernel
end CongestionNative
