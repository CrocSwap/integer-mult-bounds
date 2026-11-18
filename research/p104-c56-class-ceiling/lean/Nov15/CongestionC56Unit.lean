import Nov15.CongestionC56Defs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
/-- `8^s - 9^s` as an exponential polynomial -/
def unitCF : CF := [(8, 1), (9, -1)]
theorem unitCF_ok : okR unitCF := by decide +kernel
theorem unitK0 : Fup unitCF (1 - tK1) (1 - tK1) < -unitLoK0 := by unfold tK1 unitLoK0; decide +kernel
theorem unitK1 : Fup unitCF (1 - tK2) (1 - tK2) < -unitLoK1 := by unfold tK2 unitLoK1; decide +kernel
theorem unitK2 : Fup unitCF (1 - tC0) (1 - tC0) < -unitLoK2 := by unfold tC0 unitLoK2; decide +kernel
theorem unitC0' : Fup unitCF (1 - tC1) (1 - tC1) < -unitLoC0 := by unfold tC1 unitLoC0; decide +kernel
theorem unitC1' : Fup unitCF (1 - tC2) (1 - tC2) < -unitLoC1 := by unfold tC2 unitLoC1; decide +kernel
theorem unitC2' : Fup unitCF (1 - tC3) (1 - tC3) < -unitLoC2 := by unfold tC3 unitLoC2; decide +kernel
theorem unitC3' : Fup unitCF (1 - 1 / 10) (1 - 1 / 10) < -unitLoC3 := by unfold unitLoC3; decide +kernel
end CongestionNative
