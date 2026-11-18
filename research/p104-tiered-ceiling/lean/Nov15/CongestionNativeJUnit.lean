import Nov15.CongestionNativeJDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
/-- `8^s - 9^s` as an exponential polynomial -/
def unitCF : CF := [(8, 1), (9, -1)]
theorem unitCF_ok : okR unitCF := by decide +kernel
theorem unitJ0 : Fup unitCF (1 - tJ1) (1 - tJ1) < -unitLoJ0 := by unfold tJ1 unitLoJ0; decide +kernel
theorem unitJ1 : Fup unitCF (1 - tJ2) (1 - tJ2) < -unitLoJ1 := by unfold tJ2 unitLoJ1; decide +kernel
theorem unitJ2 : Fup unitCF (1 - tC0) (1 - tC0) < -unitLoJ2 := by unfold tC0 unitLoJ2; decide +kernel
theorem unitC0' : Fup unitCF (1 - tC1) (1 - tC1) < -unitLoC0 := by unfold tC1 unitLoC0; decide +kernel
theorem unitC1' : Fup unitCF (1 - tC2) (1 - tC2) < -unitLoC1 := by unfold tC2 unitLoC1; decide +kernel
theorem unitC2' : Fup unitCF (1 - tC3) (1 - tC3) < -unitLoC2 := by unfold tC3 unitLoC2; decide +kernel
theorem unitC3' : Fup unitCF (1 - 1 / 10) (1 - 1 / 10) < -unitLoC3 := by unfold unitLoC3; decide +kernel
end CongestionNative
