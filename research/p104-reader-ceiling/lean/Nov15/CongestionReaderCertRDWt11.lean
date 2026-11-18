import Nov15.CongestionReaderCertRDDefs
import Nov15.CongestionTreeW
import Nov15.CTreerdaDefs
import Nov15.CTreerdiDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem wtRD_5_6 : CTree.wtPair CTree.rdaW (1 - tTJ0RD) (1 - a0RD) (5, 6) = true := by unfold tTJ0RD a0RD; decide +kernel
theorem wtRD_5_7 : CTree.wtPair CTree.rdaW (1 - tTJ0RD) (1 - a0RD) (5, 7) = true := by unfold tTJ0RD a0RD; decide +kernel
end CongestionNative
