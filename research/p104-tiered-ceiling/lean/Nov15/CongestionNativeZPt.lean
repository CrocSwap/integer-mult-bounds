import Nov15.CongestionI3DualConst
import Nov15.CongestionI3NumC1
import Nov15.CongestionNativeJUnit
import Nov15.CongestionNativeZDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem cfC_dZ : 0 < dLo cfC (93 / 100) (1 - tZ0) := by unfold tZ0; decide +kernel
theorem ptZ0 : Fup cfC (1 - tZ0) (1 - tZ0) < 17 * LZ0 := by unfold tZ0 LZ0 lcpZ0 sgZ0; decide +kernel
theorem ptZ1 : Fup cfC (1 - tZ1) (1 - tZ1) < 17 * LZ1 := by unfold tZ1 LZ1 lcpZ1 sgZ1; decide +kernel
theorem ptZ2 : Fup cfC (1 - tZ2) (1 - tZ2) < 17 * LZ2 := by unfold tZ2 LZ2 lcpZ2 sgZ2; decide +kernel
theorem ptZ3 : Fup cfC (1 - tZ3) (1 - tZ3) < 17 * LZ3 := by unfold tZ3 LZ3 lcpZ3 sgZ3; decide +kernel
theorem boxZ4a : Fup cfC (9 / 10) (915 / 1000) < 17 * LZ4 := by unfold LZ4 lcpZ4 sgZ4; decide +kernel
theorem boxZ4b : Fup cfC (915 / 1000) (93 / 100) < 17 * LZ4 := by unfold LZ4 lcpZ4 sgZ4; decide +kernel
end CongestionNative
