import Nov15.CongestionReaderCertRFDefs
import Nov15.CongestionReaderTree
import Nov15.CTreerfaDefs
import Nov15.CTreerfiDefs
namespace CongestionNative
open NumCertK CongestionI3
theorem lineRF1 : CTree.lineOKR CTree.rfar0 CTree.rfir0 capIRF1 dIRF lamRF1 gARF1 gBRF1 = true := by unfold capIRF1 dIRF lamRF1 gARF1 gBRF1; decide +kernel
theorem numRF1 : lcpRF1 + 8 * cHRF1 ≤ (((lamRF1 : ℚ) * 4962 - ((gARF1 : ℚ) * 104 - ((gARF1 : ℚ) - gBRF1) * 48) - ((25 : ℕ) : ℚ) * dIRF) / 10 ^ 14) := by
  unfold lcpRF1 cHRF1 lamRF1 gARF1 gBRF1 dIRF; norm_num
theorem capRF1 : (capIRF1 : ℚ) ≤ unLoRF1 * 10 ^ 14 / 48 := by unfold capIRF1 unLoRF1; norm_num
end CongestionNative
