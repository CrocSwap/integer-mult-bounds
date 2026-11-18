import Nov15.CongestionNativeJUnit
import Nov15.CongestionNativeNDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem unitN0 : Fup unitCF (1 - tN1) (1 - tN1) < -unitLoN0 := by unfold tN1 unitLoN0; decide +kernel
theorem unitN1 : Fup unitCF (1 - tN2) (1 - tN2) < -unitLoN1 := by unfold tN2 unitLoN1; decide +kernel
theorem unitN2 : Fup unitCF (1 - tN3) (1 - tN3) < -unitLoN2 := by unfold tN3 unitLoN2; decide +kernel
theorem unitN3 : Fup unitCF (1 - tN4) (1 - tN4) < -unitLoN3 := by unfold tN4 unitLoN3; decide +kernel
theorem unitN4 : Fup unitCF (1 - tN5) (1 - tN5) < -unitLoN4 := by unfold tN5 unitLoN4; decide +kernel
end CongestionNative
