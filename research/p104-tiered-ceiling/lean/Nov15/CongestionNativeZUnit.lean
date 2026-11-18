import Nov15.CongestionNativeJUnit
import Nov15.CongestionNativeZDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem unitZ0 : Fup unitCF (1 - tZ1) (1 - tZ1) < -unitLoZ0 := by unfold tZ1 unitLoZ0; decide +kernel
theorem unitZ1 : Fup unitCF (1 - tZ2) (1 - tZ2) < -unitLoZ1 := by unfold tZ2 unitLoZ1; decide +kernel
theorem unitZ2 : Fup unitCF (1 - tZ3) (1 - tZ3) < -unitLoZ2 := by unfold tZ3 unitLoZ2; decide +kernel
theorem unitZ3 : Fup unitCF (1 - tZ4) (1 - tZ4) < -unitLoZ3 := by unfold tZ4 unitLoZ3; decide +kernel
theorem unitZ4 : Fup unitCF (1 - tZ5) (1 - tZ5) < -unitLoZ4 := by unfold tZ5 unitLoZ4; decide +kernel
end CongestionNative
