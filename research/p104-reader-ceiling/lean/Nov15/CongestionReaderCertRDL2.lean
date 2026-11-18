import Nov15.CongestionReaderCertRDDefs
import Nov15.CongestionReaderTree
import Nov15.CTreerdaDefs
import Nov15.CTreerdiDefs
namespace CongestionNative
open NumCertK CongestionI3
theorem lineRD2 : CTree.lineOKR CTree.rdar0 CTree.rdir0 capIRD2 dIRD lamRD2 gARD2 gBRD2 = true := by unfold capIRD2 dIRD lamRD2 gARD2 gBRD2; decide +kernel
theorem numRD2 : lcpRD2 + 8 * cHRD2 ≤ (((lamRD2 : ℚ) * 4962 - ((gARD2 : ℚ) * 104 - ((gARD2 : ℚ) - gBRD2) * 48) - ((15 : ℕ) : ℚ) * dIRD) / 10 ^ 14) := by
  unfold lcpRD2 cHRD2 lamRD2 gARD2 gBRD2 dIRD; norm_num
theorem capRD2 : (capIRD2 : ℚ) ≤ unLoRD2 * 10 ^ 14 / 48 := by unfold capIRD2 unLoRD2; norm_num
end CongestionNative
