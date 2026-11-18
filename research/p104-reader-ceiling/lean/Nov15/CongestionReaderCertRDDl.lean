import Nov15.CongestionReaderCertRDDefs
import Nov15.CongestionTreeW
namespace CongestionNative
open NumCertK CongestionI3
def cfDelRD : CF := [(7, 1), (2, 1), (8, -1), (1, -1)]
theorem dlDRD : 0 < dLo (CTree.negCF cfDelRD) (1 - tTJ0RD) (1 - a0RD) := by unfold tTJ0RD a0RD cfDelRD CTree.negCF; decide +kernel
theorem dlPRD : Fup (CTree.negCF cfDelRD) (1 - a0RD) (1 - a0RD) ≤ -((dIRD : ℚ) / 10 ^ 14) := by unfold a0RD dIRD cfDelRD CTree.negCF; decide +kernel
end CongestionNative
