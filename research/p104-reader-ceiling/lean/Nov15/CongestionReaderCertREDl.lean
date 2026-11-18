import Nov15.CongestionReaderCertREDefs
import Nov15.CongestionTreeW
namespace CongestionNative
open NumCertK CongestionI3
def cfDelRE : CF := [(7, 1), (2, 1), (8, -1), (1, -1)]
theorem dlDRE : 0 < dLo (CTree.negCF cfDelRE) (1 - tTJ0RE) (1 - a0RE) := by unfold tTJ0RE a0RE cfDelRE CTree.negCF; decide +kernel
theorem dlPRE : Fup (CTree.negCF cfDelRE) (1 - a0RE) (1 - a0RE) ≤ -((dIRE : ℚ) / 10 ^ 14) := by unfold a0RE dIRE cfDelRE CTree.negCF; decide +kernel
end CongestionNative
