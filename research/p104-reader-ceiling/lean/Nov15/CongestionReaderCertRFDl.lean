import Nov15.CongestionReaderCertRFDefs
import Nov15.CongestionTreeW
namespace CongestionNative
open NumCertK CongestionI3
def cfDelRF : CF := [(7, 1), (2, 1), (8, -1), (1, -1)]
theorem dlDRF : 0 < dLo (CTree.negCF cfDelRF) (1 - tTJ0RF) (1 - a0RF) := by unfold tTJ0RF a0RF cfDelRF CTree.negCF; decide +kernel
theorem dlPRF : Fup (CTree.negCF cfDelRF) (1 - a0RF) (1 - a0RF) ≤ -((dIRF : ℚ) / 10 ^ 14) := by unfold a0RF dIRF cfDelRF CTree.negCF; decide +kernel
end CongestionNative
