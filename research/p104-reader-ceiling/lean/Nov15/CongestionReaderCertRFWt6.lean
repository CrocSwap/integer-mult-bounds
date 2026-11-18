import Nov15.CongestionReaderCertRFDefs
import Nov15.CongestionTreeW
import Nov15.CTreerfaDefs
import Nov15.CTreerfiDefs
namespace CongestionNative
open NumCertK CongestionI3 CongestionI3Dual
theorem wtRF_2_8 : CTree.wtPair CTree.rfaW (1 - tTJ0RF) (1 - a0RF) (2, 8) = true := by unfold tTJ0RF a0RF; decide +kernel
theorem wtRF_3_4 : CTree.wtPair CTree.rfaW (1 - tTJ0RF) (1 - a0RF) (3, 4) = true := by unfold tTJ0RF a0RF; decide +kernel
end CongestionNative
