import Nov15.CongestionReaderCertRDDefs
import Nov15.CongestionTreeW
import Nov15.CTreerdaDefs
import Nov15.CTreerdiDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem wtRD_1_8 : CTree.wtPair CTree.rdaW (1 - tTJ0RD) (1 - a0RD) (1, 8) = true := by unfold tTJ0RD a0RD; decide +kernel
theorem wtRD_2_3 : CTree.wtPair CTree.rdaW (1 - tTJ0RD) (1 - a0RD) (2, 3) = true := by unfold tTJ0RD a0RD; decide +kernel
end CongestionNative
