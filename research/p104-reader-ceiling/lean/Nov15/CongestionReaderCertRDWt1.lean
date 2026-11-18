import Nov15.CongestionReaderCertRDDefs
import Nov15.CongestionTreeW
import Nov15.CTreerdaDefs
import Nov15.CTreerdiDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem wtRD_1_4 : CTree.wtPair CTree.rdaW (1 - tTJ0RD) (1 - a0RD) (1, 4) = true := by unfold tTJ0RD a0RD; decide +kernel
theorem wtRD_1_5 : CTree.wtPair CTree.rdaW (1 - tTJ0RD) (1 - a0RD) (1, 5) = true := by unfold tTJ0RD a0RD; decide +kernel
end CongestionNative
