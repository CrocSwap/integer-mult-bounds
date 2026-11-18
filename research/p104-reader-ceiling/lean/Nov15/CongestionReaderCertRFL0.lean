import Nov15.CongestionReaderCertRFDefs
import Nov15.CongestionReaderTree
import Nov15.CTreerfaDefs
import Nov15.CTreerfiDefs
namespace CongestionNative
open NumCertK CongestionI3
theorem lineRF0 : CTree.lineOKR CTree.rfar0 CTree.rfir0 capIRF0 dIRF lamRF0 gARF0 gBRF0 = true := by unfold capIRF0 dIRF lamRF0 gARF0 gBRF0; decide +kernel
theorem numRF0 : lcpRF0 + 8 * cHRF0 ≤ (((lamRF0 : ℚ) * 4962 - ((gARF0 : ℚ) * 104 - ((gARF0 : ℚ) - gBRF0) * 48) - ((25 : ℕ) : ℚ) * dIRF) / 10 ^ 14) := by
  unfold lcpRF0 cHRF0 lamRF0 gARF0 gBRF0 dIRF; norm_num
theorem capRF0 : (capIRF0 : ℚ) ≤ unLoRF0 * 10 ^ 14 / 48 := by unfold capIRF0 unLoRF0; norm_num
end CongestionNative
